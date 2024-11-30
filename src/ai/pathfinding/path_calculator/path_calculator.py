from dataclasses import dataclass, field
from typing import List, Optional, Callable, Any
from src.utils.config import Position, Direction, PathType
from .grid_analyzer import GridAnalyzer
from .path_search import PathSearch
from src.cells import Stick

@dataclass
class PathCalculator:
    """Core pathfinding coordinator that manages path calculation strategies.
    
    Delegates to specialized components for grid analysis and path searching
    while maintaining the main pathfinding interface."""
    
    # Core Attributes
    world: Any  # Reference to game world state
    directions: List[Position] = field(default_factory=lambda: [
        Direction.UP.value,    # (0, -1)
        Direction.RIGHT.value, # (1, 0)
        Direction.DOWN.value,  # (0, 1)
        Direction.LEFT.value   # (-1, 0)
    ])
    grid_analyzer: GridAnalyzer = field(init=False)
    path_search: PathSearch = field(init=False)

    def __post_init__(self):
        """Initialize specialized components after dataclass creation."""
        self.grid_analyzer = GridAnalyzer(self.world, self.directions)
        self.path_search = PathSearch(self.world, self.grid_analyzer)

    def count_rocks_in_path(self, path: PathType) -> int:
        """Counts number of rock obstacles in a given path."""
        return sum(1 for pos in path if self.grid_analyzer.is_rock(pos))

    def find_path_to_position(
        self, 
        target_pos: Position, 
        heuristic: Optional[Callable[[Position], float]] = None
    ) -> Optional[List[Position]]:
        """Find path to target position using optional heuristic for path scoring."""
        start_pos = self.world.player.position
        max_rocks = self.world.stats.sticks_collected if self.world.stats else float('inf')
        
        return self.path_search.breadth_first_search(
            start_pos, 
            target_pos, 
            max_rocks
        )

    def find_path_without_rocks(self, target_pos: Position) -> Optional[List[Position]]:
        """Finds path avoiding all rocks completely."""
        return self.path_search.breadth_first_search(
            self.world.player.position, 
            target_pos
            # max_rocks defaults to 0
        )

    def find_path_with_max_rocks(
        self, 
        max_rocks: int, 
        target_pos: Position
    ) -> Optional[List[Position]]:
        """Finds optimal path allowing limited rock removals."""
        return self.path_search.breadth_first_search(
            self.world.player.position,
            target_pos,
            max_rocks
        )

    def find_sticks(self) -> List[Position]:
        """Locates all stick positions in the current grid."""
        return [pos for pos, cell in self.world.grid.items() 
                if isinstance(cell, Stick)]