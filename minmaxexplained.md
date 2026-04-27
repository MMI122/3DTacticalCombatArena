# Minimax Explained for This Game

This file explains how Minimax works in your 3D tactical game, in the same style as your teacher's adversarial-search slides (state, player, actions, result, terminal, utility), then maps that to every unit type.

## 1. Game Definition (Slide-Style)

### 1.1 INITIAL_STATE(s)

Initial state in this game is not an empty board like Tic-Tac-Toe. It is:

- Procedurally generated battlefield (terrain + spawn zones)
- Two teams
- Turn starts at RED
- Unit action flags reset

Diagram (conceptual):

```text
INITIAL_STATE(s0)

Turn: 0
Phase: RED_TURN

Map: 12x12 (default)

RED spawn side (left)                    BLUE spawn side (right)
┌─────────────────────────────────────────────────────────────────┐
│ R-Warrior  R-Archer  R-Mage  R-Knight      B-Warrior B-Archer │
│                                               B-Mage   B-Knight │
└─────────────────────────────────────────────────────────────────┘

Terrain auto-generated: Plain / Forest / Hill / Water / Mountain / Ruins / Road / Bridge
```

### 1.2 PLAYER(s)

```text
PLAYER(s) =
  RED  if phase == RED_TURN
  BLUE if phase == BLUE_TURN
```

For your match setup:

- RED team agent: Minimax with Alpha-Beta pruning
- BLUE team agent: Fuzzy controller

In Minimax search logic:

- MAX node = team we optimize for
- MIN node = opponent replies

### 1.3 ACTIONS(s)

For each active RED unit, Minimax creates one child state per legal action.
Below is a detailed slide-like branch with different grids and what may happen next.

```text
START STATE s0 (RED to act)

Legend:
  RW = Red Warrior   RA = Red Archer   RH = Red Healer
  BM = Blue Mage     BW = Blue Warrior BH = Blue Healer
  H = Hill (+ATK,+DEF)   U = Ruins (+DEF)   F = Forest (+DEF, blocks LOS)

    0      1      2      3      4
  ┌──────┬──────┬──────┬──────┬──────┐
0  │  .   │  F   │  .   │  BM  │  BH  │
  ├──────┼──────┼──────┼──────┼──────┤
1  │  RW  │  .   │  U   │  .   │  BW  │
  ├──────┼──────┼──────┼──────┼──────┤
2  │  .   │  H   │  RA  │  .   │  .   │
  ├──────┼──────┼──────┼──────┼──────┤
3  │  RH  │  .   │  .   │  .   │  .   │
  └──────┴──────┴──────┴──────┴──────┘
```

```text
ACTIONS(s0): RED candidate branches (examples)

1) a1 = RA Snipe BM
2) a2 = RW Move to U (defensive setup)
3) a3 = RH Move + Hold (safe support posture)
```

### 1.3a Branch A: Choose a1 = RA Snipe BM

```text
Result state s1 after RED action a1
  - BM takes heavy damage (or dies if lethal)
  - RA has spent attack action

    0      1      2      3      4
  ┌──────┬──────┬──────┬──────┬──────┐
0  │  .   │  F   │  .   │ BM*  │  BH  │   BM* = damaged / possibly removed
  ├──────┼──────┼──────┼──────┼──────┤
1  │  RW  │  .   │  U   │  .   │  BW  │
  ├──────┼──────┼──────┼──────┼──────┤
2  │  .   │  H   │  RA  │  .   │  .   │
  ├──────┼──────┼──────┼──────┼──────┤
3  │  RH  │  .   │  .   │  .   │  .   │
  └──────┴──────┴──────┴──────┴──────┘
```

```text
Possible BLUE best response from s1 (MIN node):

b1) BH heals BM         -> reduces RED tactical gain
b2) BW advances on RA   -> immediate threat on fragile archer

Minimax uses the lower-value BLUE reply for this branch.
```

### 1.3b Branch B: Choose a2 = RW Move to Ruins

```text
Result state s2 after RED action a2
  - RW relocates onto U for +DEF survivability
  - No immediate damage now, but future trades improve

    0      1      2      3      4
  ┌──────┬──────┬──────┬──────┬──────┐
0  │  .   │  F   │  .   │  BM  │  BH  │
  ├──────┼──────┼──────┼──────┼──────┤
1  │  .   │  .   │ RW/U │  .   │  BW  │   RW/U = warrior in ruins tile
  ├──────┼──────┼──────┼──────┼──────┤
2  │  .   │  H   │  RA  │  .   │  .   │
  ├──────┼──────┼──────┼──────┼──────┤
3  │  RH  │  .   │  .   │  .   │  .   │
  └──────┴──────┴──────┴──────┴──────┘
```

