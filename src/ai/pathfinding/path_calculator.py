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

    # Private Methods - Path Finding
    def _find_unrestricted_path(self) -> Optional[PathType]:
        """Finds shortest path to nearest stick, ignoring rock obstacles.
        Used for initial path planning before considering rock removal."""
        if not self._can_find_path():
            return None
        return self._find_shortest_path_to_sticks()

    def find_path_with_max_rocks(self, max_rocks: int, target_pos: Position) -> Optional[List[Position]]:
        """Finds optimal path allowing limited rock removals."""
        return self.find_path_to_position(target_pos)

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
        if not self.world.player:
            return None
        
        start = self.world.player.position
        queue = [(start, [start])]
        visited = {start}
        
        while queue:
            current, path = queue.pop(0)
            if current == target_pos:
                return path
            
            for next_pos in self._get_valid_neighbors(current):
                if (next_pos not in visited and 
                    not isinstance(self.world.grid.get(next_pos), Rock)):
                    visited.add(next_pos)
                    queue.append((next_pos, path + [next_pos]))
                
        return None

    # Public Methods - Grid Analysis
    def find_sticks(self) -> List[Position]:
        """Locates all stick positions in the current grid."""
        return [pos for pos, cell in self.world.grid.items() 
                if isinstance(cell, Stick)]

    def count_rocks_in_path(self, path: PathType) -> int:
        """Counts number of rock obstacles in a given path."""
        return sum(1 for pos in path if self._is_rock(pos))

    # Private Methods - Path Finding Helpers
    def _can_find_path(self) -> bool:
        """Validates basic pathfinding prerequisites."""
        return self.world.player and bool(self.find_sticks())

    def _find_shortest_path_to_sticks(self) -> Optional[PathType]:
        """Finds shortest path among all available sticks."""
        shortest_path = None
        shortest_length = float('inf')
        
        for stick_pos in self.find_sticks():
            if path := self.find_path_with_max_rocks(float('inf'), stick_pos):
                if len(path) < shortest_length:
                    shortest_path = path
                    shortest_length = len(path)
                
        return shortest_path

    def _breadth_first_search_with_rocks(self, start: Position, target_pos: Position, max_rocks: int) -> Optional[List[Position]]:
        """Performs BFS pathfinding allowing rock removal."""
        queue: List[Tuple[Position, List[Position], Set[Position]]] = [(start, [start], set())]
        visited = {(start, tuple())}
        best_path = None
        best_length = float('inf')
        
        while queue:
            current, path, removed_rocks = queue.pop(0)
            
            if len(path) >= best_length:
                continue
            
            if current == target_pos:
                best_path = path
                best_length = len(path)
                continue

            for next_pos in self._get_valid_neighbors(current):
                if result := self._try_path_through_position(next_pos, path, removed_rocks, max_rocks, visited):
                    queue.append(result)

        return best_path

    def _try_path_through_position(
        self, 
        next_pos: Position, 
        current_path: List[Position], 
        removed_rocks: Set[Position],
        max_rocks: int,
        visited: Set[Tuple[Position, Tuple[Position, ...]]]
    ) -> Optional[Tuple[Position, List[Position], Set[Position]]]:
        """Attempts to extend path through a given position."""
        if current_path is None:
            current_path = []
            
        new_removed = removed_rocks.copy() if removed_rocks is not None else set()
        
        if self._is_rock(next_pos):
            if len(new_removed) >= max_rocks:
                return None
            new_removed.add(next_pos)

        # Convert removed rocks to tuple for visited set
        state = (next_pos, tuple(sorted(new_removed)))
        if state not in visited:
            visited.add(state)
            new_path = current_path + [next_pos]  # Keep as list
            return (next_pos, new_path, new_removed)
            
        return None

    # Private Methods - Grid Navigation
    def _get_valid_neighbors(self, pos: Position) -> List[Position]:
        """Gets all valid neighboring positions."""
        neighbors = []
        for dx, dy in self.directions:
            if next_pos := self._get_next_position(pos, dx, dy):
                if self._is_valid_cell(next_pos):
                    neighbors.append(next_pos)
        return neighbors

    def _get_next_position(self, pos: Position, dx: int, dy: int) -> Optional[Position]:
        """Calculates next position and validates bounds."""
        next_pos = (pos[0] + dx, pos[1] + dy)
        if self._is_in_bounds(next_pos):
            return next_pos
        return None

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