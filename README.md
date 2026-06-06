# Cave In

A small grid-based puzzle game written in Python with Pygame. You explore a cave,
collect sticks, and use them to clear rocks out of your way. It also doubles as a
learning resource: the code is organized into small, readable packages so you can
poke around and see how a simple game is put together.

## Overview

Cave In can run in three ways, selectable from the start menu:

- **Normal Mode** — you play with the keyboard.
- **Path Finder** — a hand-written search AI collects sticks on its own.
- **Neural Net** — a neural network that *learns* to play through practice
  (reinforcement learning). You train it yourself; see
  [Machine-learning controller](#machine-learning-controller) below.

## Game Mechanics

1. Move around a grid-based cave.
2. Collect sticks (brown squares) to increase your score.
3. Spend a stick to remove a rock (gray square) blocking your path. The cost is
   set by `ROCK_REMOVAL_COST` (1 by default).
4. Plan carefully — if you box yourself in, the game ends.

The cave-in (a full board) is inevitable; the goal is to reach it in as few
steps as possible.

## Getting Started

You need Python 3.7+ installed. The project uses a virtual environment (venv) and
a single dependency, `pygame`.

```bash
git clone https://github.com/KoldenAxelson/cave-in.git
cd cave-in
python -m venv venv
source venv/bin/activate
pip install pygame
python main.py
```

When the game starts you will see a menu. Use the Up/Down arrow keys to move
between options and Enter to choose one.

## Controls

- **W / A / S / D** — move up / left / down / right
- **Space** — spend a stick to remove the rock you are facing
- **Esc** — restart the game (to quit, close the window)

## How It Works (a quick tour for learners)

Everything lives under `src/`, split into small packages. Each one has a single
job, which makes the code easier to follow:

- **`src/core/`** — the game itself: the main loop and state (`game.py`), the
  world/grid (`world.py`), drawing to the screen (`renderer.py`), the start menu
  (`menu.py`), and score tracking (`stats.py`).
- **`src/cells/`** — the things that sit on the grid. `cell.py` is the base
  class; `player.py`, `rock.py`, and `stick.py` are the specific cell types.
- **`src/utils/`** — shared helpers: all the constants, enums, and type aliases
  live in `config.py`; `input_handler.py` reads the keyboard; `player_interface.py`
  gives the AI a clean way to ask about and move the player; `fill_manager.py`
  helps place rocks safely.
- **`src/ai/`** — the AI side. `ai_interface.py` is an abstract base class that
  any AI must implement (so the game does not care which AI it is talking to).
  `ai/pathfinding/` is the search-based `PathFinder` (its `path_calculator/`
  subpackage does the route finding and scoring). `ai/learning/` is the
  neural-network agent: the training environment, the network ("the brain"),
  the trainer, brain save/load, and the play-time controller.

`main.py` at the project root just creates a `Game` and runs it.

### Tuning knobs

A few gameplay constants in `config.py` are worth knowing about:

- `STICK_COUNT` — how many sticks are on the board at once. At `1` there is no
  routing decision; raise it to give an agent a real choice of which stick to
  chase next.
- `ROCK_REMOVAL_COST` — how many sticks it takes to clear a rock (see Game
  Mechanics).
- `STICK_VALUE` — how many steps the pathfinder treats one rock removal as being
  worth when deciding whether to dig through or go around.

## AI Notes

### Path Finder (work in progress)

The Path Finder mode runs and plays a game through to completion — a bug where a
`Direction` enum member was used instead of its value was just fixed. It steers
toward sticks and clears rocks on its way. It is still labeled a work in progress
because its decision-making hasn't been formally checked for optimality and a
couple of internal pieces are worth revisiting (see Known Issues). Treat it as a
solid learning example of pathfinding rather than a tuned, finished AI.

### Neural Net

A reinforcement-learning agent that learns to play by practising, rather than
following hand-written rules. It sees the raw board and chooses raw moves
(up/down/left/right or "use") — there is no pathfinding involved, so it has to
discover navigation on its own. See
[Machine-learning controller](#machine-learning-controller) for how to train and
run it.

## Machine-learning controller

This is an optional, more advanced part of the project. The full design — written
for people new to machine learning, with the concepts explained — is in
[docs/ML_CONTROLLER_PLAN.md](docs/ML_CONTROLLER_PLAN.md).

**Extra dependencies** (not needed for Normal/Path Finder play):

```bash
pip install -r requirements-ml.txt   # numpy + PyTorch (CPU is fine)
```

**1. Train a brain.** This runs headless (no window), plays thousands of games,
and saves the learned network ("the brain") to `models/cave_in_dqn.pt`. You can
quit and resume any time — progress is checkpointed.

```bash
python tools/train_dqn.py --episodes 2000      # train from scratch
python tools/train_dqn.py --resume             # continue an existing brain
```

Watch the printed `avg reward` and `avg sticks` climb as it learns. (Training
takes a while on CPU; the agent spends the early episodes mostly exploring.)

**2. Evaluate it** against the path finder on identical boards:

```bash
python tools/evaluate_agents.py --seeds 50
```

**3. Play it.** Choose **Neural Net** in the start menu. It loads the saved brain
automatically (and plays randomly if you haven't trained one yet).

How it learns, briefly: it earns reward for collecting sticks, a small penalty
per step (so it prefers shorter routes), and a policy-preserving nudge toward the
nearest stick to speed up learning. The trainer uses standard Deep Q-Network
techniques (experience replay, epsilon-greedy exploration, a target network).
The brain trains under whatever `STICK_COUNT` / board settings are in `config.py`,
and a saved brain records those settings so it won't be loaded against a
mismatched board.

## Technical Details

- Built with Python and Pygame.
- Grid-based movement on a fixed-size grid.
- A viewport/camera that can follow the player.
- A cell-based design (one class per cell type) that is easy to extend.
- The AI talks to the game through a small abstract interface, so new AI
  strategies can be dropped in without changing the core game.

## Running the Tests

The project has a `pytest` suite covering the pure game logic — movement rules,
pathfinding/BFS, the flood-fill safety check, position scoring, stat formatting —
plus the ML pieces (training environment, network, brain save/load). The tests
run headless (no window opens), so they work anywhere. The ML tests skip
automatically if PyTorch isn't installed.

```bash
source venv/bin/activate   # if not already active
pip install pytest
pytest
```

The test files live in `tests/`, with one file per area (e.g.
`tests/test_pathfinding.py`). They are written to double as readable examples of
how each piece is meant to behave.

## Code Style

The code is meant to be read, so it follows a consistent style. See
[CONVENTIONS.md](CONVENTIONS.md) for the naming, comment, and docstring rules
used throughout the project.

## Known Issues

- **Path Finder optimality is unverified.** It runs and completes games, but its
  move quality hasn't been formally measured. Two spots are worth a second look:
  the binary search over rock count in `grid_scanner.py` (its scoring may not be
  monotonic in the way binary search assumes), and the full path recomputation
  every frame in `pathfinder.update()`.
- **Neural Net needs training first.** Until you run `tools/train_dqn.py`, the
  Neural Net menu option plays on a random (untrained) network and performs
  poorly. How good it gets after training depends on how long you train.

## Contributing

Contributions are welcome, especially if you are learning. Good places to start:

- Improving or optimizing the Path Finder.
- Trying out a learning-based AI.
- Tidying up code or documentation.

The usual flow: fork the repo, create a branch, commit your changes, and open a
pull request.

## A note on AI usage

Some of the documentation and routine boilerplate in this project was written
with AI assistance, while the game's design and core logic are human-directed.
Mentioning it here just to be upfront.

## Credits

Created by Kolden Axelson.

---

Made with Python, Pygame, and a bit of patience.
