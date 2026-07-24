# Stateful mechanics - counters, phases, and persistence

Status: **RitsuLib pipeline-supported on STS2 0.107.1** for custom-relic run cadence
with `int`/`bool` attached state and combat-local cadence based on the native turn number.
`RitsuStateProof` passed the two-combat hosted proof on 2026-07-23 with RitsuLib 0.4.62.

Use this page whenever an effect remembers progress, limits uses, compares turns, or
changes behavior after a prior event. State is part of the mechanic, not an implementation
detail.

## Semantic contract

SPEC must record all of these fields:

1. **event** - the exact hook that advances or reads state;
2. **threshold/phase** - whether the effect checks before or after increment/reset;
3. **lifetime** - `turn`, `combat`, or `run`;
4. **reset** - the exact boundary and value;
5. **persistence** - runtime-only field, `AttachedState`, or `SavedAttachedState`;
6. **owner** - which player/side/card may advance it;
7. **UI meaning** - progress, current turn, uses remaining, or hidden;
8. **proof** - below-threshold, threshold, lifetime boundary, and save round trip when run-persistent.

Do not infer lifetime from the easiest C# field. Ask whether progress continues into the
next fight when the request does not settle that choice.

| Wording | Source of truth | Reset/persistence | Vanilla shape |
|---|---|---|---|
| Every N events across combats | `SavedAttachedState<SpecificRelic, int>` | never clear at combat end; normal run save restores it | Happy Flower, Nunchaku, Pen Nib |
| Limited uses in this run | `SavedAttachedState<SpecificRelic, int/bool>` | mutate at the real use site; save with the relic model | Winged Boots, Girya |
| On turn N / every N turns this combat | `PlayerCombatState.TurnNumber` | native combat state starts at turn 1 | Stone Calendar |
| Every N cards this turn | ordinary field | reset at the owner's turn boundary | turn-local counter |
| Once per combat | ordinary field | reset on combat entry only | combat-local flag |

"Every 3 turns" and "on turn 3" are not synonyms. The former defaults to a run cadence
that can continue `1, 2, trigger` across fights. The latter reads the current combat's turn
number and restarts in every fight.

Always scope side/card events to the owner. For a side hook, require
`participants.Contains(Owner.Creature)`; for a card hook, require
`cardPlay.Card.Owner == Owner`.

## Relic-owned run state

Use RitsuLib's public `SavedAttachedState<TKey,TValue>` when the saved value belongs to a
specific relic instance. Keep the handle in a `private static readonly` field so RitsuLib's
type discovery initializes it during Mod loading. Include the Mod id in the supplied name;
RitsuLib also prefixes the concrete key type, and rejects duplicate saved names.

```csharp
using STS2RitsuLib.Utils;

private const int Threshold = 3;

private static readonly SavedAttachedState<MyRelic, int> ProgressState =
    new($"{MainFile.ModId}_progress", () => 0);

public int Progress => ProgressState[this];

private void SetProgress(int value)
{
    AssertMutable();
    ProgressState[this] = value;
    InvokeDisplayAmountChanged();
}

public override bool ShowCounter => true;
public override int DisplayAmount => Progress;

public override async Task AfterSideTurnStart(
    CombatSide side,
    IReadOnlyList<Creature> participants,
    ICombatState combatState)
{
    if (!participants.Contains(Owner.Creature)) return;

    SetProgress((Progress + 1) % Threshold);
    Status = Progress == Threshold - 1
        ? RelicStatus.Active
        : RelicStatus.Normal;
    if (Progress != 0) return;

    Status = RelicStatus.Normal;
    Flash();
    await PlayerCmd.GainEnergy(1m, Owner); // replace with the SPEC effect
}

public override Task AfterCombatEnd(CombatRoom room)
{
    Status = RelicStatus.Normal; // UI only; do not clear Progress
    return Task.CompletedTask;
}
```

For a run-persistent bool, use a second typed handle and the same mutation discipline:

```csharp
private static readonly SavedAttachedState<MyRelic, bool> UsedState =
    new($"{MainFile.ModId}_used", () => false);

public bool Used => UsedState[this];
```

