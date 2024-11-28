# Standard library imports
from dataclasses import dataclass
# Third-party imports
import pygame
# Local imports
from src.utils.config import CELL_SIZE, MARGIN, CAMERA_MODE, WINDOW_WIDTH, GAME_WINDOW_HEIGHT, GRID_SIZE
from src.utils.config import Position, ColorType, Color, CameraMode

@dataclass
class Cell:
    """Base class for all grid cells in the game world.
    Provides core functionality for position tracking, drawing, and interaction."""
    
    # Core Attributes
    position: Position  # (x, y) coordinates in the game grid
    color: ColorType = Color.D_GRAY.value  # RGB color tuple for cell rendering

    # Public Methods - Game Logic
    def update(self, world) -> None:
        """Updates the cell's state for the current frame.
        Base implementation does nothing - subclasses override for specific behavior."""
        pass

    def use(self, world) -> None:
        """Handles interaction when the player activates this cell.
        Base implementation does nothing - subclasses override for specific behavior."""
        pass

    # Public Methods - Rendering
    def draw(self, surface: pygame.Surface, screen_pos: Position, cell_size: int, margin: int) -> None:
        """Renders the cell on the game surface at the specified screen position.
        Handles margin calculations and delegates actual drawing."""
        rect = self._create_cell_rect(screen_pos, cell_size, margin)
        self._draw_cell_rect(surface, rect)

    # Private Methods - Rendering Helpers
    def _create_cell_rect(self, screen_pos: Position, cell_size: int, margin: int) -> pygame.Rect:
        """Creates a pygame Rect for the cell with proper margins.
        Calculates dimensions to ensure consistent spacing between cells."""
        screen_x, screen_y = screen_pos
        return pygame.Rect(
            screen_x + margin,
            screen_y + margin,
            cell_size - (2 * margin),
            cell_size - (2 * margin)
        )

    def _draw_cell_rect(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Renders the cell's rectangle using its color attribute.
        Handles the actual pygame drawing operation."""
        pygame.draw.rect(surface, self.color, rect)