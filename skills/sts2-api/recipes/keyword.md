# Recipe: Custom Card Keyword

> Known-good on STS2 `0.107.1` with RitsuLib `0.4.62` compat. RitsuLib mints a
> deterministic `CardKeyword` value and stores it in the game's native Card keyword set;
> the R3 proof checked membership, localization, and the named Card behavior.

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
`RITSU_CARD_PROOF_KEYWORD_RESONANT`. Use `BeforeCardDescription`,
`AfterCardDescription`, or `None` intentionally. Keywords own no bitmap in open-mod;
keep `iconPath` null.

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

## Behavior and localization

Keep behavior in the host Card/Power/helper and gate it from the same keyword value when
the rule is conditional. Ship `localization/eng/card_keywords.json`:

```json
{
  "<MOD>_KEYWORD_<STEM>.title": "Resonant",
  "<MOD>_KEYWORD_<STEM>.description": "Plain-language shared rule."
}
```

`ModKeywordRegistry.GetTitle(id)` and `GetDescription(id)` expose the same localized
strings. RitsuLib's hover tip uses a deliberate null icon when no icon path is registered.

## Verification

Prove all three layers in the nearest real Card scenario:

1. the Card's native `Keywords` contains the minted value;
2. title/description localization resolves;
3. the host's named state change occurs.

For full presentation support, also render the auto-positioned text and hover tip on the
real hand Card and assert the icon is null. The R3 functional proof observed
`RITSU_CARD_PROOF_KEYWORD_RESONANT`, title `Resonant`, membership true, and Jolt's exact
6 damage. Historical M6 visible evidence remains regression input until re-run under
RitsuLib.
