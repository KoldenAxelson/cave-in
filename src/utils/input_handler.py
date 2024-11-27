# Third-party imports
import pygame
# Local imports
from .config import Position
from typing import Optional
from src.ai.ai_interface import AIInterface

# Global variable for AI controller
ai_controller: Optional[AIInterface] = None

def set_ai_controller(controller: Optional[AIInterface]) -> None:
    """Set or clear the AI controller."""
    global ai_controller
    ai_controller = controller

def should_quit(event: pygame.event.Event) -> bool:
    """Check if the game should quit based on the event."""
    return event.type == pygame.QUIT

def get_movement() -> Position:
    """Get movement input from keyboard or AI.
    
    Returns:
        Position: (dx, dy) tuple representing movement direction
    """
    if ai_controller:
        return ai_controller.get_movement()
    
    keys = pygame.key.get_pressed()
    
    # Check horizontal movement first
    dx = keys[pygame.K_d] - keys[pygame.K_a]
    if dx != 0:
        return (dx, 0)
        
    # Only check vertical if no horizontal movement
    dy = keys[pygame.K_s] - keys[pygame.K_w]
    return (0, dy)

def use_action() -> bool:
    """Check if action should be taken (from keyboard or AI).
    
    Returns:
        bool: True if action key is pressed or AI wants to take action
    """
    if ai_controller:
        return ai_controller.should_use_action()
    
    return pygame.key.get_pressed()[pygame.K_SPACE]

def should_restart() -> bool:
    """Check if the restart key (ESC) is pressed."""
    keys = pygame.key.get_pressed()
    return keys[pygame.K_ESCAPE] 