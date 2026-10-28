# Recipe: Custom Monsters and Encounters

Everything selected fought enemies need: the SPEC graph, the classes, their text and art, and the
`CombatEnemy` proof. Monsters and Encounters are separate registered nodes joined by explicit
roster edges. Author the selected reachable graph as one slice and prove only the concrete
Encounter variants the current SPEC selects. A Monster that only registers proves too little.

## Reachability graph

The player never touches a `MonsterModel` directly. The reachable host is an **Encounter**: the
map/room enters it, it generates its roster, and those Monsters take turns. One Monster may serve
several Encounters, and one Encounter may spawn multiple or repeated Monster models. Register
every selected node exactly once, list every canonical model that can appear in
`AllPossibleMonsters`, and keep the actual roster a nonempty subset. A Monster without a grounded
placement/roster edge is not reachable.

## SPEC fields

The scenario is `CombatEnemy`, not `CombatPlayer`; the tables are `monsters` + `encounters`;
generated art is one static body shared by combat and bestiary. One `content:` block declares
both node kinds so the edges stay explicit; it does not force a one-to-one pair.

```markdown
# SPEC — <Mod Name>

- **mod id**: <stable mod identity>
- **author**: <author>
- **content**:
  - surface: enemy encounter
  - monsters: <one or more logical ids, names, positive min/max HP, moves, and branches>
  - encounters: <one or more logical ids with nonempty actual and all-possible rosters>
  - relations: <encounter -> ordered roster entries; repeated Monster ids are explicit>
- **registration**:
  - availability: standalone
  - ownership: enemy
  - placement: <plain-language encounter placement rule>
  - valid acts: all | <Glory | Hive | Overgrowth | Underdocks>
- **localization**:
  - languages: [eng, zhs]
  - fields: monster `name`, one `moves.<MOVE_ID>.title` per declared move; encounter
    `title` and `loss`
  - table intent: monsters + encounters
  - formatting: vanilla text style (`reference/vanilla-text-style.md`): names and move titles
    plain Title Case; encounter `loss` names the foe as `[gold]{encounter}[/gold]`
- **effects**:
  - trigger: encounter move
  - target: <per move>
  - moves:
    - id: <UPPER_SNAKE>
      display name: <shown in the bestiary move list>
      intents: <attack N | multi N x R | buff | debuff | defend | heal; list every visible intent>
      effect: <ordered game-term effects with exact numbers and targets>
      next: <move id | branch id>
  - branches: none | <conditional branch with exhaustive conditions> |
    <random branch with positive fixed weight and successor per target>
  - loop: <deterministic move/branch cycle; every move and branch has a reachable successor>
  - scaling: <named values and bounds, or none>
- **hook participation**: none | one or more; see § Hook participation below
- **state**:
  - lifetime: combat
  - owner: the spawned monster
  - advance/check: the declared move/branch cycle
  - reset: combat end
  - persistence: none
  - visible state: native intent display (a plan, not behavior proof)
- **presentation**:
  - assets: static monster body; placeholder | generate: <one full creature in a neutral
    combat-ready pose>
  - art source: host-tool | backend:<name> | local-image (generate only)
  - native presentation: combat body plus default bestiary entry
  - art boundary: one checked 360x360 static body shared by combat and bestiary; no
    Spine/attack/hurt/death animation or separate phobia body
- **fallback**:
  - missing asset: explicit built-in creature-visuals scene
  - unavailable seam: preserve behavior or stop with an explicit unsupported boundary
- **proof**:
  - scenario: CombatEnemy
  - driver: enter the custom encounter and end the turns needed to traverse the cycle
  - invariants:
    - the spawned roster matches the selected encounter's actual roster exactly, including
      repetitions, and each monster's HP lies inside its declared range
    - every advertised move id executes in the declared order
    - self buff/custom Power: exact monster Power amount plus a later changed attack/result
    - player debuff: exact player Power amount immediately after application
    - block/heal: exact monster Block and HP deltas from a wounded pre-state
    - multi-attack: observed hit-result count equals the repeat count
    - composite action: every effect from the same move is observed
  - boundary cases: each advertised branch outcome is forced by its real condition and observed
- **adapter output** (written to MEMORY after acceptance): resolved monster and encounter
  content ids, localization keys, monster body asset role, and framework diagnostic record
```

A one-move enemy may keep one self-looping move. A multi-move enemy fills the compact move
contract below before authoring. An intent label shows what the Monster *plans*; it is never
evidence the move resolved.

