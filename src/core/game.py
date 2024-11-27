# Standard library imports
from dataclasses import dataclass
from contextlib import contextmanager
from typing import Optional
# Third-party imports
import pygame
# Local imports
from src.utils.config import WINDOW_HEIGHT, WINDOW_WIDTH, FPS
from .world import GameWorld
from .renderer import Renderer
from src.cells.player import Player
from src.utils.input_handler import should_quit, should_restart
from src.core.stats import Stats

class GameInitError(Exception):
    """Raised when game initialization fails"""
    pass

@contextmanager
def pygame_session():
    """Context manager for handling pygame initialization and cleanup.
    
    Ensures pygame is properly initialized at the start and cleaned up
    when the game exits, even if an error occurs.
    """
    pygame.init()
    try:
        yield
    finally:
        pygame.quit()

@dataclass
class Game:
    """Main game class that coordinates all game systems.
    
    Handles initialization, game loop, event processing, updates,
    and rendering. Acts as the central coordinator for all game components.
    """
    # Game state flags
    running:   bool                       = True   # Controls main game loop
    game_over: bool                       = False  # Tracks if game has ended
    
    # Core game components (initialized later)
    screen:   Optional[pygame.Surface]    = None   # Main display surface
    clock:    Optional[pygame.time.Clock] = None   # Controls game timing
    world:    Optional[GameWorld]         = None   # Game world state
    renderer: Optional[Renderer]          = None   # Handles drawing
    player:   Optional[Player]            = None   # Player instance
    stats:    Optional[Stats]             = None   # Game statistics
    
    def _initialize_game(self) -> None:
        """Initialize or reset all game components.
        
        Sets up pygame window, creates game objects, and establishes
        relationships between components.
        
        Raises:
            GameInitError: If pygame initialization fails
        """
        try:
            # Create core game components
            self.screen   = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
            self.clock    = pygame.time.Clock()
            self.world    = GameWorld()
            self.renderer = Renderer(self.screen)
            self.player   = Player()
            self.stats    = Stats()

            # Set up game window and connect components
            pygame.display.set_caption("Cave In")
            self.world.player = self.player
            self.world.stats = self.stats
            self.world.add(self.player)
        except pygame.error as e:
            raise GameInitError(f"Failed to initialize game: {e}")

    def run(self) -> None:
        """Main game loop.
        
        Handles the core game loop that processes input, updates game state,
        and renders each frame. Uses context manager for pygame lifecycle.
        """
        with pygame_session():
            self._initialize_game()
            while self.running:
                self._handle_events()
                self._update()
                self._render()

    def _handle_events(self) -> None:
        """Process all pending pygame events.
        
        Checks for quit events and delegates input handling to appropriate
        components.
        """
        for event in pygame.event.get():
            if should_quit(event):
                self.running = False

    def _update(self) -> None:
        """Update game state for the current frame.
        
        Handles:
        - World updates during normal gameplay
        - Game over condition checking
        - Game restart when requested
        """
        if not self.game_over:
            self.world.update()
            if self.world.is_board_full():
                self.game_over = True
        elif should_restart():
            self._initialize_game()
            self.game_over = False

    def _render(self) -> None:
        """Render the current game state.
        
        Delegates rendering to the renderer component and maintains
        consistent frame timing.
        """
        self.renderer.render(self.world)
        self.clock.tick(FPS)  # Control game speed