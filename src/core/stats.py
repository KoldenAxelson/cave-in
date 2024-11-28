# Standard library imports
from dataclasses import dataclass
from typing import Tuple
# Third-party imports
import pygame
# Local imports
from src.utils.config import Color, WINDOW_WIDTH, SCORE_HEIGHT

@dataclass
class Stats:
    """Tracks and displays game statistics including sticks collected and tiles moved."""
    sticks_collected: int = 0  # Counter for sticks gathered by player
    tiles_moved: int = 0       # Counter for player movement

    # Public Methods
    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Coordinates the rendering of all game statistics on the screen."""
        # Create text strings with formatted numbers
        sticks_text = f"Sticks: {self._format_number(self.sticks_collected)}"
        moves_text = f"Moves: {self._format_number(self.tiles_moved)}"
        
        # Create text surfaces
        text_surfaces = self._create_text_surfaces(font, sticks_text, moves_text)
        
        # Calculate layout
        layout = self._calculate_layout(text_surfaces)
        
        # Draw text surfaces
        self._draw_text(surface, text_surfaces, layout)

    # Private Methods - Text Formatting
    def _format_number(self, num: int) -> str:
        """Formats large numbers into a more readable format with K/M suffixes.
        Examples: 999 -> "999", 1500 -> "1.5K", 1500000 -> "1.5M" """
        if num < 1000:
            return str(num)
        elif num < 1000000:
            return f"{num/1000:.1f}K"
        return f"{num/1000000:.1f}M"

    # Private Methods - Drawing Related
    def _create_text_surfaces(self, font: pygame.font.Font, sticks_text: str, moves_text: str) -> Tuple[pygame.Surface, pygame.Surface]:
        """Creates rendered text surfaces for both stick and move statistics."""
        sticks_surface = font.render(sticks_text, True, Color.WHITE.value)
        moves_surface = font.render(moves_text, True, Color.WHITE.value)
        return sticks_surface, moves_surface

    def _calculate_layout(self, text_surfaces: Tuple[pygame.Surface, pygame.Surface]) -> Tuple[int, int, int]:
        """Calculates the optimal layout parameters for displaying statistics.
        Adjusts spacing if text width exceeds window bounds."""
        sticks_surface, moves_surface = text_surfaces
        
        # Define layout parameters
        padding = 20      # Space from screen edges
        center_gap = 40   # Space between statistics
        
        # Calculate total width needed for layout
        total_width = sticks_surface.get_width() + moves_surface.get_width() + (2 * padding) + center_gap
        
        # Adjust layout if text is too wide for window
        if total_width > WINDOW_WIDTH:
            center_gap = 20  # Reduce gap between stats
            padding = 10     # Reduce edge padding
            
        return padding, center_gap, SCORE_HEIGHT // 2

    def _draw_text(self, surface: pygame.Surface, text_surfaces: Tuple[pygame.Surface, pygame.Surface], layout: Tuple[int, int, int]) -> None:
        """Renders the statistics text surfaces at their calculated positions.
        Places stick count on the left and move count on the right."""
        sticks_surface, moves_surface = text_surfaces
        padding, center_gap, vertical_center = layout
        
        # Calculate positions for text
        sticks_pos = (padding, vertical_center)  # Left-aligned
        moves_pos = (WINDOW_WIDTH - moves_surface.get_width() - padding, vertical_center)  # Right-aligned
        
        # Draw text surfaces, vertically centered
        surface.blit(sticks_surface, 
                    (sticks_pos[0], sticks_pos[1] - sticks_surface.get_height() // 2))
        surface.blit(moves_surface, 
                    (moves_pos[0], moves_pos[1] - moves_surface.get_height() // 2)) 