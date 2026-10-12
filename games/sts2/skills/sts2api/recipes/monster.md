# Recipe: Custom Monsters and Encounters

> A grounded pattern for fought enemies in STS2. Monsters and Encounters are separate
> registered nodes joined by explicit roster edges. Author the selected reachable graph
> together and prove only the concrete Encounter variants selected by the current SPEC through
> `CombatEnemy`. A Monster that only registers proves too little.

## Reachability graph

The player never touches a `MonsterModel` directly. The reachable host is an **Encounter**:
the map/room enters an Encounter, the Encounter generates its roster, and those Monsters take
turns. One Monster may be reused by several Encounters, and one Encounter may spawn multiple
or repeated Monster models. Register every selected node exactly once, list every canonical
model that can appear in `AllPossibleMonsters`, and keep the current actual roster a nonempty
subset. Registration without at least one grounded placement/roster edge is not reachability.

## Registration (one explicit RitsuLib content pack)

- **Monster:** subclass `STS2RitsuLib.Scaffolding.Content.ModMonsterTemplate` and register
  it once with `.Monster<TMonster>()`.
- **Encounter:** subclass `ModEncounterTemplate`, override `RoomType`, and register it once
  with `.ActEncounter<TAct,TEncounter>()` for one act or `.GlobalEncounter<TEncounter>()`
  for every act. `IsValidForAct` remains the runtime filter for global registrations.
- Put every step in the scaffold's single `RegisterContent()` content pack. Do not add a
  pool attribute, constructor auto-registration, or a second registry call.

```csharp
RitsuLibFramework.CreateContentPack(MainFile.ModId)
    .Power<<CustomBuff>>()              // only when the monster owns this dependency
    .Monster<<MonsterA>>()
    .Monster<<MonsterB>>()
    .ActEncounter<Glory, <EncounterA>>()
    .GlobalEncounter<<EncounterB>>()
    .Apply();
```

## Required overrides

**Monster** (`ModMonsterTemplate`):
- `public override int MinInitialHp` / `MaxInitialHp` — set both (equal = deterministic HP).
- `protected override MonsterMoveStateMachine GenerateMoveStateMachine()` — the move AI.

**Encounter** (`ModEncounterTemplate`):
- `public override RoomType RoomType => RoomType.Monster` — declare the room type on the
  RitsuLib template rather than inferring it from registration.
- `public override bool IsValidForAct(ActModel act)` — which acts it can appear in. Acts:
  `Glory`, `Hive`, `Overgrowth`, `Underdocks` (namespace `MegaCrit.Sts2.Core.Models.Acts`).
  `=> true` makes it valid everywhere (fine for a test; scope it for shipped content).
- `public override IEnumerable<MonsterModel> AllPossibleMonsters` — canonical models:
  `ModelDb.Monster<T>()`.
- `protected override IReadOnlyList<(MonsterModel, string?)> GenerateMonsters()` — the actual
  spawn list: `ModelDb.Monster<T>().ToMutable()` paired with a slot name (`null` slot is valid
  for a minimal single-monster encounter — no custom encounter scene required).

## Optional shared capability routes

Keep attacks and other move behavior in the move graph. For a separable passive/state bundle on
the Monster, read `reference/model-capabilities.md`; for lifecycle/persistence/RNG, read
`reference/lifecycle-state-rng.md`; and for reachable per-hit attack, healing, Energy/Stars-gain
response, or maximum hand size, read `reference/shared-effect-hooks.md`. Implement on the Monster
or typed capability and keep combat-scope owner/source guards, neutral behavior, and cleanup.

## SPEC `hook participation`: a passive rule that is not a move

A move is the monster acting on its turn. When SPEC declares `hook participation`, the engine is
instead asking the monster for a number or a decision while resolving someone else's event — so
"attacks against this creature deal 25% less damage" is participation, not a move and not a Power.
Read `reference/model-hook-participation.md`.

A Monster reaches the combat-scope set only. Its own body is `Creature`, **not** `Owner`: there is
no owning Player, so a subject guard compares against `Creature` directly.

```csharp
public override decimal ModifyDamageMultiplicative(
    Creature? target, decimal amount, ValueProp props, Creature? dealer, CardModel? cardSource)
{
    if (target != Creature) return 1m;            // SPEC `subject`: damage I receive
    if (!props.IsPoweredAttack()) return 1m;      // SPEC `condition`
    return 0.75m;
}
```

Keep it out of the move state machine. A participation rule has no intent, no move id, and no
bestiary title, and adding a move to represent it makes the intent UI advertise something the
monster never performs.

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

The table projects move callbacks onto `reference/effect-primitives.md`; that shared reference
owns the command contracts. This recipe owns Monster intent parity, state-machine ordering,
`Creature`/`targets`, and the `.FromMonster(this).Execute(null)` distinction.

