"""Tests for GridAnalyzer: neighbour calculation and obstacle detection."""

import pytest

from src.ai.pathfinding.path_calculator.grid_analyzer import GridAnalyzer
from src.utils.config import Direction, GRID_SIZE


# The four orthogonal directions, in the order PathCalculator supplies them.
DIRECTIONS = [
    Direction.UP.value,
    Direction.RIGHT.value,
    Direction.DOWN.value,
    Direction.LEFT.value,
]


@pytest.fixture
def analyzer(make_world):
    world = make_world(player_pos=(5, 5))
    return GridAnalyzer(world, DIRECTIONS), world


def test_corner_has_two_neighbours(analyzer):
    grid_analyzer, _ = analyzer
    # (0, 0) can only go RIGHT and DOWN; UP and LEFT are out of bounds.
    assert grid_analyzer.get_valid_neighbors((0, 0)) == [(1, 0), (0, 1)]


def test_interior_has_four_neighbours(analyzer):
    grid_analyzer, _ = analyzer
    neighbours = grid_analyzer.get_valid_neighbors((5, 5))
    assert set(neighbours) == {(5, 4), (6, 5), (5, 6), (4, 5)}


def test_neighbours_include_rocks(analyzer):
    # Rocks are still valid *cells* (the search decides separately whether to
    # remove them), so they must show up as neighbours.
    grid_analyzer, world = analyzer
    from src.cells import Rock
    world.grid[(6, 5)] = Rock((6, 5))
    assert (6, 5) in grid_analyzer.get_valid_neighbors((5, 5))


def test_is_rock(analyzer):
    grid_analyzer, world = analyzer
    from src.cells import Rock
    world.grid[(3, 3)] = Rock((3, 3))
    assert grid_analyzer.is_rock((3, 3)) is True
    assert grid_analyzer.is_rock((4, 4)) is False


def test_is_rock_out_of_bounds(analyzer):
    grid_analyzer, _ = analyzer
    assert grid_analyzer.is_rock((-1, -1)) is False
    assert grid_analyzer.is_rock((GRID_SIZE, GRID_SIZE)) is False
