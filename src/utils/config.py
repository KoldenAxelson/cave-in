"""Global configuration settings and type definitions for the game.
Centralizes all constants, enums, and type aliases used throughout the application."""

from enum import Enum
from typing import Tuple, TypeAlias, List, Set

# Type System Definitions
# ----------------------
# Core type aliases used throughout the codebase
Position:    TypeAlias = Tuple[int, int]      # (x, y) grid coordinates
ColorType:   TypeAlias = Tuple[int, int, int] # RGB color values
PathType:    TypeAlias = List[Position]       # Sequence of positions forming a path
VisitedType: TypeAlias = Set[Tuple[Position, Tuple[Position, ...]]] # AI pathfinding state

# Enumerations
# ------------
# Core game enums defining valid states and modes
class Direction(Enum):
    """Cardinal directions for player movement and facing.
    Each direction maps to a (dx, dy) tuple for position updates."""
    UP    = ( 0,-1)
    RIGHT = ( 1, 0)
    DOWN  = ( 0, 1)
    LEFT  = (-1, 0)
    NONE  = ( 0, 0)

class Difficulty(Enum):
    """Game difficulty settings affecting rock placement mechanics.
    EASY ensures player can't get trapped, NORMAL uses random placement."""
    EASY   = "easy"     # Uses fill manager for safe rock placement
    NORMAL = "normal"   # Uses random rock placement (original)

class CameraMode(Enum):
    """Camera behavior settings affecting game view presentation.
    Controls whether player has limited vision or can see entire map."""
    PLAYER_FOLLOW = "player_follow"  # Camera follows player with limited view
    FULL_MAP     = "full_map"        # Shows entire game map

class Color(Enum):
    """Standard RGB color definitions used throughout the game.
    Provides consistent color scheme for all game elements."""
    BLACK:  ColorType = (  0,   0,   0)
    WHITE:  ColorType = (255, 255, 255)
    GRAY:   ColorType = (128, 128, 128)
    L_GRAY: ColorType = (200, 200, 200)
    D_GRAY: ColorType = ( 56,  56,  56)
    RED:    ColorType = (255,   0,   0)
    GREEN:  ColorType = (  0, 255,   0)
    BLUE:   ColorType = (  0,   0, 255)
    BROWN:  ColorType = (139,  69,  19)

# Game Constants
# -------------
# Core gameplay settings
FPS:                    int = 60   # Target frames per second
CELL_SIZE:              int = 30   # Pixel size of each grid cell
GRID_SIZE:              int = 10   # Number of cells in each row/column
MARGIN:                 int = 3    # Pixel gap between cells
VIEW_RADIUS:            int = 4    # Cells visible around player
PLAYER_MOVE_COOLDOWN: float = 0.02 # Seconds between allowed moves

# Current Mode Settings
DIFFICULTY:  Difficulty = Difficulty.EASY     # Current difficulty mode
CAMERA_MODE: CameraMode = CameraMode.FULL_MAP # Current camera mode

# Display Configuration
# -------------------
# Window and rendering settings
SCORE_HEIGHT:       int = 50    # Height of score display area
WINDOW_WIDTH:       int = (VIEW_RADIUS * 2 + 1) * CELL_SIZE  # Total window width
GAME_WINDOW_HEIGHT: int = (VIEW_RADIUS * 2 + 1) * CELL_SIZE  # Height of game area
WINDOW_HEIGHT:      int = GAME_WINDOW_HEIGHT + SCORE_HEIGHT  # Total window height

# AI Configuration
# --------------
# Settings for AI behavior
STICK_VALUE: int = GRID_SIZE  # Value assigned to sticks for AI pathfinding

# Global Mutables
# --------------
# Global variables that are shared across the game
# Nothing is shared yet, but this is a placeholder for future shared state