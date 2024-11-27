from dataclasses import dataclass, field
import pygame
from .world import GameWorld
from .stats import Stats
from src.utils.config import Color, WINDOW_WIDTH, WINDOW_HEIGHT, GRID_SIZE, CELL_SIZE, MARGIN, VIEW_RADIUS, SCORE_HEIGHT, GAME_WINDOW_HEIGHT
from src.utils.config import Position
from src.cells.cell import Cell
from typing import Optional, Tuple

@dataclass
class Renderer:
    screen: pygame.Surface
    font: pygame.font.Font = field(init=False)
    
    def __post_init__(self) -> None:
        self.font = pygame.font.Font(None, 36)

    def _draw_cell(self, surface: pygame.Surface, screen_pos: Position, cell: Optional[Cell]) -> None:
        if cell:
            cell.draw(surface, screen_pos)
        else:
            self._draw_empty_cell(surface, screen_pos)

    def _draw_empty_cell(self, surface: pygame.Surface, screen_pos: Position) -> None:
        screen_x, screen_y = screen_pos
        rect = pygame.Rect(
            screen_x + MARGIN,
            screen_y + MARGIN,
            CELL_SIZE - (2 * MARGIN),
            CELL_SIZE - (2 * MARGIN)
        )
        pygame.draw.rect(surface, Color.BLACK.value, rect)

    def _get_screen_position(self, world_pos: Position, view_start: Position) -> Position:
        x, y = world_pos
        view_x, view_y = view_start
        return ((x - view_x) * CELL_SIZE, (y - view_y) * CELL_SIZE)

    def _get_view_bounds(self, player_pos: Position) -> Tuple[int, int, int, int]:
        px, py = player_pos
        view_start_x = px - VIEW_RADIUS
        view_start_y = py - VIEW_RADIUS
        view_end_x = view_start_x + VIEW_RADIUS * 2 + 1
        view_end_y = view_start_y + VIEW_RADIUS * 2 + 1
        return view_start_x, view_start_y, view_end_x, view_end_y

    def _draw_score_section(self, surface: pygame.Surface, stats: Stats) -> None:
        score_rect = pygame.Rect(0, 0, WINDOW_WIDTH, SCORE_HEIGHT)
        pygame.draw.rect(surface, Color.D_GRAY.value, score_rect)
        
        pygame.draw.line(
            surface,
            Color.GRAY.value,
            (0, SCORE_HEIGHT - 1),
            (WINDOW_WIDTH, SCORE_HEIGHT - 1),
            2
        )
        
        stats.draw(surface, self.font)

    def _draw_world(self, surface: pygame.Surface, world: GameWorld) -> None:
        view_start_x, view_start_y, view_end_x, view_end_y = self._get_view_bounds(world.player.position)
        
        # Offset the game view to account for score section
        game_surface = pygame.Surface((WINDOW_WIDTH, GAME_WINDOW_HEIGHT))
        game_surface.fill(Color.BLACK.value)
        
        for y in range(view_start_y, view_end_y):
            for x in range(view_start_x, view_end_x):
                screen_pos = self._get_screen_position((x, y), (view_start_x, view_start_y))
                
                if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
                    cell = world.grid.get((x, y))
                    self._draw_cell(game_surface, screen_pos, cell)
                else:
                    self._draw_cell(game_surface, screen_pos, None)
        
        # Blit game surface below score section
        surface.blit(game_surface, (0, SCORE_HEIGHT))

    def _draw_game_over(self, surface: pygame.Surface, moves: int) -> None:
        # Create semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill(Color.BLACK.value)
        overlay.set_alpha(128)
        surface.blit(overlay, (0, 0))

        # Draw game over text
        game_over_text = f"Cave In! Moves: {moves}"
        restart_text = "Press ESC to restart"
        
        game_over_surface = self.font.render(game_over_text, True, Color.WHITE.value)
        restart_surface = self.font.render(restart_text, True, Color.WHITE.value)
        
        # Center both texts
        game_over_rect = game_over_surface.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 20)
        )
        restart_rect = restart_surface.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20)
        )
        
        surface.blit(game_over_surface, game_over_rect)
        surface.blit(restart_surface, restart_rect)

    def render(self, world: GameWorld) -> None:
        # Create drawing surface
        surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        surface.fill(Color.BLACK.value)

        # Draw game elements
        if world.stats:
            self._draw_score_section(surface, world.stats)
        self._draw_world(surface, world)

        # Draw game over if needed
        if world.is_board_full():
            self._draw_game_over(surface, world.stats.tiles_moved if world.stats else 0)

        # Update screen
        self.screen.blit(surface, (0, 0))
        pygame.display.flip()