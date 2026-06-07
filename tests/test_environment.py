"""Tests for the RL training environment (CaveInEnv).

These verify the *plumbing* — observation shape/contents, reward components,
episode termination, illegal-move handling — not whether an agent learns well
(that's stochastic and judged from training metrics, not unit tests).

Several tests turn individual reward terms off (e.g. shaping_scale=0) so the
remaining reward is exact and easy to assert.
"""

import numpy as np
import pytest

from src.ai.learning.environment import (
    CaveInEnv, OBSERVATION_SIZE, NUM_ACTIONS,
    MOVE_UP, MOVE_RIGHT, MOVE_DOWN, MOVE_LEFT, USE,
)
from src.cells import Cell, Rock, Stick
from src.utils.config import GRID_SIZE, Direction


def blank_grid():
    return {(c, r): Cell((c, r)) for c in range(GRID_SIZE) for r in range(GRID_SIZE)}


def place(env, player_pos, sticks=(), rocks=(), sticks_held=0, facing=Direction.RIGHT):
    """Force the env into an exact board state for deterministic assertions."""
    env.world.grid = blank_grid()
    env.player.position = player_pos
    env.world.grid[player_pos] = env.player
    env.player.facing = facing
    env.stats.sticks_collected = sticks_held
    for s in sticks:
        env.world.grid[s] = Stick(s)
    for rk in rocks:
        env.world.grid[rk] = Rock(rk)


class TestReset:
    def test_observation_shape(self):
        env = CaveInEnv(stick_count=3)
        obs = env.reset(seed=0)
        assert obs.shape == (OBSERVATION_SIZE,)
        assert obs.dtype == np.float32

    def test_seeded_reset_is_reproducible(self):
        env = CaveInEnv(stick_count=3)
        a = env.reset(seed=42)
        b = env.reset(seed=42)
        assert np.array_equal(a, b)

    def test_board_seeds_requested_sticks(self):
        env = CaveInEnv(stick_count=3)
        env.reset(seed=1)
        sticks = sum(1 for c in env.world.grid.values() if isinstance(c, Stick))
        assert sticks == 3

    def test_observation_encodes_nearest_stick_offset(self):
        # The feature observation reports the nearest stick as a (dx, dy) offset
        # relative to the player. Place a known stick and check the offset.
        env = CaveInEnv(stick_count=1)
        env.reset(seed=1)
        place(env, (5, 5), sticks=[(8, 5)])   # nearest stick 3 cells to the right
        obs = env._observation()
        # Layout: [player_x/N, player_y/N, sticks_held, then per-stick dx,dy,dist...]
        nearest_dx = obs[3]
        nearest_dy = obs[4]
        assert nearest_dx == pytest.approx(3 / GRID_SIZE)
        assert nearest_dy == pytest.approx(0.0)


class TestMovement:
    def test_legal_move_updates_position(self):
        # Isolate: no step penalty, no shaping -> reward is exactly 0 for a plain move.
        env = CaveInEnv(step_penalty=0.0, shaping_scale=0.0)
        env.reset(seed=0)
        place(env, (5, 5))
        obs, reward, done, info = env.step(MOVE_RIGHT)
        assert env.player.position == (6, 5)
        assert reward == 0.0
        assert not done
        assert info["tiles_moved"] == 1

    def test_move_into_wall_is_penalized(self):
        env = CaveInEnv(step_penalty=0.0, shaping_scale=0.0, illegal_penalty=-0.1)
        env.reset(seed=0)
        place(env, (0, 0))
        _, reward, _, _ = env.step(MOVE_LEFT)   # off the left edge
        assert reward == pytest.approx(-0.1)
        assert env.player.position == (0, 0)    # did not move

    def test_move_blocked_by_rock_is_not_wall_penalized(self):
        # Blocked by a rock (in bounds) still sets facing, so it isn't penalized
        # as a wall bonk; reward is just the (zeroed) step cost.
        env = CaveInEnv(step_penalty=0.0, shaping_scale=0.0, illegal_penalty=-0.1)
        env.reset(seed=0)
        place(env, (5, 5), rocks=[(6, 5)])
        _, reward, _, _ = env.step(MOVE_RIGHT)
        assert reward == 0.0
        assert env.player.position == (5, 5)
        assert env.player.facing is Direction.RIGHT

    def test_walking_onto_stick_rewards_one(self):
        # Collection now happens by moving onto a stick, so the +1 is earned here.
        env = CaveInEnv(step_penalty=0.0, shaping_scale=0.0, stick_reward=1.0)
        env.reset(seed=0)
        place(env, (5, 5), sticks=[(6, 5)])
        before = env.stats.sticks_collected
        _, reward, _, _ = env.step(MOVE_RIGHT)
        assert env.player.position == (6, 5)
        assert env.stats.sticks_collected == before + 1
        assert reward == pytest.approx(1.0)


class TestUseAction:
    def test_using_a_stick_is_not_rewarded(self):
        # The use action only clears rocks now; facing+using a stick does nothing.
        env = CaveInEnv(step_penalty=0.0, shaping_scale=0.0, stick_reward=1.0)
        env.reset(seed=0)
        place(env, (5, 5), sticks=[(6, 5)], facing=Direction.RIGHT)
        _, reward, _, _ = env.step(USE)
        assert env.stats.sticks_collected == 0
        assert reward == pytest.approx(0.0)

    def test_removing_a_rock_is_legal_but_unrewarded(self):
        env = CaveInEnv(step_penalty=0.0, shaping_scale=0.0)
        env.reset(seed=0)
        place(env, (5, 5), rocks=[(6, 5)], sticks_held=1, facing=Direction.RIGHT)
        _, reward, _, _ = env.step(USE)
        assert type(env.world.grid[(6, 5)]) is Cell   # rock cleared
        assert reward == pytest.approx(0.0)           # no bonus, just (zeroed) step cost

    def test_use_facing_wall_is_penalized(self):
        env = CaveInEnv(step_penalty=0.0, shaping_scale=0.0, illegal_penalty=-0.1)
        env.reset(seed=0)
        place(env, (0, 0), facing=Direction.UP)       # faces off the top edge
        _, reward, _, _ = env.step(USE)
        assert reward == pytest.approx(-0.1)


class TestShaping:
    def test_moving_toward_stick_gives_positive_shaping(self):
        # Only shaping active: stepping closer to the stick should be positive.
        env = CaveInEnv(step_penalty=0.0, shaping_scale=0.1, illegal_penalty=0.0)
        env.reset(seed=0)
        place(env, (0, 0), sticks=[(9, 0)], facing=Direction.RIGHT)
        _, reward, _, _ = env.step(MOVE_RIGHT)        # 9->8 away, i.e. closer
        assert reward > 0


class TestTermination:
    def test_max_steps_ends_episode(self):
        env = CaveInEnv(max_steps=1)
        env.reset(seed=0)
        _, _, done, _ = env.step(MOVE_UP)
        assert done is True

    def test_full_board_ends_episode(self):
        env = CaveInEnv()
        env.reset(seed=0)
        # Fill every non-player cell with rock -> board is full.
        for pos, cell in list(env.world.grid.items()):
            if cell is not env.player:
                env.world.grid[pos] = Rock(pos)
        _, _, done, _ = env.step(MOVE_UP)
        assert done is True

    def test_step_after_done_raises(self):
        env = CaveInEnv(max_steps=1)
        env.reset(seed=0)
        env.step(MOVE_UP)
        with pytest.raises(RuntimeError):
            env.step(MOVE_UP)


def test_num_actions_constant():
    assert NUM_ACTIONS == 5
