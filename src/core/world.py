# Standard library imports
from dataclasses import dataclass, field
from typing import Dict, Optional, List
import random
from itertools import product
# Local imports
from src.cells import Cell, Stick, Rock
from src.utils.config import GRID_SIZE, Position, Difficulty, DIFFICULTY
from src.core.stats import Stats
from src.utils.fill_manager import FillManager

@dataclass
class GameWorld:
    """Central manager for the game's grid-based world and all game objects.
    Handles object placement, updates, and maintains the relationships between
    all game entities."""
    grid: Dict[Position, Cell] = field(default_factory=dict)
    player: Optional[Cell] = None
    stats: Optional[Stats] = None
    fill_manager: FillManager = field(default_factory=FillManager)
    difficulty: Difficulty = DIFFICULTY

    def __post_init__(self) -> None:
        """Sets up the initial game grid with empty cells and places the first stick."""
        self.grid.update({
            pos: Cell(pos) for pos in product(range(GRID_SIZE), range(GRID_SIZE))
        })
        self._place_random_stick()

    # Public Methods
    def add(self, cell: Cell) -> None:
        """Adds a new cell object to the game grid at its specified position."""
        self.grid[cell.position] = cell

    def update(self) -> None:
        """Triggers update logic for all cells in the game grid."""
        for cell in self.grid.values():
            cell.update(self)

    def is_board_full(self) -> bool:
        """Checks if there are any empty cells remaining in the grid."""
        empty_positions = [
            pos for pos, cell in self.grid.items()
            if type(cell) == Cell
        ]
        return len(empty_positions) == 0

    # Private Methods - Object Placement
    def _place_random_stick(self) -> None:
        """Places a new stick and potentially a rock in the game world."""
        self._place_random_rock()
        
        empty_positions = self._get_empty_positions()
        if empty_positions:
            stick_pos = random.choice(empty_positions)
            self.grid[stick_pos] = Stick(stick_pos)

    def _place_random_rock(self) -> None:
        """Handles rock placement based on the current difficulty setting."""
        empty_positions = self._get_empty_positions()
        if not empty_positions:
            return

        if self.difficulty == Difficulty.NORMAL:
            self._place_normal_rock(empty_positions)
        else:
            self._place_easy_rock(empty_positions)

    def _place_normal_rock(self, empty_positions: List[Position]) -> None:
        """Places a rock with random chance in normal difficulty."""
        if random.random() < DIFFICULTY.value:
            rock_pos = random.choice(empty_positions)
            self.grid[rock_pos] = Rock(rock_pos)

    def _place_easy_rock(self, empty_positions: List[Position]) -> None:
        """Places a rock in a position that won't trap the player."""
        random.shuffle(empty_positions)
        for pos in empty_positions:
            if self.fill_manager.is_safe_rock_position(self, pos):
                self.grid[pos] = Rock(pos)
                break

    # Private Methods - Utility
    def _get_empty_positions(self) -> List[Position]:
        """Returns all grid positions that contain only basic cells."""
        return [
            pos for pos, cell in self.grid.items()
            if type(cell) == Cell
        ]