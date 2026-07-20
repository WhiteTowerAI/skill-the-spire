# Card and Standard Hover-Tip Rich Text

Card descriptions and the standard Card/relic/potion/power Hover Tips may use a bounded
subset of the rich text already authored by vanilla STS2. This is native presentation:
localization supplies balanced tags, SmartFormat resolves variables first, and the existing
`MegaRichTextLabel` consumers parse the result. Generated mods do not create labels,
effects, shaders, or Harmony patches for this feature.

## Supported vocabulary

The allowlist is per localization surface, based on the pinned vanilla English content:

| Surface | Authored tags | Native consumer |
|---|---|---|
| Card `.description` | `gold`, `purple` | real `NCard.%DescriptionLabel`, including `CardHoverTip` previews |
| Relic `.description` | `blue`, `gold`, `green`, `purple`, `red` | `HoverTipFactory.FromRelic` -> `NHoverTipSet.%Description` |
| Potion `.description` | `blue`, `gold`, `green` | `HoverTipFactory.FromPotion` -> `NHoverTipSet.%Description` |
| Power `.description` / `.smartDescription` | `blue`, `gold` | `HoverTipFactory.FromPower` and live Power tips -> `NHoverTipSet.%Description` |

Card SmartFormat formatters such as `{Damage:diff()}` may additionally emit `green` or
`red` when the preview value differs. Those colors belong to the formatter; do not wrap a
`:diff()` placeholder in another color or record its generated color as an authored span.
Auto-positioned custom-keyword text is composed after the base Card description and keeps
the existing localized no-icon keyword Hover Tip contract.

Keep titles, relic flavor, and selection prompts plain. Do not emit arbitrary Godot
BBCode, custom colors, tag parameters, motion tags, or raw markup supplied by the user.
Every authored tag must be balanced and nested in reverse closing order.

## Authoring contract

SPEC records intent, not literal markup:

```text
text effects: vanilla
text spans:
  description: "Block" -> gold
  description: "prismatic line" -> purple
```

At author time, validate every requested effect against the element's row above and apply
the matching tags only to the exact phrase. Preserve SmartFormat placeholders exactly.
If a requested color or effect is not allowed on that surface, retain it under
`presentation gaps` rather than moving it to a different phrase or inventing code.

For a custom Power, apply the same spans to `.description` and `.smartDescription` when
those strings are otherwise identical. A Card preview created by
`HoverTipFactory.FromCard` reuses the Card description and needs no separate tooltip text.

## Verification

Reuse `CombatPlayer`. One headed run may cover all consumers:

1. add the authored Card to the real hand and assert `%DescriptionLabel` is a
   BBCode-enabled `MegaRichTextLabel` containing the formatted spans plus any declared
   auto keyword;
2. focus the real holder and prove a typed Card preview plus typed relic, potion, and power
   Hover Tips reach their native rich-text description nodes;
3. capture the settled Card and tips together, then play the source Card and preserve its
   existing state proof;
4. require the strict state-proof marker, `selftest done`, and no fresh error block.

Live proof (`CanaryPresentation`, 2026-07-20): the real hand Card rendered authored
`gold`/`purple` spans and its auto-positioned `Resonant` text; an upgraded typed Card
preview rendered SmartFormat's green difference plus `gold`/`purple`; typed relic,
potion, power, and keyword tips rendered their per-surface colors in `NHoverTipSet`.
The same run preserved Block `0 -> 7`, saved headed evidence, passed strict Tier 2, and
had no fresh error.
