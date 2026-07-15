# Recipe: Custom Monster + Encounter (one vertical slice)

> A grounded pattern for a fought enemy in STS2. **Monster and encounter are one unit** —
> a monster is meaningless until an encounter spawns it, so author both together and prove
> the whole slice through `CombatEnemy`. A monster that only registers proves too little.

## Why they are inseparable

The player never touches a `MonsterModel` directly. The reachable host is the **encounter**:
the map/room enters an encounter, the encounter generates its monsters, the monsters take
turns. So the recipe pairs exactly one `CustomEncounterModel` with the `CustomMonsterModel`(s)
it spawns, and the proof drives a real combat where the monster acts.

## Registration (both auto-register — no `[Pool]`)

- **Monster:** subclass `BaseLib.Abstracts.CustomMonsterModel`. The constructor calls
  `CustomContentDictionary.RegisterType(GetType())` — instantiating the type registers it.
  No `[Pool]` (like powers, unlike card/relic/potion).
- **Encounter:** subclass `BaseLib.Abstracts.CustomEncounterModel`; its constructor is
  `protected CustomEncounterModel(RoomType roomType, bool autoAdd = true)`. With the default
  `autoAdd: true` the constructor calls `CustomContentDictionary.AddEncounter(this)` — do
  **not** also register it manually in `Initialize()`; that is redundant.

## Required overrides

**Monster** (`CustomMonsterModel`):
- `public override int MinInitialHp` / `MaxInitialHp` — set both (equal = deterministic HP).
- `protected override MonsterMoveStateMachine GenerateMoveStateMachine()` — the move AI.

**Encounter** (`CustomEncounterModel`):
- `public override bool IsValidForAct(ActModel act)` — which acts it can appear in. Acts:
  `Glory`, `Hive`, `Overgrowth`, `Underdocks` (namespace `MegaCrit.Sts2.Core.Models.Acts`).
  `=> true` makes it valid everywhere (fine for a test; scope it for shipped content).
- `public override IEnumerable<MonsterModel> AllPossibleMonsters` — canonical models:
  `ModelDb.Monster<T>()`.
- `protected override IReadOnlyList<(MonsterModel, string?)> GenerateMonsters()` — the actual
  spawn list: `ModelDb.Monster<T>().ToMutable()` paired with a slot name (`null` slot is valid
  for a minimal single-monster encounter — no custom encounter scene required).

## Move state machine

A monster's behavior is a `MonsterMoveStateMachine` of `MonsterState`s. The workhorse state
is `MoveState`:

```csharp
new MoveState(
    string stateId,                              // e.g. "PECK"
    Func<IReadOnlyList<Creature>, Task> onPerform,  // the move body; targets = player creatures
    params AbstractIntent[] intents)             // e.g. new SingleAttackIntent(6)
```

Set `moveState.FollowUpState = moveState` to loop a single move indefinitely. For several
moves, give every move an explicit successor. A branch is itself a registered
`MonsterState`, not a move/turn:

```csharp
return new MonsterMoveStateMachine(new MonsterState[] { peck }, peck);  // states, initial
```

`SingleAttackIntent(int damage)` (namespace `MegaCrit.Sts2.Core.MonsterMoves.Intents`) is the
telegraphed-attack intent. The `MoveState`/`MonsterMoveStateMachine` types live in
`MegaCrit.Sts2.Core.MonsterMoves.MonsterMoveStateMachine`.

### Compact move contract

Before writing C#, record one row per move: **id, visible intent(s), ordered effect(s), next
state**, plus every branch condition. Intents communicate the action; they do not execute it.
Every visible effect therefore needs both the matching intent and a real Cmd in the body.