Use the monster's mutable `Creature`, not a canonical model. For a player-targeted Power,
the `targets` passed to the move are the player creatures. `ValueProp.Move` is the vanilla
monster block convention. A custom Power follows `recipes/power.md` (including all three
`powers.json` keys and no `[Pool]`). Attachment alone does not prove a buff: Tier 2 must
observe its downstream effect, such as a later powered attack changing by its `Amount`.

### Explicit cycles, conditional branches, and fixed-weight random branches

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
deterministic order contract.

When SPEC explicitly selects a random branch, use `RandomBranchState` with positive fixed
weights and declared successors. The state machine supplies its run `Rng`; do not call
`System.Random`, capture mutable weight delegates, or derive weights from prompt-authored code:

```csharp
var random = new RandomBranchState("RANDOM_BRANCH");
random.AddBranch(guard, MoveRepeatType.CanRepeatForever, 2f);
random.AddBranch(pressure, MoveRepeatType.CanRepeatForever, 1f);
guard.FollowUpState = random;
pressure.FollowUpState = random;
return new MonsterMoveStateMachine(
    new MonsterState[] { random, guard, pressure }, random);
```

This admits only declared fixed weights. It does not claim that any probability distribution
was observed in-game; a future Verify stage exercises only the selected branch outcomes.

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
    // never resumes ("play phase not resumed after enemy turn").
}
```

This is the top failure mode; the card recipe's `.Targeting()` does not transfer.

## Skeleton

```csharp
// <ModName>Code/Monsters/<Name>.cs
using System.Collections.Generic;
using System.Threading.Tasks;
using Godot;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.MonsterMoves.Intents;
using MegaCrit.Sts2.Core.MonsterMoves.MonsterMoveStateMachine;
using MegaCrit.Sts2.Core.Nodes.Combat;
using STS2RitsuLib.Scaffolding.Content;
using STS2RitsuLib.Scaffolding.Godot;

namespace <ModName>.Monsters;

public sealed class <Name> : ModMonsterTemplate
{
    public static string FallbackVisualPath =>
        SceneHelper.GetScenePath("creature_visuals/fallback");
    public static string ModVisualPath =>
        $"{MainFile.ResPath}/images/monsters/<slug>.png";

    public override int MinInitialHp => <min-hp>;
    public override int MaxInitialHp => <max-hp>;
    public override MonsterAssetProfile AssetProfile => new(FallbackVisualPath);
    public override bool HasDeathSfx => false;

