"""
Unit and Team Classes
Core unit representation with stats, abilities, and state management
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple, TYPE_CHECKING
from enum import Enum, auto
from copy import deepcopy
import uuid

from config.units import UnitType, UnitStats, Ability, AbilityType, get_unit_template

if TYPE_CHECKING:
    from .battlefield import Cell


class Team(Enum):
    """Team identifiers"""
    RED = auto()   # Minimax AI
    BLUE = auto()  # Fuzzy Logic AI


class UnitState(Enum):
    """Unit state flags"""
    IDLE = auto()
    MOVED = auto()
    ATTACKED = auto()
    DEFENDING = auto()
    DEAD = auto()


@dataclass
class Position:
    """Grid position"""
    x: int
    y: int
    
    def __hash__(self):
        return hash((self.x, self.y))
    
    def __eq__(self, other):
        if isinstance(other, Position):
            return self.x == other.x and self.y == other.y
        return False
    
    def distance_to(self, other: Position) -> int:
        """Manhattan distance to another position"""
        return abs(self.x - other.x) + abs(self.y - other.y)
    
    def euclidean_distance(self, other: Position) -> float:
        """Euclidean distance to another position"""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
    
    def to_tuple(self) -> Tuple[int, int]:
        return (self.x, self.y)
    
    @classmethod
    def from_tuple(cls, t: Tuple[int, int]) -> Position:
        return cls(x=t[0], y=t[1])


@dataclass
class Unit:
    """
    Game unit with full state and capabilities
    """
    id: str
    team: Team
    unit_type: UnitType
    position: Position
    
    # Current stats (can be modified during combat)
    current_hp: int
    max_hp: int
    attack: int
    defense: int
    movement_range: int
    attack_range: int
    critical_chance: float
    evasion_chance: float
    
    # State
    state: UnitState = UnitState.IDLE
    has_moved: bool = False
    has_attacked: bool = False
    
    # Abilities
    abilities: List[Ability] = field(default_factory=list)
    ability_cooldowns: Dict[AbilityType, int] = field(default_factory=dict)
    
    # Buffs/Debuffs
    defense_bonus: int = 0
    attack_bonus: int = 0
    buff_duration: int = 0
    
    # Visual/Display
    name: str = ""
    model_scale: float = 1.0
    color_primary: Tuple[float, float, float] = (1.0, 1.0, 1.0)
    color_secondary: Tuple[float, float, float] = (0.5, 0.5, 0.5)
    
    @classmethod
    def create(cls, unit_type: UnitType, team: Team, position: Position) -> Unit:
        """Factory method to create a unit from template"""
        template = get_unit_template(unit_type)
        unit_id = f"{team.name}_{unit_type.name}_{uuid.uuid4().hex[:8]}"
        
        return cls(
            id=unit_id,
            team=team,
            unit_type=unit_type,
            position=position,
            current_hp=template.max_hp,
            max_hp=template.max_hp,
            attack=template.attack,
            defense=template.defense,
            movement_range=template.movement_range,
            attack_range=template.attack_range,
            critical_chance=template.critical_chance,
            evasion_chance=template.evasion_chance,
            abilities=deepcopy(template.abilities),
            ability_cooldowns={ab.ability_type: 0 for ab in template.abilities},
            name=template.name,
            model_scale=template.model_scale,
            color_primary=template.color_primary,
            color_secondary=template.color_secondary
        )
    
    @property
    def is_alive(self) -> bool:
        """Check if unit is alive"""
        return self.current_hp > 0 and self.state != UnitState.DEAD
    
    @property
    def hp_percentage(self) -> float:
        """Get HP as percentage"""
        return self.current_hp / self.max_hp
    
    @property
    def effective_attack(self) -> int:
        """Get attack with bonuses"""
        return self.attack + self.attack_bonus
    
    @property
    def effective_defense(self) -> int:
        """Get defense with bonuses"""
        return self.defense + self.defense_bonus
    
    @property
    def can_act(self) -> bool:
        """Check if unit can still act this turn"""
        return self.is_alive and (not self.has_moved or not self.has_attacked)
    
    def can_reach(self, target: Position) -> bool:
        """Check if unit can move to target position"""
        if self.has_moved:
            return False
        return self.position.distance_to(target) <= self.movement_range
    
    def can_attack_position(self, target: Position) -> bool:
        """Check if unit can attack target position"""
        if self.has_attacked:
            return False
        return self.position.distance_to(target) <= self.attack_range
    
    def get_available_abilities(self) -> List[Ability]:
        """Get abilities that are off cooldown"""
        return [
            ab for ab in self.abilities 
            if self.ability_cooldowns.get(ab.ability_type, 0) == 0
        ]
    
    def take_damage(self, damage: int, ignore_defense: bool = False) -> int:
        """
        Apply damage to unit
        Returns actual damage taken
        """
        if not self.is_alive:
            return 0
        
        # Calculate actual damage
        if ignore_defense:
            actual_damage = max(1, damage)
        else:
            actual_damage = max(1, damage - self.effective_defense)
        
        # Apply damage
        self.current_hp = max(0, self.current_hp - actual_damage)
        
        # Check for death
        if self.current_hp <= 0:
            self.state = UnitState.DEAD
        
        return actual_damage
    
    def heal(self, amount: int) -> int:
        """
        Heal the unit
        Returns actual amount healed
        """
        if not self.is_alive:
            return 0
        
        old_hp = self.current_hp
        self.current_hp = min(self.max_hp, self.current_hp + amount)
        return self.current_hp - old_hp
    
    def move_to(self, new_position: Position) -> bool:
        """Move unit to new position"""
        if self.has_moved:
            return False
        
        self.position = new_position
        self.has_moved = True
        self.state = UnitState.MOVED
        return True
    
    def use_ability(self, ability_type: AbilityType) -> Optional[Ability]:
        """Use an ability, returns the ability if successful"""
        for ability in self.abilities:
            if ability.ability_type == ability_type:
                if self.ability_cooldowns.get(ability_type, 0) == 0:
                    self.ability_cooldowns[ability_type] = ability.cooldown
                    return ability
        return None
    
    def apply_buff(self, defense_bonus: int = 0, attack_bonus: int = 0, duration: int = 1):
        """Apply a temporary buff"""
        self.defense_bonus += defense_bonus
        self.attack_bonus += attack_bonus
        self.buff_duration = max(self.buff_duration, duration)
    
    def start_turn(self):
        """Reset unit state for new turn"""
        self.has_moved = False
        self.has_attacked = False
        if self.is_alive:
            self.state = UnitState.IDLE
        
        # Tick down cooldowns
        for ability_type in self.ability_cooldowns:
            if self.ability_cooldowns[ability_type] > 0:
                self.ability_cooldowns[ability_type] -= 1
        
        # Tick down buffs
        if self.buff_duration > 0:
            self.buff_duration -= 1
            if self.buff_duration == 0:
                self.defense_bonus = 0
                self.attack_bonus = 0
    
    def end_turn(self):
        """Finalize unit state for end of turn"""
        self.has_moved = True
        self.has_attacked = True
    
    def clone(self) -> Unit:
        """Create a deep copy of the unit"""
        return deepcopy(self)
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        if isinstance(other, Unit):
            return self.id == other.id
        return False
    
    def __repr__(self):
        return f"Unit({self.name}, {self.team.name}, HP:{self.current_hp}/{self.max_hp}, Pos:{self.position.to_tuple()})"


@dataclass
class TeamState:
    """State of an entire team"""
    team: Team
    units: List[Unit]
    
    @property
    def alive_units(self) -> List[Unit]:
        """Get all living units"""
        return [u for u in self.units if u.is_alive]
    
    @property
    def total_hp(self) -> int:
        """Get total HP of all living units"""
        return sum(u.current_hp for u in self.alive_units)
    
    @property
    def max_total_hp(self) -> int:
        """Get max possible HP"""
        return sum(u.max_hp for u in self.units)
    
    @property
    def is_defeated(self) -> bool:
        """Check if team is defeated"""
        return len(self.alive_units) == 0
    
    def get_unit_by_id(self, unit_id: str) -> Optional[Unit]:
        """Find unit by ID"""
        for unit in self.units:
            if unit.id == unit_id:
                return unit
        return None
    
    def get_units_that_can_act(self) -> List[Unit]:
        """Get units that can still act"""
        return [u for u in self.alive_units if u.can_act]
