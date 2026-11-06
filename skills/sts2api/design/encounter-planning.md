# Combat and encounter planning

Load this reference when a request designs or revises Monsters, Encounters, an Act's fight
pools, or asks how hard a fight should be. A single Monster whose HP, moves, and order are
already exact keeps the fast path and does not load it. Implementation belongs to
`recipes/monster.md` and `recipes/act.md`; this page decides what the fight should be.

## Boundary and evidence

Keep pinned facts, observed conventions, creative decisions, and open hypotheses distinct
(`design/mechanic-planning.md` § Boundary and evidence). The facts below come from direct
inspection of the Monster, Encounter, and Act types in the pinned `sts2.dll` (assembly sha256
`a1f9e653f1e28e4076558fee1e60d218619cb7e057b887c6417f62c62c6d7a52`). Values are Ascension 0.
They describe how native fights are shaped, not limits on a Mod's fight; a static number
never proves a fight is fair or fun.

## Pinned native combat grammar

**Player baseline.** 3 Energy, 5 Cards drawn per turn, Strike `6` damage and Defend `5` Block
for 1 Energy, and 66-80 starting HP (`design/character-foundation.md`).

**Act shape.** Act 1 has two variants, Overgrowth and Underdocks: 15 base rooms, and the
first 3 regular fights come from the weak pool. Act 2 (Hive) has 14 rooms and 2 weak fights;
Act 3 (Glory) has 13 rooms and 2 weak fights. Each native Act pool lists 3 elite and 3 Boss
Encounters. The map avoids drawing two Encounters that share a tag back to back whenever
another choice remains.

**Fight bands.** Fixed-roster native Encounters by Act and tier, as median (min-max). HP is
the roster's total minimum HP. Biggest hit is the largest single attack intent in the roster,
with a multi-attack counted as its total. Peak turn is every enemy's biggest attack landing
in the same turn.

| Act | Tier | Encounters | Enemies | Total HP | Biggest hit | Peak turn |
|---|---|---:|---|---|---|---|
| 1 | weak | 6 | 1 (1-2) | 42 (37-55) | 11 (4-13) | 11.5 (4-18) |
| 1 | regular | 16 | 1 (1-3) | 68.5 (33-93) | 12 (8-16) | 14 (8-30) |
| 1 | elite | 6 | 1 (1-4) | 92.5 (61-140) | 15 (7-17) | 16 (13-28) |
| 1 | Boss | 6 | 1 (1-3) | 231 (173-306) | 17 (9-26) | 18.5 (15-26) |
| 2 | weak | 3 | 1 (1-3) | 79 (72-87) | 21 (8-23) | 23 (21-24) |
| 2 | regular | 9 | 1 (1-4) | 122 (96-171) | 16 (8-23) | 23 (10-39) |
| 2 | elite | 2 | 1 | 153 (145-161) | 18 (15-21) | 18 (15-21) |
| 2 | Boss | 3 | 1 (1-2) | 379 (321-408) | 28 (24-31) | 28 (24-43) |
| 3 | weak | 2 | 1.5 (1-2) | 129 (96-162) | 14 (12-16) | 21.5 (12-31) |
| 3 | regular | 8 | 1 (1-3) | 188 (70-261) | 18 (8-35) | 24 (8-35) |
| 3 | elite | 3 | 1 (1-3) | 276 (234-300) | 35 (29-35) | 35 (29-68) |
| 3 | Boss | 2 | 1.5 (1-2) | 555.5 (512-599) | 25 (24-26) | 32.5 (26-39) |

Encounters with a random roster are left out, so some rows are small samples.

**Monster shape.** Among the 78 Monsters in native Act pools:

- 65 have 2-4 moves; 48 use only a fixed move cycle, 15 a conditional branch, and 17 a random
  branch, which mostly forbids the same move twice in a row (`MoveRepeatType.CannotRepeat`);
- 36 open with an attack; about 30 open with setup instead (buff, debuff, status Cards,
  sleep, or summon);
- intents by Monsters using them: attack 73, buff 54, multi-attack 43, debuff 34, defend 15,
  status Cards 13, summon 6, stun 5, sleep 4, Card debuff 4, heal 3. No pool Monster uses a
  hidden or unknown intent;
- a regular Monster's HP is a small range (median top end about 7% above the bottom); a Boss
  has fixed HP; and
- Ascension raises HP through `ToughEnemies` (median +5.5%) and damage through `DeadlyEnemies`
  (median +12.5%).

**Exemplars.**

