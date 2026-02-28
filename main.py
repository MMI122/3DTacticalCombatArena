"""
3D Tactical Combat Arena - AI vs AI
Main Entry Point

A production-grade 3D game featuring:
- Minimax with Alpha-Beta Pruning AI (Red Team)
- Fuzzy Logic AI (Blue Team)
- Beautiful 3D visualization with Ursina engine
- Real-time AI decision visualization

Author: AI Game Studio
Version: 1.0.0
"""

import sys
import argparse
import threading
from typing import Optional

# Ensure proper imports
sys.path.insert(0, '.')

from config.settings import get_config, update_config, GameSpeed
from core.game_state import GameState
from core.game_manager import GameManager
from ai.minimax_agent import MinimaxAgent
from ai.fuzzy_agent import FuzzyLogicAgent
from core.unit import Team


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='3D Tactical Combat Arena - AI vs AI Battle'
    )
    
    parser.add_argument(
        '--width', type=int, default=12,
        help='Battlefield width (default: 12)'
    )
    parser.add_argument(
        '--height', type=int, default=12,
        help='Battlefield height (default: 12)'
    )
    parser.add_argument(
        '--units', type=int, default=4,
        help='Units per team (default: 4)'
    )
    parser.add_argument(
        '--seed', type=int, default=None,
        help='Random seed for battlefield generation'
    )
    parser.add_argument(
        '--depth', type=int, default=4,
        help='Minimax search depth (default: 4)'
    )
    parser.add_argument(
        '--speed', type=float, default=1.0,
        choices=[0.5, 1.0, 2.0, 4.0],
        help='Game speed multiplier (default: 1.0)'
    )
    parser.add_argument(
        '--fullscreen', action='store_true',
        help='Run in fullscreen mode'
    )
    parser.add_argument(
        '--no-graphics', action='store_true',
        help='Run without graphics (simulation only)'
    )
    parser.add_argument(
        '--tournament', type=int, default=0,
        help='Run tournament with N matches (no graphics)'
    )
    
    return parser.parse_args()


def run_graphical_game(args):
    """Run the game with full 3D graphics"""
    from graphics.renderer import GameRenderer
    from ai.decision_tree_window import DecisionTreeWindow
    
    print("=" * 60)
    print("   3D TACTICAL COMBAT ARENA - AI vs AI")
    print("=" * 60)
    print(f"\n🎮 Initializing game...")
    print(f"   Battlefield: {args.width}x{args.height}")
    print(f"   Units per team: {args.units}")
    print(f"   Minimax depth: {args.depth}")
    print(f"   Game speed: {args.speed}x")
    print()
    
    # Update config
    config = get_config()
    config.graphics.fullscreen = args.fullscreen
    config.ai.minimax_depth = args.depth
    
    # Create game manager
    game_manager = GameManager()
    game_manager.setup_new_game(
        battlefield_width=args.width,
        battlefield_height=args.height,
        units_per_team=args.units,
        seed=args.seed
    )
    
    # Create AI agents
    minimax_ai = MinimaxAgent(
        team=Team.RED,
        max_depth=args.depth,
        time_limit=5.0
    )
    
    fuzzy_ai = FuzzyLogicAgent(team=Team.BLUE)
    
    game_manager.set_agents(minimax_ai, fuzzy_ai)
    
    # Set game speed
    speed_map = {
        0.5: GameSpeed.SLOW,
        1.0: GameSpeed.NORMAL,
        2.0: GameSpeed.FAST,
        4.0: GameSpeed.ULTRA_FAST
    }
    game_manager.set_speed(speed_map.get(args.speed, GameSpeed.NORMAL))
    
    # Create renderer
    renderer = GameRenderer()
    renderer.initialize()
    renderer.setup_game(game_manager)
    
    # ── Decision Tree Visualization Window ──
    tree_window = DecisionTreeWindow()
    tree_window.start()
    
    # Hook: after each AI decision, push tree data to visualization
    def _on_ai_decision_tree(decision):
        """Forward AI decision tree data to the visualization window"""
        agent = None
        if decision.team == Team.RED:
            agent = minimax_ai
        elif decision.team == Team.BLUE:
            agent = fuzzy_ai
        
        if agent and hasattr(agent, 'last_decision_tree') and agent.last_decision_tree:
            tree_window.push_decision(agent.last_decision_tree)
    
    game_manager.on_ai_decision(_on_ai_decision_tree)
    
    # Start game in background thread
    print("🚀 Starting AI battle...\n")
    print("🔴 RED TEAM: Minimax with Alpha-Beta Pruning")
    print("🔵 BLUE TEAM: Fuzzy Logic Controller")
    print("🧠 Decision Tree Visualizer: Opens in browser (http://localhost:9173)")
    print("\nPress SPACE to pause, 1-4 to change speed")
    print("-" * 60)
    
    game_manager.run_match_async()
    
    # Run renderer (blocks until window closed)
    renderer.run()
    
    # Cleanup
    game_manager.stop()
    tree_window.stop()
    renderer.cleanup()


