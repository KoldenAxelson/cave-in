from dataclasses import dataclass, field
from typing import Optional, Any
import time
from src.cells import Stick, Rock
from src.utils.config import Position, PLAYER_MOVE_COOLDOWN
from src.utils.player_interface import PlayerInterface

@dataclass
class ActionHandler:
    """Manages AI decision-making for actions in the game world.
    
    Handles the logic for when to collect sticks and remove rocks,
    taking into account the current path and game state."""
    
    # Core Attributes
    world: Any                                  # Current game world state
    last_action_time: float = 0.0              # Timestamp of last action
    current_path: list = field(default_factory=list)  # Path being followed
    player: PlayerInterface = field(init=False) # Interface to player state
    last_action_success: bool = False          # Result of last action attempt

    # Initialization
    def __post_init__(self):
        """Initialize player interface after dataclass initialization."""
        self.player = PlayerInterface(self.world)

    # Public Methods - Core Decision Making
    def should_use_action(self) -> bool:
        """Evaluates whether an action should be taken this frame.
        Considers board state, cooldowns, and target cell type."""
        if not self._is_action_possible():
            return False

        target_pos = self._get_target_position()
        if not target_pos:
            return False

        return self._should_use_action_at(target_pos)

    def did_use_action(self) -> bool:
        """Checks if an action was successfully used recently.
        Used to prevent repeated action attempts during cooldown."""
        return (self.last_action_success and 
                time.time() - self.last_action_time < PLAYER_MOVE_COOLDOWN)

    # Public Methods - State Management
    def update(self, world, target_path):
        """Updates handler state with new world information.
        Ensures handler has current world state and path data."""
        self.world = world
        self.current_path = target_path
        self.player = PlayerInterface(world)

    # Private Methods - Action Validation
    def _is_action_possible(self) -> bool:
        """Validates basic conditions for action execution.
        Checks board fullness and action cooldown."""
        if self.world.is_board_full():
            return False
            
        if not self._can_act():
            return False
            
        return True

    def _can_act(self) -> bool:
        """Checks if action cooldown has expired.
        Ensures smooth action pacing."""
        return self.player.position and time.time() - self.last_action_time >= PLAYER_MOVE_COOLDOWN

    def _can_remove_rock(self, target_pos: Position) -> bool:
        """Validates if rock removal is possible.
        Checks stick availability and path relevance."""
        can_remove = (self.world.stats and 
                    self.world.stats.sticks_collected > 0 and 
                    target_pos in self.current_path)
        if can_remove:
            print(f"WARNING: About to remove rock at {target_pos}")
        return can_remove

    # Private Methods - Action Decision Logic
    def _should_use_action_at(self, target_pos: Position) -> bool:
        """Determines if action should be used at specific position.
        Handles different cell types (Stick vs Rock) appropriately."""
        target_cell = self.world.grid.get(target_pos)

        if isinstance(target_cell, Stick):
            return self._attempt_action()

        if isinstance(target_cell, Rock):
            return self._should_remove_rock(target_pos)

        return False

    def _should_remove_rock(self, target_pos: Position) -> bool:
        """Evaluates if a rock should be removed.
        Considers stick availability and path relevance."""
        if self._can_remove_rock(target_pos):
            return self._attempt_action()
        return False

    # Private Methods - Action Execution
    def _get_target_position(self) -> Optional[Position]:
        """Calculates position in front of player.
        Returns None if player position or facing is invalid."""
        if not self.player.position or not self.player.facing:
            return None

        px, py = self.player.position
        dx, dy = self.player.facing.value
        return (px + dx, py + dy)

    def _attempt_action(self) -> bool:
        """Attempts to execute an action and updates state.
        Records success/failure and updates timing."""
        self.last_action_success = self.player.try_use_action()
        if self.last_action_success:
            self.last_action_time = time.time()
        return self.last_action_success