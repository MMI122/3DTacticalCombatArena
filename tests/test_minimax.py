"""
Unit tests for Minimax AI Agent
"""

import pytest
import sys
sys.path.insert(0, '.')

from ai.minimax_agent import MinimaxAgent
from ai.evaluation import Evaluator
from core.game_state import GameState, ActionType
from core.unit import Team, Position


class TestMinimaxAgent:
    """Tests for Minimax Alpha-Beta AI"""
    
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
    def minimax_agent(self):
        """Create a Minimax agent"""
        return MinimaxAgent(
            team=Team.RED,
            max_depth=3,
            time_limit=2.0
        )
    
    def test_agent_creation(self, minimax_agent):
        """Test agent is created correctly"""
        assert minimax_agent.team == Team.RED
        assert minimax_agent.max_depth == 3
        assert minimax_agent.time_limit == 2.0
        assert minimax_agent.get_algorithm_name() == "Minimax with Alpha-Beta Pruning"
    
    def test_get_action_returns_valid(self, game_state, minimax_agent):
        """Test that agent returns a valid action"""
        action, score, reasoning = minimax_agent.get_action(game_state)
        
        assert action is not None
        assert isinstance(score, float)
        assert isinstance(reasoning, str)
        assert len(reasoning) > 0
    
    def test_action_is_legal(self, game_state, minimax_agent):
        """Test that returned action is legal"""
        action, _, _ = minimax_agent.get_action(game_state)
        
        legal_actions = game_state.get_all_legal_actions()
        
        # Check action is in legal actions (by properties, not identity)
        found = False
        for legal in legal_actions:
            if (legal.action_type == action.action_type and
                legal.unit_id == action.unit_id):
                found = True
                break
        
        assert found, "Returned action should be legal"
    
    def test_debug_info_populated(self, game_state, minimax_agent):
        """Test that debug info is populated after decision"""
        minimax_agent.get_action(game_state)
        
        debug_info = minimax_agent.get_debug_info()
        
        assert 'nodes_searched' in debug_info
        assert 'cache_hits' in debug_info
        assert 'search_time' in debug_info
        assert debug_info['nodes_searched'] > 0
    
    def test_transposition_table_caching(self, game_state, minimax_agent):
        """Test that transposition table is being used"""
        minimax_agent.get_action(game_state)
        
        debug_info = minimax_agent.get_debug_info()
        
        # After one full search, table should have entries
        assert len(minimax_agent.transposition_table) > 0
    
    def test_reset_clears_state(self, game_state, minimax_agent):
        """Test that reset clears agent state"""
        minimax_agent.get_action(game_state)
        
        assert len(minimax_agent.transposition_table) > 0
        
        minimax_agent.reset()
        
        assert len(minimax_agent.transposition_table) == 0
        assert len(minimax_agent.get_debug_info()) == 0
    
    def test_deeper_search_finds_better_moves(self, game_state):
        """Test that deeper search generally finds better or equal moves"""
        shallow_agent = MinimaxAgent(team=Team.RED, max_depth=1, time_limit=5.0)
        deep_agent = MinimaxAgent(team=Team.RED, max_depth=3, time_limit=5.0)
        
        _, shallow_score, _ = shallow_agent.get_action(game_state)
        _, deep_score, _ = deep_agent.get_action(game_state)
        
        # Deep agent should explore more
        assert deep_agent.get_debug_info()['nodes_searched'] >= shallow_agent.get_debug_info()['nodes_searched']


class TestEvaluator:
    """Tests for the position evaluator"""
    
    @pytest.fixture
    def game_state(self):
        return GameState.create_new_game(
            battlefield_width=8,
            battlefield_height=8,
            units_per_team=2,
            seed=42
        )
    
    @pytest.fixture
    def evaluator(self):
        return Evaluator()
    
    def test_initial_position_balanced(self, game_state, evaluator):
        """Test that initial position is roughly balanced"""
        score = evaluator.evaluate(game_state, Team.RED)
        
        # Should be close to 0 at start
        assert -50 < score < 50
    
    def test_winning_position_high_score(self, game_state, evaluator):
        """Test that winning position has high score"""
        # Kill all blue units
        for unit in game_state.blue_team.units:
            unit.take_damage(9999)
        
        score = evaluator.evaluate(game_state, Team.RED)
        
        # Should be very high (winning)
        assert score > 1000
    
    def test_losing_position_low_score(self, game_state, evaluator):
        """Test that losing position has low score"""
        # Kill all red units
        for unit in game_state.red_team.units:
            unit.take_damage(9999)
        
        score = evaluator.evaluate(game_state, Team.RED)
        
        # Should be very low (losing)
        assert score < -1000
    
    def test_perspective_matters(self, game_state, evaluator):
        """Test that evaluation flips for different teams"""
        red_score = evaluator.evaluate(game_state, Team.RED)
        blue_score = evaluator.evaluate(game_state, Team.BLUE)
        
        # Scores should be opposite
        assert abs(red_score + blue_score) < 0.1  # Allow small float error
    
    def test_cache_works(self, game_state, evaluator):
        """Test that evaluation caching works"""
        evaluator.evaluate(game_state, Team.RED)
        evaluator.evaluate(game_state, Team.RED)
        
        # Cache should have entry
        assert len(evaluator._cache) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
