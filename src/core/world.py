from dataclasses import dataclass, field
from typing import Dict, Optional
from src.cells.cell import Cell
from src.cells.stick import Stick
from src.cells.rock import Rock
from itertools import product
from src.utils.config import GRID_SIZE, Position
from src.core.stats import Stats
import random

@dataclass
class GameWorld:
    grid: Dict[Position, Cell] = field(default_factory=dict)
    player: Optional[Cell] = None
    stats: Optional[Stats] = None

    def __post_init__(self) -> None:
        self.grid.update({
            pos: Cell(pos) for pos in product(range(GRID_SIZE), range(GRID_SIZE))
        })

        self._place_random_stick()

    def _place_random_rock(self) -> None:
        empty_positions = [
            pos for pos, cell in self.grid.items()
            if type(cell) == Cell
        ]
        if empty_positions:
            rock_pos = random.choice(empty_positions)
            self.grid[rock_pos] = Rock(rock_pos)

    def _place_random_stick(self) -> None:
        empty_positions = [
            pos for pos, cell in self.grid.items()
            if type(cell) == Cell
        ]
        if empty_positions:
            stick_pos = random.choice(empty_positions)
            self.grid[stick_pos] = Stick(stick_pos)
            self._place_random_rock()

    def add(self, cell: Cell) -> None:
        self.grid[cell.position] = cell

    def update(self) -> None:
        for cell in self.grid.values():
            cell.update(self)

    def is_board_full(self) -> bool:
        empty_positions = [
            pos for pos, cell in self.grid.items()
            if type(cell) == Cell
        ]
        return len(empty_positions) == 0