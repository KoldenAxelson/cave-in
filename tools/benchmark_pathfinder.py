"""Headless benchmark for the Path Finder AI.

Runs full pathfinder playthroughs without opening a window and reports how many
steps (moves) and sticks each game took to reach a full board ("cave in").

Because the board's rocks and sticks are placed randomly, step counts vary from
game to game. Seeding the RNG makes each run reproducible, so this is the right
tool for measuring whether a code change actually affected AI behavior versus
ordinary board-to-board variance.

Usage:
    python tools/benchmark_pathfinder.py [num_runs] [--seed N] [--frame-cap N]

Examples:
    python tools/benchmark_pathfinder.py            # 20 runs, seeds 0..19
    python tools/benchmark_pathfinder.py 50         # 50 runs
    python tools/benchmark_pathfinder.py 1 --seed 7 # one specific seed
"""

import argparse
import os
import random
import statistics
import sys
import time

# Headless: never open a real window/audio device.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

# Make `import src...` work when run from the project root.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.world import GameWorld
from src.cells.player import Player
from src.core.stats import Stats
from src.ai.pathfinding.pathfinder import PathFinder
from src.utils.input_handler import set_ai_controller
import src.ai.pathfinding.pathfinder as pathfinder_module
import src.cells.rock as rock_module


# --- Count how many sticks get spent (rocks removed) per game -------------------
# stats.sticks_collected is the running *balance* (collecting adds, removing a
# rock subtracts), so it doesn't tell us how many sticks were spent. We wrap
# Rock's removal to count it.
_rocks_removed = {"count": 0}
_original_remove_rock = rock_module.Rock._remove_rock


def _counting_remove_rock(self, world):
    _rocks_removed["count"] += 1
    return _original_remove_rock(self, world)


rock_module.Rock._remove_rock = _counting_remove_rock


# --- Deterministic frame clock -------------------------------------------------
# The player and AI gate their actions on time.time() against a small cooldown.
# In the real game roughly 1/120 s passes per frame, which clears the cooldown
# once per frame and allows exactly one move per frame. We reproduce that by
# replacing time.time() with a counter that ticks once per simulated frame, so a
# benchmark run isn't tied to wall-clock speed.
_frame_clock = {"now": 0.0}
time.time = lambda: _frame_clock["now"]


def run_once(seed: int, frame_cap: int, stick_value=None):
    """Play one full game and return (steps, sticks_left, sticks_spent, finished).

    If stick_value is given, the pathfinder's STICK_VALUE weight is overridden
    for this run so we can compare different settings.
    """
    if stick_value is not None:
        pathfinder_module.STICK_VALUE = stick_value

    random.seed(seed)
    _frame_clock["now"] = 0.0
    _rocks_removed["count"] = 0

    world = GameWorld()          # NORMAL difficulty by default
    player = Player()
    stats = Stats()
    world.player = player
    world.stats = stats
    world.add(player)

    ai = PathFinder(world)
    set_ai_controller(ai)

    # With a lossy removal cost the greedy AI can "bankrupt" itself: spend sticks
    # until it can't afford to reach any remaining stick, then idle forever (the
    # board never fills, so the game never ends). We detect that stall — many
    # frames with no new move — and report the game as not finished.
    STALL_LIMIT = 300
    finished = False
    deadlocked = False
    moves_at_last_progress = stats.tiles_moved
    idle_frames = 0

    for _ in range(frame_cap):
        _frame_clock["now"] += 1.0   # advance one frame; clears the move cooldown
        world.update()               # drives Player.update() -> AI move/action
        if world.is_board_full():
            finished = True
            break

        if stats.tiles_moved == moves_at_last_progress:
            idle_frames += 1
            if idle_frames >= STALL_LIMIT:
                deadlocked = True
                break
        else:
            moves_at_last_progress = stats.tiles_moved
            idle_frames = 0

    set_ai_controller(None)
    return stats.tiles_moved, stats.sticks_collected, _rocks_removed["count"], finished, deadlocked


def _median(values):
    return int(statistics.median(values))


def sweep(weights, num_runs, frame_cap):
    """Run the same seeds at several STICK_VALUE weights and table the medians."""
    seeds = list(range(num_runs))
    print(f"Sweeping STICK_VALUE over {weights}  ({num_runs} seeds each)\n")
    print(f"{'STICK_VALUE':>12} {'med steps':>10} {'med sticks_left':>16} {'med sticks_spent':>17} {'deadlocked':>11}")
    for weight in weights:
        steps_list, left_list, spent_list = [], [], []
        deadlock_count = 0
        for seed in seeds:
            steps, sticks_left, sticks_spent, _, deadlocked = run_once(seed, frame_cap, stick_value=weight)
            steps_list.append(steps)
            left_list.append(sticks_left)
            spent_list.append(sticks_spent)
            deadlock_count += int(deadlocked)
        print(f"{weight:>12} {_median(steps_list):>10} "
              f"{_median(left_list):>16} {_median(spent_list):>17} "
              f"{deadlock_count}/{len(seeds):>10}")


def main():
    parser = argparse.ArgumentParser(description="Benchmark the Path Finder AI.")
    parser.add_argument("num_runs", nargs="?", type=int, default=20)
    parser.add_argument("--seed", type=int, default=None,
                        help="Run a single specific seed instead of 0..num_runs-1.")
    parser.add_argument("--frame-cap", type=int, default=200000,
                        help="Safety limit on frames per game.")
    parser.add_argument("--sweep", type=str, default=None,
                        help="Comma-separated STICK_VALUE weights to compare, e.g. 2,5,10")
    args = parser.parse_args()

    if args.sweep:
        weights = [int(w) for w in args.sweep.split(",")]
        sweep(weights, args.num_runs, args.frame_cap)
        return

    seeds = [args.seed] if args.seed is not None else list(range(args.num_runs))

    steps_list, sticks_list = [], []
    deadlock_count = 0
    print(f"{'seed':>6} {'steps':>8} {'sticks':>8} {'spent':>7} {'finished':>9} {'deadlocked':>11}")
    for seed in seeds:
        steps, sticks_left, sticks_spent, finished, deadlocked = run_once(seed, args.frame_cap)
        steps_list.append(steps)
        sticks_list.append(sticks_left)
        deadlock_count += int(deadlocked)
        print(f"{seed:>6} {steps:>8} {sticks_left:>8} {sticks_spent:>7} "
              f"{str(finished):>9} {str(deadlocked):>11}")

    if len(steps_list) > 1:
        print("\nSteps   -> "
              f"min {min(steps_list)}, median {int(statistics.median(steps_list))}, "
              f"mean {statistics.mean(steps_list):.0f}, max {max(steps_list)}")
        print("Sticks  -> "
              f"min {min(sticks_list)}, median {int(statistics.median(sticks_list))}, "
              f"mean {statistics.mean(sticks_list):.0f}, max {max(sticks_list)}")
        print(f"Deadlocked: {deadlock_count}/{len(seeds)} games")


if __name__ == "__main__":
    main()