## Registration (one explicit content pack)

- **Monster:** subclass `ModMonsterTemplate`, registered once with `.Monster<TMonster>()`.
- **Encounter:** subclass `ModEncounterTemplate`, override `RoomType`, and register once with
  `.ActEncounter<TAct,TEncounter>()` for one Act or `.GlobalEncounter<TEncounter>()` for every
  Act; `IsValidForAct` stays the runtime filter for global registrations.
- Every step goes in the scaffold's single `RegisterContent()` content pack. No pool attribute,
  constructor auto-registration, or second registry call.

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
- `MinInitialHp` / `MaxInitialHp`: set both (equal for deterministic HP).
- `protected override MonsterMoveStateMachine GenerateMoveStateMachine()`: the move AI.

**Encounter** (`ModEncounterTemplate`):
- `public override RoomType RoomType => RoomType.Monster`, declared rather than inferred.
- `public override bool IsValidForAct(ActModel act)`: Acts are `Glory`, `Hive`, `Overgrowth`,
  `Underdocks` (`MegaCrit.Sts2.Core.Models.Acts`); scope shipped content rather than `=> true`.
- `public override IEnumerable<MonsterModel> AllPossibleMonsters`: canonical
  `ModelDb.Monster<T>()` models.
- `protected override IReadOnlyList<(MonsterModel, string?)> GenerateMonsters()`: the actual
  spawn list, `ModelDb.Monster<T>().ToMutable()` paired with a slot name (`null` is valid for a
  minimal single-Monster Encounter; no custom Encounter scene is required).

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
        "res://<ModName>/images/monsters/<slug>.png";

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

## Monster attacks never use `.Targeting()`

A **monster** move deals damage with `.FromMonster(this).Execute(null)`; the target comes from the
move's targets. It never takes `.Targeting(target)`:

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

This is the top Monster failure mode; the Card recipe's `.Targeting()` does not transfer.

**Multiplayer** needs no Monster code. That untargeted attack hits every player, as vanilla
attacks do. The host scales the Monster on its own: Max HP and powered move Block (`ValueProp.Move`)
by `players x 1.1` in Act 1, `x 1.2` in Act 2, and `x 1.2` (`x 1.3` for a boss) in Act 3, and a
self-applied Power by the same factor only when it sets `ShouldScaleInMultiplayer`
(`recipes/power.md` § Multiplayer). A scenario that asserts Max HP or Block computes the
expected value from `t.State.Players.Count`; `t.EnemyTurn` already reports only what reached
the acting player.

## Move state machine

A Monster's behavior is a `MonsterMoveStateMachine` of `MonsterState`s
(`MegaCrit.Sts2.Core.MonsterMoves.MonsterMoveStateMachine`). The workhorse is `MoveState`:

```csharp
new MoveState(
    string stateId,                              // e.g. "PECK"
    Func<IReadOnlyList<Creature>, Task> onPerform,  // the move body; targets = player creatures
    params AbstractIntent[] intents)             // e.g. new SingleAttackIntent(6)
```

`moveState.FollowUpState = moveState` loops a single move. Several moves each get an explicit
successor, and a branch is itself a registered `MonsterState`, not a move or turn.
`SingleAttackIntent(int damage)` lives in `MegaCrit.Sts2.Core.MonsterMoves.Intents`.

A move body receives `IReadOnlyList<Creature> targets`; the mutable Monster supplies `this` and
its own `Creature`, with no owner Player or Card source. Lower effects through
`reference/effect-primitives.md` and await them in the exact move order. Commands that need a
choice context use a fresh `ThrowingPlayerChoiceContext` inside the move; player effects bind only
to the live `targets`. Monster resource, Orb, and run-acquisition effects are blocked unless SPEC
and the callback identify a receiving Player through a target Creature. Use the mutable
`Creature`, never a canonical model.

### Compact move contract

Before writing C#, record one row per move: **id, visible intent(s), ordered effect(s), next
state**, plus every branch condition. Intents communicate the action; they do not execute it, so
every visible effect needs both its intent and a real Cmd in the body.

