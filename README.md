# Cave In

A small grid-based puzzle game written in Python with Pygame. You explore a cave,
collect sticks, and use them to clear rocks out of your way. It also doubles as a
learning resource: the code is organized into small, readable packages so you can
poke around and see how a simple game is put together.

## Overview

Cave In can run in two ways:

- **Normal Mode** — you play with the keyboard.
- **Path Finder** — an AI takes over and tries to collect sticks on its own.

There is also a longer-term idea (see below) of adding a learning-based AI, but
that part does not exist yet.

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
  `ai/pathfinding/` is the one real implementation: `PathFinder` decides moves,
  and the `path_calculator/` subpackage does the actual route finding and scoring.

`main.py` at the project root just creates a `Game` and runs it.

## AI Notes

### Path Finder (work in progress)

The Path Finder mode runs and plays a game through to completion — a bug where a
`Direction` enum member was used instead of its value was just fixed. It steers
toward sticks and clears rocks on its way. It is still labeled a work in progress
because its decision-making hasn't been formally checked for optimality and a
couple of internal pieces are worth revisiting (see Known Issues). Treat it as a
solid learning example of pathfinding rather than a tuned, finished AI.

### Neural Network mode (planned, not started)

A machine-learning AI that *learns* to play (rather than following hand-written
pathfinding rules) is an idea for the future. None of it is implemented yet —
there is no training code and no neural-network mode in the menu. It is listed
here only to show where the project might go.

## Technical Details

- Built with Python and Pygame.
- Grid-based movement on a fixed-size grid.
- A viewport/camera that can follow the player.
- A cell-based design (one class per cell type) that is easy to extend.
- The AI talks to the game through a small abstract interface, so new AI
  strategies can be dropped in without changing the core game.

## Running the Tests

The project has a `pytest` suite covering the pure game logic — movement rules,
pathfinding/BFS, the flood-fill safety check, position scoring, and stat
formatting. The tests run headless (no window opens), so they work anywhere.

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
- The Neural Network mode mentioned above is not implemented.

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
