# Bounded Forced Follow-up Event

Use this contract when carrying a custom Quest Card should force one finite custom Event
sequence during a declared set of acts, in the style of a delayed story follow-up. One Mod
may declare a bounded ordered mapping list. It is a public-hook pattern; it does not require
Harmony, a vanilla-content edit, or a custom map node.


## Supported boundary

- single-player runs only;
- zero or more mapping records, each owned by one custom Quest Card token;
- one nonempty duplicate-free set of exact `IRunState.CurrentActIndex` values per mapping;
- one globally unique integer priority and `fail_closed` conflict policy per mapping;
- while a matching token is in its owner's deck, entering an Unknown MapPoint in a selected
  act forces its room roll to `RoomType.Event` and replaces the next Event pull with the
  mapping's current sequence Event;
- every sequence Event is custom, unique inside that sequence, finite, and excluded from
  ordinary random Event pools;
- the token stores a bounded saved sequence index; exactly the declared successful terminal
  option advances it or completes/removes the token, restoring normal selection.

This does not support arbitrary Event graphs, loops, repeated sequence ids, vanilla
Events/cards, multiplayer ownership, duplicate-token reward semantics, fixed-node ordering
guarantees, save-roundtrip claims, or deterministic composition with another Mod that
rewrites the same hooks. A generated source grants at most one instance of each token. If
zero or multiple instances, an invalid index, or an external forced target conflicts, the
mapping fails closed instead of choosing or repairing silently.

`on_target_success` is valid only for a one-Event sequence and consumes at that Event.
`on_sequence_complete` consumes only at the final sequence Event. No other option advances
or consumes the token. The final completion path removes every matching token defensively
so the forcing hooks cannot remain active after a violated duplicate invariant.

The Quest Card's acquisition preview is not implicit in this contract. If the same option
should show native acquisition presentation, compose the exact add-result contract from
`event-native-presentation.md`. Adding it to the deck is a semantic outcome; the preview
must reuse that same successful add result and must not grant a second Card.

## Why this works

STS2 0.107.1 exposes the complete runtime chain through public model hooks:

1. `UnknownMapPointOdds.Roll` calls `Hook.ModifyUnknownMapPointRoomTypes` before choosing
   the Unknown room type.
2. `Act.PullNextEvent` calls `Hook.ModifyNextEvent` after an Event is selected.
3. Cards in the run participate in those hooks through their model overrides.

Vanilla `LanternKey` uses both overrides in act index `2`. The unavailable vanilla
`WarHistorianRepy` model returns false from `IsAllowed`; the custom target uses the same
pool-exclusion principle while the Quest Card hook selects it explicitly.

## Mapping and priority

At each hook call, collect mappings whose exact token condition, owner, act set, and saved
index are valid. No match returns the hook input unchanged. More than one match is resolved
only by the declared globally unique priority order. Before replacement, fail closed if the
incoming Event is already one of this Mod's forced sequence Events other than the selected
mapping's current target; this preserves a prior listener's choice rather than composing an
unreviewed cross-Mod chain. Never mutate the input room set or cache a mutable Event.

The two hooks repeat the same pure selection helper. `ModifyUnknownMapPointRoomTypes`
returns a new `{ RoomType.Event }` set only when exactly one ordered selection succeeds;
`ModifyNextEvent` returns the canonical current sequence Event for that same selection.

## Quest Card token

The token is registered like any custom Card but is not a normal playable Card:

```csharp
using System.Collections.Generic;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.CardPools;
using MegaCrit.Sts2.Core.Rooms;
using STS2RitsuLib.Scaffolding.Content;

public sealed class <QuestToken> : ModCardTemplate
{
    private static readonly int[] TargetActIndices = [<zero-based act indices>];
    private static readonly ModelId[] Sequence = [<ordered custom Event ids>];
    private static readonly SavedAttachedState<<QuestToken>, int> ProgressState =
        new($"{MainFile.ModId}_forced_event_progress", () => 0);

    public <QuestToken>()
        : base(-1, CardType.Quest, CardRarity.Quest, TargetType.Self) { }

    public override int MaxUpgradeLevel => 0;

    public override IEnumerable<CardKeyword> CanonicalKeywords =>
        new[] { CardKeyword.Unplayable };

    public override IReadOnlySet<RoomType> ModifyUnknownMapPointRoomTypes(
        IReadOnlySet<RoomType> roomTypes)
    {
        if (!ForcedEventMappings.Selects(this, TargetActIndices, ProgressState[this]))
            return roomTypes;

        return new HashSet<RoomType> { RoomType.Event };
    }

    public override EventModel ModifyNextEvent(EventModel currentEvent)
    {
        if (!ForcedEventMappings.Selects(this, TargetActIndices, ProgressState[this]))
            return currentEvent;

        return ModelDb.GetById<EventModel>(Sequence[ProgressState[this]]);
    }

    internal void AdvanceOrComplete(Player owner, ModelId completedEvent)
    {
        <assert owner, exact current event, bounds, and declared consumption>;
        <advance saved index or CompleteQuest plus remove all matching tokens>;
    }
}
```