```text
Possible BLUE best response from s2 (MIN node):

b1) BW attacks RW       -> less effective due to ruins defense bonus
b2) BM targets RA       -> shifts pressure to RED backline

Minimax checks both and keeps the worse one for RED as value(a2).
```

### 1.3c Branch C: Choose a3 = RH Move + Hold

```text
Result state s3 after RED action a3
  - RH moves closer to front for future heal range
  - Immediate tempo is low (no damage this turn)

    0      1      2      3      4
  ┌──────┬──────┬──────┬──────┬──────┐
0  │  .   │  F   │  .   │  BM  │  BH  │
  ├──────┼──────┼──────┼──────┼──────┤
1  │  RW  │  .   │  U   │  .   │  BW  │
  ├──────┼──────┼──────┼──────┼──────┤
2  │  RH  │  H   │  RA  │  .   │  .   │
  ├──────┼──────┼──────┼──────┼──────┤
3  │  .   │  .   │  .   │  .   │  .   │
  └──────┴──────┴──────┴──────┴──────┘
```

```text
Possible BLUE best response from s3 (MIN node):

b1) BM attacks RA       -> punishes RED for low-tempo move
b2) BW pushes center    -> gains map control

This branch often scores lower unless next RED turn converts heal advantage.
```

### 1.3d Slide-Style Branch Summary

```text
              s0 (RED MAX)
            /        |        \
      a1: Snipe   a2: Move U   a3: Healer reposition
        (s1)         (s2)            (s3)
         |            |               |
      BLUE MIN      BLUE MIN        BLUE MIN
        / \           / \             / \
      b1   b2       b1   b2         b1   b2
```

Minimax value selection logic:

- For each action ai, BLUE chooses the response that hurts RED most.
- RED compares those worst-case outcomes and picks the highest among them.

### 1.3e Character-Wise Action Cards (Game-Specific)

```text
WARRIOR (RW)
  Move (range 2), Attack (range 1), Shield Wall, Charge, Wait

ARCHER (RA)
  Move (range 3), Attack (range 5), Snipe, Overwatch, Wait

MAGE (RM)
  Move (range 2), Attack (range 4), Fireball (AoE), Wait

KNIGHT (RK)
  Move (range 4), Attack (range 1), Charge, Wait

HEALER (RH)
  Move (range 3), Attack (range 3), Heal ally, Wait
```

### 1.4 RESULT(s, a)

```text
RESULT(s, a) = next tactical state s'

Detailed transition checklist applied at every branch:

1) Validate legality (range, line of sight, cooldown, alive units)
2) Apply action effect:
   - MOVE: position change
   - ATTACK: damage, crit/evasion checks
   - ABILITY: heal/buff/aoe/snipe effects
   - WAIT: unit ends own turn contribution
3) Update unit flags (has_moved / has_attacked)
4) Remove eliminated units from grid/team
5) If current team has no remaining actors -> end_turn and switch side

Example branch transition (a1: RA Snipe BM):

Before:
  BM HP = 70, BM alive on (3,0)

After:
  BM HP = 70 - snipe_damage
  if BM HP <= 0: BM removed, BLUE unit count drops by 1

Then BLUE response node is expanded from this exact updated grid.
```

State transition includes:

- position updates
- damage/heal application
- cooldown updates
- unit death removal
- action flags updates
- turn switch if no actors remain

### 1.5 TERMINAL(s)

```text
TERMINAL(s) = true  if RED defeated OR BLUE defeated
           = false otherwise
```

Match manager can also end a match by timeout/turn-limit, but core Minimax terminal check in `GameState` is elimination.

### 1.6 UTILITY(s)

At terminal:

- +10000 if RED wins
- -10000 if BLUE wins
- 0 if draw

At non-terminal depth cutoff:

```text
UTILITY(s) =
  hp_score * 1.0
+ unit_count_score * 50.0
+ position_score * 0.5
+ threat_score * 0.3
+ mobility_score * 0.2
+ terrain_score * 0.15
+ formation_score * 0.1
```

This is the exact evaluation structure used by the Minimax agent.

## 2. Minimax Flow in Your Code

## 2.1 High-Level Search Pipeline

```text
get_action(state)
  -> generate legal actions
  -> order actions (ActionEvaluator)
  -> iterative deepening depth=1..max_depth
       -> _search_at_depth(...)
            -> for each action: clone, execute, recurse _minimax
  -> return best action
```

## 2.2 Alpha-Beta Idea (Slide-Like)

