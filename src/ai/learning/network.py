"""The neural network — "the brain".

A neural network here is just a stack of arithmetic with a lot of tunable numbers
("weights"). This one takes the observation vector in and produces one number per
action: the predicted **Q-value** (expected total future reward) of taking that
action. Picking the action with the highest Q-value is how the agent plays.

It's deliberately small — a couple of fully-connected ("Linear") layers with
ReLU in between — which is plenty for a 10x10 board and trains fast on a CPU.
"""

from __future__ import annotations

import torch
import torch.nn as nn

from src.ai.learning.environment import OBSERVATION_SIZE, NUM_ACTIONS


class QNetwork(nn.Module):
    """Maps an observation vector to one Q-value per action."""

    def __init__(
        self,
        input_size: int = OBSERVATION_SIZE,
        num_actions: int = NUM_ACTIONS,
        hidden_size: int = 128,
    ):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, num_actions),
        )

    def forward(self, observation: torch.Tensor) -> torch.Tensor:
        """observation: shape (batch, input_size) -> returns (batch, num_actions)."""
        return self.layers(observation)
