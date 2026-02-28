"""
UI Overlay System
HUD, stats panels, and AI decision visualization
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List, Dict
from collections import deque

from ursina import (
    Entity, Text, color, camera, window, Vec2, Vec3,
    Button, time, invoke, destroy
)

from core.unit import Team
from config.settings import get_config, GameSpeed

if TYPE_CHECKING:
    from .renderer import GameRenderer
    from core.game_manager import MatchResult, AIDecision
    from ai.base_agent import BaseAgent


class UIOverlay:
    """
    Heads-up display and UI overlay
    Shows game stats, AI decisions, and controls
    """
    
    def __init__(self, renderer: 'GameRenderer'):
        self.renderer = renderer
        self.config = get_config()
        
        # UI containers
        self.root = Entity(parent=camera.ui)
        
        # Components
        self.stats_panel: Optional[Entity] = None
        self.action_log: Optional[Entity] = None
        self.turn_indicator: Optional[Entity] = None
        self.ai_thinking_panel: Optional[Entity] = None
        self.speed_indicator: Optional[Entity] = None
        self.controls_panel: Optional[Entity] = None
        self.game_over_panel: Optional[Entity] = None
        
        # Action log history
        self.log_messages: deque = deque(maxlen=8)
        self.log_texts: List[Text] = []
        
        # Build UI
        self._create_stats_panel()
        self._create_action_log()
        self._create_turn_indicator()
        self._create_ai_panel()
        self._create_speed_indicator()
        self._create_controls_help()
    
    def _create_stats_panel(self):
        """Create the stats panel showing team info"""
        # Panel background
        self.stats_panel = Entity(
            parent=self.root,
            model='quad',
            scale=(0.35, 0.25),
            position=(-0.55, 0.35),
            color=color.rgba(20, 20, 30, 200)
        )
        
        # Title
        self.stats_title = Text(
            text='⚔️ BATTLE STATS ⚔️',
            parent=self.stats_panel,
            position=(-0.45, 0.4),
            scale=1.2,
            color=color.white
        )
        
        # Red team stats
        self.red_team_label = Text(
            text='🔴 RED TEAM (Minimax)',
            parent=self.stats_panel,
            position=(-0.45, 0.25),
            scale=1.0,
            color=color.rgb(255, 100, 100)
        )
        
        self.red_stats_text = Text(
            text='Units: 4 | HP: 100%',
            parent=self.stats_panel,
            position=(-0.45, 0.1),
            scale=0.9,
            color=color.white
        )
        
        # Blue team stats
        self.blue_team_label = Text(
            text='🔵 BLUE TEAM (Fuzzy)',
            parent=self.stats_panel,
            position=(-0.45, -0.1),
            scale=1.0,
            color=color.rgb(100, 150, 255)
        )
        
        self.blue_stats_text = Text(
            text='Units: 4 | HP: 100%',
            parent=self.stats_panel,
            position=(-0.45, -0.25),
            scale=0.9,
            color=color.white
        )
        
        # Turn counter
        self.turn_text = Text(
            text='Turn: 1',
            parent=self.stats_panel,
            position=(-0.45, -0.4),
            scale=1.0,
            color=color.yellow
        )
    
    def _create_action_log(self):
        """Create the action log panel"""
        # Panel background
        self.action_log = Entity(
            parent=self.root,
            model='quad',
            scale=(0.35, 0.35),
            position=(0.55, 0.25),
            color=color.rgba(20, 20, 30, 200)
        )
        
        # Title
        self.log_title = Text(
            text='📜 ACTION LOG',
            parent=self.action_log,
            position=(-0.45, 0.45),
            scale=1.2,
            color=color.white
        )
        
        # Log entries
        for i in range(8):
            log_text = Text(
                text='',
                parent=self.action_log,
                position=(-0.45, 0.3 - i * 0.1),
                scale=0.7,
                color=color.rgb(200, 200, 200)
            )
            self.log_texts.append(log_text)
    
    def _create_turn_indicator(self):
        """Create the turn indicator at top center"""
        self.turn_indicator = Entity(
            parent=self.root,
            model='quad',
            scale=(0.4, 0.08),
            position=(0, 0.45),
            color=color.rgba(0, 0, 0, 0)
        )
        
        self.turn_indicator_text = Text(
            text='RED TURN',
            parent=self.turn_indicator,
            position=(0, 0),
            scale=2,
            origin=(0, 0),
            color=color.rgb(255, 100, 100)
        )
    
    def _create_ai_panel(self):
        """Create AI thinking/decision panel"""
        self.ai_thinking_panel = Entity(
            parent=self.root,
            model='quad',
            scale=(0.35, 0.2),
            position=(-0.55, -0.25),
            color=color.rgba(20, 20, 30, 200)
        )
        
        self.ai_title = Text(
            text='🤖 AI THINKING',
            parent=self.ai_thinking_panel,
            position=(-0.45, 0.35),
            scale=1.2,
            color=color.white
        )
        
        self.ai_name_text = Text(
            text='Agent: --',
            parent=self.ai_thinking_panel,
            position=(-0.45, 0.15),
            scale=0.9,
            color=color.cyan
        )
        
        self.ai_reasoning_text = Text(
            text='Reasoning: --',
            parent=self.ai_thinking_panel,
            position=(-0.45, -0.05),
            scale=0.8,
            color=color.rgb(200, 200, 200),
            wordwrap=30
        )
        
        self.ai_score_text = Text(
            text='Score: --',
            parent=self.ai_thinking_panel,
            position=(-0.45, -0.3),
            scale=0.9,
            color=color.yellow
        )
    
    def _create_speed_indicator(self):
        """Create game speed indicator"""
        self.speed_indicator = Entity(
            parent=self.root,
            model='quad',
            scale=(0.15, 0.05),
            position=(0, -0.45),
            color=color.rgba(20, 20, 30, 200)
        )
        
        self.speed_text = Text(
            text='Speed: 1.0x',
            parent=self.speed_indicator,
            position=(0, 0),
            scale=1.5,
            origin=(0, 0),
            color=color.white
        )
    
    def _create_controls_help(self):
        """Create controls help panel"""
        self.controls_panel = Entity(
            parent=self.root,
            model='quad',
            scale=(0.35, 0.15),
            position=(0.55, -0.35),
            color=color.rgba(20, 20, 30, 180)
        )
        
        controls_text = (
            "🎮 CONTROLS\n"
            "WASD/Arrows: Pan Camera\n"
            "Q/E: Zoom In/Out\n"
            "1-4: Speed (0.5x-4x)\n"
            "Space: Pause/Resume"
        )
        
        self.controls_text = Text(
            text=controls_text,
            parent=self.controls_panel,
            position=(-0.45, 0.35),
            scale=0.8,
            color=color.rgb(180, 180, 180),
            line_height=1.5
        )
    
    def update(self):
        """Update UI elements"""
        pass
    
    def update_stats(self):
        """Update the stats display"""
        if not self.renderer.game_state:
            return
        
        state = self.renderer.game_state
        
        # Red team
        red_alive = len(state.red_team.alive_units)
        red_hp_pct = (state.red_team.total_hp / state.red_team.max_total_hp * 100) if state.red_team.max_total_hp > 0 else 0
        self.red_stats_text.text = f'Units: {red_alive} | HP: {red_hp_pct:.0f}% | DMG: {state.stats["total_damage_red"]}'
        
        # Blue team
        blue_alive = len(state.blue_team.alive_units)
        blue_hp_pct = (state.blue_team.total_hp / state.blue_team.max_total_hp * 100) if state.blue_team.max_total_hp > 0 else 0
        self.blue_stats_text.text = f'Units: {blue_alive} | HP: {blue_hp_pct:.0f}% | DMG: {state.stats["total_damage_blue"]}'
        
        # Turn
        self.turn_text.text = f'Turn: {state.current_turn + 1}'
        
        # Speed
        if self.renderer.game_manager:
            speed = self.renderer.game_manager.game_speed.value
            self.speed_text.text = f'Speed: {speed}x'
    
    def add_action_log(self, message: str):
        """Add a message to the action log"""
        self.log_messages.append(message)
        
        # Update log display
        for i, text_entity in enumerate(self.log_texts):
            if i < len(self.log_messages):
                # Show from newest to oldest
                idx = len(self.log_messages) - 1 - i
                if idx >= 0:
                    text_entity.text = self.log_messages[idx]
                    # Fade older messages
                    alpha = 255 - (i * 25)
                    text_entity.color = color.rgba(200, 200, 200, alpha)
            else:
                text_entity.text = ''
    
    def show_turn_indicator(self, team: Team):
        """Show whose turn it is"""
        if team == Team.RED:
            self.turn_indicator_text.text = '🔴 RED TURN - Minimax AI'
            self.turn_indicator_text.color = color.rgb(255, 100, 100)
        else:
            self.turn_indicator_text.text = '🔵 BLUE TURN - Fuzzy AI'
            self.turn_indicator_text.color = color.rgb(100, 150, 255)
        
        # Flash animation
        self.turn_indicator.scale = (0.5, 0.1)
        self.turn_indicator.animate_scale((0.4, 0.08), duration=0.3)
    
    def show_thinking(self, agent: 'BaseAgent'):
        """Show AI is thinking"""
        self.ai_title.text = '🤖 AI THINKING...'
        self.ai_name_text.text = f'Agent: {agent.name}'
        self.ai_reasoning_text.text = 'Analyzing positions...'
        self.ai_score_text.text = 'Score: calculating...'
        
        # Pulsing effect
        self.ai_thinking_panel.color = color.rgba(30, 30, 50, 200)
    
    def show_decision(self, decision: 'AIDecision'):
        """Show AI decision details"""
        self.ai_title.text = '🎯 AI DECISION'
        
        team_name = 'RED (Minimax)' if decision.team == Team.RED else 'BLUE (Fuzzy)'
        self.ai_name_text.text = f'Agent: {team_name}'
        
        # Truncate reasoning if too long
        reasoning = decision.reasoning
        if len(reasoning) > 100:
            reasoning = reasoning[:100] + '...'
        self.ai_reasoning_text.text = reasoning
        
        self.ai_score_text.text = f'Score: {decision.evaluation_score:.2f} | Time: {decision.thinking_time:.3f}s'
        
        self.ai_thinking_panel.color = color.rgba(20, 20, 30, 200)
    
    def show_game_over(self, result: 'MatchResult'):
        """Show game over screen"""
        # Create game over panel
        self.game_over_panel = Entity(
            parent=self.root,
            model='quad',
            scale=(0.6, 0.5),
            position=(0, 0),
            color=color.rgba(10, 10, 20, 230)
        )
        
        # Winner announcement
        if result.winner == Team.RED:
            winner_text = '🏆 RED TEAM WINS! 🏆'
            winner_color = color.Color(1.0, 0.4, 0.4, 1.0)  # Red
            winner_ai = 'Minimax Alpha-Beta'
        elif result.winner == Team.BLUE:
            winner_text = '🏆 BLUE TEAM WINS! 🏆'
            winner_color = color.Color(0.4, 0.6, 1.0, 1.0)  # Blue
            winner_ai = 'Fuzzy Logic'
        else:
            winner_text = '⚔️ DRAW! ⚔️'
            winner_color = color.yellow
            winner_ai = 'Neither'
        
        self.winner_text = Text(
            text=winner_text,
            parent=self.game_over_panel,
            position=(0, 0.35),
            scale=3,
            origin=(0, 0),
            color=winner_color
        )
        
        self.winner_ai_text = Text(
            text=f'Winning AI: {winner_ai}',
            parent=self.game_over_panel,
            position=(0, 0.2),
            scale=2,
            origin=(0, 0),
            color=color.white
        )
        
        # Stats
        stats_text = (
            f"Total Turns: {result.total_turns}\n"
            f"Duration: {result.duration_seconds:.1f}s\n\n"
            f"🔴 Red: {result.red_units_remaining} units, {result.red_total_damage} damage dealt\n"
            f"🔵 Blue: {result.blue_units_remaining} units, {result.blue_total_damage} damage dealt"
        )
        
        self.stats_summary = Text(
            text=stats_text,
            parent=self.game_over_panel,
            position=(0, -0.05),
            scale=1.5,
            origin=(0, 0),
            color=color.Color(0.78, 0.78, 0.78, 1.0),  # Light gray
            line_height=1.5
        )
        
        # Restart hint
        self.restart_hint = Text(
            text='Press R to restart or ESC to quit',
            parent=self.game_over_panel,
            position=(0, -0.35),
            scale=1.2,
            origin=(0, 0),
            color=color.Color(0.6, 0.6, 0.6, 1.0)  # Gray
        )
    
    def cleanup(self):
        """Clean up UI elements"""
        if self.root:
            destroy(self.root, delay=0)
