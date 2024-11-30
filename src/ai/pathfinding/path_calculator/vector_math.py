from dataclasses import dataclass
from typing import Tuple, Optional, List
from src.utils.config import Position, Direction

@dataclass
class VectorMath:
    """Handles vector calculations and direction conversions for pathfinding.
    
    Provides utilities for normalizing vectors, converting between vectors and
    directions, and calculating direction changes."""

    def normalize_vector(self, dx: int, dy: int) -> Tuple[float, float]:
        """Normalize a vector to unit length."""
        length = (dx * dx + dy * dy) ** 0.5
        if length == 0:
            return (0.0, 0.0)
        return (dx / length, dy / length)

    def _vector_to_direction(self, vector: Position) -> Direction:
        """Convert a movement vector to the closest cardinal direction."""
        dx, dy = vector
        if dx == 0 and dy == 0:
            return Direction.NONE
            
        # Determine primary direction based on larger component
        if abs(dx) > abs(dy):
            return Direction.EAST if dx > 0 else Direction.WEST
        else:
            return Direction.SOUTH if dy > 0 else Direction.NORTH

    def get_movement_direction(self, dx: int, dy: int) -> Position:
        """Convert position delta to movement direction."""
        if dx > 0: return Direction.RIGHT.value
        if dx < 0: return Direction.LEFT.value
        if dy > 0: return Direction.DOWN.value
        if dy < 0: return Direction.UP.value
        return Direction.NONE.value

    def calculate_direction_change(
        self, 
        current_dir: Direction, 
        next_pos: Position,
        current_pos: Position
    ) -> float:
        """Calculate the magnitude of direction change."""
        if current_dir == Direction.NONE:
            return 0.0
            
        # Calculate new direction vector
        dx = next_pos[0] - current_pos[0]
        dy = next_pos[1] - current_pos[1]
        if dx == 0 and dy == 0:
            return 0.0
            
        new_dir = self._vector_to_direction((dx, dy))
        
        # Use direction values for comparison
        current_vec = current_dir.value
        new_vec = new_dir.value
        return abs(current_vec[0] - new_vec[0]) + abs(current_vec[1] - new_vec[1])

    def calculate_direction_alignment(
        self, 
        pos: Position, 
        target_pos: Position,
        current_movement: Optional[Position] = None
    ) -> float:
        """Calculate direction alignment between current movement and target."""
        if pos == target_pos:
            return 1.0
            
        # Get vector to target
        dx = target_pos[0] - pos[0]
        dy = target_pos[1] - pos[1]
        
        # Normalize vector
        target_vector = self.normalize_vector(dx, dy)
        
        # Get current movement direction if available
        if current_movement:
            current_vector = self.normalize_vector(current_movement[0], current_movement[1])
            # Calculate dot product for direction similarity
            dot_product = (target_vector[0] * current_vector[0] + 
                         target_vector[1] * current_vector[1])
            # Convert from [-1, 1] to [0, 1] range
            return (dot_product + 1) / 2
        
        return 0.5  # Neutral alignment if no current direction 
    
    def get_current_movement_direction(
        self,
        current_path: List[Position],
        player_facing: Optional[Direction]
    ) -> Direction:
        """Get the current movement direction based on path or player facing."""
        if len(current_path) >= 2:
            current = current_path[0]
            next_pos = current_path[1]
            dx = next_pos[0] - current[0]
            dy = next_pos[1] - current[1]
            return self._vector_to_direction((dx, dy))
        elif player_facing:
            return player_facing
        return Direction.NONE