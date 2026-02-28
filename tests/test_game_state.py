"""
Unit tests for Game State and Core Mechanics
"""

import pytest
import sys
sys.path.insert(0, '.')

from core.game_state import GameState, Action, ActionType, GamePhase
from core.unit import Unit, Team, Position, UnitType
from core.battlefield import Battlefield, Terrain


class TestPosition:
    """Tests for Position class"""
    
    def test_distance_to(self):
        """Test Manhattan distance calculation"""
        p1 = Position(0, 0)
        p2 = Position(3, 4)
        
        assert p1.distance_to(p2) == 7
        assert p2.distance_to(p1) == 7
    
    def test_equality(self):
        """Test position equality"""
        p1 = Position(5, 5)
        p2 = Position(5, 5)
        p3 = Position(5, 6)
        
        assert p1 == p2
        assert p1 != p3
    
    def test_hash(self):
        """Test position can be used in sets/dicts"""
        positions = {Position(1, 1), Position(2, 2), Position(1, 1)}
        
        assert len(positions) == 2


class TestUnit:
    """Tests for Unit class"""
    
    def test_unit_creation(self):
        """Test unit factory method"""
        unit = Unit.create(
            unit_type=UnitType.WARRIOR,
            team=Team.RED,
            position=Position(0, 0)
        )
        
        assert unit.team == Team.RED
        assert unit.unit_type == UnitType.WARRIOR
        assert unit.is_alive
        assert unit.current_hp == unit.max_hp
    
    def test_take_damage(self):
        """Test damage mechanics"""
        unit = Unit.create(UnitType.WARRIOR, Team.RED, Position(0, 0))
        initial_hp = unit.current_hp
        
        damage_taken = unit.take_damage(50)
        
        assert damage_taken > 0
        assert unit.current_hp < initial_hp
        assert unit.is_alive
    
    def test_death(self):
        """Test unit death"""
        unit = Unit.create(UnitType.ARCHER, Team.BLUE, Position(0, 0))
        
        unit.take_damage(9999)
        
        assert not unit.is_alive
        assert unit.current_hp == 0
    
    def test_heal(self):
        """Test healing mechanics"""
        unit = Unit.create(UnitType.WARRIOR, Team.RED, Position(0, 0))
        unit.current_hp = 50
        
        healed = unit.heal(30)
        
        assert healed == 30
        assert unit.current_hp == 80
    
    def test_heal_not_over_max(self):
        """Test healing doesn't exceed max HP"""
        unit = Unit.create(UnitType.WARRIOR, Team.RED, Position(0, 0))
        unit.current_hp = unit.max_hp - 10
        
        healed = unit.heal(50)
        
        assert healed == 10
        assert unit.current_hp == unit.max_hp
    
    def test_movement_tracking(self):
        """Test movement state tracking"""
        unit = Unit.create(UnitType.WARRIOR, Team.RED, Position(0, 0))
        
        assert not unit.has_moved
        
        unit.move_to(Position(1, 1))
        
        assert unit.has_moved
        assert unit.position == Position(1, 1)
    
    def test_start_turn_resets_state(self):
        """Test turn start resets unit state"""
        unit = Unit.create(UnitType.WARRIOR, Team.RED, Position(0, 0))
        unit.has_moved = True
        unit.has_attacked = True
        
        unit.start_turn()
        
        assert not unit.has_moved
        assert not unit.has_attacked


