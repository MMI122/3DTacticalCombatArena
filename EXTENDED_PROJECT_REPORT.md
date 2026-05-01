# 3D Tactical Combat Arena: AI vs AI

## Project Report

## Abstract

This project is a 3D tactical combat game written in Python and built to compare two very different artificial intelligence methods inside the same battlefield. The Red team is controlled by a Minimax agent with Alpha-Beta pruning, while the Blue team is controlled by a Fuzzy Logic agent. The game is not just a visual demo; it contains full state management, turn-based combat, procedural terrain, unit abilities, heuristic evaluation, real-time match control, timeout-based winner resolution, and a browser-based AI decision visualizer.

The project demonstrates how adversarial search and fuzzy inference behave differently when placed in the same tactical environment. It also demonstrates how a game can be structured as a formal state machine with actions, results, terminal conditions, and utility evaluation.

---

## 1. Introduction

### 1.1 Background

Game AI is an effective way to study decision-making because games provide clear rules, observable outcomes, and measurable success conditions. In this project, two distinct AI strategies compete on the same battlefield. The Minimax agent reasons by looking ahead through future states, while the Fuzzy Logic agent reasons by using linguistic rules such as low, medium, high, defensive, aggressive, and critical.

### 1.2 Project Aim

The aim of the project is to build a complete tactical combat system that is both playable and educational. It should show how different AI methods make decisions, how game states evolve over time, and how terrain, unit abilities, and scoring rules affect the final outcome.

### 1.3 Objectives

The project objectives are:

1. Build a turn-based tactical combat game in 3D.
2. Implement a Minimax agent with Alpha-Beta pruning for the Red team.
3. Implement a Fuzzy Logic agent for the Blue team.
4. Design a battlefield where terrain changes movement and combat.
5. Model multiple unit types with different statistics and abilities.
6. Track complete game state, action, and match history.
7. Add a 3-minute timeout rule with score-based winner selection.
8. Provide a browser-based visualizer for AI decisions.
9. Create a modular system that is easy to explain and maintain.

### 1.4 Scope

This report covers:

- game states and transitions,
- unit classes and unit roles,
- battlefield generation and terrain effects,
- combat calculations and critical hits,
- special abilities and cooldowns,
- AI logic and evaluation,
- match timing and score resolution,
- and the final discussion and conclusion.

---

## 2. System Overview

### 2.1 Main Modules

The codebase is divided into separate modules:

- `config/` stores unit templates and global settings.
- `core/` stores game logic, units, battlefield, and match management.
- `ai/` stores Minimax, Fuzzy Logic, and evaluation logic.
- `graphics/` stores the 3D rendering and UI overlay.
- `main.py` starts the game and connects all subsystems.

### 2.2 Overall Match Flow

The match begins with battlefield generation and team placement. After that, the game manager repeatedly asks the active AI for an action, applies the action to the game state, and checks whether the match is finished. The game ends either by elimination or timeout score.

```text
Start Match
   |
   v
Create battlefield and units
   |
   v
RED turn -> choose action -> update state
   |
   v
BLUE turn -> choose action -> update state
   |
   v
Check elimination or timeout
   |
   v
Declare winner and show result
```

---

## 3. Game States and State Transitions

This project is best understood as a state machine. Every important part of the match is represented by a state object.

### 3.1 Game Phase State

The game has four phases:

- `SETUP`
- `RED_TURN`
- `BLUE_TURN`
- `GAME_OVER`

The phase determines who can act and whether the match is still active.

### 3.2 Unit State

Each unit also has its own state flags:

- `IDLE`
- `MOVED`
- `ATTACKED`
- `DEFENDING`
- `DEAD`

These flags are important because a unit can only do a limited number of things in one turn.

### 3.3 Action State

The action system supports four action types:

- `MOVE`
- `ATTACK`
- `ABILITY`
- `WAIT`

An action includes the acting unit and, when needed, a target position or target unit.

### 3.4 Action Result State

When an action is executed, the game creates an `ActionResult`. This stores:

- whether the action succeeded,
- damage dealt,
- damage taken,
- healing done,
- critical hit status,
- unit kill status,
- and a message describing the result.

### 3.5 Match Result State

At the end of the match, the game creates a `MatchResult` that stores:

- the winner,
- the reason the match ended,
- total turns,
- remaining units for each team,
- damage totals,
- match score totals,
- timeout flag,
- duration,
- and the final state.

### 3.6 State Transition Example

```text
Before action:
  RED turn, Warrior alive, Archer in range

Action:
  Red Archer attacks Blue Mage

After action:
  Blue Mage HP reduced
  Blue Mage may die and be removed
  Archer marked as attacked
  If no RED unit can act anymore, turn changes to BLUE
```

This is the same logic used by both the actual game and the AI simulation.

---

## 4. Unit System

### 4.1 Unit Types

The game contains five unit types:

- Warrior
- Archer
- Mage
- Knight
- Healer

Each unit type has a role, a unique stat profile, and special abilities.

### 4.2 Warrior