    protected override NCreatureVisuals? TryCreateCreatureVisuals()
        => ResourceLoader.Exists(ModVisualPath)
            ? RitsuGodotNodeFactories.CreateFromResource<NCreatureVisuals>(
                ResourceLoader.Load<Texture2D>(ModVisualPath))
            : null;

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
using <ModName>.Monsters;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Acts;
using MegaCrit.Sts2.Core.Rooms;
using STS2RitsuLib.Scaffolding.Content;

namespace <ModName>.Encounters;

public sealed class <Name>Encounter : ModEncounterTemplate
{
    public override RoomType RoomType => RoomType.Monster;
    public override bool IsValidForAct(ActModel act) => act is Glory;   // scope as needed
    public override IEnumerable<MonsterModel> AllPossibleMonsters => new[] { ModelDb.Monster<<Name>>() };
    protected override IReadOnlyList<(MonsterModel, string?)> GenerateMonsters()
        => new[] { (ModelDb.Monster<<Name>>().ToMutable(), (string?)null) };
}
```

## Localization

Two JSON loc tables in each required language (the `AdditionalFiles` glob in the csproj
already picks up `localization/<lang>/*.json`). The `eng` and `zhs` tables use identical flat,
prefixed keys derived by the same rule as every other type
(`Id.Entry = "<MOD>_<CATEGORY>_<TYPE>"`):

- `monsters.json`: `<MOD>_MONSTER_<TYPE>.name` — **one key**.
- `encounters.json`: `<MOD>_ENCOUNTER_<TYPE>.title` + `.loss` — **two keys**.

```json
// monsters.json
{ "EXAMPLE_MOD_MONSTER_CLOCKWORK_MITE.name": "Clockwork Mite" }
// encounters.json
{ "EXAMPLE_MOD_ENCOUNTER_CLOCKWORK_MITE_ENCOUNTER.title": "Clockwork Mite",
  "EXAMPLE_MOD_ENCOUNTER_CLOCKWORK_MITE_ENCOUNTER.loss": "{character} was ground down by [gold]{encounter}[/gold]." }
```

```json
// zhs
{ "EXAMPLE_MOD_MONSTER_CLOCKWORK_MITE.name": "发条螨" }
{ "EXAMPLE_MOD_ENCOUNTER_CLOCKWORK_MITE_ENCOUNTER.title": "发条螨",
  "EXAMPLE_MOD_ENCOUNTER_CLOCKWORK_MITE_ENCOUNTER.loss": "{character}被[gold]{encounter}[/gold]碾碎了。" }
```

`.loss` is the run-summary line shown when the player dies to this Encounter, so it describes
the player's defeat in the vanilla shape `{character} was <verb> by [gold]{encounter}[/gold].`
Monster names, move titles, and Encounter titles stay plain Title Case
(`reference/vanilla-text-style.md`).

## Art contract (one static body; animation deferred)

A normal generated monster owns one transparent `images/monsters/<slug>.png`, normalized
to **360x360** with `contain` fit and chroma-key on. This is skill-the-spire's medium static-body
profile, not a game-wide requirement: RitsuLib renders the texture one-to-one, so its pixel
dimensions intentionally define the combat and bestiary footprint.

Do not put the PNG in `MonsterAssetProfile.VisualsScenePath`; that field names a Godot
scene. Override `TryCreateCreatureVisuals()` and use RitsuLib's public resource factory,
while the profile retains the checked fallback scene:

```csharp
public static string FallbackVisualPath =>
    SceneHelper.GetScenePath("creature_visuals/fallback");
public static string ModVisualPath =>
    $"{MainFile.ResPath}/images/monsters/<slug>.png";

public override MonsterAssetProfile AssetProfile => new(FallbackVisualPath);
public override bool HasDeathSfx => false;

protected override NCreatureVisuals? TryCreateCreatureVisuals()
    => ResourceLoader.Exists(ModVisualPath)
        ? RitsuGodotNodeFactories.CreateFromResource<NCreatureVisuals>(
            ResourceLoader.Load<Texture2D>(ModVisualPath))
        : null;
```

When the PNG exists, `RitsuGodotNodeFactories` creates a foot-aligned `Sprite2D`,
`Bounds`, `%CenterPos`, and `IntentPos`. `NCreature` sees no Spine body and safely skips
animator setup. When it is absent, `TryCreateCreatureVisuals()` returns `null`; the original
loader resumes and uses `FallbackVisualPath` without probing a missing custom-id scene.
Do **not** leave the profile path null as the fallback strategy.

The same `MonsterModel.CreateVisuals()` path feeds combat and the default bestiary layout,
so both reuse this one PNG. The generated factory layout is 396x396 with the intent anchor at
`(0,-466)` above the body; headed review checks floor alignment and no crop in both consumers.

This contract is deliberately static. Attack/hurt/death/cast triggers do not animate;
death uses the game's non-Spine fade, and `HasDeathSfx => false` avoids a nonexistent
custom-id death event. There is no separate phobia body, so phobia mode retains the same
static texture. Spine skeleton/atlas/animation, animated move previews, and distinct phobia
skins are later extensions, not current gates.

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

See `reference/selftest-harness.md` § CombatEnemy for the driver shape.

## Checklist

- [ ] Monster: `ModMonsterTemplate`; `MinInitialHp`/`MaxInitialHp`/`GenerateMoveStateMachine`
- [ ] Encounter: `ModEncounterTemplate`; explicit `RoomType.Monster`; `IsValidForAct`/
      `AllPossibleMonsters`/`GenerateMonsters`
- [ ] Every selected Monster and Encounter registered once; actual rosters are nonempty subsets
      of `AllPossibleMonsters`, including intentional repeated Monster entries
- [ ] Static visual checks `images/monsters/<slug>.png` in `TryCreateCreatureVisuals()` and uses
      `RitsuGodotNodeFactories.CreateFromResource<NCreatureVisuals>` only when it exists
- [ ] `MonsterAssetProfile` always names `creature_visuals/fallback`; missing PNG produces no
      missing custom-id resource error
- [ ] `HasDeathSfx => false`; static death uses the non-Spine fade without a missing audio event
- [ ] Monster attack uses `.FromMonster(this).Execute(null)` — **never `.Targeting()`**
- [ ] `monsters.json` (name) + `encounters.json` (title + loss) with derived ids
- [ ] Every move has matching intent(s), awaited Cmd effect(s), and an explicit successor
- [ ] Every conditional branch is ordered, exhaustive, reachable, and driven through each advertised outcome
- [ ] Multi-hit intent repeat matches `.WithHitCount`; Tier 2 asserts history result count
- [ ] Self buff/custom Power is observed on the monster and changes a later result
- [ ] `CombatEnemy` proves encounter + monster plus every advertised move/branch state invariant
- [ ] custom static body is checked in combat and bestiary; no Spine/animation/phobia claim
