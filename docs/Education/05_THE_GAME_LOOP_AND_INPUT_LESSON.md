# Lesson 5 — The game loop and player input

## Goal

Follow a single keypress from your keyboard all the way to the player moving on
screen, and understand how the loop, input, and movement rules fit together.

## Where it lives

- `src/core/game.py` — the loop and state transitions.
- `src/utils/input_handler.py` — reading input.
- `src/cells/player.py` — what the player does with that input.

## Recap: the three steps

From Lesson 1, each frame the loop runs `_handle_events`, `_update`, `_render`.
Let's zoom into how input flows through them.

## Step 1: events vs. held keys

There are two kinds of input, and games use both:

- **Events** are one-off things: the window's close button, a key being pressed
  *this instant*. `_handle_events` in `game.py` checks for the quit event.
- **Held state** is "is this key down right now?" — used for continuous movement.

Open `src/utils/input_handler.py`. Movement reads held keys:

```python
def _get_horizontal_movement(pressed_keys) -> int:
    return pressed_keys[pygame.K_d] - pressed_keys[pygame.K_a]
```

That line is a neat trick. `pressed_keys[...]` is `1` if the key is down, else `0`.
So pressing **D** (right) gives `1 - 0 = 1`, **A** (left) gives `0 - 1 = -1`, both
or neither gives `0`. One subtraction turns two keys into a direction.

## Step 2: input becomes a decision

`get_movement()` returns a `(dx, dy)` delta. But notice this, near the top:

```python
def get_movement() -> Position:
    if ai_controller:
        return ai_controller.get_movement()
    return _get_keyboard_movement()
```

This is a quietly important design choice. The rest of the game asks
`get_movement()` "which way?" and **doesn't care whether the answer came from a
human or a computer player.** When you pick "Path Finder" or "Neural Net" in the
menu, an `ai_controller` is set and the exact same code path drives the player.
We'll lean on this heavily in the AI lessons.

## Step 3: the player acts (with a cooldown)

Open `src/cells/player.py` and read `update`:

```python
def update(self, world) -> None:
    if time.time() - self.last_move_time < self.move_cooldown:
        return                       # too soon since last move — wait
    movement_delta = get_movement()
    if any(movement_delta):
        self.update_facing(movement_delta)
        self.try_move(world, movement_delta)
    if use_action():
        self.try_use_facing_cell(world)
```

Two ideas worth naming:

- **Cooldown.** The loop runs ~120 times a second, but you don't want the player
  teleporting across the board that fast. `move_cooldown` enforces a minimum time
  between moves, so holding a key gives smooth, controllable motion. This is a very
  common game-feel technique.
- **Facing.** Moving sets which way the player is facing (`update_facing`). That
  matters because using Space acts on the cell *in front of you*
  (`try_use_facing_cell`) — so to grab a stick you turn toward it, then use.

Finally, `try_move` checks the rules before committing:

```python
def _is_valid_move(self, world, target_position) -> bool:
    target_cell = world.grid[target_position]
    return (target_position != self.position and
            isinstance(target_cell, Cell) and
            type(target_cell) == Cell)
```

You can only step onto a *plain empty cell* (remember `type(...) == Cell` from
Lesson 3) — not onto a rock or stick. That single rule is what makes rocks
obstacles and sticks something you "use" rather than walk over.

## The full path of one keypress

1. You hold **D**.
2. `_update` → `player.update` → `get_movement()` → `_get_keyboard_movement` reads
   the key and returns `(1, 0)`.
3. Cooldown permits it, so `update_facing((1,0))` faces right and
   `try_move(world, (1,0))` checks the target cell.
4. If it's empty floor, the player's position updates and the move count ticks up.
5. `_render` draws the new state. You see the player one cell to the right.

That round trip happens up to 120 times per second.

## Try it yourself

1. In `config.py`, set `PLAYER_MOVE_COOLDOWN` to `0.3` and run the game. How does
   movement feel? Now try `0.0`. This single number is a big lever on game feel.
2. Trace `use_action()` in `input_handler.py`. It only returns `True` on the frame
   Space is *first* pressed, not while held. Why would holding Space-to-repeat be
   annoying here? (Hint: you'd dump all your sticks at once.)
3. The "AI or keyboard, same code" trick is the seam the whole AI half of this
   project plugs into. Keep it in mind for Lesson 8.

## Takeaways

- Input comes as **events** (one-offs) and **held-key state** (continuous).
- A **cooldown** converts a 120 Hz loop into comfortable, fair movement.
- `get_movement()` hides *who* is deciding — human or AI — behind one function,
  which is what makes computer players possible without touching the game.

Next: [Lesson 6 — Recursion and flood fill](06_RECURSION_AND_FLOOD_FILL_LESSON.md).