- HP: 150
- Attack: 30
- Defense: 20
- Movement: 2
- Range: 1
- Critical chance: 10%
- Evasion chance: 5%
- Abilities: Shield Wall, Charge

The Warrior is a tank and front-line defender. It is designed to absorb damage, hold positions, and protect the rest of the team.

### 4.3 Archer

- HP: 80
- Attack: 35
- Defense: 8
- Movement: 3
- Range: 5
- Critical chance: 25%
- Evasion chance: 15%
- Abilities: Snipe, Overwatch

The Archer is a long-range attacker. It is dangerous because it can hit from safety and has the highest critical hit chance among the units.

### 4.4 Mage

- HP: 70
- Attack: 45
- Defense: 5
- Movement: 2
- Range: 4
- Critical chance: 15%
- Evasion chance: 10%
- Ability: Fireball

The Mage is the strongest raw attacker. It is fragile but can deal heavy damage, especially with Fireball.

### 4.5 Knight

- HP: 120
- Attack: 35
- Defense: 15
- Movement: 4
- Range: 1
- Critical chance: 20%
- Evasion chance: 10%
- Ability: Charge

The Knight is a mobile fighter. It can move quickly, flank enemies, and pressure the back line.

### 4.6 Healer

- HP: 60
- Attack: 15
- Defense: 10
- Movement: 3
- Range: 3
- Critical chance: 5%
- Evasion chance: 20%
- Ability: Heal

The Healer is a support unit. Its value is not only in damage but in preserving team health and extending survival.

---

## 5. Battlefield and Terrain System

### 5.1 Battlefield Generation

The battlefield is a 3D grid generated procedurally. This means the map is not always identical. The system creates terrain such as plains, forests, hills, water, mountains, ruins, roads, and bridges.

### 5.2 Terrain Types and Effects

The terrain system in the current code includes:

- Plain: neutral terrain
- Forest: +2 defense, blocks line of sight
- Hill: +1 attack, +1 defense
- Water: impassable
- Mountain: impassable and blocks line of sight
- Ruins: +3 defense and blocks line of sight
- Road: movement bonus, lower defense
- Bridge: allows movement over water

### 5.3 Tactical Meaning of Terrain

Terrain changes the tactical value of a position.

- Forest is strong for ranged units that want cover.
- Hill is good for attackers because it increases offense and defense.
- Ruins are excellent for tanks.
- Road helps fast movement and lane control.
- Water and mountains act as barriers.
- Bridge is a key strategic choke point.

### 5.4 Terrain Example

```text
Road -> fast travel, weak cover
Plain -> neutral ground
Forest -> cover and defense
Hill -> better attack and defense
Ruins -> best defensive cover
Water -> blocked
Mountain -> blocked and line-of-sight blocker
Bridge -> crossing point
```

---

## 6. Combat System

### 6.1 Basic Formula

The combat formula is:

```text
Final Damage = max(1, Attack + terrain attack bonus - Defense - terrain defense bonus)
```

This means damage is never lower than 1.

### 6.2 Critical Hits

Critical hits multiply damage by 1.5. Each unit has its own critical chance. For example, Archer has the highest crit chance, while Healer has the lowest.

### 6.3 Evasion

Enemies can evade attacks based on their evasion chance. This adds uncertainty to combat and makes the result more dynamic.

### 6.4 Combat Example

```text
Warrior attacks Archer
Attack = 30
Archer defense = 8
Forest defense bonus = +2

Final damage = 30 - (8 + 2) = 20

If the hit is critical:
20 x 1.5 = 30 damage
```

### 6.5 Why Combat Matters

Combat determines the long-term advantage in the match. Units that deal damage early can lower the opponent's future choices, while durable units can survive longer and contribute more turns.

---

## 7. Special Abilities

### 7.1 Warrior Abilities

- Shield Wall: increases defense for a turn
- Charge: move and attack in the same action

### 7.2 Archer Abilities

- Snipe: longer range and stronger damage
- Overwatch: punishes movement near the Archer

### 7.3 Mage Ability

- Fireball: area damage over a 3x3 area

### 7.4 Knight Ability

- Charge: rapid attack after movement

### 7.5 Healer Ability

- Heal: restores HP to an ally

### 7.6 Ability Importance

Abilities create strong tactical swings. A well-timed Fireball or Heal can change a battle more than a normal attack.

---

## 8. AI Implementation

### 8.1 Minimax with Alpha-Beta Pruning

The Red team uses Minimax. This algorithm tries to choose the best action by simulating future moves and assuming the opponent also chooses the best reply.

The agent also uses:

- Alpha-Beta pruning,
- transposition tables,
- iterative deepening,
- move ordering,
- and a time limit.

### 8.2 Fuzzy Logic Controller

The Blue team uses Fuzzy Logic. Instead of deep search, it evaluates inputs like HP, threat, and distance using fuzzy rules.

The Blue agent has three fuzzy systems:

- threat assessment,
- action selection,
- target prioritization.

### 8.3 AI Comparison