| Player-visible action | Intent(s) | Grounded body |
|---|---|---|
| self buff/custom Power | `new BuffIntent()` | `PowerCmd.Apply<T>(..., Creature, amount, Creature, null)` |
| player debuff | `new DebuffIntent()` (often beside an attack intent) | `PowerCmd.Apply<T>(..., targets, amount, Creature, null)` |
| defend | `new DefendIntent()` | `CreatureCmd.GainBlock(Creature, amount, ValueProp.Move, null)` |
| heal | `new HealIntent()` | `CreatureCmd.Heal(Creature, amount)` |
| multi-attack | `new MultiAttackIntent(damage, repeats)` | `DamageCmd.Attack(damage).WithHitCount(repeats).FromMonster(this).Execute(null)` |
| attack + effect | list both intents, e.g. `SingleAttackIntent` + `DebuffIntent` | await the attack, then the Power/Block/buff Cmd in the declared order |

`ValueProp.Move` is the vanilla Monster Block convention. A custom Power follows
`recipes/power.md` (all three `powers.json` keys, no `[Pool]`); attachment alone does not prove a
buff, so Tier 2 observes its downstream effect, such as a later powered attack changing by its
`Amount`.

### Explicit cycles, conditional branches, and fixed-weight random branches

This shape covers a deterministic cycle with both sides of a half-health branch. Take names and
numbers from SPEC and add no branch the design did not ask for:

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

`ConditionalBranchState` evaluates its `AddState` predicates in order and selects the first true
state. Make them exhaustive: overlapping predicates silently make later cases unreachable, and a
gap throws `No valid next state found.` A `FollowUpState` cycle is the deterministic order
contract.

Only when SPEC selects a random branch, use `RandomBranchState` with positive fixed weights and
declared successors. The state machine supplies its run `Rng`; never call `System.Random`,
capture mutable weight delegates, or derive weights from prompt-authored code. Verify exercises
only the selected branch outcomes, never a probability distribution.

```csharp
var random = new RandomBranchState("RANDOM_BRANCH");
random.AddBranch(guard, MoveRepeatType.CanRepeatForever, 2f);
random.AddBranch(pressure, MoveRepeatType.CanRepeatForever, 1f);
guard.FollowUpState = random;
pressure.FollowUpState = random;
return new MonsterMoveStateMachine(
    new MonsterState[] { random, guard, pressure }, random);
```

Copyable move bodies for that machine (`ThrowingPlayerChoiceContext` is in
`MegaCrit.Sts2.Core.GameActions.Multiplayer`, vanilla Powers in `MegaCrit.Sts2.Core.Models.Powers`,
`ValueProp` in `MegaCrit.Sts2.Core.ValueProps`):

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

A custom attack-scaling buff uses the same hook contract as vanilla Strength, with the type,
text, and art rules of `recipes/power.md`:

```csharp
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;
using STS2RitsuLib.Scaffolding.Content;

public sealed class <CustomBuff> : ModPowerTemplate
{
    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    public override decimal ModifyDamageAdditive(Creature? target, decimal amount,
        ValueProp props, Creature? dealer, CardModel? cardSource)
        => Owner == dealer && props.IsPoweredAttack() ? Amount : 0m;
}
```

## Hook participation: a passive rule that is not a move

A move is the Monster acting on its turn. A SPEC `hook participation` block has the engine ask the
Monster for a number or decision while resolving someone else's event: "attacks against this
creature deal 25% less damage" is participation, not a move and not a Power
(`reference/model-hook-participation.md`). A Monster receives combat-scope hooks only (45 of 68);
run-scope hooks never reach it, and Build rejects them. Its own body is `Creature`, **not**
`Owner`: there is no owning Player.

```csharp
public override decimal ModifyDamageMultiplicative(
    Creature? target, decimal amount, ValueProp props, Creature? dealer, CardModel? cardSource)
{
    if (target != Creature) return 1m;            // SPEC `subject`: damage I receive
    if (!props.IsPoweredAttack()) return 1m;      // SPEC `condition`
    return 0.75m;
}
```

Keep it out of the move state machine. A participation rule has no intent, move id, or bestiary
title, and a move standing in for it makes the intent UI advertise something never performed.

## Optional routes

Keep attacks and other move behavior in the move graph. Read a route only when SPEC selects it,
append only its SPEC block for independent passive behavior, and keep combat-scope owner/source
guards, phase/order, the neutral case, lifetime/reset, cleanup, and a real `CombatEnemy`
assertion. Never widen a Monster rule into a process-wide listener.

- a separable passive/state bundle: `reference/model-capabilities.md`;
- lifecycle/persistence, or deterministic random choices beyond the declared move graph:
  `reference/lifecycle-state-rng.md`;