Do not use a plain instance/static field for run lifetime. It can appear to cross combats
in one process but loses state on save/resume. Do not clear attached run state in
`AfterCombatEnd` or `AfterRoomEntered`.

Do not put relic-owned cadence in `RunSavedDataStore`. That store is for data whose natural
owner is the run or player rather than an already serialized model instance. The narrower
attached-state route keeps ownership, cloning, and `SavedProperties` behavior aligned.

## Combat-local cadence

For "on turn N" or "every N turns in each combat", read the game's own turn number. Never
maintain a second counter.

```csharp
private const int TriggerTurn = 3;

public override async Task BeforeSideTurnEnd(
    PlayerChoiceContext choiceContext,
    CombatSide side,
    IEnumerable<Creature> participants)
{
    if (!participants.Contains(Owner.Creature) ||
        Owner.PlayerCombatState!.TurnNumber != TriggerTurn)
        return;

    Flash();
    await CreatureCmd.Damage(
        choiceContext,
        Owner.Creature.CombatState!.HittableEnemies,
        5m,
        ValueProp.Unpowered,
        Owner.Creature); // replace with the SPEC effect
}
```

For periodic combat timing, use `TurnNumber % N == 0`. For a start-of-turn effect, keep
the same source of truth and move the check to `AfterSideTurnStart`. Combat-local state
does not use saved attached state.

## Other bounded shapes

**Every N cards this turn:** use an ordinary `int`; reset it in the owner's
`BeforeSideTurnStart`, increment in `AfterCardPlayed`, and trigger on `count % N == 0`.
Add a separate turn-local fired flag only when the design says "the first N".

**Once per combat:** use an ordinary `bool`; reset only when entering a `CombatRoom`, then
guard/set it at the real trigger. Do not reset on every room or every turn.

**Previous-turn memory:** use ordinary `current` and `previous` fields. At the owner's turn
start, assign `previous = current`, then `current = 0`; clear both at combat end unless the
SPEC explicitly chooses run lifetime.

**Limited run uses:** attach an `int` or `bool` to the concrete relic, mutate it at the real
use site, and derive remaining uses/`IsUsedUp` from that saved value. UI usually shows
`limit - used`, not raw uses consumed.

## Save boundary

RitsuLib bridges `SavedAttachedState` through the model's normal `SavedProperties`
serialization. Supported RitsuLib values include `int`, `bool`, `string`, `ModelId`,
integer/enum arrays, and the vanilla serializable Card shapes. The active open-mod
pipeline deliberately supports only concrete custom-relic `int`/`bool` state.

Not supported by this page:

- profile/meta progression beyond the end of a run;
- saved state attached to potions, powers, or arbitrary non-model owners;
- arbitrary objects, dictionaries, floating-point values, or custom collections;
- wall-clock timers;
- run-persistent Character resources or multiplayer rejoin claims.

## UI rules

- Override `ShowCounter` only when a visible count helps the player understand timing.
- `DisplayAmount` must retain one meaning: progress, current turn, or uses remaining.
- A mutation that changes visible state calls `AssertMutable()` and
  `InvokeDisplayAmountChanged()` after updating the attached value.
- `RelicStatus.Active` is feedback, not persistence. Resetting Status must never reset run
  progress.

## Required Tier 2 proof

One trigger is not enough. Assert:

1. **below threshold:** exact progress at `N - 1` and no effect;
2. **threshold:** one exact effect and the specified wrap/consume state;
3. **lifetime:** a second combat proves carry-over or native reset;
4. **persistence:** `SavedProperties.From(liveRelic)`, `Fill` a fresh mutable instance, and
   assert the restored attached value.

The serialization round trip and two-combat hosted proof are independent requirements.
`RitsuStateProof` observed progress `0 -> 1 -> 2` and `used=false -> true`,
`SavedProperties.From/Fill` restoring `2/true`, a distinct second `PlayerCombatState`,
second-combat progress `2 -> 0` with exactly one Energy gain `3 -> 4` while the bool
one-shot stayed used, and the native combat-local turn/block boundary
`turn 2 / Block 3 -> turn 1 / Block 0`. It reached `selftest done`, strict Tier 2, and no
fresh error with only the declared RitsuLib runtime dependency.
