from dataclasses import dataclass
from typing import Set, Dict, Optional, List, Tuple
from src.utils.config import Position, GRID_SIZE
from src.cells import Cell, Rock, Stick

@dataclass
class FillManager:
    """Manages validation of rock placements to ensure all cells remain accessible."""
    
    def is_safe_rock_position(self, world, pos: Position) -> bool:
        """Check if placing a rock at position won't create inaccessible areas."""
        if not world.player:
            return False

        # Create grid representation with the proposed rock
        grid = self._create_grid(world, pos)
        
        # Find all connected regions from player's position
        regions = self._find_connected_regions(grid, world.player.position, world)
        
        # If there's only one region, all reachable cells are connected
        return len(regions) == 1

    def _find_connected_regions(self, grid, start_pos: Position, world) -> List[Set[Position]]:
        """Find all connected regions accessible from the start position."""
        def can_move_to(pos: Position) -> bool:
            # Check grid bounds
            if not (0 <= pos[0] < GRID_SIZE and 0 <= pos[1] < GRID_SIZE):
                return False
            # Consider both existing rocks and the proposed rock position
            return grid[pos]  # grid from _create_grid has True for walkable positions

        def flood_fill(pos: Position, visited: Set[Position]) -> Set[Position]:
            if pos in visited or not can_move_to(pos):
                return set()
            
            region = {pos}
            visited.add(pos)
            
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                next_pos = (pos[0] + dx, pos[1] + dy)
                region.update(flood_fill(next_pos, visited))
            
            return region

        visited = set()
        regions = []
        
        # Start with player's region
        player_region = flood_fill(start_pos, visited)
        if player_region:
            regions.append(player_region)
        
        # Find any other disconnected regions
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                pos = (x, y)
                if pos not in visited and can_move_to(pos):
                    region = flood_fill(pos, visited)
                    if region:
                        regions.append(region)
                    
        return regions

    def _create_grid(self, world, rock_pos: Position) -> Dict[Position, bool]:
        """Create grid representation where True means walkable."""
        return {
            (x, y): not (isinstance(world.grid.get((x, y)), Rock) or (x, y) == rock_pos)
            for x in range(GRID_SIZE)
            for y in range(GRID_SIZE)
        }
    