| Player-visible action | Intent(s) | Grounded body |
|---|---|---|
| self buff/custom Power | `new BuffIntent()` | `PowerCmd.Apply<T>(..., Creature, amount, Creature, null)` |
| player debuff | `new DebuffIntent()` (often beside an attack intent) | `PowerCmd.Apply<T>(..., targets, amount, Creature, null)` |
| defend | `new DefendIntent()` | `CreatureCmd.GainBlock(Creature, amount, ValueProp.Move, null)` |
| heal | `new HealIntent()` | `CreatureCmd.Heal(Creature, amount)` |
| multi-attack | `new MultiAttackIntent(damage, repeats)` | `DamageCmd.Attack(damage).WithHitCount(repeats).FromMonster(this).Execute(null)` |
| attack + effect | list both intents, e.g. `SingleAttackIntent` + `DebuffIntent` | await the attack, then await the Power/block/buff Cmd in the declared order |

Use the monster's mutable `Creature`, not a canonical model. For a player-targeted Power,
the `targets` passed to the move are the player creatures. `ValueProp.Move` is the vanilla
monster block convention. A custom Power follows `recipes/power.md` (including all three
`powers.json` keys and no `[Pool]`). Attachment alone does not prove a buff: Tier 2 must
observe its downstream effect, such as a later powered attack changing by its `Amount`.

### Explicit cycles and conditional branches

This complete state-machine shape covers a deterministic cycle with both sides of a
half-health branch. Replace names/numbers from SPEC; do not add a branch the design did not
ask for:

```csharp
protected override MonsterMoveStateMachine GenerateMoveStateMachine()
{
    var muster = new MoveState("MUSTER", Muster, new BuffIntent());
    var pressure = new MoveState("PRESSURE", Pressure,
        new SingleAttackIntent(3), new DebuffIntent());
    var flurry = new MoveState("FLURRY", Flurry,
        new MultiAttackIntent(2, 2));
    var guard = new MoveState("GUARD", Guard, new DefendIntent());
    var recover = new MoveState("RECOVER", Recover,
        new DefendIntent(), new HealIntent());
    var healthBranch = new ConditionalBranchState("HEALTH_BRANCH");

    // Ordered, exhaustive predicates: the first true branch wins.
    healthBranch.AddState(guard, () => Creature.CurrentHp >= Creature.MaxHp / 2);
    healthBranch.AddState(recover, () => Creature.CurrentHp < Creature.MaxHp / 2);

    muster.FollowUpState = pressure;
    pressure.FollowUpState = flurry;
    flurry.FollowUpState = healthBranch;
    guard.FollowUpState = muster;
    recover.FollowUpState = muster;

    return new MonsterMoveStateMachine(
        new MonsterState[] { muster, pressure, flurry, healthBranch, guard, recover },
        muster);
}
```

`ConditionalBranchState` evaluates its `AddState` predicates in order and selects the first
true state. Make the cases exhaustive; overlapping predicates silently make later cases
unreachable, while a gap throws `No valid next state found.` A `FollowUpState` cycle is the
deterministic order contract. Random branches are a different design and must not be
substituted for a declared cycle.

Copyable move bodies for that machine:

```csharp
private async Task Muster(IReadOnlyList<Creature> targets)
    => await PowerCmd.Apply<<CustomBuff>>(new ThrowingPlayerChoiceContext(),
        Creature, 2m, Creature, null);

private async Task Pressure(IReadOnlyList<Creature> targets)
{
    await DamageCmd.Attack(3m).FromMonster(this).Execute(null);
    await PowerCmd.Apply<WeakPower>(new ThrowingPlayerChoiceContext(),
        targets, 2m, Creature, null);
}

private async Task Flurry(IReadOnlyList<Creature> targets)
    => await DamageCmd.Attack(2m).WithHitCount(2).FromMonster(this).Execute(null);

private async Task Guard(IReadOnlyList<Creature> targets)
    => await CreatureCmd.GainBlock(Creature, 5m, ValueProp.Move, null);

private async Task Recover(IReadOnlyList<Creature> targets)
{
    await CreatureCmd.GainBlock(Creature, 4m, ValueProp.Move, null);
    await CreatureCmd.Heal(Creature, 3m);
}
```

Required namespaces beyond the basic skeleton: `MegaCrit.Sts2.Core.GameActions.Multiplayer`
for `ThrowingPlayerChoiceContext`; `MegaCrit.Sts2.Core.Models.Powers` for vanilla Powers;
and `MegaCrit.Sts2.Core.ValueProps` for `ValueProp.Move`.

