from dataclasses import dataclass
from src.utils.config import Position, Direction
from src.cells.cell import Cell
from typing import Optional

@dataclass
class PlayerInterface:
    """Interface for controlling and querying player state."""
    
    def __init__(self, world):
        self.world = world
    
    @property
    def position(self) -> Optional[Position]:
        """Get current player position."""
        return self.world.player.position if self.world.player else None
    
    @property
    def facing(self) -> Optional[Direction]:
        """Get current player facing direction."""
        return self.world.player.facing if self.world.player else None
    
    def try_move(self, delta: Position) -> bool:
        """Attempt to move player in given direction."""
        if not self.world.player:
            return False
        self.world.player.update_facing(delta)
        return self.world.player.try_move(self.world, delta)
    
    def try_use_action(self) -> bool:
        """Attempt to use action in facing direction."""
        if not self.world.player:
            return False
        
        px, py = self.position
        dx, dy = self.facing.value
        target_pos = (px + dx, py + dy)
        
        target_cell = self.world.grid.get(target_pos)
        if hasattr(target_cell, 'use'):
            target_cell.use(self.world)
            return True
        
        return False
    
    def is_valid_move(self, target_pos: Position) -> bool:
        """Check if moving to target position is valid."""
        if not self.world.player:
            return False
        target_cell = self.world.grid.get(target_pos)
        return (target_pos != self.position and 
                isinstance(target_cell, Cell) and 
                type(target_cell) == Cell) 