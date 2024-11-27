from enum import Enum
from typing import Tuple, TypeAlias

# Type Definitions
Position:  TypeAlias = Tuple[int, int]
ColorType: TypeAlias = Tuple[int, int, int]

# Game Configuration
FPS:           int = 60
CELL_SIZE:     int = 30
GRID_SIZE:     int = 6
MARGIN:        int = 3
VIEW_RADIUS:   int = 4
PLAYER_MOVE_COOLDOWN: float = 0.1

# Window Configuration
SCORE_HEIGHT:       int = 50  
WINDOW_WIDTH:       int = (VIEW_RADIUS * 2 + 1) * CELL_SIZE
GAME_WINDOW_HEIGHT: int = (VIEW_RADIUS * 2 + 1) * CELL_SIZE  
WINDOW_HEIGHT:      int = GAME_WINDOW_HEIGHT + SCORE_HEIGHT  

# Color Configuration
class Color(Enum):
    BLACK:  ColorType = (  0,   0,   0)
    WHITE:  ColorType = (255, 255, 255)
    GRAY:   ColorType = (128, 128, 128)
    L_GRAY: ColorType = (200, 200, 200)
    D_GRAY: ColorType = ( 56,  56,  56)
    RED:    ColorType = (255,   0,   0)
    GREEN:  ColorType = (  0, 255,   0)
    BLUE:   ColorType = (  0,   0, 255)
    BROWN:  ColorType = (139,  69,  19) 