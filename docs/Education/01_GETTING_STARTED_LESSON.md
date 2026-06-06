# Lesson 1 — Getting started & the big picture

## Goal

Run the game, understand how the project is organized, and grasp the single most
important idea in game programming: the **game loop**.

## Where it lives

- `main.py` — the entry point (where the program starts).
- `src/core/game.py` — the game loop.
- `Makefile` — shortcuts for common commands.

## Run it first

From the project folder:

```bash
make setup     # one time: creates a venv and installs dependencies
make run       # launches the game
```

(If you don't want to use `make`, the long form is in the main `README.md`.)

Play a few rounds with **W/A/S/D**. Press **Space** to clear a rock you're facing.
Getting a feel for the game makes the code much easier to read.

## The concept: a program that never sits still

A simple script runs top to bottom and stops. A game is different — it has to keep
reacting to you, frame after frame, until you quit. It does this with a **game
loop**: a `while` loop that repeats many times per second, and each time around it
does three things:

1. **Handle input/events** — did the player press a key or close the window?
2. **Update** — move things, apply the rules of the game.
3. **Render** — draw the current state to the screen.

That's it. Pong, Mario, and Cave In are all the same loop underneath.

## In the code

Open `src/core/game.py` and find `_main_loop`:

```python
def _main_loop(self) -> None:
    while self.running:
        self._handle_events()   # 1. input
        self._update()          # 2. rules
        self._render()          # 3. draw
```

Those three method calls are the whole heartbeat of the game. Everything else in
the project is in service of one of those three steps.

Now look at `main.py` — it's tiny:

```python
def main() -> None:
    game = Game()
    game.run()
```

It creates a `Game` object and tells it to run. (We'll cover what "objects" are in
Lesson 3 — for now, think of `Game` as a self-contained machine that knows how to
play itself.)

## How the project is organized

Code is split into small folders ("packages") under `src/`, each with one job:

- `src/core/` — the game itself (loop, world, drawing, menu, score).
- `src/cells/` — the things on the grid (player, rocks, sticks).
- `src/utils/` — shared settings and helpers.
- `src/ai/` — the computer players (pathfinding and, later, the neural network).

Splitting code this way is not decoration: it lets you understand one piece at a
time without holding the whole program in your head. That's the entire reason this
project is readable enough to learn from.

## Try it yourself

1. Run `make help` and read the list of commands. Try `make test` — it should
   report a bunch of passing tests. (We'll write tests-style thinking later.)
2. In `game.py`, read `_handle_events`, `_update`, and `_render`. In one sentence
   each, write down what they do. Don't worry about details yet.
3. Find where `FPS` is set (hint: it's a setting in `src/utils/config.py`). What do
   you think changing it would do?

## Takeaways

- A game is a **loop**: input → update → render, repeating forever.
- This project keeps that loop tiny and pushes the details into small packages.
- You can already run the game and the tests.

Next: [Lesson 2 — Representing the world](02_REPRESENTING_THE_WORLD_LESSON.md),
where we look at how the cave is stored in memory.
