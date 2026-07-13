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

Set `moveState.FollowUpState = moveState` to loop a single move indefinitely. Then:

```csharp
return new MonsterMoveStateMachine(new MonsterState[] { peck }, peck);  // states, initial
```

`SingleAttackIntent(int damage)` (namespace `MegaCrit.Sts2.Core.MonsterMoves.Intents`) is the
telegraphed-attack intent. The `MoveState`/`MonsterMoveStateMachine` types live in
`MegaCrit.Sts2.Core.MonsterMoves.MonsterMoveStateMachine`.

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
using MegaCrit.Sts2.Core.MonsterMoves.Intents;
using MegaCrit.Sts2.Core.MonsterMoves.MonsterMoveStateMachine;

namespace <ModName>.<ModName>Code.Monsters;

public sealed class <Name> : CustomMonsterModel
{
    public override int MinInitialHp => <hp>;
    public override int MaxInitialHp => <hp>;

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

## Art contract (provisional until live-rendered)

A monster's visual is a Godot **scene** (Spine animation), not a loose PNG. `CustomMonsterModel`
exposes `CustomVisualPath` (default `null` → falls back to
`res://scenes/creature_visuals/<mod>-<class>.tscn`, and if that is absent to the game's
`creature_visuals/fallback`), plus `CreateCustomVisuals()` / `SetupCustomAnimationStates()`
for full control. A minimal monster loads and fights on the fallback visual. **Do not
advertise custom monster art** until an authored scene renders live; the mechanic proof runs
on fallback visuals and that is explicitly all it claims.

## Type + Scenario proof (`CombatEnemy`)

1. **Type:** clean build/package/load; monster + encounter register; loc keys present.
2. **Scenario (`CombatEnemy`):** enter the custom encounter and observe the monster act:
   - `RunManager.Instance.EnterRoomDebug(RoomType.Monster, MapPointType.Unassigned, ModelDb.Encounter<TEncounter>().ToMutable())`
   - assert the monster spawned: `combatState.Enemies.FirstOrDefault(e => e.Monster is TMonster)` is non-null
   - wait for `PlayerTurnPhase.Play`, record `player.Creature.CurrentHp`
   - `PlayerCmd.EndTurn(player, canBackOut: false)` — **returns void, do NOT `await`**
   - wait for `Play` phase again (enemy has acted, player turn resumed)
   - assert player HP decreased by the attack amount (state delta proves the move connected)

Known-good live canary (2026-07-10, `CanaryEncounter`): custom encounter entered, `CanaryMite`
present at hp=12, `PECK` executed, player HP delta=6, `selftest done`, zero mod-named errors.
See `reference/selftest-harness.md` § CombatEnemy for the full driver body.

## Checklist

- [ ] Monster: `CustomMonsterModel`; no `[Pool]`; `MinInitialHp`/`MaxInitialHp`/`GenerateMoveStateMachine`
- [ ] Encounter: `CustomEncounterModel(RoomType.Monster)`; `IsValidForAct`/`AllPossibleMonsters`/`GenerateMonsters`
- [ ] No manual `AddEncounter` — the base constructor does it
- [ ] Monster attack uses `.FromMonster(this).Execute(null)` — **never `.Targeting()`**
- [ ] `monsters.json` (name) + `encounters.json` (title + loss) with derived ids
- [ ] `CombatEnemy` proof shows encounter + monster present + enemy action + state delta
- [ ] custom monster art (Spine scene) claims remain provisional until rendered live
