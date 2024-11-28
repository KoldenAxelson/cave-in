# Standard library imports
from dataclasses import dataclass
# Local imports
from .cell import Cell
from src.utils.config import Color, Position

@dataclass
class Stick(Cell):
    """Represents a collectible stick in the game world.
    
    A gatherable item that players can collect to remove rock obstacles.
    When collected, a new stick is randomly placed elsewhere in the world."""
    
    # Core Attributes
    color: Position = Color.BROWN.value  # Sticks are displayed as brown squares

    # Public Methods - Interaction
    def use(self, world) -> None:
        """Handles player interaction with the stick.
        Orchestrates collection, removal, and replacement of the stick."""
        self._collect_stick(world)
        self._replace_with_empty_cell(world)
        self._generate_new_stick(world)

    # Private Methods - Collection Process
    def _collect_stick(self, world) -> None:
        """Increments the player's stick collection counter.
        Only updates if game stats tracking is enabled."""
        if world.stats:
            world.stats.sticks_collected += 1

    def _replace_with_empty_cell(self, world) -> None:
        """Replaces this stick with an empty cell.
        Maintains grid consistency after stick collection."""
        world.grid[self.position] = Cell(self.position)

    def _generate_new_stick(self, world) -> None:
        """Triggers generation of a new stick elsewhere in the world.
        Ensures consistent stick count in the game."""
        world._place_random_stick()
