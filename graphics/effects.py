"""
Visual Effects System
Particle effects, damage numbers, and special ability effects
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List
import random
import math

from ursina import (
    Entity, color, Vec3, Text, time, destroy, invoke,
    Sequence, Func, Wait
)

from config.units import AbilityType

if TYPE_CHECKING:
    from .renderer import GameRenderer


class Particle(Entity):
    """Single particle for effects"""
    
    def __init__(self, **kwargs):
        self.velocity = kwargs.pop('velocity', Vec3(0, 0, 0))
        self.lifetime = kwargs.pop('lifetime', 1.0)
        self.gravity = kwargs.pop('gravity', -9.8)
        self.fade = kwargs.pop('fade', True)
        self.age = 0
        self.original_color = kwargs.get('color', color.white)
        
        super().__init__(**kwargs)
    
    def update(self):
        self.age += time.dt
        
        # Apply velocity
        self.position += self.velocity * time.dt
        
        # Apply gravity
        self.velocity.y += self.gravity * time.dt
        
        # Fade out
        if self.fade:
            alpha = max(0.0, min(1.0, 1.0 - (self.age / self.lifetime)))
            try:
                # Ursina colors use 0-1 range
                self.color = color.Color(
                    self.original_color.r,
                    self.original_color.g,
                    self.original_color.b,
                    alpha
                )
            except:
                pass
        
        # Destroy when lifetime exceeded
        if self.age >= self.lifetime:
            destroy(self)


class ParticleEmitter:
    """Emits particles over time"""
    
    def __init__(
        self,
        position: Vec3,
        particle_count: int = 20,
        particle_color: color = color.white,
        particle_size: float = 0.1,
        velocity_range: tuple = ((-1, 1), (2, 5), (-1, 1)),
        lifetime: float = 1.0,
        gravity: float = -9.8,
        burst: bool = True
    ):
        self.position = position
        self.particle_count = particle_count
        self.particle_color = particle_color
        self.particle_size = particle_size
        self.velocity_range = velocity_range
        self.lifetime = lifetime
        self.gravity = gravity
        
        self.particles: List[Particle] = []
        
        if burst:
            self._emit_burst()
    
    def _emit_burst(self):
        """Emit all particles at once"""
        for _ in range(self.particle_count):
            velocity = Vec3(
                random.uniform(*self.velocity_range[0]),
                random.uniform(*self.velocity_range[1]),
                random.uniform(*self.velocity_range[2])
            )
            
            particle = Particle(
                model='sphere',
                scale=self.particle_size * random.uniform(0.5, 1.5),
                position=self.position + Vec3(
                    random.uniform(-0.2, 0.2),
                    random.uniform(-0.2, 0.2),
                    random.uniform(-0.2, 0.2)
                ),
                color=self.particle_color,
                velocity=velocity,
                lifetime=self.lifetime * random.uniform(0.7, 1.3),
                gravity=self.gravity,
                unlit=True
            )
            
            self.particles.append(particle)


class DamageNumber(Entity):
    """Floating damage number"""
    
    def __init__(self, position: Vec3, damage: int, critical: bool = False, **kwargs):
        super().__init__(**kwargs)
        
        self.position = position
        self.age = 0
        self.lifetime = 1.5
        self.rise_speed = 2.0
        
        # Create text
        self.original_color = color.rgb(255, 255, 0) if critical else color.rgb(255, 100, 100)
        text_scale = 15 if critical else 12
        
        self.text = Text(
            text=f"{'-' if damage > 0 else '+'}{abs(damage)}{'!' if critical else ''}",
            parent=self,
            position=(0, 0, 0),
            scale=text_scale,
            color=self.original_color,
            billboard=True,
            origin=(0, 0)
        )
        
        if critical:
            self.text.text = f"CRIT! -{damage}"
    
    def update(self):
        if not hasattr(self, 'text') or self.text is None:
            return
            
        self.age += time.dt
        
        # Rise up
        self.y += self.rise_speed * time.dt
        self.rise_speed *= 0.95  # Slow down
        
        # Fade out
        alpha = max(0.0, min(1.0, 1.0 - (self.age / self.lifetime)))
        try:
            # Ursina colors use 0-1 range
            self.text.color = color.Color(
                self.original_color.r,
                self.original_color.g,
                self.original_color.b,
                alpha
            )
        except:
            pass
        
        # Destroy when done
        if self.age >= self.lifetime:
            destroy(self)


class VisualEffects:
    """
    Manages all visual effects in the game
    """
    
    def __init__(self, renderer: 'GameRenderer'):
        self.renderer = renderer
        self.active_effects: List[Entity] = []
    
    def show_damage(self, position: Vec3, damage: int, critical: bool = False):
        """Show floating damage number"""
        dmg_num = DamageNumber(
            position=position,
            damage=damage,
            critical=critical
        )
        self.active_effects.append(dmg_num)
    
    def show_heal(self, position: Vec3, amount: int):
        """Show floating heal number"""
        heal_num = DamageNumber(
            position=position,
            damage=-amount,  # Negative to show as heal
            critical=False
        )
        heal_num.text.color = color.rgb(100, 255, 100)
        self.active_effects.append(heal_num)
    
    def play_ability_effect(self, position: Vec3, ability_type: AbilityType):
        """Play visual effect for ability"""
        if ability_type == AbilityType.FIREBALL:
            self._fireball_effect(position)
        elif ability_type == AbilityType.HEAL:
            self._heal_effect(position)
        elif ability_type == AbilityType.SHIELD_WALL:
            self._shield_effect(position)
        elif ability_type == AbilityType.SNIPE:
            self._snipe_effect(position)
        elif ability_type == AbilityType.CHARGE:
            self._charge_effect(position)
    
    def _fireball_effect(self, position: Vec3):
        """Explosion effect for fireball"""
        # Orange/red particles
        ParticleEmitter(
            position=position,
            particle_count=30,
            particle_color=color.rgb(255, 100, 0),
            particle_size=0.15,
            velocity_range=((-3, 3), (2, 6), (-3, 3)),
            lifetime=1.0,
            gravity=-2
        )
        
        # Yellow core
        ParticleEmitter(
            position=position,
            particle_count=15,
            particle_color=color.rgb(255, 255, 100),
            particle_size=0.1,
            velocity_range=((-2, 2), (3, 5), (-2, 2)),
            lifetime=0.7,
            gravity=-1
        )
        
        # Flash sphere
        flash = Entity(
            model='sphere',
            position=position,
            scale=0.5,
            color=color.rgba(255, 200, 100, 200),
            unlit=True
        )
        flash.animate_scale(3, duration=0.3)
        flash.animate('color', color.rgba(255, 100, 0, 0), duration=0.3)
        invoke(lambda: destroy(flash), delay=0.35)
    
    def _heal_effect(self, position: Vec3):
        """Healing effect - green sparkles rising"""
        ParticleEmitter(
            position=position + Vec3(0, -0.5, 0),
            particle_count=25,
            particle_color=color.rgb(100, 255, 100),
            particle_size=0.08,
            velocity_range=((-0.5, 0.5), (2, 4), (-0.5, 0.5)),
            lifetime=1.5,
            gravity=0.5  # Float upward
        )
        
        # Healing ring
        ring = Entity(
            model='circle',
            position=position,
            scale=(0.1, 0.1, 0.02),
            rotation=(90, 0, 0),
            color=color.rgba(100, 255, 100, 200),
            unlit=True
        )
        ring.animate_scale((2, 2, 0.02), duration=0.5)
        ring.animate_y(position.y + 2, duration=0.5)
        ring.animate('color', color.rgba(100, 255, 100, 0), duration=0.5)
        invoke(lambda: destroy(ring), delay=0.55)
    
    def _shield_effect(self, position: Vec3):
        """Shield activation effect"""
        # Blue shield dome
        shield = Entity(
            model='sphere',
            position=position,
            scale=0.1,
            color=color.rgba(100, 150, 255, 100),
            unlit=True
        )
        shield.animate_scale(1.5, duration=0.3)
        shield.animate('color', color.rgba(100, 150, 255, 50), duration=0.5)
        invoke(lambda: destroy(shield), delay=2.0)
        
        # Sparkle particles
        ParticleEmitter(
            position=position,
            particle_count=15,
            particle_color=color.rgb(150, 200, 255),
            particle_size=0.06,
            velocity_range=((-1, 1), (0, 2), (-1, 1)),
            lifetime=1.0,
            gravity=-1
        )
    
    def _snipe_effect(self, position: Vec3):
        """Snipe hit effect"""
        # Impact flash
        flash = Entity(
            model='sphere',
            position=position,
            scale=0.2,
            color=color.rgba(255, 255, 200, 255),
            unlit=True
        )
        flash.animate_scale(0.8, duration=0.1)
        flash.animate('color', color.rgba(255, 255, 200, 0), duration=0.2)
        invoke(lambda: destroy(flash), delay=0.25)
        
        # Debris particles
        ParticleEmitter(
            position=position,
            particle_count=10,
            particle_color=color.rgb(200, 200, 200),
            particle_size=0.05,
            velocity_range=((-2, 2), (1, 3), (-2, 2)),
            lifetime=0.8,
            gravity=-15
        )
    
    def _charge_effect(self, position: Vec3):
        """Charge attack effect - dust trail"""
        ParticleEmitter(
            position=position + Vec3(0, 0.1, 0),
            particle_count=20,
            particle_color=color.rgb(180, 150, 100),
            particle_size=0.1,
            velocity_range=((-1, 1), (0.5, 2), (-1, 1)),
            lifetime=0.8,
            gravity=-2
        )
    
    def play_hit_effect(self, position: Vec3):
        """Generic hit effect"""
        # Small particle burst
        ParticleEmitter(
            position=position,
            particle_count=8,
            particle_color=color.rgb(255, 200, 200),
            particle_size=0.08,
            velocity_range=((-1.5, 1.5), (1, 3), (-1.5, 1.5)),
            lifetime=0.5,
            gravity=-8
        )
    
    def play_death_effect(self, position: Vec3, team_color: color):
        """Death effect for units"""
        # Soul rising
        soul = Entity(
            model='sphere',
            position=position,
            scale=0.3,
            color=color.rgba(200, 200, 255, 150),
            unlit=True
        )
        soul.animate_y(position.y + 3, duration=1.5)
        soul.animate_scale(0.1, duration=1.5)
        soul.animate('color', color.rgba(200, 200, 255, 0), duration=1.5)
        invoke(lambda: destroy(soul), delay=1.6)
        
        # Collapse particles
        ParticleEmitter(
            position=position,
            particle_count=15,
            particle_color=team_color,
            particle_size=0.1,
            velocity_range=((-1, 1), (0, 1), (-1, 1)),
            lifetime=1.0,
            gravity=-5
        )
    
    def cleanup(self):
        """Clean up all effects"""
        for effect in self.active_effects:
            if effect:
                destroy(effect)
        self.active_effects.clear()


# Alias for backward compatibility
ParticleEffects = VisualEffects