- reachable per-hit attack, healing, Energy/Stars-gain response, or maximum hand size:
  `reference/shared-effect-hooks.md`.

## Localization

Two flat tables per required language, keyed by the usual derived entry
(`Id.Entry = "<MOD>_<CATEGORY>_<TYPE>"`):

- `monsters.json`: `<MOD>_MONSTER_<TYPE>.name` plus one `<MOD>_MONSTER_<TYPE>.moves.<MOVE_ID>.title`
  per declared move;
- `encounters.json`: `<MOD>_ENCOUNTER_<TYPE>.title` and `.loss`.

```json
// monsters.json
{ "EXAMPLE_MOD_MONSTER_CLOCKWORK_MITE.name": "Clockwork Mite",
  "EXAMPLE_MOD_MONSTER_CLOCKWORK_MITE.moves.PECK.title": "Peck" }
// encounters.json
{ "EXAMPLE_MOD_ENCOUNTER_CLOCKWORK_MITE_ENCOUNTER.title": "Clockwork Mite",
  "EXAMPLE_MOD_ENCOUNTER_CLOCKWORK_MITE_ENCOUNTER.loss": "{character} was ground down by [gold]{encounter}[/gold]." }
```

```json
// zhs
{ "EXAMPLE_MOD_MONSTER_CLOCKWORK_MITE.name": "发条螨",
  "EXAMPLE_MOD_MONSTER_CLOCKWORK_MITE.moves.PECK.title": "啄击" }
{ "EXAMPLE_MOD_ENCOUNTER_CLOCKWORK_MITE_ENCOUNTER.title": "发条螨",
  "EXAMPLE_MOD_ENCOUNTER_CLOCKWORK_MITE_ENCOUNTER.loss": "{character}被[gold]{encounter}[/gold]碾碎了。" }
```

**Every move needs a bestiary title.** The bestiary move list looks up
`<monster entry>.moves.<MOVE_ID>.title`; when it is missing the engine shows the raw state id
(`PECK`, `MUSTER`). Give each move a SPEC `display name`. The **intent** label is different: the
engine composes it from the move's real damage with live modifiers (Weak, Vulnerable, Strength).
Pass the base number to the intent constructor and never hand-write intent text.

`.loss` is the run-summary line when the player dies to this Encounter, in the vanilla shape
`{character} was <verb> by [gold]{encounter}[/gold].` Monster names, move titles, and Encounter
titles stay plain Title Case (`reference/vanilla-text-style.md`).

## Art contract (one static body; animation deferred)

A generated Monster owns one transparent `images/monsters/<slug>.png`, normalized to **360x360**
with `contain` fit and chroma-key on. This is the pack's medium static-body profile: RitsuLib
renders the texture one-to-one, so its pixels define the combat and bestiary footprint.

Never put the PNG in `MonsterAssetProfile.VisualsScenePath`, which names a Godot scene. The
skeleton's `TryCreateCreatureVisuals()` loads the PNG through RitsuLib's public resource factory
when it exists, creating a foot-aligned `Sprite2D`, `Bounds`, `%CenterPos`, and `IntentPos`;
`NCreature` sees no Spine body and skips animator setup. When the PNG is absent it returns
`null`, and the original loader resumes with `FallbackVisualPath` without probing a missing
custom-id scene. Never leave the profile path null as the fallback strategy.

`MonsterModel.CreateVisuals()` feeds both combat and the default bestiary, so both reuse this one
PNG. The generated layout is 396x396 with the intent anchor at `(0,-466)`; headed review checks
floor alignment and no crop in both consumers.

The contract is deliberately static: attack/hurt/death/cast triggers do not animate, death uses
the game's non-Spine fade, and `HasDeathSfx => false` avoids a nonexistent custom-id death event.
Phobia mode keeps the same texture. Spine skeleton/atlas/animation, animated move previews, and
phobia skins are later extensions.

## Checklist

- [ ] Monster: `ModMonsterTemplate` with `MinInitialHp`/`MaxInitialHp`/`GenerateMoveStateMachine`.
- [ ] Encounter: `ModEncounterTemplate` with explicit `RoomType.Monster`, `IsValidForAct`,
      `AllPossibleMonsters`, and `GenerateMonsters`.
- [ ] Every selected node registered once; actual rosters are nonempty subsets of
      `AllPossibleMonsters`, with intentional repeats explicit.
