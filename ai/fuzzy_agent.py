"""
Fuzzy Logic AI Agent
Production-grade implementation using fuzzy inference system
"""

from typing import Tuple, Optional, List, Dict, Any
import numpy as np
from dataclasses import dataclass

from .base_agent import BaseAgent
from .decision_tree_data import DecisionTreeData, FuzzyDecisionInfo
from core.game_state import GameState, Action, ActionType
from core.unit import Team, Unit, Position
from core.battlefield import Terrain
from config.settings import get_config


@dataclass
class FuzzySet:
    """Represents a fuzzy set with membership function"""
    name: str
    points: List[Tuple[float, float]]  # (x, membership) pairs
    
    def membership(self, x: float) -> float:
        """Calculate membership value for input x"""
        if not self.points:
            return 0.0
        
        # Handle edge cases
        if x <= self.points[0][0]:
            return self.points[0][1]
        if x >= self.points[-1][0]:
            return self.points[-1][1]
        
        # Linear interpolation between points
        for i in range(len(self.points) - 1):
            x1, y1 = self.points[i]
            x2, y2 = self.points[i + 1]
            if x1 <= x <= x2:
                if x2 == x1:
                    return y1
                return y1 + (y2 - y1) * (x - x1) / (x2 - x1)
        
        return 0.0


@dataclass
class FuzzyRule:
    """Represents a fuzzy IF-THEN rule"""
    conditions: Dict[str, str]  # variable_name -> fuzzy_set_name
    conclusion: Dict[str, str]  # output_variable -> fuzzy_set_name
    weight: float = 1.0


class FuzzyVariable:
    """A fuzzy variable with multiple fuzzy sets"""
    
    def __init__(self, name: str, min_val: float, max_val: float):
        self.name = name
        self.min_val = min_val
        self.max_val = max_val
        self.sets: Dict[str, FuzzySet] = {}
    
    def add_set(self, name: str, points: List[Tuple[float, float]]):
        """Add a fuzzy set to this variable"""
        self.sets[name] = FuzzySet(name, points)
    
    def fuzzify(self, value: float) -> Dict[str, float]:
        """Get membership values for all sets"""
        return {name: fs.membership(value) for name, fs in self.sets.items()}


class FuzzyInferenceSystem:
    """
    Mamdani-style Fuzzy Inference System
    Used for decision making in the Fuzzy AI agent
    """
    
    def __init__(self):
        self.input_variables: Dict[str, FuzzyVariable] = {}
        self.output_variables: Dict[str, FuzzyVariable] = {}
        self.rules: List[FuzzyRule] = []
    
    def add_input_variable(self, var: FuzzyVariable):
        """Add an input variable"""
        self.input_variables[var.name] = var
    
    def add_output_variable(self, var: FuzzyVariable):
        """Add an output variable"""
        self.output_variables[var.name] = var
    
    def add_rule(self, rule: FuzzyRule):
        """Add a fuzzy rule"""
        self.rules.append(rule)
    
    def infer(self, inputs: Dict[str, float]) -> Dict[str, float]:
        """
        Perform fuzzy inference
        
        Args:
            inputs: Dictionary of input variable values
            
        Returns:
            Dictionary of defuzzified output values
        """
        # Step 1: Fuzzify inputs
        fuzzified = {}
        for var_name, value in inputs.items():
            if var_name in self.input_variables:
                fuzzified[var_name] = self.input_variables[var_name].fuzzify(value)
        
        # Step 2: Apply rules
        rule_outputs: Dict[str, List[Tuple[float, FuzzySet]]] = {
            name: [] for name in self.output_variables
        }
        
        for rule in self.rules:
            # Calculate rule activation (AND = min)
            activation = 1.0
            for var_name, set_name in rule.conditions.items():
                if var_name in fuzzified and set_name in fuzzified[var_name]:
                    activation = min(activation, fuzzified[var_name][set_name])
            
            activation *= rule.weight
            
            # Apply to outputs
            for out_var, out_set in rule.conclusion.items():
                if out_var in self.output_variables:
                    fuzzy_set = self.output_variables[out_var].sets.get(out_set)
                    if fuzzy_set:
                        rule_outputs[out_var].append((activation, fuzzy_set))
        
        # Step 3: Aggregate and defuzzify (centroid method)
        outputs = {}
        for var_name, activations in rule_outputs.items():
            if not activations:
                outputs[var_name] = 0.0
                continue
            
            var = self.output_variables[var_name]
            outputs[var_name] = self._defuzzify_centroid(var, activations)
        
        return outputs
    
    def _defuzzify_centroid(
        self,
        var: FuzzyVariable,
        activations: List[Tuple[float, FuzzySet]]
    ) -> float:
        """Defuzzify using centroid method"""
        # Sample points across the output range
        num_samples = 100
        x_vals = np.linspace(var.min_val, var.max_val, num_samples)
        
        # Calculate aggregated membership
        aggregated = np.zeros(num_samples)
        for activation, fuzzy_set in activations:
            for i, x in enumerate(x_vals):
                membership = min(activation, fuzzy_set.membership(x))
                aggregated[i] = max(aggregated[i], membership)
        
        # Calculate centroid
        total = np.sum(aggregated)
        if total == 0:
            return (var.min_val + var.max_val) / 2
        
        centroid = np.sum(x_vals * aggregated) / total
        return float(centroid)


