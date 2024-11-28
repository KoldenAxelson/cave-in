# Standard library imports
from dataclasses import dataclass
from contextlib import contextmanager
from typing import Optional, Any
# Third-party imports
import pygame
# Local imports
from src.utils.config import WINDOW_HEIGHT, WINDOW_WIDTH, FPS
from .world import GameWorld
from .renderer import Renderer
from src.cells.player import Player
from src.utils.input_handler import should_restart, set_ai_controller
from src.core.stats import Stats
from src.core.menu import StartMenu
from src.ai.pathfinding.pathfinder import PathFinder

class GameInitError(Exception):
    """Raised when game initialization fails"""
    pass

@contextmanager
def pygame_session():
    """Manages the lifecycle of pygame, ensuring proper initialization and cleanup.
    Uses a context manager pattern to guarantee pygame.quit() is called even if
    exceptions occur."""
    pygame.init()
    try:
        yield
    finally:
        pygame.quit()

@dataclass
class Game:
    """Central game coordinator that manages all game systems and state.
    Handles the game lifecycle including initialization, main loop execution,
    and cleanup while coordinating between different game components."""
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
    ai_controller: Optional[Any] = None  # AI controller
    
    # Public Methods
    def run(self) -> None:
        """Executes the complete game lifecycle from menu to gameplay.
        Controls the high-level flow of the game including menu display,
        initialization, and main loop execution."""
        with pygame_session():
            if not self._handle_menu():
                return
            
            self._initialize_game()
            self._main_loop()

    # Private Methods - AI Control
    def _set_ai_controller(self, controller) -> None:
        """Assigns a new AI controller to the game instance.
        Allows dynamic switching of AI behavior during gameplay."""
        self.ai_controller = controller

    # Private methods supporting run()
    def _handle_menu(self) -> bool:
        """Manages the start menu interaction flow.
        Creates and runs the menu interface, capturing the player's
        chosen game mode."""
        menu = StartMenu(pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT)))
        self.chosen_mode = menu.run()
        return self.chosen_mode != "quit"

    def _initialize_game(self) -> None:
        """Prepares the game environment for a new session.
        Sets up all necessary game components and their relationships,
        handling any initialization errors that occur."""
        try:
            self._create_core_components()
            self._setup_window()
            self._configure_ai()
        except pygame.error as e:
            raise GameInitError(f"Failed to initialize game: {e}")

    def _main_loop(self) -> None:
        """Drives the core game loop.
        Continuously processes events, updates game state, and renders
        the game world until the game ends."""
        while self.running:
            self._handle_events()
            self.world.update()
            self._render()

    # Initialize helpers
    def _create_core_components(self) -> None:
        """Instantiates essential game objects.
        Creates the foundational components needed for the game to run
        including display, timing, world, and player elements."""
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.world = GameWorld()
        self.renderer = Renderer(self.screen)
        self.player = Player()
        self.stats = Stats()

    def _setup_window(self) -> None:
        """Configures the game window and establishes component relationships.
        Sets up the display window and connects the player and stats
        to the game world."""
        pygame.display.set_caption("Cave In")
        self.world.player = self.player
        self.world.stats = self.stats
        self.world.add(self.player)

    def _configure_ai(self) -> None:
        """Initializes the appropriate AI controller.
        Sets up AI behavior based on the selected game mode from the menu."""
        if self.chosen_mode == "pathfinder":
            self.ai_controller = PathFinder(self.world)
            set_ai_controller(self.ai_controller)
        else:
            set_ai_controller(None)

    # Game loop helpers
    def _handle_events(self) -> None:
        """Processes game events and user input.
        Manages quit events and handles game restart requests, reinitializing
        the game when needed."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

        if should_restart():
            self._initialize_game()
            self.game_over = False

    def _update(self) -> None:
        """Updates the game state.
        Manages world updates and checks for game-over conditions,
        handling restart requests when appropriate."""
        if not self.game_over:
            self.world.update()
            if self.world.is_board_full():
                self.game_over = True
        elif should_restart():
            self._initialize_game()
            self.game_over = False

    def _render(self) -> None:
        """Handles game rendering and frame timing.
        Updates the display with the current game state and maintains
        consistent frame rate."""
        self.renderer.render(self.world)
        self.clock.tick(FPS)