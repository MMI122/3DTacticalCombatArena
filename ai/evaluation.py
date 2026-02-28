"""
Position and Game State Evaluation Functions
Heuristics used by AI agents to evaluate game positions
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass

from core.game_state import GameState
from core.unit import Unit, Team, Position
from core.battlefield import Terrain


@dataclass
class EvaluationWeights:
    """Weights for evaluation components"""
    hp_weight: float = 1.0
    unit_count_weight: float = 50.0
    position_weight: float = 0.5
    threat_weight: float = 0.3
    mobility_weight: float = 0.2
    terrain_weight: float = 0.15
    formation_weight: float = 0.1


class Evaluator:
    """
    Evaluates game states for AI decision making
    Higher scores favor RED team, lower scores favor BLUE team
    """
    
    def __init__(self, weights: EvaluationWeights = None):
        self.weights = weights or EvaluationWeights()
        self._cache: Dict[int, float] = {}
    
    def evaluate(self, state: GameState, for_team: Team = Team.RED) -> float:
        """
        Evaluate a game state
        
        Args:
            state: Game state to evaluate
            for_team: Team perspective for evaluation
            
        Returns:
            Float score (positive favors for_team, negative favors opponent)
        """
        # Check cache
        state_hash = state.get_state_hash()
        if state_hash in self._cache:
            score = self._cache[state_hash]
            return score if for_team == Team.RED else -score
        
        # Terminal state check
        if state.is_game_over:
            if state.winner == Team.RED:
                score = 10000
            elif state.winner == Team.BLUE:
                score = -10000
            else:
                score = 0
            self._cache[state_hash] = score
            return score if for_team == Team.RED else -score
        
        # Calculate components
        hp_score = self._evaluate_hp(state)
        unit_score = self._evaluate_unit_count(state)
        position_score = self._evaluate_positions(state)
        threat_score = self._evaluate_threats(state)
        mobility_score = self._evaluate_mobility(state)
        terrain_score = self._evaluate_terrain_advantage(state)
        formation_score = self._evaluate_formation(state)
        
        # Combine scores
        total = (
            hp_score * self.weights.hp_weight +
            unit_score * self.weights.unit_count_weight +
            position_score * self.weights.position_weight +
            threat_score * self.weights.threat_weight +
            mobility_score * self.weights.mobility_weight +
            terrain_score * self.weights.terrain_weight +
            formation_score * self.weights.formation_weight
        )
        
        self._cache[state_hash] = total
        return total if for_team == Team.RED else -total
    
    def _evaluate_hp(self, state: GameState) -> float:
        """Evaluate HP difference"""
        red_hp = state.red_team.total_hp
        blue_hp = state.blue_team.total_hp
        
        red_max = state.red_team.max_total_hp
        blue_max = state.blue_team.max_total_hp
        
        # Normalize to percentage
        red_pct = red_hp / red_max if red_max > 0 else 0
        blue_pct = blue_hp / blue_max if blue_max > 0 else 0
        
        return (red_pct - blue_pct) * 100
    
    def _evaluate_unit_count(self, state: GameState) -> float:
        """Evaluate unit count difference"""
        red_alive = len(state.red_team.alive_units)
        blue_alive = len(state.blue_team.alive_units)
        return float(red_alive - blue_alive)
    
    def _evaluate_positions(self, state: GameState) -> float:
        """Evaluate positional advantage (map control)"""
        red_control = 0.0
        blue_control = 0.0
        
        center_x = state.battlefield.width / 2
        center_y = state.battlefield.height / 2
        
        for unit in state.red_team.alive_units:
            # Reward being closer to center
            dist_to_center = abs(unit.position.x - center_x) + abs(unit.position.y - center_y)
            max_dist = center_x + center_y
            red_control += (max_dist - dist_to_center) / max_dist
        
        for unit in state.blue_team.alive_units:
            dist_to_center = abs(unit.position.x - center_x) + abs(unit.position.y - center_y)
            max_dist = center_x + center_y
            blue_control += (max_dist - dist_to_center) / max_dist
        
        return (red_control - blue_control) * 10
    
    def _evaluate_threats(self, state: GameState) -> float:
        """Evaluate threat levels"""
        red_threat = 0.0
        blue_threat = 0.0
        
        # Count how many enemies each unit can attack
        for unit in state.red_team.alive_units:
            enemies_in_range = state.battlefield.get_enemies_in_range(unit)
            red_threat += len(enemies_in_range) * unit.effective_attack / 100
        
        for unit in state.blue_team.alive_units:
            enemies_in_range = state.battlefield.get_enemies_in_range(unit)
            blue_threat += len(enemies_in_range) * unit.effective_attack / 100
        
        return (red_threat - blue_threat) * 10
    
    def _evaluate_mobility(self, state: GameState) -> float:
        """Evaluate movement options"""
        red_mobility = 0
        blue_mobility = 0
        
        for unit in state.red_team.alive_units:
            red_mobility += len(state.battlefield.get_reachable_positions(unit))
        
        for unit in state.blue_team.alive_units:
            blue_mobility += len(state.battlefield.get_reachable_positions(unit))
        
        return float(red_mobility - blue_mobility)
    
    def _evaluate_terrain_advantage(self, state: GameState) -> float:
        """Evaluate terrain bonuses"""
        red_terrain = 0.0
        blue_terrain = 0.0
        
        for unit in state.red_team.alive_units:
            cell = state.battlefield.get_cell(unit.position)
            if cell:
                red_terrain += cell.defense_modifier + cell.attack_modifier
        
        for unit in state.blue_team.alive_units:
            cell = state.battlefield.get_cell(unit.position)
            if cell:
                blue_terrain += cell.defense_modifier + cell.attack_modifier
        
        return (red_terrain - blue_terrain) * 5
    
    def _evaluate_formation(self, state: GameState) -> float:
        """Evaluate unit formation (staying together but not too clustered)"""
        def formation_score(units: List[Unit]) -> float:
            if len(units) < 2:
                return 0
            
            score = 0.0
            for i, unit1 in enumerate(units):
                for unit2 in units[i+1:]:
                    dist = unit1.position.distance_to(unit2.position)
                    # Ideal distance is 2-4 cells
                    if 2 <= dist <= 4:
                        score += 1
                    elif dist < 2:
                        score -= 0.5  # Too close
                    elif dist > 6:
                        score -= 0.5  # Too far
            
            return score
        
        red_formation = formation_score(state.red_team.alive_units)
        blue_formation = formation_score(state.blue_team.alive_units)
        
        return red_formation - blue_formation
    
    def clear_cache(self):
        """Clear the evaluation cache"""
        self._cache.clear()


class ActionEvaluator:
    """Evaluates individual actions for move ordering"""
    
    @staticmethod
    def estimate_action_value(state: GameState, action) -> float:
        """Quick estimation of action value for move ordering"""
        from core.game_state import ActionType
        
        score = 0.0
        
        if action.action_type == ActionType.ATTACK:
            # Attacks on low HP units are valuable
            target = state.get_unit_by_id(action.target_unit_id)
            if target:
                # Value killing blows highly
                unit = state.get_unit_by_id(action.unit_id)
                if unit and target.current_hp <= unit.effective_attack:
                    score += 100  # Kill shot
                else:
                    score += 50  # Regular attack
                
                # Prioritize low HP targets
                score += (1 - target.hp_percentage) * 20
        
        elif action.action_type == ActionType.ABILITY:
            score += 40  # Abilities are generally good
        
        elif action.action_type == ActionType.MOVE:
            # Evaluate positional improvement
            unit = state.get_unit_by_id(action.unit_id)
            if unit and action.target_position:
                # Moving toward enemies
                enemies = state.opposing_team.alive_units
                if enemies:
                    closest_enemy_dist = min(
                        action.target_position.distance_to(e.position) 
                        for e in enemies
                    )
                    score += 10 - closest_enemy_dist
                
                # Moving to better terrain
                cell = state.battlefield.get_cell(action.target_position)
                if cell:
                    score += cell.defense_modifier * 2
        
        elif action.action_type == ActionType.WAIT:
            score -= 10  # Waiting is usually not optimal
        
        return score
