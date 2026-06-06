"""The play-time controller: lets a trained brain drive the game.

This implements the same `AIInterface` the path finder uses, so the game doesn't
need to know or care that a neural network is making the decisions. Each turn it
encodes the board, asks the network for the Q-value of every action, and plays the
highest one (no exploration, no learning — that all happens during training).

If no saved brain exists yet, it runs on a fresh (random) network and plays
badly. That's expected until training has produced a brain file.
"""

from __future__ import annotations

import os
import time

import torch

from src.ai.ai_interface import AIInterface
from src.ai.learning.environment import (
    encode_observation,
    MOVE_UP, MOVE_RIGHT, MOVE_DOWN, MOVE_LEFT, USE,
)
from src.ai.learning.network import QNetwork
from src.ai.learning.storage import (
    DEFAULT_MODEL_PATH, load_brain, current_metadata,
)
from src.utils.config import Direction, PLAYER_MOVE_COOLDOWN, STICK_COUNT

_ACTION_TO_DELTA = {
    MOVE_UP: Direction.UP.value,
    MOVE_RIGHT: Direction.RIGHT.value,
    MOVE_DOWN: Direction.DOWN.value,
    MOVE_LEFT: Direction.LEFT.value,
}


class NeuralController(AIInterface):
    """Drives the player using a trained Q-network."""

    def __init__(self, world, brain_path: str = DEFAULT_MODEL_PATH):
        self.world = world
        self.network = QNetwork()
        self.loaded = False

        if os.path.exists(brain_path):
            stick_count = getattr(world, "stick_count", STICK_COUNT)
            load_brain(
                brain_path,
                self.network,
                expected_metadata=current_metadata(stick_count),
            )
            self.loaded = True

        self.network.eval()           # inference mode (no training behaviour)
        self._chosen_action = USE
        self._last_use_time = 0.0

    # -- AIInterface ------------------------------------------------------------
    def update(self, world) -> None:
        """Keep a reference to the current world (the game mutates it in place)."""
        self.world = world

    def get_movement(self):
        """Called first each turn: decide the action, return its movement (if any)."""
        self._chosen_action = self._choose_action()
        return _ACTION_TO_DELTA.get(self._chosen_action, Direction.NONE.value)

    def should_use_action(self) -> bool:
        """Called after get_movement: act only if this turn's choice was USE.
        A short cooldown stops the same 'use' from firing every frame."""
        if self._chosen_action != USE:
            return False
        now = time.time()
        if now - self._last_use_time < PLAYER_MOVE_COOLDOWN:
            return False
        self._last_use_time = now
        return True

    # -- Decision ---------------------------------------------------------------
    def _choose_action(self) -> int:
        """Run the network on the current board and return the highest-Q action."""
        observation = encode_observation(self.world)
        with torch.no_grad():
            q_values = self.network(torch.from_numpy(observation).unsqueeze(0))
        return int(torch.argmax(q_values, dim=1).item())