Minimax is stronger when it can explore the future deeply. Fuzzy Logic is faster and more human-like. The project shows both styles in the same game so the differences are easy to study.

---

## 9. State Evaluation and Heuristics

The Minimax agent uses a weighted evaluation function. The major components are:

- HP difference,
- unit count,
- position,
- threats,
- mobility,
- terrain,
- formation.

The weights show the relative importance of each component. Unit count has the biggest influence because losing a unit is a permanent strategic loss.

The evaluation function allows the Minimax agent to compare many non-terminal states and choose the most promising one.

---

## 10. Match End Conditions and Scoring

### 10.1 Elimination Victory

A match ends normally when one team eliminates the other team.

### 10.2 Timeout Victory

If the match lasts for 3 minutes without elimination, the winner is decided by score.

### 10.3 Match Score Formula

```text
Match Score = (Units Alive x 1000) + (Total HP x 2) + (Kills x 300) + (Damage Dealt x 1)
```

### 10.4 Why the Score System Exists

This rule prevents endless stalemates and makes survival matter. It also rewards team health, kills, and overall pressure.

### 10.5 Draw Handling

If both teams have the same match score at timeout, the match is a draw.

---

## 11. Browser-Based Decision Visualization

The project includes a browser visualizer that shows the AI's thought process.

For Minimax, it can show:

- the root node,
- action branches,
- scores,
- pruned branches,
- and the selected path.

For Fuzzy Logic, it can show:

- scored actions,
- action labels,
- reasoning text,
- and the best choice.

This makes the AI easier to explain in class because the reasoning is visible instead of hidden.

---

## 12. Detailed Game Flow Example

### 12.1 Opening

At the start of a match, both teams are spawned on opposite sides of the battlefield. The battlefield contains terrain that already affects future choices.

### 12.2 Middle Game

As units move, attack, heal, and die, the board changes constantly. The Minimax agent tries to choose lines that lead to the best future utility, while the Fuzzy agent uses the current situation to decide the most reasonable action.

### 12.3 Endgame

At the end of the match, fewer units remain and every decision matters more. The timeout rule becomes important if the game continues for too long.

---

## 13. Discussion

### 13.1 What the Project Demonstrates

This project demonstrates the difference between two AI paradigms:

- search-based reasoning,
- and rule-based reasoning.

It also demonstrates how a game can be formalized as a state machine with actions and transitions.

### 13.2 Strengths

The strongest parts of the project are:

- clear modular design,
- rich tactical mechanics,
- multiple unit types,
- meaningful terrain,
- useful AI comparison,
- and strong visualization support.

### 13.3 Limitations

The project also has some limitations:

- Minimax can become expensive at deeper depths,
- fuzzy rules require tuning,
- randomness can change outcomes,
- and visual complexity can grow quickly.

### 13.4 Why the Report Must Match the Code

Since the game is code-driven, the report must reflect the actual implementation. This is why the report includes the current unit stats, terrain list, state types, combat formula, timeout rule, and scoring system exactly as implemented in the codebase.

---

## 14. Conclusion

The 3D Tactical Combat Arena is a complete AI vs AI tactical game that combines game design, state management, combat systems, terrain strategy, and artificial intelligence in one project. The Red team uses Minimax with Alpha-Beta pruning, while the Blue team uses Fuzzy Logic. The battle system is rich enough to support detailed strategy, and the timeout scoring rule ensures that every match has a fair ending.

The project is successful both as a game and as an educational example of AI comparison. It shows how two different decision-making methods can operate under the same rules while producing different styles of play.

---

## 15. References

1. Russell, S. and Norvig, P. *Artificial Intelligence: A Modern Approach*.
2. Lecture material on adversarial search and game trees.
3. Zadeh, L. A. foundational work on fuzzy sets and fuzzy logic.
4. Python documentation: https://docs.python.org/
5. Ursina Engine documentation: https://www.ursinaengine.org/
6. scikit-fuzzy documentation: https://scikit-fuzzy.readthedocs.io/
7. Source code in this repository, especially `core/game_state.py`, `core/game_manager.py`, `core/battlefield.py`, `core/unit.py`, `ai/minimax_agent.py`, `ai/fuzzy_agent.py`, and `ai/evaluation.py`.

---

## Appendix A. Summary of Important States

- `GamePhase`: SETUP, RED_TURN, BLUE_TURN, GAME_OVER
- `UnitState`: IDLE, MOVED, ATTACKED, DEFENDING, DEAD
- `ActionType`: MOVE, ATTACK, ABILITY, WAIT
- `ActionResult`: success, damage, healing, kill, critical hit, message
- `MatchResult`: winner, reason, scores, timeout, duration, final state

---

## Appendix B. Short Summary

- Two AI teams fight automatically.
- Red uses Minimax with Alpha-Beta pruning.
- Blue uses Fuzzy Logic.
- Five unit types each have a distinct role.
- Terrain changes movement, attack, and defense.
- Matches end by elimination or by timeout scoring.
- The game includes a browser-based visualizer for AI decisions.
