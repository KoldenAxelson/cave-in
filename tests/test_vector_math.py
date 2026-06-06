"""Tests for VectorMath: the pure vector/direction math used by the pathfinder."""

import pytest

from src.ai.pathfinding.path_calculator.vector_math import VectorMath
from src.utils.config import Direction


@pytest.fixture
def vector_math():
    return VectorMath()


class TestNormalizeVector:
    def test_zero_vector_stays_zero(self, vector_math):
        assert vector_math.normalize_vector(0, 0) == (0.0, 0.0)

    def test_axis_aligned_becomes_unit(self, vector_math):
        assert vector_math.normalize_vector(3, 0) == (1.0, 0.0)
        assert vector_math.normalize_vector(0, 5) == (0.0, 1.0)

    def test_3_4_5_triangle(self, vector_math):
        result = vector_math.normalize_vector(3, 4)
        assert result == pytest.approx((0.6, 0.8))


class TestVectorToDirection:
    def test_zero_is_none(self, vector_math):
        assert vector_math._vector_to_direction((0, 0)) is Direction.NONE

    def test_dominant_horizontal(self, vector_math):
        assert vector_math._vector_to_direction((2, 1)) is Direction.RIGHT
        assert vector_math._vector_to_direction((-3, 1)) is Direction.LEFT

    def test_dominant_vertical(self, vector_math):
        assert vector_math._vector_to_direction((1, 2)) is Direction.DOWN
        assert vector_math._vector_to_direction((1, -3)) is Direction.UP

    def test_tie_falls_through_to_vertical(self, vector_math):
        # abs(dx) == abs(dy): the `>` check is False, so the vertical branch wins.
        assert vector_math._vector_to_direction((1, 1)) is Direction.DOWN
        assert vector_math._vector_to_direction((1, -1)) is Direction.UP


class TestGetMovementDirection:
    def test_cardinal_deltas(self, vector_math):
        assert vector_math.get_movement_direction(1, 0) == Direction.RIGHT.value
        assert vector_math.get_movement_direction(-1, 0) == Direction.LEFT.value
        assert vector_math.get_movement_direction(0, 1) == Direction.DOWN.value
        assert vector_math.get_movement_direction(0, -1) == Direction.UP.value

    def test_no_movement(self, vector_math):
        assert vector_math.get_movement_direction(0, 0) == Direction.NONE.value

    def test_horizontal_takes_priority(self, vector_math):
        # When both components are non-zero, horizontal is checked first.
        assert vector_math.get_movement_direction(1, 1) == Direction.RIGHT.value


class TestDirectionChange:
    def test_none_direction_is_zero(self, vector_math):
        assert vector_math.calculate_direction_change(
            Direction.NONE, (1, 0), (0, 0)
        ) == 0.0

    def test_no_movement_is_zero(self, vector_math):
        assert vector_math.calculate_direction_change(
            Direction.RIGHT, (1, 0), (1, 0)
        ) == 0.0

    def test_straight_line_is_zero(self, vector_math):
        # Heading right, then stepping right again = no turn.
        assert vector_math.calculate_direction_change(
            Direction.RIGHT, (2, 0), (1, 0)
        ) == 0.0

    def test_turn_is_positive(self, vector_math):
        # Heading right, then turning down is a real direction change.
        assert vector_math.calculate_direction_change(
            Direction.RIGHT, (1, 1), (1, 0)
        ) > 0.0


class TestDirectionAlignment:
    def test_at_target_is_perfect(self, vector_math):
        assert vector_math.calculate_direction_alignment((2, 2), (2, 2)) == 1.0

    def test_no_movement_is_neutral(self, vector_math):
        assert vector_math.calculate_direction_alignment((0, 0), (2, 0)) == 0.5

    def test_same_heading_is_one(self, vector_math):
        assert vector_math.calculate_direction_alignment(
            (0, 0), (2, 0), current_movement=(1, 0)
        ) == pytest.approx(1.0)

    def test_opposite_heading_is_zero(self, vector_math):
        assert vector_math.calculate_direction_alignment(
            (0, 0), (2, 0), current_movement=(-1, 0)
        ) == pytest.approx(0.0)

    def test_perpendicular_heading_is_half(self, vector_math):
        assert vector_math.calculate_direction_alignment(
            (0, 0), (2, 0), current_movement=(0, 1)
        ) == pytest.approx(0.5)


class TestCurrentMovementDirection:
    def test_inferred_from_path(self, vector_math):
        path = [(0, 0), (1, 0)]
        assert vector_math.get_current_movement_direction(path, None) is Direction.RIGHT

    def test_falls_back_to_facing(self, vector_math):
        assert vector_math.get_current_movement_direction([(0, 0)], Direction.UP) is Direction.UP

    def test_none_when_no_path_or_facing(self, vector_math):
        assert vector_math.get_current_movement_direction([], None) is Direction.NONE
