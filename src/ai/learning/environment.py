"""The training environment: Cave In made into something an RL agent can learn on.

A reinforcement-learning agent learns by repeatedly: looking at an *observation*,
choosing an *action*, and receiving a *reward*. This module wraps the existing
game in the two functions every RL trainer expects:

    obs                       = env.reset()       # start a fresh game
    obs, reward, done, info   = env.step(action)  # take one action

Nothing here opens a window or depends on real time — actions are applied
directly to the game world, one decision at a time, so training runs fast and
headless. See docs/ML_CONTROLLER_PLAN.md for the full design rationale.
"""

from __future__ import annotations

import random
from typing import Optional, Tuple

import numpy as np

from src.core.world import GameWorld
from src.core.stats import Stats
from src.cells.player import Player
from src.cells import Cell, Rock, Stick
from src.utils.config import GRID_SIZE, Direction, STICK_COUNT


# --- Action space --------------------------------------------------------------
# Five primitive actions. The agent only ever chooses one of these per turn; it
# is never handed a path. Moving also sets the player's facing direction, and
# USE acts on whatever cell the player currently faces (collect a stick / clear a
# rock), exactly like pressing Space in the real game.
MOVE_UP, MOVE_RIGHT, MOVE_DOWN, MOVE_LEFT, USE = range(5)
NUM_ACTIONS = 5

_MOVE_DELTAS = {
    MOVE_UP: Direction.UP.value,
    MOVE_RIGHT: Direction.RIGHT.value,
    MOVE_DOWN: Direction.DOWN.value,
    MOVE_LEFT: Direction.LEFT.value,
}

# Three 10x10 layers (player / rocks / sticks) plus two scalars.
OBSERVATION_SIZE = 3 * GRID_SIZE * GRID_SIZE + 2


def encode_observation(world) -> np.ndarray:
    """Turn a game world into the fixed-size number vector the network reads.

    This is shared by the training environment and the play-time controller so
    the brain always sees the exact same format it was trained on. Layout:
    three 10x10 layers (player, rocks, sticks) flattened, then two scalars
    (sticks held, fraction of board filled).
    """
    player_layer = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.float32)
    rock_layer = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.float32)
    stick_layer = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.float32)

    for (column, row), cell in world.grid.items():
        if isinstance(cell, Rock):
            rock_layer[column, row] = 1.0
        elif isinstance(cell, Stick):
            stick_layer[column, row] = 1.0
    player_column, player_row = world.player.position
    player_layer[player_column, player_row] = 1.0

    cell_count = GRID_SIZE * GRID_SIZE
    sticks_held = (world.stats.sticks_collected if world.stats else 0) / cell_count
    non_empty = sum(1 for cell in world.grid.values() if type(cell) is not Cell)
    filled_fraction = non_empty / cell_count

    return np.concatenate([
        player_layer.flatten(),
        rock_layer.flatten(),
        stick_layer.flatten(),
        np.array([sticks_held, filled_fraction], dtype=np.float32),
    ])


