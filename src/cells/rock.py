# Standard library imports
from dataclasses import dataclass
# Local imports
from .cell import Cell
from src.utils.config import Color, ColorType

@dataclass
class Rock(Cell):
    """Represents a rock obstacle in the game world.
    
    A destructible obstacle that can be removed by spending a collected stick.
    Inherits from Cell class and overrides interaction behavior."""
    
    # Core Attributes
    color: ColorType = Color.GRAY.value  # Rocks are displayed as gray squares

    # Public Methods - Interaction
    def use(self, world) -> None:
        """Handles player interaction with the rock.
        Checks if removal is possible and executes if conditions are met."""
        if self._can_remove_rock(world):
            self._remove_rock(world)

    # Private Methods - Rock Removal Logic
    def _can_remove_rock(self, world) -> bool:
        """Validates if the rock can be removed.
        Requires game stats to exist and at least one stick to be collected."""
        return world.stats and world.stats.sticks_collected > 0

    def _remove_rock(self, world) -> None:
        """Executes the rock removal process.
        Consumes one stick and replaces rock with an empty cell."""
        world.stats.sticks_collected -= 1  # Consume one stick
        # Replace rock with empty cell
        world.grid[self.position] = Cell(self.position)
