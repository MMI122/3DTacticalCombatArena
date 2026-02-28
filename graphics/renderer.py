"""
Main Game Renderer
Orchestrates all 3D rendering using Ursina engine
"""

from __future__ import annotations
from typing import Optional, Dict, List, Callable, TYPE_CHECKING
from dataclasses import dataclass
import math

from ursina import (
    Ursina, Entity, window, camera, color, held_keys, time,
    Vec3, Vec2, mouse, Sky, DirectionalLight, AmbientLight,
    PointLight, invoke, application
)
from ursina.prefabs.first_person_controller import FirstPersonController

from config.settings import get_config, GameSpeed
from core.game_state import GameState, GamePhase, ActionResult
from core.unit import Team

if TYPE_CHECKING:
    from core.game_manager import GameManager, AIDecision


@dataclass
class CameraState:
    """Camera position and rotation state"""
    position: Vec3
    rotation: Vec3
    zoom: float


class GameRenderer:
    """
    Main rendering system using Ursina 3D engine
    Handles all visual aspects of the game
    """
    
    def __init__(self):
        self.app: Optional[Ursina] = None
        self.config = get_config()
        
        # View components
        self.battlefield_view: Optional['BattlefieldView'] = None
        self.unit_views: Dict[str, 'UnitView'] = {}
        self.ui_overlay: Optional['UIOverlay'] = None
        self.effects: Optional['VisualEffects'] = None
        
        # Game reference
        self.game_manager: Optional['GameManager'] = None
        self.game_state: Optional[GameState] = None
        
        # Camera
        self.camera_state = CameraState(
            position=Vec3(*self.config.camera.initial_position),
            rotation=Vec3(*self.config.camera.initial_rotation),
            zoom=45.0  # Start zoomed out to see full battlefield
        )
        self.camera_target = Vec3(0, 0, 0)
        
        # State
        self.is_initialized = False
        self.paused = False
        
        # Animation queue
        self.animation_queue: List[Callable] = []
        self.current_animation: Optional[Callable] = None
    
    def initialize(self):
        """Initialize the Ursina application"""
        if self.is_initialized:
            return
        
        # Create Ursina app
        self.app = Ursina(
            title='3D Tactical Combat Arena - AI vs AI',
            borderless=False,
            fullscreen=self.config.graphics.fullscreen,
            development_mode=False,
            vsync=self.config.graphics.vsync
        )
        
        # Window settings
        window.size = (int(self.config.graphics.window_width), int(self.config.graphics.window_height))
        window.fps_counter.enabled = True
        window.exit_button.visible = False
        
        # Setup lighting
        self._setup_lighting()
        
        # Setup camera
        self._setup_camera()
        
        # Setup sky
        self._setup_environment()
        
        # Import views here to avoid circular imports
        from .battlefield_view import BattlefieldView
        from .unit_view import UnitView
        from .ui_overlay import UIOverlay
        from .effects import VisualEffects
        
        self.BattlefieldView = BattlefieldView
        self.UnitView = UnitView
        self.UIOverlay = UIOverlay
        self.VisualEffects = VisualEffects
        
        self.is_initialized = True
    
    def _setup_lighting(self):
        """Setup scene lighting for dramatic effect"""
        # Main directional light (sun)
        self.sun = DirectionalLight(
            shadows=True,
            shadow_map_resolution=(2048, 2048)
        )
        self.sun.look_at(Vec3(1, -1, 1))
        
        # Ambient light
        self.ambient = AmbientLight(
            color=color.rgba(100, 100, 120, 255)
        )
        
        # Additional fill lights
        self.fill_light_1 = PointLight(
            position=Vec3(-10, 15, -10),
            color=color.rgba(255, 200, 150, 100)
        )
        
        self.fill_light_2 = PointLight(
            position=Vec3(10, 15, 10),
            color=color.rgba(150, 200, 255, 80)
        )
    
    def _setup_camera(self):
        """Setup camera with controls"""
        camera.orthographic = False
        camera.fov = 60
        
        # Position camera
        camera.position = self.camera_state.position
        camera.rotation = self.camera_state.rotation
    
    def _setup_environment(self):
        """Setup sky and environment"""
        # Simple colored background - use Ursina's built-in colors
        window.color = color.azure  # Sky blue background
        
        # Add ambient light so entities are visible
        from ursina import AmbientLight
        ambient = AmbientLight(color=color.Color(0.6, 0.6, 0.6, 1.0))
    
    def setup_game(self, game_manager: 'GameManager'):
        """Setup the game visuals"""
        self.game_manager = game_manager
        self.game_state = game_manager.game_state
        
        # Create battlefield view
        self.battlefield_view = self.BattlefieldView(
            self.game_state.battlefield,
            self
        )
        
        # Create unit views
        self._create_unit_views()
        
        # Create UI overlay
        self.ui_overlay = self.UIOverlay(self)
        
        # Create effects system
        self.effects = self.VisualEffects(self)
        
        # Center camera on battlefield
        center_x = self.game_state.battlefield.width * self.config.battlefield.cell_size / 2
        center_z = self.game_state.battlefield.height * self.config.battlefield.cell_size / 2
        self.camera_target = Vec3(center_x, 0, center_z)
        self._update_camera()
        
        # Register callbacks with game manager
        self._register_game_callbacks()
    
    def _create_unit_views(self):
        """Create visual representations for all units"""
        for unit in self.game_state.get_all_units():
            unit_view = self.UnitView(unit, self)
            self.unit_views[unit.id] = unit_view
    
    def _register_game_callbacks(self):
        """Register callbacks for game events"""
        self.game_manager.on_action_executed(self._on_action_executed)
        self.game_manager.on_turn_start(self._on_turn_start)
        self.game_manager.on_turn_end(self._on_turn_end)
        self.game_manager.on_game_over(self._on_game_over)
        self.game_manager.on_ai_thinking(self._on_ai_thinking)
        self.game_manager.on_ai_decision(self._on_ai_decision)
    
    def _on_action_executed(self, state: GameState, result: ActionResult):
        """Handle action execution visual"""
        from core.game_state import ActionType
        
        unit_view = self.unit_views.get(result.action.unit_id)
        if not unit_view:
            return
        
        if result.action.action_type == ActionType.MOVE:
            # Animate movement
            target = result.action.target_position
            world_pos = self.battlefield_view.grid_to_world(target.x, target.y)
            unit_view.move_to(world_pos, duration=0.3)
        
        elif result.action.action_type == ActionType.ATTACK:
            # Animate attack
            target_view = self.unit_views.get(result.action.target_unit_id)
            if target_view:
                unit_view.attack_animation(target_view)
                
                # Show damage number
                if self.effects:
                    self.effects.show_damage(
                        target_view.entity.position + Vec3(0, 2, 0),
                        result.damage_dealt,
                        result.critical_hit
                    )
                
                # Flash target
                target_view.take_damage_animation()
                
                # Update health bar
                target_view.update_health_bar()
                
                # If killed, play death animation
                if result.unit_killed:
                    target_view.death_animation()
        
        elif result.action.action_type == ActionType.ABILITY:
            unit_view.ability_animation()
            if self.effects and result.action.target_position:
                world_pos = self.battlefield_view.grid_to_world(
                    result.action.target_position.x,
                    result.action.target_position.y
                )
                self.effects.play_ability_effect(
                    world_pos,
                    result.action.ability_type
                )
        
        # Update UI
        if self.ui_overlay:
            self.ui_overlay.update_stats()
            self.ui_overlay.add_action_log(result.message)
    
    def _on_turn_start(self, state: GameState):
        """Handle turn start"""
        if self.ui_overlay:
            self.ui_overlay.show_turn_indicator(state.current_team.team)
    
    def _on_turn_end(self, state: GameState):
        """Handle turn end"""
        pass
    
    def _on_game_over(self, result):
        """Handle game over"""
        if self.ui_overlay:
            self.ui_overlay.show_game_over(result)
    
    def _on_ai_thinking(self, agent):
        """Handle AI thinking state"""
        if self.ui_overlay:
            self.ui_overlay.show_thinking(agent)
    
    def _on_ai_decision(self, decision: 'AIDecision'):
        """Handle AI decision made"""
        if self.ui_overlay:
            self.ui_overlay.show_decision(decision)
    
    def _update_camera(self):
        """Update camera position"""
        # Calculate camera position based on target and zoom
        offset = Vec3(
            0,
            self.camera_state.zoom * math.sin(math.radians(45)),
            -self.camera_state.zoom * math.cos(math.radians(45))
        )
        
        camera.position = self.camera_target + offset
        camera.look_at(self.camera_target)
    
    def update(self):
        """Called every frame - handle input and animations"""
        # Camera controls
        self._handle_camera_input()
        
        # Update animations
        self._update_animations()
        
        # Update UI
        if self.ui_overlay:
            self.ui_overlay.update()
    
    def _handle_camera_input(self):
        """Handle camera movement and rotation"""
        # Pan with WASD or arrow keys
        pan_speed = self.config.camera.pan_speed * time.dt
        
        if held_keys['w'] or held_keys['up arrow']:
            self.camera_target.z += pan_speed
        if held_keys['s'] or held_keys['down arrow']:
            self.camera_target.z -= pan_speed
        if held_keys['a'] or held_keys['left arrow']:
            self.camera_target.x -= pan_speed
        if held_keys['d'] or held_keys['right arrow']:
            self.camera_target.x += pan_speed
        
        # Zoom with Q/E or mouse wheel
        zoom_speed = self.config.camera.zoom_speed
        
        if held_keys['q']:
            self.camera_state.zoom = min(
                self.config.camera.max_zoom,
                self.camera_state.zoom + zoom_speed * time.dt * 10
            )
        if held_keys['e']:
            self.camera_state.zoom = max(
                self.config.camera.min_zoom,
                self.camera_state.zoom - zoom_speed * time.dt * 10
            )
        
        # Speed controls
        if held_keys['1']:
            self.game_manager.set_speed(GameSpeed.SLOW)
        if held_keys['2']:
            self.game_manager.set_speed(GameSpeed.NORMAL)
        if held_keys['3']:
            self.game_manager.set_speed(GameSpeed.FAST)
        if held_keys['4']:
            self.game_manager.set_speed(GameSpeed.ULTRA_FAST)
        
        # Pause with space
        if held_keys['space']:
            if self.paused:
                self.game_manager.resume()
                self.paused = False
            else:
                self.game_manager.pause()
                self.paused = True
        
        self._update_camera()
    
    def _update_animations(self):
        """Update ongoing animations"""
        for unit_view in self.unit_views.values():
            unit_view.update()
    
    def run(self):
        """Start the Ursina application"""
        if not self.is_initialized:
            self.initialize()
        
        # Set update function
        def ursina_update():
            self.update()
        
        # Override Ursina's update
        from ursina import Entity
        updater = Entity()
        updater.update = ursina_update
        
        # Run the app
        self.app.run()
    
    def cleanup(self):
        """Cleanup resources"""
        if self.battlefield_view:
            self.battlefield_view.cleanup()
        
        for unit_view in self.unit_views.values():
            unit_view.cleanup()
        
        if self.ui_overlay:
            self.ui_overlay.cleanup()
