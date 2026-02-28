
---

##  Summary

This project implements a production-grade 3D tactical combat game featuring two competing AI agents: **Minimax with Alpha-Beta Pruning** (Red Team) vs **Fuzzy Logic Controller** (Blue Team). The game showcases advanced AI algorithms in a visually rich 3D environment.

---

## 1. Introduction

### 1.1 Project Objective
To develop a turn-based tactical combat game that demonstrates the comparison between two fundamentally different AI approaches:
- **Adversarial Search** (Minimax) - Exhaustive game tree exploration
- **Fuzzy Inference** (Fuzzy Logic) - Human-like rule-based reasoning

### 1.2 Key Features
- Beautiful 3D graphics using Ursina engine
- 5 unique unit types with special abilities
- Dynamic terrain system affecting combat
- Real-time AI decision visualization
- Tournament mode for statistical analysis

---

## 2. Assumed System Architecture

### 2.1 Assumed Project Structure
```
PythonAdvanced3DGame/
├── main.py              # Entry point
├── ai/                  # AI agents
│   ├── minimax_agent.py # Minimax AI
│   ├── fuzzy_agent.py   # Fuzzy Logic AI
│   └── evaluation.py    # Heuristic evaluation
├── core/                # Game logic
│   ├── game_state.py    # State management
│   ├── battlefield.py   # Terrain system
│   └── unit.py          # Unit classes
├── graphics/            # 3D rendering
│   ├── renderer.py      # Main renderer
│   ├── battlefield_view.py
│   └── effects.py       # Visual effects
└── config/              # Configuration
    └── settings.py
```


## 3. Game Mechanics

### 3.1 Game Flow

```
┌─────────────────────────────────────────────────────┐
│                    GAME START                       │
│   🔴 Red Team placed on one side                   │
│   🔵 Blue Team placed on opposite side             │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│                    RED TURN                         │
│   Each unit: Move (optional) → Attack/Ability      │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│                    BLUE TURN                        │
│   Each unit: Move (optional) → Attack/Ability      │
└─────────────────────────────────────────────────────┘
                          │
              (Repeat until one team eliminated)
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│                    GAME OVER                        │
│   Winner = Team with surviving units               │
└─────────────────────────────────────────────────────┘
```

### 3.2 Unit Types

| Unit | HP | Attack | Defense | Range | Movement | Role |
|------|-----|--------|---------|-------|----------|------|
| **Warrior** | 150 | 30 | 20 | 1 | 2 | Tank/Frontline |
| **Archer** | 80 | 35 | 8 | 5 | 3 | Ranged DPS |
| **Mage** | 70 | 45 | 5 | 4 | 2 | Area Damage |
| **Knight** | 120 | 35 | 15 | 1 | 4 | Mobile Fighter |
| **Healer** | 60 | 15 | 10 | 3 | 3 | Support |

### 3.3 Terrain System

| Terrain | Defense Bonus | Attack Bonus | Movement Cost |
|---------|---------------|--------------|---------------|
| Plain 🟩 | +0 | +0 | 1 |
| Forest 🌲 | +2 | +0 | 2 |
| Hill 🏔️ | +1 | +1 | 2 |
| Ruins ⬜ | +3 | +0 | 1 |
| Water 💧 | N/A | N/A | Impassable |

### 3.4 Combat Formula

```
┌─────────────────────────────────────────────────────────────┐
│                    DAMAGE FORMULA                           │
│                                                             │
│   Raw Damage = Attacker's Attack + Terrain Attack Bonus     │
│   Defense = Target's Defense + Terrain Defense Bonus        │
│   Final Damage = max(1, Raw Damage - Defense)               │
│   Critical Hits = 1.5x damage                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. AI Implementation

### 4.1 Minimax Agent (Red Team)

**Algorithm:** Minimax with Alpha-Beta Pruning

**Key Features:**
- Alpha-Beta pruning for efficiency
- Transposition tables for caching
- Iterative deepening for time management
- Move ordering for better pruning

**Decision Process:**
```
Current: Red turn
├── Move Warrior forward → Score: 45
│   └── (Blue attacks) → Score: 30
│       └── (Red attacks back) → Score: 52
├── Attack with Archer → Score: 60 ⭐ BEST!
│   └── (Blue retreats) → Score: 55
└── Wait → Score: 20
    └── (Blue advances) → Score: 15

