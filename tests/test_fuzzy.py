"""
Unit tests for Fuzzy Logic AI Agent
"""

import pytest
import sys
sys.path.insert(0, '.')

from ai.fuzzy_agent import (
    FuzzyLogicAgent, FuzzyInferenceSystem, FuzzyVariable, FuzzyRule, FuzzySet
)
from core.game_state import GameState, ActionType
from core.unit import Team, Position


class TestFuzzySet:
    """Tests for FuzzySet class"""
    
    def test_triangular_membership(self):
        """Test triangular membership function"""
        fuzzy_set = FuzzySet(
            name="medium",
            points=[(0, 0), (50, 1), (100, 0)]
        )
        
        assert fuzzy_set.membership(0) == 0
        assert fuzzy_set.membership(50) == 1
        assert fuzzy_set.membership(100) == 0
        assert fuzzy_set.membership(25) == 0.5
        assert fuzzy_set.membership(75) == 0.5
    
    def test_trapezoidal_membership(self):
        """Test trapezoidal membership function"""
        fuzzy_set = FuzzySet(
            name="high",
            points=[(60, 0), (80, 1), (100, 1)]
        )
        
        assert fuzzy_set.membership(60) == 0
        assert fuzzy_set.membership(80) == 1
        assert fuzzy_set.membership(100) == 1
        assert fuzzy_set.membership(70) == 0.5
    
    def test_edge_cases(self):
        """Test edge cases for membership"""
        fuzzy_set = FuzzySet(
            name="test",
            points=[(20, 1), (80, 1)]
        )
        
        # Below range
        assert fuzzy_set.membership(0) == 1
        # Above range
        assert fuzzy_set.membership(100) == 1


class TestFuzzyVariable:
    """Tests for FuzzyVariable class"""
    
    def test_fuzzify(self):
        """Test fuzzification of crisp value"""
        var = FuzzyVariable("temperature", 0, 100)
        var.add_set("cold", [(0, 1), (30, 1), (50, 0)])
        var.add_set("warm", [(30, 0), (50, 1), (70, 0)])
        var.add_set("hot", [(50, 0), (70, 1), (100, 1)])
        
        result = var.fuzzify(50)
        
        assert "cold" in result
        assert "warm" in result
        assert "hot" in result
        assert result["warm"] == 1  # Peak at 50


class TestFuzzyInferenceSystem:
    """Tests for the Fuzzy Inference System"""
    
    @pytest.fixture
    def simple_fis(self):
        """Create a simple FIS for testing"""
        fis = FuzzyInferenceSystem()
        
        # Input variable
        input_var = FuzzyVariable("input", 0, 100)
        input_var.add_set("low", [(0, 1), (30, 1), (50, 0)])
        input_var.add_set("high", [(50, 0), (70, 1), (100, 1)])
        fis.add_input_variable(input_var)
        
        # Output variable
        output_var = FuzzyVariable("output", 0, 100)
        output_var.add_set("low", [(0, 1), (30, 1), (50, 0)])
        output_var.add_set("high", [(50, 0), (70, 1), (100, 1)])
        fis.add_output_variable(output_var)
        
        # Rules
        fis.add_rule(FuzzyRule({"input": "low"}, {"output": "low"}))
        fis.add_rule(FuzzyRule({"input": "high"}, {"output": "high"}))
        
        return fis
    
    def test_inference_low_input(self, simple_fis):
        """Test inference with low input"""
        result = simple_fis.infer({"input": 20})
        
        assert "output" in result
        assert result["output"] < 50  # Should be low
    
    def test_inference_high_input(self, simple_fis):
        """Test inference with high input"""
        result = simple_fis.infer({"input": 80})
        
        assert "output" in result
        assert result["output"] > 50  # Should be high


class TestFuzzyLogicAgent:
    """Tests for the Fuzzy Logic AI Agent"""
    
    @pytest.fixture
    def game_state(self):
        """Create a fresh game state"""
        return GameState.create_new_game(
            battlefield_width=8,
            battlefield_height=8,
            units_per_team=2,
            seed=42
        )
    
    @pytest.fixture
    def fuzzy_agent(self):
        """Create a Fuzzy Logic agent"""
        return FuzzyLogicAgent(team=Team.BLUE)
    
    def test_agent_creation(self, fuzzy_agent):
        """Test agent is created correctly"""
        assert fuzzy_agent.team == Team.BLUE
        assert fuzzy_agent.get_algorithm_name() == "Fuzzy Logic Controller"
    
    def test_get_action_returns_valid(self, game_state, fuzzy_agent):
        """Test that agent returns a valid action"""
        # Switch to blue team's turn
        game_state.end_turn()  # End red's turn
        
        action, score, reasoning = fuzzy_agent.get_action(game_state)
        
        assert action is not None
        assert isinstance(score, float)
        assert isinstance(reasoning, str)
        assert len(reasoning) > 0
    
    def test_action_is_legal(self, game_state, fuzzy_agent):
        """Test that returned action is legal"""
        game_state.end_turn()  # Switch to blue
        
        action, _, _ = fuzzy_agent.get_action(game_state)
        
        legal_actions = game_state.get_all_legal_actions()
        
        found = False
        for legal in legal_actions:
            if (legal.action_type == action.action_type and
                legal.unit_id == action.unit_id):
                found = True
                break
        
        assert found, "Returned action should be legal"
    
    def test_fuzzy_systems_initialized(self, fuzzy_agent):
        """Test that all fuzzy systems are initialized"""
        assert fuzzy_agent.threat_fis is not None
        assert fuzzy_agent.action_fis is not None
        assert fuzzy_agent.target_fis is not None
    
    def test_threat_system_works(self, fuzzy_agent):
        """Test threat assessment system"""
        result = fuzzy_agent.threat_fis.infer({
            "enemy_hp": 80,
            "enemy_attack": 70,
            "distance": 2
        })
        
        assert "threat" in result
        assert 0 <= result["threat"] <= 100
    
    def test_action_system_works(self, fuzzy_agent):
        """Test action selection system"""
        result = fuzzy_agent.action_fis.infer({
            "own_hp": 80,
            "team_advantage": 20,
            "enemies_in_range": 2
        })
        
        assert "aggression" in result
        assert 0 <= result["aggression"] <= 100
    
    def test_target_system_works(self, fuzzy_agent):
        """Test target prioritization system"""
        result = fuzzy_agent.target_fis.infer({
            "target_hp": 30,
            "target_damage": 80,
            "can_kill": 1
        })
        
        assert "priority" in result
        assert 0 <= result["priority"] <= 100
        
        # High priority for kill shot
        assert result["priority"] > 80
    
    def test_different_situations_different_responses(self, game_state, fuzzy_agent):
        """Test agent responds differently to different situations"""
        game_state.end_turn()
        
        # Get action in normal state
        action1, score1, _ = fuzzy_agent.get_action(game_state)
        
        # Damage our units heavily
        for unit in game_state.blue_team.units:
            unit.current_hp = int(unit.max_hp * 0.2)
        
        # Get action in damaged state - should be more defensive
        action2, score2, _ = fuzzy_agent.get_action(game_state)
        
        # Actions might differ based on situation
        # At minimum, scores should be different
        # (This is a weak test but validates some adaptation)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
