"""Integration tests for the BFS pathfinding via PathCalculator/PathSearch.

These build small, exact boards and assert on the paths the search returns.
"""

import pytest

from src.ai.pathfinding.path_calculator.path_calculator import PathCalculator
from src.utils.config import ROCK_REMOVAL_COST


def is_contiguous(path):
    """True if each step in the path moves exactly one orthogonal cell."""
    for (ax, ay), (bx, by) in zip(path, path[1:]):
        if abs(ax - bx) + abs(ay - by) != 1:
            return False
    return True


class TestPathWithoutRocks:
    def test_straight_line(self, make_world):
        world = make_world(player_pos=(0, 0))
        calculator = PathCalculator(world)
        path = calculator.find_path_without_rocks((0, 3))
        assert path[0] == (0, 0)
        assert path[-1] == (0, 3)
        assert len(path) == 4          # 4 cells: start + 3 steps
        assert is_contiguous(path)

    def test_start_equals_target(self, make_world):
        world = make_world(player_pos=(2, 2))
        calculator = PathCalculator(world)
        assert calculator.find_path_without_rocks((2, 2)) == [(2, 2)]

    def test_detours_around_a_rock(self, make_world):
        # Rock sits directly between start and target; the rock-free path must
        # go around it, so it is longer than the Manhattan distance.
        world = make_world(player_pos=(0, 0), rocks=[(1, 0)])
        calculator = PathCalculator(world)
        path = calculator.find_path_without_rocks((2, 0))
        assert path[0] == (0, 0) and path[-1] == (2, 0)
        assert (1, 0) not in path
        assert is_contiguous(path)
        assert len(path) == 5          # forced one-cell detour

    def test_returns_none_when_target_is_walled_off(self, make_world):
        # Surround the target with rocks; with no removals allowed it is
        # unreachable.
        world = make_world(player_pos=(0, 0),
                           rocks=[(5, 4), (5, 6), (4, 5), (6, 5)])
        calculator = PathCalculator(world)
        assert calculator.find_path_without_rocks((5, 5)) is None


class TestPathWithRocks:
    def test_breaks_straight_through_when_allowed(self, make_world):
        # The shortest route runs through one rock. With a removal budget the
        # search should prefer the short straight path over the longer detour.
        world = make_world(player_pos=(0, 0), rocks=[(1, 0)])
        calculator = PathCalculator(world)
        path = calculator.find_path_with_max_rocks(1, (2, 0))
        assert path == [(0, 0), (1, 0), (2, 0)]

    def test_reaches_walled_target_with_budget(self, make_world):
        world = make_world(player_pos=(5, 3),
                           rocks=[(5, 4), (5, 6), (4, 5), (6, 5)])
        calculator = PathCalculator(world)
        # Needs to remove the (5,4) rock to get in.
        path = calculator.find_path_with_max_rocks(1, (5, 5))
        assert path is not None
        assert path[0] == (5, 3) and path[-1] == (5, 5)


class TestRockCounting:
    def test_counts_rocks_on_path(self, make_world):
        world = make_world(player_pos=(0, 0), rocks=[(1, 0)])
        calculator = PathCalculator(world)
        assert calculator.count_rocks_in_path([(0, 0), (1, 0), (2, 0)]) == 1

    def test_no_rocks_on_clear_path(self, make_world):
        world = make_world(player_pos=(0, 0))
        calculator = PathCalculator(world)
        assert calculator.count_rocks_in_path([(0, 0), (0, 1), (0, 2)]) == 0


class TestFindSticks:
    def test_finds_all_sticks(self, make_world):
        world = make_world(player_pos=(0, 0), stick_positions=[(2, 2), (7, 8)])
        calculator = PathCalculator(world)
        assert set(calculator.find_sticks()) == {(2, 2), (7, 8)}

    def test_no_sticks(self, make_world):
        world = make_world(player_pos=(0, 0))
        calculator = PathCalculator(world)
        assert calculator.find_sticks() == []


class TestFindPathToPosition:
    # find_path_to_position derives its rock budget from sticks:
    # affordable removals == sticks_collected // ROCK_REMOVAL_COST.

    def test_cannot_afford_removal_forces_detour(self, make_world):
        # One short of the cost -> budget 0 -> must go around the rock.
        world = make_world(player_pos=(0, 0), rocks=[(1, 0)],
                           sticks=ROCK_REMOVAL_COST - 1)
        calculator = PathCalculator(world)
        path = calculator.find_path_to_position((2, 0))
        assert path is not None
        assert (1, 0) not in path

    def test_can_afford_one_removal_routes_through(self, make_world):
        # Exactly the cost -> budget 1 -> shortest route may go through the rock.
        world = make_world(player_pos=(0, 0), rocks=[(1, 0)],
                           sticks=ROCK_REMOVAL_COST)
        calculator = PathCalculator(world)
        path = calculator.find_path_to_position((2, 0))
        assert path == [(0, 0), (1, 0), (2, 0)]
