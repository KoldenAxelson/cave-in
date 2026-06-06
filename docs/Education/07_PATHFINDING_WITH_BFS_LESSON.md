# Lesson 7 — Pathfinding with breadth-first search

## Goal

Understand how a computer finds the shortest route across the cave using
**breadth-first search (BFS)** — the core of the Path Finder AI.

## Where it lives

- `src/ai/pathfinding/path_calculator/grid_analyzer.py` — finding neighbors.
- `src/ai/pathfinding/path_calculator/path_search.py` — the BFS itself.
- `src/ai/pathfinding/pathfinder.py` — the AI that uses it to play.

## The concept: the grid is secretly a graph

A **graph** is just "things, and connections between them." Our grid is a graph:
each cell is a node, and two cells are connected if you can step between them. Once
you see the grid as a graph, "find a path to the stick" becomes the classic
problem "find a route between two nodes."

**Breadth-first search** finds the *shortest* such route. The idea: explore
outward from the start in rings. First all cells 1 step away, then all cells 2 steps
away, and so on. Because you expand evenly in all directions, the very first time
you reach the goal, you must have arrived by a shortest path.

The mechanism is a **queue** (first-in, first-out, like a line at a counter):

1. Put the start cell in the queue.
2. Take the front cell out. If it's the goal, done.
3. Otherwise add its unvisited neighbors to the *back* of the queue.
4. Repeat.

The queue naturally enforces "finish everything at distance N before touching
distance N+1," which is what makes the path shortest.

> Compare with Lesson 6: flood fill and BFS both spread outward over the grid.
> Flood fill used recursion and only cared *which* cells are reachable. BFS uses a
> queue and also remembers *how to get there*, the shortest way.

## In the code

First, neighbors. Open `grid_analyzer.py`:

```python
def get_valid_neighbors(self, pos):
    return [next_pos for delta_x, delta_y in self.directions
            if (next_pos := self._get_next_position(pos, delta_x, delta_y))
            and self._is_valid_cell(next_pos)]
```

This returns the in-bounds cells next to `pos`. (`self.directions` is the four
up/right/down/left deltas — the same four from earlier lessons.)

Now the search. Open `path_search.py` and look at the rock-free branch of
`breadth_first_search`:

```python
queue = [(start, [start])]      # each entry: (cell, path-taken-to-get-here)
visited = {start}

while queue:
    current, path = queue.pop(0)        # take from the FRONT (FIFO)
    if current == target_pos:
        return path                     # first arrival = shortest path

    for next_pos in self.grid_analyzer.get_valid_neighbors(current):
        if next_pos not in visited and not self.grid_analyzer.is_rock(next_pos):
            visited.add(next_pos)
            queue.append((next_pos, path + [next_pos]))   # add to the BACK
```

Every queue entry carries both *where you are* and *the path you took to get
there*. When you reach the target, that stored path is your answer. The `visited`
set stops you re-exploring cells (same job it did in flood fill). `pop(0)` takes
from the front and `append` adds to the back — that front/back discipline is the
whole reason BFS finds the shortest path.

## Beyond plain BFS

The same file has a second mode that allows the agent to *remove* rocks along the
way (spending sticks), searching for the cheapest path when a rock-free one is
blocked. And `pathfinder.py` is the player that ties it together: each time it
needs a goal it picks the nearest stick, asks for a path, and then walks that path
one step at a time, exposing each step through the same `get_movement()` seam from
Lesson 5.

You don't need to digest every line of that today. The important leap is: **a smart
game character is often just a classic graph algorithm plus a loop that follows the
result.**

## A note on "smart"

It's tempting to call the Path Finder "AI," and people do. But notice there's no
learning here — it's a fixed, hand-written procedure that computes the shortest
path every time. It's *clever*, but it can't get better or adapt. That limitation
is exactly the motivation for the next part of the course: an agent that **learns**
rather than follows rules.

## Try it yourself

1. Play "Path Finder" mode (`make run`, choose it) and watch it route around rocks.
2. On paper, BFS a tiny grid: mark the start, then write `1` on its neighbors, `2`
   on *their* unvisited neighbors, and so on until you hit the goal. The numbers are
   distances; trace back from the goal along decreasing numbers to read the path.
3. Why does taking from the **front** of the queue matter? What kind of path would
   you get if you took from the *back* instead (turning the queue into a stack)?
   (That's depth-first search — it finds *a* path, not necessarily the shortest.)
4. Run the pathfinding tests (`tests/test_pathfinding.py`) and read one that checks
   the path goes *around* a rock.

## Takeaways

- A grid is a **graph**; pathfinding is route-finding on that graph.
- **BFS** explores in rings using a **queue**, so the first time it reaches the
  goal it has the **shortest** path.
- A `visited` set prevents loops; carrying the path in each queue entry lets you
  recover the route.
- This AI is clever but *fixed* — it doesn't learn. That sets up the rest of the
  course.

Next: [Lesson 8 — Interfaces and swappable brains](08_INTERFACES_AND_SWAPPABLE_BRAINS_LESSON.md).
