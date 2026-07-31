# Combat-only visible CardPile / ExtraHand

Status: implemented authoring route for STS2 `0.107.1` and RitsuLib `0.4.67`.

The documented public Card Piles Package and its public consumers are supported when the
pinned profile exposes the required public members. This page is the initial generated
recipe for one visible, generated-Mod-local, singleplayer combat pile. Missing recipes for
other documented styles, views, anchors, or scopes are authoring gaps, not reasons to call
the public Package unsupported.

## Initial generated contract

| Concern | Required semantic result |
|---|---|
| owner/lifetime | local Player / combat; a new `PlayerCombatState` owns a new empty pile |
| presentation | visible ExtraHand using native card holders and the fixed compact layout below |
| capacity | finite positive integer; check capacity before starting the awaited move |
| overflow | reject the incoming move without changing either pile |
| order | every entry and non-play exit declares `Top` or `Bottom` |
| duplicates | distinct instances of the same model may coexist; the same Card instance exists in exactly one pile |
| manual play | enabled or disabled per pile; when enabled, use the normal Card play pipeline |
| cancellation | target and queued-action cancellation restore the exact Card to its recorded source index |
| success | successful manual play follows the Card's normal result-pile lifecycle |
| cleanup | combat end removes pile contents/UI/subscriptions; combat 2 starts with a distinct empty pile |
| multiplayer | singleplayer only in the generated recipe |

This is a real Card pile, not the ordered semantic buffer. Cards enter only through an
explicit requested move. Never intercept an already played source Card into this pile,
retain played Cards in an ad hoc collection, or change unrelated Cards' result piles.

## Registration

Add one `.CardPileOwned(...)` step to the existing content pack before its single final
`.Apply()`. Use a stable local stem because the qualified pile ID also owns localization.

```csharp
using Godot;
using STS2RitsuLib.CardPiles;

RitsuLibFramework.CreateContentPack(MainFile.ModId)
    // Keep the existing generated content registrations here.
    .CardPileOwned(ArchivePile.LocalStem, new ModCardPileSpec
    {
        Scope = ModCardPileScope.CombatOnly,
        Style = ModCardPileUiStyle.ExtraHand,
        Anchor = new ModCardPileAnchor(
            ModCardPileAnchorKind.ExtraHandAbove,
            new Vector2(0f, -420f)),
        CardShouldBeVisible = true,
        ExtraHand = new ModCardPileExtraHandSpec
        {
            Direction = ModExtraHandLayoutDirection.Horizontal,
            Spacing = 180f,
            CardScale = Vector2.One * 0.55f,
            HoverScale = Vector2.One * 0.75f,
            ShowPlayableGlow = true,
            AllowCardPlay = <true when manual play is enabled>,
        },
    })
    .Apply();
```

The generated recipe uses one preset-relative offset and one compact three-Card horizontal
layout. Its resting Cards stay above the native Hand even at the recipe's capacity; hover
enlargement remains bounded. Do not emit `LayoutResolver`, presentation callbacks, flight
resolvers, or absolute/user-authored viewport coordinates. A future recipe may expose
another documented public consumer without changing Package support.

## Stable type and bounded movement

Derive the qualified ID once, resolve its deterministic `PileType`, inspect the live pile,
then use the normal awaited command. Capacity and optional same-model rejection are
preflight rules; they are not a replacement collection.

```csharp
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using STS2RitsuLib.CardPiles;
using STS2RitsuLib.Content;

namespace <ModName>.<ModName>Code;

internal static class ArchivePile
{
    internal const string LocalStem = "archive";
    internal const int Capacity = 3;

    internal static string Id { get; } =
        ModContentRegistry.GetQualifiedCardPileId(MainFile.ModId, LocalStem);

    internal static PileType Type => ModCardPileRegistry.GetPileType(Id);

    internal static async Task<bool> TryMoveAsync(
        CardModel card,
        CardPilePosition position)
    {
        var pile = Type.GetPile(card.Owner);
        if (pile == null || pile.Cards.Count >= Capacity)
            return false;

        await CardPileCmd.Add(card, Type, position);
        return ReferenceEquals(card.Pile, pile);
    }
}
```

Call this helper only from an awaited game-action path. Use only
`CardPilePosition.Top` or `CardPilePosition.Bottom` from SPEC. For a generated Card, create
it through the current combat state and pass that exact instance to `TryMoveAsync`; do not
create a second visual-only copy. If SPEC rejects repeated model IDs, add that check beside
the capacity check before the command. Do not call `AddInternal`, `RemoveInternal`, or
`skipVisuals: true` from generated gameplay.

