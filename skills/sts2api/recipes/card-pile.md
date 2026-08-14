# Recipe: Custom Card Pile

Use this recipe to route an independently requested Card Pile into the complete public API.
Read `reference/card-piles.md` before authoring; that page owns the exact registration, scope,
persistence, styles, anchors, screens, sorting, visibility, hotkeys, native movement, localization,
ExtraHand interaction, callbacks, and proof matrix.

## Required lowering

For every pile, lower the SPEC's stable identity and complete selected behavior through the Mod's
one content pack:

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

Resolve its qualified ID and dynamic type through `ModContentRegistry.GetQualifiedCardPileId` and
`ModCardPileRegistry.GetPileType`. Move the exact live Card with awaited `CardPileCmd`; reject
capacity, duplicate, or semantic failures before movement. Run-persistent piles use RitsuLib's
save/restore route; do not serialize a second shadow list. ExtraHand manual play uses RitsuLib's
native-Hand coordinator; do not reproduce or patch it.

## Completeness boundary

`headless`, `TopBarDeck`, `BottomLeft`, `BottomRight`, and `ExtraHand`; every documented preset or
custom anchor; default/capstone open routes; vanilla/deck-like/explicit views; sorting, inspection,
upgrade preview, visibility, hover, hotkeys, flight positions, and ExtraHand layouts/callbacks are
all authorable when selected. Missing old examples or focused game proof does not narrow them.

Follow `surfaces/card-pile.md` and the detailed reference for SelfTest and headed/controller proof.
Static compile and the historical `0.5.4` ExtraHand observations do not establish new `0.5.11`
variants as game-observed. Do not add deferred Settings, Multiplayer, Telemetry, Update Check,
Progression, or Badge integrations through a pile control.
