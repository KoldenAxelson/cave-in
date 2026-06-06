# Standard library imports
from dataclasses import dataclass
# Local imports
from .cell import Cell
from src.utils.config import Color, ColorType, ROCK_REMOVAL_COST

@dataclass
class Rock(Cell):
    """Represents a rock obstacle in the game world.

    A destructible obstacle that can be removed by spending sticks
    (ROCK_REMOVAL_COST of them). Inherits from Cell class and overrides
    interaction behavior."""

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
        Requires game stats to exist and enough sticks to pay the removal cost."""
        return world.stats and world.stats.sticks_collected >= ROCK_REMOVAL_COST

    def _remove_rock(self, world) -> None:
        """Executes the rock removal process.
        Spends ROCK_REMOVAL_COST sticks and replaces the rock with an empty cell."""
        world.stats.sticks_collected -= ROCK_REMOVAL_COST
        world.grid[self.position] = Cell(self.position)
