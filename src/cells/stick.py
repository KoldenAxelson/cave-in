# Standard library imports
from dataclasses import dataclass
# Local imports
from .cell import Cell
from src.utils.config import Color, Position

@dataclass
class Stick(Cell):
    """Represents a collectible stick in the game.
    
    Inherits from Cell class and represents a collectible item that
    players can gather to remove rock obstacles. When collected,
    a new stick is randomly placed elsewhere in the world.
    """
    color: Position = Color.BROWN.value  # Sticks are displayed as brown squares

    def use(self, world) -> None:
        """Handle player interaction with the stick."""
        # Update player's stick collection count first
        if world.stats:
            world.stats.sticks_collected += 1
        
        # Replace stick with empty cell at current position
        world.grid[self.position] = Cell(self.position)
        
        # Generate new stick at random position (which will place rock first if needed)
        world._place_random_stick()
