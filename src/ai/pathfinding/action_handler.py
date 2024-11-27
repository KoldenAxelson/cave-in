from dataclasses import dataclass, field
from typing import Optional, Any
import time
from src.cells import Stick, Rock
from src.utils.config import Position, PLAYER_MOVE_COOLDOWN
from src.utils.player_interface import PlayerInterface

@dataclass
class ActionHandler:
    """Handles player actions in the game world."""
    
    world: Any
    last_action_time: float = 0.0
    current_path: list = field(default_factory=list)
    player: PlayerInterface = field(init=False)
    last_action_success: bool = False

    def __post_init__(self):
        """Initialize player interface after dataclass initialization."""
        self.player = PlayerInterface(self.world)

    def should_use_action(self) -> bool:
        """Determine if an action should be used based on current state."""
        if not self._can_act():
            return False

        target_pos = self._get_target_position()
        if not target_pos:
            return False

        target_cell = self.world.grid.get(target_pos)

        if isinstance(target_cell, Stick):
            return self._attempt_action()

        if isinstance(target_cell, Rock) and self._can_remove_rock(target_pos):
            return self._attempt_action()

        return False

    def did_use_action(self) -> bool:
        """Check if the last action was used successfully."""
        return self.last_action_success and time.time() - self.last_action_time < PLAYER_MOVE_COOLDOWN

    def update(self, world, target_path):
        """Update handler state with new world and path information."""
        self.world = world
        self.current_path = target_path
        self.player = PlayerInterface(world)

    def _can_act(self) -> bool:
        """Check if the player can perform an action."""
        return self.player.position and time.time() - self.last_action_time >= PLAYER_MOVE_COOLDOWN

    def _get_target_position(self) -> Optional[Position]:
        """Calculate the position directly in front of the player."""
        if not self.player.position or not self.player.facing:
            return None

        px, py = self.player.position
        dx, dy = self.player.facing.value
        return (px + dx, py + dy)

    def _attempt_action(self) -> bool:
        """Attempt to use an action and update state accordingly."""
        self.last_action_success = self.player.try_use_action()
        if self.last_action_success:
            self.last_action_time = time.time()
        return self.last_action_success

    def _can_remove_rock(self, target_pos: Position) -> bool:
        """Check if a rock can be removed at the target position."""
        return (self.world.stats and 
                self.world.stats.sticks_collected > 0 and 
                target_pos in self.current_path)