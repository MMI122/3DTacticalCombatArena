"""
Unit 3D Visualization
Creates animated 3D representations of game units
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import math

from ursina import (
    Entity, color, Vec3, Text, time, Sequence, Func, Wait,
    lerp, invoke, destroy, curve
)
from ursina.shaders import lit_with_shadows_shader

from core.unit import Unit, Team, UnitType
from config.settings import get_config

if TYPE_CHECKING:
    from .renderer import GameRenderer


class UnitView:
    """
    3D visualization of a game unit with animations
    """
    
    def __init__(self, unit: Unit, renderer: 'GameRenderer'):
        self.unit = unit
        self.renderer = renderer
        self.config = get_config()
        
        # Main entity
        self.entity: Optional[Entity] = None
        
        # Sub-components
        self.body: Optional[Entity] = None
        self.head: Optional[Entity] = None
        self.weapon: Optional[Entity] = None
        self.health_bar_bg: Optional[Entity] = None
        self.health_bar: Optional[Entity] = None
        self.team_indicator: Optional[Entity] = None
        self.name_text: Optional[Text] = None
        self.selection_ring: Optional[Entity] = None
        
        # Animation state
        self.is_animating = False
        self.animation_queue = []
        self.idle_time = 0
        self.hover_offset = 0
        
        # Create the unit visual
        self._create_unit()
    
    def _get_team_color(self) -> color:
        """Get color based on team"""
        if self.unit.team == Team.RED:
            return color.Color(0.86, 0.24, 0.24, 1.0)  # Red team
        else:
            return color.Color(0.24, 0.47, 0.86, 1.0)  # Blue team
    
    def _get_secondary_color(self) -> color:
        """Get secondary color based on team"""
        if self.unit.team == Team.RED:
            return color.Color(0.59, 0.16, 0.16, 1.0)  # Dark red
        else:
            return color.Color(0.16, 0.31, 0.59, 1.0)  # Dark blue
    
    def _create_unit(self):
        """Create the 3D unit model"""
        # Calculate world position
        if self.renderer.battlefield_view:
            world_pos = self.renderer.battlefield_view.grid_to_world(
                self.unit.position.x, self.unit.position.y
            )
        else:
            world_pos = Vec3(
                self.unit.position.x * 2,
                0,
                self.unit.position.y * 2
            )
        
        # Main entity (container)
        self.entity = Entity(position=world_pos + Vec3(0, 0.5, 0))
        
        # Create based on unit type
        if self.unit.unit_type == UnitType.WARRIOR:
            self._create_warrior()
        elif self.unit.unit_type == UnitType.ARCHER:
            self._create_archer()
        elif self.unit.unit_type == UnitType.MAGE:
            self._create_mage()
        elif self.unit.unit_type == UnitType.KNIGHT:
            self._create_knight()
        elif self.unit.unit_type == UnitType.HEALER:
            self._create_healer()
        else:
            self._create_default()
        
        # Health bar
        self._create_health_bar()
        
        # Team indicator
        self._create_team_indicator()
        
        # Selection ring (hidden by default)
        self._create_selection_ring()
        
        # Name text
        self._create_name_text()
    
    def _create_warrior(self):
        """Create warrior model - heavy, bulky"""
        team_color = self._get_team_color()
        secondary = self._get_secondary_color()
        
        # Body (wide, sturdy)
        self.body = Entity(
            parent=self.entity,
            model='cube',
            scale=(0.7, 1.0, 0.5),
            position=(0, 0.5, 0),
            color=team_color,
            unlit=True
        )
        
        # Head
        self.head = Entity(
            parent=self.entity,
            model='sphere',
            scale=0.35,
            position=(0, 1.2, 0),
            color=color.Color(1.0, 0.86, 0.7, 1.0),  # Skin tone
            unlit=True
        )
        
        # Helmet
        helmet = Entity(
            parent=self.entity,
            model='cube',
            scale=(0.4, 0.25, 0.4),
            position=(0, 1.35, 0),
            color=secondary
        )
        
        # Shield
        self.weapon = Entity(
            parent=self.entity,
            model='cube',
            scale=(0.1, 0.6, 0.5),
            position=(-0.45, 0.5, 0),
            color=secondary
        )
        
        # Sword
        sword = Entity(
            parent=self.entity,
            model='cube',
            scale=(0.08, 0.8, 0.08),
            position=(0.45, 0.6, 0),
            color=color.Color(0.78, 0.78, 0.78, 1.0)  # Silver
        )
    
    def _create_archer(self):
        """Create archer model - slim, agile"""
        team_color = self._get_team_color()
        
        # Body (slim)
        self.body = Entity(
            parent=self.entity,
            model='cube',
            scale=(0.4, 0.9, 0.3),
            position=(0, 0.45, 0),
            color=team_color,
            unlit=True
        )
        
        # Head
        self.head = Entity(
            parent=self.entity,
            model='sphere',
            scale=0.3,
            position=(0, 1.1, 0),
            color=color.Color(1.0, 0.86, 0.7, 1.0),  # Skin tone
            unlit=True
        )
        
        # Hood (cap)
        hood = Entity(
            parent=self.entity,
            model='sphere',
            scale=(0.35, 0.25, 0.35),
            position=(0, 1.2, 0),
            color=color.Color(0.13, 0.55, 0.13, 1.0)  # Forest green
        )
        
        # Bow
        self.weapon = Entity(
            parent=self.entity,
            model='circle',
            scale=(0.4, 0.6, 0.1),
            position=(-0.35, 0.6, 0),
            rotation=(0, 0, 90),
            color=color.Color(0.55, 0.35, 0.17, 1.0)  # Brown
        )
    
    def _create_mage(self):
        """Create mage model - robed, mystical"""
        team_color = self._get_team_color()
        
        # Robe body (cylinder approximation)
        self.body = Entity(
            parent=self.entity,
            model='cube',
            scale=(0.55, 1.0, 0.55),
            position=(0, 0.5, 0),
            color=color.Color(0.29, 0.0, 0.51, 1.0),  # Indigo
            unlit=True
        )
        
        # Head
        self.head = Entity(
            parent=self.entity,
            model='sphere',
            scale=0.28,
            position=(0, 1.1, 0),
            color=color.Color(1.0, 0.86, 0.7, 1.0),  # Skin tone
            unlit=True
        )
        
        # Wizard hat (pointed cap)
        hat = Entity(
            parent=self.entity,
            model='sphere',
            scale=(0.3, 0.45, 0.3),
            position=(0, 1.35, 0),
            color=color.Color(0.29, 0.0, 0.51, 1.0)  # Indigo
        )
        
        # Staff
        self.weapon = Entity(
            parent=self.entity,
            model='cube',
            scale=(0.08, 1.4, 0.08),
            position=(0.4, 0.7, 0),
            color=color.Color(0.55, 0.35, 0.17, 1.0)  # Brown
        )
        
        # Staff orb
        orb = Entity(
            parent=self.entity,
            model='sphere',
            scale=0.15,
            position=(0.4, 1.45, 0),
            color=team_color
        )
    
    def _create_knight(self):
        """Create knight model - mounted, armored"""
        team_color = self._get_team_color()
        secondary = self._get_secondary_color()
        
        # Horse body
        horse = Entity(
            parent=self.entity,
            model='cube',
            scale=(0.5, 0.5, 0.9),
            position=(0, 0.3, 0),
            color=color.Color(0.55, 0.35, 0.17, 1.0),  # Brown
            unlit=True
        )
        
        # Horse head
        horse_head = Entity(
            parent=self.entity,
            model='cube',
            scale=(0.25, 0.35, 0.3),
            position=(0, 0.5, 0.5),
            color=color.Color(0.55, 0.35, 0.17, 1.0),  # Brown
            unlit=True
        )
        
        # Rider body
        self.body = Entity(
            parent=self.entity,
            model='cube',
            scale=(0.4, 0.7, 0.35),
            position=(0, 0.9, 0),
            color=team_color,
            unlit=True
        )
        
        # Rider head
        self.head = Entity(
            parent=self.entity,
            model='sphere',
            scale=0.25,
            position=(0, 1.35, 0),
            color=color.Color(0.78, 0.78, 0.78, 1.0),  # Silver helmet
            unlit=True
        )
        
        # Lance
        self.weapon = Entity(
            parent=self.entity,
            model='cube',
            scale=(0.06, 0.06, 1.5),
            position=(0.3, 0.9, 0.3),
            color=color.Color(0.78, 0.78, 0.78, 1.0)  # Silver
        )
    
    def _create_healer(self):
        """Create healer model - robed, glowing"""
        team_color = self._get_team_color()
        
        # Robe
        self.body = Entity(
            parent=self.entity,
            model='cube',
            scale=(0.45, 0.9, 0.45),
            position=(0, 0.45, 0),
            color=color.Color(1.0, 1.0, 0.78, 1.0),  # Light yellow
            unlit=True
        )
        
        # Head
        self.head = Entity(
            parent=self.entity,
            model='sphere',
            scale=0.28,
            position=(0, 1.05, 0),
            color=color.Color(1.0, 0.86, 0.7, 1.0),  # Skin tone
            unlit=True
        )
        
        # Halo
        halo = Entity(
            parent=self.entity,
            model='circle',
            scale=(0.3, 0.3, 0.05),
            position=(0, 1.4, 0),
            rotation=(90, 0, 0),
            color=color.Color(1.0, 0.84, 0.0, 1.0)  # Gold
        )
        
        # Staff with cross
        self.weapon = Entity(
            parent=self.entity,
            model='cube',
            scale=(0.06, 1.2, 0.06),
            position=(0.35, 0.6, 0),
            color=color.white
        )
        
        cross_h = Entity(
            parent=self.entity,
            model='cube',
            scale=(0.25, 0.06, 0.06),
            position=(0.35, 1.1, 0),
            color=color.Color(1.0, 0.84, 0.0, 1.0)  # Gold
        )
    
    def _create_default(self):
        """Create default unit model"""
        team_color = self._get_team_color()
        
        self.body = Entity(
            parent=self.entity,
            model='cube',
            scale=(0.5, 0.8, 0.5),
            position=(0, 0.4, 0),
            color=team_color,
            unlit=True
        )
        
        self.head = Entity(
            parent=self.entity,
            model='sphere',
            scale=0.3,
            position=(0, 1.0, 0),
            color=color.Color(1.0, 0.86, 0.7, 1.0),  # Skin tone
            unlit=True
        )
    
    def _create_health_bar(self):
        """Create health bar above unit"""
        bar_width = 0.8
        bar_height = 0.1
        
        # Background
        self.health_bar_bg = Entity(
            parent=self.entity,
            model='quad',
            scale=(bar_width, bar_height),
            position=(0, 1.8, 0),
            color=color.Color(0.24, 0.24, 0.24, 1.0),  # Dark gray
            billboard=True,
            unlit=True
        )
        
        # Health bar
        self.health_bar = Entity(
            parent=self.entity,
            model='quad',
            scale=(bar_width * self.unit.hp_percentage, bar_height * 0.8),
            position=(0, 1.8, -0.01),
            color=color.Color(0.2, 0.78, 0.2, 1.0),  # Green
            billboard=True,
            unlit=True
        )
    
    def _create_team_indicator(self):
        """Create team color indicator - large visible base"""
        team_col = self._get_team_color()
        
        # Outer glow ring (larger, semi-transparent)
        self.team_glow = Entity(
            parent=self.entity,
            model='circle',
            scale=1.4,
            position=(0, 0.02, 0),
            rotation=(90, 0, 0),
            color=color.Color(team_col.r, team_col.g, team_col.b, 0.4),
            unlit=True
        )
        
        # Main team indicator circle (solid, visible)
        self.team_indicator = Entity(
            parent=self.entity,
            model='circle',
            scale=1.0,
            position=(0, 0.03, 0),
            rotation=(90, 0, 0),
            color=team_col,
            unlit=True
        )
        
        # Inner ring for contrast
        self.team_ring = Entity(
            parent=self.entity,
            model='circle',
            scale=0.7,
            position=(0, 0.04, 0),
            rotation=(90, 0, 0),
            color=self._get_secondary_color(),
            unlit=True
        )
    
    def _create_selection_ring(self):
        """Create selection indicator ring"""
        self.selection_ring = Entity(
            parent=self.entity,
            model='circle',
            scale=(0.8, 0.8, 0.1),
            position=(0, 0.05, 0),
            rotation=(90, 0, 0),
            color=color.yellow,
            enabled=False
        )
    
    def _create_name_text(self):
        """Create floating name text with team color"""
        team_col = self._get_team_color()
        # Add team prefix to name for clarity
        team_prefix = "[RED] " if self.unit.team == Team.RED else "[BLUE] "
        
        self.name_text = Text(
            text=f"{team_prefix}{self.unit.name}",
            parent=self.entity,
            position=(0, 2.0, 0),
            scale=8,
            billboard=True,
            origin=(0, 0),
            color=team_col  # Name text colored by team
        )
    
    def update(self):
        """Update animations"""
        if not self.entity or not self.unit.is_alive:
            return
        
        # Idle animation (gentle hovering)
        self.idle_time += time.dt
        self.hover_offset = math.sin(self.idle_time * 2) * 0.05
        
        if self.body and not self.is_animating:
            self.body.y = 0.5 + self.hover_offset
    
    def update_health_bar(self):
        """Update health bar based on current HP"""
        if self.health_bar:
            hp_pct = self.unit.hp_percentage
            self.health_bar.scale_x = 0.8 * hp_pct
            
            # Color based on HP (using 0-1 range)
            if hp_pct > 0.6:
                self.health_bar.color = color.Color(0.2, 0.78, 0.2, 1.0)  # Green
            elif hp_pct > 0.3:
                self.health_bar.color = color.Color(1.0, 0.78, 0.2, 1.0)  # Yellow
            else:
                self.health_bar.color = color.Color(1.0, 0.2, 0.2, 1.0)  # Red
    
    def move_to(self, target_pos: Vec3, duration: float = 0.5):
        """Animate movement to target position"""
        if not self.entity:
            return
        
        self.is_animating = True
        start_pos = self.entity.position
        target = target_pos + Vec3(0, 0.5, 0)
        
        def animate_move():
            # Use Ursina's animation
            self.entity.animate_position(target, duration=duration, curve=curve.in_out_sine)
        
        animate_move()
        
        # Reset animation flag after completion
        invoke(self._end_animation, delay=duration)
    
    def attack_animation(self, target_view: 'UnitView'):
        """Play attack animation"""
        if not self.entity or not target_view.entity:
            return
        
        self.is_animating = True
        original_pos = self.entity.position
        
        # Lunge toward target
        direction = (target_view.entity.position - self.entity.position).normalized()
        lunge_pos = original_pos + direction * 0.5
        
        # Sequence: lunge forward, return
        self.entity.animate_position(lunge_pos, duration=0.15, curve=curve.out_sine)
        invoke(lambda: self.entity.animate_position(original_pos, duration=0.15), delay=0.2)
        invoke(self._end_animation, delay=0.4)
    
    def take_damage_animation(self):
        """Play damage taken animation"""
        if not self.body:
            return
        
        original_color = self.body.color
        
        # Flash red
        self.body.color = color.Color(1.0, 0.4, 0.4, 1.0)
        invoke(lambda: setattr(self.body, 'color', original_color), delay=0.2)
        
        # Shake
        original_x = self.entity.x
        shake_amount = 0.1
        
        def shake():
            self.entity.x = original_x + shake_amount
            invoke(lambda: setattr(self.entity, 'x', original_x - shake_amount), delay=0.05)
            invoke(lambda: setattr(self.entity, 'x', original_x), delay=0.1)
        
        shake()
    
    def ability_animation(self):
        """Play ability use animation"""
        if not self.entity:
            return
        
        self.is_animating = True
        
        # Glow effect
        if self.body:
            original_color = self.body.color
            glow_color = color.Color(1.0, 1.0, 0.78, 1.0)  # Light yellow glow
            
            self.body.color = glow_color
            invoke(lambda: setattr(self.body, 'color', original_color), delay=0.3)
        
        # Rise up
        original_y = self.entity.y
        self.entity.animate_y(original_y + 0.5, duration=0.2)
        invoke(lambda: self.entity.animate_y(original_y, duration=0.2), delay=0.25)
        invoke(self._end_animation, delay=0.5)
    
    def death_animation(self):
        """Play death animation"""
        if not self.entity:
            return
        
        self.is_animating = True
        
        # Fall over and fade out
        self.entity.animate_rotation((0, 0, 90), duration=0.5)
        self.entity.animate_y(self.entity.y - 0.3, duration=0.5)
        
        # Fade out all components
        def fade_out():
            for child in self.entity.children:
                if hasattr(child, 'color'):
                    try:
                        child.animate('color', color.Color(child.color.r, child.color.g, child.color.b, 0), duration=0.5)
                    except:
                        pass
        
        invoke(fade_out, delay=0.3)
        invoke(lambda: self.entity.disable(), delay=1.0)
    
    def select(self):
        """Show selection indicator"""
        if self.selection_ring:
            self.selection_ring.enabled = True
    
    def deselect(self):
        """Hide selection indicator"""
        if self.selection_ring:
            self.selection_ring.enabled = False
    
    def _end_animation(self):
        """End current animation"""
        self.is_animating = False
    
    def cleanup(self):
        """Clean up entity"""
        if self.entity:
            self.entity.disable()
