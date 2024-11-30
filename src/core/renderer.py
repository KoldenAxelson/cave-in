from dataclasses import dataclass, field
import pygame
from .world import GameWorld
from .stats import Stats
from src.utils.config import Color, WINDOW_WIDTH, WINDOW_HEIGHT, GRID_SIZE, CELL_SIZE, MARGIN, VIEW_RADIUS, SCORE_HEIGHT, GAME_WINDOW_HEIGHT, CAMERA_MODE, CameraMode
from src.utils.config import Position
from src.cells import Player,Cell
from typing import Optional, Tuple

@dataclass
class Renderer:
    """Handles all game rendering operations including world, UI, and special effects."""
    screen: pygame.Surface
    font: pygame.font.Font = field(init=False)
    
    def __post_init__(self) -> None:
        """Initializes the font system after dataclass creation."""
        self.font = pygame.font.Font(None, 26)

    # Public Methods
    def render(self, world: GameWorld) -> None:
        """Coordinates the rendering of all game elements including world, UI, and overlays."""
        surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        surface.fill(Color.BLACK.value)

        if world.stats:
            self._draw_score_section(surface, world.stats)
        self._draw_world(surface, world)

        if world.is_board_full():
            self._draw_game_over(surface, world.stats.tiles_moved if world.stats else 0)

        self.screen.blit(surface, (0, 0))
        pygame.display.flip()

    # World rendering related methods
    def _draw_world(self, surface: pygame.Surface, world: GameWorld) -> None:
        """Manages the rendering of the game world and all its visible cells."""
        view_bounds = self._get_view_bounds(world.player.position)
        game_surface = self._create_game_surface()
        self._draw_visible_cells(game_surface, world, view_bounds)
        surface.blit(game_surface, (0, SCORE_HEIGHT))

    def _create_game_surface(self) -> pygame.Surface:
        """Creates a fresh surface for rendering the game world."""
        game_surface = pygame.Surface((WINDOW_WIDTH, GAME_WINDOW_HEIGHT))
        game_surface.fill(Color.BLACK.value)
        return game_surface

    def _draw_visible_cells(self, game_surface: pygame.Surface, world: GameWorld, view_bounds: Tuple[int, int, int, int]) -> None:
        """Renders all cells within the current view boundaries."""
        view_start_x, view_start_y, view_end_x, view_end_y = view_bounds
        
        for y in range(view_start_y, view_end_y):
            for x in range(view_start_x, view_end_x):
                screen_pos = self._get_screen_position((x, y), (view_start_x, view_start_y))
                
                if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
                    cell = world.grid.get((x, y))
                    self._draw_cell(game_surface, screen_pos, cell)
                else:
                    self._draw_cell(game_surface, screen_pos, None)

    def _draw_cell(self, surface: pygame.Surface, screen_pos: Position, cell: Optional[Cell]) -> None:
        """Renders a single cell or empty space at the specified position."""
        cell_size, margin = self._get_cell_size()
        
        if cell:
            cell.draw(surface, screen_pos, cell_size, margin)
        else:
            rect = pygame.Rect(
                screen_pos[0] + margin,
                screen_pos[1] + margin,
                cell_size - (2 * margin),
                cell_size - (2 * margin)
            )
            pygame.draw.rect(surface, Color.BLACK.value, rect)

    def _draw_empty_cell(self, surface: pygame.Surface, screen_pos: Position) -> None:
        """Renders a black rectangle representing an empty cell."""
        if CAMERA_MODE == CameraMode.FULL_MAP:
            cell_size = min(
                WINDOW_WIDTH // GRID_SIZE,
                GAME_WINDOW_HEIGHT // GRID_SIZE
            )
            margin = max(1, MARGIN * cell_size // CELL_SIZE)
        else:
            cell_size = CELL_SIZE
            margin = MARGIN
            
        rect = pygame.Rect(
            screen_pos[0] + margin,
            screen_pos[1] + margin,
            cell_size - (2 * margin),
            cell_size - (2 * margin)
        )
        pygame.draw.rect(surface, Color.BLACK.value, rect)

    # UI rendering related methods
    def _draw_score_section(self, surface: pygame.Surface, stats: Stats) -> None:
        """Renders the score panel including background, separator line, and statistics."""
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

    def _draw_game_over(self, surface: pygame.Surface, moves: int) -> None:
        """Manages the rendering of the game over screen including overlay and text."""
        self._draw_overlay(surface)
        self._draw_game_over_text(surface, moves)

    def _draw_overlay(self, surface: pygame.Surface) -> None:
        """Creates a semi-transparent black overlay for the game over screen."""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill(Color.BLACK.value)
        overlay.set_alpha(128)
        surface.blit(overlay, (0, 0))

    def _draw_game_over_text(self, surface: pygame.Surface, moves: int) -> None:
        """Renders the game over message and restart instructions."""
        game_over_text = f"Cave In! Moves: {moves}"
        restart_text = "Press ESC to restart"
        
        game_over_surface = self.font.render(game_over_text, True, Color.WHITE.value)
        restart_surface = self.font.render(restart_text, True, Color.WHITE.value)
        
        game_over_rect = game_over_surface.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 20)
        )
        restart_rect = restart_surface.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20)
        )
        
        surface.blit(game_over_surface, game_over_rect)
        surface.blit(restart_surface, restart_rect)

    # Utility methods
    def _get_screen_position(self, world_pos: Position, view_start: Position) -> Position:
        """Translates world coordinates to screen coordinates based on current view."""
        x, y = world_pos
        view_x, view_y = view_start
        
        if CAMERA_MODE == CameraMode.FULL_MAP:
            cell_size = min(
                WINDOW_WIDTH // GRID_SIZE,
                GAME_WINDOW_HEIGHT // GRID_SIZE
            )
            offset_x = (WINDOW_WIDTH - (GRID_SIZE * cell_size)) // 2
            offset_y = (GAME_WINDOW_HEIGHT - (GRID_SIZE * cell_size)) // 2
            return (x * cell_size + offset_x, y * cell_size + offset_y)
            
        return ((x - view_x) * CELL_SIZE, (y - view_y) * CELL_SIZE)

    def _get_view_bounds(self, player_pos: Position) -> Tuple[int, int, int, int]:
        """Calculates the visible area boundaries based on player position and camera mode."""
        if CAMERA_MODE == CameraMode.FULL_MAP:
            return 0, 0, GRID_SIZE, GRID_SIZE
            
        px, py = player_pos
        view_start_x = px - VIEW_RADIUS
        view_start_y = py - VIEW_RADIUS
        view_end_x = view_start_x + VIEW_RADIUS * 2 + 1
        view_end_y = view_start_y + VIEW_RADIUS * 2 + 1
        return view_start_x, view_start_y, view_end_x, view_end_y

    def _get_cell_size(self) -> Tuple[int, int]:
        """Determines the appropriate cell size and margin based on current camera mode."""
        if CAMERA_MODE == CameraMode.FULL_MAP:
            cell_size = min(
                WINDOW_WIDTH // GRID_SIZE,
                GAME_WINDOW_HEIGHT // GRID_SIZE
            )
            margin = max(1, MARGIN * cell_size // CELL_SIZE)
        else:
            cell_size = CELL_SIZE
            margin = MARGIN
        return cell_size, margin