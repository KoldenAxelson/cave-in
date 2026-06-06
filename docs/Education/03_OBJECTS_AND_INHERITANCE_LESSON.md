# Lesson 3 — Objects and inheritance

## Goal

Understand classes, objects, inheritance, and **polymorphism** — the ideas that
let `Cell`, `Player`, `Rock`, and `Stick` share code while each behaving in its
own way.

## Where it lives

- `src/cells/cell.py` — the base `Cell` class.
- `src/cells/player.py`, `rock.py`, `stick.py` — the specific cell types.

## The concept: a blueprint and the things built from it

A **class** is a blueprint. An **object** (or "instance") is a thing built from
that blueprint. The blueprint says what data each object carries (its
*attributes*) and what it can do (its *methods*).

`Cell` is the blueprint for "something that sits on the grid." Every cell has a
`position` and a `color`, and can `draw` itself, `update` itself each frame, and be
`use`d by the player. Open `src/cells/cell.py`:

```python
@dataclass
class Cell:
    position: Position
    color: ColorType = Color.DARK_GRAY.value

    def update(self, world) -> None:
        pass    # base cell does nothing each frame

    def use(self, world) -> None:
        pass    # base cell does nothing when used
```

(`@dataclass` is a Python shortcut that writes the boilerplate "set up these
attributes when an object is created" for you. Without it you'd hand-write an
`__init__` method.)

## Inheritance: build on what exists

A plain `Cell` is just empty floor. A rock is *a kind of* cell that also blocks
movement and can be cleared. Rather than copy `Cell` and tweak it, `Rock`
**inherits** from `Cell` — it gets everything `Cell` has, then changes only what's
different. Open `src/cells/rock.py`:

```python
@dataclass
class Rock(Cell):                       # "Rock is a Cell"
    color: ColorType = Color.GRAY.value # rocks look different

    def use(self, world) -> None:       # rocks do something when used
        if self._can_remove_rock(world):
            self._remove_rock(world)
```

`Rock(Cell)` means "Rock is a Cell." It keeps `position`, `draw`, and `update` from
`Cell`, overrides `color`, and gives `use` real behavior (spend sticks, clear the
rock). `Stick` does the same idea: using it collects the stick. `Player` inherits
from `Cell` too, adding movement and a facing direction.

## Polymorphism: the same call, different behavior

Here's the payoff. The game often does this when the player presses Space:

```python
target_cell.use(world)
```

It doesn't check "is this a rock or a stick?" first. It just calls `use`, and
**each cell type runs its own version**:

- a `Rock`'s `use` clears the rock,
- a `Stick`'s `use` collects it,
- a plain `Cell`'s `use` does nothing.

This is **polymorphism** ("many shapes"): one instruction, many behaviors
depending on the object's actual type. It's what lets the game add new cell types
later without rewriting the code that uses them — a new cell just needs its own
`use`.

## A subtle point: `type(cell) == Cell` vs `isinstance`

Back in Lesson 2 we saw `is_board_full` use `type(cell) == Cell`. Now it makes
sense. Because `Rock`, `Stick`, and `Player` are all *kinds of* `Cell`,
`isinstance(rock, Cell)` is **True** — a rock *is* a cell. But "empty floor" means
a *plain* cell specifically, so the code checks `type(cell) == Cell`, which is only
true for the base class, not its subclasses. Picking the right check is exactly
the kind of detail OOP forces you to think about.

## Try it yourself

1. In a shell:
   ```python
   from src.cells import Cell, Rock, Stick
   r = Rock((2, 2))
   print(isinstance(r, Cell))   # True  — a Rock is a Cell
   print(type(r) == Cell)       # False — but it's not a *plain* Cell
   ```
2. Read `stick.py`'s `use`. It does three things in order — what are they? (Notice
   it triggers a *new* stick to appear elsewhere.)
3. Imagine a new cell type `Gem` worth bonus points. Which methods would you
   override, and which would you inherit unchanged?

## Takeaways

- A **class** is a blueprint; an **object** is an instance of it.
- **Inheritance** (`Rock(Cell)`) reuses a base class and changes only what differs.
- **Polymorphism** lets one call (`cell.use(world)`) do the right thing for each
  type — the key to extensible code.

Next: [Lesson 4 — Constants, enums, and type hints](04_CONSTANTS_ENUMS_AND_TYPES_LESSON.md).
