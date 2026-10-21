# Recipe: Custom Card Pile

Use for an independently registered place that stores, moves, inspects, or visibly presents exact
Card instances outside the vanilla piles. A Card Pile owns its combat/run lifetime, registration,
persistence, screen/control/ExtraHand presentation, movement rules, and cleanup. Read the complete
`reference/card-piles.md` before authoring: it owns registration, scope, persistence, styles,
anchors, screens, sorting, visibility, hotkeys, native movement, localization, ExtraHand
interaction, callbacks, and the proof matrix. Also read `recipes/card.md` for Card creation and
play, and `reference/card-play-lifecycle.md` when manual play composes with owner play hooks or
result-pile rules.

Never reduce this surface to the ExtraHand case: `headless`, `TopBarDeck`, `BottomLeft`,
`BottomRight`, and `ExtraHand`; every documented preset or custom anchor; default/capstone open
routes; vanilla/deck-like/explicit views; sorting, inspection, upgrade preview, visibility, hover,
hotkeys, flight positions, and ExtraHand layouts/callbacks are all authorable when selected. Never
add deferred Settings, Multiplayer, Telemetry, Update Check, Progression, or Badge integrations
through a pile control.

## DESIGN and SPEC vocabulary

Settle and write every selected pile's:

- stable local identity, capacity/duplicate rules, combat-only or run-persistent scope, and exact
  reset/save/restore/run-end behavior;
- `headless`, top-bar deck, bottom-left, bottom-right, or ExtraHand style; matching preset plus
  offset, or explicit custom position/pivot;
- English and Simplified Chinese title (plain Title Case), description, and empty text (short
  sentences with `[gold]` glossary terms and `[blue]` counts, per
  `reference/vanilla-text-style.md`); checked icon or placeholder;
- visibility predicate, hover placement, hotkeys, default or capstone open behavior, and vanilla,
  deck-like, or explicit inspect/upgrade/sort view;
- every trigger that moves an exact Card instance in or out: source, destination, top/bottom
  order, pre-move rejection, and normal result-pile behavior;
- ExtraHand visibility, layout, scale, glow, manual-play policy, and any scoped visual callbacks;
  and
- real-host SelfTest plus headed/controller cases for every selected lifetime and UI consumer.

## Required lowering

Lower each pile's stable identity and complete selected behavior through the Mod's one content
pack:

```csharp
ModContentPackBuilder.For(MainFile.ModId)
    .CardPileOwned("archive", new ModCardPileSpec
    {
        Scope = ModCardPileScope.RunPersistent,
        Style = ModCardPileUiStyle.TopBarDeck,
        Anchor = ModCardPileAnchor.Default,
        IconPath = "res://<ModName>/images/archive.png",
        View = ModCardPileViewSpec.DeckLike,
    })
    .Apply();
```

Resolve its qualified id and dynamic type through `ModContentRegistry.GetQualifiedCardPileId` and
`ModCardPileRegistry.GetPileType`. Move the exact live Card only with awaited native `CardPileCmd`,
rejecting capacity, duplicate, or semantic failures before movement. Never mutate pile collections
directly or clone a Card to imitate movement. Run-persistent piles use RitsuLib's save/restore
route, never a second shadow list. ExtraHand manual play uses RitsuLib's native play coordinator;
never reproduce or patch it.

## Proof matrix

Follow the selected matrix in `reference/card-piles.md`:

1. assert the qualified id, dynamic `PileType`, exact scope, one live pile per declared owner, and
   no duplicate registration;
2. test empty/full/capacity/duplicate rejection before mutation, exact instance identity, movement
   order, and every declared exit/result destination;
3. test combat reset or run persistence, save/load restoration, existing-save behavior, and run
   cleanup as selected;
4. test each selected button, hotkey, visibility, hover, open/view/sort/inspect/upgrade consumer;
5. for ExtraHand, test mouse/controller focus, cancel restoration, payment, consecutive plays,
   normal result piles, numbered-shortcut isolation, layout, and callback cleanup; and
6. headed review covers requested aspect ratios, custom anchors, neighboring controls, icon/text,
   animations, and controller behavior.

Static compile, registration, and pile lookup are not UI, movement, persistence, or gameplay
proof.
