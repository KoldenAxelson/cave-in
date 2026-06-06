# `from __future__ import annotations` must be the first statement. It keeps all
# annotations as strings so they don't need their classes imported at runtime.
from __future__ import annotations
# Third-party imports
import pygame
# Local imports
from .config import Position
from typing import Optional, TYPE_CHECKING

# AIInterface is only needed for type hints. Importing it at runtime would create
# a circular import (ai -> utils -> cells -> input_handler -> ai), so we guard it
# behind TYPE_CHECKING.
if TYPE_CHECKING:
    from src.ai.ai_interface import AIInterface

# Global variables
ai_controller: Optional[AIInterface] = None
previous_space_pressed: bool = False  # Remembers last frame's space state for edge detection

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

# Public Methods - Configuration
def set_ai_controller(controller: Optional[AIInterface]) -> None:
    """Updates the active AI controller for automated input handling."""
    global ai_controller
    ai_controller = controller

# Private Methods - Movement Related
def _get_keyboard_movement() -> Position:
    """Processes keyboard input to determine movement direction.
    Prioritizes horizontal movement over vertical movement."""
    pressed_keys = pygame.key.get_pressed()

    # Horizontal movement takes priority, so diagonal input never happens
    horizontal_delta = _get_horizontal_movement(pressed_keys)
    if horizontal_delta != 0:
        return (horizontal_delta, 0)

    vertical_delta = _get_vertical_movement(pressed_keys)
    return (0, vertical_delta)

def _get_horizontal_movement(pressed_keys) -> int:
    """Calculates horizontal movement from A/D key states.
    Returns -1 for left, 1 for right, 0 for no movement."""
    return pressed_keys[pygame.K_d] - pressed_keys[pygame.K_a]

def _get_vertical_movement(pressed_keys) -> int:
    """Calculates vertical movement from W/S key states.
    Returns -1 for up, 1 for down, 0 for no movement."""
    return pressed_keys[pygame.K_s] - pressed_keys[pygame.K_w]

# Private Methods - Action Related
def _check_space_pressed() -> bool:
    """Detects when space bar is newly pressed.
    Prevents continuous triggering while space is held down."""
    global previous_space_pressed

    current_space_pressed = pygame.key.get_pressed()[pygame.K_SPACE]

    # Fire only on the rising edge so holding space doesn't repeat the action
    action_triggered = current_space_pressed and not previous_space_pressed

    previous_space_pressed = current_space_pressed

    return action_triggered
