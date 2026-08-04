# M6 Bounded Forced Follow-up Event

Date: 2026-07-20

Environment: STS2 0.107.1, BaseLib 3.3.5, Windows headed run. The disposable
`baselines/.forced-followup-canary` project was built as `CanaryForcedEvent` and reused the
existing `MapNode` startup gate.

## Grounded runtime contract

The public production chain is:

```text
UnknownMapPointOdds.Roll -> Hook.ModifyUnknownMapPointRoomTypes
Act.PullNextEvent        -> Hook.ModifyNextEvent
```

Vanilla `LanternKey` uses both hooks in act index `2`; `WarHistorianRepy.IsAllowed()`
returns false. The canary reproduced the bounded shape with one custom unplayable Quest
Card and one custom target Event, without Harmony or vanilla edits.

The Quest Card returned both hook inputs unchanged without the token and in the wrong act.
In the target act it returned only `RoomType.Event` and replaced the next Event with
`SealedArchive`. The target returned false from `IsAllowed`, so it could not enter the
ordinary random pool. Its `Break the seal` option called `PlayerCmd.CompleteQuest`, removed
the token through `CardPileCmd.RemoveFromDeck`, and finished normally.

## Headed proof

Build: 0 warnings, 0 errors.

One successful headed run completed in 37.5 seconds. It entered a real Unknown MapPoint,
rendered the `Sealed Archive` title/description and enabled `Break the seal` option, clicked
that real option, and emitted:

```text
CanaryForcedEvent state proof: forcedFollowUp noToken=True wrongAct=True roomForced=True eventForced=True entered=True seals=1->0 restored=True
selftest done
Fresh-run errors: none
PASS Tier-2
```

Screenshot:
`C:\Users\YY\AppData\Roaming\SlayTheSpire2\canary_forced_followup.png`

Two earlier launches timed out in setup before entering the Event because the first harness
used an incomplete startup gate. They produced no behavior result. Reusing the established
map-generation/current-room gate fixed setup; the successful run was not repeated.

## Promotion boundary

Pipeline support is limited to solo, one custom Quest Card, one custom target Event, and
one specified act. The verified trigger is a real Unknown MapPoint; one named target option
consumes the token and restores ordinary hooks. The source grant must prevent duplicates,
while the target defensively removes every matching token.

Not promoted: arbitrary Event chains, fixed-node ordering guarantees, vanilla edits,
multiplayer ownership, duplicate-token reward semantics, interoperability ordering with
other hook-rewriting mods, or a new save-roundtrip claim. Quest Card acquisition preview
also remains presentation item 4 rather than being inferred from this semantic proof.
