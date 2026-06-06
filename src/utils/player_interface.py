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
    def try_move(self, movement_delta: Position) -> bool:
        """Attempts to move the player by the given delta.
        Updates facing direction and returns True if movement was successful."""
        if not self.world.player:
            return False
        self.world.player.update_facing(movement_delta)
        return self.world.player.try_move(self.world, movement_delta)

    def is_valid_move(self, target_position: Position) -> bool:
        """Checks if a move to the target position is valid.
        Ensures target is empty and different from current position."""
        if not self.world.player:
            return False
        target_cell = self.world.grid.get(target_position)
        # An empty floor tile is exactly type Cell; rocks/sticks are subclasses
        return (target_position != self.position and
                isinstance(target_cell, Cell) and
                type(target_cell) == Cell)
    
    # Public Methods - Actions
    def try_use_action(self) -> bool:
        """Attempts to use an action in the direction the player is facing.
        Returns True if an action was successfully performed."""
        if not self.world.player:
            return False
        
        target_position = self._get_target_position()
        return self._try_use_target(target_position)

    # Private Methods - Action Helpers
    def _get_target_position(self) -> Position:
        """Calculates the grid position directly in front of the player.
        Uses player position and facing direction to determine target."""
        player_x, player_y = self.position
        delta_x, delta_y = self.facing.value
        return (player_x + delta_x, player_y + delta_y)

    def _try_use_target(self, target_position: Position) -> bool:
        """Attempts to interact with a cell at the target position.
        Returns True if the cell had a usable action."""
        target_cell = self.world.grid.get(target_position)
        if hasattr(target_cell, 'use'):
            target_cell.use(self.world)
            return True
        return False 