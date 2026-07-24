# Bounded Forced Follow-up Event

Use this contract when carrying one custom Quest Card should force one custom Event during
one specified act, in the style of a delayed story follow-up. It is a public-hook pattern;
it does not require Harmony, a vanilla-content edit, or a custom map node.

## Supported boundary

- single-player runs only;
- one custom Quest Card token and one custom target Event;
- one exact `IRunState.CurrentActIndex` selected in SPEC;
- while the token is in the deck, entering an Unknown MapPoint in that act forces its room
  roll to `RoomType.Event` and replaces the next Event pull with the target Event;
- the target Event is excluded from ordinary random Event pools;
- one named target option completes and removes the token, restoring normal room/Event
  selection.

This does not support arbitrary Event chains, vanilla Events/cards, multiple target acts,
multiplayer ownership, duplicate-token reward semantics, fixed-node ordering guarantees,
save-roundtrip claims, or deterministic composition with another mod that rewrites the
same hooks. A generated source should grant at most one token. The target completion path
removes every matching token defensively so the forcing hooks cannot remain active.

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
    public const int TargetActIndex = <zero-based act index>;

    public <QuestToken>()
        : base(-1, CardType.Quest, CardRarity.Quest, TargetType.Self) { }

    public override int MaxUpgradeLevel => 0;

    public override IEnumerable<CardKeyword> CanonicalKeywords =>
        new[] { CardKeyword.Unplayable };

    public override IReadOnlySet<RoomType> ModifyUnknownMapPointRoomTypes(
        IReadOnlySet<RoomType> roomTypes)
    {
        if (Owner?.RunState.CurrentActIndex != TargetActIndex)
            return roomTypes;

        return new HashSet<RoomType> { RoomType.Event };
    }

    public override EventModel ModifyNextEvent(EventModel currentEvent)
    {
        if (Owner?.RunState.CurrentActIndex != TargetActIndex)
            return currentEvent;

        return ModelDb.Event<<TargetEvent>>();
    }
}
```

Register the token exactly once through
`.Card<ColorlessCardPool, <QuestToken>>()`; do not add a pool attribute or a second
registration path.

Return the original hook input unchanged outside the target act. Do not cache `Owner`, the
run state, or the target mutable Event. The canonical target from `ModelDb.Event<T>()` is
the correct replacement value.

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

## Forced target Event

Author the target with the normal Event recipe, plus these exclusions and completion
rules:

The target file needs `System`, `System.Linq`, `System.Threading.Tasks`,
`MegaCrit.Sts2.Core.Commands`, `MegaCrit.Sts2.Core.Runs`,
`STS2RitsuLib.Scaffolding.Content`, and the Quest Card namespace in addition to the normal
Event recipe imports.

```csharp
public sealed class <TargetEvent> : ModEventTemplate
{
    public override bool IsShared => true;

    // The Quest Card hook is the only supported route into this Event.
    public override bool IsAllowed(IRunState runState) => false;

    private async Task <CompletionOption>()
    {
        var owner = Owner ?? throw new InvalidOperationException("Event has no owner");
        var tokens = owner.Deck.Cards.OfType<<QuestToken>>().ToList();
        if (tokens.Count == 0)
            throw new InvalidOperationException(
                "Forced Event entered without its quest token");

        foreach (var token in tokens)
            PlayerCmd.CompleteQuest(token);
        await CardPileCmd.RemoveFromDeck(tokens);

        SetEventFinished(PageDescription("<RESULT_KEY>"));
    }
}
```

`IsAllowed(...) => false` is intentional: natural Event selection must never surface the
target before the token condition. Register the canonical model once with
`.SharedEvent<<TargetEvent>>()`, but do not add ordinary eligibility, patch the Event pool,
or return a mutable Event instance from `ModifyNextEvent`.

## Verification contract

Extend one `MapNode` run; do not create separate headed runs for each guard:

1. after the normal run/map startup gate, call both `Hook` aggregators without the token
   and require the original room set and Event object;
2. create one token through the run and add it to `PileType.Deck` with
   `skipVisuals: true` as proof setup only;
3. call both hooks in the wrong act and require unchanged inputs;
4. enter the specified act, then require `{ RoomType.Event }` and the canonical target;
5. enter one real Unknown MapPoint with `EnterMapPointInternal`, wait for the target
   `EventRoom`, and capture the settled headed state;
6. click the real completion `NEventOptionButton`, require token count `1 -> 0`, and call
   both hooks again to prove normal selection is restored;
7. emit one structured marker containing all guards, then `selftest done`.

Use the standard startup gate from `reference/selftest-harness.md` before
`EnterMapPointInternal`; `RunManager.IsInProgress` alone races the initial map/room setup.
The proof must enter through `MapPointType.Unknown`, not debug-enter the target canonical
Event directly, because the room-type and Event-replacement hooks are the behavior under
test.

R4 live proof (2026-07-23, STS2 `0.107.1` / RitsuLib `0.4.62`): the combined Event headed
run rendered `Sealed Archive`, its description, and its real `Break the seal` option
through an Unknown MapPoint. Strict Tier 2 reported:

```text
forcedFollowUp noToken=True wrongAct=True roomForced=True eventForced=True entered=true seals=1->0 restored=True
selftest done
Fresh-run errors: none
```