- [ ] Monster attacks use `.FromMonster(this).Execute(null)`, **never `.Targeting()`**.
- [ ] Every move has matching intent(s), awaited Cmd effect(s), and an explicit successor;
      multi-hit intent repeats match `.WithHitCount`.
- [ ] Every conditional branch is ordered, exhaustive, and reachable.
- [ ] `monsters.json` (name plus one move title per move) and `encounters.json` (title + loss).
- [ ] The static visual is existence-checked in `TryCreateCreatureVisuals()`; the profile always
      names `creature_visuals/fallback`; `HasDeathSfx => false`.

## Self-test driver body

Use the **`CombatEnemy`** host: one `plan.Encounter<TEncounter>(name, body)` scenario per selected
reachable Encounter variant. It finishes any combat in progress, enters a fresh mutable copy of the
Encounter with its real roster and HP, and waits for the player's Play phase. It applies no
Plating, so the enemy's hits land, and raises the player to 999/999 HP so a long cycle cannot end
the run; pass `keepPlayerHp: true` when a move reads the player's HP. The roll call already lists
every Mod Monster (`hp=min-max`) and every Encounter an Act or a scenario names, with its roster.

- `t.Monster<TMonster>()` returns the live Creature and fails the scenario when it did not spawn;
- before every turn, assert intent types and repeat count from `t.NextMove(monster).Intents`;
- `await t.EnemyTurn(monster, "MOVE_ID")` asserts `NextMove.Id`, ends the player turn with enemies
  acting, waits for the next player Play phase, requires one new `MonsterPerformedMoveEntry` with
  that id, and returns `SelfTestEnemyTurn(MoveId, PlayerHpLost, Hits, UnblockedDamage)`;
- assert each move's exact state contract; for multi-hit, assert the returned `Hits` (new
  `CreatureAttackedEntry.DamageResults`), not only total HP loss;
- force each conditional outcome by changing its real input through a public Cmd, then observe the
  selected move. Never call the move body, the predicate, `PerformMove`, `SetMoveImmediate`, or
  `ForceCurrentState` as proof: they bypass normal enemy turn selection. A move body's own
  `attacked:` log is diagnostic only.

```csharp
plan.Encounter<EmberHoundEncounter>("ember_hound_bites_for_6", async t =>
{
    var hound = t.Monster<EmberHound>();
    var bite = await t.EnemyTurn(hound, "BITE");
    t.Proof(bite.PlayerHpLost == 6 && bite.Hits == 1,
        $"bite expected hp=6 hits=1 observed={bite.PlayerHpLost}/{bite.Hits}");
});
```

The representative cycle above (`MUSTER -> PRESSURE -> FLURRY -> HEALTH_BRANCH -> GUARD|RECOVER ->
MUSTER`) reads each move's intents before its turn, proves the self buff by a later changed
attack, and reaches both branches through a real HP change:

