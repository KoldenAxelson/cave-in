import pygame
from .config import Position

def should_quit(event: pygame.event.Event) -> bool:
    return event.type == pygame.QUIT 

def get_movement() -> Position:
    keys = pygame.key.get_pressed()

    dx = keys[pygame.K_d] - keys[pygame.K_a]
    if dx != 0:
        return (dx, 0)
    
    dy = keys[pygame.K_s] - keys[pygame.K_w]
    return (0, dy)

def use_action() -> bool:
    keys = pygame.key.get_pressed()
    return keys[pygame.K_SPACE]

def should_restart() -> bool:
    keys = pygame.key.get_pressed()
    return keys[pygame.K_ESCAPE] 