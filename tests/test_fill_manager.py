"""Tests for FillManager: the flood-fill safety check used by EASY mode.

A rock placement is "safe" only if every walkable cell stays reachable from the
player (i.e. the board remains a single connected region).
"""

import pytest

from src.utils.fill_manager import FillManager


@pytest.fixture
def fill_manager():
    return FillManager()


def test_open_board_placement_is_safe(make_world, fill_manager):
    world = make_world(player_pos=(5, 5))
    # Dropping a rock in open space leaves everything connected.
    assert fill_manager.is_safe_rock_position(world, (2, 2)) is True


def test_placement_that_seals_a_corner_is_unsafe(make_world, fill_manager):
    # (0,0)'s only neighbours are (1,0) and (0,1). With (0,1) already a rock,
    # adding a rock at (1,0) would isolate the (0,0) corner -> two regions.
    world = make_world(player_pos=(9, 9), rocks=[(0, 1)])
    assert fill_manager.is_safe_rock_position(world, (1, 0)) is False


def test_safe_elsewhere_even_with_existing_rock(make_world, fill_manager):
    # Same board as above, but a rock in the open middle keeps one region.
    world = make_world(player_pos=(9, 9), rocks=[(0, 1)])
    assert fill_manager.is_safe_rock_position(world, (5, 5)) is True


def test_no_player_is_never_safe(make_world, fill_manager):
    world = make_world(player_pos=(5, 5))
    world.player = None
    assert fill_manager.is_safe_rock_position(world, (2, 2)) is False
