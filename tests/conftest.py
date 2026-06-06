"""Shared pytest fixtures and helpers for the Cave In test suite.

The tests exercise pure game logic (movement rules, pathfinding, flood-fill,
scoring, stat formatting) and never open a real window. Some modules import
pygame at the top, so we point SDL at its dummy ("headless") drivers *before*
pygame is imported anywhere. This lets the whole suite run on a machine with no
display, such as a CI server.
"""

import os

# Must be set before any module (via the imports below) pulls in pygame.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pytest

from src.utils.config import GRID_SIZE
from src.cells import Cell, Rock, Stick, Player
from src.core.stats import Stats
from src.core.world import GameWorld


def blank_grid():
    """Return a fresh grid where every position holds a plain (empty) Cell."""
    return {
        (column, row): Cell((column, row))
        for column in range(GRID_SIZE)
        for row in range(GRID_SIZE)
    }


@pytest.fixture
def make_world():
    """Factory for a fully-controlled GameWorld.

    GameWorld() normally scatters a random stick and rock on creation, which
    makes assertions non-deterministic. We build one and then replace its grid
    with a known layout so each test starts from an exact, predictable board.

    Args of the returned factory:
        player_pos:   where to place the Player.
        sticks:       starting value of stats.sticks_collected.
        rocks:        iterable of positions to fill with Rock.
        stick_positions: iterable of positions to fill with Stick.
    """
    def _make(player_pos=(0, 0), sticks=0, rocks=(), stick_positions=()):
        world = GameWorld()
        world.grid = blank_grid()
        world.stats = Stats(sticks_collected=sticks)

        player = Player(position=player_pos)
        world.player = player
        world.grid[player_pos] = player

        for rock_position in rocks:
            world.grid[rock_position] = Rock(rock_position)
        for stick_position in stick_positions:
            world.grid[stick_position] = Stick(stick_position)

        return world

    return _make
