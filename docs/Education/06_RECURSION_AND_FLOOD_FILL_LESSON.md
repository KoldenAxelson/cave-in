# Lesson 6 — Recursion and flood fill

## Goal

Understand **recursion** (a function that calls itself) by reading a real, useful
algorithm: the **flood fill** that checks whether placing a rock would trap the
player.

## Where it lives

- `src/utils/fill_manager.py` — the whole flood-fill safety check.

## The concept: a function that calls itself

Recursion sounds mind-bending but it's just a function that solves a big problem by
calling itself on smaller pieces. Every recursion needs two things:

1. A **base case** — a situation simple enough to answer immediately (stops the
   recursion).
2. A **recursive case** — break the problem into smaller versions and call yourself.

The classic mental model is exploring a maze: "to explore from where I'm standing,
mark this spot, then explore each neighbor the same way." Each "explore each
neighbor" is the function calling itself.

## The problem we're solving

Cave In has an "easy" mode that refuses to drop a rock if it would seal off part of
the cave and trap the player. To check that, we need to answer: *"starting from the
player, can you still reach every open cell?"* That's a **connectivity** question,
and flood fill answers it.

## In the code

Open `src/utils/fill_manager.py` and read `_flood_fill_region`:

```python
def _flood_fill_region(self, position, visited, grid):
    if position in visited or not self._can_move_to(position, grid):
        return set()                 # BASE CASE: stop here

    region = {position}              # this cell is reachable
    visited.add(position)            # remember we've been here

    for delta_x, delta_y in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
        neighbour = (position[0] + delta_x, position[1] + delta_y)
        region.update(self._flood_fill_region(neighbour, visited, grid))

    return region
```

Walk through it:

- **Base case:** if we've already visited this cell, or it's a wall/rock/off-grid,
  return an empty set — nothing new to add. This is what stops the function from
  recursing forever.
- **Recursive case:** record this cell, mark it visited, then call ourselves on all
  four neighbors and merge whatever *they* can reach. The `visited` set is shared
  across all the calls, which is how we avoid going in circles.

The result is the **set of all cells reachable** from the starting point — one
connected "region." Like dropping ink on a tile and watching it spread until it
hits walls.

## From flood fill to a safety check

Now read `is_safe_rock_position`:

```python
def is_safe_rock_position(self, world, candidate_position) -> bool:
    if not world.player:
        return False
    walkable_grid = self._create_grid(world, candidate_position)
    regions = self._find_connected_regions(walkable_grid, world.player.position, world)
    return len(regions) == 1
```

The logic is elegant:

1. Pretend the rock is already placed (`_create_grid` marks that cell as blocked).
2. Flood-fill from the player to find everything still reachable — that's the first
   region. Then scan for any cells the fill *didn't* reach; each is a separate,
   cut-off region.
3. If there's exactly **one** region, the whole cave is still connected → safe. More
   than one region means the rock would create an island → unsafe, don't place it.

A whole "don't trap the player" rule, expressed as "count the regions after flood
fill." That's the power of picking the right algorithm.

## A caution about recursion

Recursion is elegant but each self-call uses a bit of memory (the "call stack").
On a 10×10 grid that's fine — at most 100 cells deep. On a giant grid you could hit
Python's recursion limit and crash. Many real programs rewrite flood fill as a loop
with an explicit list of "cells to visit" for exactly this reason. Knowing when
recursion is safe is part of using it well. (You'll see the loop-based cousin of
this — breadth-first search — in the very next lesson.)

## Try it yourself

1. On paper, draw a 3×3 grid, put the player in a corner, and flood-fill by hand,
   numbering cells in the order the recursion would visit them. Notice how
   `visited` stops you from revisiting.
2. In `_flood_fill_region`, the four neighbor deltas are up/right/down/left. What
   would happen to the "reachability" meaning if you *added* diagonal deltas like
   `(1, 1)`? Would the player actually be able to move that way? (Check Lesson 5.)
3. Run `make test` and find the flood-fill tests (`tests/test_fill_manager.py`).
   Read one — it sets up a board that *would* trap the player and asserts the check
   returns `False`.

## Takeaways

- **Recursion** = base case + a function calling itself on smaller pieces.
- **Flood fill** finds every cell reachable from a start point.
- Counting regions after a flood fill answers "would this rock trap the player?" —
  a real feature built from a classic algorithm.
- Recursion is elegant but watch the depth; loops are the alternative.

Next: [Lesson 7 — Pathfinding with breadth-first search](07_PATHFINDING_WITH_BFS_LESSON.md).
