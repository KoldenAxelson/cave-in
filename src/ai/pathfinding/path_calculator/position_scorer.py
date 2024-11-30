from dataclasses import dataclass
from typing import Any, Tuple, List, Optional
from src.utils.config import Position, GRID_SIZE
from src.cells import Cell, Rock, Stick
from .vector_math import VectorMath

@dataclass
class PositionScorer:
    """Evaluates and scores positions for pathfinding decisions.
    
    Handles position validation, scoring based on multiple factors including
    rock density, direction alignment, and progress towards target."""
    
    # Core Attributes
    world: Any  # Reference to game world state
    vector_math: VectorMath = None

    def __post_init__(self):
        """Initialize vector math helper if not provided."""
        if self.vector_math is None:
            self.vector_math = VectorMath()

    def score_position(
        self, 
        pos: Position, 
        target_pos: Position,
        current_movement: Position = None
    ) -> float:
        """Score position based on progress toward target."""
        progress_score = abs(pos[0] - target_pos[0]) + abs(pos[1] - target_pos[1])
        direction_alignment = self.vector_math.calculate_direction_alignment(
            pos, target_pos, current_movement
        )
        rock_density = self.calculate_local_rock_density(pos)
        
        return progress_score * (1 - direction_alignment * 0.3) * (1 + rock_density * 0.5)

    def calculate_local_rock_density(self, pos: Position) -> float:
        """Calculate density of rocks in vicinity."""
        rocks_count = 0
        checked_cells = 0
        
        # Check 5x5 area centered on position
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                check_pos = (pos[0] + dx, pos[1] + dy)
                if self.is_valid_position(check_pos):
                    checked_cells += 1
                    if isinstance(self.world.grid.get(check_pos), Rock):
                        rocks_count += 1
        
        return rocks_count / checked_cells if checked_cells > 0 else 0

    def is_valid_position(self, pos: Position) -> bool:
        """Check if a position is valid."""
        if not (0 <= pos[0] < GRID_SIZE and 0 <= pos[1] < GRID_SIZE):
            return False
        
        cell = self.world.grid.get(pos)
        return isinstance(cell, (Cell, Rock, Stick))

    def is_valid_check_position(
        self, 
        current_pos: Position, 
        check_pos: Position,
        view_radius: int
    ) -> bool:
        """Check if a position is valid for pathfinding within view radius."""
        if not self.is_valid_position(check_pos):
            return False
        dx = abs(current_pos[0] - check_pos[0])
        dy = abs(current_pos[1] - check_pos[1])
        return dx + dy <= view_radius

    def get_manhattan_distance(
        self,
        pos1: Position,
        pos2: Position
    ) -> int:
        """Calculate Manhattan distance between two positions."""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def find_closest_stick(self, player_pos: Position, sticks: List[Position]) -> Optional[Position]:
        """Find closest stick using Manhattan distance."""
        if not sticks:
            return None
        return min(sticks, key=lambda pos: self.get_manhattan_distance(pos, player_pos))