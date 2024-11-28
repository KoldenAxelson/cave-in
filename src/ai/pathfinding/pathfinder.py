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
        if not (sticks := self.path_calculator.find_sticks()) or not self.world.player:
            self._clear_paths()
            return

        current_pos = self.world.player.position
        target_stick = self._find_closest_stick(current_pos, sticks)
        
        # Try to find ANY walkable path to the stick (no rocks)
        if path := self.path_calculator.find_path_without_rocks(target_stick):
            self._set_paths(path)
            return
        
        print(f"WARNING: No rock-free path found to stick at {target_stick}")
        
        # Only if no walkable path exists, try paths with rocks
        visible_target = self._find_best_visible_position(current_pos, target_stick)
        if not visible_target:
            self._clear_paths()
            return
        
        # Try to find optimal path considering rocks
        best_path = None
        best_score = float('inf')
        
        # First try direct path to target
        if path := self.path_calculator.find_path_to_position(visible_target):
            rocks_in_path = self.path_calculator.count_rocks_in_path(path)
            score = (STICK_VALUE * rocks_in_path) + len(path)
            
            if rocks_in_path == 0:  # If no rocks, this is optimal
                self._set_paths(path)
                return
            
            best_path = path
            best_score = score
        
        # Try paths with fewer rocks if initial path had rocks
        if alternative := self._find_best_alternative_path(
            max_rocks=self.path_calculator.count_rocks_in_path(best_path) if best_path else float('inf'),
            target_pos=visible_target
        ):
            alt_path, alt_score = alternative
            if alt_score < best_score:
                best_path = alt_path
                best_score = alt_score

        if best_path:
            self._set_paths(best_path)
        else:
            self._clear_paths()

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
        """Find closest valid position to target within view radius."""
        best_pos = None
        best_distance = float('inf')
        
        # Search all positions within view radius
        for dx in range(-VIEW_RADIUS, VIEW_RADIUS + 1):
            for dy in range(-VIEW_RADIUS, VIEW_RADIUS + 1):
                check_pos = (target_pos[0] + dx, target_pos[1] + dy)
                
                # Check if position is valid and within view radius
                if self._is_valid_check_position(current_pos, check_pos):
                    dist_to_target = self.manhattan_distance(check_pos, target_pos)
                    if dist_to_target < best_distance:
                        best_distance = dist_to_target
                        best_pos = check_pos
        
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

        # Binary search for optimal rock count
        left, right = 0, max_rocks
        while left <= right:
            mid = (left + right) // 2
            if path := self.path_calculator.find_path_with_max_rocks(mid, target_pos):
                score = (STICK_VALUE * mid) + len(path)
                if score < best_score:
                    best_score = score
                    best_path = path
                # If path exists with this many rocks, try fewer
                right = mid - 1
            else:
                # If no path exists with this few rocks, try more
                left = mid + 1

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

    def _find_closest_walkable_position(self, current_pos: Position, target_pos: Position) -> Optional[Position]:
        """Find closest position that doesn't contain a rock within view radius."""
        best_pos = None
        best_distance = float('inf')
        
        # Search all positions within view radius
        for dx in range(-VIEW_RADIUS, VIEW_RADIUS + 1):
            for dy in range(-VIEW_RADIUS, VIEW_RADIUS + 1):
                check_pos = (target_pos[0] + dx, target_pos[1] + dy)
                
                # Check if position is valid, within view radius, and not a rock
                if (self._is_valid_check_position(current_pos, check_pos) and 
                    not isinstance(self.world.grid.get(check_pos), Rock)):
                    dist_to_target = self.manhattan_distance(check_pos, target_pos)
                    if dist_to_target < best_distance:
                        best_distance = dist_to_target
                        best_pos = check_pos
        
        return best_pos