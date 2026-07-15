# Reference: stateful mechanics and counter lifetimes

Use this page when an effect remembers progress: "every 3 turns", "the third card
this turn", "once each combat", "if last turn...", or "3 uses this run". A counter
is not a new content type. It is state owned by the real card/relic/power and advanced
from that element's normal hook.

The design contract has six parts. Do not author code until all six are explicit:

1. **event** -- the exact owned event that advances state (owner's turn start, an
   Attack played by the owner, a room entered, and so on);
2. **threshold and phase** -- `N`, plus whether the event advances state before the
   threshold check or consumes/reset state after it;
3. **lifetime** -- `turn`, `combat`, or `run`;
4. **reset** -- the exact lifecycle boundary that resets it;
5. **persistence** -- ordinary mutable field or `[SavedProperty]`;
6. **proof** -- below threshold, at threshold, and the relevant reset/carry-over and
   save round trip.

**Current support boundary:** custom-relic run cadence with `[SavedProperty] int/bool`
and custom-relic combat turn cadence with `PlayerCombatState.TurnNumber` are
pipeline-supported and live-proven. The turn-local, once-per-combat, previous-turn, and
limited-run-use patterns below are grounded/copyable but remain provisional until their
own scenario canaries. Card/Enchantment/Modifier holders and every advanced-save case are
not promoted by the relic canary; see the maintainer audit for the exact ladder.

## Choose the lifetime first

| User meaning | Source of truth | Reset/persistence | Vanilla analog |
|---|---|---|---|
| Every Nth event **this turn** | ordinary `int` field | reset at the owner's `BeforeSideTurnStart` | `OrnamentalFan`, `LetterOpener` |
| On turn N, or every N turns, **of each combat** | `Owner.PlayerCombatState!.TurnNumber` when possible | combat owns/reset its turn number; do not duplicate it | `StoneCalendar` |
| Once per combat / N events this combat | ordinary `bool`/`int` field | reset when entering a `CombatRoom` | `Permafrost` |
| What happened last turn | current + previous ordinary fields | shift current into previous, then clear current at owner's turn start | `Pocketwatch` |
| Every N events **across combats in this run** | `[SavedProperty]` `int` property | never reset at combat end; run save/load restores it | `HappyFlower`, `Nunchaku`, `PenNib`, `TuningFork` |
| N total uses in this run | `[SavedProperty]` `int`/`bool` property | never reset in combat; optionally expose `IsUsedUp` | `WingedBoots`, `Girya` |

"Every 3 turns" and "on turn 3" are not synonyms. The former normally means a
Happy Flower-style run cadence (`1, 2, trigger; next combat continues`). The latter
means a Stone Calendar-style combat turn (`TurnNumber == 3`; every new combat begins
at turn 1). If the user's wording does not settle carry-over, ask one plain question:
"Should progress continue into the next fight, or restart each fight?" Offer the
Happy Flower-style carry-over as the default for "every N turns".

Always scope side/card events to the owner. For a side hook, require
`participants.Contains(Owner.Creature)`; for a card hook, require
`cardPlay.Card.Owner == Owner`. Otherwise multiplayer or enemy turns advance the counter.

## Run-persistent periodic counter (Happy Flower shape)

This is the known-good shape for "every N owner turns across combats". It increments
first, wraps with modulo, and triggers on zero. The public property is intentional:
the run serializer and the self-test can inspect it.

```csharp
using MegaCrit.Sts2.Core.Saves.Runs;   // SavedProperty

private const int Threshold = 3;
private int _progress;

[SavedProperty]
public int Progress
{
    get => _progress;
    private set
    {
        AssertMutable();
        _progress = value;
        InvokeDisplayAmountChanged();
    }
}

public override bool ShowCounter => true;
public override int DisplayAmount => Progress;

public override async Task AfterSideTurnStart(CombatSide side,
    IReadOnlyList<Creature> participants, ICombatState combatState)
{
    if (!participants.Contains(Owner.Creature))
        return;

    Progress = (Progress + 1) % Threshold;
    Status = Progress == Threshold - 1 ? RelicStatus.Active : RelicStatus.Normal;
    if (Progress != 0)
        return;

    Status = RelicStatus.Normal;
    Flash();
    await PlayerCmd.GainEnergy(1m, Owner);   // replace with the SPEC effect
}

public override Task AfterCombatEnd(CombatRoom room)
{
    Status = RelicStatus.Normal;             // UI only; DO NOT clear Progress
    return Task.CompletedTask;
}
```

Do not use a plain field for run lifetime. It appears to cross combats in one process
but silently loses progress when the user saves and resumes. Do not reset the saved
property in `AfterCombatEnd` or `AfterRoomEntered`.

## Combat-local turn cadence (Stone Calendar shape)

