from dataclasses import dataclass
from typing import List, Any, Optional
from src.utils.config import Position, GRID_SIZE
from src.cells import Rock, Stick, Cell

@dataclass
class GridAnalyzer:
    """Analyzes grid state and validates positions for pathfinding.
    
    Handles grid-related operations including neighbor calculation,
    position validation, and obstacle detection."""
    
    # Core Attributes
    world: Any  # Reference to game world state
    directions: List[Position]  # Available movement directions

    # Public Methods - Grid Analysis
    def get_valid_neighbors(self, pos: Position) -> List[Position]:
        """Gets all valid neighboring positions."""
        return [next_pos for delta_x, delta_y in self.directions
                if (next_pos := self._get_next_position(pos, delta_x, delta_y))
                and self._is_valid_cell(next_pos)]

    def is_rock(self, pos: Position) -> bool:
        """Checks if position contains a rock obstacle."""
        return isinstance(self.world.grid.get(pos), Rock)

    # Private Methods - Grid Navigation
    def _get_next_position(self, pos: Position, delta_x: int, delta_y: int) -> Optional[Position]:
        """Calculates next position and validates bounds."""
        next_pos = (pos[0] + delta_x, pos[1] + delta_y)
        return next_pos if self._is_in_bounds(next_pos) else None

    # Private Methods - Grid Validation
    def _is_in_bounds(self, pos: Position) -> bool:
        """Checks if position is within grid bounds."""
        column, row = pos
        return (0 <= column < GRID_SIZE and 0 <= row < GRID_SIZE)

    def _is_valid_cell(self, pos: Position) -> bool:
        """Checks if position contains a valid cell type."""
        cell = self.world.grid.get(pos)
        return isinstance(cell, (Cell, Rock, Stick))