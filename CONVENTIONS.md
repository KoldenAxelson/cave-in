# Cave In — Code Conventions

This project doubles as a learning resource, so the code should be easy to read
on its own. These conventions apply to all cleanup work.

## Guiding principle

> Reading the code should explain *what* it does.
> Comments should explain what the code *can't* — the *why*, the non-obvious, the
> gotchas.

## Naming

- Prefer **explicit, descriptive names even when they are longer**.
  - `delta_x` / `delta_y` instead of `dx` / `dy`
  - `player_x` / `player_y` instead of `px` / `py`
  - `column` / `row` (or `grid_x` / `grid_y`) instead of bare `x` / `y` in loops
  - `distance` instead of `d`, `offset` is fine as-is
- Use full words over abbreviations (`position` not `pos`) **only for local
  variables and internal parameters** — see the "Do not rename" list below.
- Loop variables in comprehensions should also be descriptive where it aids
  clarity.

## Comments

- **Keep all docstrings.** Do not delete them. You may lightly reword a docstring
  if it is inaccurate, but the one-docstring-per-method style stays.
- **Inline `#` comments**: remove any that merely restate the code
  (e.g. `x += 1  # increment x`). Keep or add inline comments that explain
  *intent*, *edge cases*, or *why* something is done a particular way.

## Hard rules — do NOT do these

- **Do not change behavior.** This is a pure readability refactor.
- **Do not rename exported / public symbols**, because other modules depend on
  them by name:
  - class names (`Player`, `PathFinder`, …)
  - public method names (anything not prefixed with `_`)
  - config constants and enum members (`GRID_SIZE`, `Color.DARK_GRAY`,
    `Direction.UP`, …)
  Renaming **local variables and internal parameters is encouraged**.
- **Stay within your assigned directory.** Do not edit files outside it.
- Do not touch `venv/`, `__pycache__/`, or generated files.
- Preserve type hints; fix one only if it is clearly wrong.

## After editing

- Make sure every file you touched still compiles:
  `python3 -m compileall -q <your_dir>`
