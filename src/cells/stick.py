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
        """Handle player interaction with the stick.
        
        When the player faces the stick and presses the action key,
        this method is called to collect the stick.
        
        Args:
            world: GameWorld instance containing current game state
            
        Effects:
            1. Replaces this stick with an empty cell
            2. Triggers placement of a new stick somewhere in the world
            3. Increments the player's stick collection counter
        """
        # Replace stick with empty cell at current position
        world.grid[self.position] = Cell(self.position)
        
        # Generate new stick at random position
        world._place_random_stick()
        
        # Update player's stick collection count
        if world.stats:
            world.stats.sticks_collected += 1
