"""
Game Manager
Main game loop and orchestration for AI vs AI battles
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Callable, TYPE_CHECKING
from enum import Enum, auto
import time
import threading

from .game_state import GameState, GamePhase, Action, ActionResult
from .unit import Team
from config.settings import get_config, GameSpeed

if TYPE_CHECKING:
    from ai.base_agent import BaseAgent


class MatchStatus(Enum):
    """Current match status"""
    NOT_STARTED = auto()
    RUNNING = auto()
    PAUSED = auto()
    FINISHED = auto()


@dataclass
class MatchResult:
    """Result of a completed match"""
    winner: Optional[Team]
    end_reason: str
    total_turns: int
    red_units_remaining: int
    blue_units_remaining: int
    red_total_damage: int
    blue_total_damage: int
    red_match_score: float
    blue_match_score: float
    timed_out: bool
    duration_seconds: float
    final_state: GameState


@dataclass
class AIDecision:
    """Record of an AI's decision"""
    team: Team
    action: Action
    thinking_time: float
    evaluation_score: float
    reasoning: str


class GameManager:
    """
    Orchestrates the game flow for AI vs AI matches
    Handles turn management, AI execution, and event callbacks
    """
    
    def __init__(
        self,
        game_state: Optional[GameState] = None,
        red_agent: Optional[BaseAgent] = None,
        blue_agent: Optional[BaseAgent] = None
    ):
        self.game_state = game_state
        self.red_agent = red_agent
        self.blue_agent = blue_agent
        
        self.config = get_config()
        self.status = MatchStatus.NOT_STARTED
        self.game_speed = self.config.game_speed
        
        # Event callbacks
        self._on_turn_start: List[Callable] = []
        self._on_turn_end: List[Callable] = []
        self._on_action_executed: List[Callable] = []
        self._on_game_over: List[Callable] = []
        self._on_ai_thinking: List[Callable] = []
        self._on_ai_decision: List[Callable] = []
        
        # Match history
        self.decisions_history: List[AIDecision] = []
        self.match_start_time: float = 0
        
        # Async control
        self._stop_requested = False
        self._pause_requested = False
        self._game_thread: Optional[threading.Thread] = None
    
    def setup_new_game(
        self,
        battlefield_width: int = 12,
        battlefield_height: int = 12,
        units_per_team: int = 4,
        seed: Optional[int] = None
    ):
        """Initialize a new game"""
        self.game_state = GameState.create_new_game(
            battlefield_width=battlefield_width,
            battlefield_height=battlefield_height,
            units_per_team=units_per_team,
            seed=seed
        )
        self.status = MatchStatus.NOT_STARTED
        self.decisions_history.clear()
        self._stop_requested = False
        self._pause_requested = False
    
    def set_agents(self, red_agent: BaseAgent, blue_agent: BaseAgent):
        """Set the AI agents for both teams"""
        self.red_agent = red_agent
        self.blue_agent = blue_agent
        red_agent.team = Team.RED
        blue_agent.team = Team.BLUE
    
    def get_current_agent(self) -> Optional[BaseAgent]:
        """Get the agent for the current turn"""
        if self.game_state.current_phase == GamePhase.RED_TURN:
            return self.red_agent
        elif self.game_state.current_phase == GamePhase.BLUE_TURN:
            return self.blue_agent
        return None
    
    # Event registration
    def on_turn_start(self, callback: Callable):
        """Register callback for turn start"""
        self._on_turn_start.append(callback)
    
    def on_turn_end(self, callback: Callable):
        """Register callback for turn end"""
        self._on_turn_end.append(callback)
    
    def on_action_executed(self, callback: Callable):
        """Register callback for action execution"""
        self._on_action_executed.append(callback)
    
    def on_game_over(self, callback: Callable):
        """Register callback for game end"""
        self._on_game_over.append(callback)
    
    def on_ai_thinking(self, callback: Callable):
        """Register callback for AI thinking phase"""
        self._on_ai_thinking.append(callback)
    
    def on_ai_decision(self, callback: Callable):
        """Register callback for AI decision made"""
        self._on_ai_decision.append(callback)
    
    # Event triggers
    def _trigger_turn_start(self):
        for cb in self._on_turn_start:
            try:
                cb(self.game_state)
            except Exception as e:
                print(f"Error in turn_start callback: {e}")
    
    def _trigger_turn_end(self):
        for cb in self._on_turn_end:
            try:
                cb(self.game_state)
            except Exception as e:
                print(f"Error in turn_end callback: {e}")
    
    def _trigger_action_executed(self, result: ActionResult):
        for cb in self._on_action_executed:
            try:
                cb(self.game_state, result)
            except Exception as e:
                print(f"Error in action_executed callback: {e}")
    
    def _trigger_game_over(self, result: MatchResult):
        for cb in self._on_game_over:
            try:
                cb(result)
            except Exception as e:
                print(f"Error in game_over callback: {e}")
    
    def _trigger_ai_thinking(self, agent: BaseAgent):
        for cb in self._on_ai_thinking:
            try:
                cb(agent)
            except Exception as e:
                print(f"Error in ai_thinking callback: {e}")
    
    def _trigger_ai_decision(self, decision: AIDecision):
        for cb in self._on_ai_decision:
            try:
                cb(decision)
            except Exception as e:
                print(f"Error in ai_decision callback: {e}")
    
    def execute_single_turn(self) -> bool:
        """
        Execute a single turn for the current team
        Returns True if game continues, False if game over
        """
        if self.game_state.is_game_over:
            return False
        
        agent = self.get_current_agent()
        if not agent:
            return False
        
        self._trigger_turn_start()
        
        # AI makes decisions until turn is complete
        turn_complete = False
        while not turn_complete and not self._stop_requested:
            # Check if any units can still act
            units_that_can_act = self.game_state.current_team.get_units_that_can_act()
            if not units_that_can_act:
                turn_complete = True
                break
            
            # AI thinking
            self._trigger_ai_thinking(agent)
            
            start_time = time.time()
            action, evaluation, reasoning = agent.get_action(self.game_state)
            thinking_time = time.time() - start_time
            
            if action is None:
                # No valid action, end turn
                turn_complete = True
                break
            
            # Record decision
            decision = AIDecision(
                team=self.game_state.current_team.team,
                action=action,
                thinking_time=thinking_time,
                evaluation_score=evaluation,
                reasoning=reasoning
            )
            self.decisions_history.append(decision)
            self._trigger_ai_decision(decision)
            
            # Execute action
            result = self.game_state.execute_action(action)
            self._trigger_action_executed(result)
            
            # Speed delay for visualization
            delay = self.config.ai.decision_delay / self.game_speed.value
            time.sleep(delay)
            
            # Check for game over after each action
            if self.game_state.is_game_over:
                return False
        
        # End turn
        self.game_state.end_turn()
        self._trigger_turn_end()
        
        return not self.game_state.is_game_over
    
    def run_match(self) -> MatchResult:
        """Run a complete match until game over"""
        if not self.game_state or not self.red_agent or not self.blue_agent:
            raise RuntimeError("Game not properly initialized")
        
        self.status = MatchStatus.RUNNING
        self.match_start_time = time.time()
        
        # Initialize first turn
        self.game_state.start_turn()
        
        timed_out = False
        ended_by_turn_limit = False

        while not self.game_state.is_game_over and not self._stop_requested:
            if self._pause_requested:
                self.status = MatchStatus.PAUSED
                while self._pause_requested and not self._stop_requested:
                    time.sleep(0.1)
                self.status = MatchStatus.RUNNING

            # Time-based match stop: decide winner by overall team score
            elapsed = time.time() - self.match_start_time
            if elapsed >= self.config.match_timeout_seconds:
                timed_out = True
                break
            
            self.execute_single_turn()
            
            # Safety: max turns
            if self.game_state.current_turn >= self.config.max_turns:
                ended_by_turn_limit = True
                break
        
        # Create result
        duration = time.time() - self.match_start_time
        red_score = self._calculate_team_score(Team.RED)
        blue_score = self._calculate_team_score(Team.BLUE)

        if self.game_state.is_game_over:
            winner = self.game_state.winner
            end_reason = 'elimination'
        elif timed_out or ended_by_turn_limit:
            if red_score > blue_score:
                winner = Team.RED
            elif blue_score > red_score:
                winner = Team.BLUE
            else:
                winner = None
            end_reason = 'timeout_score' if timed_out else 'turn_limit_score'
        else:
            winner = self.game_state.winner
            end_reason = 'stopped'

        result = MatchResult(
            winner=winner,
            end_reason=end_reason,
            total_turns=self.game_state.current_turn,
            red_units_remaining=len(self.game_state.red_team.alive_units),
            blue_units_remaining=len(self.game_state.blue_team.alive_units),
            red_total_damage=self.game_state.stats['total_damage_red'],
            blue_total_damage=self.game_state.stats['total_damage_blue'],
            red_match_score=red_score,
            blue_match_score=blue_score,
            timed_out=timed_out,
            duration_seconds=duration,
            final_state=self.game_state
        )
        
        self.status = MatchStatus.FINISHED
        self._trigger_game_over(result)
        
        return result

    def _calculate_team_score(self, team: Team) -> float:
        """Calculate final match score used for timeout/turn-limit winner resolution."""
        if team == Team.RED:
            team_state = self.game_state.red_team
            damage_dealt = self.game_state.stats['total_damage_red']
            kills = self.game_state.stats['units_killed_red']
        else:
            team_state = self.game_state.blue_team
            damage_dealt = self.game_state.stats['total_damage_blue']
            kills = self.game_state.stats['units_killed_blue']

        units_alive = len(team_state.alive_units)
        total_hp = team_state.total_hp

        # Balanced score: survival > kills > pressure dealt.
        return (
            units_alive * 1000.0 +
            total_hp * 2.0 +
            kills * 300.0 +
            damage_dealt * 1.0
        )
    
    def run_match_async(self) -> threading.Thread:
        """Run match in background thread"""
        self._game_thread = threading.Thread(target=self.run_match)
        self._game_thread.start()
        return self._game_thread
    
    def pause(self):
        """Pause the game"""
        self._pause_requested = True
    
    def resume(self):
        """Resume the game"""
        self._pause_requested = False
    
    def stop(self):
        """Stop the game"""
        self._stop_requested = True
    
    def set_speed(self, speed: GameSpeed):
        """Change game speed"""
        self.game_speed = speed
    
    def get_match_statistics(self) -> Dict[str, Any]:
        """Get current match statistics"""
        if not self.game_state:
            return {}
        
        return {
            'current_turn': self.game_state.current_turn,
            'current_phase': self.game_state.current_phase.name,
            'red_units_alive': len(self.game_state.red_team.alive_units),
            'blue_units_alive': len(self.game_state.blue_team.alive_units),
            'red_total_hp': self.game_state.red_team.total_hp,
            'blue_total_hp': self.game_state.blue_team.total_hp,
            'red_damage_dealt': self.game_state.stats['total_damage_red'],
            'blue_damage_dealt': self.game_state.stats['total_damage_blue'],
            'red_kills': self.game_state.stats['units_killed_red'],
            'blue_kills': self.game_state.stats['units_killed_blue'],
            'total_decisions': len(self.decisions_history),
            'avg_thinking_time': sum(d.thinking_time for d in self.decisions_history) / len(self.decisions_history) if self.decisions_history else 0
        }
