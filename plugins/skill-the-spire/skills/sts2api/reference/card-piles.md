# Reference: custom Card Piles

This page owns custom Card Piles authoring for STS2 `0.107.1` with official RitsuLib
`0.6.7`. The official Custom Card Piles tutorial establishes the feature family. Every documented
public consumer present in the pinned profile is supported; a missing focused proof is a
verification fact, not a reason to shrink the API boundary.

## Semantic input

A Mod may declare one or more piles. Each pile records:

- `local stem`: stable Mod-local identity;
- `scope`: `combat` or `run`;
- `style`: `headless`, `top bar deck`, `bottom left`, `bottom right`, or `extra hand`;
- `anchor`: style default, a matching preset plus offset, or custom position plus pivot;
- `icon`: none, checked Mod resource, or explicit built-in fallback;
- `localization`: title, description, and empty text in required `eng` and `zhs`, plus any
  additional shipped language;
- `open behavior`: default pile screen or one declared public `ICapstoneScreen` route;
- `visibility`: one deterministic player/pile/room predicate or always visible;
- `hover tip`: placement and screen offset;
- `hotkeys`: zero or more existing input-action IDs that open the pile;
- `view`: vanilla, deck-like, or explicit inspect/upgrade/sort/style settings;
- `movement`: every entry/exit trigger, exact source/destination, top/bottom position, and
  whether the move is conditional;
- optional ExtraHand presentation, interaction, layout, and visual callbacks.

Pile state must also describe capacity, duplicate-instance policy, empty/full behavior,
and what happens to its Cards at combat end, run end, or another declared transition.
These are gameplay semantics, not framework names. Do not retain a played Card merely
because a custom pile exists: result-pile behavior is declared separately from explicit
`CardPileCmd` movement.

## Registration and identity

Add every pile to the Mod's one deferred content pack before its final `.Apply()`:

```csharp
using STS2RitsuLib.CardPiles;

RitsuLibFramework.CreateContentPack(MainFile.ModId)
    // Other content registrations remain in this same builder.
    .CardPileOwned("archive", new ModCardPileSpec
    {
        Scope = ModCardPileScope.CombatOnly,
        Style = ModCardPileUiStyle.BottomLeft,
        Anchor = ModCardPileAnchor.Default,
        IconPath = "res://<ModName>/images/archive.png",
        OnOpen = static context => context.ShowDefaultPileScreen(),
        VisibleWhen = static context => context.Player != null,
    })
    .Apply();
```

`CardPileOwned` qualifies the ID as `{MODID}_CARDPILE_{LOCALSTEM}`. Derive its deterministic
type once when needed:

```csharp
internal static string ArchiveId { get; } =
    ModContentRegistry.GetQualifiedCardPileId(MainFile.ModId, "archive");

internal static PileType ArchiveType => ModCardPileRegistry.GetPileType(ArchiveId);
```

Use raw-global `CardPile(...)` only when SPEC explicitly declares interoperability with an
existing shared global ID. Normal generated content uses Mod-owned IDs.

## Scope

`ModCardPileScope.CombatOnly` creates one pile per `PlayerCombatState`, includes it in
`AllPiles`/combat-pile behavior, and discards it with that combat.

`ModCardPileScope.RunPersistent` attaches the pile to `Player`, includes it in
`Player.Piles`, persists across combats, and is serialized by RitsuLib `0.6.7` run-save
data. Save/load, existing-save behavior, and run-end cleanup are verification obligations
for a generated Mod that actually uses this scope; they are not separate support gates.

## UI styles and anchors

All public styles are supported:

| Style | Player-facing consumer |
|---|---|
| `Headless` | no control; movement and programmatic inspection remain available |
| `TopBarDeck` | openable pile button beside the top-bar deck area |
| `BottomLeft` | openable combat pile button near draw/discard |
| `BottomRight` | openable combat pile button near exhaust |
| `ExtraHand` | visible native Card holders with optional manual play |

Use `ModCardPileAnchor.Default` when no exact placement is requested. The supported preset
kinds are `BottomLeftPrimary`, `BottomLeftSecondary`, `BottomRightPrimary`,
`BottomRightSecondary`, `TopBarAfterDeck`, `TopBarBeforeModifiers`, `ExtraHandAbove`, and
`ExtraHandBelow`. Pair a preset with its matching style and add the requested `Vector2`
offset.

Custom coordinates use `ModCardPileAnchorKind.Custom`, `CustomPosition`, `Offset`, and
`CustomAuthoringPivot`, or the public `AtPosition`, `AtCenter`, and `AtPivot` factories.
Custom placement is supported as authored behavior. Its headed proof must cover the actual
target aspect ratios and every neighboring native/custom UI surface named by SPEC.

## Opening, hover tips, hotkeys, and visibility

A `null` `OnOpen` uses the vanilla pile screen. `context.ShowDefaultPileScreen()` selects
that route explicitly; `context.OpenCapstoneScreen(screen)` opens a declared public custom
screen. Empty piles show the localized `.empty` message instead of calling `OnOpen`.

`VisibleWhen` may use the public `ModCardPileVisibilityContext` to read the definition,
player, pile, and button/room context. Generate a pure deterministic predicate: no Cmds,
mutation, RNG, async work, retained node references, or logging side effects.

`Hotkeys` contains existing Godot input-action IDs and opens the pile screen. It does not
bind an individual ExtraHand Card to the vanilla numbered Card shortcuts.

`HoverTipPlacement` supports `Auto`, `BelowButtonTrailingEdge`, `AboveButtonCentered`, and
`BelowButtonCentered`; `HoverTipScreenOffset` adds the requested final offset. Missing or
invalid `IconPath` uses RitsuLib's placeholder texture.