def run_simulation(args):
    """Run simulation without graphics"""
    print("=" * 60)
    print("   3D TACTICAL COMBAT - SIMULATION MODE")
    print("=" * 60)
    
    # Create game
    game_manager = GameManager()
    game_manager.setup_new_game(
        battlefield_width=args.width,
        battlefield_height=args.height,
        units_per_team=args.units,
        seed=args.seed
    )
    
    # Create AI agents
    minimax_ai = MinimaxAgent(
        team=Team.RED,
        max_depth=args.depth,
        time_limit=5.0
    )
    fuzzy_ai = FuzzyLogicAgent(team=Team.BLUE)
    
    game_manager.set_agents(minimax_ai, fuzzy_ai)
    
    # No delay for simulation
    get_config().ai.decision_delay = 0
    
    print(f"\n🎮 Running simulation...")
    print(f"   Battlefield: {args.width}x{args.height}")
    print(f"   Units: {args.units} per team")
    
    # Run match
    result = game_manager.run_match()
    
    # Print results
    print("\n" + "=" * 60)
    print("   MATCH RESULTS")
    print("=" * 60)
    
    if result.winner == Team.RED:
        print("\n🏆 WINNER: RED TEAM (Minimax Alpha-Beta)")
    elif result.winner == Team.BLUE:
        print("\n🏆 WINNER: BLUE TEAM (Fuzzy Logic)")
    else:
        print("\n⚔️ DRAW!")
    
    print(f"\n📊 Statistics:")
    print(f"   Total turns: {result.total_turns}")
    print(f"   Duration: {result.duration_seconds:.2f}s")
    print(f"   Red units remaining: {result.red_units_remaining}")
    print(f"   Blue units remaining: {result.blue_units_remaining}")
    print(f"   Red damage dealt: {result.red_total_damage}")
    print(f"   Blue damage dealt: {result.blue_total_damage}")


def run_tournament(args, num_matches: int):
    """Run multiple matches for statistical analysis"""
    print("=" * 60)
    print("   3D TACTICAL COMBAT - TOURNAMENT MODE")
    print("=" * 60)
    print(f"\n🏆 Running {num_matches} matches...")
    
    results = {
        'red_wins': 0,
        'blue_wins': 0,
        'draws': 0,
        'total_turns': 0,
        'total_time': 0,
        'red_total_damage': 0,
        'blue_total_damage': 0
    }
    
    # No delay for tournament
    get_config().ai.decision_delay = 0
    
    for i in range(num_matches):
        print(f"\n--- Match {i + 1}/{num_matches} ---")
        
        # Create fresh game
        game_manager = GameManager()
        game_manager.setup_new_game(
            battlefield_width=args.width,
            battlefield_height=args.height,
            units_per_team=args.units,
            seed=args.seed + i if args.seed else None
        )
        
        # Create AI agents
        minimax_ai = MinimaxAgent(
            team=Team.RED,
            max_depth=args.depth,
            time_limit=5.0
        )
        fuzzy_ai = FuzzyLogicAgent(team=Team.BLUE)
        
        game_manager.set_agents(minimax_ai, fuzzy_ai)
        
        # Run match
        result = game_manager.run_match()
        
        # Record results
        if result.winner == Team.RED:
            results['red_wins'] += 1
            print(f"   Winner: RED (Minimax)")
        elif result.winner == Team.BLUE:
            results['blue_wins'] += 1
            print(f"   Winner: BLUE (Fuzzy)")
        else:
            results['draws'] += 1
            print(f"   Result: DRAW")
        
        results['total_turns'] += result.total_turns
        results['total_time'] += result.duration_seconds
        results['red_total_damage'] += result.red_total_damage
        results['blue_total_damage'] += result.blue_total_damage
    
    # Print tournament results
    print("\n" + "=" * 60)
    print("   TOURNAMENT RESULTS")
    print("=" * 60)
    
    print(f"\n🔴 RED (Minimax) Wins: {results['red_wins']} ({results['red_wins']/num_matches*100:.1f}%)")
    print(f"🔵 BLUE (Fuzzy) Wins: {results['blue_wins']} ({results['blue_wins']/num_matches*100:.1f}%)")
    print(f"⚔️ Draws: {results['draws']} ({results['draws']/num_matches*100:.1f}%)")
    
    print(f"\n📊 Averages per match:")
    print(f"   Turns: {results['total_turns']/num_matches:.1f}")
    print(f"   Duration: {results['total_time']/num_matches:.2f}s")
    print(f"   Red damage: {results['red_total_damage']/num_matches:.1f}")
    print(f"   Blue damage: {results['blue_total_damage']/num_matches:.1f}")
    
    # Determine overall winner
    print("\n" + "=" * 60)
    if results['red_wins'] > results['blue_wins']:
        print("🏆 TOURNAMENT WINNER: MINIMAX ALPHA-BETA 🏆")
    elif results['blue_wins'] > results['red_wins']:
        print("🏆 TOURNAMENT WINNER: FUZZY LOGIC 🏆")
    else:
        print("⚔️ TOURNAMENT TIED ⚔️")
    print("=" * 60)


def main():
    """Main entry point"""
    args = parse_arguments()
    
    try:
        if args.tournament > 0:
            run_tournament(args, args.tournament)
        elif args.no_graphics:
            run_simulation(args)
        else:
            run_graphical_game(args)
    except KeyboardInterrupt:
        print("\n\n🛑 Game interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
