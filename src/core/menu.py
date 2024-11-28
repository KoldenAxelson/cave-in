from dataclasses import dataclass
import pygame
from src.utils.config import Color, WINDOW_WIDTH, WINDOW_HEIGHT

@dataclass
class MenuItem:
    """A selectable menu option with associated text and action."""
    text: str
    action: callable
    selected: bool = False

class StartMenu:
    """Manages the game's main menu interface and user interaction."""
    
    def __init__(self, screen: pygame.Surface):
        """Initializes the menu with default options and visual settings."""
        self.screen = screen
        self.font = pygame.font.Font(None, 48)
        self.title_font = pygame.font.Font(None, 74)
        self.selected_index = 0
        self.items = [
            MenuItem("Normal Mode", self._start_normal_mode),
            MenuItem("Path Finder", self._start_pathfinder_mode),
            MenuItem("Quit", self._quit_game)
        ]
        self.running = True
        self.chosen_action = None
    
    # Public Methods
    def run(self) -> str:
        """Executes the menu loop until an option is selected."""
        while self.running:
            self.handle_input()
            self.draw()
        return self.chosen_action 

    def handle_input(self):
        """Processes user input for menu navigation and selection."""
        for event in pygame.event.get():
            if self._handle_quit_event(event):
                return
            if event.type == pygame.KEYDOWN:
                self._handle_keypress(event)

    def draw(self):
        """Coordinates the rendering of all menu elements."""
        self._clear_screen()
        self._draw_title()
        self._draw_menu_items()
        pygame.display.flip()

    # Private Methods - Game Mode Actions
    def _start_normal_mode(self):
        """Sets up the game for normal player-controlled mode."""
        self.running = False
        self.chosen_action = "normal"
    
    def _start_pathfinder_mode(self):
        """Sets up the game for AI-controlled pathfinder mode."""
        self.running = False
        self.chosen_action = "pathfinder"
    
    def _quit_game(self):
        """Initiates the game exit sequence."""
        self.running = False
        self.chosen_action = "quit"

    # Private Methods - Drawing Related
    def _clear_screen(self):
        """Fills the screen with the background color."""
        self.screen.fill(Color.BLACK.value)

    def _draw_title(self):
        """Renders the game title at the top of the menu."""
        title_surface = self.title_font.render("Cave In", True, Color.WHITE.value)
        title_rect = title_surface.get_rect(
            centerx=WINDOW_WIDTH // 2,
            centery=WINDOW_HEIGHT // 4
        )
        self.screen.blit(title_surface, title_rect)

    def _draw_menu_items(self):
        """Manages the rendering of all menu options."""
        for i, item in enumerate(self.items):
            self._draw_single_item(i, item)

    def _draw_single_item(self, index: int, item: MenuItem):
        """Renders one menu item with appropriate highlighting if selected."""
        color = Color.RED.value if index == self.selected_index else Color.WHITE.value
        text_surface = self.font.render(item.text, True, color)
        text_rect = text_surface.get_rect(
            centerx=WINDOW_WIDTH // 2,
            centery=WINDOW_HEIGHT // 2 + (index * 60)
        )
        self.screen.blit(text_surface, text_rect)

    # Private Methods - Input Handling
    def _handle_quit_event(self, event: pygame.event.Event) -> bool:
        """Processes the quit event and updates menu state accordingly."""
        if event.type == pygame.QUIT:
            self.running = False
            self.chosen_action = "quit"
            return True
        return False

    def _handle_keypress(self, event: pygame.event.Event):
        """Routes keyboard input to appropriate menu navigation handlers."""
        if event.key == pygame.K_UP:
            self._move_selection_up()
        elif event.key == pygame.K_DOWN:
            self._move_selection_down()
        elif event.key == pygame.K_RETURN:
            self._select_current_item()

    def _move_selection_up(self):
        """Shifts the selection highlight to the previous menu item."""
        self.selected_index = (self.selected_index - 1) % len(self.items)

    def _move_selection_down(self):
        """Shifts the selection highlight to the next menu item."""
        self.selected_index = (self.selected_index + 1) % len(self.items)

    def _select_current_item(self):
        """Executes the action associated with the currently selected menu item."""
        self.items[self.selected_index].action() 