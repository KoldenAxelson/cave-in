from enum import Enum
from typing import Tuple, TypeAlias, List, Set

# Type Definitions
Position:  TypeAlias = Tuple[int, int]
ColorType: TypeAlias = Tuple[int, int, int]
PathType = List[Position]
VisitedType = Set[Tuple[Position, Tuple[Position, ...]]] 

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

class Direction(Enum):
    """Represents the four possible directions the player can face.
    
    Each direction is represented as a tuple of (dx, dy) where:
    - dx is the x-axis movement (-1 for left, 1 for right, 0 for no horizontal movement)
    - dy is the y-axis movement (-1 for up, 1 for down, 0 for no vertical movement)
    """
    UP    = ( 0,-1)
    RIGHT = ( 1, 0)
    DOWN  = ( 0, 1)
    LEFT  = (-1, 0)
    NONE  = ( 0, 0)

class Difficulty(Enum):
    """Game difficulty settings affecting rock placement."""
    EASY = "easy"       # Uses fill manager for safe rock placement
    NORMAL = "normal"   # Uses random rock placement (original)

class CameraMode(Enum):
    """Available camera modes for game rendering."""
    PLAYER_FOLLOW = "player_follow"  # Camera follows player with limited view
    FULL_MAP = "full_map"           # Shows entire game map

# Game Configuration
FPS:           int = 60
CELL_SIZE:     int = 30
GRID_SIZE:     int = 8
MARGIN:        int = 3
VIEW_RADIUS:   int = 4
PLAYER_MOVE_COOLDOWN: float = 0.02
DIFFICULTY:  Difficulty = Difficulty.EASY  
CAMERA_MODE: CameraMode = CameraMode.FULL_MAP

# Window Configuration
SCORE_HEIGHT:       int = 50  
WINDOW_WIDTH:       int = (VIEW_RADIUS * 2 + 1) * CELL_SIZE
GAME_WINDOW_HEIGHT: int = (VIEW_RADIUS * 2 + 1) * CELL_SIZE  
WINDOW_HEIGHT:      int = GAME_WINDOW_HEIGHT + SCORE_HEIGHT  

# AI Configuration
STICK_VALUE = GRID_SIZE * 2
