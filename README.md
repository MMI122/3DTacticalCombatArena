# 3D Tactical Combat Arena - AI vs AI

A production-grade 3D game featuring two AI agents competing against each other:
- **🔴 Red Team**: Minimax with Alpha-Beta Pruning
- **🔵 Blue Team**: Fuzzy Logic Controller

## 🎮 Features

- **Beautiful 3D Graphics** using Ursina engine
- **Turn-based tactical combat** on procedurally generated battlefields
- **Multiple unit types**: Warrior, Archer, Mage, Knight, Healer
- **Terrain effects**: 8 types (Plains, Forests, Hills, Water, Mountains, Ruins, Roads, Bridges) with combat modifiers
- **Special abilities**: Charge, Snipe, Fireball, Shield Wall, Heal, Overwatch
- **3-minute match timeout** with dynamic winner determination
- **Match scoring system**: Comprehensive formula tracking unit survival, HP, kills, and damage
- **Real-time AI decision visualization**: Browser-based interface showing decision trees
- **Dual AI systems**: Minimax (optimal play) vs Fuzzy Logic (human-like decisions)
- **Match statistics and detailed game analysis**
- **Tournament mode** for statistical analysis

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Game

```bash
python main.py
```

### 3. Controls

| Key | Action |
|-----|--------|
| WASD / Arrows | Pan camera |
| Q / E | Zoom out / in |
| 1-4 | Game speed (0.5x - 4x) |
| Space | Pause / Resume |

## 🤖 AI Algorithms

### Minimax with Alpha-Beta Pruning (Red Team)

- **Type**: Adversarial search algorithm
- **Approach**: Exhaustively searches the game tree
- **Features**:
  - Alpha-Beta pruning for efficiency
  - Transposition tables for caching
  - Iterative deepening for time management
  - Move ordering for better pruning
- **Best for**: Finding optimal moves in zero-sum games

### Fuzzy Logic Controller (Blue Team)

- **Type**: Rule-based inference system
- **Approach**: Uses linguistic rules to make decisions
- **Features**:
  - Threat assessment system
  - Aggression level controller
  - Target prioritization
  - Human-readable rules
- **Best for**: Handling uncertainty and gradual transitions

## 🎯 Game Mechanics

### Unit Types

| Unit | HP | Attack | Defense | Range | Movement | Special |
|------|-----|--------|---------|-------|----------|---------|
| Warrior | 150 | 30 | 20 | 1 | 2 | Shield Wall, Charge |
| Archer | 80 | 35 | 8 | 5 | 3 | Snipe, Overwatch |
| Mage | 70 | 45 | 5 | 4 | 2 | Fireball |
| Knight | 120 | 35 | 15 | 1 | 4 | Charge |
| Healer | 60 | 15 | 10 | 3 | 3 | Heal |

### Terrain Types

| Terrain | Defense | Attack | Movement | Passable |
|---------|---------|--------|----------|----------|
| Plain | 0 | 0 | 1x | Yes |
| Forest | +2 | 0 | 2x | Yes |
| Hill | +1 | +1 | 2x | Yes |
| Ruins | +3 | 0 | 1x | Yes |
| Road | -1 | 0 | 0.5x (bonus speed) | Yes |
| Bridge | 0 | 0 | 1x | Yes |
| Water | - | - | - | No |
| Mountain | - | - | - | No |

### Match End Conditions

Matches end under two conditions:

#### 1. Elimination Victory
- One team completely destroys the other (all units eliminated)
- Remaining team automatically wins

#### 2. Timeout Victory
- If 3 minutes (180 seconds) elapse without elimination
- Winner determined by **Match Score**, not elimination

### Match Scoring System

When timeout occurs, winner is determined by comprehensive scoring:

```
Match Score = (Units Alive × 1000) 
            + (Total HP Remaining × 2)
            + (Enemy Units Killed × 300)
            + (Damage Dealt × 1)
```

**Scoring Components:**
- **Units Alive (×1000)**: Most important - surviving units are permanent advantages
- **Total HP (×2)**: Health remaining multiplied across all units
- **Kills (×300)**: Each enemy unit eliminated contributes significantly
- **Damage (×1)**: Cumulative damage dealt acts as tiebreaker

**Example Scenario (at timeout):**
- **Red**: 3 units, 250 total HP, 2 kills, 1200 damage → Score = 3000 + 500 + 600 + 1200 = **5300**
- **Blue**: 2 units, 180 total HP, 1 kill, 900 damage → Score = 2000 + 360 + 300 + 900 = **3560**
- **Winner**: Red Team (5300 > 3560)

## 📊 Command Line Options

```bash
python main.py [options]

Options:
  --width N         Battlefield width (default: 12)
  --height N        Battlefield height (default: 12)
  --units N         Units per team (default: 4)
  --seed N          Random seed for reproducibility
  --depth N         Minimax search depth (default: 4)
  --speed X         Game speed: 0.5, 1.0, 2.0, 4.0 (default: 1.0)
  --fullscreen      Run in fullscreen mode
  --no-graphics     Run simulation only (no graphics)
  --tournament N    Run N matches and show statistics
```

### Examples

```bash
# Standard game
python main.py

# Larger battlefield with more units
python main.py --width 16 --height 16 --units 6

# Fast tournament of 10 matches
python main.py --tournament 10 --depth 3

# Simulation only (no graphics)
python main.py --no-graphics --seed 42
```

## 🧪 Running Tests

```bash
pytest tests/ -v
```

## 📁 Project Structure

```
PythonAdvanced3DGame/
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── README.md              # This file
├── config/
│   ├── settings.py        # Game configuration
│   └── units.py           # Unit definitions
├── core/
│   ├── game_state.py      # Game logic
│   ├── unit.py            # Unit class
│   ├── battlefield.py     # Battlefield/terrain
│   └── game_manager.py    # Match orchestration
├── ai/
│   ├── base_agent.py      # AI interface
│   ├── minimax_agent.py   # Minimax Alpha-Beta AI
│   ├── fuzzy_agent.py     # Fuzzy Logic AI
│   └── evaluation.py      # Position evaluation
├── graphics/
│   ├── renderer.py        # Main renderer
│   ├── battlefield_view.py # 3D battlefield
│   ├── unit_view.py       # 3D unit models
│   ├── effects.py         # Particle effects
│   └── ui_overlay.py      # HUD and UI
└── tests/
    ├── test_minimax.py    # Minimax tests
    ├── test_fuzzy.py      # Fuzzy logic tests
    └── test_game_state.py # Core mechanic tests
```

## 🔧 Technical Details

- **Python 3.8+** required
- **Ursina** for 3D rendering
- **NumPy** for numerical computations
- **scikit-fuzzy** for fuzzy logic (optional, custom implementation included)
- **pytest** for testing

## 🎓 Educational Value

This project demonstrates:
- **Game AI**: Two different approaches to game AI
- **3D Graphics**: Real-time 3D rendering with Python
- **Software Architecture**: Production-grade code organization
- **Algorithm Comparison**: Minimax vs Fuzzy Logic effectiveness