```text
                ROOT (MAX: RED)
              /        |        \
           a1          a2        a3
         (MIN)       (MIN)      (MIN)
         /  \         /  \       /  \
       12    8       14   ?     10   ?
             ^            ^          ^
          beta=8      alpha=14    prune if alpha>=beta
```

- `alpha` = best already guaranteed for MAX
- `beta` = best already guaranteed for MIN
- prune branch when `alpha >= beta`

## 2.3 Optimizations Used

- Alpha-Beta pruning
- Transposition table (cache by state hash)
- Iterative deepening
- Action ordering (kill shots, abilities, tactical moves first)
- Time limit guard (default 5s)

## 3. Worked Tactical Example (Game-Style Diagram)

Below is an illustrative (not exact engine output) style like your lecture tree.

```text
UTILITY(s)

Root: RED to play (MAX)

                  s0
        (Red Warrior can act)
              /        \
      a1: Attack      a2: Move to ruins
            |               |
        BLUE reply       BLUE reply
         (MIN)             (MIN)
        /    \            /    \
    b1:heal b2:attack  b1:attack b2:retreat
      |       |          |         |
     +42     +18        +31       +27

MIN chooses lower child:
  value(a1) = min(+42, +18) = +18
  value(a2) = min(+31, +27) = +27

MAX chooses higher action:
  pick a2 (Move to ruins)
```

Interpretation: short-term attack looked strong, but opponent best response reduced value. Better strategic action wins.

## 4. Every Character in Minimax Detail

Stats from `config/units.py`.

## 4.1 Warrior

- HP 150, ATK 30, DEF 20, Move 2, Range 1
- Crit 10%, Evasion 5%
- Abilities: Shield Wall, Charge

Minimax role:

- High survival value in evaluator (affects HP + unit-count longevity)
- Strong front-line anchor
- Good for forced trades and chokepoints

Typical branches evaluated:

```text
Warrior node actions:
  - Move to cover
  - Melee attack
  - Shield Wall (def boost)
  - Charge (burst engage)
  - Wait
```

## 4.2 Archer

- HP 80, ATK 35, DEF 8, Move 3, Range 5
- Crit 25%, Evasion 15%
- Abilities: Snipe, Overwatch

Minimax role:

- High tactical value from long range and kill-shot opportunities
- Action ordering often prioritizes lethal shots
- Sensitive to terrain/LOS and safety in deeper plies

## 4.3 Mage

- HP 70, ATK 45, DEF 5, Move 2, Range 4
- Crit 15%, Evasion 10%
- Ability: Fireball (AoE)

Minimax role:

- Branching spike due to AoE target options
- Can generate high evaluation swing in one action
- Often chosen when multi-target damage improves threat + unit-count trajectory

## 4.4 Knight

- HP 120, ATK 35, DEF 15, Move 4, Range 1
- Crit 20%, Evasion 10%
- Ability: Charge

Minimax role:

- Mobility-heavy tactical flanker
- Useful for move-attack lines that alter enemy reply set
- Strong in search because it creates forcing lines in fewer turns

## 4.5 Healer

- HP 60, ATK 15, DEF 10, Move 3, Range 3
- Crit 5%, Evasion 20%
- Ability: Heal (40 HP)

Minimax role:

- Defensive resource extender
- Heals increase future utility via HP component and unit survival probability
- Strong in deep searches where sustain outvalues short-term poke

## 5. Character-Conditioned Utility Intuition

How each class influences utility components:

```text
Class      HP   UnitCount   Threat   Mobility   Terrain   Formation
Warrior    +++     +++        ++        +         ++         ++
Archer      +       ++        +++       ++        +++         +
Mage        +       ++        +++       +          ++         +
Knight     ++       ++        ++        +++         +         ++
Healer      +      +++         +        ++          +        +++
```

## 6. Why Minimax Works Well in This Game

- Opponent-aware planning (best-response assumption)
- Works with deterministic action simulation
- Tactical depth catches traps and counterplays
- Pruning keeps decision time practical

## 7. Limits and Practical Notes

- Large action space can still be expensive
- Depth cutoff means heuristic quality matters a lot
- Random combat elements (crit/evasion) are not full chance nodes in classic expectiminimax form

## 8. Slide-Ready Summary

```text
INITIAL_STATE(s): generated map + team units + RED turn
PLAYER(s): RED/BLUE by phase
ACTIONS(s): move/attack/ability/wait over active units
RESULT(s,a): execute action -> updated state
TERMINAL(s): one team defeated
UTILITY(s): weighted tactical evaluator (or +/-10000 terminal)

Proceeding:
  generate -> order -> minimax recurse -> alpha-beta prune -> choose max utility action
```
