"""Tests for PositionScorer: distance, validity, rock density and scoring."""

import pytest

from src.ai.pathfinding.path_calculator.position_scorer import PositionScorer
from src.utils.config import GRID_SIZE


@pytest.fixture
def scorer(make_world):
    world = make_world(player_pos=(5, 5))
    return PositionScorer(world), world


class TestManhattanDistance:
    def test_basic(self, scorer):
        position_scorer, _ = scorer
        assert position_scorer.get_manhattan_distance((0, 0), (3, 4)) == 7

    def test_same_point_is_zero(self, scorer):
        position_scorer, _ = scorer
        assert position_scorer.get_manhattan_distance((2, 2), (2, 2)) == 0


class TestFindClosestStick:
    def test_picks_nearest(self, scorer):
        position_scorer, _ = scorer
        sticks = [(9, 9), (6, 5), (0, 0)]
        assert position_scorer.find_closest_stick((5, 5), sticks) == (6, 5)

    def test_empty_list_returns_none(self, scorer):
        position_scorer, _ = scorer
        assert position_scorer.find_closest_stick((5, 5), []) is None


class TestValidPosition:
    def test_in_bounds(self, scorer):
        position_scorer, _ = scorer
        assert position_scorer.is_valid_position((0, 0)) is True
        assert position_scorer.is_valid_position((GRID_SIZE - 1, GRID_SIZE - 1)) is True

    def test_out_of_bounds(self, scorer):
        position_scorer, _ = scorer
        assert position_scorer.is_valid_position((-1, 0)) is False
        assert position_scorer.is_valid_position((GRID_SIZE, 0)) is False

    def test_within_view_radius(self, scorer):
        position_scorer, _ = scorer
        # Manhattan distance 2 from (5,5), radius 2 -> allowed.
        assert position_scorer.is_valid_check_position((5, 5), (6, 6), 2) is True
        # Manhattan distance 3, radius 2 -> rejected.
        assert position_scorer.is_valid_check_position((5, 5), (7, 6), 2) is False


class TestRockDensity:
    def test_no_rocks_is_zero(self, scorer):
        position_scorer, _ = scorer
        assert position_scorer.calculate_local_rock_density((5, 5)) == 0.0

    def test_density_is_fraction_of_sampled_cells(self, make_world):
        # (5,5) interior: the full 5x5 sample window (25 cells) is in-bounds.
        rocks = [(4, 4), (5, 4), (6, 4), (4, 5)]  # 4 rocks
        world = make_world(player_pos=(0, 0), rocks=rocks)
        position_scorer = PositionScorer(world)
        assert position_scorer.calculate_local_rock_density((5, 5)) == pytest.approx(4 / 25)


class TestScorePosition:
    def test_at_target_scores_zero(self, scorer):
        position_scorer, _ = scorer
        # progress_score is 0 at the target, so the whole product is 0.
        assert position_scorer.score_position((3, 3), (3, 3)) == 0.0

    def test_closer_beats_farther(self, scorer):
        # With no current movement (neutral alignment) and no rocks, a closer
        # position should score lower (better) than a farther one.
        position_scorer, _ = scorer
        target = (5, 0)
        near = position_scorer.score_position((4, 0), target)
        far = position_scorer.score_position((0, 0), target)
        assert near < far
