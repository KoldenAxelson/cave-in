from dataclasses import dataclass
import pygame
from src.utils.config import WINDOW_HEIGHT, WINDOW_WIDTH, FPS
from .world import GameWorld
from .renderer import Renderer
from src.cells.player import Player
from src.utils.input_handler import should_quit, should_restart
from contextlib import contextmanager
from typing import Optional
from src.core.stats import Stats

class GameInitError(Exception):
    """Raised when game initialization fails"""
    pass

@contextmanager
def pygame_session():
    pygame.init()
    try:
        yield
    finally:
        pygame.quit()

@dataclass
class Game:
    running:   bool                       = True
    game_over: bool                       = False
    screen:   Optional[pygame.Surface]    = None
    clock:    Optional[pygame.time.Clock] = None
    world:    Optional[GameWorld]         = None
    renderer: Optional[Renderer]          = None
    player:   Optional[Player]            = None
    stats:    Optional[Stats]             = None
    
    def _initialize_game(self) -> None:
        try:
            self.screen   = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
            self.clock    = pygame.time.Clock()
            self.world    = GameWorld()
            self.renderer = Renderer(self.screen)
            self.player   = Player()
            self.stats    = Stats()

            pygame.display.set_caption("Cave In")
            self.world.player = self.player
            self.world.stats = self.stats
            self.world.add(self.player)
        except pygame.error as e:
            raise GameInitError(f"Failed to initialize game: {e}")

    def run(self) -> None:
        with pygame_session():
            self._initialize_game()
            while self.running:
                self._handle_events()
                self._update()
                self._render()

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if should_quit(event):
                self.running = False

    def _update(self) -> None:
        if not self.game_over:
            self.world.update()
            if self.world.is_board_full():
                self.game_over = True
        elif should_restart():
            self._initialize_game()
            self.game_over = False

    def _render(self) -> None:
        self.renderer.render(self.world)
        self.clock.tick(FPS)