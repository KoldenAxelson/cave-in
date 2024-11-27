from abc import ABC, abstractmethod
from src.utils.config import Position

class AIInterface(ABC):
    @abstractmethod
    def get_movement(self) -> Position:
        """Calculate and return the next movement for the AI."""
        pass

    @abstractmethod
    def should_use_action(self) -> bool:
        """Determine if the AI should use an action (collect stick or remove rock)."""
        pass

    @abstractmethod
    def update(self, world) -> None:
        """Update the AI's internal state based on the current world state."""
        pass 