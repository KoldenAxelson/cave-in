# Third-party imports
import pygame
# Local imports
from .config import Position

def should_quit(event: pygame.event.Event) -> bool:
    """Check if the game should quit based on the event.
    
    Args:
        event: Pygame event to check
        
    Returns:
        bool: True if quit event detected (window close button clicked)
    """
    return event.type == pygame.QUIT 

def get_movement() -> Position:
    """Get player movement input from keyboard.
    
    Returns:
        Position: Tuple of (dx, dy) representing movement direction where:
            - dx: -1 for left (A), 1 for right (D), 0 for no horizontal movement
            - dy: -1 for up (W), 1 for down (S), 0 for no vertical movement
            
    Note:
        - Prioritizes horizontal movement over vertical
        - Only returns movement in one direction at a time
        - Uses WASD keys for movement
    """
    keys = pygame.key.get_pressed()

    # Check horizontal movement first (A/D keys)
    dx = keys[pygame.K_d] - keys[pygame.K_a]
    if dx != 0:
        return (dx, 0)
    
    # If no horizontal movement, check vertical (W/S keys)
    dy = keys[pygame.K_s] - keys[pygame.K_w]
    return (0, dy)

def use_action() -> bool:
    """Check if the action key (SPACE) is pressed.
    
    Returns:
        bool: True if SPACE key is pressed
        
    Note:
        Used for interactions like collecting sticks or removing rocks
    """
    keys = pygame.key.get_pressed()
    return keys[pygame.K_SPACE]

def should_restart() -> bool:
    """Check if the restart key (ESC) is pressed.
    
    Returns:
        bool: True if ESC key is pressed
        
    Note:
        Used to restart the game after game over
    """
    keys = pygame.key.get_pressed()
    return keys[pygame.K_ESCAPE] 