Register the token exactly once through
`.Card<ColorlessCardPool, <QuestToken>>()`; do not add a pool attribute or a second
registration path.

Return the original hook input unchanged outside the mapping's acts and whenever selection
fails closed. Do not cache `Owner`, run state, or a mutable Event. Resolve the canonical
current target from its registered `ModelId` on every replacement. The saved index is
bounded to `0..sequence.Count-1` and belongs to the concrete token instance.

If a supported Event option grants the token, create it from that option's mutable owner
and add it to the real deck through the existing outcome vocabulary:

```csharp
var owner = Owner ?? throw new InvalidOperationException("Event has no owner");
if (!owner.Deck.Cards.OfType<<QuestToken>>().Any())
{
    var token = owner.RunState.CreateCard<<QuestToken>>(owner);
    await CardPileCmd.Add(token, PileType.Deck);
}
```

The duplicate guard is part of the bounded generated shape. Do not use `skipVisuals: true`
in gameplay code; that flag is acceptable only in the verification setup, where Card
acquisition presentation is deliberately not under test.

## Forced sequence Events

Author every sequence Event with the normal Event recipe, plus these exclusions and
completion rules:

The target file needs `System`, `System.Linq`, `System.Threading.Tasks`,
`MegaCrit.Sts2.Core.Commands`, `MegaCrit.Sts2.Core.Runs`,
`STS2RitsuLib.Scaffolding.Content`, and the Quest Card namespace in addition to the normal
Event recipe imports.

```csharp
using MegaCrit.Sts2.Core.Runs;
using STS2RitsuLib.Scaffolding.Content;

public sealed class <TargetEvent> : ModEventTemplate
{
    public override bool IsShared => true;

    // The Quest Card hook is the only supported route into this Event.
    public override bool IsAllowed(IRunState runState) => false;

    private async Task <CompletionOption>()
    {
        var owner = Owner ?? throw new InvalidOperationException("Event has no owner");
        var tokens = owner.Deck.Cards.OfType<<QuestToken>>().ToList();
        if (tokens.Count != 1)
            throw new InvalidOperationException(
                "Forced Event requires exactly one matching quest token");

        tokens[0].AdvanceOrComplete(owner, Id);

        SetEventFinished(PageDescription("<RESULT_KEY_OR_NEXT_STEP_KEY>"));
    }
}
```

`IsAllowed(...) => false` is intentional: natural Event selection must never surface a
sequence Event before the token condition. Register every canonical model exactly once with
`.SharedEvent<T>()`, but do not add ordinary eligibility, patch the Event pool, or return a
mutable Event instance from `ModifyNextEvent`.

## Verification contract

Future generated Mods verify only their selected mapping and sequence, in one `MapNode` run
when the scenario is reachable. Do not create one proof matrix per mapping family:

1. after the normal run/map startup gate, call both `Hook` aggregators without the token
   and require the original room set and Event object;
2. create one token through the run and add it to `PileType.Deck` with
   `skipVisuals: true` as proof setup only;
3. call both hooks in the wrong act and require unchanged inputs;
4. enter one selected act, then require `{ RoomType.Event }` and the canonical current
   sequence Event; where two mappings can match, assert the declared priority winner;
5. enter one real Unknown MapPoint with `EnterMapPointInternal`, wait for that `EventRoom`,
   and capture the settled headed state;
6. click the exact successful option and assert index advance or terminal token count
   `1 -> 0`; at terminal, call both hooks again to prove normal selection is restored;
7. emit one structured marker containing all guards, then `selftest done`.

Use the standard startup gate from `reference/selftest-harness.md` before
`EnterMapPointInternal`; `RunManager.IsInProgress` alone races the initial map/room setup.
The proof must enter through `MapPointType.Unknown`, not debug-enter the target canonical
Event directly, because the room-type and Event-replacement hooks are the behavior under
test.

A passing run reports a structured line of this shape:

```text
forcedFollowUp noToken=True wrongAct=True roomForced=True eventForced=True entered=true seals=1->0 restored=True
selftest done
```
