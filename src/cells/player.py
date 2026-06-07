# Standard library imports
from dataclasses import dataclass
import time
# Third-party imports
import pygame
# Local imports
from .cell import Cell
from .stick import Stick
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
        
        movement_delta = get_movement()
        if any(movement_delta):  # any non-zero component means the player pressed a direction
            self.update_facing(movement_delta)
            self.try_move(world, movement_delta)
        
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
            
        target_position = self._calculate_new_position(delta)
        if self._is_valid_move(world, target_position):
            self._perform_move(world, target_position)
            return True
        return False

    def try_use_facing_cell(self, world) -> bool:
        """Attempts to interact with the cell in front of the player.
        Returns True if interaction was successful."""
        if not self.facing:
            return False
            
        facing_delta_x, facing_delta_y = self.facing.value
        player_x, player_y = self.position
        target_position = (player_x + facing_delta_x, player_y + facing_delta_y)

        if 0 <= target_position[0] < GRID_SIZE and 0 <= target_position[1] < GRID_SIZE:
            target_cell = world.grid.get(target_position)
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
        current_x, current_y = self.position
        delta_x, delta_y = delta
        # Clamp to the grid so the player can never step outside the world edges.
        return (
            max(0, min(GRID_SIZE - 1, current_x + delta_x)),
            max(0, min(GRID_SIZE - 1, current_y + delta_y))
        )

    def _is_valid_move(self, world, target_position: Position) -> bool:
        """Validates if a move to the target position is allowed.
        Walkable targets are empty floor (a plain Cell) or a Stick — stepping
        onto a stick collects it (see _perform_move). Rocks block movement and
        must be cleared with an action instead."""
        target_cell = world.grid[target_position]
        if target_position == self.position:
            return False
        # `type(...) is Cell` matches only a plain empty cell, not Rock/Player;
        # Stick is allowed explicitly because we collect it by walking onto it.
        return type(target_cell) is Cell or isinstance(target_cell, Stick)

    def _perform_move(self, world, target_position: Position) -> None:
        """Executes the movement to a new position.
        Updates grid state and movement stats, and collects a stick if we just
        stepped onto one."""
        target_cell = world.grid[target_position]

        # Leave behind an empty cell where the player was standing.
        world.grid[self.position] = Cell(self.position)
        self.position = target_position
        world.grid[target_position] = self
        self.last_move_time = time.time()

        if world.stats:
            world.stats.tiles_moved += 1

        # Stepping onto a stick collects it. The player already occupies this
        # cell now, so the replacement stick can't spawn on top of us.
        if isinstance(target_cell, Stick):
            if world.stats:
                world.stats.sticks_collected += 1
            world._place_random_stick()

    # Private Methods - Rendering Helpers
    def _calculate_indicator_position(self, screen_pos: Position, cell_size: int) -> Position:
        """Calculates the screen position for the direction indicator.
        Places indicator offset from cell center based on facing direction."""
        screen_x, screen_y = screen_pos
        center_x = screen_x + cell_size // 2
        center_y = screen_y + cell_size // 2
        facing_delta_x, facing_delta_y = self.facing.value
        # Push the indicator a quarter-cell toward the facing direction.
        indicator_x = center_x + facing_delta_x * (cell_size // 4)
        indicator_y = center_y + facing_delta_y * (cell_size // 4)
        return (indicator_x, indicator_y)

    def _draw_direction_indicator(self, surface: pygame.Surface, indicator_position: Position, cell_size: int) -> None:
        """Renders the direction indicator as a white circle.
        Size scales with cell size for consistent appearance."""
        indicator_radius = max(2, cell_size // 10)  # never smaller than 2px so it stays visible
        pygame.draw.circle(surface, Color.WHITE.value, indicator_position, indicator_radius)
