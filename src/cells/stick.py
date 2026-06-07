# Standard library imports
from dataclasses import dataclass
# Local imports
from .cell import Cell
from src.utils.config import Color, ColorType

@dataclass
class Stick(Cell):
    """Represents a collectible stick in the game world.

    A gatherable item the player collects by **walking onto it** (see
    Player._perform_move). Collecting a stick spawns a replacement elsewhere, so
    the board always holds the same number of sticks."""

    # Core Attributes
    color: ColorType = Color.BROWN.value  # Sticks are displayed as brown squares

    # Public Methods - Interaction
    def use(self, world) -> None:
        """Sticks are collected by walking onto them, not by the use action, so
        using a faced stick does nothing. (The use action is for clearing rocks.)"""
        pass
