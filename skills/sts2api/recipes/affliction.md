# Recipe: Affliction

Use for a new combat-only condition attached to a Card. Extend `ModAfflictionTemplate`, register
once in the deferred content pack, and apply/remove only through the public Card commands.

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

Call `base.CanAfflict(card)` before adding restrictions. `Amount` is stored as `int`; do not
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

`Afflict<T>` returns `null` for rejected application. `AfflictAndPreview` applies each Card, then
previews only successful Cards; every Card must have the same owner when preview is enabled. Pick
targets with the Mod-scoped RNG route in `reference/lifecycle-state-rng.md`, never `System.Random`.
Use `CardCmd.ClearAffliction`; direct internal removal is not an authoring route.

The Card wrapper calls the attached Affliction's awaited `OnPlay` after the Card's own play body
and Enchantment execution. `AfterApplied` and `BeforeRemoved` are synchronous `void`; keep them to
immediate state changes and use an async lifecycle hook for commands.

## Text, hover tips, and overlay

Use `afflictions.json` in `eng` and `zhs` once this surface has any localization:

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

Follow the Affliction row of `reference/vanilla-text-style.md`: plain title, `[blue]` amounts,
`[gold]` glossary terms, Energy through `energyIcons()`.

Set `HasExtraCardText` only when the key exists. `RegisteredKeywordIds` and
`AdditionalHoverTips` add display tips; they do not implement keyword behavior. A selected custom
overlay overrides `AssetProfile` with an existing PackedScene path. Omit it for the explicit empty
profile; never claim a missing overlay is a visual fallback.

## Shared behavior and proof

Read `reference/model-hook-participation.md` for `surface: affliction`, plus the selected model
capability/lifecycle/shared-effect references. The Affliction's `Card` is the exact owner and its
`CombatState` is valid only while attached in combat. Guard other Cards and neutral subjects.

SelfTest follows `surfaces/affliction.md`: rejected application, first apply, stack/reject,
attached play/hook behavior, clear, and combat reset. Headed review separately owns localized
extra text, hover tips, and overlay layout.