For "on turn N of each combat", read the game's own combat turn number instead of
maintaining a second counter. This naturally starts at 1 in every combat and cannot leak
into the next fight.

```csharp
private const int TriggerTurn = 3;

public override bool ShowCounter => CombatManager.Instance.IsInProgress && !IsCanonical;
public override int DisplayAmount => ShowCounter
    ? Owner.PlayerCombatState!.TurnNumber
    : -1;

public override async Task BeforeSideTurnEnd(PlayerChoiceContext choiceContext,
    CombatSide side, IEnumerable<Creature> participants)
{
    if (!participants.Contains(Owner.Creature) ||
        Owner.PlayerCombatState!.TurnNumber != TriggerTurn)
        return;

    Flash();
    await CreatureCmd.Damage(choiceContext,
        Owner.Creature.CombatState!.HittableEnemies,
        5m, ValueProp.Unpowered, Owner.Creature);   // replace with the SPEC effect
}

public override Task AfterSideTurnStart(CombatSide side,
    IReadOnlyList<Creature> participants, ICombatState combatState)
{
    if (participants.Contains(Owner.Creature))
        InvokeDisplayAmountChanged();
    return Task.CompletedTask;
}
```

For "every N turns in each combat", use `TurnNumber % N == 0`. For an effect at the
start rather than end of the turn, keep the same source of truth but move the equality/
modulo check to `AfterSideTurnStart`. No `[SavedProperty]` belongs on combat-local state.

## Other recurring state shapes

**Every N cards this turn:** ordinary `int`; reset it in the owner's
`BeforeSideTurnStart`, increment in `AfterCardPlayed`, trigger when
`count % N == 0`. This can trigger more than once in an unusually long turn. If the
design says "only the first N", add a separate turn-local fired flag.

**Once per combat:** ordinary `bool`; reset only when `AfterRoomEntered(AbstractRoom
room)` receives a `CombatRoom`, then guard/set it in the real trigger hook. Do not reset
on every room or every turn.

**Previous-turn memory:** use ordinary `current` and `previous` fields. At the owner's
`BeforeSideTurnStart`, assign `previous = current`, then `current = 0`; read `previous`
for this turn's effect. Clear both in `AfterCombatEnd` unless the design explicitly says
the memory crosses combats.

**Limited run uses:** `[SavedProperty] public int TimesUsed`; increment at the real use
site and derive remaining uses/`IsUsedUp` from it. A remaining-use counter in the UI is
usually `limit - TimesUsed`, not the raw used count.

## Save support boundary

BaseLib 3.3.x scans mod types during post-mod initialization. If a supported custom
holder declares a valid `[SavedProperty]`, BaseLib injects that type into
`SavedPropertiesTypeCache`, so custom relic state participates in normal run saves.

Base-game `[SavedProperty]` supports `int`, `bool`, `string`, `ModelId`, `int[]`, enums/
enum arrays, `SerializableCard`, `SerializableCard[]`, and `List<SerializableCard>`.
Supported holder families are `RelicModel`, `CardModel`, `EnchantmentModel`, and
`ModifierModel`. For this pipeline, run counters use the smallest fitting `int`/`bool`.

The following are **not pipeline-supported** by this page:

- profile/meta progression that survives the end of a run;
- `[SavedProperty]` on potions/powers or arbitrary holder classes;
- arbitrary objects, dictionaries, floating-point state, or custom collections;
- wall-clock/real-time timers.

BaseLib has advanced `SavedSpireField`/extended-save seams, but they need their own
grounding and canary before the pipeline may advertise them. Do not quietly substitute
one when `[SavedProperty]` warns that a type or holder is unsupported.

## UI counter rules

- Override `ShowCounter` only when a visible counter helps the player understand timing.
- `DisplayAmount` should show the same semantic the description implies: progress so far,
  current combat turn, or uses remaining. Do not switch meanings between combats.
- Every mutable setter that changes the shown value calls `AssertMutable()` and
  `InvokeDisplayAmountChanged()`.
- `RelicStatus.Active` is anticipation/feedback, not state. Resetting `Status` must never
  reset a run-persistent counter.

## Required Tier-2 proof

One successful trigger is insufficient for a stateful effect. The self-test must assert:

1. **below threshold:** the effect has not fired at `N - 1` and progress is exact;
2. **at threshold:** it fires once with the exact state delta and wraps/consumes as SPEC says;
3. **lifetime boundary:** turn/combat state resets, or run state carries into a second combat;
4. **run persistence:** for `[SavedProperty]`, call `SavedProperties.From(liveRelic)`, fill
   a fresh mutable instance, and assert the restored property before claiming save support.

`SavedProperties.From`/`Fill` are explicitly exposed for internal/tests. This round trip
does not replace the two-combat hosted proof: one verifies serialization, the other verifies
the gameplay lifecycle. See `reference/selftest-harness.md` for the cadence driver.
