"""The DQN trainer — where the random brain learns to play.

This is the "practice loop." The agent plays many games; after each move it stores
the experience and nudges its network so its Q-value predictions get more
accurate. Three standard DQN ingredients make this work (all explained in
docs/ML_CONTROLLER_PLAN.md and inline below):

- **Epsilon-greedy exploration:** early on the agent acts mostly at random so it
  discovers what's out there; over time it acts more on what it has learned.
- **Experience replay:** it learns from random batches of past moves, not just
  the latest one (see replay_buffer.py).
- **Target network:** a slowly-updated copy of the brain provides a stable
  learning target, so the agent isn't "chasing its own tail."

`train()` runs headless, prints progress, and saves the brain periodically so
quitting never loses more than the last checkpoint.
"""

from __future__ import annotations

import random
from collections import deque
from dataclasses import dataclass
from typing import Optional
import os

import numpy as np
import torch
import torch.nn as nn

from src.ai.learning.environment import CaveInEnv, NUM_ACTIONS
from src.ai.learning.network import QNetwork
from src.ai.learning.replay_buffer import ReplayBuffer
from src.ai.learning import storage


@dataclass
class TrainConfig:
    """All training knobs in one place (sensible defaults for a 10x10 board)."""
    episodes: int = 500
    max_steps: int = 2000          # safety cap per game
    stick_count: int = 3

    gamma: float = 0.99            # how much future reward counts (matches env shaping)
    learning_rate: float = 1e-3
    buffer_capacity: int = 50_000
    batch_size: int = 64
    min_replay: int = 1_000        # don't learn until the memory has this many transitions

    epsilon_start: float = 1.0     # start fully exploratory...
    epsilon_end: float = 0.05      # ...end mostly exploiting what's learned
    epsilon_decay_steps: int = 50_000

    target_update: int = 1_000     # copy online->target every this many steps

    save_path: str = storage.DEFAULT_MODEL_PATH
    save_every: int = 25           # checkpoint every N episodes
    log_every: int = 10            # print progress every N episodes
    resume: bool = False
    seed: Optional[int] = None


def select_action(network: QNetwork, observation: np.ndarray, epsilon: float) -> int:
    """Epsilon-greedy: random action with probability epsilon, else the best one."""
    if random.random() < epsilon:
        return random.randrange(NUM_ACTIONS)
    with torch.no_grad():
        q_values = network(torch.from_numpy(observation).unsqueeze(0))
    return int(q_values.argmax(dim=1).item())


def learn_step(online, target, optimizer, buffer, batch_size, gamma) -> float:
    """One gradient update toward better Q-values. Returns the loss."""
    observations, actions, rewards, next_observations, dones = buffer.sample(batch_size)

    observations = torch.from_numpy(observations)
    actions = torch.from_numpy(actions).unsqueeze(1)
    rewards = torch.from_numpy(rewards)
    next_observations = torch.from_numpy(next_observations)
    dones = torch.from_numpy(dones)

    # Q(s,a) the network currently predicts for the actions we actually took.
    predicted_q = online(observations).gather(1, actions).squeeze(1)

    # What it *should* have predicted: the reward plus the best achievable value
    # from the next state (estimated by the stable target network). If the game
    # ended (done=1), there is no future, so that term drops out.
    with torch.no_grad():
        best_next_q = target(next_observations).max(dim=1).values
        td_target = rewards + gamma * best_next_q * (1.0 - dones)

    loss = nn.functional.mse_loss(predicted_q, td_target)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    return float(loss.item())


def _linear_epsilon(step: int, config: TrainConfig) -> float:
    """Epsilon decays linearly from start to end over epsilon_decay_steps."""
    fraction = min(1.0, step / config.epsilon_decay_steps)
    return config.epsilon_start + fraction * (config.epsilon_end - config.epsilon_start)


def train(config: TrainConfig) -> list:
    """Run the full training loop. Returns per-episode history dicts."""
    if config.seed is not None:
        random.seed(config.seed)
        np.random.seed(config.seed)
        torch.manual_seed(config.seed)

    env = CaveInEnv(stick_count=config.stick_count, max_steps=config.max_steps)
    online = QNetwork()
    target = QNetwork()
    target.load_state_dict(online.state_dict())
    target.eval()
    optimizer = torch.optim.Adam(online.parameters(), lr=config.learning_rate)
    buffer = ReplayBuffer(config.buffer_capacity)
    metadata = storage.current_metadata(config.stick_count)

    start_episode = 0
    global_step = 0

    # Resume from a saved brain if asked (continues training, not just plays).
    if config.resume and os.path.exists(config.save_path):
        payload = storage.load_brain(
            config.save_path, online, optimizer=optimizer, expected_metadata=metadata
        )
        target.load_state_dict(online.state_dict())
        start_episode = payload.get("episode", 0)
        print(f"Resumed from {config.save_path} at episode {start_episode}.")

    recent_rewards = deque(maxlen=50)
    recent_sticks = deque(maxlen=50)
    recent_steps = deque(maxlen=50)
    history = []

    for episode in range(start_episode, start_episode + config.episodes):
        observation = env.reset()
        episode_reward = 0.0
        done = False
        info = {"sticks_collected": 0, "steps": 0}

        while not done:
            epsilon = _linear_epsilon(global_step, config)
            action = select_action(online, observation, epsilon)
            next_observation, reward, done, info = env.step(action)

            buffer.push(observation, action, reward, next_observation, float(done))
            observation = next_observation
            episode_reward += reward
            global_step += 1

            if len(buffer) >= config.min_replay:
                learn_step(online, target, optimizer, buffer,
                           config.batch_size, config.gamma)

            # Periodically refresh the stable target network.
            if global_step % config.target_update == 0:
                target.load_state_dict(online.state_dict())

        recent_rewards.append(episode_reward)
        recent_sticks.append(info["sticks_collected"])
        recent_steps.append(info["steps"])
        history.append({
            "episode": episode,
            "reward": episode_reward,
            "sticks": info["sticks_collected"],
            "steps": info["steps"],
            "epsilon": epsilon,
        })

        if (episode + 1) % config.log_every == 0:
            print(
                f"ep {episode + 1:>5} | "
                f"avg reward {np.mean(recent_rewards):7.2f} | "
                f"avg sticks {np.mean(recent_sticks):5.1f} | "
                f"avg steps {np.mean(recent_steps):7.1f} | "
                f"epsilon {epsilon:.3f} | buffer {len(buffer)}"
            )

        if (episode + 1) % config.save_every == 0:
            storage.save_brain(config.save_path, online, optimizer,
                               episode=episode + 1, epsilon=epsilon, metadata=metadata)

    # Final save.
    storage.save_brain(config.save_path, online, optimizer,
                       episode=start_episode + config.episodes,
                       epsilon=_linear_epsilon(global_step, config), metadata=metadata)
    print(f"Training done. Brain saved to {config.save_path}.")
    return history
