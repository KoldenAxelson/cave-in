from dataclasses import dataclass, field
from typing import List, Optional, Set, Tuple, Any
from src.utils.config import Position, Direction, GRID_SIZE, PathType
from src.cells.stick import Stick
from src.cells.rock import Rock
from src.cells.cell import Cell

@dataclass
class PathCalculator:
    """Calculates optimal paths through the game grid."""
    
    world: Any
    directions: List[Position] = field(default_factory=lambda: [
        Direction.UP.value,    # (0, -1)
        Direction.RIGHT.value, # (1, 0)
        Direction.DOWN.value,  # (0, 1)
        Direction.LEFT.value   # (-1, 0)
    ])

    def find_sticks(self) -> List[Position]:
        """Find all stick positions in the grid."""
        return [pos for pos, cell in self.world.grid.items() 
                if isinstance(cell, Stick)]

    def find_unrestricted_path(self) -> Optional[PathType]:
        """Find shortest path to nearest stick ignoring rocks."""
        if not self.world.player or not (sticks := self.find_sticks()):
            return None

        start = self.world.player.position
        return self._breadth_first_search(start, sticks)

    def find_path_with_max_rocks(self, max_rocks: int) -> Optional[PathType]:
        """Find path allowing up to N rock removals."""
        if not self.world.player:
            return None

        start = self.world.player.position
        queue: List[Tuple[Position, PathType, Set[Position]]] = [(start, [start], set())]
        visited = {(start, tuple())}

        while queue:
            current, path, removed_rocks = queue.pop(0)
            
            if self._is_stick(current):
                return path

            for next_pos in self._get_valid_neighbors(current):
                new_removed = removed_rocks.copy()
                
                if self._is_rock(next_pos):
                    if len(removed_rocks) >= max_rocks:
                        continue
                    new_removed.add(next_pos)

                state = (next_pos, tuple(sorted(new_removed)))
                if state not in visited:
                    visited.add(state)
                    queue.append((next_pos, path + [next_pos], new_removed))

        return None

    def count_rocks_in_path(self, path: PathType) -> int:
        """Count number of rocks in a given path."""
        return sum(1 for pos in path if self._is_rock(pos))

    def _breadth_first_search(self, start: Position, targets: List[Position]) -> Optional[PathType]:
        """Perform BFS to find shortest path to any target."""
        queue: List[Tuple[Position, PathType]] = [(start, [start])]
        visited: Set[Position] = {start}
        shortest_path: Optional[PathType] = None
        shortest_length = float('inf')

        while queue:
            current, path = queue.pop(0)
            
            if len(path) >= shortest_length:
                continue

            if current in targets and len(path) < shortest_length:
                shortest_path = path
                shortest_length = len(path)
                continue

            for next_pos in self._get_valid_neighbors(current):
                if next_pos not in visited:
                    visited.add(next_pos)
                    queue.append((next_pos, path + [next_pos]))

        return shortest_path

    def _get_valid_neighbors(self, pos: Position) -> List[Position]:
        """Get all valid neighboring positions."""
        neighbors = []
        for dx, dy in self.directions:
            if next_pos := self._get_next_position(pos, dx, dy):
                if self._is_valid_cell(next_pos):
                    neighbors.append(next_pos)
        return neighbors

    def _get_next_position(self, pos: Position, dx: int, dy: int) -> Optional[Position]:
        """Calculate next position and validate bounds."""
        next_pos = (pos[0] + dx, pos[1] + dy)
        if self._is_in_bounds(next_pos):
            return next_pos
        return None

    def _is_in_bounds(self, pos: Position) -> bool:
        """Check if position is within grid bounds."""
        return (0 <= pos[0] < GRID_SIZE and 0 <= pos[1] < GRID_SIZE)

    def _is_valid_cell(self, pos: Position) -> bool:
        """Check if position contains a valid cell type."""
        cell = self.world.grid.get(pos)
        return isinstance(cell, (Cell, Rock, Stick))

    def _is_rock(self, pos: Position) -> bool:
        """Check if position contains a rock."""
        return isinstance(self.world.grid.get(pos), Rock)

    def _is_stick(self, pos: Position) -> bool:
        """Check if position contains a stick."""
        return isinstance(self.world.grid.get(pos), Stick)