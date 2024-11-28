from dataclasses import dataclass
from src.utils.config import Position, Direction
from src.cells.cell import Cell
from typing import Optional

@dataclass
class PlayerInterface:
    """Interface for controlling and querying player state and actions.
    Provides a clean API for player movement, actions, and state queries."""
    
    def __init__(self, world):
        """Initializes the interface with a reference to the game world."""
        self.world = world
    
    # Public Properties
    @property
    def position(self) -> Optional[Position]:
        """Retrieves the current player position in the world.
        Returns None if no player exists."""
        return self.world.player.position if self.world.player else None
    
    @property
    def facing(self) -> Optional[Direction]:
        """Retrieves the current direction the player is facing.
        Returns None if no player exists."""
        return self.world.player.facing if self.world.player else None
    
    # Public Methods - Movement
    def try_move(self, delta: Position) -> bool:
        """Attempts to move the player by the given delta.
        Updates facing direction and returns True if movement was successful."""
        if not self.world.player:
            return False
        self.world.player.update_facing(delta)
        return self.world.player.try_move(self.world, delta)
    
    def is_valid_move(self, target_pos: Position) -> bool:
        """Checks if a move to the target position is valid.
        Ensures target is empty and different from current position."""
        if not self.world.player:
            return False
        target_cell = self.world.grid.get(target_pos)
        return (target_pos != self.position and 
                isinstance(target_cell, Cell) and 
                type(target_cell) == Cell)
    
    # Public Methods - Actions
    def try_use_action(self) -> bool:
        """Attempts to use an action in the direction the player is facing.
        Returns True if an action was successfully performed."""
        if not self.world.player:
            return False
        
        target_pos = self._get_target_position()
        return self._try_use_target(target_pos)

    # Private Methods - Action Helpers
    def _get_target_position(self) -> Position:
        """Calculates the grid position directly in front of the player.
        Uses player position and facing direction to determine target."""
        px, py = self.position
        dx, dy = self.facing.value
        return (px + dx, py + dy)

    def _try_use_target(self, target_pos: Position) -> bool:
        """Attempts to interact with a cell at the target position.
        Returns True if the cell had a usable action."""
        target_cell = self.world.grid.get(target_pos)
        if hasattr(target_cell, 'use'):
            target_cell.use(self.world)
            return True
        return False
    
    def is_valid_move(self, target_pos: Position) -> bool:
        """Checks if a move to the target position is valid.
        Ensures target is empty and different from current position."""
        if not self.world.player:
            return False
        target_cell = self.world.grid.get(target_pos)
        return (target_pos != self.position and 
                isinstance(target_cell, Cell) and 
                type(target_cell) == Cell) 