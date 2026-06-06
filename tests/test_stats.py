"""Tests for Stats number formatting (the K/M suffix logic)."""

import pytest

from src.core.stats import Stats


@pytest.fixture
def stats():
    return Stats()


@pytest.mark.parametrize("value,expected", [
    (0, "0"),
    (999, "999"),
    (1000, "1.0K"),
    (1500, "1.5K"),
    (999999, "1000.0K"),     # just below the M threshold
    (1000000, "1.0M"),
    (1500000, "1.5M"),
])
def test_format_number(stats, value, expected):
    assert stats._format_number(value) == expected


def test_counters_default_to_zero():
    fresh = Stats()
    assert fresh.sticks_collected == 0
    assert fresh.tiles_moved == 0
