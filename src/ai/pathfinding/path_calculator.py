from dataclasses import dataclass, field
from typing import List, Optional, Set, Tuple, Any, Callable
from src.utils.config import Position, Direction, GRID_SIZE, PathType
from src.cells import Cell, Rock, Stick

@dataclass
class PathCalculator:
    """Calculates optimal paths through the game grid.
    
    Implements pathfinding algorithms for finding routes to sticks,
    handling rock obstacles, and optimizing path lengths."""
    
    # Core Attributes
    world: Any  # Reference to game world state
    directions: List[Position] = field(default_factory=lambda: [
        Direction.UP.value,    # (0, -1)
        Direction.RIGHT.value, # (1, 0)
        Direction.DOWN.value,  # (0, 1)
        Direction.LEFT.value   # (-1, 0)
    ])

    # Public Methods - Path Finding
    def find_path_to_position(
        self, 
        target_pos: Position, 
        heuristic: Optional[Callable[[Position], float]] = None
    ) -> Optional[List[Position]]:
        """Find path to target position using optional heuristic for path scoring."""
        if not self.world.player:
            return None
            
        start_pos = self.world.player.position
        max_rocks = self.world.stats.sticks_collected if self.world.stats else float('inf')
        
        return self._breadth_first_search_with_rocks(start_pos, target_pos, max_rocks)

    def find_path_without_rocks(self, target_pos: Position) -> Optional[List[Position]]:
        """Finds path avoiding all rocks completely."""
        return self._breadth_first_search_no_rocks(self.world.player.position, target_pos)

    def find_path_with_max_rocks(self, max_rocks: int, target_pos: Position) -> Optional[List[Position]]:
        """Finds optimal path allowing limited rock removals."""
        return self.find_path_to_position(target_pos)

    # Public Methods - Grid Analysis
    def find_sticks(self) -> List[Position]:
        """Locates all stick positions in the current grid."""
        return [pos for pos, cell in self.world.grid.items() 
                if isinstance(cell, Stick)]

    def count_rocks_in_path(self, path: PathType) -> int:
        """Counts number of rock obstacles in a given path."""
        return sum(1 for pos in path if self._is_rock(pos))

    # Private Methods - Path Finding Core
    def _breadth_first_search_with_rocks(
        self, 
        start: Position, 
        target_pos: Position, 
        max_rocks: int
    ) -> Optional[List[Position]]:
        """Performs BFS pathfinding allowing rock removal."""
        queue = self._initialize_search_queue(start)
        visited = {(start, tuple())}
        best_path = None
        best_length = float('inf')
        
        while queue:
            current, path, removed_rocks = queue.pop(0)
            
            if self._should_skip_path(path, best_length):
                continue
            
            if self._is_target_reached(current, target_pos):
                best_path, best_length = self._update_best_path(path, best_length)
                continue

            self._explore_neighbors(current, path, removed_rocks, max_rocks, visited, queue)

        return best_path

    def _breadth_first_search_no_rocks(
        self, 
        start: Position, 
        target_pos: Position
    ) -> Optional[List[Position]]:
        """Performs BFS pathfinding avoiding all rocks."""
        queue = [(start, [start])]
        visited = {start}
        
        while queue:
            current, path = queue.pop(0)
            if current == target_pos:
                return path
            
            self._explore_rock_free_neighbors(current, path, visited, queue)
        
        return None

    # Private Methods - Search Helpers
    def _initialize_search_queue(
        self, 
        start: Position
    ) -> List[Tuple[Position, List[Position], Set[Position]]]:
        """Initialize the search queue with starting position."""
        return [(start, [start], set())]

    def _should_skip_path(self, path: List[Position], best_length: float) -> bool:
        """Determine if current path should be skipped."""
        return len(path) >= best_length

    def _is_target_reached(self, current: Position, target: Position) -> bool:
        """Check if current position is the target."""
        return current == target

    def _update_best_path(
        self, 
        path: List[Position], 
        current_best: float
    ) -> Tuple[List[Position], float]:
        """Update the best path if current is better."""
        return path, len(path)

    def _explore_neighbors(
        self,
        current: Position,
        path: List[Position],
        removed_rocks: Set[Position],
        max_rocks: int,
        visited: Set[Tuple[Position, Tuple[Position, ...]]],
        queue: List[Tuple[Position, List[Position], Set[Position]]]
    ) -> None:
        """Explore neighboring positions and update queue."""
        for next_pos in self._get_valid_neighbors(current):
            if result := self._try_path_through_position(
                next_pos, path, removed_rocks, max_rocks, visited
            ):
                queue.append(result)

    def _explore_rock_free_neighbors(
        self,
        current: Position,
        path: List[Position],
        visited: Set[Position],
        queue: List[Tuple[Position, List[Position]]]
    ) -> None:
        """Explore neighboring positions avoiding rocks."""
        for next_pos in self._get_valid_neighbors(current):
            if (next_pos not in visited and 
                not isinstance(self.world.grid.get(next_pos), Rock)):
                visited.add(next_pos)
                queue.append((next_pos, path + [next_pos]))

    def _try_path_through_position(
        self, 
        next_pos: Position, 
        current_path: List[Position], 
        removed_rocks: Set[Position],
        max_rocks: int,
        visited: Set[Tuple[Position, Tuple[Position, ...]]]
    ) -> Optional[Tuple[Position, List[Position], Set[Position]]]:
        """Attempts to extend path through a given position."""
        if not self._is_valid_path_extension(next_pos, removed_rocks, max_rocks):
            return None
            
        new_removed = self._update_removed_rocks(next_pos, removed_rocks)
        state = (next_pos, tuple(sorted(new_removed)))
        
        if state not in visited:
            visited.add(state)
            new_path = current_path + [next_pos]
            return (next_pos, new_path, new_removed)
            
        return None

    # Private Methods - Path Validation
    def _is_valid_path_extension(
        self, 
        pos: Position, 
        removed_rocks: Set[Position],
        max_rocks: int
    ) -> bool:
        """Check if position can be added to path."""
        if self._is_rock(pos):
            return len(removed_rocks) < max_rocks
        return True

    def _update_removed_rocks(
        self, 
        pos: Position, 
        removed_rocks: Set[Position]
    ) -> Set[Position]:
        """Update set of removed rocks if position contains rock."""
        new_removed = removed_rocks.copy()
        if self._is_rock(pos):
            new_removed.add(pos)
        return new_removed

    # Private Methods - Grid Navigation
    def _get_valid_neighbors(self, pos: Position) -> List[Position]:
        """Gets all valid neighboring positions."""
        return [next_pos for dx, dy in self.directions
                if (next_pos := self._get_next_position(pos, dx, dy))
                and self._is_valid_cell(next_pos)]

    def _get_next_position(self, pos: Position, dx: int, dy: int) -> Optional[Position]:
        """Calculates next position and validates bounds."""
        next_pos = (pos[0] + dx, pos[1] + dy)
        return next_pos if self._is_in_bounds(next_pos) else None

    # Private Methods - Grid Validation
    def _is_in_bounds(self, pos: Position) -> bool:
        """Checks if position is within grid bounds."""
        return (0 <= pos[0] < GRID_SIZE and 0 <= pos[1] < GRID_SIZE)

    def _is_valid_cell(self, pos: Position) -> bool:
        """Checks if position contains a valid cell type."""
        cell = self.world.grid.get(pos)
        return isinstance(cell, (Cell, Rock, Stick))

    def _is_rock(self, pos: Position) -> bool:
        """Checks if position contains a rock obstacle."""
        return isinstance(self.world.grid.get(pos), Rock)

    def _is_stick(self, pos: Position) -> bool:
        """Checks if position contains a stick."""
        return isinstance(self.world.grid.get(pos), Stick)