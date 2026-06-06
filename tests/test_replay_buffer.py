"""Tests for the experience replay buffer (no PyTorch needed — pure numpy)."""

import numpy as np
import pytest

from src.ai.learning.replay_buffer import ReplayBuffer
from src.ai.learning.environment import OBSERVATION_SIZE


def _fake_transition(value=0.0):
    obs = np.full(OBSERVATION_SIZE, value, dtype=np.float32)
    next_obs = np.full(OBSERVATION_SIZE, value + 1, dtype=np.float32)
    return (obs, 1, 0.5, next_obs, 0.0)


def test_length_grows_with_pushes():
    buffer = ReplayBuffer(capacity=100)
    assert len(buffer) == 0
    for _ in range(10):
        buffer.push(*_fake_transition())
    assert len(buffer) == 10


def test_capacity_caps_size_and_drops_oldest():
    buffer = ReplayBuffer(capacity=5)
    for i in range(8):
        buffer.push(*_fake_transition(value=float(i)))
    assert len(buffer) == 5  # only the most recent 5 are kept


def test_sample_returns_correctly_shaped_arrays():
    buffer = ReplayBuffer(capacity=100)
    for _ in range(20):
        buffer.push(*_fake_transition())
    observations, actions, rewards, next_observations, dones = buffer.sample(8)
    assert observations.shape == (8, OBSERVATION_SIZE)
    assert next_observations.shape == (8, OBSERVATION_SIZE)
    assert actions.shape == (8,)
    assert rewards.shape == (8,)
    assert dones.shape == (8,)
    assert actions.dtype == np.int64
    assert rewards.dtype == np.float32
