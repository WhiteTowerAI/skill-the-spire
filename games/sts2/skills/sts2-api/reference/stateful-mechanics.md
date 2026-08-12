# Stateful mechanics - counters, phases, and persistence

Status: **authorable with RitsuLib on STS2 0.107.1**. The historical hosted proof observed
custom-Relic run cadence with saved `int`/`bool` state and native combat turn timing.
M8.7 generalizes the source contract to the bounded scalar/transition shapes below; newly
admitted owner, schema, and consumer combinations remain game-unobserved.

Use this page whenever an effect remembers progress, limits uses, compares turns, or
changes behavior after a prior event. State is part of the mechanic, not an implementation
detail.

<!-- open-mod-surface-contract/v1
{
  "family": "bounded_state",
  "owner": "reference/stateful-mechanics.md",
  "spec_key": "bounded_state",
  "profile": {"sts2": "0.107.1", "ritsulib_compat": "0.5.4"},
  "fields": {
    "states": {"type": "list<object>", "cardinality": "0..*", "default": []},
    "states[].id": {"type": "text", "cardinality": "1", "unique": true},
    "states[].owner.surface/id": {"type": "enum/text", "cardinality": "1 each"},
    "states[].schema": {"type": "list<object>", "cardinality": "1..*"},
    "states[].schema[].name/type/initial": {"type": "text/enum/typed scalar", "cardinality": "1 each"},
    "states[].schema[].min/max": {"type": "finite number", "cardinality": "1 each for numeric"},
    "states[].schema[].max_length": {"type": "positive integer", "cardinality": "1 for string"},
    "states[].lifetime/persistence": {"type": "enum", "cardinality": "1 each"},
    "states[].reset/visibility": {"type": "text", "cardinality": "1 each"},
    "states[].transitions": {"type": "list<object>", "cardinality": "1..*"},
    "states[].transitions[].id": {"type": "text", "cardinality": "1", "unique": true},
    "states[].transitions[].listener.surface/id": {"type": "enum/text", "cardinality": "1 each"},
    "states[].transitions[].hook": {"type": "enum", "cardinality": "1"},
    "states[].transitions[].updates": {"type": "list<declared field name>", "cardinality": "1..*"},
    "states[].transitions[].route": {"type": "declared route", "cardinality": "1"},
    "states[].consumers": {"type": "list<object>", "cardinality": "0..*", "default": []},
    "states[].consumers[].id/route": {"type": "text/route", "cardinality": "1 each"},
    "states[].outputs": {"type": "list<object>", "cardinality": "0..*", "default": []},
    "states[].outputs[].consumer/route": {"type": "declared consumer id/route", "cardinality": "1 each"}
  },
  "enums": {
    "owner_surface": ["card", "relic", "potion", "power", "orb", "enchantment", "monster", "character", "combat"],
    "transition_surface": ["card", "relic", "potion", "power", "orb", "enchantment", "monster", "character", "combat", "event"],
    "saved_type": ["bool", "int", "decimal", "string"],
    "run_saved_type": ["bool", "int", "string"],
    "run_saved_owner_surface": ["card", "relic", "enchantment"],
    "lifetime": ["turn", "combat", "run"],
    "persistence": ["none", "combat_snapshot", "run_save"],
    "transition_hook": [
      "before_owner_turn_start",
      "after_owner_turn_start",
      "after_owner_card_played",
      "after_combat_entered",
      "after_combat_end",
      "on_owner_card_play",
      "on_event_option_success",
      "on_rest_site_success",
      "on_monster_move_transition",
      "on_secondary_resource_changed"
    ],
    "hook_listener_surfaces": {
      "on_owner_card_play": ["card"],
      "on_event_option_success": ["event"],
      "on_rest_site_success": ["card", "relic"],
      "on_monster_move_transition": ["monster"],
      "on_secondary_resource_changed": ["card", "character", "combat"]
    }
  },
  "conditions": [
    "numeric fields have finite ordered bounds",
    "run_save requires run lifetime, a Card/Relic/Enchantment SavedProperties owner, and bool/int/string fields",
    "every transition updates only declared fields and has an exact listener plus allowlisted hook",
    "specialized hooks use only their declared listener surfaces",
    "every output names a declared grounded consumer"
  ],
  "mutually_exclusive": ["run_save with a non-SavedProperties owner or field"],
  "routes": [
    "reference/stateful-mechanics.md#semantic-contract",
    "reference/stateful-mechanics.md#other-bounded-shapes"
  ],
  "hard_boundaries": [
    "no arbitrary executable state machine from user text",
    "no retained physical played-Card instances or ungrounded custom zones",
    "every visible mutation has one refresh route"
  ],
  "generated_obligations": [
    "bind state to the exact owner and clone lifecycle",
    "use AttachedState or SavedAttachedState according to persistence",
    "lower only declared transitions consumers and outputs"
  ],
  "evidence": {"framework_expressible": true, "open_mod_authorable": true, "game_observed": false},
  "legacy": "v1/v2 cadence and ordered-buffer profiles resume unchanged; revised state writes v3"
}
-->

## Semantic contract

