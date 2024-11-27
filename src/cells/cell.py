from dataclasses import dataclass
import pygame
from src.utils.config import CELL_SIZE, MARGIN, Color
from src.utils.config import Position, ColorType

@dataclass
class Cell:
    position: Position
    color: ColorType = Color.D_GRAY.value

    def update(self, world) -> None:
        pass

    def draw(self, surface: pygame.Surface, screen_pos: Position) -> None:
        screen_x, screen_y = screen_pos
        rect = pygame.Rect(
            screen_x + MARGIN,
            screen_y + MARGIN,
            CELL_SIZE - (2 * MARGIN),
            CELL_SIZE - (2 * MARGIN)
        )
        pygame.draw.rect(surface, self.color, rect)

    def use(self, world) -> None:
        """Called when a player interacts with this cell"""
        pass