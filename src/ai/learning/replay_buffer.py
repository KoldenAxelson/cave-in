"""Experience replay — the agent's memory of past moves.

Instead of learning only from the move it just made, a DQN agent stores each
experience and later learns from **random batches** of them. Two reasons:

1. It reuses each experience many times (more efficient).
2. Consecutive moves in a game are highly similar; learning from them in order is
   unstable. Sampling randomly breaks that correlation and steadies training.

Each stored experience is one transition: (observation, action taken, reward
received, next observation, whether the game ended).
"""

from __future__ import annotations

import random
from collections import deque
from typing import Tuple

import numpy as np


class ReplayBuffer:
    """A fixed-size memory of transitions; oldest are dropped when it's full."""

    def __init__(self, capacity: int):
        self.buffer = deque(maxlen=capacity)

    def push(self, observation, action, reward, next_observation, done) -> None:
        """Store one transition."""
        self.buffer.append((observation, action, reward, next_observation, done))

    def sample(self, batch_size: int) -> Tuple[np.ndarray, ...]:
        """Return a random batch as arrays:
        (observations, actions, rewards, next_observations, dones)."""
        batch = random.sample(self.buffer, batch_size)
        observations, actions, rewards, next_observations, dones = zip(*batch)
        return (
            np.array(observations, dtype=np.float32),
            np.array(actions, dtype=np.int64),
            np.array(rewards, dtype=np.float32),
            np.array(next_observations, dtype=np.float32),
            np.array(dones, dtype=np.float32),
        )

    def __len__(self) -> int:
        return len(self.buffer)
