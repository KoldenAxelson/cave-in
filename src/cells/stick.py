from dataclasses import dataclass
from .cell import Cell
from src.utils.config import Color, Position

@dataclass
class Stick(Cell):
    color: Position = Color.BROWN.value

    def use(self, world) -> None:
        world.grid[self.position] = Cell(self.position)
        world._place_random_stick()
        if world.stats:
            world.stats.sticks_collected += 1
