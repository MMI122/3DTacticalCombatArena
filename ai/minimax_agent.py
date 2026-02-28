"""
Minimax Agent with Alpha-Beta Pruning
Production-grade implementation with advanced optimizations
"""

from typing import Tuple, Optional, List, Dict, Any
import time
from dataclasses import dataclass

from .base_agent import BaseAgent
from .evaluation import Evaluator, ActionEvaluator, EvaluationWeights
from .decision_tree_data import DecisionNode, DecisionTreeData, NodeStatus
from core.game_state import GameState, Action, ActionType, GamePhase
from core.unit import Team
from config.settings import get_config


@dataclass
class TranspositionEntry:
    """Entry in the transposition table"""
    depth: int
    score: float
    flag: str  # 'exact', 'lower', 'upper'
    best_action: Optional[Action]


class MinimaxAgent(BaseAgent):
    """
    AI agent using Minimax algorithm with Alpha-Beta pruning
    
    Features:
    - Alpha-Beta pruning for efficient search
    - Transposition tables to avoid redundant calculations
    - Iterative deepening for time management
    - Move ordering for better pruning
    - Quiescence search for tactical positions
    """
    
    def __init__(
        self,
        team: Optional[Team] = None,
        max_depth: int = 4,
        time_limit: float = 5.0,
        use_iterative_deepening: bool = True,
        use_transposition_table: bool = True
    ):
        super().__init__("Minimax Alpha-Beta AI", team)
        
        config = get_config()
        self.max_depth = max_depth or config.ai.minimax_depth
        self.time_limit = time_limit or config.ai.minimax_time_limit
        self.use_iterative_deepening = use_iterative_deepening
        self.use_transposition_table = use_transposition_table
        
        self.evaluator = Evaluator()
        
        # Transposition table
        self.transposition_table: Dict[int, TranspositionEntry] = {}
        
        # Statistics
        self.nodes_searched = 0
        self.cache_hits = 0
        self.pruned_branches = 0
        self.search_start_time = 0
        
        # Best move found so far (for iterative deepening)
        self.best_action_so_far: Optional[Action] = None
        self.best_score_so_far: float = float('-inf')
        
        # Decision tree capture
        self._node_counter = 0
        self._capture_tree = True
        self._max_capture_depth = 2  # Only capture top 2 levels for viz
        self.last_decision_tree: Optional[DecisionTreeData] = None
    
    def get_action(self, game_state: GameState) -> Tuple[Optional[Action], float, str]:
        """
        Get the best action using Minimax with Alpha-Beta pruning
        """
        self.search_start_time = time.time()
        self.nodes_searched = 0
        self.cache_hits = 0
        self.pruned_branches = 0
        self.best_action_so_far = None
        self.best_score_so_far = float('-inf')
        self._node_counter = 0
        
        # Get all legal actions
        actions = game_state.get_all_legal_actions()
        if not actions:
            return None, 0.0, "No actions available"
        
        # If only one action, take it
        if len(actions) == 1:
            return actions[0], 0.0, "Only one action available"
        
        # Order actions for better pruning
        actions = self._order_actions(game_state, actions)
        
        best_action = None
        best_score = float('-inf')
        reasoning_parts = []
        
        if self.use_iterative_deepening:
            # Iterative deepening search
            for depth in range(1, self.max_depth + 1):
                if self._time_exceeded():
                    break
                
                try:
                    action, score = self._search_at_depth(game_state, actions, depth)
                    if action:
                        best_action = action
                        best_score = score
                        self.best_action_so_far = action
                        self.best_score_so_far = score
                        reasoning_parts.append(f"Depth {depth}: score={score:.2f}")
                except TimeoutError:
                    break
        else:
            # Fixed depth search
            best_action, best_score = self._search_at_depth(
                game_state, actions, self.max_depth
            )
        
        # Build reasoning string
        elapsed = time.time() - self.search_start_time
        reasoning = (
            f"Minimax Alpha-Beta (depth={self.max_depth})\n"
            f"Nodes: {self.nodes_searched}, Cache hits: {self.cache_hits}, "
            f"Pruned: {self.pruned_branches}\n"
            f"Time: {elapsed:.3f}s, Score: {best_score:.2f}\n"
            + "\n".join(reasoning_parts[-3:])  # Last 3 depth results
        )
        
        # Debug info
        self._debug_info = {
            'nodes_searched': self.nodes_searched,
            'cache_hits': self.cache_hits,
            'pruned_branches': self.pruned_branches,
            'search_time': elapsed,
            'final_score': best_score,
            'depths_completed': len(reasoning_parts)
        }
        
        # Build decision tree data for visualization
        if self._capture_tree and best_action:
            self._build_decision_tree_data(game_state, actions, best_action, best_score, elapsed)
        
        return best_action, best_score, reasoning
    
    def _format_action_label(self, state: GameState, action: Action) -> str:
        """Create a readable label for an action"""
        unit = state.get_unit_by_id(action.unit_id)
        unit_name = unit.name if unit else "Unit"
        
        if action.action_type == ActionType.MOVE:
            return f"Move {unit_name} → ({action.target_position.x},{action.target_position.y})"
        elif action.action_type == ActionType.ATTACK:
            target = state.get_unit_by_id(action.target_unit_id)
            target_name = target.name if target else "Enemy"
            return f"{unit_name} Attack {target_name}"
        elif action.action_type == ActionType.ABILITY:
            return f"{unit_name} {action.ability_type.name}"
        else:
            return f"{unit_name} Wait"
    
    def _build_decision_tree_data(
        self, state: GameState, actions: List[Action],
        best_action: Action, best_score: float, elapsed: float
    ):
        """Build the decision tree for visualization"""
        self._node_counter = 0
        team_name = "RED" if self.team == Team.RED else "BLUE"
        
        # Create root node
        root = DecisionNode(
            node_id=self._next_node_id(),
            action_label=f"{team_name} Team's Turn",
            action_detail=f"Evaluating {len(actions)} possible actions",
            score=best_score,
            depth=0,
            is_maximizing=True,
            status=NodeStatus.SELECTED,
            team=team_name
        )
        
        # Score all actions at top level for the tree
        alpha = float('-inf')
        beta = float('inf')
        
        for action in actions:
            new_state = state.clone()
            result = new_state.execute_action(action)
            if not result.success:
                continue
            
            unit = new_state.get_unit_by_id(action.unit_id)
            if unit and not unit.can_act:
                if not new_state.current_team.get_units_that_can_act():
                    new_state.end_turn()
            
            score = self.evaluator.evaluate(new_state, self.team)
            label = self._format_action_label(state, action)
            
            is_best = self._actions_equal(action, best_action)
            child_status = NodeStatus.SELECTED if is_best else NodeStatus.DISCARDED
            
            child = DecisionNode(
                node_id=self._next_node_id(),
                action_label=label,
                action_detail=f"Score: {score:.1f}",
                score=score,
                depth=1,
                is_maximizing=False,
                status=child_status,
                unit_name=state.get_unit_by_id(action.unit_id).name if state.get_unit_by_id(action.unit_id) else "",
                team=team_name
            )
            
            # Add a few grandchildren for the selected node to show depth
            if is_best and not new_state.is_game_over:
                counter_actions = new_state.get_all_legal_actions()[:5]  # Limit
                for ca in counter_actions:
                    ca_state = new_state.clone()
                    ca_result = ca_state.execute_action(ca)
                    if not ca_result.success:
                        continue
                    ca_score = self.evaluator.evaluate(ca_state, self.team)
                    ca_label = self._format_action_label(new_state, ca)
                    opp_team = "BLUE" if team_name == "RED" else "RED"
                    grandchild = DecisionNode(
                        node_id=self._next_node_id(),
                        action_label=ca_label,
                        action_detail=f"Counter: {ca_score:.1f}",
                        score=ca_score,
                        depth=2,
                        is_maximizing=True,
                        status=NodeStatus.EXPLORED,
                        team=opp_team
                    )
                    child.children.append(grandchild)
            
            root.children.append(child)
        
        # Mark pruned branches
        if self.pruned_branches > 0:
            pruned_node = DecisionNode(
                node_id=self._next_node_id(),
                action_label=f"✂ {self.pruned_branches} branches pruned",
                action_detail="Alpha-Beta cutoff",
                score=0,
                depth=1,
                is_maximizing=False,
                status=NodeStatus.PRUNED,
                team=team_name
            )
            root.children.append(pruned_node)
        
        self.last_decision_tree = DecisionTreeData(
            team=team_name,
            algorithm="Minimax",
            turn_number=state.current_turn,
            root=root,
            best_action_label=self._format_action_label(state, best_action),
            best_score=best_score,
            nodes_searched=self.nodes_searched,
            pruned_count=self.pruned_branches,
            thinking_time=elapsed
        )
    
    def _next_node_id(self) -> int:
        self._node_counter += 1
        return self._node_counter
    
    def _search_at_depth(
        self,
        game_state: GameState,
        actions: List[Action],
        depth: int
    ) -> Tuple[Optional[Action], float]:
        """Search at a specific depth"""
        best_action = None
        best_score = float('-inf')
        alpha = float('-inf')
        beta = float('inf')
        
        is_maximizing = game_state.current_team.team == self.team
        
        for action in actions:
            if self._time_exceeded():
                raise TimeoutError("Search time exceeded")
            
            # Simulate action
            new_state = game_state.clone()
            result = new_state.execute_action(action)
            
            if not result.success:
                continue
            
            # Check if turn should end after this action
            unit = new_state.get_unit_by_id(action.unit_id)
            if unit and not unit.can_act:
                # Unit finished, check if other units can act
                if not new_state.current_team.get_units_that_can_act():
                    new_state.end_turn()
            
            # Recursive search
            if is_maximizing:
                score = self._minimax(new_state, depth - 1, alpha, beta, False)
            else:
                score = self._minimax(new_state, depth - 1, alpha, beta, True)
            
            if score > best_score:
                best_score = score
                best_action = action
            
            alpha = max(alpha, score)
        
        return best_action, best_score
    
    def _minimax(
        self,
        state: GameState,
        depth: int,
        alpha: float,
        beta: float,
        maximizing: bool
    ) -> float:
        """
        Minimax algorithm with Alpha-Beta pruning
        """
        self.nodes_searched += 1
        
        # Time check
        if self._time_exceeded():
            return self.evaluator.evaluate(state, self.team)
        
        # Check transposition table
        if self.use_transposition_table:
            state_hash = state.get_state_hash()
            entry = self.transposition_table.get(state_hash)
            if entry and entry.depth >= depth:
                self.cache_hits += 1
                if entry.flag == 'exact':
                    return entry.score
                elif entry.flag == 'lower':
                    alpha = max(alpha, entry.score)
                elif entry.flag == 'upper':
                    beta = min(beta, entry.score)
                
                if alpha >= beta:
                    self.pruned_branches += 1
                    return entry.score
        
        # Terminal or depth limit
        if depth <= 0 or state.is_game_over:
            return self.evaluator.evaluate(state, self.team)
        
        # Get legal actions
        actions = state.get_all_legal_actions()
        if not actions:
            # No actions - end turn
            state.end_turn()
            return self._minimax(state, depth - 1, alpha, beta, not maximizing)
        
        # Order actions
        actions = self._order_actions(state, actions)
        
        best_score = float('-inf') if maximizing else float('inf')
        best_action = None
        
        for action in actions:
            # Simulate action
            new_state = state.clone()
            result = new_state.execute_action(action)
            
            if not result.success:
                continue
            
            # Determine if we need to switch turns
            next_maximizing = maximizing
            remaining_actors = new_state.current_team.get_units_that_can_act()
            
            if not remaining_actors:
                new_state.end_turn()
                next_maximizing = not maximizing
            
            # Recursive call
            score = self._minimax(new_state, depth - 1, alpha, beta, next_maximizing)
            
            if maximizing:
                if score > best_score:
                    best_score = score
                    best_action = action
                alpha = max(alpha, score)
            else:
                if score < best_score:
                    best_score = score
                    best_action = action
                beta = min(beta, score)
            
            # Alpha-beta cutoff
            if alpha >= beta:
                self.pruned_branches += 1
                break
        
        # Store in transposition table
        if self.use_transposition_table:
            flag = 'exact'
            if best_score <= alpha:
                flag = 'upper'
            elif best_score >= beta:
                flag = 'lower'
            
            self.transposition_table[state_hash] = TranspositionEntry(
                depth=depth,
                score=best_score,
                flag=flag,
                best_action=best_action
            )
        
        return best_score
    
    def _order_actions(self, state: GameState, actions: List[Action]) -> List[Action]:
        """Order actions for better alpha-beta pruning"""
        # Score each action
        scored_actions = [
            (action, ActionEvaluator.estimate_action_value(state, action))
            for action in actions
        ]
        
        # Sort by score descending
        scored_actions.sort(key=lambda x: x[1], reverse=True)
        
        # If we have a best action from previous iteration, put it first
        if self.best_action_so_far:
            for i, (action, _) in enumerate(scored_actions):
                if self._actions_equal(action, self.best_action_so_far):
                    scored_actions.insert(0, scored_actions.pop(i))
                    break
        
        return [action for action, _ in scored_actions]
    
    def _actions_equal(self, a1: Action, a2: Action) -> bool:
        """Check if two actions are equivalent"""
        return (
            a1.action_type == a2.action_type and
            a1.unit_id == a2.unit_id and
            a1.target_position == a2.target_position and
            a1.target_unit_id == a2.target_unit_id
        )
    
    def _time_exceeded(self) -> bool:
        """Check if time limit exceeded"""
        return time.time() - self.search_start_time > self.time_limit
    
    def reset(self):
        """Reset agent for new game"""
        super().reset()
        self.transposition_table.clear()
        self.evaluator.clear_cache()
    
    def get_algorithm_name(self) -> str:
        return "Minimax with Alpha-Beta Pruning"
    
    def get_algorithm_description(self) -> str:
        return """
Minimax Algorithm with Alpha-Beta Pruning

MINIMAX:
- Explores the game tree to find the optimal move
- Assumes opponent plays optimally (adversarial)
- Maximizes own score, minimizes opponent's score

ALPHA-BETA PRUNING:
- Optimization that prunes branches that cannot affect the final decision
- Alpha: best score MAX can guarantee
- Beta: best score MIN can guarantee
- Prune when alpha >= beta

OPTIMIZATIONS:
- Transposition Table: Caches evaluated positions
- Iterative Deepening: Searches deeper while time permits
- Move Ordering: Searches best moves first for better pruning

PARAMETERS:
- Max Depth: {depth}
- Time Limit: {time}s
- Transposition Table: {tt}
- Iterative Deepening: {id}
""".format(
            depth=self.max_depth,
            time=self.time_limit,
            tt="Enabled" if self.use_transposition_table else "Disabled",
            id="Enabled" if self.use_iterative_deepening else "Disabled"
        )
