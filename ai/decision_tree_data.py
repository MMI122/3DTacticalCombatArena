"""
AI Decision Tree Data Structures
Captures the decision-making process of AI agents for visualization
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum, auto


class NodeStatus(Enum):
    """Status of a tree node"""
    EXPLORED = auto()
    PRUNED = auto()
    SELECTED = auto()
    DISCARDED = auto()


@dataclass
class DecisionNode:
    """A single node in the AI decision tree"""
    node_id: int
    action_label: str        # e.g. "Move Warrior → (3,4)" or "Attack Archer"
    action_detail: str       # More details about the action
    score: float             # Evaluation score
    depth: int               # Depth in tree
    is_maximizing: bool      # True if maximizing player
    status: NodeStatus = NodeStatus.EXPLORED
    children: List[DecisionNode] = field(default_factory=list)
    alpha: float = float('-inf')
    beta: float = float('inf')
    
    # Extra info
    unit_name: str = ""
    team: str = ""
    
    @property
    def is_selected(self) -> bool:
        return self.status == NodeStatus.SELECTED
    
    @property
    def is_pruned(self) -> bool:
        return self.status == NodeStatus.PRUNED


@dataclass 
class FuzzyDecisionInfo:
    """Fuzzy logic decision breakdown for visualization"""
    action_label: str
    score: float
    reasoning: str
    aggression: float = 50.0
    is_selected: bool = False
    
    # Fuzzy inputs
    own_hp_pct: float = 0.0
    team_advantage: float = 0.0
    enemies_in_range: int = 0
    target_name: str = ""
    target_hp_pct: float = 0.0


@dataclass
class DecisionTreeData:
    """Complete decision tree data for one AI move"""
    team: str                              # "RED" or "BLUE"
    algorithm: str                         # "Minimax" or "Fuzzy"
    turn_number: int = 0
    root: Optional[DecisionNode] = None    # Tree root (for Minimax)
    fuzzy_decisions: List[FuzzyDecisionInfo] = field(default_factory=list)  # For Fuzzy
    best_action_label: str = ""
    best_score: float = 0.0
    nodes_searched: int = 0
    pruned_count: int = 0
    thinking_time: float = 0.0
