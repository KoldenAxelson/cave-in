# Standard library imports
from dataclasses import dataclass
# Third-party imports
import pygame
# Local imports
from src.utils.config import CELL_SIZE, MARGIN, Color
from src.utils.config import Position, ColorType

@dataclass
class Cell:
    """Base class for all grid cells in the game.
    
    This class serves as the foundation for all cell types (Player, Rock, Stick).
    It provides basic functionality for position tracking, drawing, and interaction.
    """
    position: Position  # Tuple of (x, y) coordinates in the game grid
    color: ColorType = Color.D_GRAY.value  # RGB color tuple, defaults to dark gray

    def update(self, world) -> None:
        """Update the cell's state for the current frame.
        
        Args:
            world: GameWorld instance containing the current game state
            
        Note:
            Base implementation does nothing. Subclasses should override
            this method if they need frame-by-frame updates.
        """
        pass

    def draw(self, surface: pygame.Surface, screen_pos: Position) -> None:
        """Draw the cell on the given surface at the specified position.
        
        Args:
            surface: Pygame surface to draw on
            screen_pos: Tuple of (x, y) coordinates for where to draw on screen
            
        Note:
            Draws a rectangle with the cell's color and applies margins
            for visual separation between cells.
        """
        screen_x, screen_y = screen_pos
        # Create rectangle with margins applied
        rect = pygame.Rect(
            screen_x + MARGIN,  # Left edge + margin
            screen_y + MARGIN,  # Top edge + margin
            CELL_SIZE - (2 * MARGIN),  # Width accounting for both margins
            CELL_SIZE - (2 * MARGIN)   # Height accounting for both margins
        )
        # Draw the rectangle with the cell's color
        pygame.draw.rect(surface, self.color, rect)

    def use(self, world) -> None:
        """Handle interaction when the player uses/activates this cell.
        
        Args:
            world: GameWorld instance containing the current game state
            
        Note:
            Base implementation does nothing. Subclasses should override
            this method to implement their specific interaction behavior
            (e.g., Stick collection, Rock removal).
        """
        pass