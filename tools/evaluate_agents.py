"""Head-to-head evaluation: the trained neural agent vs the path finder.

Both agents are run on the *same* set of seeded boards, headless, using the same
one-decision-per-frame harness as the benchmark, so the comparison is fair and
reproducible. We report, per agent:

- how many games it actually finished (reached the cave-in),
- the median step count over the games it finished (lower is better),
- the median sticks collected,
- how many games it deadlocked / stalled out.

Run:
    python tools/evaluate_agents.py                 # 20 seeds, 3 sticks
    python tools/evaluate_agents.py --seeds 50
    python tools/evaluate_agents.py --brain-path models/cave_in_dqn.pt

If no trained brain exists yet, the neural agent runs on a random network (so the
harness can be checked before training finishes) and is clearly marked untrained.
"""

import argparse
import os
import random
import statistics
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core.world import GameWorld
from src.cells.player import Player
from src.core.stats import Stats
from src.ai.pathfinding.pathfinder import PathFinder
from src.utils.input_handler import set_ai_controller

# Deterministic per-frame clock (same trick as the benchmark): the agents gate on
# time.time() against a small cooldown; advancing a fake clock once per frame
# clears the cooldown each frame so each frame is exactly one decision.
_frame_clock = {"now": 0.0}
time.time = lambda: _frame_clock["now"]


def run_episode(make_controller, seed, stick_count, max_frames, stall_limit):
    """Play one game with the given controller; return (steps, sticks, finished, deadlocked)."""
    random.seed(seed)
    _frame_clock["now"] = 0.0

    world = GameWorld(stick_count=stick_count)
    player = Player()
    stats = Stats()
    world.player = player
    world.stats = stats
    world.add(player)

    controller = make_controller(world)
    set_ai_controller(controller)

    finished = False
    deadlocked = False
    moves_at_last_progress = 0
    idle_frames = 0

    for _ in range(max_frames):
        _frame_clock["now"] += 1.0
        world.update()
        if world.is_board_full():
            finished = True
            break
        if stats.tiles_moved == moves_at_last_progress:
            idle_frames += 1
            if idle_frames >= stall_limit:
                deadlocked = True
                break
        else:
            moves_at_last_progress = stats.tiles_moved
            idle_frames = 0

    set_ai_controller(None)
    return stats.tiles_moved, stats.sticks_collected, finished, deadlocked


def evaluate(make_controller, label, seeds, stick_count, max_frames, stall_limit):
    results = [
        run_episode(make_controller, seed, stick_count, max_frames, stall_limit)
        for seed in seeds
    ]
    finished_steps = [steps for steps, _, finished, _ in results if finished]
    sticks = [s for _, s, _, _ in results]
    finished_count = len(finished_steps)
    deadlocks = sum(1 for *_, dl in results if dl)

    median_steps = str(int(statistics.median(finished_steps))) if finished_steps else "n/a"
    median_sticks = int(statistics.median(sticks))
    print(f"{label:18} {finished_count:>3}/{len(seeds):<3}  "
          f"med_steps(finished)={median_steps:>6}  "
          f"med_sticks={median_sticks:>4}  deadlocked={deadlocks}")


def main():
    parser = argparse.ArgumentParser(description="Compare the neural agent and the path finder.")
    parser.add_argument("--seeds", type=int, default=20)
    parser.add_argument("--stick-count", type=int, default=3)
    parser.add_argument("--max-frames", type=int, default=20000)
    parser.add_argument("--stall-limit", type=int, default=300)
    parser.add_argument("--brain-path", type=str, default="models/cave_in_dqn.pt")
    args = parser.parse_args()

    seeds = list(range(args.seeds))
    print(f"Evaluating on {args.seeds} seeds (stick_count={args.stick_count})\n")
    print(f"{'agent':18} {'finished':>7}  {'steps':>20}  {'sticks':>11}  deadlocks")

    # Path finder (the baseline).
    evaluate(lambda world: PathFinder(world), "PathFinder",
             seeds, args.stick_count, args.max_frames, args.stall_limit)

    # Neural agent (lazy import so torch is only needed for this part).
    try:
        from src.ai.learning.neural_controller import NeuralController
    except ImportError:
        print("NeuralNet         skipped (PyTorch not installed)")
        return

    trained = os.path.exists(args.brain_path)
    label = "NeuralNet" if trained else "NeuralNet(untrained)"
    evaluate(lambda world: NeuralController(world, brain_path=args.brain_path), label,
             seeds, args.stick_count, args.max_frames, args.stall_limit)

    if not trained:
        print(f"\nNote: no brain at {args.brain_path} — neural results are from a "
              f"random (untrained) network. Train first with tools/train_dqn.py.")


if __name__ == "__main__":
    main()
