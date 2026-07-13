# Recipe: Custom Card Keyword

> A grounded, copy-adaptable pattern for adding a named rule vocabulary to cards.
> A keyword supplies the localized title/tooltip and a stable enum value; it does **not**
> implement behavior by itself. The host Card/Power/helper must implement the rule, and
> tier-2 must prove both keyword membership and the named state change.

## When to use

Use a custom keyword when several cards/mechanics should speak the same concise language
(e.g. vanilla `Ethereal`, `Retain`, `Sly`). Do not create a keyword for a one-off sentence,
and do not use a Power merely to obtain highlighted tooltip text.

## Registration

BaseLib generates a custom `CardKeyword` enum value from a static field:

```csharp
using BaseLib.Patches.Content;
using MegaCrit.Sts2.Core.Entities.Cards;

namespace <ModName>.<ModName>Code;

public static class Keywords
{
    [CustomEnum]
    [KeywordProperties(AutoKeywordPosition.After)]
    public static CardKeyword <KeywordName>;
}
```

- `[CustomEnum]` is required. BaseLib assigns the value before ModelDb initialization.
- The loc prefix is `<ROOT_NAMESPACE_UPPER>-<FIELD_OR_CUSTOM_NAME_UPPER>`.
- `[KeywordProperties]` is optional. `Before`/`After` automatically inserts the keyword's
  localized title around the card description; `None` keeps it tooltip-only/manual.
- `RichKeyword` defaults true and enables rich tooltip formatting.
- No `[Pool]`, model subclass, or manual registry call exists for keywords.

## Localization

Write `localization/eng/card_keywords.json`; the analyzer requires exactly `.title` and
`.description` for every custom `CardKeyword`:

```json
{
  "<MODNAME_UPPER>-<KEYWORD_UPPER>.title": "<Shown name>",
  "<MODNAME_UPPER>-<KEYWORD_UPPER>.description": "<Plain-language shared rule>"
}
```

## Attach it to a card

For an intrinsic keyword, override the host card's canonical set:

```csharp
public override IEnumerable<CardKeyword> CanonicalKeywords =>
    new[] { Keywords.<KeywordName> };
```

For a combat-time change, use `CardCmd.ApplyKeyword(card, Keywords.<KeywordName>)` and
`CardCmd.RemoveKeyword(...)`. Other models may also override `TryModifyKeywordsInCombat`
for a global, computed keyword; do that only when the rule really belongs to a persistent
Power/Relic rather than the card itself.

## Implement the rule

A custom enum plus tooltip has no automatic semantics. Put the real behavior in the host
hook or a shared helper. Keep display and behavior tied to the same keyword field so the
label cannot drift from the rule:

```csharp
bool active = Keywords.Contains(Keywords.<KeywordName>);
if (active)
    await <the real Cmd sequence>;
```

If multiple hosts share non-trivial behavior, extract a small mechanic helper; do not copy
an entire Power into every card.

## Type + Scenario proof

A keyword is not complete when only localization loads.

1. **Type proof:** clean build/package/load; exact `card_keywords` loc; host Card contains
   the generated keyword value.
2. **Scenario proof (`CombatPlayer`):** drive the host by its real type (normally Card),
   assert keyword membership, then assert the rule's concrete state delta and terminal
   marker. Tooltip rendering is a separate visual observation, not a substitute for behavior.

Known-good live canary (2026-07-10): `Resonant Guard` has custom `Resonant`, verifies
`present=True`, then gains Block (`0 -> 7`) when played.

## Checklist

- [ ] `[CustomEnum]` static `CardKeyword` field in the mod root namespace
- [ ] optional `[KeywordProperties]` position chosen intentionally
- [ ] `card_keywords.json` has prefixed `.title` + `.description`
- [ ] host Card attaches the exact generated field
- [ ] named behavior is implemented separately from display
- [ ] Type Canary build/load and Scenario Canary membership + state delta both pass
