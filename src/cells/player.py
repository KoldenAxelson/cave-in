# Standard library imports
from dataclasses import dataclass, field
from enum import Enum
import time
# Third-party imports
import pygame
# Local imports
from .cell import Cell
from src.utils.config import Color, CELL_SIZE, GRID_SIZE, PLAYER_MOVE_COOLDOWN
from src.utils.config import Position, ColorType
from src.utils.input_handler import get_movement, use_action

class Direction(Enum):
    """Represents the four possible directions the player can face.
    
    Each direction is represented as a tuple of (dx, dy) where:
    - dx is the x-axis movement (-1 for left, 1 for right, 0 for no horizontal movement)
    - dy is the y-axis movement (-1 for up, 1 for down, 0 for no vertical movement)
    """
    UP = (0, -1)
    RIGHT = (1, 0)
    DOWN = (0, 1)
    LEFT = (-1, 0)

@dataclass
class Player(Cell):
    """Player character class that handles movement, interaction, and rendering.
    
    Inherits from Cell class and adds player-specific functionality like
    movement with cooldown, direction facing, and interaction with other cells.
    """
    position: Position = (GRID_SIZE // 2, GRID_SIZE // 2)  # Start in center of grid
    color: ColorType = Color.RED.value  # Player is represented as red
    last_move_time: float = 0.0  # Timestamp of last movement
    move_cooldown: float = PLAYER_MOVE_COOLDOWN  # Time required between moves
    facing: Direction = Direction.DOWN  # Initial facing direction

    def update(self, world) -> None:
        """Update player state based on input and game rules.
        
        Args:
            world: GameWorld instance containing current game state
        """
        # Check if enough time has passed since last move
        if time.time() - self.last_move_time < self.move_cooldown:
            return
        
        # Handle movement input
        delta = get_movement()
        if any(delta):  # If there is any movement input
            self._update_facing(delta)  # Update direction player is facing
            self._try_move(world, delta)  # Attempt to move in that direction
        
        # Handle action input (using items/interacting)
        if use_action():
            self._try_use_facing_cell(world)

    def _try_move(self, world, delta: Position) -> None:
        """Attempt to move the player in the specified direction.
        
        Args:
            world: GameWorld instance containing current game state
            delta: Tuple of (dx, dy) representing desired movement
        """
        x, y = self.position
        dx, dy = delta
        # Calculate new position, clamped to grid boundaries
        new_pos = (
            max(0, min(GRID_SIZE - 1, x + dx)),
            max(0, min(GRID_SIZE - 1, y + dy))
        )
        
        # Check if movement is valid (empty cell)
        target_cell = world.grid[new_pos]
        if new_pos != self.position and isinstance(target_cell, Cell) and type(target_cell) == Cell:
            # Update grid with player's new position
            world.grid[self.position] = Cell(self.position)  # Leave empty cell behind
            self.position = new_pos  # Update player position
            world.grid[new_pos] = self  # Place player in new position
            self.last_move_time = time.time()  # Reset move cooldown
            
            # Update movement statistics
            if world.stats:
                world.stats.tiles_moved += 1

    def _update_facing(self, delta: Position) -> None:
        """Update the direction the player is facing based on movement input.
        
        Args:
            delta: Tuple of (dx, dy) representing movement direction
        """
        for direction in Direction:
            if delta == direction.value:
                self.facing = direction
                break

    def draw(self, surface: pygame.Surface, screen_pos: Position) -> None:
        """Draw the player cell and direction indicator.
        
        Args:
            surface: Pygame surface to draw on
            screen_pos: Tuple of (x, y) coordinates for where to draw on screen
        """
        super().draw(surface, screen_pos)  # Draw base cell (red square)
        self._draw_direction_indicator(surface, screen_pos)  # Add direction indicator
    
    def _draw_direction_indicator(self, surface: pygame.Surface, screen_pos: Position) -> None:
        """Draw a white dot indicating which direction the player is facing.
        
        Args:
            surface: Pygame surface to draw on
            screen_pos: Tuple of (x, y) coordinates for where to draw on screen
        """
        screen_x, screen_y = screen_pos
        # Calculate center of cell
        center_x = screen_x + CELL_SIZE // 2
        center_y = screen_y + CELL_SIZE // 2
        # Get direction offset
        dx, dy = self.facing.value
        # Calculate indicator position (offset from center)
        indicator_x = center_x + dx * (CELL_SIZE // 4)
        indicator_y = center_y + dy * (CELL_SIZE // 4)
        # Draw white circle as direction indicator
        pygame.draw.circle(surface, Color.WHITE.value, (indicator_x, indicator_y), 3)

    def _try_use_facing_cell(self, world) -> None:
        """Attempt to interact with the cell the player is facing.
        
        Args:
            world: GameWorld instance containing current game state
        """
        dx, dy = self.facing.value
        x, y = self.position
        target_pos = (x + dx, y + dy)
        
        # Check if target position is within grid bounds
        if 0 <= target_pos[0] < GRID_SIZE and 0 <= target_pos[1] < GRID_SIZE:
            target_cell = world.grid.get(target_pos)
            if target_cell:
                target_cell.use(world)  # Trigger cell's use action
