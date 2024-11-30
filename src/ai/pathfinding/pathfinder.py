from dataclasses import dataclass
from typing import List, Any, Optional, Tuple
from src.utils.config import Position, Direction, STICK_VALUE
from src.ai.ai_interface import AIInterface
from src.utils.player_interface import PlayerInterface
from .path_calculator import PathCalculator
from .path_calculator.vector_math import VectorMath
from .path_calculator.position_scorer import PositionScorer
from .path_calculator.grid_scanner import GridScanner
from .action_handler import ActionHandler

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
    
    # Helper Components
    vector_math: VectorMath = None
    position_scorer: PositionScorer = None
    grid_scanner: GridScanner = None

    def __post_init__(self):
        """Initialize dependent components after dataclass initialization."""
        self.path_calculator = PathCalculator(self.world)
        self.action_handler = ActionHandler(self.world)
        self.current_path = []
        self.player = PlayerInterface(self.world)
        self.last_movement = Direction.NONE.value
        
        # Initialize helper components
        self.vector_math = VectorMath()
        self.position_scorer = PositionScorer(self.world, self.vector_math)
        self.grid_scanner = GridScanner(self.world, self.vector_math, self.position_scorer)
        
        self._calculate_next_path()

    # Public Methods - AI Interface Implementation
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
        self.position_scorer.world = world
        self.grid_scanner.world = world
        self._calculate_next_path()

    # Private Methods - Path Planning
    def _calculate_next_path(self) -> None:
        """Calculate optimal path to nearest stick."""
        target_stick = self.position_scorer.find_closest_stick(
            self.player.position,
            self.path_calculator.find_sticks()
        )
        if not target_stick:
            self._clear_paths()
            return
        
        self._find_and_set_path(target_stick)

    def _find_and_set_path(self, target_stick: Position) -> None:
        """Find and set optimal path to target stick."""
        if path := self.path_calculator.find_path_without_rocks(target_stick):
            self._set_paths(path)
            return
        
        visible_target = self.grid_scanner.find_best_visible_position(
            self.player.position, 
            target_stick
        )
        
        self._find_optimal_path_with_rocks(visible_target)

    def _find_optimal_path_with_rocks(self, target_pos: Position) -> None:
        """Find optimal path considering rock removal."""
        path = self._find_initial_path(target_pos)
        self._optimize_path_with_rocks(path, target_pos)

    def _find_initial_path(self, target_pos: Position) -> Optional[List[Position]]:
        """Find initial path using momentum heuristic."""
        current_direction = self.vector_math.get_current_movement_direction(
            self.current_path,
            self.player.facing if self.player else None
        )
        
        def momentum_heuristic(pos: Position) -> float:
            direction_change = self.vector_math.calculate_direction_change(
                current_direction, 
                pos,
                self.player.position
            )
            return direction_change * 0.3
            
        return self.path_calculator.find_path_to_position(target_pos, heuristic=momentum_heuristic)

    def _optimize_path_with_rocks(self, path: List[Position], target_pos: Position) -> None:
        """Optimize path by potentially finding alternative with fewer rocks."""
        rocks_in_path = self.path_calculator.count_rocks_in_path(path)
        
        if rocks_in_path == 0:
            self._set_paths(path)
            return
            
        if alternative := self.grid_scanner.find_best_alternative_path(
            rocks_in_path, 
            target_pos,
            self.path_calculator,
            STICK_VALUE
        ):
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

    def _calculate_movement(self) -> Position:
        """Calculate the next movement based on current path."""
        if not self.current_path:
            return Direction.NONE.value
            
        next_pos = self.current_path[0]
        current_pos = self.player.position
        
        dx = next_pos[0] - current_pos[0]
        dy = next_pos[1] - current_pos[1]
        
        movement = self.vector_math.get_movement_direction(dx, dy)
        
        if movement != Direction.NONE.value and self.player.try_move(movement):
            self.current_path.pop(0)
            self.last_movement = movement
        
        return movement