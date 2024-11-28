from dataclasses import dataclass
from typing import Set, Dict, Optional, List, Tuple
from src.utils.config import Position, GRID_SIZE
from src.cells import Cell, Rock, Stick

@dataclass
class FillManager:
    """Manages validation of rock placements to ensure all cells remain accessible."""
    
    def is_safe_rock_position(self, world, pos: Position) -> bool:
        """Check if placing a rock at position won't create inaccessible areas."""
        # Quick rejection: if position has 7+ rock neighbors, it's safe
        if self._count_rock_neighbors(world, pos) >= 7:
            return True
            
        # Create grid representation with the proposed rock
        grid = self._create_grid(world, pos)
        
        if not world.player:
            return False
            
        # Find all connected regions
        regions = self._find_connected_regions(grid, world.player.position)
        
        # If there's only one region, all reachable cells are connected
        if len(regions) == 1:
            return True
            
        # Check if any region contains both a stick and an empty cell
        for region in regions:
            has_stick = False
            has_empty = False
            for pos in region:
                cell = world.grid.get(pos)
                if isinstance(cell, Stick):
                    has_stick = True
                elif type(cell) == Cell:
                    has_empty = True
                if has_stick and has_empty:
                    return False
        return True

    def _count_rock_neighbors(self, world, pos: Position) -> int:
        """Count number of rock neighbors (including diagonals)."""
        x, y = pos
        count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                check_pos = (x + dx, y + dy)
                if self._is_valid_position(check_pos):
                    cell = world.grid.get(check_pos)
                    if isinstance(cell, Rock):
                        count += 1
        return count

    def _find_connected_regions(self, grid: Dict[Position, bool], start: Position) -> List[Set[Position]]:
        """Find all connected regions of walkable cells using flood fill."""
        unvisited = {pos for pos, walkable in grid.items() if walkable}
        regions = []
        
        while unvisited:
            region = set()
            to_visit = [next(iter(unvisited))]
            
            while to_visit:
                current = to_visit.pop()
                if current not in unvisited:
                    continue
                    
                unvisited.remove(current)
                region.add(current)
                x, y = current
                
                for next_pos in [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]:
                    if next_pos in unvisited and grid.get(next_pos, False):
                        to_visit.append(next_pos)
                        
            regions.append(region)
            
        return regions

    def _create_grid(self, world, rock_pos: Position) -> Dict[Position, bool]:
        """Create grid representation where True means walkable."""
        return {
            (x, y): not (isinstance(world.grid.get((x, y)), Rock) or (x, y) == rock_pos)
            for x in range(GRID_SIZE)
            for y in range(GRID_SIZE)
        }

    def _is_valid_position(self, pos: Position) -> bool:
        """Check if position is within grid bounds."""
        x, y = pos
        return 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE
    
    def clear_cache(self) -> None:
        """Clear the cache of verified positions."""
        self.verified_positions.clear() 