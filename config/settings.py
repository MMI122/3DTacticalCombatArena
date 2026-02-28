"""
Game Configuration Settings
Production-grade settings management for the 3D Tactical Combat Arena
"""

from dataclasses import dataclass, field
from typing import Tuple, Dict, Any
from enum import Enum


class GameSpeed(Enum):
    """Game simulation speed options"""
    SLOW = 0.5
    NORMAL = 1.0
    FAST = 2.0
    ULTRA_FAST = 4.0


class Difficulty(Enum):
    """AI difficulty levels"""
    EASY = 1
    MEDIUM = 2
    HARD = 3
    EXPERT = 4


@dataclass
class GraphicsSettings:
    """Graphics and rendering configuration"""
    window_width: int = 1920
    window_height: int = 1080
    fullscreen: bool = False
    vsync: bool = True
    antialiasing: bool = True
    shadow_quality: str = "high"  # low, medium, high, ultra
    particle_density: float = 1.0
    bloom_enabled: bool = True
    ambient_occlusion: bool = True
    fps_limit: int = 60


@dataclass
class BattlefieldSettings:
    """Battlefield configuration"""
    grid_width: int = 12
    grid_height: int = 12
    cell_size: float = 2.0
    terrain_height_variation: float = 0.5
    obstacle_density: float = 0.15
    cover_density: float = 0.1


@dataclass
class UnitSettings:
    """Default unit statistics"""
    base_hp: int = 100
    base_attack: int = 25
    base_defense: int = 10
    base_movement: int = 3
    base_attack_range: int = 2


@dataclass
class AISettings:
    """AI agent configuration"""
    # Minimax settings
    minimax_depth: int = 4
    minimax_time_limit: float = 5.0  # seconds
    use_transposition_table: bool = True
    use_iterative_deepening: bool = True
    
    # Fuzzy Logic settings
    fuzzy_aggression_base: float = 0.5
    fuzzy_defense_weight: float = 0.3
    fuzzy_attack_weight: float = 0.4
    fuzzy_position_weight: float = 0.3
    
    # General AI settings
    decision_delay: float = 0.1  # Visual delay between decisions (faster!)
    show_thinking: bool = True


@dataclass
class CameraSettings:
    """Camera configuration"""
    initial_position: Tuple[float, float, float] = (0, 25, -20)
    initial_rotation: Tuple[float, float, float] = (45, 0, 0)
    zoom_speed: float = 2.0
    rotation_speed: float = 100.0
    pan_speed: float = 15.0
    min_zoom: float = 10.0
    max_zoom: float = 100.0  # Increased to see full battlefield


@dataclass
class AudioSettings:
    """Audio configuration"""
    master_volume: float = 0.8
    music_volume: float = 0.5
    sfx_volume: float = 0.7
    ambient_volume: float = 0.3


@dataclass
class GameConfig:
    """Master game configuration"""
    graphics: GraphicsSettings = field(default_factory=GraphicsSettings)
    battlefield: BattlefieldSettings = field(default_factory=BattlefieldSettings)
    units: UnitSettings = field(default_factory=UnitSettings)
    ai: AISettings = field(default_factory=AISettings)
    camera: CameraSettings = field(default_factory=CameraSettings)
    audio: AudioSettings = field(default_factory=AudioSettings)
    
    # Game rules
    units_per_team: int = 4
    max_turns: int = 100
    simultaneous_turns: bool = False
    
    # Match settings
    game_speed: GameSpeed = GameSpeed.FAST  # Default to faster gameplay
    show_ai_reasoning: bool = True
    auto_save_replays: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            'graphics': self.graphics.__dict__,
            'battlefield': self.battlefield.__dict__,
            'units': self.units.__dict__,
            'ai': self.ai.__dict__,
            'camera': self.camera.__dict__,
            'audio': self.audio.__dict__,
            'units_per_team': self.units_per_team,
            'max_turns': self.max_turns,
            'game_speed': self.game_speed.value
        }


# Global configuration instance
CONFIG = GameConfig()


def get_config() -> GameConfig:
    """Get the global configuration instance"""
    return CONFIG


def update_config(**kwargs) -> None:
    """Update configuration values"""
    global CONFIG
    for key, value in kwargs.items():
        if hasattr(CONFIG, key):
            setattr(CONFIG, key, value)