For a custom attack-scaling buff, use the same hook contract as vanilla Strength while
keeping the type/loc/art rules from `recipes/power.md`:

```csharp
public sealed class <CustomBuff> : <ModName>Power
{
    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    public override decimal ModifyDamageAdditive(Creature? target, decimal amount,
        ValueProp props, Creature? dealer, CardModel? cardSource)
        => Owner == dealer && props.IsPoweredAttack() ? Amount : 0m;
}
```

## ⚠️ The one correction that matters — monster attacks do NOT `.Targeting()`

A **monster** move deals damage with `.FromMonster(this).Execute(null)` — the target is
resolved automatically from the move's targets. It does **NOT** take `.Targeting(target)`:

```csharp
private async Task Peck(IReadOnlyList<Creature> targets)
{
    // CORRECT — vanilla SingleAttackMoveMonster pattern:
    await DamageCmd.Attack(6m).FromMonster(this).Execute(null);

    // WRONG — .Targeting() is the CARD pattern (DamageCmd.Attack(...).FromCard(this).Targeting(...)).
    // On a monster it HANGS mid-move: the enemy turn never completes and the player's turn
    // never resumes ("play phase not resumed after enemy turn"). Live-confirmed 2026-07-10.
}
```

This is the top failure mode; the card recipe's `.Targeting()` does not transfer.

## Skeleton

```csharp
// <ModName>Code/Monsters/<Name>.cs
using System.Collections.Generic;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.MonsterMoves.Intents;
using MegaCrit.Sts2.Core.MonsterMoves.MonsterMoveStateMachine;

namespace <ModName>.<ModName>Code.Monsters;

public sealed class <Name> : CustomMonsterModel
{
    public override int MinInitialHp => <hp>;
    public override int MaxInitialHp => <hp>;
    public override string CustomVisualPath =>
        SceneHelper.GetScenePath("creature_visuals/fallback");

    protected override MonsterMoveStateMachine GenerateMoveStateMachine()
    {
        var move = new MoveState("<MOVE_ID>", <MoveBody>, new SingleAttackIntent(<dmg>));
        move.FollowUpState = move;                       // loop
        return new MonsterMoveStateMachine(new MonsterState[] { move }, move);
    }

    private async Task <MoveBody>(IReadOnlyList<Creature> targets)
        => await DamageCmd.Attack(<dmg>m).FromMonster(this).Execute(null);
}
```

```csharp
// <ModName>Code/Encounters/<Name>Encounter.cs
using System.Collections.Generic;
using BaseLib.Abstracts;
using <ModName>.<ModName>Code.Monsters;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Acts;
using MegaCrit.Sts2.Core.Rooms;

namespace <ModName>.<ModName>Code.Encounters;

public sealed class <Name>Encounter : CustomEncounterModel
{
    public <Name>Encounter() : base(RoomType.Monster) { }
    public override bool IsValidForAct(ActModel act) => act is Glory;   // scope as needed
    public override IEnumerable<MonsterModel> AllPossibleMonsters => new[] { ModelDb.Monster<<Name>>() };
    protected override IReadOnlyList<(MonsterModel, string?)> GenerateMonsters()
        => new[] { (ModelDb.Monster<<Name>>().ToMutable(), (string?)null) };
}
```

## Localization

Two JSON loc tables (the `AdditionalFiles` glob in the csproj already picks up any new
`localization/eng/*.json`). Keys are flat, prefixed, and derived by the same rule as every
other type (`Id.Entry = "<NS_UPPER>-<SLUG>"`):

- `monsters.json`: `<NS_UPPER>-<SLUG>.name` — **one key** (`MonsterLoc = name`).
- `encounters.json`: `<NS_UPPER>-<SLUG>.title` + `.loss` — **two keys** (`EncounterLoc = title + loss`).

```json
// monsters.json
{ "CANARYENCOUNTER-CANARY_MITE.name": "Canary Mite" }
// encounters.json
{ "CANARYENCOUNTER-CANARY_MITE_ENCOUNTER.title": "Canary Mite",
  "CANARYENCOUNTER-CANARY_MITE_ENCOUNTER.loss": "The canary has fallen." }
```

