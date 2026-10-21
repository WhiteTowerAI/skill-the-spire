# Recipe: Affliction

Use for a new combat-only condition attached to one concrete Card. An Affliction is not a run-wide
curse, a deck-wide rule, or another name for an Enchantment: it is applied to a mutable Card during
combat, participates while attached, and travels only with the host Card lifecycle the game
provides. Extend `ModAfflictionTemplate`, register once in the deferred content pack, and
apply/remove only through the public Card commands. The Affliction itself is the truthful owner;
never register a process-wide listener or Global Effect to imitate a Card-attached condition.

## DESIGN and SPEC vocabulary

Settle and write:

- identity and the Card types/keywords/states it may afflict;
- stackable or single-application behavior and the integer amount meaning;
- application source, selected Card or Card set, preview style, and rejection behavior;
- attached triggers/effects, hook participation, and the exact owner guard;
- `AfterApplied`, `BeforeRemoved`, and attached-Card `OnPlay` behavior when selected;
- title, description, optional extra Card text, `{Amount}` use, hover tips, and overlay choice;
- removal/reset expectations and every neutral or rejected case; and
- `CombatPlayer` SelfTest plus headed Card-overlay/text review when presentation is selected.

An Affliction is combat-only: never promise run persistence, deck acquisition, or a post-combat
owner. The existing Affliction must be the same concrete type before stacking; another attached
type is not a replacement route.

## Registration and model

```csharp
RitsuLibFramework.CreateContentPack(ModId)
    .Affliction<Afflictions.<AfflictionName>>()
    .Apply();
```

```csharp
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using STS2RitsuLib.Scaffolding.Content;

namespace <ModName>.Afflictions;

public sealed class <AfflictionName> : ModAfflictionTemplate
{
    public override bool IsStackable => <true-or-false>;
    public override bool HasExtraCardText => <true-or-false>;
    public override bool CanAfflictUnplayableCards => <true-or-false>;

    public override bool CanAfflict(CardModel card) =>
        base.CanAfflict(card) && <exact-extra-card-guard>;

    // Override AfterApplied, BeforeRemoved, OnPlay, or reachable model hooks only when SPEC
    // selects them. Synchronous apply/remove callbacks cannot await commands.
}
```

Call `base.CanAfflict(card)` before adding restrictions. `Amount` is stored as `int`; never
advertise fractional stacking even though the command parameter is decimal. One Card carries at
most one Affliction type. A stackable second application of the same type increments `Amount` and
does not call `AfterApplied` again.

## Apply, preview, and remove

```csharp
AfflictionName? applied = await CardCmd.Afflict<AfflictionName>(card, amount: 2m);

IEnumerable<AfflictionName> appliedMany =
    await CardCmd.AfflictAndPreview<AfflictionName>(cards, amount: 1m);

CardCmd.ClearAffliction(card);
```

`Afflict<T>` returns `null` when combat/host checks or `CanAfflict` reject the application.
`AfflictAndPreview` applies each Card, then previews only the successful ones; every Card must have
the same owner when preview is enabled. Pick targets with the Mod-scoped RNG route in
`reference/lifecycle-state-rng.md`, never `System.Random`. Remove only through
`CardCmd.ClearAffliction`. Apply, preview, and clear are this recipe's specialized transaction,
not ordinary Card creation or movement.

## The effect sequence

The Card wrapper calls the attached Affliction's awaited
`OnPlay(PlayerChoiceContext choiceContext, Creature? target)` after the Card's own play body and
Enchantment execution; it is the only path that composes ordinary commands directly. It binds the
host `Card`, `Card.Owner`, `Card.Owner.Creature`, `choiceContext`, and the nullable resolved
`target`. Null-check the target when the primitive needs one, lower effects through
`reference/effect-primitives.md`, and keep the host Card as `cardSource`. The callback does not
receive the enclosing `CardPlay`: pass `cardPlay: null` where a primitive permits it and block any
effect that requires it. `AfterApplied` and `BeforeRemoved` are synchronous `void`: keep them to
immediate state changes and use an actual async lifecycle hook for commands.

## Hook participation and optional routes

Raw hooks use `reference/model-hook-participation.md` with `surface: affliction`; only
combat-reachable hooks are admitted, and Build rejects the rest. The Affliction's `Card` is the
exact owner, and its `CombatState` is valid only while attached in combat; guard other Cards and
neutral subjects. Read `reference/model-capabilities.md` only when behavior is a separable component
rather than the Affliction's identity, `reference/lifecycle-state-rng.md` for subscriptions,
disposal, or deterministic target selection, and `reference/shared-effect-hooks.md` for the
dedicated per-hit, heal, resource, and hand services.

## Text, hover tips, and overlay

Use `afflictions.json` in `eng` and `zhs`:

```json
{
  "<MOD>-<AFFLICTION>.title": "Galvanized",
  "<MOD>-<AFFLICTION>.description": "Take [blue]{Amount}[/blue] damage when this card is played.",
  "<MOD>-<AFFLICTION>.extraCardText": "Take [blue]{Amount}[/blue] damage."
}
```

```json
{
  "<MOD>-<AFFLICTION>.title": "流电",
  "<MOD>-<AFFLICTION>.description": "打出这张牌时受到[blue]{Amount}[/blue]点伤害。",
  "<MOD>-<AFFLICTION>.extraCardText": "受到[blue]{Amount}[/blue]点伤害。"
}
```

Follow the Affliction row of `reference/vanilla-text-style.md`: plain title, `[blue]{Amount}[/blue]`,
`[gold]` glossary terms, Energy through `energyIcons()`; `.extraCardText` is one short Card-face
sentence. A Card or Relic that applies the Affliction names it in `[gold]` and declares
`HoverTipFactory.FromAffliction<T>()` in its `AdditionalHoverTips`.

Set `HasExtraCardText` only when the key exists. `RegisteredKeywordIds` and `AdditionalHoverTips`
add display tips; they never implement keyword behavior. A selected custom overlay overrides
`AssetProfile` with an existing PackedScene path; omit it for the explicit empty profile and never
claim a missing overlay is a visual fallback.

## Proof matrix

Use a real mutable Card in a `CombatPlayer` scenario:

1. reject every disallowed Card and assert no Affliction, history entry, preview, or side effect;
2. apply to one allowed Card and assert the concrete type, exact integer amount, owner Card
   identity, `AfterApplied` exactly once, localized text, and the selected overlay resource;
3. for stackable behavior, apply again and assert the same attached instance/type and exact summed
   amount; for non-stackable behavior, assert the second application is rejected;
4. play the attached Card and assert `OnPlay` and selected hook effects after the real Card
   wrapper, plus one unrelated Card or event that stays neutral;
5. clear through `CardCmd.ClearAffliction`, assert `BeforeRemoved` exactly once and no further
   participation, then cross the declared combat end/reset edge; and
6. for multi-Card preview, use same-owner Cards and assert only successful Cards are previewed.

Headed review separately owns localized extra text, hover tips, overlay layout, and
mouse/controller quality. Source and Build establish neither attachment behavior nor visual proof.
