from abc import ABC, abstractmethod
from src.utils.config import Position

class AIInterface(ABC):
    """Abstract interface defining core AI behavior for game agents.
    
    Provides a standard contract that all AI implementations must follow,
    ensuring consistent behavior across different AI strategies."""

    # Core Decision Making
    @abstractmethod
    def get_movement(self) -> Position:
        """Calculates the next movement direction for the AI.
        
        Returns:
            Position: A (dx, dy) tuple representing the desired movement direction.
                     Values are constrained to (-1, 0, 1) for each component.
        """
        pass

    @abstractmethod
    def should_use_action(self) -> bool:
        """Determines if the AI should interact with an adjacent cell.
        
        Used for both stick collection and rock removal decisions.
        
        Returns:
            bool: True if the AI should attempt an interaction, False otherwise.
        """
        pass

    # State Management
    @abstractmethod
    def update(self, world) -> None:
        """Updates the AI's internal state based on the current world state.
        
        Called each frame to allow the AI to process new information and
        update its decision-making state.
        
        Args:
            world: The current game world state containing grid and entities.
        """
        pass 