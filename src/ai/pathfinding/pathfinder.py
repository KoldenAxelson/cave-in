from dataclasses import dataclass
from typing import List, Any, Optional, Tuple
from src.utils.config import Position, Direction, STICK_VALUE, VIEW_RADIUS, GRID_SIZE
from src.ai.ai_interface import AIInterface
from src.utils.player_interface import PlayerInterface
from .path_calculator import PathCalculator
from .action_handler import ActionHandler
from src.cells.stick import Stick
from src.cells.rock import Rock
from src.cells.cell import Cell

@dataclass
class PathFinder(AIInterface):
    """AI that finds and follows optimal paths to collect sticks."""
    world: Any
    path_calculator: PathCalculator = None
    action_handler: ActionHandler = None
    current_path: List[Position] = None
    target_path: List[Position] = None
    player: PlayerInterface = None

    def __post_init__(self):
        """Initialize dependent components after dataclass initialization."""
        self.path_calculator = PathCalculator(self.world)
        self.action_handler = ActionHandler(self.world)
        self.current_path = []
        self.target_path = []
        self.player = PlayerInterface(self.world)
        self._calculate_next_path()

    def _calculate_next_path(self) -> None:
        """Calculate optimal path to nearest stick using view-radius limited pathfinding.
        
        Strategy:
        1. Find all sticks in the world
        2. Find closest stick (Manhattan distance)
        3. Calculate path to best visible position towards stick
        4. If no rocks in path, use it
        5. Otherwise, try paths with fewer rocks and compare scores
        """
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
        if not (unrestricted_path := self.path_calculator.find_path_to_position(visible_target)):
            self._clear_paths()
            return

        # Score unrestricted path
        rocks_in_unrestricted = self.path_calculator.count_rocks_in_path(unrestricted_path)
        unrestricted_score = (STICK_VALUE * rocks_in_unrestricted) + len(unrestricted_path)

        # Use unrestricted path if no rocks
        if rocks_in_unrestricted == 0:
            self._set_paths(unrestricted_path)
            return

        # Find best alternative path with fewer rocks
        best_path_info = self._find_best_alternative_path(rocks_in_unrestricted, visible_target)
        
        # Use best path if better than unrestricted, otherwise use unrestricted
        if best_path_info and best_path_info[1] < unrestricted_score:
            self._set_paths(best_path_info[0])
        else:
            # If surrounded by rocks, attempt to clear a path
            if self._is_surrounded_by_rocks(target_stick):
                self._attempt_to_clear_path(target_stick)
            else:
                self._set_paths(unrestricted_path)

    def _find_closest_stick(self, current_pos: Position, sticks: List[Position]) -> Position:
        """Find the closest stick using Manhattan distance."""
        return min(sticks, key=lambda pos: self._manhattan_distance(current_pos, pos))

    def _manhattan_distance(self, pos1: Position, pos2: Position) -> int:
        """Calculate Manhattan distance between two positions."""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def _find_best_visible_position(self, current_pos: Position, target_pos: Position) -> Optional[Position]:
        """Find best position within view radius considering both proximity and path quality.
        
        Uses vector math to find the closest valid position in the direction of the target.
        If the target stick is visible, prioritize pathing directly to it.
        """
        # Early return if adjacent to target
        if self._is_adjacent(current_pos, target_pos):
            return target_pos

        # If target is within view radius and we can path to it, prioritize it
        if (self._manhattan_distance(current_pos, target_pos) <= VIEW_RADIUS and 
            self._is_valid_position(target_pos)):
            return target_pos

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
        closest_any = self._find_closest_valid_position(current_pos, target_direction)

        if not closest_any:
            return target_pos

        return closest_any

    def _find_closest_valid_position(self, current_pos: Position, target_pos: Position, empty_only: bool = False) -> Optional[Position]:
        """Find closest valid position to target within view radius.
        
        Args:
            current_pos: Starting position
            target_pos: Ideal target position
            empty_only: If True, only consider empty cells
        """
        best_pos = None
        best_distance = float('inf')
        
        # Search in expanding square around target position
        for radius in range(VIEW_RADIUS + 1):
            for dx in range(-radius, radius + 1):
                for dy in [-radius, radius]:
                    check_pos = (target_pos[0] + dx, target_pos[1] + dy)
                    if self._is_valid_check_position(current_pos, check_pos, empty_only):
                        dist = self._manhattan_distance(check_pos, target_pos)
                        if dist < best_distance:
                            best_distance = dist
                            best_pos = check_pos
                            
            for dy in range(-radius + 1, radius):
                for dx in [-radius, radius]:
                    check_pos = (target_pos[0] + dx, target_pos[1] + dy)
                    if self._is_valid_check_position(current_pos, check_pos, empty_only):
                        dist = self._manhattan_distance(check_pos, target_pos)
                        if dist < best_distance:
                            best_distance = dist
                            best_pos = check_pos
                            
            if best_pos:  # Found valid position at this radius
                break
            
        return best_pos

    def _is_valid_check_position(self, current_pos: Position, check_pos: Position, empty_only: bool) -> bool:
        """Check if a position is valid for pathfinding.
        
        Args:
            current_pos: Current position
            check_pos: Position to check
            empty_only: If True, only consider empty cells
        """
        if not self._is_valid_position(check_pos):
            return False
        
        if self._manhattan_distance(current_pos, check_pos) > VIEW_RADIUS:
            return False
        
        if empty_only:
            return self._is_empty_cell(check_pos)
        
        return True

    def _is_adjacent(self, pos1: Position, pos2: Position) -> bool:
        """Check if two positions are adjacent (including diagonals)."""
        return abs(pos1[0] - pos2[0]) <= 1 and abs(pos1[1] - pos2[1]) <= 1

    def _is_empty_cell(self, pos: Position) -> bool:
        """Check if position contains an empty cell."""
        cell = self.world.grid.get(pos)
        return isinstance(cell, Cell) and not isinstance(cell, (Rock, Stick))

    def _is_valid_position(self, pos: Position) -> bool:
        """Check if a position is valid (in bounds and walkable)."""
        if not (0 <= pos[0] < GRID_SIZE and 0 <= pos[1] < GRID_SIZE):
            return False
        
        cell = self.world.grid.get(pos)
        return isinstance(cell, (Cell, Rock, Stick))

    def _find_best_alternative_path(self, max_rocks: int, target_pos: Position) -> Optional[Tuple[List[Position], int]]:
        """Find the path with the best score using fewer rocks.
        
        Args:
            max_rocks: Maximum number of rocks in the unrestricted path
            target_pos: Position we're trying to reach
            
        Returns:
            Tuple of (best_path, best_score) if found, None otherwise
        """
        best_path = None
        best_score = float('inf')

        for allowed_rocks in range(max_rocks - 1, -1, -1):
            if path := self.path_calculator.find_path_with_max_rocks(allowed_rocks, target_pos):
                rocks = self.path_calculator.count_rocks_in_path(path)
                score = (STICK_VALUE * rocks) + len(path)
                
                if score < best_score:
                    best_score = score
                    best_path = path

        return (best_path, best_score) if best_path else None

    def get_movement(self) -> Position:
        """Calculate and return the next movement for the AI."""
        if self.action_handler.did_use_action():
            return (0, 0)

        if not self.current_path:
            self._calculate_next_path()
            if not self.current_path:
                return (0, 0)

        return self._calculate_movement()

    def should_use_action(self) -> bool:
        """Determine if the AI should use an action."""
        return self.action_handler.should_use_action()

    def update(self, world) -> None:
        """Update AI state with new world information."""
        old_world = self.world
        self._update_components(world)
        
        if self._world_state_changed(old_world, world) or not self.current_path:
            self._calculate_next_path()

    def _clear_paths(self) -> None:
        """Reset path information."""
        self.current_path = []
        self.target_path = []
        self.action_handler.update(self.world, [])

    def _set_paths(self, path: List[Position]) -> None:
        """Update path information with new path."""
        self.target_path = path
        self.current_path = path[1:]  # Skip current position
        self.action_handler.update(self.world, self.target_path)

    def _calculate_movement(self) -> Position:
        """Calculate the next movement based on current path."""
        next_pos = self.current_path[0]
        current_pos = self.player.position
        
        dx = next_pos[0] - current_pos[0]
        dy = next_pos[1] - current_pos[1]
        
        movement = self._get_movement_direction(dx, dy)
        
        if any(movement) and self.player.try_move(movement):
            self.current_path.pop(0)
        
        return movement

    @staticmethod
    def _get_movement_direction(dx: int, dy: int) -> Position:
        """Convert position delta to movement direction."""
        if dx > 0: return Direction.RIGHT.value
        if dx < 0: return Direction.LEFT.value
        if dy > 0: return Direction.DOWN.value
        if dy < 0: return Direction.UP.value
        return Direction.NONE.value

    def _update_components(self, world) -> None:
        """Update all component references with new world state."""
        self.world = world
        self.path_calculator.world = world
        self.action_handler.update(world, self.target_path)
        self.player = PlayerInterface(world)

    def _world_state_changed(self, old_world, new_world) -> bool:
        """Check if relevant world state has changed."""
        if not old_world or not new_world:
            return True
        
        def get_positions(world, cell_type):
            return {pos for pos, cell in world.grid.items() 
                   if isinstance(cell, cell_type)}
        
        old_sticks = get_positions(old_world, Stick)
        new_sticks = get_positions(new_world, Stick)
        old_rocks = get_positions(old_world, Rock)
        new_rocks = get_positions(new_world, Rock)
        
        return old_sticks != new_sticks or old_rocks != new_rocks

    def _is_surrounded_by_rocks(self, pos: Position) -> bool:
        """Check if a position is completely surrounded by rocks or the edge of the map."""
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                neighbor = (pos[0] + dx, pos[1] + dy)
                if not self._is_rock_or_edge(neighbor):
                    return False
        return True

    def _is_rock_or_edge(self, pos: Position) -> bool:
        """Check if a position is a rock or at the edge of the map."""
        if not (0 <= pos[0] < GRID_SIZE and 0 <= pos[1] < GRID_SIZE):
            return True  # Treat out-of-bounds as blocked
        return isinstance(self.world.grid.get(pos), Rock)

    def _attempt_to_clear_path(self, target_pos: Position) -> None:
        """Attempt to clear a path to the target by removing rocks."""
        if self.world.stats.sticks_collected > 0:
            # Try to remove rocks around the target
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    neighbor = (target_pos[0] + dx, target_pos[1] + dy)
                    if self._is_rock(neighbor):
                        self.world.grid[neighbor] = Cell(neighbor)
                        self.world.stats.sticks_collected -= 1
                        return
        self._clear_paths()

    def _is_rock(self, pos: Position) -> bool:
        """Check if a position contains a rock."""
        return isinstance(self.world.grid.get(pos), Rock)