A non-play exit is another awaited `CardPileCmd.Add` of the exact instance to its declared
destination and position. The command owns removal from the source pile, history/visual
coordination, and the resulting `CardPileAddResult`.

The optional fourth `CardPileCmd.Add` argument is `clonedBy`, not a general action source.
Do not pass the entering/exiting Card or its trigger there unless the actual gameplay effect
is a clone operation.

## ExtraHand interaction lifecycle

RitsuLib mounts each visible Card in a native `NHandCardHolder`. That public Package route
provides hover enlargement, keyword tips, controller focus, playable glow, and optional
manual play.

When manual play begins, RitsuLib records the source pile and source index, silently moves
the exact Card into the backend vanilla Hand, and enters `NPlayerHand.StartCardPlay` with
the selected holder. This preserves the native selected-card transform, `_currentCardPlay`,
awaiting-holder cleanup, mouse/controller targeting, and immediate follow-up play. During
targeting, vanilla logic intentionally sees `PileType.Hand`.

- target-selection cancellation restores the exact Card at its recorded source index;
- queued-action cancellation before commit performs the same restoration;
- failed payment must not spend resources, run play hooks, or lose the Card;
- successful manual play uses normal payment, hooks, action queue, and result-pile
  processing;
- Exhaust, retain, ethereal, or another result rule declared by the Card remains the Card's
  own normal lifecycle rather than an ExtraHand override.

`AllowCardPlay = false` keeps the holders visible/hoverable but not clickable. It does not
turn the pile into a hidden zone.

### Numbered shortcut ownership

Numbered select-card shortcuts remain exclusive to the native Hand. RitsuLib creates each
ExtraHand holder under the `NModExtraHand` container; generated code must never add or
reparent those idle holders into `NPlayerHand.CardHolderContainer`, call
`NPlayerHand.Add`, or synthesize numbered input. Consequently `NPlayerHand.ActiveHolders`,
which owns the vanilla numbered-shortcut index, contains only native-Hand holders.

RitsuLib may temporarily bridge one holder through the native Hand only after mouse or
controller play has already begun. That internal play lifecycle does not make idle
ExtraHand Cards candidates for `1`-`5` or the other numbered select-card shortcuts.
`ModCardPileSpec.Hotkeys` opens a pile view; it is not a numbered Card-play binding.

## Localization

Add all three keys to `<ModName>/localization/eng/static_hover_tips.json` using the
qualified ID stem:

```json
{
  "MYMOD_CARDPILE_ARCHIVE.title": "Archive",
  "MYMOD_CARDPILE_ARCHIVE.description": "Cards set aside for this combat.",
  "MYMOD_CARDPILE_ARCHIVE.empty": "The Archive is empty."
}
```

The visible ExtraHand itself has no title bar or empty label: zero Cards means zero holders.
The `.empty` entry remains required by the registered Card Pile localization contract and
is used by openable pile-view consumers.

## Proof contract

Use one focused `CombatPlayer` fixture. Local assertions own exact Card IDs, instance
identity, pile membership/order, capacity, overflow, Energy/payment, hook count, result
pile, and combat reset. The real game UI owns holder presentation and interaction.

Required behavior matrix:

1. empty, one, full, and overflow states;
2. explicit Top and Bottom insertion plus one non-play exit;
3. distinct same-model instances without duplicating one instance;
4. hover/keyword tips, playable and unplayable glow;
5. mouse and controller focus inside the pile and entry/return from native Hand;
6. numbered shortcuts `1`-`5` select only native-Hand Cards and never an idle ExtraHand Card;
7. single-target and multi-target manual play when both are generated;
8. insufficient payment, target cancel, and queued-action cancel;
9. successful Play to the Card's normal result pile with exactly-once payment/hooks;
10. after one successful ExtraHand Play fully resolves, a remaining ExtraHand Card can
    immediately enter the same native selected-card presentation and play path;
11. combat-end UI/content cleanup and a clean second combat;
12. 16:9 and 16:10 placement disjoint from native Hand, Energy, draw/discard/exhaust
    controls, Powers, and the fixed Character resource UI.

When the human lead reserves the game run, build and deploy the fixture but do not launch
STS2. Give the lead the exact `fight`, `card`, and `energy` console commands plus the matrix
above. A reported headed result is recorded as manual observation. An unrun exact Tier 1
log gate or structured `selftest done` remains an exception, not a pass.

## Boundaries

The initial generated recipe does not author run persistence, remote-player UI,
multiplayer ordering, vanilla-pile replacement, hidden zones, arbitrary layout callbacks,
or retained played Cards. These are exact recipe/lifecycle boundaries; they do not reduce
support for other documented public Card Piles Package consumers whose APIs exist in the
pinned RitsuLib profile.
