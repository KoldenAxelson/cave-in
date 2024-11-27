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
    """AI that finds and follows optimal paths to collect sticks."""
    world: Any
    path_calculator: PathCalculator = None
    action_handler: ActionHandler = None
    current_path: List[Position] = None
    player: PlayerInterface = None

    def __post_init__(self):
        """Initialize dependent components after dataclass initialization."""
        self.path_calculator = PathCalculator(self.world)
        self.action_handler = ActionHandler(self.world)
        self.current_path = []
        self.player = PlayerInterface(self.world)
        self._calculate_next_path()

    def _calculate_next_path(self) -> None:
        """Calculate optimal path to nearest stick using view-radius limited pathfinding."""
        if not (sticks := self.path_calculator.find_sticks()):
            self._clear_paths()
            return

        if not self.world.player:
            self._clear_paths()
            return

        current_pos = self.world.player.position
        target_stick = self._find_closest_stick(current_pos, sticks)
        
        # Find best visible position towards stick
        visible_target = self._find_best_visible_position(current_pos, target_stick)
        
        if not visible_target:
            self._clear_paths()
            return

        # Get path to visible target
        if not (path := self.path_calculator.find_path_to_position(visible_target)):
            self._clear_paths()
            return

        # Check for rocks in path
        rocks_in_path = self.path_calculator.count_rocks_in_path(path)
        
        # If no rocks, use path directly
        if rocks_in_path == 0:
            self._set_paths(path)
            return
            
        # Calculate score for current path
        current_score = (STICK_VALUE * rocks_in_path) + len(path)
        
        # Try to find better path with fewer rocks
        if best_path_info := self._find_best_alternative_path(rocks_in_path, visible_target):
            if best_path_info[1] < current_score:
                self._set_paths(best_path_info[0])
                return
                
        # Use original path if no better alternative found
        self._set_paths(path)

    def _find_closest_stick(self, current_pos: Position, sticks: List[Position]) -> Position:
        """Find the closest stick using Manhattan distance."""
        return min(sticks, key=lambda pos: self.manhattan_distance(current_pos, pos))

    def _find_best_visible_position(self, current_pos: Position, target_pos: Position) -> Optional[Position]:
        """Find best position within view radius considering path quality."""
        # Calculate direction vector
        dx = target_pos[0] - current_pos[0]
        dy = target_pos[1] - current_pos[1]
        
        # Normalize to largest step within VIEW_RADIUS
        max_delta = max(abs(dx), abs(dy))
        if max_delta > 0:
            scale = min(VIEW_RADIUS, max_delta) / max_delta
            dx = int(dx * scale)
            dy = int(dy * scale)
        
        # Calculate best position in direction of target
        target_direction = (current_pos[0] + dx, current_pos[1] + dy)
        return self._find_closest_valid_position(current_pos, target_direction)

    def _find_closest_valid_position(self, current_pos: Position, target_pos: Position) -> Optional[Position]:
        """Find closest valid position to target within view radius using spiral search."""
        best_pos = None
        best_distance = float('inf')
        
        # Search in a spiral pattern from target position
        for dist in range(VIEW_RADIUS + 1):
            for dx in range(-dist, dist + 1):
                for dy in [-dist, dist]:
                    check_pos = (target_pos[0] + dx, target_pos[1] + dy)
                    if self._is_valid_check_position(current_pos, check_pos):
                        dist_to_target = self.manhattan_distance(check_pos, target_pos)
                        if dist_to_target < best_distance:
                            best_distance = dist_to_target
                            best_pos = check_pos
            
            if best_pos:  # Found valid position at this radius
                break
                
        return best_pos

    def _is_valid_check_position(self, current_pos: Position, check_pos: Position) -> bool:
        """Check if a position is valid for pathfinding."""
        if not self._is_valid_position(check_pos):
            return False
        
        return self.manhattan_distance(current_pos, check_pos) <= VIEW_RADIUS

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

        for allowed_rocks in range(max_rocks):
            if path := self.path_calculator.find_path_with_max_rocks(allowed_rocks, target_pos):
                score = (STICK_VALUE * allowed_rocks) + len(path)
                
                if score < best_score:
                    best_score = score
                    best_path = path

        return (best_path, best_score) if best_path else None

    def get_movement(self) -> Position:
        """Calculate and return the next movement for the AI."""
        if self.action_handler.did_use_action():
            return Direction.NONE.value

        if not self.current_path:
            self._calculate_next_path()
            
        return self._calculate_movement()

    def should_use_action(self) -> bool:
        """Determine if the AI should use an action."""
        return self.action_handler.should_use_action()

    def update(self, world) -> None:
        """Update AI state with new world information."""
        self.world = world
        self.path_calculator.world = world
        self.action_handler.update(world, self.current_path)
        self.player = PlayerInterface(world)
        self._calculate_next_path()

    def _clear_paths(self) -> None:
        """Reset path information."""
        self.current_path = []
        self.action_handler.update(self.world, [])

    def _set_paths(self, path: List[Position]) -> None:
        """Update path information with new path."""
        self.current_path = path[1:]  # Skip current position
        self.action_handler.update(self.world, path)

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
    
    @staticmethod
    def manhattan_distance(pos1: Position, pos2: Position) -> int:
        """Calculate Manhattan distance between two positions."""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])