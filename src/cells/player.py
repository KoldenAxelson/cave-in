# Standard library imports
from dataclasses import dataclass
import time
# Third-party imports
import pygame
# Local imports
from .cell import Cell
from src.utils.config import Color, CELL_SIZE, GRID_SIZE, PLAYER_MOVE_COOLDOWN, CAMERA_MODE, WINDOW_WIDTH, GAME_WINDOW_HEIGHT, MARGIN
from src.utils.config import Position, ColorType, Direction, CameraMode
from src.utils.input_handler import get_movement, use_action

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
        """Update player state based on input and game rules."""
        # Check if enough time has passed since last move
        if time.time() - self.last_move_time < self.move_cooldown:
            return
        
        # Handle movement input
        delta = get_movement()
        if any(delta):  # If there is any movement input
            self.update_facing(delta)
            self.try_move(world, delta)
        
        # Handle action input (using items/interacting)
        if use_action():
            self.try_use_facing_cell(world)

    def draw(self, surface: pygame.Surface, screen_pos: Position, cell_size: int, margin: int) -> None:
        """Draw the player cell and direction indicator."""
        super().draw(surface, screen_pos, cell_size, margin)
        
        screen_x, screen_y = screen_pos
        # Calculate center of cell
        center_x = screen_x + cell_size // 2
        center_y = screen_y + cell_size // 2
        # Get direction offset
        dx, dy = self.facing.value
        # Calculate indicator position (offset from center)
        indicator_x = center_x + dx * (cell_size // 4)
        indicator_y = center_y + dy * (cell_size // 4)
        # Scale indicator size with cell size
        indicator_size = max(2, cell_size // 10)
        # Draw white circle as direction indicator
        pygame.draw.circle(surface, Color.WHITE.value, (indicator_x, indicator_y), indicator_size)

    def update_facing(self, delta: Position) -> None:
        """Update the direction the player is facing based on movement input."""
        for direction in Direction:
            if delta == direction.value:
                self.facing = direction
                break

    def try_move(self, world, delta: Position) -> bool:
        """Attempt to move the player in the specified direction."""
        if time.time() - self.last_move_time < self.move_cooldown:
            return False
            
        x, y = self.position
        dx, dy = delta
        new_pos = (
            max(0, min(GRID_SIZE - 1, x + dx)),
            max(0, min(GRID_SIZE - 1, y + dy))
        )
        
        target_cell = world.grid[new_pos]
        if new_pos != self.position and isinstance(target_cell, Cell) and type(target_cell) == Cell:
            world.grid[self.position] = Cell(self.position)
            self.position = new_pos
            world.grid[new_pos] = self
            self.last_move_time = time.time()
            
            if world.stats:
                world.stats.tiles_moved += 1
            return True
        return False

    def try_use_facing_cell(self, world) -> bool:
        """Attempt to use/interact with the cell the player is facing."""
        if not self.facing:
            return False
            
        dx, dy = self.facing.value
        px, py = self.position
        target_pos = (px + dx, py + dy)
        
        if 0 <= target_pos[0] < GRID_SIZE and 0 <= target_pos[1] < GRID_SIZE:
            target_cell = world.grid.get(target_pos)
            if hasattr(target_cell, 'use'):
                target_cell.use(world)
                return True
        return False
