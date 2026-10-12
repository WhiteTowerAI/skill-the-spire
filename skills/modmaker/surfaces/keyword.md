# Surface: keyword

Everything the pipeline needs for one custom card keyword, in one place. Read this page at
the `spec.md`, `author.md`, and `verify.md` stages when SPEC declares a custom keyword.

## No SPEC fields of its own

A custom keyword is never standalone content: it owns shared vocabulary and a tooltip, and
its named behavior always lives in a host Card, Power, or helper. It therefore has **no
element block**. Declare it inside its host Card's SPEC fields:

```markdown
  - keywords: <keyword name> — <the shared rule the tooltip states>
    behavior owner: <the host element that implements it>
    placement: before description | after description | none (numbered keyword line)
```

The host Card's `localization` section records exact English and Simplified Chinese keyword
title/description text. The stable entry and the SmartFormat variables are identical between
languages.

That the keyword carries no behavior is the reason for this shape, and also the thing its
proof must not assume — see § Proof matrix. Keyword and enchantment stay host-scoped;
`orb` has its own envelope.

The Keyword must not select `reference/model-capabilities.md`,
`reference/shared-effect-hooks.md`, or lifecycle state as its own implementation. If its named
behavior needs one of those routes, the Card, Power, or other real host selects and owns it; the
Keyword still owns only vocabulary and tooltip presentation.

## The engine writes the keyword into the card text

Registering a keyword and attaching it to a card makes RitsuLib insert the keyword's
localized title, in gold, plus a localized period, at the card description boundary
(`ModKeywordRegistry.GetCardText` via `ModKeywordCardDescriptionInjector.AppendFragments`).

**Do not also write the keyword name into the host card's description.** The player sees it
twice. This matches native keywords, where `CardKeywordOrder` composes `Exhaust`/`Ethereal`
text automatically and vanilla `Impervious` carries none of it in its own description.

The keyword's own `.description` states the shared rule for the tooltip. The host card's
description states only what that specific card does.

### Placement follows the vanilla order

The pinned `CardKeywordOrder` puts `Ethereal`, `Sly`, `Retain`, `Innate`, and `Unplayable`
**before** the description, and `Exhaust` and `Eternal` **after** it. Choose by the same
meaning:

- `BeforeCardDescription` for a rule about whether or when the card is in hand or playable
  (start in hand, stay in hand, leave hand, cannot be played);
- `AfterCardDescription` for a rule about what happens to the card after it is played or
  where it lives in the deck (removed, returns, cannot be removed).

RitsuLib inserts Mod lines above the vanilla "before" group and below the vanilla "after"
group, and orders several Mod keywords by keyword id. Record the choice in SPEC.

### A keyword that carries a number is not a card keyword line

A native card keyword has no amount: the composed line is only `Title.`. When the rule
needs a per-card number ("Resonant 3"), follow vanilla `Forge` instead: register the keyword
with `ModKeywordCardDescriptionPlacement.None`, keep it in the card's keyword set for its
tooltip, declare the number as a card `DynamicVar`, and write the line yourself as the
card's first or last description line: `[gold]Resonant[/gold] {Resonant:diff()}.` /
`[gold]共鸣[/gold]{Resonant:diff()}。`. When the number is a stack that changes during combat,
it is a Power, not a keyword: use `surfaces/power.md`.

### Naming a keyword elsewhere

Any other string that names the keyword (another Card that grants it, a Relic, a Power)
writes the exact title in `[gold]` and declares its tip:
`.. new[] { HostCard.KeywordId }.ToHoverTips()` in `AdditionalHoverTips`
(`reference/vanilla-text-style.md` § Hover tips for named terms).

### Keyword text style

The title is one or two Title Case words in English and the matching Chinese term; it never
reuses a vanilla keyword or Power name from the glossary. The `.description` is one or two
plain sentences that highlight other glossary terms in `[gold]`, like vanilla:
`If this card is discarded from your [gold]Hand[/gold] before the end of your turn, play it
for free.`

## Author the element class

**Custom keyword** — register it once with `.CardKeywordOwnedByLocNamespace(...)`, keep
`iconPath: null`, and attach the minted native `CardKeyword` through `CanonicalKeywords` or
the runtime add/remove helpers. The keyword owns vocabulary and tooltip text only; implement
its named behavior in the host.

- Ship matching `localization/eng/card_keywords.json` and
  `localization/zhs/card_keywords.json` with `.title` and `.description` under the
  exact `<MOD>_KEYWORD_<STEM>` entry.
- For combat-time mutation, resolve the minted value once and use `card.AddModKeyword(value)`
  / `card.RemoveModKeyword(value)`. Do not generate a custom enum field or side-loaded
  keyword state.
- Leave the host card's description free of the keyword name.

See `../sts2api/recipes/keyword.md` for the exact registration call and JSON shape.

## Self-test driver body

A keyword has no scenario of its own. Use its host Card's `InCombat` driver
(`surfaces/card.md`) and add the keyword assertions below to that run.

## Proof matrix

- Assert the keyword resolves on a real card: the minted value is present in the card's
  keyword set, and its title and description resolve to the shipped localization rather than
  a numeric fallback key. An unresolved keyword renders as a generated numeric loc key, which
  no behavior assertion would catch.
- Assert the composed card text contains the keyword title exactly **once**, so a
  hand-written duplicate is caught rather than shipped, and that it sits on the declared side
  of the description.
- **Assert the named behavior in the host.** The keyword itself carries no behavior, so a
  registration-and-tooltip proof passes for a keyword whose rule was never implemented —
  the player reads a rule the game does not follow. Drive the host and assert the concrete
  state change the tooltip promises.
- For runtime add/remove, assert both transitions on a real card.