class FuzzyLogicAgent(BaseAgent):
    """
    AI agent using Fuzzy Logic for decision making
    
    Uses fuzzy rules to evaluate:
    - Threat assessment
    - Aggression level
    - Target prioritization
    - Positioning value
    """
    
    def __init__(self, team: Optional[Team] = None):
        super().__init__("Fuzzy Logic AI", team)
        
        config = get_config()
        self.aggression_base = config.ai.fuzzy_aggression_base
        
        # Build fuzzy inference systems
        self.threat_fis = self._build_threat_system()
        self.action_fis = self._build_action_system()
        self.target_fis = self._build_target_system()
        
        # Statistics
        self.rules_fired = 0
        self.decisions_made = 0
        
        # Decision tree capture
        self.last_decision_tree: Optional[DecisionTreeData] = None
    
    def _build_threat_system(self) -> FuzzyInferenceSystem:
        """Build fuzzy system for threat assessment"""
        fis = FuzzyInferenceSystem()
        
        # Input: Enemy HP percentage (0-100)
        enemy_hp = FuzzyVariable("enemy_hp", 0, 100)
        enemy_hp.add_set("critical", [(0, 1), (20, 1), (35, 0)])
        enemy_hp.add_set("low", [(15, 0), (30, 1), (50, 1), (65, 0)])
        enemy_hp.add_set("medium", [(45, 0), (60, 1), (75, 1), (90, 0)])
        enemy_hp.add_set("high", [(70, 0), (85, 1), (100, 1)])
        fis.add_input_variable(enemy_hp)
        
        # Input: Enemy attack power (0-100 normalized)
        enemy_attack = FuzzyVariable("enemy_attack", 0, 100)
        enemy_attack.add_set("weak", [(0, 1), (25, 1), (40, 0)])
        enemy_attack.add_set("moderate", [(30, 0), (50, 1), (70, 0)])
        enemy_attack.add_set("strong", [(60, 0), (80, 1), (100, 1)])
        fis.add_input_variable(enemy_attack)
        
        # Input: Distance to enemy (1-10)
        distance = FuzzyVariable("distance", 1, 10)
        distance.add_set("close", [(1, 1), (2, 1), (4, 0)])
        distance.add_set("medium", [(3, 0), (5, 1), (7, 0)])
        distance.add_set("far", [(6, 0), (8, 1), (10, 1)])
        fis.add_input_variable(distance)
        
        # Output: Threat level (0-100)
        threat = FuzzyVariable("threat", 0, 100)
        threat.add_set("minimal", [(0, 1), (20, 1), (35, 0)])
        threat.add_set("low", [(25, 0), (40, 1), (55, 0)])
        threat.add_set("moderate", [(45, 0), (60, 1), (75, 0)])
        threat.add_set("high", [(65, 0), (80, 1), (90, 0)])
        threat.add_set("critical", [(80, 0), (90, 1), (100, 1)])
        fis.add_output_variable(threat)
        
        # Rules
        rules = [
            # Close enemies with high attack are critical threats
            FuzzyRule({"distance": "close", "enemy_attack": "strong"}, {"threat": "critical"}, 1.0),
            FuzzyRule({"distance": "close", "enemy_attack": "moderate"}, {"threat": "high"}, 0.9),
            FuzzyRule({"distance": "close", "enemy_attack": "weak"}, {"threat": "moderate"}, 0.8),
            
            # Medium distance threats
            FuzzyRule({"distance": "medium", "enemy_attack": "strong"}, {"threat": "high"}, 0.9),
            FuzzyRule({"distance": "medium", "enemy_attack": "moderate"}, {"threat": "moderate"}, 0.8),
            FuzzyRule({"distance": "medium", "enemy_attack": "weak"}, {"threat": "low"}, 0.7),
            
            # Far enemies are less threatening
            FuzzyRule({"distance": "far", "enemy_attack": "strong"}, {"threat": "moderate"}, 0.7),
            FuzzyRule({"distance": "far", "enemy_attack": "moderate"}, {"threat": "low"}, 0.6),
            FuzzyRule({"distance": "far", "enemy_attack": "weak"}, {"threat": "minimal"}, 0.5),
            
            # Low HP enemies are lower priority threats (we're winning)
            FuzzyRule({"enemy_hp": "critical"}, {"threat": "minimal"}, 0.6),
            FuzzyRule({"enemy_hp": "low", "distance": "far"}, {"threat": "low"}, 0.5),
        ]
        
        for rule in rules:
            fis.add_rule(rule)
        
        return fis
    
    def _build_action_system(self) -> FuzzyInferenceSystem:
        """Build fuzzy system for action selection"""
        fis = FuzzyInferenceSystem()
        
        # Input: Own HP percentage
        own_hp = FuzzyVariable("own_hp", 0, 100)
        own_hp.add_set("critical", [(0, 1), (20, 1), (35, 0)])
        own_hp.add_set("low", [(25, 0), (40, 1), (55, 0)])
        own_hp.add_set("healthy", [(45, 0), (70, 1), (100, 1)])
        fis.add_input_variable(own_hp)
        
        # Input: Team HP advantage (-100 to 100)
        team_advantage = FuzzyVariable("team_advantage", -100, 100)
        team_advantage.add_set("losing", [(-100, 1), (-50, 1), (-10, 0)])
        team_advantage.add_set("even", [(-30, 0), (0, 1), (30, 0)])
        team_advantage.add_set("winning", [(10, 0), (50, 1), (100, 1)])
        fis.add_input_variable(team_advantage)
        
        # Input: Enemies in range (0-5)
        enemies_in_range = FuzzyVariable("enemies_in_range", 0, 5)
        enemies_in_range.add_set("none", [(0, 1), (0.5, 0)])
        enemies_in_range.add_set("few", [(0, 0), (1, 1), (2, 1), (3, 0)])
        enemies_in_range.add_set("many", [(2, 0), (3, 1), (5, 1)])
        fis.add_input_variable(enemies_in_range)
        
        # Output: Aggression level (0-100)
        aggression = FuzzyVariable("aggression", 0, 100)
        aggression.add_set("defensive", [(0, 1), (25, 1), (40, 0)])
        aggression.add_set("balanced", [(30, 0), (50, 1), (70, 0)])
        aggression.add_set("aggressive", [(60, 0), (80, 1), (100, 1)])
        fis.add_output_variable(aggression)
        
        # Rules for aggression
        rules = [
            # When winning and healthy, be aggressive
            FuzzyRule({"team_advantage": "winning", "own_hp": "healthy"}, {"aggression": "aggressive"}, 1.0),
            FuzzyRule({"team_advantage": "winning", "own_hp": "low"}, {"aggression": "balanced"}, 0.8),
            
            # When even, base on HP
            FuzzyRule({"team_advantage": "even", "own_hp": "healthy"}, {"aggression": "balanced"}, 0.9),
            FuzzyRule({"team_advantage": "even", "own_hp": "low"}, {"aggression": "defensive"}, 0.8),
            FuzzyRule({"team_advantage": "even", "own_hp": "critical"}, {"aggression": "defensive"}, 1.0),
            
            # When losing, be careful
            FuzzyRule({"team_advantage": "losing", "own_hp": "healthy"}, {"aggression": "balanced"}, 0.9),
            FuzzyRule({"team_advantage": "losing", "own_hp": "low"}, {"aggression": "defensive"}, 0.9),
            FuzzyRule({"team_advantage": "losing", "own_hp": "critical"}, {"aggression": "defensive"}, 1.0),
            
            # Enemies in range affects aggression
            FuzzyRule({"enemies_in_range": "many", "own_hp": "healthy"}, {"aggression": "aggressive"}, 0.9),
            FuzzyRule({"enemies_in_range": "many", "own_hp": "low"}, {"aggression": "defensive"}, 0.8),
            FuzzyRule({"enemies_in_range": "none"}, {"aggression": "balanced"}, 0.5),
        ]
        
        for rule in rules:
            fis.add_rule(rule)
        
        return fis
    
    def _build_target_system(self) -> FuzzyInferenceSystem:
        """Build fuzzy system for target prioritization"""
        fis = FuzzyInferenceSystem()
        
        # Input: Target HP percentage
        target_hp = FuzzyVariable("target_hp", 0, 100)
        target_hp.add_set("critical", [(0, 1), (15, 1), (30, 0)])
        target_hp.add_set("low", [(20, 0), (35, 1), (50, 0)])
        target_hp.add_set("medium", [(40, 0), (60, 1), (80, 0)])
        target_hp.add_set("high", [(70, 0), (85, 1), (100, 1)])
        fis.add_input_variable(target_hp)
        
        # Input: Target damage potential (normalized 0-100)
        target_damage = FuzzyVariable("target_damage", 0, 100)
        target_damage.add_set("low", [(0, 1), (30, 1), (50, 0)])
        target_damage.add_set("medium", [(40, 0), (60, 1), (80, 0)])
        target_damage.add_set("high", [(70, 0), (85, 1), (100, 1)])
        fis.add_input_variable(target_damage)
        
        # Input: Can we kill in one hit? (0 or 1)
        can_kill = FuzzyVariable("can_kill", 0, 1)
        can_kill.add_set("no", [(0, 1), (0.5, 0)])
        can_kill.add_set("yes", [(0.5, 0), (1, 1)])
        fis.add_input_variable(can_kill)
        
        # Output: Target priority (0-100)
        priority = FuzzyVariable("priority", 0, 100)
        priority.add_set("low", [(0, 1), (25, 1), (40, 0)])
        priority.add_set("medium", [(30, 0), (50, 1), (70, 0)])
        priority.add_set("high", [(60, 0), (80, 1), (90, 0)])
        priority.add_set("critical", [(80, 0), (95, 1), (100, 1)])
        fis.add_output_variable(priority)
        
        # Rules
        rules = [
            # Always prioritize kills
            FuzzyRule({"can_kill": "yes"}, {"priority": "critical"}, 1.0),
            
            # High damage dealers are priority
            FuzzyRule({"target_damage": "high", "target_hp": "low"}, {"priority": "critical"}, 0.95),
            FuzzyRule({"target_damage": "high", "target_hp": "medium"}, {"priority": "high"}, 0.9),
            FuzzyRule({"target_damage": "high", "target_hp": "high"}, {"priority": "high"}, 0.85),
            
            # Low HP targets are opportunities
            FuzzyRule({"target_hp": "critical"}, {"priority": "high"}, 0.9),
            FuzzyRule({"target_hp": "low", "target_damage": "medium"}, {"priority": "high"}, 0.8),
            
            # Medium priority targets
            FuzzyRule({"target_damage": "medium", "target_hp": "medium"}, {"priority": "medium"}, 0.7),
            FuzzyRule({"target_damage": "low", "target_hp": "low"}, {"priority": "medium"}, 0.6),
            
            # Low priority
            FuzzyRule({"target_damage": "low", "target_hp": "high"}, {"priority": "low"}, 0.5),
        ]
        
        for rule in rules:
            fis.add_rule(rule)
        
        return fis
    
    def get_action(self, game_state: GameState) -> Tuple[Optional[Action], float, str]:
        """
        Get the best action using fuzzy logic reasoning
        """
        self.decisions_made += 1
        
        actions = game_state.get_all_legal_actions()
        if not actions:
            return None, 0.0, "No actions available"
        
        # Evaluate global situation
        team_hp_pct = (game_state.current_team.total_hp / 
                      game_state.current_team.max_total_hp * 100)
        enemy_hp_pct = (game_state.opposing_team.total_hp / 
                       game_state.opposing_team.max_total_hp * 100)
        team_advantage = team_hp_pct - enemy_hp_pct
        
        # Score each action
        scored_actions: List[Tuple[Action, float, str]] = []
        
        for action in actions:
            score, reasoning = self._evaluate_action(game_state, action, team_advantage)
            scored_actions.append((action, score, reasoning))
        
        # Sort by score descending
        scored_actions.sort(key=lambda x: x[1], reverse=True)
        
        best_action, best_score, best_reasoning = scored_actions[0]
        
        # Build full reasoning
        reasoning = (
            f"Fuzzy Logic Decision\n"
            f"Team Advantage: {team_advantage:.1f}%\n"
            f"Actions Evaluated: {len(actions)}\n"
            f"Best Score: {best_score:.2f}\n"
            f"Reasoning: {best_reasoning}"
        )
        
        self._debug_info = {
            'team_advantage': team_advantage,
            'actions_evaluated': len(actions),
            'best_score': best_score,
            'top_3_actions': [(str(a), s) for a, s, _ in scored_actions[:3]]
        }
        
        # Build decision data for visualization
        fuzzy_decisions = []
        for action, score, reason in scored_actions:
            unit = game_state.get_unit_by_id(action.unit_id)
            unit_name = unit.name if unit else "Unit"
            
            if action.action_type == ActionType.MOVE:
                label = f"Move {unit_name} → ({action.target_position.x},{action.target_position.y})"
            elif action.action_type == ActionType.ATTACK:
                target = game_state.get_unit_by_id(action.target_unit_id)
                target_name = target.name if target else "Enemy"
                label = f"{unit_name} Attack {target_name}"
            elif action.action_type == ActionType.ABILITY:
                label = f"{unit_name} {action.ability_type.name}"
            else:
                label = f"{unit_name} Wait"
            
            fd = FuzzyDecisionInfo(
                action_label=label,
                score=score,
                reasoning=reason,
                aggression=50.0,
                is_selected=(action == best_action),
                own_hp_pct=team_hp_pct,
                team_advantage=team_advantage,
                enemies_in_range=0
            )
            fuzzy_decisions.append(fd)
        
        team_name = "RED" if self.team == Team.RED else "BLUE"
        self.last_decision_tree = DecisionTreeData(
            team=team_name,
            algorithm="Fuzzy",
            turn_number=game_state.current_turn,
            fuzzy_decisions=fuzzy_decisions,
            best_action_label=fuzzy_decisions[0].action_label if fuzzy_decisions else "",
            best_score=best_score,
            nodes_searched=len(actions),
            thinking_time=0.0
        )
        
        return best_action, best_score, reasoning
    
    def _evaluate_action(
        self,
        state: GameState,
        action: Action,
        team_advantage: float
    ) -> Tuple[float, str]:
        """Evaluate a single action using fuzzy logic"""
        unit = state.get_unit_by_id(action.unit_id)
        if not unit:
            return 0.0, "Invalid unit"
        
        score = 0.0
        reasoning_parts = []
        
        # Get aggression level
        enemies_in_range = len(state.battlefield.get_enemies_in_range(unit))
        action_inputs = {
            "own_hp": unit.hp_percentage * 100,
            "team_advantage": team_advantage,
            "enemies_in_range": enemies_in_range
        }
        action_output = self.action_fis.infer(action_inputs)
        aggression = action_output.get("aggression", 50)
        
        if action.action_type == ActionType.ATTACK:
            target = state.get_unit_by_id(action.target_unit_id)
            if target:
                # Evaluate target priority
                can_kill = 1.0 if target.current_hp <= unit.effective_attack else 0.0
                target_inputs = {
                    "target_hp": target.hp_percentage * 100,
                    "target_damage": target.effective_attack / 50 * 100,  # Normalize
                    "can_kill": can_kill
                }
                target_output = self.target_fis.infer(target_inputs)
                priority = target_output.get("priority", 50)
                
                # Combine with aggression
                score = priority * (0.5 + aggression / 200)
                
                if can_kill:
                    reasoning_parts.append(f"KILL SHOT on {target.name}!")
                else:
                    reasoning_parts.append(f"Attack {target.name} (priority: {priority:.1f})")
        
        elif action.action_type == ActionType.MOVE:
            # Evaluate move based on aggression
            if action.target_position:
                # Distance to nearest enemy
                enemies = state.opposing_team.alive_units
                if enemies:
                    current_dist = min(
                        unit.position.distance_to(e.position) for e in enemies
                    )
                    new_dist = min(
                        action.target_position.distance_to(e.position) for e in enemies
                    )
                    
                    # If aggressive, reward closing distance
                    # If defensive, reward maintaining/increasing distance
                    if aggression > 60:
                        score = (current_dist - new_dist) * 10 + 30
                        reasoning_parts.append(f"Advancing (aggression: {aggression:.1f})")
                    elif aggression < 40:
                        score = (new_dist - current_dist) * 10 + 20
                        reasoning_parts.append(f"Retreating (aggression: {aggression:.1f})")
                    else:
                        # Balanced - prefer cover
                        cell = state.battlefield.get_cell(action.target_position)
                        if cell:
                            score = 30 + cell.defense_modifier * 10
                            reasoning_parts.append(f"Positioning (terrain bonus: {cell.defense_modifier})")
        
        elif action.action_type == ActionType.ABILITY:
            # Abilities are generally valuable
            score = 70 + aggression * 0.2
            reasoning_parts.append(f"Using ability {action.ability_type.name}")
        
        elif action.action_type == ActionType.WAIT:
            # Waiting is low priority unless defensive
            if aggression < 40:
                score = 25
                reasoning_parts.append("Holding position (defensive)")
            else:
                score = 5
                reasoning_parts.append("Waiting (suboptimal)")
        
        return score, "; ".join(reasoning_parts) if reasoning_parts else "No specific reasoning"
    
    def get_algorithm_name(self) -> str:
        return "Fuzzy Logic Controller"
    
    def get_algorithm_description(self) -> str:
        return """
Fuzzy Logic AI Controller

FUZZY INFERENCE:
- Uses linguistic variables (low, medium, high) instead of precise values
- Handles uncertainty and imprecise information naturally
- Rules are human-readable IF-THEN statements

FUZZY SYSTEMS:
1. Threat Assessment
   - Evaluates enemy danger based on HP, attack, distance
   - Outputs threat level (minimal to critical)

2. Action Selection
   - Considers own HP, team advantage, enemies in range
   - Outputs aggression level (defensive to aggressive)

3. Target Prioritization
   - Evaluates target HP, damage potential, kill possibility
   - Outputs target priority (low to critical)

DECISION PROCESS:
1. Fuzzify inputs (convert to membership values)
2. Apply rules (IF conditions THEN conclusions)
3. Aggregate rule outputs
4. Defuzzify (centroid method) to get crisp value
5. Score actions based on fuzzy outputs
6. Select highest scoring action

ADVANTAGES:
- Intuitive, human-like reasoning
- Handles gradual transitions smoothly
- Robust to noise and uncertainty
- Easy to tune and understand
"""
    
    def reset(self):
        """Reset agent state"""
        super().reset()
        self.rules_fired = 0
        self.decisions_made = 0
