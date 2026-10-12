# Recipe: Custom Card Keyword

> Under the pinned STS2 `0.107.1` / RitsuLib `0.6.7` profile, RitsuLib mints a deterministic `CardKeyword` value and stores it in the
> game's native Card keyword set.

## Contract

A keyword supplies shared vocabulary and tooltip text. It never implements gameplay by
itself. Register one mod-qualified keyword from the content pack:

```csharp
using STS2RitsuLib.Keywords;

RitsuLibFramework.CreateContentPack(ModId)
    .CardKeywordOwnedByLocNamespace(
        "resonant",
        iconPath: null,
        ModKeywordCardDescriptionPlacement.AfterCardDescription,
        includeInCardHoverTip: true)
    .Apply();
```

The qualified id is `MOD_KEYWORD_STEM`, for example
`EXAMPLE_MOD_KEYWORD_RESONANT`. Keywords own no bitmap in skill-the-spire; keep `iconPath`
null.

Pick the placement by the pinned `CardKeywordOrder` meaning (`surfaces/keyword.md`
§ Placement follows the vanilla order): `BeforeCardDescription` for hand/playability rules
like `Ethereal`, `Sly`, `Retain`, `Innate`, `Unplayable`; `AfterCardDescription` for
after-play/deck rules like `Exhaust`, `Eternal`; `None` only for a numbered keyword whose
line the Card description writes itself (`[gold]Resonant[/gold] {Resonant:diff()}.`, the
vanilla `Forge` shape).

## Attach to a Card

Prefer the native canonical set:

```csharp
using MegaCrit.Sts2.Core.Entities.Cards;
using STS2RitsuLib.Keywords;

public const string KeywordId = "<MOD>_KEYWORD_<STEM>";

public override IEnumerable<CardKeyword> CanonicalKeywords =>
    new[] { KeywordId.GetModCardKeyword() };
```

For combat-time mutation, resolve the minted value once and use
`card.AddModKeyword(value)` / `card.RemoveModKeyword(value)`. Do not generate a custom
enum field or side-loaded keyword state.

The Keyword itself never selects `reference/model-capabilities.md`,
`reference/shared-effect-hooks.md`, or lifecycle state. When the described rule needs one of those
routes, the actual Card, Power, or other model recipe owns and implements it.

## Behavior and localization

Keep behavior in the host Card/Power/helper and gate it from the same keyword value when
the rule is conditional. Ship matching `localization/eng/card_keywords.json` and
`localization/zhs/card_keywords.json`:

```json
{
  "<MOD>_KEYWORD_<STEM>.title": "Resonant",
  "<MOD>_KEYWORD_<STEM>.description": "When this card is played, also play the top card of your [gold]Draw Pile[/gold]."
}
```

```json
{
  "<MOD>_KEYWORD_<STEM>.title": "共鸣",
  "<MOD>_KEYWORD_<STEM>.description": "打出这张牌时，同时打出你[gold]抽牌堆[/gold]顶的牌。"
}
```

The description follows `reference/vanilla-text-style.md`: one or two sentences, other
glossary terms in `[gold]`, Chinese full-width punctuation. Any other string that names the
keyword writes `[gold]Resonant[/gold]` and declares
`.. new[] { KeywordId }.ToHoverTips()` in its `AdditionalHoverTips`.

`ModKeywordRegistry.GetTitle(id)` and `GetDescription(id)` expose the same localized
strings. RitsuLib's hover tip uses a deliberate null icon when no icon path is registered.

## Verification

Prove all three layers in the nearest real Card scenario:

1. the Card's native `Keywords` contains the minted value;
2. title/description localization resolves;
3. the host's named state change occurs.

For full presentation support, also render the auto-positioned text and hover tip on the
real hand Card and assert the icon is null.
