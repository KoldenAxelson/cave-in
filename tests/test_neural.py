"""Tests for the ML pieces: network shape, brain save/load, and the controller.

These are 'plumbing' tests — they check the network produces the right shape, the
brain round-trips to disk correctly (and refuses incompatible loads), and the
controller emits valid actions. They do NOT check that a brain plays *well*;
that's what training and the benchmark are for.

Skipped automatically if PyTorch isn't installed (it's an optional dependency).
"""

import numpy as np
import pytest

torch = pytest.importorskip("torch")  # skip this file if torch isn't installed

from src.ai.learning.environment import OBSERVATION_SIZE, NUM_ACTIONS, NUM_ACTIONS as _NA
from src.ai.learning.network import QNetwork
from src.ai.learning import storage
from src.ai.learning.neural_controller import NeuralController
from src.core.world import GameWorld
from src.cells.player import Player
from src.core.stats import Stats


def _make_world(stick_count=3):
    world = GameWorld(stick_count=stick_count)
    world.player = Player()
    world.stats = Stats()
    world.add(world.player)
    return world


class TestNetwork:
    def test_forward_shape(self):
        net = QNetwork()
        batch = torch.zeros((4, OBSERVATION_SIZE), dtype=torch.float32)
        out = net(batch)
        assert out.shape == (4, NUM_ACTIONS)

    def test_single_observation(self):
        net = QNetwork()
        obs = torch.zeros((1, OBSERVATION_SIZE), dtype=torch.float32)
        assert net(obs).shape == (1, NUM_ACTIONS)


class TestPersistence:
    def test_save_load_round_trip(self, tmp_path):
        path = str(tmp_path / "brain.pt")
        net = QNetwork()
        meta = storage.current_metadata(stick_count=3)
        storage.save_brain(path, net, episode=7, epsilon=0.5, metadata=meta)

        loaded_net = QNetwork()
        payload = storage.load_brain(path, loaded_net, expected_metadata=meta)

        # Weights must come back identical -> identical output for identical input.
        probe = torch.randn((1, OBSERVATION_SIZE))
        assert torch.allclose(net(probe), loaded_net(probe))
        assert payload["episode"] == 7
        assert payload["epsilon"] == 0.5

    def test_optimizer_state_round_trips(self, tmp_path):
        path = str(tmp_path / "brain.pt")
        net = QNetwork()
        opt = torch.optim.Adam(net.parameters(), lr=1e-3)
        storage.save_brain(path, net, optimizer=opt, metadata=storage.current_metadata(3))

        net2 = QNetwork()
        opt2 = torch.optim.Adam(net2.parameters(), lr=1e-3)
        payload = storage.load_brain(path, net2, optimizer=opt2)
        assert payload["optimizer_state"] is not None

    def test_incompatible_brain_is_rejected(self, tmp_path):
        path = str(tmp_path / "brain.pt")
        net = QNetwork()
        saved_meta = storage.current_metadata(stick_count=3)
        saved_meta["observation_size"] = OBSERVATION_SIZE + 999   # pretend wrong shape
        storage.save_brain(path, net, metadata=saved_meta)

        with pytest.raises(storage.BrainIncompatibleError):
            storage.load_brain(path, QNetwork(),
                               expected_metadata=storage.current_metadata(3))


class TestNeuralController:
    def test_runs_without_a_saved_brain(self):
        # No file -> fresh random brain, but it must still produce valid actions.
        world = _make_world()
        controller = NeuralController(world, brain_path="/nonexistent/brain.pt")
        assert controller.loaded is False
        movement = controller.get_movement()
        assert movement in [(0, -1), (1, 0), (0, 1), (-1, 0), (0, 0)]
        assert isinstance(controller.should_use_action(), bool)

    def test_loads_a_saved_brain(self, tmp_path):
        path = str(tmp_path / "brain.pt")
        world = _make_world(stick_count=3)
        storage.save_brain(path, QNetwork(), metadata=storage.current_metadata(3))

        controller = NeuralController(world, brain_path=path)
        assert controller.loaded is True
        controller.get_movement()  # should not raise

    def test_movement_and_use_are_consistent(self):
        # Whatever action it picks, exactly one of (move, use) should be active.
        world = _make_world()
        controller = NeuralController(world, brain_path="/nonexistent/brain.pt")
        controller._last_use_time = -1000  # ensure use cooldown is clear
        movement = controller.get_movement()
        uses = controller.should_use_action()
        moved = movement != (0, 0)
        assert moved != uses  # exactly one is true
