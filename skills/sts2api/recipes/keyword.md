# Recipe: Custom Card Keyword

A custom keyword supplies shared vocabulary and a tooltip. RitsuLib mints a deterministic
`CardKeyword` value and stores it in the game's native Card keyword set. The keyword never
implements gameplay: its named behavior always lives in a host Card, Power, or helper, which
also selects any model-capability, shared-effect-hook, or lifecycle-state route it needs.

## SPEC fields

A keyword has no element block of its own. Declare it inside its host Card's SPEC fields:

```markdown
  - keywords: <keyword name> — <the shared rule the tooltip states>
    behavior owner: <the host element that implements it>
    placement: before description | after description | none (numbered keyword line)
```

The host Card's `localization` section records the exact English and Simplified Chinese keyword
title/description. The stable entry and the SmartFormat variables are identical between
languages.

## Registration

Register one Mod-qualified keyword from the content pack:

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

The qualified id is `MOD_KEYWORD_STEM`, e.g. `EXAMPLE_MOD_KEYWORD_RESONANT`. Keywords own no
bitmap; keep `iconPath` null (the hover tip uses a deliberate null icon).

## Attach to a Card

Prefer the native canonical set:

```csharp
using MegaCrit.Sts2.Core.Entities.Cards;
using STS2RitsuLib.Keywords;

public const string KeywordId = "<MOD>_KEYWORD_<STEM>";

public override IEnumerable<CardKeyword> CanonicalKeywords =>
    new[] { KeywordId.GetModCardKeyword() };
```

For combat-time mutation, resolve the minted value once and use `card.AddModKeyword(value)` /
`card.RemoveModKeyword(value)`. Never generate a custom enum field or side-loaded keyword state.
Keep the behavior in the host and gate it from the same keyword value when the rule is
conditional.

## The engine writes the keyword into the card text

Attaching the keyword makes RitsuLib insert its localized title, in gold, plus a localized
period, at the description boundary (`ModKeywordRegistry.GetCardText` via
`ModKeywordCardDescriptionInjector.AppendFragments`). **Never also write the keyword name into
the host Card's description**, or the player sees it twice. Native keywords work the same way:
`CardKeywordOrder` composes `Exhaust`/`Ethereal`, and vanilla `Impervious` carries none of it in
its own text. The keyword's `.description` states the shared rule for the tooltip; the host
Card's description states only what that Card does.

### Placement follows the vanilla order

The pinned `CardKeywordOrder` puts `Ethereal`, `Sly`, `Retain`, `Innate`, and `Unplayable`
**before** the description and `Exhaust` and `Eternal` **after** it. Choose by the same meaning:

- `BeforeCardDescription` for whether or when the Card is in hand or playable (start in hand,
  stay in hand, leave hand, cannot be played);
- `AfterCardDescription` for what happens to the Card after play or where it lives in the deck
  (removed, returns, cannot be removed).

RitsuLib inserts Mod lines above the vanilla "before" group and below the vanilla "after"
group, ordering several Mod keywords by id. Record the choice in SPEC.

### A keyword that carries a number is not a card keyword line

A native keyword has no amount: the composed line is only `Title.`. When the rule needs a
per-Card number ("Resonant 3"), follow vanilla `Forge`: register with
`ModKeywordCardDescriptionPlacement.None`, keep the keyword in the Card's set for its tooltip,
declare the number as a Card `DynamicVar`, and write the line yourself as the first or last
description line: `[gold]Resonant[/gold] {Resonant:diff()}.` / `[gold]共鸣[/gold]{Resonant:diff()}。`.
A number that is a stack changing during combat is a Power, not a keyword (`recipes/power.md`).

## Localization

Ship matching `localization/eng/card_keywords.json` and `localization/zhs/card_keywords.json`
with `.title` and `.description` under the exact `<MOD>_KEYWORD_<STEM>` entry:

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

The title is one or two Title Case words and the matching Chinese term; it never reuses a
vanilla keyword or Power name from the glossary. The description is one or two plain sentences
in the vanilla style, highlighting other glossary terms in `[gold]`, with Chinese full-width
punctuation. Any other string that names the keyword (another Card, a Relic, a Power) writes the
exact title in `[gold]` and declares `.. new[] { KeywordId }.ToHoverTips()` in its
`AdditionalHoverTips` (`reference/vanilla-text-style.md` § Hover tips for named terms).
`ModKeywordRegistry.GetTitle(id)` and `GetDescription(id)` expose the same strings.

## Self-test driver body

A keyword has no scenario of its own. Add the assertions below to its host Card's scenario
(`recipes/card.md`).

## Proof matrix

- Assert the keyword resolves on a real Card: the minted value is in the Card's native
  `Keywords`, and its title and description resolve to shipped localization rather than a
  generated numeric fallback key, which no behavior assertion would catch.
- Assert the composed Card text contains the keyword title exactly **once**, on the declared
  side of the description, so a hand-written duplicate is caught.
- **Assert the named behavior in the host.** The keyword carries no behavior, so a
  registration-and-tooltip proof passes for a rule that was never implemented. Drive the host
  and assert the concrete state change the tooltip promises.
- For runtime add/remove, assert both transitions on a real Card.
- Full presentation renders the auto-positioned text and hover tip on the real hand Card and
  asserts the null icon.
