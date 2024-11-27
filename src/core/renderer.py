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
    """Handles all game rendering operations."""
    screen: pygame.Surface  # Main pygame display surface
    font: pygame.font.Font = field(init=False)  # Font for rendering text
    
    def __post_init__(self) -> None:
        """Initialize the font after dataclass initialization."""
        self.font = pygame.font.Font(None, 36)

    def _draw_cell(self, surface: pygame.Surface, screen_pos: Position, cell: Optional[Cell]) -> None:
        """Draw a cell or empty space at the specified screen position.
        
        Args:
            surface: Surface to draw on
            screen_pos: Position on screen to draw
            cell: Cell object to draw, or None for empty space
        """
        if cell:
            cell.draw(surface, screen_pos)
        else:
            self._draw_empty_cell(surface, screen_pos)

    def _draw_empty_cell(self, surface: pygame.Surface, screen_pos: Position) -> None:
        """Draw an empty cell (black rectangle) at the specified position.
        
        Args:
            surface: Surface to draw on
            screen_pos: Position on screen to draw
        """
        screen_x, screen_y = screen_pos
        rect = pygame.Rect(
            screen_x + MARGIN,
            screen_y + MARGIN,
            CELL_SIZE - (2 * MARGIN),
            CELL_SIZE - (2 * MARGIN)
        )
        pygame.draw.rect(surface, Color.BLACK.value, rect)

    def _get_screen_position(self, world_pos: Position, view_start: Position) -> Position:
        """Convert world coordinates to screen coordinates.
        
        Args:
            world_pos: Position in game world
            view_start: Starting position of current view
        
        Returns:
            Tuple of screen x,y coordinates
        """
        x, y = world_pos
        view_x, view_y = view_start
        return ((x - view_x) * CELL_SIZE, (y - view_y) * CELL_SIZE)

    def _get_view_bounds(self, player_pos: Position) -> Tuple[int, int, int, int]:
        """Calculate the visible area bounds around the player.
        
        Args:
            player_pos: Current player position
        
        Returns:
            Tuple of (start_x, start_y, end_x, end_y) for visible area
        """
        px, py = player_pos
        view_start_x = px - VIEW_RADIUS
        view_start_y = py - VIEW_RADIUS
        view_end_x = view_start_x + VIEW_RADIUS * 2 + 1
        view_end_y = view_start_y + VIEW_RADIUS * 2 + 1
        return view_start_x, view_start_y, view_end_x, view_end_y

    def _draw_score_section(self, surface: pygame.Surface, stats: Stats) -> None:
        """Draw the score section at the top of the screen.
        
        Args:
            surface: Surface to draw on
            stats: Game statistics to display
        """
        # Draw score background
        score_rect = pygame.Rect(0, 0, WINDOW_WIDTH, SCORE_HEIGHT)
        pygame.draw.rect(surface, Color.D_GRAY.value, score_rect)
        
        # Draw separator line
        pygame.draw.line(
            surface,
            Color.GRAY.value,
            (0, SCORE_HEIGHT - 1),
            (WINDOW_WIDTH, SCORE_HEIGHT - 1),
            2
        )
        
        # Draw stats
        stats.draw(surface, self.font)

    def _draw_world(self, surface: pygame.Surface, world: GameWorld) -> None:
        """Draw the game world within the visible area around the player.
        
        Args:
            surface: Surface to draw on
            world: GameWorld object containing game state
        """
        # Calculate visible area
        view_start_x, view_start_y, view_end_x, view_end_y = self._get_view_bounds(world.player.position)
        
        # Create separate surface for game view (below score section)
        game_surface = pygame.Surface((WINDOW_WIDTH, GAME_WINDOW_HEIGHT))
        game_surface.fill(Color.BLACK.value)
        
        # Draw visible cells
        for y in range(view_start_y, view_end_y):
            for x in range(view_start_x, view_end_x):
                screen_pos = self._get_screen_position((x, y), (view_start_x, view_start_y))
                
                # Only draw cells within grid bounds
                if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
                    cell = world.grid.get((x, y))
                    self._draw_cell(game_surface, screen_pos, cell)
                else:
                    self._draw_cell(game_surface, screen_pos, None)
        
        # Add game view below score section
        surface.blit(game_surface, (0, SCORE_HEIGHT))

    def _draw_game_over(self, surface: pygame.Surface, moves: int) -> None:
        """Draw the game over overlay with final score and restart instructions.
        
        Args:
            surface: Surface to draw on
            moves: Number of moves made in the game
        """
        # Create semi-transparent dark overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill(Color.BLACK.value)
        overlay.set_alpha(128)
        surface.blit(overlay, (0, 0))

        # Prepare game over text
        game_over_text = f"Cave In! Moves: {moves}"
        restart_text = "Press ESC to restart"
        
        game_over_surface = self.font.render(game_over_text, True, Color.WHITE.value)
        restart_surface = self.font.render(restart_text, True, Color.WHITE.value)
        
        # Center text on screen
        game_over_rect = game_over_surface.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 20)
        )
        restart_rect = restart_surface.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20)
        )
        
        # Draw text
        surface.blit(game_over_surface, game_over_rect)
        surface.blit(restart_surface, restart_rect)

    def render(self, world: GameWorld) -> None:
        """Main render function that draws the complete game state.
        
        Args:
            world: GameWorld object containing current game state
        """
        # Create main drawing surface
        surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        surface.fill(Color.BLACK.value)

        # Draw main game elements
        if world.stats:
            self._draw_score_section(surface, world.stats)
        self._draw_world(surface, world)

        # Draw game over overlay if game is finished
        if world.is_board_full():
            self._draw_game_over(surface, world.stats.tiles_moved if world.stats else 0)

        # Update display
        self.screen.blit(surface, (0, 0))
        pygame.display.flip()