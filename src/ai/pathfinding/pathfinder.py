from dataclasses import dataclass
from typing import List, Any, Optional, Tuple
from src.utils.config import Position, Direction, STICK_VALUE
from src.ai.ai_interface import AIInterface
from src.utils.player_interface import PlayerInterface
from .path_calculator import PathCalculator
from .action_handler import ActionHandler
from src.cells.stick import Stick
from src.cells.rock import Rock

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
        """Calculate optimal path to nearest stick based on path scoring.
        
        Finds the best path by:
        1. Getting unrestricted path to nearest stick
        2. If no rocks in path, use it
        3. Otherwise, try paths with fewer rocks and compare scores
        4. Score = (STICK_VALUE * rocks_in_path) + path_length
        """
        # Early returns if no valid paths exist
        if not (sticks := self.path_calculator.find_sticks()):
            self._clear_paths()
            return

        if not (unrestricted_path := self.path_calculator.find_unrestricted_path()):
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
        best_path_info = self._find_best_alternative_path(rocks_in_unrestricted)
        
        # Use best path if better than unrestricted, otherwise use unrestricted
        if best_path_info and best_path_info[1] < unrestricted_score:
            self._set_paths(best_path_info[0])
        else:
            self._set_paths(unrestricted_path)

    def _find_best_alternative_path(self, max_rocks: int) -> Optional[Tuple[List[Position], int]]:
        """Find the path with the best score using fewer rocks."""
        best_path = None
        best_score = float('inf')

        for allowed_rocks in range(max_rocks - 1, -1, -1):
            if path := self.path_calculator.find_path_with_max_rocks(allowed_rocks):
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