# Lesson 4 — Constants, enums, and type hints

## Goal

Learn three habits that make code readable and hard to break: centralizing
**constants**, using **enums** for fixed sets of choices, and adding **type hints**.

## Where it lives

- `src/utils/config.py` — the whole settings file. Open it and keep it visible.

## Constants: name your magic numbers

A "magic number" is a bare value sitting in code with no explanation — `10`, `0.2`,
`128`. Six months later nobody remembers what it meant. The fix is to give it a
name in one place:

```python
GRID_SIZE: int = 10            # cells per row/column
PLAYER_MOVE_COOLDOWN: float = 0.002
STICK_COUNT: int = 1           # how many sticks on the board at once
ROCK_REMOVAL_COST: int = 1     # sticks spent to clear a rock
```

Now `GRID_SIZE` appears all over the project, and if you ever want a 15×15 cave you
change it in exactly **one** place. Constants also document intent: `ROCK_REMOVAL_COST`
tells you what the number *means* in a way that a bare `1` never could.

## Enums: a fixed menu of choices

Some values should only ever be one of a small, known set. A direction is up,
right, down, left, or none — never "diagonal" or "banana." An **enum**
(enumeration) makes that set explicit. Look at `Direction`:

```python
class Direction(Enum):
    UP    = ( 0, -1)
    RIGHT = ( 1,  0)
    DOWN  = ( 0,  1)
    LEFT  = (-1,  0)
    NONE  = ( 0,  0)
```

Two nice things here:

1. The names are meaningful: you write `Direction.UP` instead of remembering that
   "up" is `(0, -1)`.
2. Each direction *carries its movement* as a `(dx, dy)` tuple in `.value`. So
   `Direction.RIGHT.value` is `(1, 0)` — add that to a position and you move right.

This is also a real bug-prevention tool. Earlier in this project's history there
was a crash because code referenced `Direction.EAST`, which doesn't exist. With an
enum, a typo like that fails loudly and immediately instead of silently
misbehaving. (The `Color` enum works the same way, naming RGB values like
`Color.RED`.)

## Type hints: say what goes in and out

Python doesn't force you to declare types, but you *can* annotate them, and it
makes code dramatically clearer. Notice the `: int`, `: float` above, and the
**type aliases** at the top of the file:

```python
Position:  TypeAlias = Tuple[int, int]       # an (x, y) coordinate
ColorType: TypeAlias = Tuple[int, int, int]  # an (r, g, b) color
PathType:  TypeAlias = List[Position]        # a sequence of positions
```

Now a function signature like `def try_move(self, world, delta: Position) -> bool`
reads almost like English: "give me a position-shaped delta, I'll return a
true/false." Type hints don't change how the program runs, but they help you (and
your editor) catch mistakes and understand unfamiliar code faster.

## Try it yourself

1. Open `config.py` and find every constant. For each, guess what would visibly
   change in the game if you doubled it. Then try changing `STICK_COUNT` to `3`,
   run `make run`, and see.
2. `Direction.RIGHT.value` is `(1, 0)`. In a shell, add it to a position:
   ```python
   from src.utils.config import Direction
   pos = (4, 4)
   dx, dy = Direction.RIGHT.value
   print((pos[0] + dx, pos[1] + dy))   # (5, 4)
   ```
3. Why is an enum safer than just using strings like `"up"`/`"down"` scattered
   around the code?

## Takeaways

- **Constants** name magic numbers and put settings in one editable place.
- **Enums** capture a fixed set of choices safely and can carry data (like a
  movement delta) with each name.
- **Type hints** document what functions expect and return, making code easier to
  read and harder to misuse.

Next: [Lesson 5 — The game loop and player input](05_THE_GAME_LOOP_AND_INPUT_LESSON.md),
where the pieces start moving.
