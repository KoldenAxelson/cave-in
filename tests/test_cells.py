"""Tests for cell behaviour: base Cell, Rock/Stick interactions and Player moves."""

import pytest

from src.cells import Cell, Rock, Stick, Player
from src.utils.config import Direction, GRID_SIZE, ROCK_REMOVAL_COST


class TestBaseCell:
    def test_update_and_use_are_noops(self, make_world):
        # The base Cell does nothing on update/use; it should not raise or mutate.
        world = make_world(player_pos=(0, 0))
        cell = Cell((3, 3))
        cell.update(world)
        cell.use(world)
        assert world.stats.sticks_collected == 0


class TestRock:
    # Expectations are derived from ROCK_REMOVAL_COST so these stay correct if
    # the removal cost is retuned in config.
    def test_use_removes_rock_and_spends_full_cost(self, make_world):
        world = make_world(player_pos=(0, 0), rocks=[(3, 3)], sticks=ROCK_REMOVAL_COST)
        rock = world.grid[(3, 3)]
        rock.use(world)
        assert world.stats.sticks_collected == 0
        assert type(world.grid[(3, 3)]) is Cell   # rock replaced by empty cell

    def test_use_does_nothing_without_enough_sticks(self, make_world):
        insufficient = ROCK_REMOVAL_COST - 1      # one short of the cost
        world = make_world(player_pos=(0, 0), rocks=[(3, 3)], sticks=insufficient)
        rock = world.grid[(3, 3)]
        rock.use(world)
        assert isinstance(world.grid[(3, 3)], Rock)            # still there
        assert world.stats.sticks_collected == insufficient    # nothing spent

    def test_use_spends_only_the_cost_when_richer(self, make_world):
        world = make_world(player_pos=(0, 0), rocks=[(3, 3)], sticks=ROCK_REMOVAL_COST + 3)
        world.grid[(3, 3)].use(world)
        assert world.stats.sticks_collected == 3


class TestStick:
    def test_use_collects_and_replaces(self, make_world):
        world = make_world(player_pos=(0, 0), stick_positions=[(3, 3)])
        stick = world.grid[(3, 3)]
        stick.use(world)
        assert world.stats.sticks_collected == 1
        # A replacement stick is spawned elsewhere, so the board still has one.
        assert any(isinstance(cell, Stick) for cell in world.grid.values())


class TestPlayerMovement:
    def _player(self, world):
        player = world.player
        player.move_cooldown = 0  # remove timing from movement tests
        return player

    def test_move_into_empty_cell(self, make_world):
        world = make_world(player_pos=(5, 5))
        player = self._player(world)
        assert player.try_move(world, (1, 0)) is True
        assert player.position == (6, 5)
        assert world.grid[(6, 5)] is player
        assert type(world.grid[(5, 5)]) is Cell   # left an empty cell behind
        assert world.stats.tiles_moved == 1

    def test_cannot_move_into_rock(self, make_world):
        world = make_world(player_pos=(5, 5), rocks=[(6, 5)])
        player = self._player(world)
        assert player.try_move(world, (1, 0)) is False
        assert player.position == (5, 5)
        assert world.stats.tiles_moved == 0

    def test_cannot_move_into_stick(self, make_world):
        world = make_world(player_pos=(5, 5), stick_positions=[(6, 5)])
        player = self._player(world)
        # Only plain empty cells are walkable; a stick must be used, not stepped on.
        assert player.try_move(world, (1, 0)) is False
        assert player.position == (5, 5)

    def test_move_into_wall_is_blocked(self, make_world):
        world = make_world(player_pos=(0, 0))
        player = self._player(world)
        # Clamped target equals current position -> not a valid move.
        assert player.try_move(world, (-1, 0)) is False
        assert player.position == (0, 0)
        assert world.stats.tiles_moved == 0


class TestPlayerHelpers:
    def test_calculate_new_position_clamps_to_grid(self, make_world):
        world = make_world(player_pos=(9, 9))
        player = world.player
        assert player._calculate_new_position((1, 1)) == (9, 9)
        player.position = (0, 0)
        assert player._calculate_new_position((-1, -1)) == (0, 0)
        player.position = (5, 5)
        assert player._calculate_new_position((1, 0)) == (6, 5)

    def test_update_facing(self, make_world):
        world = make_world(player_pos=(5, 5))
        player = world.player
        player.update_facing((1, 0))
        assert player.facing is Direction.RIGHT
        player.update_facing((0, -1))
        assert player.facing is Direction.UP


class TestPlayerUseFacingCell:
    def test_uses_rock_in_front(self, make_world):
        world = make_world(player_pos=(5, 5), rocks=[(6, 5)], sticks=ROCK_REMOVAL_COST)
        player = world.player
        player.facing = Direction.RIGHT
        assert player.try_use_facing_cell(world) is True
        assert type(world.grid[(6, 5)]) is Cell
        assert world.stats.sticks_collected == 0

    def test_uses_stick_in_front(self, make_world):
        world = make_world(player_pos=(5, 5), stick_positions=[(6, 5)])
        player = world.player
        player.facing = Direction.RIGHT
        assert player.try_use_facing_cell(world) is True
        assert world.stats.sticks_collected == 1
