# 🎮 Understanding the 3D Tactical Combat Arena

## 📖 Table of Contents
1. [Game Overview](#game-overview)
2. [How the Game Works](#how-the-game-works)
3. [Turn Structure](#turn-structure)
4. [Unit Actions (Legal Moves)](#unit-actions-legal-moves)
5. [Combat Mechanics](#combat-mechanics)
6. [Terrain System](#terrain-system)
7. [Special Abilities](#special-abilities)
8. [How the AI Agents Think](#how-the-ai-agents-think)
9. [Winning Conditions](#winning-conditions)
10. [Example Game Scenario](#example-game-scenario)

---

## 🎯 Game Overview

This is a **turn-based tactical combat game** where two AI agents battle each other:

| Team | AI Algorithm | Play Style |
|------|-------------|------------|
| 🔴 **Red Team** | Minimax with Alpha-Beta Pruning | Calculative, looks many moves ahead |
| 🔵 **Blue Team** | Fuzzy Logic Controller | Intuitive, uses human-like rules |

**The Battlefield:**
- A 12×12 grid (144 cells)
- Each team starts with 4 units
- Various terrain types affect combat

---

## ⚙️ How the Game Works

### Basic Flow
```
┌─────────────────────────────────────────────────────┐
│                    GAME START                       │
│                                                     │
│   🔴 Red Team placed on one side of battlefield    │
│   🔵 Blue Team placed on opposite side             │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│                    RED TURN                         │
│                                                     │
│   Each Red unit gets to:                           │
│   1. Move (optional)                               │
│   2. Attack OR Use Ability (optional)              │
│   3. Wait (end unit's turn early)                  │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│                    BLUE TURN                        │
│                                                     │
│   Each Blue unit gets to:                          │
│   1. Move (optional)                               │
│   2. Attack OR Use Ability (optional)              │
│   3. Wait (end unit's turn early)                  │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
              (Repeat until one team eliminated)
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│                    GAME OVER                        │
│   Winner = Team with surviving units               │
└─────────────────────────────────────────────────────┘
```

---

## 🔄 Turn Structure

### What Happens During a Turn

During each team's turn, the AI must decide what each unit should do. Every unit can perform:

1. **One Movement** - Move to a reachable cell
2. **One Action** - Attack an enemy OR use a special ability
3. **Wait** - Skip remaining actions and end the unit's turn

### Unit State Tracking

```
Unit at start of turn:
├── has_moved = False
├── has_attacked = False
└── can_act = True

After moving:
├── has_moved = True ✓
├── has_attacked = False
└── can_act = True (can still attack)

After attacking:
├── has_moved = True ✓
├── has_attacked = True ✓
└── can_act = False (turn complete)
```

---

## 🎲 Unit Actions (Legal Moves)

### What is a "Legal Move"?

A **legal move** is any action that a unit is allowed to take given the current game state. The game calculates all legal moves for each unit considering:

### 1. **MOVE Actions**
A unit can move to a cell if:
- ✅ The unit hasn't moved yet this turn
- ✅ The cell is within movement range
- ✅ The cell is passable (not blocked by water/mountains)
- ✅ The cell is not occupied by another unit
- ✅ There's a valid path to reach it

**Example:**
```
Movement Range = 3 cells

Before Move:              Legal Move Positions (●):
┌───┬───┬───┬───┬───┐    ┌───┬───┬───┬───┬───┐
│   │   │   │   │   │    │   │ ● │ ● │ ● │   │
├───┼───┼───┼───┼───┤    ├───┼───┼───┼───┼───┤
│   │   │   │   │   │    │ ● │ ● │ ● │ ● │ ● │
├───┼───┼───┼───┼───┤    ├───┼───┼───┼───┼───┤
│   │   │ W │   │   │    │ ● │ ● │ W │ ● │ ● │
├───┼───┼───┼───┼───┤    ├───┼───┼───┼───┼───┤
│   │   │   │   │   │    │ ● │ ● │ ● │ ● │ ● │
├───┼───┼───┼───┼───┤    ├───┼───┼───┼───┼───┤
│   │   │   │   │   │    │   │ ● │ ● │ ● │   │
└───┴───┴───┴───┴───┘    └───┴───┴───┴───┴───┘
    W = Warrior (Range 2)
```

### 2. **ATTACK Actions**
A unit can attack if:
- ✅ The unit hasn't attacked yet this turn
- ✅ An enemy is within attack range
- ✅ There's line of sight to the enemy (not blocked by terrain)

**Example - Archer Attack Range:**
```
Attack Range = 5 cells

┌───┬───┬───┬───┬───┬───┬───┐
│   │   │   │ ✗ │   │   │   │  ✗ = Attackable enemy
├───┼───┼───┼───┼───┼───┼───┤
│   │   │   │   │   │ ✗ │   │
├───┼───┼───┼───┼───┼───┼───┤
│   │   │ 🏹 │───│───│───│───│  ← Line of sight
├───┼───┼───┼───┼───┼───┼───┤
│   │   │   │   │   │   │   │
└───┴───┴───┴───┴───┴───┴───┘
    🏹 = Archer
```

### 3. **ABILITY Actions**
A unit can use an ability if:
- ✅ The ability is off cooldown
- ✅ Valid targets exist (allies for heal, enemies for damage)
- ✅ Targets are in range

### 4. **WAIT Action**
- ✅ Always available
- Ends the unit's turn immediately
- Used when no beneficial action exists

---

## ⚔️ Combat Mechanics

### Damage Calculation

When unit A attacks unit B:

```
┌─────────────────────────────────────────────────────────────┐
│                    DAMAGE FORMULA                           │
│                                                             │
│   Raw Damage = Attacker's Attack + Terrain Attack Bonus     │
│                                                             │
│   Defense = Target's Defense + Terrain Defense Bonus        │
│                                                             │
│   Final Damage = max(1, Raw Damage - Defense)               │
│                                                             │
│   (Critical Hits do 1.5x damage!)                          │
└─────────────────────────────────────────────────────────────┘
```

**Example Combat:**
```
🔴 Red Warrior (Attack: 30) attacks 🔵 Blue Archer (Defense: 8)

Warrior is on Plain (+0 attack)
Archer is in Forest (+2 defense)

Raw Damage = 30 + 0 = 30
Defense = 8 + 2 = 10
Final Damage = 30 - 10 = 20 HP

Archer HP: 80 → 60
```

### Death and Elimination

- When a unit's HP reaches 0, it **dies** and is removed from the battlefield
- The unit can no longer take actions
- If ALL units of a team die, that team **loses**

---

## 🏔️ Terrain System

The battlefield has different terrain types that affect combat:

### Terrain Effects

| Terrain | Visual | Defense | Attack | Movement Cost | Special |
|---------|--------|---------|--------|---------------|---------|
| **Plain** | 🟩 Green | +0 | +0 | 1 | Standard terrain |
| **Forest** | 🟫 Brown + Trees | +2 | +0 | 2 | Blocks line of sight |
| **Hill** | 🏔️ Elevated | +1 | +1 | 2 | Good for archers |
| **Ruins** | ⬜ Gray Stones | +3 | +0 | 1 | Excellent cover |
| **Water** | 💧 Blue | N/A | N/A | ∞ | **Impassable!** |
| **Road** | ➖ Path | -1 | +0 | 0.5 | Fast movement |

### Tactical Terrain Use

**Hiding in Forest:**
```
Forest provides +2 Defense bonus AND blocks ranged attacks!

┌───┬───┬───┬───┬───┐
│ 🔵│   │🌲🌲│   │   │   🌲🌲 = Forest
├───┼───┼───┼───┼───┤
│   │   │🌲🌲│   │🏹│   🏹 = Enemy Archer
├───┼───┼───┼───┼───┤
│   │   │🌲🔴│   │   │   🔴 = Red unit hiding in forest
└───┴───┴───┴───┴───┘

Archer CANNOT shoot through/into forest! (Line of sight blocked)
```

**Defending in Ruins:**
```
Ruins give +3 Defense - perfect for tanks!

🔴 Warrior in Ruins: Defense 20 + 3 = 23
Enemy attacks deal much less damage!
```

---

## ✨ Special Abilities

Each unit type has unique special abilities:

### Warrior Abilities
| Ability | Effect | Cooldown |
|---------|--------|----------|
| **Shield Wall** | +5 Defense for 2 turns | 3 turns |
| **Charge** | Move AND attack in same action | 4 turns |

### Archer Abilities
| Ability | Effect | Cooldown |
|---------|--------|----------|
| **Snipe** | +3 Range, +50% damage on one attack | 4 turns |
| **Overwatch** | Counter-attack enemies that move nearby | 5 turns |

### Mage Abilities
| Ability | Effect | Cooldown |
|---------|--------|----------|
| **Fireball** | Area damage (hits 3×3 area) | 4 turns |

### Knight Abilities
| Ability | Effect | Cooldown |
|---------|--------|----------|
| **Charge** | Move AND attack in same action | 3 turns |

### Healer Abilities
| Ability | Effect | Cooldown |
|---------|--------|----------|
| **Heal** | Restore 40 HP to ally in range | 2 turns |

---

## 🤖 How the AI Agents Think

### 🔴 Red Team: Minimax AI

The Minimax AI thinks like a chess computer:

```
"If I move here, then opponent does X,
 then I do Y, then opponent does Z...
 which sequence leads to the best outcome for me?"
```

**How it works:**
1. Generate ALL possible moves
2. For each move, simulate opponent's best response
3. Continue simulating several turns deep (depth = 4)
4. Evaluate final positions
5. Choose move leading to best outcome

**Example thinking:**
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

### 🔵 Blue Team: Fuzzy Logic AI

The Fuzzy Logic AI thinks with human-like rules:

```
"My HP is low AND enemies are close → Be DEFENSIVE"
"Enemy HP is critical AND I can kill → PRIORITY TARGET"
"We're winning AND I'm healthy → Be AGGRESSIVE"
```

**How it works:**
1. Assess current situation (HP, position, threats)
2. Apply fuzzy rules to get "aggression level"
3. Choose targets based on priority rules
4. Pick action matching the strategy

**Example thinking:**
```
Situation Assessment:
├── Own HP: 65% → "Low-ish"
├── Team Advantage: +20% → "Slightly winning"
├── Enemies in range: 2 → "Few"
└── → Aggression Level: 55% (Balanced)

Target Prioritization:
├── Enemy Mage: HP 30%, High damage → Priority: 85 ⭐
├── Enemy Knight: HP 80%, Medium damage → Priority: 40
└── → Target: Mage (can eliminate the threat!)

Decision: Attack the Mage
```

---

## 🏆 Winning Conditions

### How to Win

A team wins when **ALL enemy units are eliminated**:

```
┌─────────────────────────────────────────────────────┐
│                   VICTORY CHECK                      │
│                                                      │
│   IF Red Team has 0 alive units:                    │
│       🔵 BLUE WINS!                                 │
│                                                      │
│   IF Blue Team has 0 alive units:                   │
│       🔴 RED WINS!                                  │
│                                                      │
│   OTHERWISE:                                         │
│       Game continues...                             │
└─────────────────────────────────────────────────────┘
```

### What the AIs Try to Do

Both AIs evaluate board positions based on:

| Factor | Weight | Description |
|--------|--------|-------------|
| **HP Difference** | High | More total HP = better |
| **Unit Count** | Very High | Losing a unit is devastating |
| **Position** | Medium | Control center, good terrain |
| **Threats** | Medium | Units that can attack safely |
| **Mobility** | Low | Movement options available |

**Kill Priority:**
```
Both AIs heavily prioritize KILLING enemy units because:
- Dead units deal 0 damage forever
- Fewer enemies = easier battles
- One less enemy = permanent advantage
```

---

## 🎬 Example Game Scenario

Let's walk through a sample battle:

### Turn 1: Opening Moves

```
Starting Position:
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
        🌲=Forest, 💧=Water
```

**Red's thinking (Minimax):**
> "I should advance my Warrior toward the center while my Archer moves to high ground. My Mage should position to use Fireball when enemies cluster."

**Red's actions:**
1. Warrior moves forward 2 cells
2. Archer moves toward forest (for cover)
3. Mage advances carefully
4. Healer follows behind Warrior

### Turn 2: Blue Response

**Blue's thinking (Fuzzy Logic):**
> "Team advantage is even. My Knight is fast - I'll flank around the water. My Mage should target clusters. HP is healthy so I can be aggressive."

**Blue's actions:**
1. Knight charges around the water (high mobility)
2. Archer positions in forest (defensive)
3. Mage advances to casting range
4. Healer stays back

### Turn 5: First Blood!

```
Mid-Battle Position:
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

**Red's move:**
> "Blue Knight has 45 HP remaining. My Warrior can reach and attack. That's a KILL opportunity!"

```
🔴 Warrior attacks 🔵 Knight!
Damage: 30 - 15 = 15
Knight HP: 45 → 30

🔴 Archer follows up!
Damage: 35 - 15 = 20
Knight HP: 30 → 10

🔴 Mage casts Fireball! (Area damage)
Knight HP: 10 → 0 ☠️

💀 BLUE KNIGHT ELIMINATED!
```

### Turn 10: Endgame

```
Final Battle:
┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐
│   │   │   │   │   │🔴W│🔵A│   │   │   │   │   │
│   │   │   │   │   │(80HP)(15HP)│   │   │   │   │
├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
│   │   │   │   │   │   │   │   │   │   │   │   │
├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
│   │   │   │   │   │🔴H│   │   │   │   │   │   │
│   │   │   │   │   │(40HP)│   │   │   │   │   │
└───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘

Red: 2 units remaining (Warrior 80HP, Healer 40HP)
Blue: 1 unit remaining (Archer 15HP) 
```

**Red's final move:**
> "Blue Archer at 15 HP. One attack ends the game!"

```
🔴 Warrior attacks 🔵 Archer!
Damage: 30 - 8 = 22
Archer HP: 15 → 0 ☠️

💀 BLUE ARCHER ELIMINATED!

═══════════════════════════════════════
    🔴 RED TEAM WINS! 🏆
═══════════════════════════════════════
```

---

## 📊 Quick Reference Card

### Unit Stats Summary
| Unit | HP | ATK | DEF | Range | Move | Role |
|------|-----|-----|-----|-------|------|------|
| Warrior | 150 | 30 | 20 | 1 | 2 | Tank/Frontline |
| Archer | 80 | 35 | 8 | 5 | 3 | Ranged DPS |
| Mage | 70 | 45 | 5 | 4 | 2 | Area Damage |
| Knight | 120 | 35 | 15 | 1 | 4 | Mobile Fighter |
| Healer | 60 | 15 | 10 | 3 | 3 | Support |

### Action Priority
1. **Kill shots** - Eliminate weak enemies
2. **Damage high-value targets** - Mages, Archers
3. **Position for advantage** - Terrain, range
4. **Heal/Defend** - When ahead or under pressure
5. **Wait** - When no good options

---

*This guide explains how the 3D Tactical Combat Arena works. Watch the AI battle and see if you can predict their moves!*
