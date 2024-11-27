from dataclasses import dataclass
import pygame
from src.utils.config import Color, WINDOW_WIDTH, SCORE_HEIGHT

@dataclass
class Stats:
    sticks_collected: int = 0
    tiles_moved: int = 0

    def _format_number(self, num: int) -> str:
        if num < 1000:
            return str(num)
        elif num < 1000000:
            return f"{num/1000:.1f}K"
        return f"{num/1000000:.1f}M"

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        sticks_text = f"Sticks: {self._format_number(self.sticks_collected)}"
        moves_text = f"Moves: {self._format_number(self.tiles_moved)}"
        
        sticks_surface = font.render(sticks_text, True, Color.WHITE.value)
        moves_surface = font.render(moves_text, True, Color.WHITE.value)
        
        padding = 20
        center_gap = 40  
        
        total_width = sticks_surface.get_width() + moves_surface.get_width() + (2 * padding) + center_gap
        
        if total_width > WINDOW_WIDTH:
            center_gap = 20  
            padding = 10     
        
        sticks_pos = (padding, SCORE_HEIGHT // 2)
        moves_pos = (WINDOW_WIDTH - moves_surface.get_width() - padding, SCORE_HEIGHT // 2)
        
        surface.blit(sticks_surface, 
                    (sticks_pos[0], sticks_pos[1] - sticks_surface.get_height() // 2))
        surface.blit(moves_surface, 
                    (moves_pos[0], moves_pos[1] - moves_surface.get_height() // 2)) 