## Art contract (explicit placeholder; custom art provisional)

A monster's visual is a Godot **scene** (Spine animation), not a loose PNG. `CustomMonsterModel`
exposes `CustomVisualPath`, plus `CreateCustomVisuals()` / `SetupCustomAnimationStates()` for
full control. Until a custom Spine scene is authored, explicitly override:

```csharp
public override string CustomVisualPath =>
    SceneHelper.GetScenePath("creature_visuals/fallback");
```

Do **not** leave `CustomVisualPath` null as the placeholder strategy. BaseLib then asks the
game for `res://scenes/creature_visuals/<mod>-<class>.tscn`; a missing file logs a fresh
resource error before the game recovers to its error scene, so strict Tier 2 correctly fails.
The explicit built-in fallback loads without that error. **Do not advertise custom monster
art** until an authored scene renders live; the mechanic proof uses this placeholder and
claims only behavior.

## Type + Scenario proof (`CombatEnemy`)

1. **Type:** clean build/package/load; monster + encounter register; loc keys present.
2. **Scenario (`CombatEnemy`):** enter the custom encounter and observe the monster act:
   - `RunManager.Instance.EnterRoomDebug(RoomType.Monster, MapPointType.Unassigned, ModelDb.Encounter<TEncounter>().ToMutable())`
   - assert the monster spawned: `combatState.Enemies.FirstOrDefault(e => e.Monster is TMonster)` is non-null
   - before every turn, assert `monster.NextMove.Id` and its intent types/repeat count
   - snapshot combat history and creature HP/Block/Power state
   - `PlayerCmd.EndTurn(player, canBackOut: false)` — **returns void, do NOT `await`**
   - wait for `Play` with a larger player `TurnNumber` (enemy acted; do not accept the old
     still-`Play` frame)
   - require one new `MonsterPerformedMoveEntry` with the expected id
   - assert each move's exact state contract; for multi-hit, count the new
     `CreatureAttackedEntry.DamageResults`, not only total HP loss
   - force each conditional outcome by changing its real input state, then observe the
     selected move; never call the move body or `ForceCurrentState` as proof

The minimal 2026-07-10 `CanaryEncounter` proved one `PECK`/6-damage turn. The 2026-07-15
`CanaryMonsterVocabulary` then live-proved the multi-turn contract: custom self Power
`2 -> 4` with later attack scaling, Weak `2`, two-hit history, healthy Block `+5`, wounded
HP/Block `+3/+4`, both conditional outcomes, and a complete explicit cycle. A separate
one-sentence `EmberWarden` mod repeated the pipeline with different numbers and zero repair.
See `reference/selftest-harness.md` § CombatEnemy for both driver shapes.

## Checklist

- [ ] Monster: `CustomMonsterModel`; no `[Pool]`; `MinInitialHp`/`MaxInitialHp`/`GenerateMoveStateMachine`
- [ ] Encounter: `CustomEncounterModel(RoomType.Monster)`; `IsValidForAct`/`AllPossibleMonsters`/`GenerateMonsters`
- [ ] No manual `AddEncounter` — the base constructor does it
- [ ] Placeholder visual explicitly overrides `CustomVisualPath` with
      `SceneHelper.GetScenePath("creature_visuals/fallback")`; no missing-resource error
- [ ] Monster attack uses `.FromMonster(this).Execute(null)` — **never `.Targeting()`**
- [ ] `monsters.json` (name) + `encounters.json` (title + loss) with derived ids
- [ ] Every move has matching intent(s), awaited Cmd effect(s), and an explicit successor
- [ ] Every conditional branch is ordered, exhaustive, reachable, and driven through each advertised outcome
- [ ] Multi-hit intent repeat matches `.WithHitCount`; Tier 2 asserts history result count
- [ ] Self buff/custom Power is observed on the monster and changes a later result
- [ ] `CombatEnemy` proves encounter + monster plus every advertised move/branch state invariant
- [ ] custom monster art (Spine scene) claims remain provisional until rendered live
