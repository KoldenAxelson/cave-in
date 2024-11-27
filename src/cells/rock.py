from dataclasses import dataclass
from .cell import Cell
from src.utils.config import Color, ColorType

@dataclass
class Rock(Cell):
    color: ColorType = Color.GRAY.value

    def use(self, world) -> None:
        if world.stats and world.stats.sticks_collected > 0:
            world.stats.sticks_collected -= 1
            world.grid[self.position] = Cell(self.position)
