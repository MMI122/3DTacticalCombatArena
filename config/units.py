"""
Unit Type Definitions
Defines all unit types with their statistics and abilities
"""

from dataclasses import dataclass
from typing import List, Optional, Dict
from enum import Enum, auto


class UnitType(Enum):
    """Available unit types"""
    WARRIOR = auto()      # Melee tank - high HP, medium attack
    ARCHER = auto()       # Ranged DPS - low HP, high attack, long range
    MAGE = auto()         # Area damage - medium HP, high attack, medium range
    KNIGHT = auto()       # Mobile fighter - medium HP, high attack, high movement
    HEALER = auto()       # Support - low HP, can heal allies


class AbilityType(Enum):
    """Special ability types"""
    CHARGE = auto()       # Move and attack in one action
    SNIPE = auto()        # Extended range attack
    FIREBALL = auto()     # Area of effect damage
    SHIELD_WALL = auto()  # Increased defense for a turn
    HEAL = auto()         # Restore ally HP
    OVERWATCH = auto()    # Counter-attack when enemy moves nearby


@dataclass
class Ability:
    """Special ability definition"""
    name: str
    ability_type: AbilityType
    cooldown: int
    damage_modifier: float = 1.0
    range_modifier: float = 1.0
    area_of_effect: int = 0
    heal_amount: int = 0
    defense_bonus: int = 0
    description: str = ""


@dataclass
class UnitStats:
    """Complete unit statistics"""
    unit_type: UnitType
    name: str
    max_hp: int
    attack: int
    defense: int
    movement_range: int
    attack_range: int
    critical_chance: float
    evasion_chance: float
    abilities: List[Ability]
    description: str
    
    # Visual properties
    model_scale: float = 1.0
    color_primary: tuple = (1, 1, 1)
    color_secondary: tuple = (0.5, 0.5, 0.5)


# Ability definitions
ABILITIES = {
    AbilityType.CHARGE: Ability(
        name="Charge",
        ability_type=AbilityType.CHARGE,
        cooldown=3,
        damage_modifier=1.5,
        description="Rush forward and strike with bonus damage"
    ),
    AbilityType.SNIPE: Ability(
        name="Snipe",
        ability_type=AbilityType.SNIPE,
        cooldown=2,
        damage_modifier=2.0,
        range_modifier=1.5,
        description="Precise long-range shot with critical damage"
    ),
    AbilityType.FIREBALL: Ability(
        name="Fireball",
        ability_type=AbilityType.FIREBALL,
        cooldown=3,
        damage_modifier=0.8,
        area_of_effect=2,
        description="Explosive magic dealing area damage"
    ),
    AbilityType.SHIELD_WALL: Ability(
        name="Shield Wall",
        ability_type=AbilityType.SHIELD_WALL,
        cooldown=4,
        defense_bonus=20,
        description="Raise shields for massive defense boost"
    ),
    AbilityType.HEAL: Ability(
        name="Heal",
        ability_type=AbilityType.HEAL,
        cooldown=2,
        heal_amount=40,
        description="Restore health to an ally"
    ),
    AbilityType.OVERWATCH: Ability(
        name="Overwatch",
        ability_type=AbilityType.OVERWATCH,
        cooldown=2,
        damage_modifier=0.7,
        description="Attack enemies that move within range"
    )
}


# Unit type definitions
UNIT_TEMPLATES: Dict[UnitType, UnitStats] = {
    UnitType.WARRIOR: UnitStats(
        unit_type=UnitType.WARRIOR,
        name="Warrior",
        max_hp=150,
        attack=30,
        defense=20,
        movement_range=2,
        attack_range=1,
        critical_chance=0.1,
        evasion_chance=0.05,
        abilities=[ABILITIES[AbilityType.SHIELD_WALL], ABILITIES[AbilityType.CHARGE]],
        description="Heavy frontline fighter with high durability",
        model_scale=1.2,
        color_primary=(0.8, 0.2, 0.2),
        color_secondary=(0.4, 0.1, 0.1)
    ),
    UnitType.ARCHER: UnitStats(
        unit_type=UnitType.ARCHER,
        name="Archer",
        max_hp=80,
        attack=35,
        defense=8,
        movement_range=3,
        attack_range=5,
        critical_chance=0.25,
        evasion_chance=0.15,
        abilities=[ABILITIES[AbilityType.SNIPE], ABILITIES[AbilityType.OVERWATCH]],
        description="Long-range specialist with deadly precision",
        model_scale=0.9,
        color_primary=(0.2, 0.8, 0.2),
        color_secondary=(0.1, 0.4, 0.1)
    ),
    UnitType.MAGE: UnitStats(
        unit_type=UnitType.MAGE,
        name="Mage",
        max_hp=70,
        attack=45,
        defense=5,
        movement_range=2,
        attack_range=4,
        critical_chance=0.15,
        evasion_chance=0.1,
        abilities=[ABILITIES[AbilityType.FIREBALL]],
        description="Powerful spellcaster with area damage",
        model_scale=1.0,
        color_primary=(0.6, 0.2, 0.8),
        color_secondary=(0.3, 0.1, 0.4)
    ),
    UnitType.KNIGHT: UnitStats(
        unit_type=UnitType.KNIGHT,
        name="Knight",
        max_hp=120,
        attack=35,
        defense=15,
        movement_range=4,
        attack_range=1,
        critical_chance=0.2,
        evasion_chance=0.1,
        abilities=[ABILITIES[AbilityType.CHARGE]],
        description="Mobile cavalry unit for flanking maneuvers",
        model_scale=1.3,
        color_primary=(0.2, 0.4, 0.8),
        color_secondary=(0.1, 0.2, 0.4)
    ),
    UnitType.HEALER: UnitStats(
        unit_type=UnitType.HEALER,
        name="Healer",
        max_hp=60,
        attack=15,
        defense=10,
        movement_range=3,
        attack_range=3,
        critical_chance=0.05,
        evasion_chance=0.2,
        abilities=[ABILITIES[AbilityType.HEAL]],
        description="Support unit that keeps allies in the fight",
        model_scale=0.85,
        color_primary=(1.0, 1.0, 0.3),
        color_secondary=(0.5, 0.5, 0.15)
    )
}


def get_unit_template(unit_type: UnitType) -> UnitStats:
    """Get the template for a unit type"""
    return UNIT_TEMPLATES[unit_type]


def get_default_team_composition() -> List[UnitType]:
    """Get the default team of units"""
    return [
        UnitType.WARRIOR,
        UnitType.ARCHER,
        UnitType.MAGE,
        UnitType.KNIGHT
    ]


def get_balanced_team_composition() -> List[UnitType]:
    """Get a balanced team composition"""
    return [
        UnitType.WARRIOR,
        UnitType.ARCHER,
        UnitType.KNIGHT,
        UnitType.HEALER
    ]
