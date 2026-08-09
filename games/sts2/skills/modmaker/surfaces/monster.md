# Surface: monster (enemy encounter)

Everything the pipeline needs for one enemy encounter, in one place: the SPEC envelope it
must declare, the two element classes the author writes, and the proof its verification owes.
Read this page at the `spec.md`, `author.md`, and `verify.md` stages when
`element: enemy encounter`.

A monster and the encounter that spawns it are **always authored as one slice**. They are not
two `elements` plus an interaction edge — that form is for source→dependent links like
card→power. One indivisible slice, one recipe (`recipes/monster.md`), one `CombatEnemy` proof.

## SPEC envelope

Scenario is `CombatEnemy`, not `CombatPlayer`; loc tables are `monsters` + `encounters`;
generated art is one static body shared by combat and bestiary; animation is later.

```markdown
# SPEC — <Mod Name>

- **element**: enemy encounter
- **monster logical id**: <stable local stem, e.g. canary_mite>
- **encounter logical id**: <stable local stem, e.g. canary_mite_encounter>
- **mod id**: <stable mod identity>
- **author**: <author>
- **hp**: <int>   (Min == Max for deterministic HP)
- **moves**:
  - id: <UPPER_SNAKE>
    display name: <shown in the bestiary move list>
    intents: <attack N | multi N x R | buff | debuff | defend | heal; list every visible intent>
    effect: <ordered game-term effects with exact numbers and targets>
    next: <move id | branch id>
- **branches**: none | <branch id>: if <exhaustive condition> -> <move id>; else -> <move id>
- **loop**: <deterministic move/branch cycle; every move and branch has a reachable successor>
- **group**: single | <the monsters the encounter spawns>
- **valid acts**: all | <Glory | Hive | Overgrowth | Underdocks>
- **scenario**: CombatEnemy
- **observe**:
  - the spawned roster matches `group` exactly, and each monster's HP equals the declared value
  - every advertised move id executes in the declared order
  - self buff/custom Power: exact monster Power amount plus a later changed attack/result
  - player debuff: exact player Power amount immediately after application
  - block/heal: exact monster Block and HP deltas from a wounded pre-state
  - multi-attack: observed hit-result count equals the repeat count
  - composite action: every effect from the same move is observed
  - branch: each advertised outcome is forced by its real condition and observed
- **art**: placeholder | generate: <one full creature in a neutral combat-ready pose>
- **art source**: runtime-imagegen | vofy | byo-http | local-image  (generate only)
- **art boundary**: one checked 360x360 static body shared by combat and bestiary; an
  explicit built-in scene remains the fallback; no Spine/attack/hurt/death animation or
  separate phobia body
- **derived ids** (adapter resolves after the semantic SPEC is accepted):
  - monster logical id and localization fields: `name`, one `moves.<MOVE_ID>.title` per move
  - encounter logical id and localization fields: `title`, `loss`
```

A one-move enemy may keep one self-looping move. A multi-move enemy must fill the compact
move/branch contract above before authoring. An intent label is not behavior proof (`INV-1`):
the intent UI shows what the Monster *plans*, which is not evidence the move resolved.

## Every move needs a bestiary title

The bestiary move list looks up `<monster entry>.moves.<MOVE_ID>.title` in the `monsters`
table. When that key is missing the engine falls back to the raw state id, so the player sees
`PECK` and `MUSTER` in screaming snake case. Ship one `moves.<MOVE_ID>.title` per declared
move alongside `.name`, and give each move a `display name` in SPEC so the text is a decision
rather than an accident.

The **intent** label is different: the engine composes it from the move's real damage,
applying live modifiers such as Weak, Vulnerable, and Strength. Pass the base number to the
intent constructor and never hand-write intent text — it would desync from the real hit.

## Author the element classes

**Enemy encounter** — author two classes as one slice (see `recipes/monster.md`), no
`[Pool]` on either:

