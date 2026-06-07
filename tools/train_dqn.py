"""Command-line entry point for training the Cave In neural controller.

Examples:
    # Train from scratch with the default settings (3 sticks, 10x10):
    python tools/train_dqn.py

    # Train longer, saving to the default models/ location:
    python tools/train_dqn.py --episodes 2000

    # Continue training an existing brain:
    python tools/train_dqn.py --resume

The trained brain is written to models/cave_in_dqn.pt by default, and the game's
"Neural Net" menu option will pick it up automatically.

Requires the ML dependencies:  pip install -r requirements-ml.txt
"""

import argparse
import os
import sys

# Make `import src...` work when run from the project root.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Headless: training never opens a window.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.ai.learning.trainer import TrainConfig, train


def main():
    defaults = TrainConfig()
    parser = argparse.ArgumentParser(description="Train the Cave In DQN agent.")
    parser.add_argument("--episodes", type=int, default=defaults.episodes)
    parser.add_argument("--max-steps", type=int, default=defaults.max_steps)
    parser.add_argument("--stick-count", type=int, default=defaults.stick_count)
    parser.add_argument("--learning-rate", type=float, default=defaults.learning_rate)
    parser.add_argument("--batch-size", type=int, default=defaults.batch_size)
    parser.add_argument("--min-replay", type=int, default=defaults.min_replay,
                        help="Transitions to collect before learning starts.")
    parser.add_argument("--epsilon-decay-steps", type=int, default=defaults.epsilon_decay_steps,
                        help="Steps over which random exploration decays to its floor.")
    parser.add_argument("--save-path", type=str, default=defaults.save_path)
    parser.add_argument("--save-every", type=int, default=defaults.save_every)
    parser.add_argument("--log-every", type=int, default=defaults.log_every)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--resume", action="store_true",
                        help="Continue training the existing saved brain.")
    args = parser.parse_args()

    config = TrainConfig(
        episodes=args.episodes,
        max_steps=args.max_steps,
        stick_count=args.stick_count,
        learning_rate=args.learning_rate,
        batch_size=args.batch_size,
        min_replay=args.min_replay,
        epsilon_decay_steps=args.epsilon_decay_steps,
        save_path=args.save_path,
        save_every=args.save_every,
        log_every=args.log_every,
        seed=args.seed,
        resume=args.resume,
    )
    train(config)


if __name__ == "__main__":
    main()
