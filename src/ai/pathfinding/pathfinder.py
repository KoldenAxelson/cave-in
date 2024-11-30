from dataclasses import dataclass
from typing import List, Any, Optional, Tuple
from src.utils.config import Position, Direction, STICK_VALUE, VIEW_RADIUS, GRID_SIZE
from src.ai.ai_interface import AIInterface
from src.utils.player_interface import PlayerInterface
from .path_calculator.path_calculator import PathCalculator
from .action_handler import ActionHandler
from src.cells import Cell, Rock, Stick

@dataclass
class PathFinder(AIInterface):
    """AI that finds and follows optimal paths to collect sticks.
    
    Implements pathfinding strategies with rock avoidance and removal,
    optimizing paths based on stick value and path length."""
    
    # Core Attributes
    world: Any                                  # Current game world state
    path_calculator: PathCalculator = None      # Handles core pathfinding
    action_handler: ActionHandler = None        # Manages action decisions
    current_path: List[Position] = None         # Current path being followed
    player: PlayerInterface = None              # Interface to player state
    last_movement: Position = None              # Tracks last movement direction

    # Initialization
    def __post_init__(self):
        """Initialize dependent components after dataclass initialization."""
        self.path_calculator = PathCalculator(self.world)
        self.action_handler = ActionHandler(self.world)
        self.current_path = []
        self.player = PlayerInterface(self.world)
        self.last_movement = Direction.NONE.value  # Initialize with no movement
        self._calculate_next_path()

    # Public Methods - AI Interface Implementation
    def get_movement(self) -> Position:
        """Calculate and return the next movement for the AI.
        Handles path recalculation when needed."""
        if self.action_handler.did_use_action():
            return Direction.NONE.value

        if not self.current_path:
            self._calculate_next_path()
            
        return self._calculate_movement()

    def should_use_action(self) -> bool:
        """Determine if the AI should use an action.
        Delegates to action handler for decision."""
        return self.action_handler.should_use_action()

    def update(self, world) -> None:
        """Update AI state with new world information.
        Refreshes all component states and recalculates path."""
        self.world = world
        self.path_calculator.world = world
        self.action_handler.update(world, self.current_path)
        self.player = PlayerInterface(world)
        self._calculate_next_path()

    # Private Methods - Path Planning
    def _calculate_next_path(self) -> None:
        """Calculate optimal path to nearest stick."""
        if not self._has_valid_state():
            self._clear_paths()
            return

        target_stick = self._find_closest_stick()
        if not target_stick:
            self._clear_paths()
            return
        
        self._find_and_set_path(target_stick)

    def _find_and_set_path(self, target_stick: Position) -> None:
        """Find and set optimal path to target stick."""
        if path := self.path_calculator.find_path_without_rocks(target_stick):
            self._set_paths(path)
            return
        
        visible_target = self._find_best_visible_position(self.world.player.position, target_stick)
        if not visible_target:
            self._clear_paths()
            return
        
        self._find_optimal_path_with_rocks(visible_target)

    def _find_optimal_path_with_rocks(self, target_pos: Position) -> None:
        """Find optimal path considering rock removal."""
        path = self._find_initial_path(target_pos)
        if not path:
            self._clear_paths()
            return
            
        self._optimize_path_with_rocks(path, target_pos)

    def _find_initial_path(self, target_pos: Position) -> Optional[List[Position]]:
        """Find initial path using momentum heuristic."""
        current_direction = self._get_current_movement_direction()
        
        def momentum_heuristic(pos: Position) -> float:
            direction_change = self._calculate_direction_change(current_direction, pos)
            return direction_change * 0.3
            
        return self.path_calculator.find_path_to_position(target_pos, heuristic=momentum_heuristic)

    def _optimize_path_with_rocks(self, path: List[Position], target_pos: Position) -> None:
        """Optimize path by potentially finding alternative with fewer rocks."""
        rocks_in_path = self.path_calculator.count_rocks_in_path(path)
        
        if rocks_in_path == 0:
            self._set_paths(path)
            return
            
        if alternative := self._find_best_alternative_path(rocks_in_path, target_pos):
            alt_path, alt_score = alternative
            current_score = len(path) + (STICK_VALUE * rocks_in_path)
            
            if alt_score < current_score:
                path = alt_path
                
        self._set_paths(path)

    # Private Methods - Path Management
    def _clear_paths(self) -> None:
        """Reset path information."""
        self.current_path = []
        self.action_handler.update(self.world, [])

    def _set_paths(self, path: List[Position]) -> None:
        """Update path information with new path."""
        self.current_path = path[1:]  # Skip current position
        self.action_handler.update(self.world, path)

    # Private Methods - Movement & Direction
    def _calculate_movement(self) -> Position:
        """Calculate the next movement based on current path."""
        if not self.current_path:
            return Direction.NONE.value
            
        next_pos = self.current_path[0]
        current_pos = self.player.position
        
        dx = next_pos[0] - current_pos[0]
        dy = next_pos[1] - current_pos[1]
        
        movement = self._get_movement_direction(dx, dy)
        
        if movement != Direction.NONE.value and self.player.try_move(movement):
            self.current_path.pop(0)
        
        return movement

    def _get_movement_direction(self, dx: int, dy: int) -> Position:
        """Convert position delta to movement direction."""
        if dx > 0: return Direction.RIGHT.value
        if dx < 0: return Direction.LEFT.value
        if dy > 0: return Direction.DOWN.value
        if dy < 0: return Direction.UP.value
        return Direction.NONE.value

    def _get_current_movement_direction(self) -> Direction:
        """Get the current movement direction based on path or player facing."""
        if len(self.current_path) >= 2:
            current = self.current_path[0]
            next_pos = self.current_path[1]
            dx = next_pos[0] - current[0]
            dy = next_pos[1] - current[1]
            return self._vector_to_direction((dx, dy))
        elif self.player and self.player.facing:
            return self.player.facing
        return Direction.NONE

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

    def _calculate_direction_change(self, current_dir: Direction, next_pos: Position) -> float:
        """Calculate the magnitude of direction change."""
        if current_dir == Direction.NONE or not self.player:
            return 0.0
            
        # Calculate new direction vector
        dx = next_pos[0] - self.player.position[0]
        dy = next_pos[1] - self.player.position[1]
        if dx == 0 and dy == 0:
            return 0.0
            
        new_dir = self._vector_to_direction((dx, dy))
        
        # Use direction values for comparison
        current_vec = current_dir.value
        new_vec = new_dir.value

    # Private Methods - State & Validation
    def _has_valid_state(self) -> bool:
        """Check if pathfinding prerequisites are met."""
        return (self.world.player and 
                bool(self.path_calculator.find_sticks()))

    def _find_closest_stick(self) -> Optional[Position]:
        """Find closest stick using Manhattan distance."""
        if not self.world.player:
            return None
        sticks = self.path_calculator.find_sticks()
        if not sticks:
            return None
        player_pos = self.world.player.position
        return min(sticks, key=lambda pos: abs(pos[0] - player_pos[0]) + abs(pos[1] - player_pos[1]))

    def _is_valid_position(self, pos: Position) -> bool:
        """Check if a position is valid."""
        if not (0 <= pos[0] < GRID_SIZE and 0 <= pos[1] < GRID_SIZE):
            return False
        
        cell = self.world.grid.get(pos)
        return isinstance(cell, (Cell, Rock, Stick))

    def _is_valid_check_position(self, current_pos: Position, check_pos: Position) -> bool:
        """Check if a position is valid for pathfinding."""
        if not self._is_valid_position(check_pos):
            return False
        dx = abs(current_pos[0] - check_pos[0])
        dy = abs(current_pos[1] - check_pos[1])
        return dx + dy <= VIEW_RADIUS

    # Private Methods - Position Calculations
    def _normalize_vector(self, dx: int, dy: int) -> Tuple[float, float]:
        """Normalize a vector to unit length."""
        length = (dx * dx + dy * dy) ** 0.5
        if length == 0:
            return (0.0, 0.0)
        return (dx / length, dy / length)

    def _score_position(self, pos: Position, target_pos: Position) -> float:
        """Score position based on progress toward target."""
        progress_score = abs(pos[0] - target_pos[0]) + abs(pos[1] - target_pos[1])
        direction_alignment = self._calculate_direction_alignment(pos, target_pos)
        rock_density = self._calculate_local_rock_density(pos)
        
        return progress_score * (1 - direction_alignment * 0.3) * (1 + rock_density * 0.5)

    def _calculate_direction_alignment(self, pos: Position, target_pos: Position) -> float:
        """Calculate direction alignment."""
        if pos == target_pos:
            return 1.0
            
        # Get vector to target
        dx = target_pos[0] - pos[0]
        dy = target_pos[1] - pos[1]
        
        # Normalize vector
        target_vector = self._normalize_vector(dx, dy)
        
        # Get current movement direction if available
        if hasattr(self, 'last_movement'):
            current_vector = self._normalize_vector(self.last_movement[0], self.last_movement[1])
            # Calculate dot product for direction similarity
            dot_product = (target_vector[0] * current_vector[0] + 
                         target_vector[1] * current_vector[1])
            # Convert from [-1, 1] to [0, 1] range
            return (dot_product + 1) / 2
        
        return 0.5  # Neutral alignment if no current direction

    def _calculate_local_rock_density(self, pos: Position) -> float:
        """Calculate density of rocks in vicinity."""
        rocks_count = 0
        checked_cells = 0
        
        # Check 5x5 area centered on position
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                check_pos = (pos[0] + dx, pos[1] + dy)
                if self._is_valid_position(check_pos):
                    checked_cells += 1
                    if isinstance(self.world.grid.get(check_pos), Rock):
                        rocks_count += 1
        
        return rocks_count / checked_cells if checked_cells > 0 else 0

    # Private Methods - Scanning & Search
    def _calculate_scan_vectors(self, current_pos: Position, target_pos: Position) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """Calculate primary and secondary vectors for scanning."""
        primary_vector = self._normalize_vector(
            target_pos[0] - current_pos[0],
            target_pos[1] - current_pos[1]
        )
        # Calculate perpendicular vector for secondary scanning
        secondary_vector = (-primary_vector[1], primary_vector[0])
        return primary_vector, secondary_vector

    def _calculate_check_position(self, main_pos: Position, secondary_vector: Tuple[float, float], offset: int) -> Position:
        """Calculate position to check based on main position and offset."""
        return (
            main_pos[0] + int(secondary_vector[0] * offset),
            main_pos[1] + int(secondary_vector[1] * offset)
        )

    def _find_best_visible_position(self, current_pos: Position, target_pos: Position) -> Optional[Position]:
        """Find best position along vector to target."""
        vectors = self._calculate_scan_vectors(current_pos, target_pos)
        return self._scan_for_best_position(current_pos, vectors, target_pos)

    def _scan_for_best_position(
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
            main_pos = self._get_main_scan_position(current_pos, primary_vector, d)
            best_pos, best_score = self._scan_perpendicular(
                current_pos, main_pos, secondary_vector, d, best_pos, best_score, target_pos
            )
        
        return best_pos

    def _get_main_scan_position(
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

    def _scan_perpendicular(
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
            check_pos = self._calculate_check_position(main_pos, secondary_vector, offset)
            
            if self._is_valid_check_position(current_pos, check_pos):
                score = self._score_position(check_pos, target_pos)
                if score < best_score:
                    best_score = score
                    best_pos = check_pos
                    
        return best_pos, best_score

    def _find_best_alternative_path(self, max_rocks: int, target_pos: Position) -> Optional[Tuple[List[Position], int]]:
        """Find the path with the best score using fewer rocks."""
        best_path = None
        best_score = float('inf')

        # Binary search for optimal rock count
        left, right = 0, max_rocks
        while left <= right:
            mid = (left + right) // 2
            if path := self.path_calculator.find_path_with_max_rocks(mid, target_pos):
                score = (STICK_VALUE * mid) + len(path)
                if score < best_score:
                    best_score = score
                    best_path = path
                right = mid - 1
            else:
                left = mid + 1

        return (best_path, best_score) if best_path else None

    # Private Methods - Movement Tracking
    def _update_movement_history(self, movement: Position) -> None:
        """Track the last movement direction for path scoring."""
        self.last_movement = movement

    def update(self, world) -> None:
        """Update pathfinder state and track movement."""
        super().update(world)
        if movement := self.get_movement():
            self._update_movement_history(movement)