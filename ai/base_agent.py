"""
Base AI Agent Interface
Abstract base class for all AI agents
"""

from abc import ABC, abstractmethod
from typing import Tuple, Optional, List, Dict, Any

from core.game_state import GameState, Action
from core.unit import Team


class BaseAgent(ABC):
    """
    Abstract base class for AI agents
    All AI implementations must inherit from this class
    """
    
    def __init__(self, name: str, team: Optional[Team] = None):
        self.name = name
        self.team = team
        self._debug_info: Dict[str, Any] = {}
    
    @abstractmethod
    def get_action(self, game_state: GameState) -> Tuple[Optional[Action], float, str]:
        """
        Determine the best action to take
        
        Args:
            game_state: Current game state
            
        Returns:
            Tuple of:
            - Action to take (or None to end turn)
            - Evaluation score of the action
            - Reasoning string explaining the decision
        """
        pass
    
    @abstractmethod
    def get_algorithm_name(self) -> str:
        """Return the name of the algorithm used"""
        pass
    
    @abstractmethod
    def get_algorithm_description(self) -> str:
        """Return a description of how the algorithm works"""
        pass
    
    def get_debug_info(self) -> Dict[str, Any]:
        """Get debug information from the last decision"""
        return self._debug_info
    
    def reset(self):
        """Reset agent state for a new game"""
        self._debug_info.clear()
    
    def __repr__(self):
        return f"{self.__class__.__name__}({self.name}, {self.team})"


class RandomAgent(BaseAgent):
    """Simple random agent for testing"""
    
    def __init__(self, team: Optional[Team] = None):
        super().__init__("Random Agent", team)
    
    def get_action(self, game_state: GameState) -> Tuple[Optional[Action], float, str]:
        import random
        
        actions = game_state.get_all_legal_actions()
        if not actions:
            return None, 0.0, "No actions available"
        
        action = random.choice(actions)
        return action, 0.0, "Random selection"
    
    def get_algorithm_name(self) -> str:
        return "Random"
    
    def get_algorithm_description(self) -> str:
        return "Selects actions completely at random. Used for testing."