- Nibbit (Act 1, alone): Butt 12 -> Slice 6 and 5 Block -> Hiss +2 Strength -> repeat.
- Byrdonis (Act 1 elite, 81-84 HP): opens with Swoop 17, then alternates Peck 3x3 and Swoop.
- Vantom (Act 1 Boss, 173 HP): Ink Blot 7 -> Inky Lance 6x2 -> Dismember 26 plus 3 status
  Cards -> Prepare +2 Strength -> repeat.
- Ceremonial Beast (Act 1 Boss, 252 HP): Stamp sets a visible 150 threshold, then Plow 18
  and +2 Strength repeats. At or below 150 HP it is stunned for one turn, then cycles Beast
  Cry (debuff) -> Stomp 15 -> Crush 17 and +3 Strength.

## Native-shaped recommendation

These are observed conventions. Use them as the default when the user gives no other
direction, and record a deliberate departure in `DESIGN.md` § Decisions.

1. **One question per fight.** Name what the fight tests: block the big hit, kill the
   priority target, race a scaling enemy, play around status Cards or a debuff, or handle
   several enemies. Weak fights teach that question; regular fights ask it; elites ask it
   hard; Bosses combine two and change phase.
2. **Truthful telegraphs.** Every move shows its real intent and exact damage before the
   player commits. Do not hide a move; native pool Monsters never do.
3. **Rhythm.** A cycle of 2-4 moves that mixes pressure and relief: a telegraphed big hit
   followed by a weaker, setup, or recovery turn. Opening with setup gives the player a
   first turn to build. Escalation, such as Strength on a repeating move, makes stalling lose
   to a clock.
4. **Order before randomness.** Default to a fixed cycle. Use a random branch only when the
   concept asks for it, and then forbid the same move twice in a row.
5. **Numbers inside the band.** Start HP, biggest hit, and peak turn from the target Act and
   tier row. A value outside its band is a creative decision with a stated reason; the
   Mod-forward power bias in `design/balance-planning.md` applies to player options, not to
   enemies.
6. **Several enemies.** Split the total HP across the roster. A support enemy that buffs,
   heals, or summons gets less HP than the attacker, so killing it first is a real option.
7. **Phases are visible.** A Boss phase change follows a threshold the player can see and
   push, ideally with one stunned or quiet turn as the transition.

## Compact encounter pass

Resolve only the fields that are still open:

- **placement:** Act, tier, valid Acts, and the pool or entry rule;
- **question:** the one thing the fight tests and the player decision it creates;
- **roster:** each enemy's job (attacker, support, summoner, blocker) and kill priority;
- **moves:** each move's intent, exact effect, and successor; opener; branch rules;
- **numbers:** HP range, biggest hit, and peak turn against the band, plus an estimated
  number of turns to win from stated player output (a derived result, never a measurement);
- **escalation and end:** what makes waiting worse, and why the fight cannot stall forever;
- **edge rules:** a minion or summoner dying, every enemy dying mid-sequence, a phase threshold
  crossed by overkill, a full summon roster, and multiplayer (the host scales Monster Max HP
  and powered Block on its own, `recipes/monster.md`); and
- **Ascension:** none by default. Native-matching HP and damage values for high Ascension are
  a Mod-local route through the public `AscensionHelper.GetValueIfAscension`
  (`grounding.md` § Mod-local Routes).

Intents outside the monster recipe's maintained table (attack, multi-attack, buff, debuff,
defend, heal), such as status Cards, summon, stun, or sleep, are Mod-local routes under the
same rule. They are never reasons to change the accepted fight.

## Fairness review

Before confirmation, check:

- Can an ordinary deck at this point block or survive the peak turn, or is it a forced loss?
- Does a fight hard-counter the Mod's own archetype without a warning the player can read?
- Does a breather follow the biggest hit, and does every intent tell the truth?
- Can the fight stall through endless Block, healing, or summons? Can the player end it?
- Does a multi-enemy fight make kill order a real decision?

Name each concern and its smallest fix: timing, intent, HP split, escalation, or a cap. Do
not call a fight balanced from these checks; difficulty stays an open hypothesis until a
human plays it.

## Handoff

Carry a compact capsule into `interview.md`:

```text
encounter: <Act, tier, placement>
question: <what the fight tests -> player decision>
roster: <enemy jobs and kill priority>
moves: <opener -> cycle, branches, intents>
numbers: <HP, biggest hit, peak turn vs band; turns-to-win estimate and its assumptions>
escalation/end: <clock and stall guard>
edge rules: <deaths, thresholds, summons, multiplayer>
fairness: <concerns and fixes, or none>
open hypotheses: none | <claim and evidence needed>
```

Lower only accepted, supported, exact values into `SPEC.md` through `recipes/monster.md`
and, for Act pools, `recipes/act.md`. `DESIGN.md` owns durable intent and current/not-now
scope.
