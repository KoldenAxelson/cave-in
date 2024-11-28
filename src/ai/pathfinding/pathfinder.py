from dataclasses import dataclass
from typing import List, Any, Optional, Tuple
from src.utils.config import Position, Direction, STICK_VALUE, VIEW_RADIUS, GRID_SIZE
from src.ai.ai_interface import AIInterface
from src.utils.player_interface import PlayerInterface
from .path_calculator import PathCalculator
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

    # Initialization
    def __post_init__(self):
        """Initialize dependent components after dataclass initialization."""
        self.path_calculator = PathCalculator(self.world)
        self.action_handler = ActionHandler(self.world)
        self.current_path = []
        self.player = PlayerInterface(self.world)
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
        """Calculate optimal path to nearest stick.
        Orchestrates the path finding process."""
        if not self._has_valid_state():
            self._clear_paths()
            return

        target_stick = self._find_closest_stick()
        if not target_stick:
            self._clear_paths()
            return
        
        self._find_and_set_path(target_stick)

    def _find_and_set_path(self, target_stick: Position) -> None:
        """Find and set optimal path to target stick.
        Tries rock-free path first, then considers rock removal."""
        if path := self.path_calculator.find_path_without_rocks(target_stick):
            self._set_paths(path)
            return
        
        visible_target = self._find_best_visible_position(self.world.player.position, target_stick)
        if not visible_target:
            self._clear_paths()
            return
        
        self._find_optimal_path_with_rocks(visible_target)

    def _find_optimal_path_with_rocks(self, target_pos: Position) -> None:
        """Find optimal path considering rock removal.
        Balances path length against number of rocks to remove."""
        best_path = None
        best_score = float('inf')
        
        if path := self.path_calculator.find_path_to_position(target_pos):
            rocks_in_path = self.path_calculator.count_rocks_in_path(path)
            score = (STICK_VALUE * rocks_in_path) + len(path)
            
            if rocks_in_path == 0:
                self._set_paths(path)
                return
            
            best_path = path
            best_score = score
        
        if alternative := self._find_best_alternative_path(
            max_rocks=self.path_calculator.count_rocks_in_path(best_path) if best_path else float('inf'),
            target_pos=target_pos
        ):
            alt_path, alt_score = alternative
            if alt_score < best_score:
                best_path = alt_path
                best_score = alt_score

        if best_path:
            self._set_paths(best_path)
        else:
            self._clear_paths()

    # Private Methods - Path Management
    def _clear_paths(self) -> None:
        """Reset path information.
        Clears current path and updates action handler."""
        self.current_path = []
        self.action_handler.update(self.world, [])

    def _set_paths(self, path: List[Position]) -> None:
        """Update path information with new path.
        Skips current position and updates action handler."""
        self.current_path = path[1:]  # Skip current position
        self.action_handler.update(self.world, path)

    # Private Methods - Movement Calculation
    def _calculate_movement(self) -> Position:
        """Calculate the next movement based on current path.
        Returns movement direction or NONE if no movement needed."""
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
        """Convert position delta to movement direction.
        Maps coordinate changes to cardinal directions."""
        if dx > 0: return Direction.RIGHT.value
        if dx < 0: return Direction.LEFT.value
        if dy > 0: return Direction.DOWN.value
        if dy < 0: return Direction.UP.value
        return Direction.NONE.value

    # Private Methods - State Validation
    def _has_valid_state(self) -> bool:
        """Check if pathfinding prerequisites are met.
        Ensures player exists and sticks are available."""
        return (self.world.player and 
                bool(sticks := self.path_calculator.find_sticks()))

    def _find_closest_stick(self) -> Optional[Position]:
        """Find closest stick using Manhattan distance.
        Returns None if no sticks are available."""
        if not self.world.player:
            return None
        sticks = self.path_calculator.find_sticks()
        if not sticks:
            return None
        return min(sticks, key=lambda pos: self.manhattan_distance(self.world.player.position, pos))

    # Utility Methods
    @staticmethod
    def manhattan_distance(pos1: Position, pos2: Position) -> int:
        """Calculate Manhattan distance between two positions.
        Used for finding closest sticks."""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    # Private Methods - Position Calculations
    def _find_best_visible_position(self, current_pos: Position, target_pos: Position) -> Optional[Position]:
        """Find best position within view radius considering path quality."""
        if self._is_within_view_radius(current_pos, target_pos):
            return target_pos
            
        dx = target_pos[0] - current_pos[0]
        dy = target_pos[1] - current_pos[1]
        
        max_delta = max(abs(dx), abs(dy))
        if max_delta > 0:
            scale = min(VIEW_RADIUS, max_delta) / max_delta
            dx = int(dx * scale)
            dy = int(dy * scale)
        
        target_direction = (current_pos[0] + dx, current_pos[1] + dy)
        
        # Try to find a walkable position first
        if walkable_pos := self._find_closest_walkable_position(current_pos, target_direction):
            return walkable_pos
            
        # Fall back to any valid position if no walkable path exists
        return self._find_closest_valid_position(current_pos, target_direction)

    def _find_closest_valid_position(self, current_pos: Position, target_pos: Position) -> Optional[Position]:
        """Find closest valid position to target within view radius."""
        best_pos = None
        best_distance = float('inf')
        
        for dx in range(-VIEW_RADIUS, VIEW_RADIUS + 1):
            for dy in range(-VIEW_RADIUS, VIEW_RADIUS + 1):
                check_pos = (target_pos[0] + dx, target_pos[1] + dy)
                
                if self._is_valid_check_position(current_pos, check_pos):
                    dist_to_target = self.manhattan_distance(check_pos, target_pos)
                    if dist_to_target < best_distance:
                        best_distance = dist_to_target
                        best_pos = check_pos
        
        return best_pos

    def _find_closest_walkable_position(self, current_pos: Position, target_pos: Position) -> Optional[Position]:
        """Find closest position that doesn't contain a rock within view radius."""
        best_pos = None
        best_distance = float('inf')
        
        for dx in range(-VIEW_RADIUS, VIEW_RADIUS + 1):
            for dy in range(-VIEW_RADIUS, VIEW_RADIUS + 1):
                check_pos = (target_pos[0] + dx, target_pos[1] + dy)
                
                if (self._is_valid_check_position(current_pos, check_pos) and 
                    not isinstance(self.world.grid.get(check_pos), Rock)):
                    dist_to_target = self.manhattan_distance(check_pos, target_pos)
                    if dist_to_target < best_distance:
                        best_distance = dist_to_target
                        best_pos = check_pos
        
        return best_pos

    def _is_valid_check_position(self, current_pos: Position, check_pos: Position) -> bool:
        """Check if a position is valid for pathfinding."""
        if not self._is_valid_position(check_pos):
            return False
        
        return self._is_within_view_radius(current_pos, check_pos)

    def _is_valid_position(self, pos: Position) -> bool:
        """Check if a position is valid (in bounds and walkable)."""
        if not (0 <= pos[0] < GRID_SIZE and 0 <= pos[1] < GRID_SIZE):
            return False
        
        cell = self.world.grid.get(pos)
        return isinstance(cell, (Cell, Rock, Stick))

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

    def _is_within_view_radius(self, pos1: Position, pos2: Position) -> bool:
        """Check if two positions are within view radius of each other."""
        return self.manhattan_distance(pos1, pos2) <= VIEW_RADIUS