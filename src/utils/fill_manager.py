from dataclasses import dataclass
from typing import Set, Dict, Optional, List, Tuple
from src.utils.config import Position, GRID_SIZE
from src.cells import Cell, Rock, Stick

@dataclass
class FillManager:
    """Validates rock placements to ensure all cells remain accessible to the player.
    Uses flood fill algorithm to detect isolated regions that would trap the player."""
    
    # Public Methods
    def is_safe_rock_position(self, world, candidate_position: Position) -> bool:
        """Determines if placing a rock at the given position would create isolated areas.
        A position is safe if all remaining cells are still reachable by the player."""
        if not world.player:
            return False

        walkable_grid = self._create_grid(world, candidate_position)
        regions = self._find_connected_regions(walkable_grid, world.player.position, world)
        # A single region means everything stays connected; more than one means a trap
        return len(regions) == 1

    # Private Methods - Grid Creation
    def _create_grid(self, world, rock_position: Position) -> Dict[Position, bool]:
        """Creates a boolean grid representation of walkable spaces.
        Maps existing rocks and the proposed new rock position as non-walkable."""
        return {
            (column, row): not (isinstance(world.grid.get((column, row)), Rock) or (column, row) == rock_position)
            for column in range(GRID_SIZE)
            for row in range(GRID_SIZE)
        }

    # Private Methods - Region Finding
    def _find_connected_regions(self, grid, start_position: Position, world) -> List[Set[Position]]:
        """Discovers all connected regions in the grid starting from player position.
        Uses flood fill to map out accessible areas and identify any disconnected regions."""
        visited = set()
        regions = []

        # The player's own region is found first so it always appears in the list
        player_region = self._flood_fill_region(start_position, visited, grid)
        if player_region:
            regions.append(player_region)

        # Any leftover regions are areas the player can no longer reach
        regions.extend(self._find_remaining_regions(visited, grid))

        return regions

    def _find_remaining_regions(self, visited: Set[Position], grid: Dict[Position, bool]) -> List[Set[Position]]:
        """Searches for any unvisited regions in the grid.
        Identifies isolated areas that weren't reached in the initial flood fill."""
        regions = []
        for column in range(GRID_SIZE):
            for row in range(GRID_SIZE):
                position = (column, row)
                if position not in visited and self._can_move_to(position, grid):
                    region = self._flood_fill_region(position, visited, grid)
                    if region:
                        regions.append(region)
        return regions

    def _flood_fill_region(self, position: Position, visited: Set[Position], grid: Dict[Position, bool]) -> Set[Position]:
        """Explores and maps a connected region using recursive flood fill.
        Returns a set of all positions that can be reached from the starting position."""
        if position in visited or not self._can_move_to(position, grid):
            return set()

        region = {position}
        visited.add(position)

        # Recurse into the four orthogonal neighbours (no diagonals)
        for delta_x, delta_y in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            neighbour_position = (position[0] + delta_x, position[1] + delta_y)
            region.update(self._flood_fill_region(neighbour_position, visited, grid))

        return region

    # Private Methods - Utility
    def _can_move_to(self, position: Position, grid: Dict[Position, bool]) -> bool:
        """Validates if a position is within bounds and walkable.
        Checks grid boundaries and whether the cell is blocked."""
        column, row = position
        return (0 <= column < GRID_SIZE and
                0 <= row < GRID_SIZE and
                grid[position])
    