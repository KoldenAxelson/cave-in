# Lesson 2 — Representing the world

## Goal

Understand how the cave is stored using **tuples** and **dictionaries**, and why
choosing the right data structure makes the rest of the program simple.

## Where it lives

- `src/core/world.py` — the `GameWorld` that holds the grid.
- `src/utils/config.py` — `GRID_SIZE` and the `Position` type.

## The concept: a map from coordinates to contents

The cave is a 10×10 grid. We need to answer questions like "what's at column 3,
row 7?" constantly. How should we store that?

You might reach for a list of lists (`grid[row][column]`). That works, but this
project uses a **dictionary** instead, where the *key* is a coordinate pair and
the *value* is whatever sits there:

```python
grid = {
    (0, 0): <a cell>,
    (0, 1): <a cell>,
    ...
    (9, 9): <a cell>,
}
```

A coordinate like `(3, 7)` is a **tuple** — an ordered, unchangeable little group
of values. Tuples are perfect for coordinates: a position is always exactly two
numbers, and you never want `(3, 7)` to secretly change into something else.
Because tuples are unchangeable, Python lets you use them as dictionary keys
(lists, which *can* change, are not allowed as keys).

So the whole world is "a dictionary from position-tuples to cell-objects." Looking
something up is then just `grid[(3, 7)]`.

## In the code

Open `src/core/world.py`. The grid is built when the world is created:

```python
self.grid.update({
    position: Cell(position)
    for position in product(range(GRID_SIZE), range(GRID_SIZE))
})
```

A couple of things to unpack:

- `product(range(GRID_SIZE), range(GRID_SIZE))` produces every `(column, row)`
  pair from `(0,0)` to `(9,9)` — all 100 positions. (`product` comes from Python's
  `itertools`; it's the pairing of every value in the first range with every value
  in the second.)
- `{position: Cell(position) for position in ...}` is a **dictionary
  comprehension** — a compact way to build a dict by looping. Read it as: "for
  each position, make an entry mapping that position to a fresh empty `Cell`."

So the world starts as 100 empty cells. Then a few sticks (and rocks) are placed
on top by replacing some entries.

Look at how the world answers a question like "is the board full?":

```python
def is_board_full(self) -> bool:
    empty_positions = [
        position for position, cell in self.grid.items()
        if type(cell) == Cell
    ]
    return len(empty_positions) == 0
```

`self.grid.items()` gives you each `(position, cell)` pair. The list comprehension
keeps only the positions whose cell is a *plain* empty `Cell` (more on the
different cell types in Lesson 3). If there are none left, the board is full.

## Why this matters

The data structure you pick shapes every other piece of code. Because the world is
a dictionary keyed by position:

- "What's here?" is a one-line lookup.
- "Put a rock here" is a one-line assignment: `grid[(3, 7)] = Rock((3, 7))`.
- Looping over the whole board is `for position, cell in grid.items()`.

Good data modeling is quiet but powerful: it removes whole categories of fiddly
code before you ever write them.

## Try it yourself

1. In a Python shell (`make run` not needed), import and poke at the world:
   ```python
   from src.core.world import GameWorld
   w = GameWorld()
   print(len(w.grid))          # how many cells?
   print(w.grid[(0, 0)])       # what's in a corner?
   ```
2. Why can't we use a list like `[3, 7]` as a dictionary key, but `(3, 7)` is fine?
   (Hint: one of them can change after creation.)
3. `is_board_full` uses `type(cell) == Cell` rather than `isinstance(cell, Cell)`.
   We'll see why in the next lesson — make a guess now and check later.

## Takeaways

- **Tuples** are fixed little groups — ideal for coordinates and usable as dict
  keys.
- **Dictionaries** map keys to values; here, positions to cells.
- Modeling the world as `{position: cell}` makes lookups, placement, and iteration
  trivial.

Next: [Lesson 3 — Objects and inheritance](03_OBJECTS_AND_INHERITANCE_LESSON.md),
where we find out what those "cells" actually are.