class TestBattlefield:
    """Tests for Battlefield class"""
    
    @pytest.fixture
    def battlefield(self):
        return Battlefield(width=10, height=10, seed=42)
    
    def test_creation(self, battlefield):
        """Test battlefield is created correctly"""
        assert battlefield.width == 10
        assert battlefield.height == 10
    
    def test_valid_position(self, battlefield):
        """Test position validation"""
        assert battlefield.is_valid_position(Position(0, 0))
        assert battlefield.is_valid_position(Position(9, 9))
        assert not battlefield.is_valid_position(Position(-1, 0))
        assert not battlefield.is_valid_position(Position(10, 10))
    
    def test_get_cell(self, battlefield):
        """Test cell retrieval"""
        cell = battlefield.get_cell(Position(5, 5))
        
        assert cell is not None
        assert cell.position == Position(5, 5)
    
    def test_place_unit(self, battlefield):
        """Test unit placement"""
        unit = Unit.create(UnitType.WARRIOR, Team.RED, Position(0, 0))
        
        # Find a passable cell
        for y in range(battlefield.height):
            for x in range(battlefield.width):
                cell = battlefield.get_cell_at(x, y)
                if cell and cell.properties.passable and cell.is_empty:
                    result = battlefield.place_unit(unit, Position(x, y))
                    assert result
                    assert battlefield.get_unit_at(Position(x, y)) == unit
                    return
    
    def test_spawn_positions(self, battlefield):
        """Test spawn position generation"""
        red_spawns = battlefield.get_spawn_positions(Team.RED, 4)
        blue_spawns = battlefield.get_spawn_positions(Team.BLUE, 4)
        
        assert len(red_spawns) == 4
        assert len(blue_spawns) == 4
        
        # Red spawns should be on left side
        for pos in red_spawns:
            assert pos.x < battlefield.width // 2
        
        # Blue spawns should be on right side
        for pos in blue_spawns:
            assert pos.x >= battlefield.width // 2


class TestGameState:
    """Tests for GameState class"""
    
    @pytest.fixture
    def game_state(self):
        return GameState.create_new_game(
            battlefield_width=10,
            battlefield_height=10,
            units_per_team=3,
            seed=42
        )
    
    def test_creation(self, game_state):
        """Test game state is created correctly"""
        assert len(game_state.red_team.units) == 3
        assert len(game_state.blue_team.units) == 3
        assert game_state.current_turn == 0
        assert game_state.current_phase == GamePhase.RED_TURN
    
    def test_get_legal_actions(self, game_state):
        """Test legal action generation"""
        actions = game_state.get_all_legal_actions()
        
        assert len(actions) > 0
        
        # All actions should be for red team (current team)
        for action in actions:
            unit = game_state.get_unit_by_id(action.unit_id)
            assert unit.team == Team.RED
    
    def test_execute_move(self, game_state):
        """Test move execution"""
        unit = game_state.red_team.alive_units[0]
        reachable = game_state.battlefield.get_reachable_positions(unit)
        
        if reachable:
            action = Action(
                action_type=ActionType.MOVE,
                unit_id=unit.id,
                target_position=reachable[0]
            )
            
            result = game_state.execute_action(action)
            
            assert result.success
            assert unit.has_moved
            assert unit.position == reachable[0]
    
    def test_execute_wait(self, game_state):
        """Test wait action"""
        unit = game_state.red_team.alive_units[0]
        
        action = Action(
            action_type=ActionType.WAIT,
            unit_id=unit.id
        )
        
        result = game_state.execute_action(action)
        
        assert result.success
        assert unit.has_moved
        assert unit.has_attacked
    
    def test_turn_switch(self, game_state):
        """Test turn switching"""
        assert game_state.current_phase == GamePhase.RED_TURN
        
        game_state.end_turn()
        
        assert game_state.current_phase == GamePhase.BLUE_TURN
        
        game_state.end_turn()
        
        assert game_state.current_phase == GamePhase.RED_TURN
        assert game_state.current_turn == 1
    
    def test_game_over_detection(self, game_state):
        """Test game over detection"""
        assert not game_state.is_game_over
        
        # Kill all blue units
        for unit in game_state.blue_team.units:
            unit.take_damage(9999)
        
        assert game_state.is_game_over
        assert game_state.winner == Team.RED
    
    def test_clone(self, game_state):
        """Test state cloning"""
        clone = game_state.clone()
        
        assert clone.current_turn == game_state.current_turn
        assert len(clone.red_team.units) == len(game_state.red_team.units)
        
        # Modifying clone shouldn't affect original
        clone.current_turn = 999
        assert game_state.current_turn == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
