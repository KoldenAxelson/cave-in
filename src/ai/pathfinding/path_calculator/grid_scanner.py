from dataclasses import dataclass
from typing import Any, Optional, Tuple, List
from src.utils.config import Position, VIEW_RADIUS
from .vector_math import VectorMath
from .position_scorer import PositionScorer

@dataclass
class GridScanner:
    """Handles grid scanning and position searching for pathfinding.
    
    Implements scanning algorithms to find optimal positions and paths,
    considering visibility constraints and position scoring."""
    
    # Core Attributes
    world: Any  # Reference to game world state
    vector_math: VectorMath = None
    position_scorer: PositionScorer = None

    def __post_init__(self):
        """Initialize helper components if not provided."""
        if self.vector_math is None:
            self.vector_math = VectorMath()
        if self.position_scorer is None:
            self.position_scorer = PositionScorer(self.world, self.vector_math)

    def find_best_visible_position(
        self, 
        current_pos: Position, 
        target_pos: Position
    ) -> Optional[Position]:
        """Find best position along vector to target."""
        vectors = self.calculate_scan_vectors(current_pos, target_pos)
        return self.scan_for_best_position(current_pos, vectors, target_pos)

    def calculate_scan_vectors(
        self, 
        current_pos: Position, 
        target_pos: Position
    ) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """Calculate primary and secondary vectors for scanning."""
        primary_vector = self.vector_math.normalize_vector(
            target_pos[0] - current_pos[0],
            target_pos[1] - current_pos[1]
        )
        # Calculate perpendicular vector for secondary scanning
        secondary_vector = (-primary_vector[1], primary_vector[0])
        return primary_vector, secondary_vector

    def scan_for_best_position(
        self, 
        current_pos: Position, 
        vectors: Tuple[Tuple[float, float], Tuple[float, float]],
        target_pos: Position
    ) -> Optional[Position]:
        """Scan area for best position."""
        primary_vector, secondary_vector = vectors
        best_pos = None
        best_score = float('inf')
        
        for d in range(VIEW_RADIUS + 1):
            main_pos = self.get_main_scan_position(current_pos, primary_vector, d)
            best_pos, best_score = self.scan_perpendicular(
                current_pos, main_pos, secondary_vector, d, best_pos, best_score, target_pos
            )
        
        return best_pos

    def get_main_scan_position(
        self, 
        current_pos: Position, 
        primary_vector: Tuple[float, float], 
        distance: int
    ) -> Position:
        """Calculate position along primary vector."""
        return (
            current_pos[0] + int(primary_vector[0] * distance),
            current_pos[1] + int(primary_vector[1] * distance)
        )

    def calculate_check_position(
        self, 
        main_pos: Position, 
        secondary_vector: Tuple[float, float], 
        offset: int
    ) -> Position:
        """Calculate position to check based on main position and offset."""
        return (
            main_pos[0] + int(secondary_vector[0] * offset),
            main_pos[1] + int(secondary_vector[1] * offset)
        )

    def scan_perpendicular(
        self,
        current_pos: Position,
        main_pos: Position,
        secondary_vector: Tuple[float, float],
        distance: int,
        best_pos: Optional[Position],
        best_score: float,
        target_pos: Position
    ) -> Tuple[Optional[Position], float]:
        """Scan perpendicular to main vector."""
        for offset in range(-distance//2, distance//2 + 1):
            check_pos = self.calculate_check_position(main_pos, secondary_vector, offset)
            
            if self.position_scorer.is_valid_check_position(current_pos, check_pos, VIEW_RADIUS):
                score = self.position_scorer.score_position(check_pos, target_pos)
                if score < best_score:
                    best_score = score
                    best_pos = check_pos
                    
        return best_pos, best_score 

    def find_best_alternative_path(
        self, 
        max_rocks: int, 
        target_pos: Position,
        path_calculator: Any,  # Reference to PathCalculator
        stick_value: int
    ) -> Optional[Tuple[List[Position], int]]:
        """Find the path with the best score using fewer rocks."""
        best_path = None
        best_score = float('inf')

        # Binary search for optimal rock count
        left, right = 0, max_rocks
        while left <= right:
            mid = (left + right) // 2
            if path := path_calculator.find_path_with_max_rocks(mid, target_pos):
                score = (stick_value * mid) + len(path)
                if score < best_score:
                    best_score = score
                    best_path = path
                right = mid - 1
            else:
                left = mid + 1

        return (best_path, best_score) if best_path else None