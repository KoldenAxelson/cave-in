from dataclasses import dataclass
from typing import List, Set, Tuple, Optional, Any
from src.utils.config import Position, PathType

@dataclass
class PathSearch:
    """Implements search algorithms for pathfinding.
    
    Handles path searching strategies including BFS with and without rocks,
    and manages path optimization and validation."""
    
    # Core Attributes
    world: Any  # Reference to game world state
    grid_analyzer: Any  # Reference to grid analysis helper

    def breadth_first_search_with_rocks(
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

            self.explore_neighbors(
                current, path, removed_rocks, max_rocks, visited, queue
            )

        return best_path

    def breadth_first_search_no_rocks(
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
            
            self.explore_rock_free_neighbors(
                current, path, visited, queue
            )
        
        return None
    

    def explore_neighbors(
        self,
        current: Position,
        path: List[Position],
        removed_rocks: Set[Position],
        max_rocks: int,
        visited: Set[Position],
        queue: List[Position]
    ) -> None:
        """Explore neighboring positions and update queue."""
        for next_pos in self.grid_analyzer.get_valid_neighbors(current):
            if result := self._try_path_through_position(
                next_pos, path, removed_rocks, max_rocks, visited
            ):
                queue.append(result)

    def explore_rock_free_neighbors(
        self,
        current: Position,
        path: List[Position],
        visited: Set[Position],
        queue: List[Position]
    ) -> None:
        """Explore neighboring positions avoiding rocks."""
        for next_pos in self.grid_analyzer.get_valid_neighbors(current):
            if (next_pos not in visited and 
                not self.grid_analyzer.is_rock(next_pos)):
                visited.add(next_pos)
                queue.append((next_pos, path + [next_pos]))

    # Private Methods - Search Queue Management
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

    def _is_valid_path_extension(
        self, 
        pos: Position, 
        removed_rocks: Set[Position],
        max_rocks: int
    ) -> bool:
        """Check if position can be added to path."""
        if self.grid_analyzer.is_rock(pos):
            return len(removed_rocks) < max_rocks
        return True

    def _update_removed_rocks(
        self, 
        pos: Position, 
        removed_rocks: Set[Position]
    ) -> Set[Position]:
        """Update set of removed rocks if position contains rock."""
        new_removed = removed_rocks.copy()
        if self.grid_analyzer.is_rock(pos):
            new_removed.add(pos)
        return new_removed 