# Card and Standard Hover-Tip Extra Emphasis

Every Card, relic, potion, and power description already follows
`reference/vanilla-text-style.md`: glossary terms in `[gold]`, colored numbers on non-Card
surfaces, `\n` between Card effects, and native Chinese. That default needs no request.

This page covers only **extra** emphasis a user explicitly asks for beyond the default, such
as "make the word 'prismatic' purple". It is native presentation: localization supplies
balanced tags, SmartFormat resolves variables first, and the existing `MegaRichTextLabel`
consumers parse the result. Generated mods do not create labels, effects, shaders, or Harmony
patches for this feature.

## Supported vocabulary

The allowlist per surface is the vanilla set, owned by `reference/vanilla-text-style.md`:

| Surface | Authored tags | Native consumer |
|---|---|---|
| Card `.description` | `gold`, `purple`, `blue` | real `NCard.%DescriptionLabel`, including `CardHoverTip` previews |
| Relic `.description` | `blue`, `gold`, `green`, `purple`, `red` | `HoverTipFactory.FromRelic` -> `NHoverTipSet.%Description` |
| Potion `.description` | `blue`, `gold`, `green` | `HoverTipFactory.FromPotion` -> `NHoverTipSet.%Description` |
| Power `.description` / `.smartDescription` | `blue`, `gold` | `HoverTipFactory.FromPower` and live Power tips -> `NHoverTipSet.%Description` |

Card SmartFormat formatters such as `{Damage:diff()}` emit `green` or `red` when the preview
value differs. Those colors belong to the formatter; do not wrap a `:diff()` placeholder in
another color or record its generated color as an authored span. Auto-positioned
custom-keyword text is composed after the base Card description and keeps the existing
localized no-icon keyword Hover Tip contract.

Keep titles, relic flavor, and selection prompts plain. Do not emit arbitrary Godot BBCode,
custom colors, tag parameters, motion tags, or raw markup supplied by the user. Every
authored tag must be balanced and nested in reverse closing order; Build fails otherwise.

## Authoring contract

SPEC records extra emphasis as intent, not literal markup:

```text
extra emphasis:
  description: "prismatic line" -> purple
```

At author time, validate every requested span against the element's row above and apply the
matching tag only to the exact phrase. Preserve SmartFormat placeholders exactly. If a
requested color or effect is not allowed on that surface, retain it under
`presentation gaps` rather than moving it to a different phrase or inventing code. Extra
emphasis never removes a default highlight.

For a custom Power, apply the same spans to `.description` and `.smartDescription` when
those strings are otherwise identical. A Card preview created by `HoverTipFactory.FromCard`
reuses the Card description and needs no separate tooltip text.

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
