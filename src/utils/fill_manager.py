from dataclasses import dataclass
from typing import Set, Dict, Optional, List, Tuple
from src.utils.config import Position, GRID_SIZE
from src.cells import Cell, Rock, Stick

@dataclass
class FillManager:
    """Validates rock placements to ensure all cells remain accessible to the player.
    Uses flood fill algorithm to detect isolated regions that would trap the player."""
    
    # Public Methods
    def is_safe_rock_position(self, world, pos: Position) -> bool:
        """Determines if placing a rock at the given position would create isolated areas.
        A position is safe if all remaining cells are still reachable by the player."""
        if not world.player:
            return False

        grid = self._create_grid(world, pos)
        regions = self._find_connected_regions(grid, world.player.position, world)
        return len(regions) == 1

    # Private Methods - Grid Creation
    def _create_grid(self, world, rock_pos: Position) -> Dict[Position, bool]:
        """Creates a boolean grid representation of walkable spaces.
        Maps existing rocks and the proposed new rock position as non-walkable."""
        return {
            (x, y): not (isinstance(world.grid.get((x, y)), Rock) or (x, y) == rock_pos)
            for x in range(GRID_SIZE)
            for y in range(GRID_SIZE)
        }

    # Private Methods - Region Finding
    def _find_connected_regions(self, grid, start_pos: Position, world) -> List[Set[Position]]:
        """Discovers all connected regions in the grid starting from player position.
        Uses flood fill to map out accessible areas and identify any disconnected regions."""
        visited = set()
        regions = []
        
        # Start with player's region
        player_region = self._flood_fill_region(start_pos, visited, grid)
        if player_region:
            regions.append(player_region)
        
        # Find any other disconnected regions
        regions.extend(self._find_remaining_regions(visited, grid))
                    
        return regions

    def _find_remaining_regions(self, visited: Set[Position], grid: Dict[Position, bool]) -> List[Set[Position]]:
        """Searches for any unvisited regions in the grid.
        Identifies isolated areas that weren't reached in the initial flood fill."""
        regions = []
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                pos = (x, y)
                if pos not in visited and self._can_move_to(pos, grid):
                    region = self._flood_fill_region(pos, visited, grid)
                    if region:
                        regions.append(region)
        return regions

    def _flood_fill_region(self, pos: Position, visited: Set[Position], grid: Dict[Position, bool]) -> Set[Position]:
        """Explores and maps a connected region using recursive flood fill.
        Returns a set of all positions that can be reached from the starting position."""
        if pos in visited or not self._can_move_to(pos, grid):
            return set()
        
        region = {pos}
        visited.add(pos)
        
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            next_pos = (pos[0] + dx, pos[1] + dy)
            region.update(self._flood_fill_region(next_pos, visited, grid))
        
        return region

    # Private Methods - Utility
    def _can_move_to(self, pos: Position, grid: Dict[Position, bool]) -> bool:
        """Validates if a position is within bounds and walkable.
        Checks grid boundaries and whether the cell is blocked."""
        return (0 <= pos[0] < GRID_SIZE and 
                0 <= pos[1] < GRID_SIZE and 
                grid[pos])
    
    # Private Methods - Position Validation
    def _is_safe_rock_position(self, pos: Position, grid: Dict[Position, bool]) -> bool:
        """Determines if placing a rock at the given position would create an isolated region.
        Uses flood fill to check if all empty cells remain connected."""
        # Temporarily mark position as blocked
        grid[pos] = False
        
        # Find all connected regions from player start
        visited = set()
        self._flood_fill_region(self.player_start, visited, grid)
        
        # Check if any unreachable regions exist
        remaining = self._find_remaining_regions(visited, grid)
        
        # Reset position state
        grid[pos] = True
        return not remaining
    