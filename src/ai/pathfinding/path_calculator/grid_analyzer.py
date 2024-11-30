from dataclasses import dataclass
from typing import List, Set, Any, Optional
from src.utils.config import Position, GRID_SIZE, PathType
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
        return [next_pos for dx, dy in self.directions
                if (next_pos := self._get_next_position(pos, dx, dy))
                and self._is_valid_cell(next_pos)]
    
    def is_rock(self, pos: Position) -> bool:
        """Checks if position contains a rock obstacle."""
        return isinstance(self.world.grid.get(pos), Rock)

    # Private Methods - Grid Navigation
    def _get_next_position(self, pos: Position, dx: int, dy: int) -> Optional[Position]:
        """Calculates next position and validates bounds."""
        next_pos = (pos[0] + dx, pos[1] + dy)
        return next_pos if self._is_in_bounds(next_pos) else None

    # Private Methods - Grid Validation
    def _is_in_bounds(self, pos: Position) -> bool:
        """Checks if position is within grid bounds."""
        return (0 <= pos[0] < GRID_SIZE and 0 <= pos[1] < GRID_SIZE)

    def _is_valid_cell(self, pos: Position) -> bool:
        """Checks if position contains a valid cell type."""
        cell = self.world.grid.get(pos)
        return isinstance(cell, (Cell, Rock, Stick))

    def _is_stick(self, pos: Position) -> bool:
        """Checks if position contains a stick."""
        return isinstance(self.world.grid.get(pos), Stick) 