class CaveInEnv:
    """A single-agent, headless Cave In environment for reinforcement learning."""

    def __init__(
        self,
        stick_count: int = STICK_COUNT,
        max_steps: int = 5000,
        stick_reward: float = 1.0,
        step_penalty: float = -0.02,
        illegal_penalty: float = -0.1,
        shaping_scale: float = 0.1,
        gamma: float = 0.99,
    ):
        # Reward weights — see docs §3.3. Tunable; defaults match the plan.
        self.stick_count = stick_count
        self.max_steps = max_steps
        self.stick_reward = stick_reward
        self.step_penalty = step_penalty
        self.illegal_penalty = illegal_penalty
        self.shaping_scale = shaping_scale
        self.gamma = gamma

        self.world: Optional[GameWorld] = None
        self.player: Optional[Player] = None
        self.stats: Optional[Stats] = None
        self.steps: int = 0
        self.done: bool = True

    # -- Core RL interface ------------------------------------------------------
    def reset(self, seed: Optional[int] = None) -> np.ndarray:
        """Start a fresh game and return the first observation.
        Pass a seed to make the random board reproducible (used by tests)."""
        if seed is not None:
            random.seed(seed)

        self.world = GameWorld(stick_count=self.stick_count)
        self.player = Player()
        self.stats = Stats()
        self.world.player = self.player
        self.world.stats = self.stats
        self.world.add(self.player)
        # Movement is gated by a real-time cooldown during normal play; in
        # training one step == one decision, so we disable that timing gate.
        self.player.move_cooldown = 0

        self.steps = 0
        self.done = False
        return self._observation()

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, dict]:
        """Apply one action and return (observation, reward, done, info)."""
        if self.done:
            raise RuntimeError("step() called on a finished episode; call reset() first.")

        distance_before = self._nearest_stick_distance()
        reward = self.step_penalty  # a small "living cost" every turn
        collected = False

        if action == USE:
            reward += self._apply_use()
        elif action in _MOVE_DELTAS:
            reward += self._apply_move(action)
        else:
            raise ValueError(f"Invalid action: {action}")

        # Potential-based shaping toward the nearest stick (policy-preserving):
        #   F = scale * (gamma * -d_after - (-d_before)) = scale * (d_before - gamma*d_after)
        # Moving closer is a small positive nudge; round trips net to ~zero.
        distance_after = self._nearest_stick_distance()
        reward += self.shaping_scale * (distance_before - self.gamma * distance_after)

        self.steps += 1
        self.done = self.world.is_board_full() or self.steps >= self.max_steps

        info = {
            "sticks_collected": self.stats.sticks_collected,
            "tiles_moved": self.stats.tiles_moved,
            "steps": self.steps,
        }
        return self._observation(), reward, self.done, info

    # -- Action helpers ---------------------------------------------------------
    def _apply_move(self, action: int) -> float:
        """Face the chosen direction and try to move. Returns any extra reward."""
        delta = _MOVE_DELTAS[action]
        player_x, player_y = self.player.position
        raw_target = (player_x + delta[0], player_y + delta[1])

        # Facing always updates (so the agent can turn toward a stick/rock to use
        # it next turn), even when the move itself is blocked.
        self.player.update_facing(delta)
        self.player.try_move(self.world, delta)

        # Only a move into the wall (out of bounds) is "wasted". A move blocked by
        # a rock/stick still usefully sets facing, so it isn't penalized here.
        if not self._in_bounds(raw_target):
            return self.illegal_penalty
        return 0.0

    def _apply_use(self) -> float:
        """Use the faced cell. +reward for collecting a stick; penalty for a no-op."""
        facing_x, facing_y = self.player.facing.value
        player_x, player_y = self.player.position
        target = (player_x + facing_x, player_y + facing_y)
        faced_a_stick = isinstance(self.world.grid.get(target), Stick)

        succeeded = self.player.try_use_facing_cell(self.world)

        if succeeded and faced_a_stick:
            return self.stick_reward      # collected a stick (the goal)
        if not succeeded:
            return self.illegal_penalty   # faced empty space / unaffordable rock
        return 0.0                        # legal rock removal (no bonus, costs a step+stick)

    # -- Observation ------------------------------------------------------------
    def _observation(self) -> np.ndarray:
        """Encode the current board (shared with the play-time controller)."""
        return encode_observation(self.world)

    # -- Small utilities --------------------------------------------------------
    def _nearest_stick_distance(self) -> int:
        """Manhattan distance from the player to the closest stick (0 if none)."""
        player_x, player_y = self.player.position
        distances = [
            abs(player_x - stick_x) + abs(player_y - stick_y)
            for (stick_x, stick_y), cell in self.world.grid.items()
            if isinstance(cell, Stick)
        ]
        return min(distances) if distances else 0

    @staticmethod
    def _in_bounds(position: Tuple[int, int]) -> bool:
        column, row = position
        return 0 <= column < GRID_SIZE and 0 <= row < GRID_SIZE