Decision: Attack with Archer (highest eventual score)
```

### 4.2 Fuzzy Logic Agent (Blue Team)

**Algorithm:** Mamdani-style Fuzzy Inference System

**Key Features:**
- Threat assessment system
- Aggression level controller
- Target prioritization
- Human-readable rules

**Decision Process:**
```
Situation Assessment:
├── Own HP: 65% → "Low-ish"
├── Team Advantage: +20% → "Slightly winning"
├── Enemies in range: 2 → "Few"
└── → Aggression Level: 55% (Balanced)

Target Prioritization:
├── Enemy Mage: HP 30%, High damage → Priority: 85 ⭐
├── Enemy Knight: HP 80%, Medium damage → Priority: 40
└── → Target: Mage (eliminate the threat!)

Decision: Attack the Mage
```

**Fuzzy Rules Example:**
```
IF HP is LOW AND enemies are CLOSE → Be DEFENSIVE
IF enemy HP is CRITICAL AND can_kill → PRIORITY TARGET  
IF winning AND healthy → Be AGGRESSIVE
```

---

## 5. State Evaluation

### 5.1 Evaluation Components

| Factor | Weight | Description |
|--------|--------|-------------|
| HP Difference | 1.0 | Total HP comparison |
| Unit Count | 50.0 | Number of surviving units |
| Position | 0.5 | Terrain & center control |
| Threats | 0.3 | Attack opportunities |
| Mobility | 0.2 | Movement options |
| Terrain | 0.15 | Terrain advantage |
| Formation | 0.1 | Unit coordination |

### 5.2 Evaluation Formula
```python
total_score = (
    hp_score * 1.0 +
    unit_count * 50.0 +
    position_score * 0.5 +
    threat_score * 0.3 +
    mobility_score * 0.2 +
    terrain_score * 0.15 +
    formation_score * 0.1
)
```

---

## 6. Sample Battle Walkthrough

### 6.1 Initial Setup
```
┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐
│🔴W│   │   │   │   │   │   │   │   │   │   │🔵K│
├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
│🔴A│   │   │🌲 │   │   │   │   │🌲 │   │   │🔵A│
├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
│🔴M│   │   │   │   │💧│💧│   │   │   │   │🔵M│
├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
│🔴H│   │   │   │   │   │   │   │   │   │   │🔵H│
└───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘
Legend: W=Warrior, A=Archer, M=Mage, H=Healer, K=Knight
```

### 6.2 Mid-Battle (Turn 5)
```
┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐
│   │   │   │   │🔴W│   │   │🔵K│   │   │   │   │
├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
│   │   │🔴A│🌲 │   │   │   │   │🌲🔵A│   │   │   │
├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
│   │   │   │🔴M│   │💧│💧│   │🔵M│   │   │   │
├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
│   │🔴H│   │   │   │   │   │   │   │   │🔵H│   │
└───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘
```

### 6.3 Kill Sequence
```
🔴 Warrior attacks 🔵 Knight!
   Damage: 30 - 15 = 15 → Knight HP: 45 → 30

🔴 Archer follows up!
   Damage: 35 - 15 = 20 → Knight HP: 30 → 10

🔴 Mage casts Fireball!
   Knight HP: 10 → 0 ☠️

💀 BLUE KNIGHT ELIMINATED!
```

### 6.4 Endgame
```
Final: Red wins with 2 units remaining
═══════════════════════════════════════
        🔴 RED TEAM WINS! 🏆
═══════════════════════════════════════
```

---

## 7. Special Abilities

| Unit | Ability | Effect | Cooldown |
|------|---------|--------|----------|
| Warrior | Shield Wall | +5 Defense, 2 turns | 3 turns |
| Warrior | Charge | Move + Attack | 4 turns |
| Archer | Snipe | +3 Range, +50% damage | 4 turns |
| Archer | Overwatch | Counter-attack | 5 turns |
| Mage | Fireball | 3×3 area damage | 4 turns |
| Knight | Charge | Move + Attack | 3 turns |
| Healer | Heal | Restore 40 HP | 2 turns |

---

---