- `<ModName>Code/Monsters/<Name>.cs` extends `ModMonsterTemplate`: set `MinInitialHp`/
  `MaxInitialHp` (equal for deterministic HP), then translate every SPEC move to one
  `MoveState` whose intent list matches every visible effect. Link deterministic order with
  explicit `.FollowUpState`; for a declared condition, add one `ConditionalBranchState`
  with exhaustive ordered predicates and include it in the machine's state list. A
  self-buff/custom Power uses `PowerCmd.Apply<T>` on `Creature`; a player debuff applies to
  `targets`; block/heal use `CreatureCmd.GainBlock/Heal`; multi-hit uses matching
  `MultiAttackIntent(N, R)` + `.WithHitCount(R)`; a composite move lists and awaits every
  effect in order. Every attack ends with `.FromMonster(this).Execute(null)` — **never
  `.Targeting()`** (that is the card pattern and it hangs the enemy turn).
- Ship `monsters.json` with `.name` and one `moves.<MOVE_ID>.title` per declared move.
- Declare `ModVisualPath` at `images/monsters/<slug>.png`; existence-check it in
  `TryCreateCreatureVisuals()` and call
  `RitsuGodotNodeFactories.CreateFromResource<NCreatureVisuals>` only when present. Keep
  `MonsterAssetProfile` on `creature_visuals/fallback` for the missing-file branch, and set
  `HasDeathSfx => false`. Never put the PNG in the profile's scene path.
- If the monster needs a custom buff/debuff, author its power from `surfaces/power.md` and
  include all three `powers.json` keys. A buff is not proven by attachment alone: SPEC and
  Tier 2 must observe its downstream effect on a later move.
- `<ModName>Code/Encounters/<Name>Encounter.cs` extends `ModEncounterTemplate`, overrides
  `RoomType => RoomType.Monster`, `IsValidForAct`, and `AllPossibleMonsters`
  (`ModelDb.Monster<T>()`), and `GenerateMonsters()` (`ModelDb.Monster<T>().ToMutable()` +
  slot, `null` slot ok). Add one `.Monster<T>()` plus one `.ActEncounter<TAct,T>()` or
  `.GlobalEncounter<T>()` to `RegisterContent()`; do not add a second registration path.

## Self-test driver body

**enemy encounter** → the **`CombatEnemy`** variant in `reference/selftest-harness.md`: enter
the custom encounter, then assert `NextMove.Id` before each turn and the performed-move entry
after, driving the full declared cycle and both outcomes of every branch.

## Proof matrix

- **Assert the spawned roster and HP.** The reference driver locates its monster with
  `Enemies.FirstOrDefault(...)` and logs HP as an info line, which proves neither the declared
  `group` composition nor the HP value. Assert the enemy count and composition match `group`,
  and assert each monster's current HP equals the declared value as its own state proof.
- Assert every advertised move id executes in the declared order, via `NextMove.Id` before and
  the performed-move history after.
- Drive every branch through both outcomes by changing the real condition — mutating HP through
  a public Cmd, not by calling the predicate.
- Traverse the declared cycle far enough to prove it loops rather than terminating.
- Assert each move's concrete consequence: monster Power amount plus a later changed attack for
  a self buff; player Power amount for a debuff; Block/HP deltas from a wounded pre-state;
  observed hit-result count for a multi-attack; every effect of a composite move.
- One HP delta is not sufficient for a multi-move enemy. Before the terminal proof, the harness
  must execute every SPEC move/branch outcome and assert its move history, concrete
  creature/Power state, downstream buff consequence, and multi-hit result count.
- Confirm the bestiary move list shows the shipped titles in a headed pass, not raw state ids.

## Manual fallback (only when the harness cannot reach its scenario)

Grant it:

   - **enemy encounter:** `fight <PREFIX>-<ENCOUNTER_SLUG>` enters the custom encounter
     (run in progress). Confirm the custom monster spawned before ending the turn.

Trigger it:

   **enemy encounter** → end enough turns to traverse the declared cycle; confirm every
   move's visible intent and exact HP/Block/Power change, and drive each conditional outcome.