Each state declaration is data, not prompt-authored executable code. SPEC records all of
these fields:

1. **owner** - the exact instance whose clone/lifetime owns the state;
2. **schema** - one or more unique `bool`, bounded `int`/`decimal`, or length-bounded
   `string` fields with typed initial values;
3. **transition** - stable id, exact listener surface/id, allowlisted hook, updated field
   names, guard/order rule, and grounded route;
4. **consumer/output** - every reader or visible output and its route;
5. **event phase** - whether each consumer checks before or after a transition;
6. **lifetime** - `turn`, `combat`, or `run`;
7. **reset** - the exact boundary and value;
8. **persistence** - runtime-only, explicit combat snapshot, or normal run save;
9. **visibility** - hidden or one bounded existing consumer plus its refresh route.

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

The state owner and transition listener need not be the same surface: a Card may append a
semantic value to combat-owned state. They must be named independently. Always scope
side/Card events to the declared listener and state owner. For a side hook, require
`participants.Contains(Owner.Creature)`; for a Card hook, require
`cardPlay.Card.Owner == Owner`.

## Structural lowering

- **turn lifetime:** use an ordinary bounded field on the declared model/listener and reset
  it at the exact owner turn boundary;
- **combat lifetime on a model:** use an ordinary bounded field and reset only on combat
  entry/end as declared;
- **combat-owned shared state:** use `AttachedState<PlayerCombatState,TState>`; never a
  static dictionary or a retained physical Card list;
- **run lifetime:** use `SavedAttachedState<SpecificCard|SpecificRelic|SpecificEnchantment,T>`
  with `bool`, `int`, or `string`. The owner must already travel through its normal
  `SavedProperties` serialization. Do not infer this path for Potion, Power, Orb, Monster,
  Character, or combat owners;
- **visible output:** refresh exactly one selected existing consumer after every mutation.

Lower only the allowlisted transition hooks in the owner contract. A request needing an
arbitrary graph, timer, delegate, custom collection, or hook outside this vocabulary is a
missing capability and blocks under INV-9.

## Saved model-owned run state

Use RitsuLib's public `SavedAttachedState<TKey,TValue>` when the saved value belongs to a
specific Card, Relic, or Enchantment instance that follows the normal run serialization
path. Keep the handle in a `private static readonly` field so RitsuLib's
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

Do not put model-owned state in `RunSavedDataStore`. That store is for data whose natural
owner is the run or player and is not a prompt-selected fallback for a missing owner route.
The attached-state route keeps ownership, cloning, and `SavedProperties` behavior aligned.

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

**Limited run uses:** attach an `int` or `bool` to the concrete Card/Relic/Enchantment,
mutate it at the real use site, and derive remaining uses/`IsUsedUp` from that saved value. UI usually shows
`limit - used`, not raw uses consumed.

## Save boundary

RitsuLib bridges `SavedAttachedState` through the model's normal `SavedProperties`
serialization. Although RitsuLib accepts additional values, the v3 bounded-state family
admits only `bool`, `int`, and length-bounded `string` for run saves. `decimal` is
runtime/combat-only. Card, Relic, and Enchantment are the pinned owner surfaces whose normal
serialization calls `SavedProperties.From`/`Fill`; do not infer a save path for another owner.

Not supported by this page:

- profile/meta progression beyond the end of a run;
- run-saved state attached to Potions, Powers, Orbs, Monsters, Characters, combat state, or
  arbitrary non-model owners;
- arbitrary objects, dictionaries, floating-point values, or custom collections;
- wall-clock timers;
- remote-player secondary-resource UI or multiplayer rejoin claims.

## UI rules

- Override `ShowCounter` only when a visible count helps the player understand timing.
- `DisplayAmount` must retain one meaning: progress, current turn, or uses remaining.
- A mutation that changes visible state calls `AssertMutable()` and
  `InvokeDisplayAmountChanged()` after updating the attached value.
- `RelicStatus.Active` is feedback, not persistence. Resetting Status must never reset run
  progress.

## Verification selected by a generated Mod

Derive an ordinary checklist only from the state declarations in current SPEC. For every
selected transition, drive the exact listener/guard and assert updated fields remain inside
bounds; also drive one neutral case outside the guard. Assert the declared reset/lifetime
boundary, each visible consumer refresh, and every selected output. Add a second combat only
for a combat boundary or cross-combat carry-over. Add `SavedProperties.From/Fill` only for a
run-save owner. A threshold profile additionally checks `N - 1`, trigger, and wrap/consume;
do not impose that matrix on an unrelated flag, phase, or previous-turn declaration.

The historical serialization round trip and two-combat hosted proof remain independent facts.
`RitsuStateProof` observed progress `0 -> 1 -> 2` and `used=false -> true`,
`SavedProperties.From/Fill` restoring `2/true`, a distinct second `PlayerCombatState`,
second-combat progress `2 -> 0` with exactly one Energy gain `3 -> 4` while the bool
one-shot stayed used, and the native combat-local turn/block boundary
`turn 2 / Block 3 -> turn 1 / Block 0`. It reached `selftest done`, strict Tier 2, and no
fresh error with only the declared RitsuLib runtime dependency.
