# Standard library imports
from dataclasses import dataclass
# Third-party imports
import pygame
# Local imports
from src.utils.config import Color, WINDOW_WIDTH, SCORE_HEIGHT

@dataclass
class Stats:
    """Tracks and displays game statistics.
    
    Manages the collection and display of game metrics including:
    - Number of sticks collected
    - Number of tiles moved
    """
    sticks_collected: int = 0  # Counter for sticks gathered by player
    tiles_moved: int = 0       # Counter for player movement

    def _format_number(self, num: int) -> str:
        """Format large numbers into a more readable format.
        
        Args:
            num: Number to format
            
        Returns:
            str: Formatted number string
            
        Examples:
            999    -> "999"
            1500   -> "1.5K"
            1500000-> "1.5M"
        """
        if num < 1000:
            return str(num)
        elif num < 1000000:
            return f"{num/1000:.1f}K"
        return f"{num/1000000:.1f}M"

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Render statistics on the game surface.
        
        Args:
            surface: Pygame surface to draw on
            font: Font to use for text rendering
            
        Note:
            Displays statistics in the score section at the top of the screen.
            Automatically adjusts layout if text becomes too wide for the window.
        """
        # Create text strings with formatted numbers
        sticks_text = f"Sticks: {self._format_number(self.sticks_collected)}"
        moves_text = f"Moves: {self._format_number(self.tiles_moved)}"
        
        # Render text to surfaces
        sticks_surface = font.render(sticks_text, True, Color.WHITE.value)
        moves_surface = font.render(moves_text, True, Color.WHITE.value)
        
        # Define layout parameters
        padding = 20      # Space from screen edges
        center_gap = 40   # Space between statistics
        
        # Calculate total width needed for layout
        total_width = sticks_surface.get_width() + moves_surface.get_width() + (2 * padding) + center_gap
        
        # Adjust layout if text is too wide for window
        if total_width > WINDOW_WIDTH:
            center_gap = 20  # Reduce gap between stats
            padding = 10     # Reduce edge padding
        
        # Calculate positions for text
        sticks_pos = (padding, SCORE_HEIGHT // 2)  # Left-aligned
        moves_pos = (WINDOW_WIDTH - moves_surface.get_width() - padding, SCORE_HEIGHT // 2)  # Right-aligned
        
        # Draw text surfaces, vertically centered
        surface.blit(sticks_surface, 
                    (sticks_pos[0], sticks_pos[1] - sticks_surface.get_height() // 2))
        surface.blit(moves_surface, 
                    (moves_pos[0], moves_pos[1] - moves_surface.get_height() // 2)) 