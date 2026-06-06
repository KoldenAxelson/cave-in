"""Tests for the DQN training logic (gated on PyTorch being installed).

These check the learning *machinery* runs correctly — action selection, one
gradient update, and a tiny end-to-end training run that saves a brain. They do
not assert the agent becomes good (that needs a full training run).
"""

import numpy as np
import pytest

torch = pytest.importorskip("torch")

from src.ai.learning.environment import OBSERVATION_SIZE, NUM_ACTIONS
from src.ai.learning.network import QNetwork
from src.ai.learning.replay_buffer import ReplayBuffer
from src.ai.learning import storage
from src.ai.learning.trainer import (
    TrainConfig, select_action, learn_step, train,
)


def _fill_buffer(buffer, n=64):
    for _ in range(n):
        obs = np.random.rand(OBSERVATION_SIZE).astype(np.float32)
        next_obs = np.random.rand(OBSERVATION_SIZE).astype(np.float32)
        buffer.push(obs, np.random.randint(NUM_ACTIONS), np.random.rand(),
                    next_obs, 0.0)


class TestSelectAction:
    def test_random_when_epsilon_one(self):
        net = QNetwork()
        obs = np.zeros(OBSERVATION_SIZE, dtype=np.float32)
        actions = {select_action(net, obs, epsilon=1.0) for _ in range(50)}
        assert actions.issubset(set(range(NUM_ACTIONS)))

    def test_greedy_is_deterministic(self):
        net = QNetwork()
        obs = np.random.rand(OBSERVATION_SIZE).astype(np.float32)
        a = select_action(net, obs, epsilon=0.0)
        b = select_action(net, obs, epsilon=0.0)
        assert a == b
        assert 0 <= a < NUM_ACTIONS


class TestLearnStep:
    def test_returns_loss_and_changes_weights(self):
        online, target = QNetwork(), QNetwork()
        target.load_state_dict(online.state_dict())
        optimizer = torch.optim.Adam(online.parameters(), lr=1e-2)
        buffer = ReplayBuffer(1000)
        _fill_buffer(buffer, 128)

        before = [p.clone() for p in online.parameters()]
        loss = learn_step(online, target, optimizer, buffer, batch_size=32, gamma=0.99)
        after = list(online.parameters())

        assert isinstance(loss, float)
        # At least one parameter tensor should have moved.
        assert any(not torch.allclose(b, a) for b, a in zip(before, after))


class TestTrainSmoke:
    def test_tiny_training_runs_and_saves(self, tmp_path):
        path = str(tmp_path / "brain.pt")
        config = TrainConfig(
            episodes=2, max_steps=40, stick_count=3,
            min_replay=10, batch_size=8, buffer_capacity=500,
            target_update=20, save_every=1, log_every=1,
            save_path=path, seed=0,
        )
        history = train(config)
        assert len(history) == 2
        assert all("reward" in h for h in history)

        import os
        assert os.path.exists(path)
        # The saved brain should load back and match the current config.
        payload = storage.load_brain(path, QNetwork(),
                                     expected_metadata=storage.current_metadata(3))
        assert payload["episode"] == 2
