# Standard library imports
from dataclasses import dataclass
# Local imports
from .cell import Cell
from src.utils.config import Color, ColorType

@dataclass
class Rock(Cell):
    """Represents a rock obstacle in the game.
    
    Inherits from Cell class and represents a destructible obstacle
    that can be removed by spending a collected stick.
    """
    color: ColorType = Color.GRAY.value  # Rocks are displayed as gray squares

    def use(self, world) -> None:
        """Handle player interaction with the rock.
        
        When the player faces the rock and presses the action key,
        this method is called to attempt rock removal.
        
        Args:
            world: GameWorld instance containing current game state
            
        Note:
            - Only removes the rock if the player has at least one stick
            - Consumes one stick when removing the rock
            - Replaces the rock with an empty cell when removed
        """
        # Check if stats exist and player has sticks to use
        if world.stats and world.stats.sticks_collected > 0:
            world.stats.sticks_collected -= 1  # Consume one stick
            # Replace rock with empty cell
            world.grid[self.position] = Cell(self.position)
