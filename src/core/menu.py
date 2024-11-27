from dataclasses import dataclass
import pygame
from src.utils.config import Color, WINDOW_WIDTH, WINDOW_HEIGHT

@dataclass
class MenuItem:
    """Represents a selectable menu item."""
    text: str
    action: callable
    selected: bool = False

class StartMenu:
    """Handles the game's start menu interface."""
    
    def __init__(self, screen: pygame.Surface):
        """Initialize the start menu.
        
        Args:
            screen: Pygame surface to draw on
        """
        self.screen = screen
        self.font = pygame.font.Font(None, 48)
        self.title_font = pygame.font.Font(None, 74)
        self.selected_index = 0
        self.items = [
            MenuItem("Normal Mode", self._start_normal_mode),
            # More modes can be added here later
            MenuItem("Quit", self._quit_game)
        ]
        self.running = True
        self.chosen_action = None
    
    def _start_normal_mode(self):
        """Start the game in normal (player-controlled) mode."""
        self.running = False
        self.chosen_action = "normal"
    
    def _quit_game(self):
        """Exit the game."""
        self.running = False
        self.chosen_action = "quit"
    
    def handle_input(self):
        """Process menu input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.chosen_action = "quit"
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_index = (self.selected_index - 1) % len(self.items)
                elif event.key == pygame.K_DOWN:
                    self.selected_index = (self.selected_index + 1) % len(self.items)
                elif event.key == pygame.K_RETURN:
                    self.items[self.selected_index].action()
    
    def draw(self):
        """Render the menu screen."""
        self.screen.fill(Color.BLACK.value)
        
        # Draw title
        title_surface = self.title_font.render("Cave In", True, Color.WHITE.value)
        title_rect = title_surface.get_rect(
            centerx=WINDOW_WIDTH // 2,
            centery=WINDOW_HEIGHT // 4
        )
        self.screen.blit(title_surface, title_rect)
        
        # Draw menu items
        for i, item in enumerate(self.items):
            color = Color.RED.value if i == self.selected_index else Color.WHITE.value
            text_surface = self.font.render(item.text, True, color)
            text_rect = text_surface.get_rect(
                centerx=WINDOW_WIDTH // 2,
                centery=WINDOW_HEIGHT // 2 + (i * 60)
            )
            self.screen.blit(text_surface, text_rect)
        
        pygame.display.flip()
    
    def run(self) -> str:
        """Run the menu loop.
        
        Returns:
            str: The chosen action ("normal", "quit", etc.)
        """
        while self.running:
            self.handle_input()
            self.draw()
        return self.chosen_action 