## Pile screen capabilities

`View = null` preserves the vanilla pile screen. `ModCardPileViewSpec.DeckLike` enables
the standard deck-like inspection, upgrade-preview, and sorting behavior. An explicit
`ModCardPileViewSpec` may independently configure:

- Card inspection and the upgrade-preview toggle;
- sort bar visibility;
- sort options `Obtained`, `Type`, `Cost`, `Alphabetical`, and `Rarity`;
- ascending/descending default sorting;
- toolbar and sort-button texture paths, fixed materials, or public style providers;
- sort-button hue suppression;
- upgrade-preview label and outline colors.

When multiple styling inputs target the same property, follow RitsuLib's documented
precedence rather than emitting duplicate competing sources. Resource paths are checked
and packed like other generated assets. A provider is generated only from deterministic
semantic conditions; do not pass raw user code through SPEC.

## Movement and access

Use the native public pile commands and always await asynchronous movement:

```csharp
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;

await CardPileCmd.Add(card, ArchiveType, CardPilePosition.Bottom);

var pile = ArchiveType.GetPile(card.Owner);
foreach (CardModel stored in pile?.Cards ?? [])
{
    // Read the live cards in current pile order.
}
```

`CardPilePosition.Top` and `Bottom` are both supported. Check capacity or other rejection
rules before starting an awaited move so a rejected move leaves both piles unchanged. Move
the exact Card instance; never create a visual duplicate or call internal pile mutation.
The optional fourth `CardPileCmd.Add` argument is `clonedBy`, not a generic source.

Other public vanilla `CardPileCmd` operations may target the registered pile when their
documented signature accepts its `PileType`. Resolve the live pile through `GetPile(player)`
when an operation needs current cards or order.

## ExtraHand

For `Style = ExtraHand`, `CardShouldBeVisible` controls whether pile Cards receive visible
native holders. `ModCardPileExtraHandSpec` supports all documented public settings:

- layout direction `Horizontal`, `Vertical`, or `VanillaHand`;
- spacing, resting Card scale, and hover scale;
- playable glow on/off;
- manual play on/off (`AllowCardPlay`);
- optional base-game Hand semantics through `Behaviors`: `ApplyHandTurnEndRules` (end-of-turn
  in-Hand and Ethereal processing), `FlushWithHand` (end-of-turn retain/discard flush), both
  as `FullHand`, or the default `None`;
- disabled presentation: `DisabledOffset`, `DisabledModulate`, and
  `DisabledTransitionDuration` (defaults match the base-game Hand);
- a deterministic `LayoutResolver` returning `ModExtraHandCardTransform`;
- `OnCardVisualCreated` and `OnCardArrived` callbacks using the public Card/holder context.

ExtraHand Cards never count toward the base-game maximum Hand size or draw capacity, under any
`Behaviors` combination. Without `FlushWithHand` they stay in the pile at end of turn; a SPEC
that wants them discarded or retained like Hand Cards selects that behavior explicitly.

With manual play enabled, official RitsuLib keeps the Card model in its ExtraHand pile
throughout targeting and queuing. Only the holder node joins the native play flow
(`NPlayerHand.StartCardPlay`), and the vanilla manual-play checks treat the pile as
Hand-compatible inside that path, so Hand-sensitive costs and validation still apply.
Play-enabled Cards participate in the core playable-Card checks. Cancellation or a
multiplayer rollback returns the same Card node to its source pile; success uses normal
payment, hooks, targeting, and result-pile processing. Generated Mods do not reproduce or
patch this coordinator.

Idle ExtraHand holders remain outside `NPlayerHand.ActiveHolders`, so vanilla numbered
shortcuts remain owned by the native Hand. Layout and callbacks may use the public context
(`Definition`, `Container`, `Card`, `Holder`, `Index`, `Count`, `IsFocused`, and
`DefaultTransform`) to implement the declared presentation. Callback behavior must remain
scoped to that pile and must clean up any event connection or child node it creates.

## Localization

Write all three keys to every shipped
`<ModName>/localization/<lang>/static_hover_tips.json` table:

```json
{
  "MY_MOD_CARDPILE_ARCHIVE.title": "Archive",
  "MY_MOD_CARDPILE_ARCHIVE.description": "Cards stored by this Mod.",
  "MY_MOD_CARDPILE_ARCHIVE.empty": "The Archive is empty."
}
```

The keys use the qualified pile ID. Do not invent a separate localization namespace for
the ExtraHand presentation.

## Verification ownership

Verification scales to what the generated Mod selected; it does not decide API
support. Deterministic checks own identity, order, capacity, rejection, duplicate-instance
rules, visibility predicates, and declared state transitions. The closest real host owns
the selected UI and lifecycle:

- combat/run scope creation, reset, save/load, and cleanup;
- each selected button/TopBar/ExtraHand/custom-anchor presentation;
- empty/open/view/sort/inspect/upgrade-preview/hotkey behavior;
- Card movement, exact instance identity, top/bottom order, and non-play exits;
- ExtraHand mouse/controller focus, cancellation, payment, consecutive play, result piles,
  numbered-shortcut isolation, callbacks, and layout at requested aspect ratios.

## Boundaries

The API creates new Mod-owned piles. It does not by itself replace vanilla piles,
change unrelated Cards' result locations, or authorize ungrounded Harmony, reflection,
Publicizer, or IL generation. Use only the selected public Card Piles API and normal game
commands. This route does not design, add, or claim verification for Multiplayer behavior or a
Card Pile-to-Multiplayer integration. Record any newly confirmed API/lifecycle defect as the
smallest affected consumer limitation rather than retracting the whole route.
