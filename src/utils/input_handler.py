# Third-party imports
import pygame
# Local imports
from .config import Position
from typing import Optional
from src.ai.ai_interface import AIInterface

# Global variables
ai_controller: Optional[AIInterface] = None
previous_space_pressed: bool = False  # Track previous space bar state

# Public Methods - Core Input Handling
def get_movement() -> Position:
    """Retrieves movement input from either AI controller or keyboard.
    Delegates to appropriate handler based on whether AI is active."""
    if ai_controller:
        return ai_controller.get_movement()
    
    return _get_keyboard_movement()

def use_action() -> bool:
    """Determines if an action should be triggered this frame.
    Checks AI controller or space bar based on active input mode."""
    if ai_controller:
        return ai_controller.should_use_action()
    
    return _check_space_pressed()

def should_restart() -> bool:
    """Checks if the restart command (ESC key) is currently active."""
    keys = pygame.key.get_pressed()
    return keys[pygame.K_ESCAPE]

def should_quit(event: pygame.event.Event) -> bool:
    """Determines if the game should exit based on window close event."""
    return event.type == pygame.QUIT

# Public Methods - Configuration
def set_ai_controller(controller: Optional[AIInterface]) -> None:
    """Updates the active AI controller for automated input handling."""
    global ai_controller
    ai_controller = controller

# Private Methods - Movement Related
def _get_keyboard_movement() -> Position:
    """Processes keyboard input to determine movement direction.
    Prioritizes horizontal movement over vertical movement."""
    keys = pygame.key.get_pressed()
    
    # Check horizontal movement first
    dx = _get_horizontal_movement(keys)
    if dx != 0:
        return (dx, 0)
        
    # Only check vertical if no horizontal movement
    dy = _get_vertical_movement(keys)
    return (0, dy)

def _get_horizontal_movement(keys) -> int:
    """Calculates horizontal movement from A/D key states.
    Returns -1 for left, 1 for right, 0 for no movement."""
    return keys[pygame.K_d] - keys[pygame.K_a]

def _get_vertical_movement(keys) -> int:
    """Calculates vertical movement from W/S key states.
    Returns -1 for up, 1 for down, 0 for no movement."""
    return keys[pygame.K_s] - keys[pygame.K_w]

# Private Methods - Action Related
def _check_space_pressed() -> bool:
    """Detects when space bar is newly pressed.
    Prevents continuous triggering while space is held down."""
    global previous_space_pressed
    
    # Get current space bar state
    current_space_pressed = pygame.key.get_pressed()[pygame.K_SPACE]
    
    # Only return True if space is currently pressed but wasn't previously
    action_triggered = current_space_pressed and not previous_space_pressed
    
    # Update previous state for next frame
    previous_space_pressed = current_space_pressed
    
    return action_triggered 