```csharp
plan.Encounter<<Name>Encounter>("<name>_cycle_and_branches", async t =>
{
    var mob = t.Monster<<Name>>();
    t.Proof(t.NextMove(mob).Intents.OfType<BuffIntent>().Count() == 1, "MUSTER intent expected=buff observed=match");
    await t.EnemyTurn(mob, "MUSTER");
    t.Proof(t.PowerAmount<<CustomBuff>>(mob) == 2,
        $"self power expected=2 observed={t.PowerAmount<<CustomBuff>>(mob)}");

    var pressureIntents = t.NextMove(mob).Intents;
    t.Proof(pressureIntents.OfType<SingleAttackIntent>().Count() == 1 &&
            pressureIntents.OfType<DebuffIntent>().Count() == 1,
        "PRESSURE intents expected=attack+debuff observed=match");
    var pressure = await t.EnemyTurn(mob, "PRESSURE");
    t.Proof(pressure.PlayerHpLost == 5 && t.PowerAmount<WeakPower>(t.Me) == 2,
        $"attack+debuff expected=5/2 observed={pressure.PlayerHpLost}/{t.PowerAmount<WeakPower>(t.Me)}");

    var multi = t.NextMove(mob).Intents.OfType<MultiAttackIntent>().SingleOrDefault();
    t.Proof(multi?.Repeats == 2, $"FLURRY repeats expected=2 observed={multi?.Repeats}");
    var flurry = await t.EnemyTurn(mob, "FLURRY");
    t.Proof(flurry.Hits == 2 && flurry.PlayerHpLost == 8,
        $"multi-attack expected=2/8 observed={flurry.Hits}/{flurry.PlayerHpLost}");

    // At full health the branch must choose GUARD.
    int blockBefore = mob.Block;
    await t.EnemyTurn(mob, "GUARD");
    t.Proof(mob.Block - blockBefore == 5, $"healthy branch block expected=+5 observed={mob.Block - blockBefore}");

    // Change the branch's real input through a public Cmd, without forcing a move state.
    // t.Do runs it on every multiplayer peer (selftest-harness.md § Multiplayer Tier 2).
    int woundedHp = Math.Max(1, mob.MaxHp / 2 - 1);
    await t.Do(owner => CreatureCmd.Damage(new ThrowingPlayerChoiceContext(), mob, mob.CurrentHp - woundedHp,
        ValueProp.Unblockable | ValueProp.Unpowered, owner.Creature, null), "wound for branch");
    t.Proof(mob.CurrentHp == woundedHp, $"branch setup hp expected={woundedHp} observed={mob.CurrentHp}");

    // Traverse the cycle again. The stacked buff must change later attack damage.
    await t.EnemyTurn(mob, "MUSTER");
    t.Proof(t.PowerAmount<<CustomBuff>>(mob) == 4,
        $"stacked self power expected=4 observed={t.PowerAmount<<CustomBuff>>(mob)}");
    pressure = await t.EnemyTurn(mob, "PRESSURE");
    t.Proof(pressure.PlayerHpLost == 7 && t.PowerAmount<WeakPower>(t.Me) == 2,
        $"buffed attack+debuff expected=7/2 observed={pressure.PlayerHpLost}/{t.PowerAmount<WeakPower>(t.Me)}");
    flurry = await t.EnemyTurn(mob, "FLURRY");
    t.Proof(flurry.Hits == 2 && flurry.PlayerHpLost == 12,
        $"buffed multi-attack expected=2/12 observed={flurry.Hits}/{flurry.PlayerHpLost}");

    int hpBeforeRecover = mob.CurrentHp;
    blockBefore = mob.Block;
    await t.EnemyTurn(mob, "RECOVER");
    t.Proof(mob.CurrentHp - hpBeforeRecover == 3 && mob.Block - blockBefore == 4,
        $"wounded branch heal+block expected=3/4 observed={mob.CurrentHp - hpBeforeRecover}/{mob.Block - blockBefore}");
}, budgetSeconds: 120);
```

That scenario needs `MegaCrit.Sts2.Core.MonsterMoves.Intents`, `MegaCrit.Sts2.Core.Models.Powers`,
`MegaCrit.Sts2.Core.GameActions.Multiplayer`, and `MegaCrit.Sts2.Core.ValueProps`. Adapt move
ids, numbers, Power types, and branch setup to SPEC. A move that hangs the enemy turn (usually a
`.Targeting(target)` attack) fails with `selftest FAILED: player play phase not resumed after
enemy turn`.

Exercise selected deterministic/conditional states and selected random outcomes; do not create a
retained proof project per authorable shape.

## Proof matrix

- **Assert the spawned roster and HP.** Assert the enemy count, ordered identities, and
  repetitions match `actual_roster`, and each Monster's current HP lies in its declared range,
  as their own state proofs.
- Assert every advertised move id executes in the declared order (`NextMove.Id` before, the
  performed-move history after), and traverse the cycle far enough to prove it loops.
- Drive every branch through each outcome by changing the real condition.
- Assert each move's concrete consequence: Power amount plus a later changed attack for a self
  buff; player Power amount for a debuff; Block/HP deltas from a wounded pre-state; hit-result
  count for a multi-attack; every effect of a composite move. One HP delta is not enough for a
  multi-move enemy.
- **Hook participation: assert the neutral case outside the guard.** No move performs a passive
  rule. Assert the modified value through a real attack, then drive one event the guard ignores
  (an attack on another creature, or an excluded damage kind) and assert it unchanged.
- In a headed pass, confirm the bestiary move list shows the shipped titles, and the static body
  is aligned and uncropped in combat and bestiary.

## Manual fallback (only when the harness cannot reach its scenario)

Grant it: `fight <PREFIX>-<ENCOUNTER_SLUG>` enters the custom Encounter (run in progress); confirm
the custom Monster spawned before ending the turn. Trigger it: end enough turns to traverse the
selected graph, confirming every selected move's visible intent and exact HP/Block/Power change,
and drive each selected conditional or random outcome without treating one sample as
distribution proof.
