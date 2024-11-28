# Standard library imports
from dataclasses import dataclass
import time
# Third-party imports
import pygame
# Local imports
from .cell import Cell
from src.utils.config import Color, GRID_SIZE, PLAYER_MOVE_COOLDOWN
from src.utils.config import Position, ColorType, Direction, CameraMode
from src.utils.input_handler import get_movement, use_action

@dataclass
class Player(Cell):
    """Player character class that handles movement, interaction, and rendering.
    Inherits from Cell class and adds player-specific functionality."""
    
    # Core Attributes
    position: Position = (GRID_SIZE // 2, GRID_SIZE // 2)  # Start in center of grid
    color: ColorType = Color.RED.value                     # Player is represented as red
    last_move_time: float = 0.0                            # Timestamp of last movement
    move_cooldown: float = PLAYER_MOVE_COOLDOWN            # Time required between moves
    facing: Direction = Direction.DOWN                     # Initial facing direction

    # Public Methods - Core Game Loop
    def update(self, world) -> None:
        """Updates player state based on input and game rules.
        Handles movement and action inputs with appropriate cooldowns."""
        if time.time() - self.last_move_time < self.move_cooldown:
            return
        
        delta = get_movement()
        if any(delta):  # If there is any movement input
            self.update_facing(delta)
            self.try_move(world, delta)
        
        if use_action():
            self.try_use_facing_cell(world)

    # Public Methods - Movement and Actions
    def update_facing(self, delta: Position) -> None:
        """Updates the direction the player is facing based on movement input.
        Matches facing direction to movement direction."""
        for direction in Direction:
            if delta == direction.value:
                self.facing = direction
                break

    def try_move(self, world, delta: Position) -> bool:
        """Attempts to move the player in the specified direction.
        Handles cooldown, boundary checks, and collision detection."""
        if not self._can_move_now():
            return False
            
        new_pos = self._calculate_new_position(delta)
        if self._is_valid_move(world, new_pos):
            self._perform_move(world, new_pos)
            return True
        return False

    def try_use_facing_cell(self, world) -> bool:
        """Attempts to interact with the cell in front of the player.
        Returns True if interaction was successful."""
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

    # Public Methods - Rendering
    def draw(self, surface: pygame.Surface, screen_pos: Position, cell_size: int, margin: int) -> None:
        """Renders the player cell and its direction indicator.
        Extends base cell rendering with a direction indicator."""
        super().draw(surface, screen_pos, cell_size, margin)
        indicator_pos = self._calculate_indicator_position(screen_pos, cell_size)
        self._draw_direction_indicator(surface, indicator_pos, cell_size)

    # Private Methods - Movement Helpers
    def _can_move_now(self) -> bool:
        """Checks if enough time has passed since last movement.
        Enforces movement cooldown for smooth gameplay."""
        return time.time() - self.last_move_time >= self.move_cooldown

    def _calculate_new_position(self, delta: Position) -> Position:
        """Calculates potential new position while respecting grid boundaries.
        Clamps coordinates to valid grid range."""
        x, y = self.position
        dx, dy = delta
        return (
            max(0, min(GRID_SIZE - 1, x + dx)),
            max(0, min(GRID_SIZE - 1, y + dy))
        )

    def _is_valid_move(self, world, new_pos: Position) -> bool:
        """Validates if a move to the target position is allowed.
        Checks for collisions and ensures target is an empty cell."""
        target_cell = world.grid[new_pos]
        return (new_pos != self.position and 
                isinstance(target_cell, Cell) and 
                type(target_cell) == Cell)

    def _perform_move(self, world, new_pos: Position) -> None:
        """Executes the movement to a new position.
        Updates grid state, position, and movement statistics."""
        world.grid[self.position] = Cell(self.position)
        self.position = new_pos
        world.grid[new_pos] = self
        self.last_move_time = time.time()
        
        if world.stats:
            world.stats.tiles_moved += 1

    # Private Methods - Rendering Helpers
    def _calculate_indicator_position(self, screen_pos: Position, cell_size: int) -> Position:
        """Calculates the screen position for the direction indicator.
        Places indicator offset from cell center based on facing direction."""
        screen_x, screen_y = screen_pos
        center_x = screen_x + cell_size // 2
        center_y = screen_y + cell_size // 2
        dx, dy = self.facing.value
        indicator_x = center_x + dx * (cell_size // 4)
        indicator_y = center_y + dy * (cell_size // 4)
        return (indicator_x, indicator_y)

    def _draw_direction_indicator(self, surface: pygame.Surface, pos: Position, cell_size: int) -> None:
        """Renders the direction indicator as a white circle.
        Size scales with cell size for consistent appearance."""
        indicator_size = max(2, cell_size // 10)
        pygame.draw.circle(surface, Color.WHITE.value, pos, indicator_size)
