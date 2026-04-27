# Fuzzy Explained for This Game

This file explains how the Fuzzy Logic AI works in your game, with visual/slide-style diagrams and detailed behavior for every character.

## 1. Big Picture

Your BLUE AI does not build a deep adversarial tree like Minimax.
It does this instead:

```text
Observe state -> convert to fuzzy memberships -> apply IF-THEN rules
-> defuzzify to crisp scores -> score all actions -> pick highest score
```

This creates human-like behavior under uncertainty.

## 2. Three Fuzzy Subsystems in Your Code

Your `FuzzyLogicAgent` uses 3 Mamdani-style systems.

## 2.1 Threat System

Inputs:

- enemy_hp (0..100)
- enemy_attack (0..100 normalized)
- distance (1..10)

Output:

- threat (0..100)

Rule examples from code:

```text
IF distance is close AND enemy_attack is strong -> threat is critical
IF distance is far AND enemy_attack is weak   -> threat is minimal
IF enemy_hp is critical                       -> threat is minimal (finish opportunity)
```

## 2.2 Action System

Inputs:

- own_hp (0..100)
- team_advantage (-100..100)
- enemies_in_range (0..5)

Output:

- aggression (0..100)

Rule examples:

```text
IF winning AND healthy -> aggressive
IF even AND low hp     -> defensive
IF losing AND critical -> defensive
IF many enemies AND healthy -> aggressive
```

## 2.3 Target System

Inputs:

- target_hp (0..100)
- target_damage (0..100 normalized)
- can_kill (0 or 1)

Output:

- priority (0..100)

Rule examples:

```text
IF can_kill is yes -> priority is critical
IF target_damage high AND target_hp low -> critical
IF target_damage low AND target_hp high -> low
```

## 3. Slide-Style Progression (Like Lecture Format)

## 3.1 INITIAL_STATE(s)

```text
INITIAL_STATE(s0): generated battlefield, two teams, RED starts.
```

## 3.2 PLAYER(s)

```text
PLAYER(s):
  RED -> Minimax agent
  BLUE -> Fuzzy agent
```

In this file, we focus on BLUE's decision phase.

## 3.3 ACTIONS(s)

```text
ACTIONS(s) = {
  Move(...), Attack(...), Ability(...), Wait(...)
}
```

## 3.4 RESULT(s, a)

```text
RESULT(s, a) = s'
```

State updates exactly like game engine action execution.

## 3.5 TERMINAL(s)

```text
TERMINAL(s)=true if one team eliminated
```

## 3.6 UTILITY(s) for Fuzzy

Fuzzy does not use one deep recursive utility function. It computes per-action score directly:

- ATTACK: `score = priority * (0.5 + aggression/200)`
- MOVE:
  - aggressive -> reward closing distance
  - defensive -> reward increasing distance
  - balanced -> reward better defense terrain
- ABILITY: `score = 70 + aggression*0.2`
- WAIT: 25 if defensive else 5

Then picks max-scoring action.

## 4. Inference Pipeline Diagram

```text
                    Current Game Snapshot
                             |
             -------------------------------------
             |                  |               |
         Threat FIS         Action FIS      Target FIS
             |                  |               |
         threat score      aggression score  priority score
             \                  |              /
              \                 |             /
               ------ action scoring ---------
                           |
                     sort descending
                           |
                     choose best action
```

## 5. Membership-Function Intuition

## 5.1 own_hp fuzzy sets (Action FIS)

```text
critical: high near 0..20
low:      peaks around ~40
healthy:  high from ~70..100
```

## 5.2 team_advantage fuzzy sets

```text
losing:  strongly negative
even:    around 0
winning: positive side
```

## 5.3 can_kill fuzzy set

```text
no  -> 0
yes -> 1
```

If `can_kill=yes`, target priority becomes near-critical quickly.

## 6. Worked Example (Slide-Like)

```text
BLUE turn:
  own_hp = 38% (low)
  team_advantage = -18 (slightly losing)
  enemies_in_range = 2

Action FIS -> aggression ~34 (defensive leaning)

Candidate actions:
  a1 Attack red mage (can_kill=no, priority=62)
     score = 62 * (0.5 + 34/200) = 62 * 0.67 = 41.5

  a2 Move backward to safer tile
     defensive move reward -> 46

  a3 Ability (if available)
     70 + 34*0.2 = 76.8

Best action: a3 Ability
```

## 7. Every Character in Fuzzy Detail

Stats from `config/units.py`.

## 7.1 Warrior (Tank)

- HP 150, ATK 30, DEF 20, Move 2, Range 1
- Crit 10%, Evasion 5%
- Abilities: Shield Wall, Charge

Fuzzy behavior profile:

- Usually stable aggression due to high HP pool
- Defensive mode uses Shield Wall and holding lines
- Winning mode can Charge to convert pressure

## 7.2 Archer (Long-Range DPS)

- HP 80, ATK 35, DEF 8, Move 3, Range 5
- Crit 25%, Evasion 15%
- Abilities: Snipe, Overwatch

Fuzzy behavior profile:

- High target priority on killable enemies
- Likes high-value ranged picks when `can_kill=yes`
- In low HP states, favors safer spacing and terrain

## 7.3 Mage (AoE Burst)

- HP 70, ATK 45, DEF 5, Move 2, Range 4
- Crit 15%, Evasion 10%
- Ability: Fireball

Fuzzy behavior profile:

- Attack priority jumps when clustered enemies are available
- Ability action often receives high score baseline
- Vulnerable HP can push agent into defensive positioning

## 7.4 Knight (Mobile Fighter)

- HP 120, ATK 35, DEF 15, Move 4, Range 1
- Crit 20%, Evasion 10%
- Ability: Charge

Fuzzy behavior profile:

- Aggressive mode strongly rewards distance-closing moves
- Excellent for converting aggression into engagement
- Balanced mode may still reposition for tactical spacing

## 7.5 Healer (Support)

- HP 60, ATK 15, DEF 10, Move 3, Range 3
- Crit 5%, Evasion 20%
- Ability: Heal (40)

Fuzzy behavior profile:

- Ability score baseline makes healing very attractive when available
- Low HP can force defensive behavior and retreating distance policy
- Team-advantage recovery often driven by sustain decisions

## 8. Action-Type Score Behavior Summary

```text
Action Type   Main Fuzzy Driver                     Typical Outcome
Attack        target priority + aggression          focus weak/high-value targets
Move          aggression policy + terrain safety    advance or retreat intelligently
Ability       high base value + aggression boost    frequent tactical ability usage
Wait          mostly defensive fallback             rare unless safer to hold
```

## 9. Why Fuzzy Works Well Here

- Handles noisy/complex tactical context without full deep tree
- Encodes human-readable behavior rules
- Smoothly transitions (not hard-threshold only)
- Fast compared to deep adversarial search

## 10. Limits

- No explicit deep best-response search like Minimax
- Quality depends on rule/base tuning
- Can miss long tactical traps if local scores look attractive

## 11. Slide-Ready Summary

```text
For each BLUE turn:
1) Gather candidate actions
2) Compute team context (hp%, advantage, enemies in range)
3) Fuzzify inputs
4) Fire rules in threat/action/target systems
5) Defuzzify to crisp aggression/priority values
6) Score each action with fuzzy formulas
7) Pick highest score

Character effect:
- Warrior: front-line stabilizer
- Archer: lethal ranged opportunist
- Mage: AoE swing piece
- Knight: mobility pressure unit
- Healer: sustain and recovery engine
```
