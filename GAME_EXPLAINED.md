# 🎮 3D Tactical Combat Arena - Complete Game Explanation

This document explains every aspect of the game in detail with visual examples.

---

## Table of Contents

1. [How Turns Work](#1-how-turns-work)
2. [Unit Stats Explained](#2-unit-stats-explained)
3. [Terrain System](#3-terrain-system)
4. [Combat Formula](#4-combat-formula)
5. [Critical Hits](#5-critical-hits)
6. [AI Decision Process](#6-ai-decision-process)
7. [Score System](#7-score-system)
8. [Why Scoring is Needed](#8-why-scoring-is-needed)
9. [Evaluation Components](#9-evaluation-components)
10. [Special Abilities](#10-special-abilities)

---

## 1. How Turns Work

Think of it like chess, but each team has **4 units** (Warrior, Archer, Mage, Healer).

### During Red's Turn:

**Each of Red's 4 units gets to act, one by one:**

```
Unit 1 (Warrior):
  ├── Move? (optional) → Walk up to 2 cells
  └── Attack? (optional) → Hit an enemy in range

Unit 2 (Archer):
  ├── Move? (optional) → Walk up to 3 cells  
  └── Attack? (optional) → Shoot enemy up to 5 cells away

Unit 3 (Mage):
  ├── Move? (optional) → Walk up to 2 cells
  └── Attack OR Ability? → Fireball!

Unit 4 (Healer):
  ├── Move? (optional) → Walk up to 3 cells
  └── Ability? → Heal a teammate

Then Blue's turn starts...
```

### What "Optional" Means:

| Situation | What Unit Does |
|-----------|----------------|
| Enemy far away | Move closer, don't attack |
| Enemy in range | Don't move, just attack |
| Already in good position | Move AND attack |
| Nothing useful to do | Wait (skip turn) |

### Simple Example:

```
Before Red's turn:
┌───┬───┬───┬───┬───┐
│🔴W│   │   │   │🔵A│   🔴W = Red Warrior
└───┴───┴───┴───┴───┘   🔵A = Blue Archer (enemy)

Red Warrior's options:
1. Move 2 cells right → Still can't reach enemy
2. Wait → Do nothing

After moving:
┌───┬───┬───┬───┬───┐
│   │   │🔴W│   │🔵A│   Warrior moved closer!
└───┴───┴───┴───┴───┘   Next turn he can attack!
```

**The AI decides what each unit should do** - that's where Minimax and Fuzzy Logic come in!

---

## 2. Unit Stats Explained

### Using Warrior as Example:

| Stat | Warrior Value | What It Means |
|------|---------------|---------------|
| **HP** | 150 | Health Points - How much damage he can take before dying |
| **Attack** | 30 | How much damage he deals when hitting enemy |
| **Defense** | 20 | Reduces incoming damage (acts like armor) |
| **Range** | 1 | How far he can attack (1 = must be next to enemy) |
| **Movement** | 2 | How many cells he can walk per turn |
| **Role** | Tank | His job - absorb damage, protect teammates |

---

### 2.1 HP (Health Points)

```
Warrior: 150 HP  ████████████████████ (Tanky!)
Archer:   80 HP  ██████████           (Squishy)
Healer:   60 HP  ████████             (Very squishy)
```

**When HP hits 0 → Unit dies!**

---

### 2.2 Attack & Defense (Damage Calculation)

```
🔴 Warrior (Attack: 30) hits 🔵 Archer (Defense: 8)

Damage = Attack - Defense
Damage = 30 - 8 = 22 HP lost!

Archer HP: 80 → 58
```

**High Defense = Takes less damage:**

```
🔵 Archer (Attack: 35) hits 🔴 Warrior (Defense: 20)

Damage = 35 - 20 = 15 HP lost

Warrior HP: 150 → 135  (barely scratched!)
```

---

### 2.3 Range (Attack Distance)

```
Range 1 (Warrior, Knight) - Melee fighters
┌───┬───┬───┐
│   │ ✓ │   │   Can only hit
├───┼───┼───┤   adjacent cells
│ ✓ │🔴W│ ✓ │   (next to them)
├───┼───┼───┤
│   │ ✓ │   │
└───┴───┴───┘

Range 5 (Archer) - Sniper!
┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐
│ ✓ │ ✓ │ ✓ │ ✓ │ ✓ │🏹│ ✓ │ ✓ │ ✓ │ ✓ │ ✓ │
└───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘
         Can shoot enemies 5 cells away!
```

---

### 2.4 Movement (Walking Speed)

```
Warrior (Move: 2) - Slow
┌───┬───┬───┬───┬───┐
│   │ ✓ │ ✓ │   │   │  Can walk up to
├───┼───┼───┼───┼───┤  2 cells per turn
│ ✓ │ ✓ │🔴W│ ✓ │ ✓ │
├───┼───┼───┼───┼───┤
│   │ ✓ │ ✓ │   │   │
└───┴───┴───┴───┴───┘

Knight (Move: 4) - Fast!
┌───┬───┬───┬───┬───┬───┬───┬───┬───┐
│   │   │ ✓ │ ✓ │ ✓ │ ✓ │ ✓ │   │   │
├───┼───┼───┼───┼───┼───┼───┼───┼───┤  Can walk up to
│   │ ✓ │ ✓ │ ✓ │ ✓ │ ✓ │ ✓ │ ✓ │   │  4 cells per turn
├───┼───┼───┼───┼───┼───┼───┼───┼───┤  (flanks enemies!)
│ ✓ │ ✓ │ ✓ │ ✓ │🔵K│ ✓ │ ✓ │ ✓ │ ✓ │
└───┴───┴───┴───┴───┴───┴───┴───┴───┘
```

---

### 2.5 Roles (What Each Unit Does Best)

| Unit | Role | Strategy |
|------|------|----------|
| **Warrior** | Tank | Stand in front, absorb damage |
| **Archer** | Ranged DPS | Stay back, snipe from far |
| **Mage** | Area Damage | Fireball groups of enemies |
| **Knight** | Mobile Fighter | Run around, flank enemies |
| **Healer** | Support | Keep teammates alive |

---

### 2.6 Quick Comparison

```
           HP    ATK   DEF   RANGE   MOVE
Warrior   ████   ██    ████    █      █     Slow tank
Archer    ██     ███   █       █████  ███   Glass cannon
Mage      ██     █████ █       ████   █     Big damage, fragile
Knight    ███    ███   ███     █      █████ Fast attacker
Healer    █      █     █       ███    ███   Keeps team alive
```

---

## 3. Terrain System

Terrain changes how combat works when a unit stands on it.

### 3.1 Defense Bonus (How Much Harder to Hit)

When a unit stands on terrain, they get **extra defense**:

```
🔴 Warrior (Attack: 30) attacks 🔵 Archer

Archer on PLAIN (Defense Bonus: +0):
  Damage = 30 - 8 = 22 HP

Archer in FOREST (Defense Bonus: +2):
  Damage = 30 - (8+2) = 20 HP  ← Takes less damage!

Archer in RUINS (Defense Bonus: +3):
  Damage = 30 - (8+3) = 19 HP  ← Even safer!
```

**Think of it like cover in a shooter game!**

---

### 3.2 Attack Bonus (Hit Harder From Here)

Some terrain makes your attacks stronger:

```
🔴 Archer on PLAIN (Attack Bonus: +0):
  Damage = 35 - 8 = 27 HP

🔴 Archer on HILL (Attack Bonus: +1):
  Damage = (35+1) - 8 = 28 HP  ← High ground advantage!
```

**Hills = Sniper spots!** 🏔️

---

### 3.3 Movement Cost (How Hard to Walk Through)

This is how many "movement points" it takes to enter a cell:

```
Knight has Movement: 4

On ROAD (Cost: 0.5):
  Can walk 8 cells! (4 ÷ 0.5 = 8)  ← Super fast!

On PLAIN (Cost: 1):
  Can walk 4 cells (normal)

On FOREST (Cost: 2):
  Can walk only 2 cells (4 ÷ 2 = 2)  ← Slowed down!

On WATER (Cost: ∞):
  CANNOT ENTER! ❌ Blocked!
```

---

### 3.4 Terrain Overview

```
┌──────┬──────┬──────┬──────┬──────┐
│ ROAD │PLAIN │FOREST│ HILL │WATER │
│ ──── │  🟩  │  🌲  │  🏔️  │  💧  │
├──────┼──────┼──────┼──────┼──────┤
│DEF -1│DEF +0│DEF +2│DEF +1│ N/A  │
│ATK +0│ATK +0│ATK +0│ATK +1│ N/A  │
│MOVE ½│MOVE 1│MOVE 2│MOVE 2│BLOCK │
└──────┴──────┴──────┴──────┴──────┘
```

---

### 3.5 Tactical Tips

| Terrain | Best For | Why |
|---------|----------|-----|
| **Road** | Rushing | Move fast, but exposed (DEF -1) |
| **Plain** | Normal combat | No bonuses, no penalties |
| **Forest** | Archers hiding | +2 DEF, blocks enemy shots! |
| **Hill** | Sniping | +1 ATK, +1 DEF, great for archers |
| **Ruins** | Tanks defending | +3 DEF, best cover in game |
| **Water** | Blocking paths | Nobody can cross! |

---

### 3.6 Real Battle Example

```
Situation:
┌───┬───┬───┬───┬───┐
│🔴W│   │🌲 │   │🔵A│
│   │   │+2D│   │   │
└───┴───┴───┴───┴───┘

Option A: Archer stays on plain
  → Warrior hits for 30-8 = 22 damage

Option B: Archer moves to forest 🌲
  → Warrior hits for 30-10 = 20 damage
  → PLUS forest blocks ranged attacks through it!

Smart AI picks Option B! 🧠
```

---

## 4. Combat Formula

### The Basic Formula:

```
Final Damage = Attack - Defense
(minimum 1 damage always)
```

That's it! But terrain and crits add more...

---

### 4.1 Step-by-Step Breakdown

#### Step 1: Get Raw Damage

```
Raw Damage = Attacker's Attack + Terrain Attack Bonus

Example:
  Warrior (Attack: 30) standing on Hill (+1 Attack)
  Raw Damage = 30 + 1 = 31
```

#### Step 2: Calculate Defense

```
Defense = Target's Defense + Terrain Defense Bonus

Example:
  Archer (Defense: 8) hiding in Forest (+2 Defense)
  Total Defense = 8 + 2 = 10
```

#### Step 3: Calculate Final Damage

```
Final Damage = Raw Damage - Defense

Example:
  Final Damage = 31 - 10 = 21 HP lost!
```

#### Step 4: Critical Hit? (Random Chance)

```
If critical hit → Damage × 1.5

Normal hit:  21 damage
Critical:    21 × 1.5 = 31 damage! 💥
```

---

### 4.2 Full Example

```
ATTACKER                          TARGET
┌─────────────────┐              ┌─────────────────┐
│ 🔴 Warrior      │    ──────►   │ 🔵 Archer       │
│ Attack: 30      │   ATTACKS    │ Defense: 8      │
│ On: Hill (+1)   │              │ On: Forest (+2) │
└─────────────────┘              └─────────────────┘

CALCULATION:
┌─────────────────────────────────────────────────┐
│ Step 1: Raw Damage = 30 + 1 = 31               │
│ Step 2: Total Defense = 8 + 2 = 10             │
│ Step 3: Final Damage = 31 - 10 = 21            │
│ Step 4: No crit → 21 damage                    │
└─────────────────────────────────────────────────┘

RESULT:
  Archer HP: 80 → 59  (-21 HP)
```

---

### 4.3 Why "Minimum 1 Damage"?

Even if defense is higher than attack, you always deal at least 1 damage:

```
🔵 Healer (Attack: 15) attacks 🔴 Warrior (Defense: 20)

Normal math: 15 - 20 = -5  ❌ Negative!
Game rule:   Minimum 1 damage always ✓

Warrior HP: 150 → 149  (scratched him at least!)
```

---

### 4.4 Quick Reference Table

| Scenario | Attack | Defense | Damage |
|----------|--------|---------|--------|
| Normal hit | 30 | 8 | 22 |
| Hill bonus (+1 atk) | 31 | 8 | 23 |
| Forest cover (+2 def) | 30 | 10 | 20 |
| Both bonuses | 31 | 10 | 21 |
| Critical hit (1.5x) | 30 | 8 | 33 |
| Weak vs Tank | 15 | 20 | **1** (minimum) |

---

### 4.5 Visual Summary

```
         ATTACKER                    TARGET
        ┌────────┐                  ┌────────┐
        │ATK: 30 │                  │DEF: 8  │
        │        │                  │        │
        │Terrain:│                  │Terrain:│
        │  +1    │                  │  +2    │
        └───┬────┘                  └───┬────┘
            │                           │
            ▼                           ▼
      Raw Damage: 31            Total Defense: 10
            │                           │
            └───────────┬───────────────┘
                        ▼
                  31 - 10 = 21
                        │
                        ▼
              ┌─────────────────┐
              │ FINAL DAMAGE: 21│
              │                 │
              │ Archer HP: 80→59│
              └─────────────────┘
```

---

### 4.6 TL;DR

```
Damage = (Your Attack + Your Terrain Bonus) 
       - (Enemy Defense + Enemy Terrain Bonus)

Always at least 1 damage.
Crits do 1.5x damage.
```

---

## 5. Critical Hits

A **critical hit** is a **lucky bonus damage** that happens randomly!

---

### 5.1 Normal Hit vs Critical Hit

```
NORMAL HIT:
  Warrior attacks Archer
  Damage = 30 - 8 = 22 HP

CRITICAL HIT! 💥
  Warrior attacks Archer  
  Damage = 22 × 1.5 = 33 HP  ← 50% bonus damage!
```

---

### 5.2 Think of It Like

| Real Life Example | Game Equivalent |
|-------------------|-----------------|
| Punching someone | Normal hit (22 damage) |
| Punching someone in the face! 👊 | Critical hit (33 damage) |

---

### 5.3 How It Works

```
Every attack has a RANDOM chance to crit

┌─────────────────────────────────────┐
│          ATTACK ROLL                │
│                                     │
│   🎲 Roll dice...                   │
│                                     │
│   90% chance → Normal hit           │
│   10% chance → CRITICAL HIT! 💥     │
│                                     │
│   If crit: Damage × 1.5             │
└─────────────────────────────────────┘
```

---

### 5.4 Example

```
🔴 Mage (Attack: 45) attacks 🔵 Healer (Defense: 10)

Normal damage = 45 - 10 = 35 HP

Scenario A: No crit
  Healer HP: 60 → 25  (survives!)

Scenario B: CRITICAL HIT! 💥
  Damage = 35 × 1.5 = 52 HP
  Healer HP: 60 → 8  (almost dead!)
```

---

### 5.5 Why Crits Matter

```
🔵 Archer has 35 HP left

Normal hit (22 damage):
  35 - 22 = 13 HP  → Archer SURVIVES 😅

Critical hit (33 damage):
  35 - 33 = 2 HP   → Archer almost dead! 😰

Or if Archer has 30 HP:
  Critical hit → 30 - 33 = DEAD! ☠️
```

---

### 5.6 TL;DR

| Term | Meaning |
|------|---------|
| **Critical Hit** | Random lucky hit |
| **Effect** | 1.5× normal damage (50% bonus) |
| **Chance** | ~10% per attack |
| **Why it matters** | Can turn battles! Kill units you couldn't normally |

It adds **randomness and excitement** to combat - sometimes the underdog gets lucky! 🍀

---

## 6. AI Decision Process

There are **2 AIs** in this game, and they think **completely differently**:

---

### 6.1 🔴 Red Team: Minimax AI (The Calculator)

**How it thinks:** "Let me try EVERY possible move and see which one wins!"

#### Step-by-Step:

```
Red's Turn - Warrior can do 3 things:

Option A: Move forward
Option B: Attack enemy
Option C: Wait

AI thinks: "What happens if I pick each one?"
```

#### It Simulates the Future:

```
                    Current Position
                          │
         ┌────────────────┼────────────────┐
         ▼                ▼                ▼
    Option A         Option B         Option C
   "Move forward"   "Attack enemy"      "Wait"
         │                │                │
         ▼                ▼                ▼
   Blue responds     Blue responds    Blue responds
   (AI simulates)    (AI simulates)   (AI simulates)
         │                │                │
         ▼                ▼                ▼
    Score: 45         Score: 60        Score: 20
                          ⭐
                      BEST MOVE!
```

#### Scoring Example:

```
AI asks: "How good is this position for me?"

GOOD things (+ points):
  ✓ My units alive        +50 each
  ✓ My units have HP      +1 per HP
  ✓ Enemy units dead      +100 each
  ✓ Good position         +10

BAD things (- points):
  ✗ My units dead         -100 each
  ✗ Enemy has more HP     -1 per HP
  ✗ Bad position          -10

Total = Score
```

#### Real Example:

```
Option A: Move Warrior forward
  → Blue will attack my Warrior
  → Warrior loses 20 HP
  → Score: 45 points

Option B: Attack with Archer 
  → Enemy Mage dies! ☠️
  → Score: 60 points ⭐ BEST!

Option C: Wait
  → Blue advances freely
  → Score: 20 points

Decision: ATTACK WITH ARCHER!
```

---

### 6.2 🔵 Blue Team: Fuzzy Logic AI (The Human)

**How it thinks:** Uses "IF-THEN" rules like a human would!

#### Step-by-Step:

```
Step 1: Look at situation
Step 2: Apply rules
Step 3: Pick action based on rules
```

#### The Rules:

```
┌─────────────────────────────────────────────────────┐
│                  FUZZY RULES                        │
├─────────────────────────────────────────────────────┤
│ IF my HP is LOW and enemies are CLOSE              │
│    → Be DEFENSIVE (run away, heal)                 │
├─────────────────────────────────────────────────────┤
│ IF enemy HP is CRITICAL and I can reach them       │
│    → KILL THEM! (top priority)                     │
├─────────────────────────────────────────────────────┤
│ IF we're WINNING and I'm HEALTHY                   │
│    → Be AGGRESSIVE (push forward, attack)          │
├─────────────────────────────────────────────────────┤
│ IF teammate HP is LOW and I'm a healer             │
│    → HEAL THEM!                                    │
└─────────────────────────────────────────────────────┘
```

#### Real Example:

```
Situation:
  - My Archer HP: 25/80 (LOW!)
  - Enemy Warrior: 2 cells away (CLOSE!)
  - Enemy Mage HP: 15/70 (CRITICAL!)

Check rules:
  Rule 1: HP LOW + Enemy CLOSE → Be DEFENSIVE ✓
  Rule 2: Enemy CRITICAL + Can kill → PRIORITY TARGET ✓

Both rules apply! Which is stronger?

  Rule 1 strength: 70% (I'm hurt)
  Rule 2 strength: 85% (free kill!)

Decision: ATTACK THE MAGE! (Rule 2 wins)
```

---

### 6.3 Side-by-Side Comparison

| | 🔴 Minimax | 🔵 Fuzzy Logic |
|---|-----------|----------------|
| **Thinks like** | Chess computer | Human player |
| **Method** | Try ALL moves | Apply rules |
| **Speed** | Slow (calculates a lot) | Fast (just checks rules) |
| **Strength** | Never misses best move | Handles uncertainty well |
| **Weakness** | Takes time | Might miss tricky moves |

---

### 6.4 Visual: How They Choose Differently

```
Same situation:
┌───┬───┬───┬───┬───┐
│🔴W│   │   │🔵M│🔵H│   🔵M = Mage (15 HP - weak!)
│   │   │   │   │   │   🔵H = Healer (60 HP - full)
└───┴───┴───┴───┴───┘

🔴 MINIMAX thinks:
  "Attack Mage → score +85 (he dies, +100 points!)"
  "Attack Healer → score +40 (she survives)"
  Decision: Attack Mage ✓

🔵 FUZZY LOGIC thinks:
  "Rule: IF enemy HP CRITICAL → PRIORITY TARGET"
  "Mage HP is critical!"
  Decision: Attack Mage ✓

Same result, DIFFERENT reasoning!
```

---

### 6.5 When They Differ

```
Tricky situation:
┌───┬───┬───┬───┬───┐
│🔴W│   │🔵K│   │🔵H│   
│80 │   │50 │   │60 │   (numbers = HP)
└───┴───┴───┴───┴───┘

🔴 MINIMAX (looks 4 moves ahead):
  "If I attack Knight now...
   Blue heals Knight...
   I attack again...
   Knight dies in 2 turns!"
  Decision: Attack Knight

🔵 FUZZY LOGIC (looks at NOW):
  "Knight HP not critical (50 > 30)"
  "No urgent rule applies"
  Decision: Move forward (safer)

Minimax sees the FUTURE, Fuzzy sees the NOW!
```

---

### 6.6 TL;DR

| AI | How It Decides |
|----|----------------|
| **Minimax** 🔴 | "Calculate every possibility, pick highest score" |
| **Fuzzy** 🔵 | "Check my rules, follow the strongest one" |

---

## 7. Score System

The score is just a **number that tells the AI "how good is this situation for me?"**

**Higher score = Better for me**
**Lower score = Worse for me**

---

### 7.1 How Score is Calculated

Think of it like counting points in a video game:

```
┌─────────────────────────────────────────────────┐
│              SCORE CALCULATION                  │
├─────────────────────────────────────────────────┤
│                                                 │
│  MY STUFF (+ points):                          │
│    Each unit alive     = +50 points            │
│    Each HP remaining   = +1 point              │
│    Good terrain        = +5 points             │
│    Can attack enemy    = +10 points            │
│                                                 │
│  ENEMY STUFF (- points):                       │
│    Each enemy alive    = -50 points            │
│    Each enemy HP       = -1 point              │
│    Enemy good position = -5 points             │
│                                                 │
│  TOTAL = My points - Enemy points              │
└─────────────────────────────────────────────────┘
```

---

### 7.2 Simple Example

```
SITUATION A:
┌─────────────────┬─────────────────┐
│    🔴 RED       │    🔵 BLUE      │
├─────────────────┼─────────────────┤
│ Warrior: 100 HP │ Archer: 50 HP   │
│ Archer:  80 HP  │ Mage:   30 HP   │
└─────────────────┴─────────────────┘

RED's Score:
  My units:  2 × 50 = +100
  My HP:     100 + 80 = +180
  
  Enemy units: 2 × 50 = -100  
  Enemy HP:    50 + 30 = -80

  TOTAL: 100 + 180 - 100 - 80 = +100 points

Score = +100 (Red is winning!)
```

---

### 7.3 Now Let's See Those Numbers (45, 60, 20)

```
CURRENT: Red has Warrior, Blue has Mage (30 HP)

OPTION A: Move Warrior forward
┌───┬───┬───┬───┬───┐
│   │🔴W│   │🔵M│   │   Warrior moved closer
└───┴───┴───┴───┴───┘   but didn't attack

  My units: +50
  My HP:    +100
  Enemy:    -50, -30 HP
  Position: +5 (closer to enemy)
  
  Score: 50 + 100 - 50 - 30 + 5 = 75
  
  BUT Blue will attack back! (-30)
  Final Score: 75 - 30 = 45 ✓


OPTION B: Attack enemy Mage
┌───┬───┬───┬───┬───┐
│🔴W│   │   │💀│   │   Mage DIED!
└───┴───┴───┴───┴───┘

  My units: +50
  My HP:    +100
  Enemy:    +0 (dead = no penalty!)
  Kill bonus: +10
  
  Score: 50 + 100 + 0 + 10 = 160
  
  Blue has no one to attack back!
  Final Score: 160 - 100 = 60 ✓  ⭐ BEST!


OPTION C: Wait (do nothing)
┌───┬───┬───┬───┬───┐
│🔴W│   │   │🔵M│   │   Nothing changed
└───┴───┴───┴───┴───┘

  My units: +50
  My HP:    +100
  Enemy:    -50, -30
  
  Score: 50 + 100 - 50 - 30 = 70
  
  Blue attacks me freely! (-50)
  Final Score: 70 - 50 = 20 ✓
```

---

### 7.4 Visual Summary

```
        OPTIONS AND SCORES
        
Option A          Option B          Option C
"Move"            "Attack"          "Wait"
   │                 │                 │
   ▼                 ▼                 ▼
┌──────┐         ┌──────┐         ┌──────┐
│  45  │         │  60  │         │  20  │
└──────┘         └──────┘         └──────┘
   │                 │                 │
   │                 ⭐                │
   │            HIGHEST!              │
   │                 │                 │
   └────────────────►│◄────────────────┘
                     │
              AI picks this!
```

---

### 7.5 Real-World Analogy

```
Think of it like choosing what to eat:

Option A: Sandwich
  Taste: +5
  Health: +3
  Cost: -2
  Score: 6

Option B: Pizza 🍕
  Taste: +8
  Health: +1
  Cost: -3
  Score: 6

Option C: Salad
  Taste: +2
  Health: +8
  Cost: -1
  Score: 9 ⭐ BEST!

You'd pick Salad (highest score)!
Same logic for the AI!
```

---

### 7.6 TL;DR

| Score | Meaning |
|-------|---------|
| **High (60+)** | Great move! I'm winning! |
| **Medium (30-50)** | Okay move, nothing special |
| **Low (0-20)** | Bad move, enemy benefits |
| **Negative** | Terrible! I'm losing! |

The AI always picks the **highest score** = best move!

---

## 8. Why Scoring is Needed

You're right - the goal is just "kill all enemies." So why scores?

### 8.1 The Problem: AI Can't See the Ending

```
GAME START                           GAME END
    │                                    │
    │    ??? How do I get there ???      │
    │                                    │
    ▼                                    ▼
┌────────┐                          ┌────────┐
│Both    │  ────── 50+ turns ─────► │One team│
│teams   │                          │dead    │
│alive   │                          │        │
└────────┘                          └────────┘

AI thinks: "I know I need to kill everyone...
            but WHICH MOVE gets me there?"
```

---

### 8.2 The Real Problem

```
Turn 1: Red's Warrior can do 3 things

Option A: Move left
Option B: Move right  
Option C: Attack

Which one leads to WINNING 30 turns later?

🤷 AI has NO IDEA!

Nobody dies yet, so all 3 options look "equal" 
if we only check "did enemy team die?"
```

---

### 8.3 That's Why We Need Scores!

Scores tell the AI: **"You're not winning YET, but you're getting CLOSER to winning"**

```
┌─────────────────────────────────────────────────┐
│                                                 │
│  WINNING = All enemies dead                    │
│                                                 │
│  But GETTING CLOSER to winning means:          │
│    ✓ Enemy lost HP (easier to kill later)      │
│    ✓ Enemy lost a unit (fewer threats)         │
│    ✓ My units are healthy (survive longer)     │
│    ✓ Good position (can attack next turn)      │
│                                                 │
│  Score measures "HOW CLOSE am I to winning?"   │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

### 8.4 Example: Why Score Matters

```
Turn 5 - Nobody dead yet. Red picks a move:

Option A: Hit Mage for 20 damage
  Mage HP: 70 → 50
  Score: +20 (damaged enemy = closer to kill!)

Option B: Hit Warrior for 20 damage  
  Warrior HP: 150 → 130
  Score: +10 (damaged, but Warrior has lots of HP)

Option C: Move away
  Nobody damaged
  Score: +0 (no progress toward winning)

WITHOUT scores: All 3 look the same (nobody died)
WITH scores: Option A is best (Mage closer to death!)
```

---

### 8.5 Think of It Like GPS

```
DESTINATION: Enemy base (kill all enemies)

WITHOUT SCORE (no GPS):
  "Am I at the destination? No."
  "Am I at the destination? No."
  "Am I at the destination? No."
  → Wanders randomly, never knows if getting closer!

WITH SCORE (GPS):
  "500 meters away" 
  "400 meters away" ✓ Getting closer!
  "450 meters away" ✗ Wrong way!
  → Knows which direction to go!
```

---

### 8.6 Visual

```
                    WINNING
                    (Score: ∞)
                       🏆
                       │
                       │ Score: 200
                       │ (enemy almost dead)
                       │
                       │ Score: 100  
                       │ (enemy damaged)
                       │
                       │ Score: 50
                       │ (even game)
                       │
                       │ Score: 0
                       │ (game start)
                    ───┴───

Higher score = Closer to winning!
AI climbs UP toward victory!
```

---

### 8.7 Real Example

```
Turn 10:
┌───┬───┬───┐
│🔴W│   │🔵A│   Archer has 15 HP left!
│150│   │15 │
└───┴───┴───┘

Option A: Attack Archer
  → Archer DIES! ☠️
  → Score: +500 (HUGE! One enemy gone!)
  
Option B: Move away
  → Archer survives
  → Score: +10
  
WITHOUT scoring: "Neither wins the game yet"
WITH scoring: "Option A is WAY better!" ⭐

Next turn, easier to win with 1 less enemy!
```

---

### 8.8 TL;DR

| Question | Answer |
|----------|--------|
| **Goal** | Kill all enemies |
| **Problem** | Most turns, nobody dies. How to pick moves? |
| **Solution** | Score = "How close am I to winning?" |
| **High score** | Closer to winning (enemy hurt, my team healthy) |
| **AI picks** | Move with highest score = fastest path to victory |

**Score is like a compass pointing toward victory!** 🧭

---

## 9. Evaluation Components

These are the **7 things** the AI looks at to calculate the score. Think of them as a **checklist**!

---

### 9.1 The 7 Components

```
┌─────────────────────────────────────────────────────┐
│              SCORE = Add all of these              │
├─────────────────────────────────────────────────────┤
│  1. HP Difference        × 1.0   (very important)  │
│  2. Unit Count           × 50.0  (MOST important!) │
│  3. Position             × 0.5   (somewhat)        │
│  4. Threats              × 0.3   (minor)           │
│  5. Mobility             × 0.2   (minor)           │
│  6. Terrain              × 0.15  (small)           │
│  7. Formation            × 0.1   (smallest)        │
└─────────────────────────────────────────────────────┘
```

---

### 9.2 Component 1: HP Difference (Weight: 1.0)

**"Who has more health?"**

```
RED TEAM:                    BLUE TEAM:
Warrior: 100 HP              Archer: 50 HP
Archer:   80 HP              Mage:   30 HP
─────────────                ─────────────
Total:   180 HP              Total:  80 HP

HP Difference = 180 - 80 = +100

Score: +100 × 1.0 = +100 points for Red!
```

**Why it matters:** More HP = survive longer = win!

---

### 9.3 Component 2: Unit Count (Weight: 50.0) ⭐ MOST IMPORTANT

**"Who has more units alive?"**

```
RED: 3 units alive
BLUE: 2 units alive

Difference = 3 - 2 = +1 unit advantage

Score: +1 × 50.0 = +50 points for Red!
```

**Why weight is so high (50)?**
```
Dead unit = 0 damage forever!
          = 0 HP to lose!
          = permanent advantage!

Killing someone is HUGE!
```

---

### 9.4 Component 3: Position (Weight: 0.5)

**"Who controls the battlefield center?"**

```
┌───┬───┬───┬───┬───┐
│   │   │   │   │🔵 │  Blue stuck in corner
├───┼───┼───┼───┼───┤
│   │   │🔴 │   │   │  Red controls CENTER!
├───┼───┼───┼───┼───┤
│   │   │   │   │   │
└───┴───┴───┴───┴───┘

Red position: +10 (center = good)
Blue position: -5 (corner = bad)

Score: (10 - (-5)) × 0.5 = +7.5 points
```

**Why it matters:** Center = can reach anywhere faster!

---

### 9.5 Component 4: Threats (Weight: 0.3)

**"Who can attack more enemies right now?"**

```
┌───┬───┬───┬───┬───┐
│   │🔵A│   │   │   │  Blue Archer can hit: 0 targets
├───┼───┼───┼───┼───┤
│   │   │   │🔴A│   │  Red Archer can hit: 1 target (Blue!)
├───┼───┼───┼───┼───┤
│   │🔵W│   │   │   │  
└───┴───┴───┴───┴───┘

Red threats: 1
Blue threats: 0

Score: (1 - 0) × 0.3 = +0.3 points
```

**Why it matters:** More targets = more options to attack!

---

### 9.6 Component 5: Mobility (Weight: 0.2)

**"Who can move to more places?"**

```
┌───┬───┬───┬───┬───┐
│   │   │💧│💧│💧│  Water blocks Blue!
├───┼───┼───┼───┼───┤
│🔴W│   │💧│   │🔵W│  
├───┼───┼───┼───┼───┤
│   │   │💧│💧│💧│
└───┴───┴───┴───┴───┘

Red can move to: 8 cells (free space!)
Blue can move to: 3 cells (trapped by water!)

Score: (8 - 3) × 0.2 = +1 point
```

**Why it matters:** More movement = more options = flexibility!

---

### 9.7 Component 6: Terrain (Weight: 0.15)

**"Who is standing on better terrain?"**

```
┌───────┬───────┬───────┐
│ RUINS │       │ PLAIN │
│ 🔴W   │       │  🔵W  │
│ +3DEF │       │ +0DEF │
└───────┴───────┴───────┘

Red terrain bonus: +3 (ruins = great cover!)
Blue terrain bonus: +0 (plain = nothing)

Score: (3 - 0) × 0.15 = +0.45 points
```

**Why it matters:** Better terrain = take less damage!

---

### 9.8 Component 7: Formation (Weight: 0.1)

**"Are teammates protecting each other?"**

```
GOOD FORMATION:              BAD FORMATION:
┌───┬───┬───┐               ┌───┬───┬───┐
│🔴W│🔴A│   │               │🔴W│   │   │
├───┼───┼───┤  Grouped!     ├───┼───┼───┤  Scattered!
│🔴H│   │   │  Healer can   │   │   │🔴A│  Healer too
└───┴───┴───┘  heal both!   └───┴───┴───┘  far to heal!

Score: +5                    Score: -5
```

**Why it matters:** Together = support each other!

---

### 9.9 Full Calculation Example

```
RED vs BLUE Situation:

┌────────────────────────────────────────────────────────┐
│ Component        │ Red  │ Blue │ Diff │ Weight │ Score │
├────────────────────────────────────────────────────────┤
│ HP Total         │ 200  │ 120  │ +80  │ × 1.0  │ +80   │
│ Units Alive      │ 3    │ 2    │ +1   │ × 50.0 │ +50   │
│ Position         │ 10   │ 5    │ +5   │ × 0.5  │ +2.5  │
│ Threats          │ 2    │ 1    │ +1   │ × 0.3  │ +0.3  │
│ Mobility         │ 15   │ 10   │ +5   │ × 0.2  │ +1.0  │
│ Terrain          │ 3    │ 0    │ +3   │ × 0.15 │ +0.45 │
│ Formation        │ 8    │ 5    │ +3   │ × 0.1  │ +0.3  │
├────────────────────────────────────────────────────────┤
│                              TOTAL SCORE: │ +134.55   │
└────────────────────────────────────────────────────────┘

Positive score = Red is winning!
```

---

### 9.10 Why Different Weights?

```
IMPORTANCE RANKING:

Unit Count (50.0)  ████████████████████  KILLING IS HUGE!
HP (1.0)           █████████████         Health matters a lot
Position (0.5)     ██████                Good to have
Threats (0.3)      ████                  Nice bonus
Mobility (0.2)     ███                   Small help
Terrain (0.15)     ██                    Minor bonus
Formation (0.1)    █                     Tiny bonus
```

---

### 9.11 TL;DR

| Component | What It Checks | Importance |
|-----------|---------------|------------|
| **Unit Count** | How many alive? | ⭐⭐⭐⭐⭐ HIGHEST |
| **HP** | How much health? | ⭐⭐⭐⭐ |
| **Position** | Control center? | ⭐⭐⭐ |
| **Threats** | Can attack enemies? | ⭐⭐ |
| **Mobility** | Can move freely? | ⭐⭐ |
| **Terrain** | Standing on good ground? | ⭐ |
| **Formation** | Team grouped up? | ⭐ |

**Add them all up = Final Score!**

---

## 10. Special Abilities

Special abilities are **powerful moves** that units can use instead of normal attacks. But they have a **cooldown** (wait time before using again).

---

### 10.1 Think of It Like a Video Game

```
NORMAL ATTACK:              SPECIAL ABILITY:
┌─────────────┐             ┌─────────────┐
│ Basic punch │             │ SUPER MOVE! │
│ Can use     │             │ Much stronger│
│ every turn  │             │ BUT must    │
│             │             │ wait 3 turns │
└─────────────┘             └─────────────┘
```

---

### 10.2 🛡️ WARRIOR Abilities

#### Shield Wall (+5 Defense for 2 turns)

```
Normal:                     With Shield Wall:
┌─────────────┐             ┌─────────────┐
│ Warrior     │             │ Warrior     │
│ Defense: 20 │  ────────►  │ Defense: 25 │  
│             │   ACTIVATE  │ (2 turns)   │
└─────────────┘             └─────────────┘

Enemy attacks:
  Normal:      30 - 20 = 10 damage taken
  Shield Wall: 30 - 25 = 5 damage taken  ← HALF!

Cooldown: Wait 3 turns before using again
```

**When to use:** When enemies are about to attack you!

---

#### Charge (Move AND Attack in same action)

```
NORMAL TURN:                CHARGE:
┌───┬───┬───┬───┬───┐       ┌───┬───┬───┬───┬───┐
│🔴W│   │   │   │🔵A│       │   │   │   │🔴W│💥│
└───┴───┴───┴───┴───┘       └───┴───┴───┴───┴───┘
   │                              CHARGE!
   ▼                        Move + Attack TOGETHER!
Turn 1: Move ──►            
Turn 2: Attack              All in ONE turn!

Cooldown: Wait 4 turns before using again
```

**When to use:** Surprise attack on far enemies!

---

### 10.3 🏹 ARCHER Abilities

#### Snipe (+3 Range, +50% damage)

```
NORMAL ATTACK:              SNIPE:
Range: 5 cells              Range: 8 cells! (5+3)
Damage: 35                  Damage: 52! (35 × 1.5)

┌───┬───┬───┬───┬───┬───┬───┬───┬───┐
│🏹 │   │   │   │   │ ✓ │ ✓ │ ✓ │ ✓ │
└───┴───┴───┴───┴───┴───┴───┴───┴───┘
│←── Normal range ──►│←─ SNIPE extra ─►│

Cooldown: Wait 4 turns
```

**When to use:** Kill someone who thinks they're safe far away!

---

#### Overwatch (Counter-attack enemies who move nearby)

```
Archer activates OVERWATCH:

┌───┬───┬───┬───┬───┐
│   │   │   │   │   │
├───┼───┼───┼───┼───┤
│   │ ⚠️ │ ⚠️ │ ⚠️ │   │   ⚠️ = Danger zone!
├───┼───┼───┼───┼───┤
│   │ ⚠️ │🏹 │ ⚠️ │   │   
├───┼───┼───┼───┼───┤
│   │ ⚠️ │ ⚠️ │ ⚠️ │   │
└───┴───┴───┴───┴───┘

Enemy walks into zone:
┌───┬───┬───┬───┬───┐
│   │   │🔵W│   │   │   Blue walks in
├───┼───┼───┼───┼───┤        │
│   │   │ ↓ │   │   │        ▼
├───┼───┼───┼───┼───┤   AUTOMATIC ATTACK!
│   │   │🏹💥│   │   │   Archer shoots him!
└───┴───┴───┴───┴───┘

Cooldown: Wait 5 turns
```

**When to use:** Guard an area, punish enemies who come close!

---

### 10.4 🔮 MAGE Ability

#### Fireball (3×3 Area Damage)

```
NORMAL ATTACK:              FIREBALL:
Hits 1 enemy                Hits 3×3 area = up to 9 targets!

┌───┬───┬───┬───┬───┐       ┌───┬───┬───┬───┬───┐
│   │   │   │   │   │       │   │🔥│🔥│🔥│   │
├───┼───┼───┼───┼───┤       ├───┼───┼───┼───┼───┤
│🔮 │──►│🔵 │   │   │       │🔮 │🔥│🔵│🔥│   │  ALL enemies
├───┼───┼───┼───┼───┤       ├───┼───┼───┼───┼───┤  in fire zone
│   │   │   │   │   │       │   │🔥│🔵│🔥│   │  take damage!
└───┴───┴───┴───┴───┘       └───┴───┴───┴───┴───┘
    Hits 1                       Hits 2!

Cooldown: Wait 4 turns
```

**When to use:** Enemies grouped together = FIREBALL! 💥

---

### 10.5 ⚔️ KNIGHT Ability

#### Charge (Move AND Attack together)

```
Same as Warrior, but Knight is FASTER!

Knight Movement: 4 (vs Warrior's 2)

┌───┬───┬───┬───┬───┬───┬───┐
│🔵K│   │   │   │   │   │🔴A│
└───┴───┴───┴───┴───┴───┴───┘
         │
         │ CHARGE!
         ▼
┌───┬───┬───┬───┬───┬───┬───┐
│   │   │   │   │   │🔵K│💥│  Ran 5 cells + attacked!
└───┴───┴───┴───┴───┴───┴───┘

Cooldown: Wait 3 turns
```

**When to use:** Assassinate backline enemies (Archers, Mages)!

---

### 10.6 💚 HEALER Ability

#### Heal (Restore 40 HP to ally)

```
Warrior took damage:
┌─────────────┐
│ Warrior     │
│ HP: 60/150  │  ← Hurt!
└─────────────┘
       │
       │ Healer uses HEAL
       ▼
┌─────────────┐
│ Warrior     │
│ HP: 100/150 │  ← +40 HP restored!
└─────────────┘

Cooldown: Wait 2 turns (short!)
```

**When to use:** Teammate low on health!

---

### 10.7 What is COOLDOWN?

```
Turn 1: Use Fireball! 🔥
Turn 2: Cooldown... ⏳ (3 turns left)
Turn 3: Cooldown... ⏳ (2 turns left)
Turn 4: Cooldown... ⏳ (1 turn left)
Turn 5: Fireball READY! 🔥 Can use again!
```

**Stronger ability = Longer cooldown**

---

### 10.8 Quick Reference

| Unit | Ability | What It Does | Cooldown |
|------|---------|--------------|----------|
| **Warrior** | Shield Wall | +5 Defense for 2 turns | 3 turns |
| **Warrior** | Charge | Move + Attack together | 4 turns |
| **Archer** | Snipe | +3 Range, +50% damage | 4 turns |
| **Archer** | Overwatch | Auto-attack nearby enemies | 5 turns |
| **Mage** | Fireball | 3×3 area damage | 4 turns |
| **Knight** | Charge | Move + Attack together | 3 turns |
| **Healer** | Heal | Restore 40 HP to ally | 2 turns |

---

### 10.9 When AI Uses Abilities

```
AI thinks:

"Should I use Fireball?"
  ├── Are 2+ enemies grouped? → YES, FIREBALL! 🔥
  └── Only 1 enemy? → No, save it for later

"Should I use Heal?"
  ├── Teammate below 50% HP? → YES, HEAL! 💚
  └── Everyone healthy? → No, attack instead

"Should I use Charge?"
  ├── Can I reach AND kill someone? → YES, CHARGE! ⚔️
  └── Target will survive? → No, just move closer
```

---

### 10.10 TL;DR

| Concept | Meaning |
|---------|---------|
| **Special Ability** | Powerful move, better than normal attack |
| **Cooldown** | Must wait X turns before using again |
| **When to use** | Save for big moments, not every turn! |

---

## Summary

This document covered:

1. **Turn System** - Each unit moves then attacks
2. **Unit Stats** - HP, Attack, Defense, Range, Movement, Role
3. **Terrain** - Defense bonus, Attack bonus, Movement cost
4. **Combat Formula** - Attack - Defense = Damage (min 1)
5. **Critical Hits** - 10% chance for 1.5x damage
6. **AI Decision Process** - Minimax (calculator) vs Fuzzy (human-like)
7. **Score System** - Numbers showing how good a position is
8. **Why Scoring** - Guides AI toward winning
9. **Evaluation Components** - 7 factors that make up the score
10. **Special Abilities** - Powerful moves with cooldowns

---

*Document created from chat conversation - February 2026*
