"""Tests for GameWorld: grid setup, board-full detection and empty-cell queries."""

import pytest

from src.core.world import GameWorld
from src.cells import Cell, Rock, Stick, Player
from src.utils.config import GRID_SIZE, Difficulty


class TestInitialGrid:
    def test_grid_covers_every_position(self):
        world = GameWorld()
        assert len(world.grid) == GRID_SIZE * GRID_SIZE

    def test_fresh_world_has_one_stick_and_one_rock(self):
        # __post_init__ places exactly one rock (NORMAL difficulty) and one stick.
        world = GameWorld()
        sticks = [c for c in world.grid.values() if isinstance(c, Stick)]
        rocks = [c for c in world.grid.values() if isinstance(c, Rock)]
        assert len(sticks) == 1
        assert len(rocks) == 1


class TestBoardFull:
    def test_blank_board_is_not_full(self, make_world):
        world = make_world(player_pos=(0, 0))
        assert world.is_board_full() is False

    def test_board_with_only_player_and_rocks_is_full(self, make_world):
        # Fill every non-player cell with a rock -> no empty Cells remain.
        world = make_world(player_pos=(0, 0))
        for position, cell in list(world.grid.items()):
            if not isinstance(cell, Player):
                world.grid[position] = Rock(position)
        assert world.is_board_full() is True


class TestEmptyPositions:
    def test_excludes_player_rocks_and_sticks(self, make_world):
        world = make_world(player_pos=(0, 0), rocks=[(1, 1)], stick_positions=[(2, 2)])
        empty = world._get_empty_positions()
        assert (0, 0) not in empty   # player
        assert (1, 1) not in empty   # rock
        assert (2, 2) not in empty   # stick
        assert (5, 5) in empty       # plain cell
        assert len(empty) == GRID_SIZE * GRID_SIZE - 3


class TestAdd:
    def test_add_places_cell_at_its_position(self, make_world):
        world = make_world(player_pos=(0, 0))
        rock = Rock((4, 4))
        world.add(rock)
        assert world.grid[(4, 4)] is rock


class TestEasyDifficultyPlacement:
    def test_easy_mode_never_traps_the_player(self):
        # In EASY mode every placed rock must keep the board fully connected.
        from src.utils.fill_manager import FillManager
        world = GameWorld(difficulty=Difficulty.EASY)
        world.grid = {
            (column, row): Cell((column, row))
            for column in range(GRID_SIZE) for row in range(GRID_SIZE)
        }
        world.player = Player(position=(0, 0))
        world.grid[(0, 0)] = world.player

        fill_manager = FillManager()
        world._place_easy_rock(world._get_empty_positions())

        placed = [pos for pos, cell in world.grid.items() if isinstance(cell, Rock)]
        assert len(placed) == 1
        # The chosen position must itself pass the safety check on a board
        # without that rock present.
        world.grid[placed[0]] = Cell(placed[0])
        assert fill_manager.is_safe_rock_position(world, placed[0]) is True
