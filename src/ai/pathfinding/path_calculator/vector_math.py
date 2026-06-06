from dataclasses import dataclass
from typing import Tuple, Optional, List
from src.utils.config import Position, Direction

@dataclass
class VectorMath:
    """Handles vector calculations and direction conversions for pathfinding.
    
    Provides utilities for normalizing vectors, converting between vectors and
    directions, and calculating direction changes."""

    def normalize_vector(self, delta_x: int, delta_y: int) -> Tuple[float, float]:
        """Normalize a vector to unit length."""
        length = (delta_x * delta_x + delta_y * delta_y) ** 0.5
        if length == 0:
            return (0.0, 0.0)
        return (delta_x / length, delta_y / length)

    def _vector_to_direction(self, vector: Position) -> Direction:
        """Convert a movement vector to the closest cardinal direction."""
        delta_x, delta_y = vector
        if delta_x == 0 and delta_y == 0:
            return Direction.NONE

        # Pick the axis with the larger component; ties fall through to vertical
        if abs(delta_x) > abs(delta_y):
            return Direction.RIGHT if delta_x > 0 else Direction.LEFT
        else:
            return Direction.DOWN if delta_y > 0 else Direction.UP

    def get_movement_direction(self, delta_x: int, delta_y: int) -> Position:
        """Convert position delta to movement direction."""
        # Horizontal movement takes priority over vertical when both are non-zero
        if delta_x > 0: return Direction.RIGHT.value
        if delta_x < 0: return Direction.LEFT.value
        if delta_y > 0: return Direction.DOWN.value
        if delta_y < 0: return Direction.UP.value
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

        delta_x = next_pos[0] - current_pos[0]
        delta_y = next_pos[1] - current_pos[1]
        if delta_x == 0 and delta_y == 0:
            return 0.0

        new_dir = self._vector_to_direction((delta_x, delta_y))

        # Manhattan distance between the two direction vectors approximates how
        # sharp the turn is: 0 means same heading, larger means a bigger change
        current_vector = current_dir.value
        new_vector = new_dir.value
        return abs(current_vector[0] - new_vector[0]) + abs(current_vector[1] - new_vector[1])

    def calculate_direction_alignment(
        self, 
        pos: Position, 
        target_pos: Position,
        current_movement: Optional[Position] = None
    ) -> float:
        """Calculate direction alignment between current movement and target."""
        if pos == target_pos:
            return 1.0

        delta_x = target_pos[0] - pos[0]
        delta_y = target_pos[1] - pos[1]
        target_vector = self.normalize_vector(delta_x, delta_y)

        if current_movement:
            current_vector = self.normalize_vector(current_movement[0], current_movement[1])
            # Dot product of two unit vectors gives their direction similarity:
            # 1 = same heading, -1 = opposite
            dot_product = (target_vector[0] * current_vector[0] +
                         target_vector[1] * current_vector[1])
            # Rescale the dot product from [-1, 1] into [0, 1]
            return (dot_product + 1) / 2

        return 0.5  # Neutral alignment when there is no current heading to compare against
    
    def get_current_movement_direction(
        self,
        current_path: List[Position],
        player_facing: Optional[Direction]
    ) -> Direction:
        """Get the current movement direction based on path or player facing."""
        # Prefer the heading implied by the path's first step; fall back to the
        # player's facing direction when the path is too short to infer one
        if len(current_path) >= 2:
            current = current_path[0]
            next_pos = current_path[1]
            delta_x = next_pos[0] - current[0]
            delta_y = next_pos[1] - current[1]
            return self._vector_to_direction((delta_x, delta_y))
        elif player_facing:
            return player_facing
        return Direction.NONE