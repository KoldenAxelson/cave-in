# Standard library imports
from dataclasses import dataclass
# Third-party imports
import pygame
# Local imports
from src.utils.config import CELL_SIZE, MARGIN, CAMERA_MODE, WINDOW_WIDTH, GAME_WINDOW_HEIGHT, GRID_SIZE
from src.utils.config import Position, ColorType, Color, CameraMode

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
        """Draw the cell on the given surface at the specified position."""
        screen_x, screen_y = screen_pos
        
        # Get cell size based on camera mode
        if CAMERA_MODE == CameraMode.FULL_MAP:
            cell_size = min(
                WINDOW_WIDTH // GRID_SIZE,
                GAME_WINDOW_HEIGHT // GRID_SIZE
            )
            margin = max(1, MARGIN * cell_size // CELL_SIZE)  # Scale margin with cell size
        else:
            cell_size = CELL_SIZE
            margin = MARGIN
        
        # Create rectangle with margins applied
        rect = pygame.Rect(
            screen_x + margin,  # Left edge + margin
            screen_y + margin,  # Top edge + margin
            cell_size - (2 * margin),  # Width accounting for both margins
            cell_size - (2 * margin)   # Height accounting for both margins
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