# Standard library imports
from dataclasses import dataclass, field
from typing import Dict, Optional
import random
from itertools import product
# Local imports
from src.cells import Cell, Stick, Rock
from src.utils.config import GRID_SIZE, Position, Difficulty, DIFFICULTY
from src.core.stats import Stats
from src.utils.fill_manager import FillManager

@dataclass
class GameWorld:
    """Represents the game world and manages all game objects.
    
    The GameWorld class maintains the game grid and handles object placement,
    updates, and game state checks. It serves as the central point for
    managing all game entities and their interactions.
    """
    # Dictionary mapping grid positions to cell objects
    grid: Dict[Position, Cell] = field(default_factory=dict)
    player: Optional[Cell] = None  # Reference to player object
    stats: Optional[Stats] = None  # Reference to game statistics
    fill_manager: FillManager = field(default_factory=FillManager)

    def __post_init__(self) -> None:
        """Initialize the game grid after dataclass initialization.
        
        Creates an empty grid of basic cells and places the initial
        stick to start the game.
        """
        # Fill grid with empty cells at all positions
        self.grid.update({
            pos: Cell(pos) for pos in product(range(GRID_SIZE), range(GRID_SIZE))
        })

        # Place initial stick to start the game
        self._place_random_stick()

    def _place_random_rock(self) -> None:
        """Place a rock obstacle based on difficulty setting."""
        empty_positions = [
            pos for pos, cell in self.grid.items()
            if type(cell) == Cell
        ]
        
        if not empty_positions:
            return

        if DIFFICULTY == Difficulty.EASY:
            # Try positions until we find a safe one
            random.shuffle(empty_positions)
            for pos in empty_positions:
                if self.fill_manager.is_safe_rock_position(self, pos):
                    self.grid[pos] = Rock(pos)
                    return
        else:
            # Normal difficulty - place rock randomly
            rock_pos = random.choice(empty_positions)
            self.grid[rock_pos] = Rock(rock_pos)

    def _place_random_stick(self) -> None:
        """Place a collectible stick at a random empty position in the grid.
        
        Finds all empty cells in the grid and randomly selects one
        to place a new stick. Also triggers rock placement to maintain
        game balance.
        """
        # Get list of all positions containing only basic cells
        empty_positions = [
            pos for pos, cell in self.grid.items()
            if type(cell) == Cell
        ]
        # Place stick and rock if there are empty positions
        if empty_positions:
            stick_pos = random.choice(empty_positions)
            self.grid[stick_pos] = Stick(stick_pos)
            self._place_random_rock()  # Place rock with each stick

    def add(self, cell: Cell) -> None:
        """Add a cell to the game grid at its specified position.
        
        Args:
            cell: Cell object to add to the grid
        """
        self.grid[cell.position] = cell

    def update(self) -> None:
        """Update all cells in the game grid.
        
        Calls the update method on each cell in the grid, allowing
        cells to perform any necessary frame-by-frame updates.
        """
        for cell in self.grid.values():
            cell.update(self)

    def is_board_full(self) -> bool:
        """Check if there are any empty cells remaining in the grid.
        
        Returns:
            bool: True if no empty cells remain, False otherwise
            
        Note:
            This is used to determine if the game should end (player is trapped).
        """
        # Count positions that contain only basic cells
        empty_positions = [
            pos for pos, cell in self.grid.items()
            if type(cell) == Cell
        ]
        return len(empty_positions) == 0