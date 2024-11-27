from dataclasses import dataclass, field
from .cell import Cell
from src.utils.config import Color, CELL_SIZE,GRID_SIZE, PLAYER_MOVE_COOLDOWN
from src.utils.config import Position, ColorType
from src.utils.input_handler import get_movement, use_action
import time
import pygame
from enum import Enum

class Direction(Enum):
    UP = (0, -1)
    RIGHT = (1, 0)
    DOWN = (0, 1)
    LEFT = (-1, 0)

@dataclass
class Player(Cell):
    position: Position = (GRID_SIZE // 2, GRID_SIZE // 2)
    color: ColorType = Color.RED.value
    last_move_time: float = 0.0
    move_cooldown: float = PLAYER_MOVE_COOLDOWN
    facing: Direction = Direction.DOWN

    def update(self, world) -> None:
        if time.time() - self.last_move_time < self.move_cooldown:
            return
        
        delta = get_movement()
        if any(delta):
            self._update_facing(delta)
            self._try_move(world, delta)
        
        if use_action():
            self._try_use_facing_cell(world)

    def _try_move(self, world, delta: Position) -> None:
        x, y = self.position
        dx, dy = delta
        new_pos = (
            max(0, min(GRID_SIZE - 1, x + dx)),
            max(0, min(GRID_SIZE - 1, y + dy))
        )
        
        target_cell = world.grid[new_pos]
        if new_pos != self.position and isinstance(target_cell, Cell) and type(target_cell) == Cell:
            world.grid[self.position] = Cell(self.position)
            self.position = new_pos
            world.grid[new_pos] = self
            self.last_move_time = time.time()
            
            if world.stats:
                world.stats.tiles_moved += 1

    def _update_facing(self, delta: Position) -> None:
        for direction in Direction:
            if delta == direction.value:
                self.facing = direction
                break

    def draw(self, surface: pygame.Surface, screen_pos: Position) -> None:
        super().draw(surface, screen_pos)
        self._draw_direction_indicator(surface, screen_pos)
    
    def _draw_direction_indicator(self, surface: pygame.Surface, screen_pos: Position) -> None:
        screen_x, screen_y = screen_pos
        center_x = screen_x + CELL_SIZE // 2
        center_y = screen_y + CELL_SIZE // 2
        dx, dy = self.facing.value
        indicator_x = center_x + dx * (CELL_SIZE // 4)
        indicator_y = center_y + dy * (CELL_SIZE // 4)
        pygame.draw.circle(surface, Color.WHITE.value, (indicator_x, indicator_y), 3)

    def _try_use_facing_cell(self, world) -> None:
        dx, dy = self.facing.value
        x, y = self.position
        target_pos = (x + dx, y + dy)
        
        if 0 <= target_pos[0] < GRID_SIZE and 0 <= target_pos[1] < GRID_SIZE:
            target_cell = world.grid.get(target_pos)
            if target_cell:
                target_cell.use(world)
