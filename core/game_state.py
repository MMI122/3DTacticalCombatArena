"""
Game State Management
Complete game state with action system and state transitions
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple, Any
from enum import Enum, auto
from copy import deepcopy
import random

from .unit import Unit, Team, TeamState, Position, UnitState
from .battlefield import Battlefield, Terrain
from config.units import UnitType, AbilityType, get_default_team_composition


class ActionType(Enum):
    """Types of actions units can take"""
    MOVE = auto()
    ATTACK = auto()
    ABILITY = auto()
    WAIT = auto()  # End unit's turn
    

@dataclass
class Action:
    """Represents a single game action"""
    action_type: ActionType
    unit_id: str
    target_position: Optional[Position] = None
    target_unit_id: Optional[str] = None
    ability_type: Optional[AbilityType] = None
    
    def __repr__(self):
        if self.action_type == ActionType.MOVE:
            return f"Move({self.unit_id} -> {self.target_position})"
        elif self.action_type == ActionType.ATTACK:
            return f"Attack({self.unit_id} -> {self.target_unit_id})"
        elif self.action_type == ActionType.ABILITY:
            return f"Ability({self.unit_id}: {self.ability_type})"
        else:
            return f"Wait({self.unit_id})"


@dataclass
class ActionResult:
    """Result of executing an action"""
    success: bool
    action: Action
    damage_dealt: int = 0
    damage_taken: int = 0
    healing_done: int = 0
    unit_killed: bool = False
    critical_hit: bool = False
    message: str = ""


class GamePhase(Enum):
    """Current phase of the game"""
    SETUP = auto()
    RED_TURN = auto()
    BLUE_TURN = auto()
    GAME_OVER = auto()


@dataclass
class TurnRecord:
    """Record of actions taken in a turn"""
    turn_number: int
    team: Team
    actions: List[ActionResult]
    
    
class GameState:
    """
    Complete game state
    Manages all game logic, state transitions, and action execution
    """
    
    def __init__(
        self,
        battlefield: Battlefield,
        red_team: TeamState,
        blue_team: TeamState,
        current_turn: int = 0,
        current_phase: GamePhase = GamePhase.RED_TURN
    ):
        self.battlefield = battlefield
        self.red_team = red_team
        self.blue_team = blue_team
        self.current_turn = current_turn
        self.current_phase = current_phase
        
        # History for replay
        self.history: List[TurnRecord] = []
        self.current_turn_actions: List[ActionResult] = []
        
        # Game statistics
        self.stats = {
            'total_damage_red': 0,
            'total_damage_blue': 0,
            'units_killed_red': 0,
            'units_killed_blue': 0,
            'turns_played': 0
        }
    
    @classmethod
    def create_new_game(
        cls,
        battlefield_width: int = 12,
        battlefield_height: int = 12,
        units_per_team: int = 4,
        seed: Optional[int] = None
    ) -> GameState:
        """Factory method to create a new game"""
        # Create battlefield
        battlefield = Battlefield(battlefield_width, battlefield_height, seed)
        
        # Get unit compositions
        team_comp = get_default_team_composition()[:units_per_team]
        
        # Create red team units
        red_spawns = battlefield.get_spawn_positions(Team.RED, units_per_team)
        red_units = []
        for i, unit_type in enumerate(team_comp):
            if i < len(red_spawns):
                unit = Unit.create(unit_type, Team.RED, red_spawns[i])
                battlefield.place_unit(unit, red_spawns[i])
                red_units.append(unit)
        
        # Create blue team units
        blue_spawns = battlefield.get_spawn_positions(Team.BLUE, units_per_team)
        blue_units = []
        for i, unit_type in enumerate(team_comp):
            if i < len(blue_spawns):
                unit = Unit.create(unit_type, Team.BLUE, blue_spawns[i])
                battlefield.place_unit(unit, blue_spawns[i])
                blue_units.append(unit)
        
        red_team = TeamState(Team.RED, red_units)
        blue_team = TeamState(Team.BLUE, blue_units)
        
        return cls(battlefield, red_team, blue_team)
    
    @property
    def current_team(self) -> TeamState:
        """Get the team whose turn it is"""
        if self.current_phase == GamePhase.RED_TURN:
            return self.red_team
        return self.blue_team
    
    @property
    def opposing_team(self) -> TeamState:
        """Get the opposing team"""
        if self.current_phase == GamePhase.RED_TURN:
            return self.blue_team
        return self.red_team
    
    @property
    def is_game_over(self) -> bool:
        """Check if game has ended"""
        return self.red_team.is_defeated or self.blue_team.is_defeated
    
    @property
    def winner(self) -> Optional[Team]:
        """Get the winning team, if any"""
        if self.red_team.is_defeated:
            return Team.BLUE
        if self.blue_team.is_defeated:
            return Team.RED
        return None
    
    def get_unit_by_id(self, unit_id: str) -> Optional[Unit]:
        """Find a unit by ID"""
        unit = self.red_team.get_unit_by_id(unit_id)
        if unit:
            return unit
        return self.blue_team.get_unit_by_id(unit_id)
    
    def get_all_units(self) -> List[Unit]:
        """Get all units on the battlefield"""
        return self.red_team.units + self.blue_team.units
    
    def get_alive_units(self) -> List[Unit]:
        """Get all living units"""
        return self.red_team.alive_units + self.blue_team.alive_units
    
    def get_legal_actions(self, unit: Unit) -> List[Action]:
        """Get all legal actions for a unit"""
        actions = []
        
        if not unit.is_alive or unit.team != self.current_team.team:
            return actions
        
        # Move actions
        if not unit.has_moved:
            for pos in self.battlefield.get_reachable_positions(unit):
                actions.append(Action(
                    action_type=ActionType.MOVE,
                    unit_id=unit.id,
                    target_position=pos
                ))
        
        # Attack actions
        if not unit.has_attacked:
            for enemy in self.battlefield.get_enemies_in_range(unit):
                if self.battlefield.has_line_of_sight(unit.position, enemy.position):
                    actions.append(Action(
                        action_type=ActionType.ATTACK,
                        unit_id=unit.id,
                        target_unit_id=enemy.id,
                        target_position=enemy.position
                    ))
        
        # Ability actions
        for ability in unit.get_available_abilities():
            if ability.ability_type == AbilityType.HEAL:
                # Target allies
                for ally in self.battlefield.get_allies_in_range(unit, unit.attack_range):
                    if ally.current_hp < ally.max_hp:
                        actions.append(Action(
                            action_type=ActionType.ABILITY,
                            unit_id=unit.id,
                            ability_type=ability.ability_type,
                            target_unit_id=ally.id,
                            target_position=ally.position
                        ))
            elif ability.ability_type == AbilityType.SHIELD_WALL:
                # Self-target
                actions.append(Action(
                    action_type=ActionType.ABILITY,
                    unit_id=unit.id,
                    ability_type=ability.ability_type
                ))
            elif ability.ability_type in [AbilityType.FIREBALL, AbilityType.SNIPE]:
                # Target enemies
                for enemy in self.battlefield.get_enemies_in_range(unit):
                    actions.append(Action(
                        action_type=ActionType.ABILITY,
                        unit_id=unit.id,
                        ability_type=ability.ability_type,
                        target_unit_id=enemy.id,
                        target_position=enemy.position
                    ))
        
        # Wait action (always available)
        actions.append(Action(
            action_type=ActionType.WAIT,
            unit_id=unit.id
        ))
        
        return actions
    
    def get_all_legal_actions(self) -> List[Action]:
        """Get all legal actions for current team"""
        actions = []
        for unit in self.current_team.get_units_that_can_act():
            actions.extend(self.get_legal_actions(unit))
        return actions
    
    def execute_action(self, action: Action) -> ActionResult:
        """Execute an action and update game state"""
        unit = self.get_unit_by_id(action.unit_id)
        
        if not unit or not unit.is_alive:
            return ActionResult(
                success=False,
                action=action,
                message="Unit not found or dead"
            )
        
        result = ActionResult(success=False, action=action)
        
        if action.action_type == ActionType.MOVE:
            result = self._execute_move(unit, action)
        elif action.action_type == ActionType.ATTACK:
            result = self._execute_attack(unit, action)
        elif action.action_type == ActionType.ABILITY:
            result = self._execute_ability(unit, action)
        elif action.action_type == ActionType.WAIT:
            result = self._execute_wait(unit, action)
        
        if result.success:
            self.current_turn_actions.append(result)
        
        return result
    
    def _execute_move(self, unit: Unit, action: Action) -> ActionResult:
        """Execute a move action"""
        if unit.has_moved:
            return ActionResult(
                success=False,
                action=action,
                message="Unit has already moved"
            )
        
        target = action.target_position
        if not self.battlefield.is_passable(target):
            return ActionResult(
                success=False,
                action=action,
                message="Target position not passable"
            )
        
        # Move the unit
        old_pos = unit.position
        self.battlefield.move_unit(unit, target)
        unit.has_moved = True
        
        return ActionResult(
            success=True,
            action=action,
            message=f"{unit.name} moved from {old_pos.to_tuple()} to {target.to_tuple()}"
        )
    
    def _execute_attack(self, unit: Unit, action: Action) -> ActionResult:
        """Execute an attack action"""
        if unit.has_attacked:
            return ActionResult(
                success=False,
                action=action,
                message="Unit has already attacked"
            )
        
        target = self.get_unit_by_id(action.target_unit_id)
        if not target or not target.is_alive:
            return ActionResult(
                success=False,
                action=action,
                message="Target not found or dead"
            )
        
        # Check range
        if unit.position.distance_to(target.position) > unit.attack_range:
            return ActionResult(
                success=False,
                action=action,
                message="Target out of range"
            )
        
        # Calculate damage
        terrain_cell = self.battlefield.get_cell(unit.position)
        attack_bonus = terrain_cell.attack_modifier if terrain_cell else 0
        
        target_cell = self.battlefield.get_cell(target.position)
        defense_bonus = target_cell.defense_modifier if target_cell else 0
        
        base_damage = unit.effective_attack + attack_bonus
        
        # Critical hit check
        critical = random.random() < unit.critical_chance
        if critical:
            base_damage = int(base_damage * 1.5)
        
        # Evasion check
        if random.random() < target.evasion_chance:
            unit.has_attacked = True
            return ActionResult(
                success=True,
                action=action,
                damage_dealt=0,
                message=f"{target.name} evaded the attack!"
            )
        
        # Apply damage
        actual_damage = target.take_damage(base_damage)
        unit.has_attacked = True
        
        # Update stats
        if unit.team == Team.RED:
            self.stats['total_damage_red'] += actual_damage
        else:
            self.stats['total_damage_blue'] += actual_damage
        
        killed = not target.is_alive
        if killed:
            self.battlefield.remove_unit(target)
            if target.team == Team.RED:
                self.stats['units_killed_blue'] += 1
            else:
                self.stats['units_killed_red'] += 1
        
        return ActionResult(
            success=True,
            action=action,
            damage_dealt=actual_damage,
            unit_killed=killed,
            critical_hit=critical,
            message=f"{unit.name} dealt {actual_damage} damage to {target.name}" +
                    (" (CRITICAL!)" if critical else "") +
                    (" - ELIMINATED!" if killed else "")
        )
    
    def _execute_ability(self, unit: Unit, action: Action) -> ActionResult:
        """Execute a special ability"""
        ability = unit.use_ability(action.ability_type)
        if not ability:
            return ActionResult(
                success=False,
                action=action,
                message="Ability not available"
            )
        
        result = ActionResult(success=True, action=action)
        
        if ability.ability_type == AbilityType.HEAL:
            target = self.get_unit_by_id(action.target_unit_id)
            if target and target.is_alive:
                healed = target.heal(ability.heal_amount)
                result.healing_done = healed
                result.message = f"{unit.name} healed {target.name} for {healed} HP"
        
        elif ability.ability_type == AbilityType.SHIELD_WALL:
            unit.apply_buff(defense_bonus=ability.defense_bonus, duration=2)
            result.message = f"{unit.name} raised Shield Wall! (+{ability.defense_bonus} defense)"
        
        elif ability.ability_type == AbilityType.FIREBALL:
            target = self.get_unit_by_id(action.target_unit_id)
            if target:
                # Area damage
                center = target.position
                total_damage = 0
                targets_hit = []
                
                for dy in range(-ability.area_of_effect + 1, ability.area_of_effect):
                    for dx in range(-ability.area_of_effect + 1, ability.area_of_effect):
                        pos = Position(center.x + dx, center.y + dy)
                        hit_unit = self.battlefield.get_unit_at(pos)
                        if hit_unit and hit_unit.is_alive and hit_unit.team != unit.team:
                            damage = int(unit.effective_attack * ability.damage_modifier)
                            actual = hit_unit.take_damage(damage)
                            total_damage += actual
                            targets_hit.append(hit_unit.name)
                            if not hit_unit.is_alive:
                                self.battlefield.remove_unit(hit_unit)
                
                result.damage_dealt = total_damage
                result.message = f"{unit.name} cast Fireball hitting {', '.join(targets_hit)} for {total_damage} total damage"
        
        elif ability.ability_type == AbilityType.SNIPE:
            target = self.get_unit_by_id(action.target_unit_id)
            if target and target.is_alive:
                damage = int(unit.effective_attack * ability.damage_modifier)
                actual = target.take_damage(damage)
                result.damage_dealt = actual
                result.unit_killed = not target.is_alive
                if not target.is_alive:
                    self.battlefield.remove_unit(target)
                result.message = f"{unit.name} sniped {target.name} for {actual} damage"
        
        unit.has_attacked = True
        return result
    
    def _execute_wait(self, unit: Unit, action: Action) -> ActionResult:
        """Execute wait action - end unit's turn"""
        unit.end_turn()
        return ActionResult(
            success=True,
            action=action,
            message=f"{unit.name} is waiting"
        )
    
    def end_turn(self):
        """End the current team's turn"""
        # Record turn
        self.history.append(TurnRecord(
            turn_number=self.current_turn,
            team=self.current_team.team,
            actions=self.current_turn_actions.copy()
        ))
        self.current_turn_actions.clear()
        
        # End turn for all units
        for unit in self.current_team.units:
            unit.end_turn()
        
        # Switch teams
        if self.current_phase == GamePhase.RED_TURN:
            self.current_phase = GamePhase.BLUE_TURN
            # Start turn for blue team
            for unit in self.blue_team.units:
                unit.start_turn()
        else:
            self.current_phase = GamePhase.RED_TURN
            self.current_turn += 1
            self.stats['turns_played'] = self.current_turn
            # Start turn for red team
            for unit in self.red_team.units:
                unit.start_turn()
        
        # Check for game over
        if self.is_game_over:
            self.current_phase = GamePhase.GAME_OVER
    
    def start_turn(self):
        """Start a new turn for the current team"""
        for unit in self.current_team.units:
            unit.start_turn()
    
    def clone(self) -> GameState:
        """Create a deep copy of the game state for AI simulation"""
        new_battlefield = self.battlefield.clone()
        
        # Get units from cloned battlefield
        new_red_units = [
            new_battlefield.get_cell(u.position).occupant
            for u in self.red_team.units
            if new_battlefield.get_cell(u.position) and 
               new_battlefield.get_cell(u.position).occupant
        ]
        new_blue_units = [
            new_battlefield.get_cell(u.position).occupant
            for u in self.blue_team.units
            if new_battlefield.get_cell(u.position) and 
               new_battlefield.get_cell(u.position).occupant
        ]
        
        # Handle dead units that are no longer on battlefield
        for u in self.red_team.units:
            if not u.is_alive:
                new_red_units.append(u.clone())
        for u in self.blue_team.units:
            if not u.is_alive:
                new_blue_units.append(u.clone())
        
        new_red_team = TeamState(Team.RED, new_red_units)
        new_blue_team = TeamState(Team.BLUE, new_blue_units)
        
        new_state = GameState(
            battlefield=new_battlefield,
            red_team=new_red_team,
            blue_team=new_blue_team,
            current_turn=self.current_turn,
            current_phase=self.current_phase
        )
        new_state.stats = self.stats.copy()
        
        return new_state
    
    def get_state_hash(self) -> int:
        """Get a hash of the current state for transposition tables"""
        state_tuple = (
            self.current_phase,
            self.current_turn,
            tuple(
                (u.id, u.position.to_tuple(), u.current_hp, u.has_moved, u.has_attacked)
                for u in self.get_alive_units()
            )
        )
        return hash(state_tuple)
    
    def __repr__(self):
        return (
            f"GameState(Turn {self.current_turn}, Phase: {self.current_phase.name}, "
            f"Red: {len(self.red_team.alive_units)}, Blue: {len(self.blue_team.alive_units)})"
        )
