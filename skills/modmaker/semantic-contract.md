# SPEC authoring contract

`DESIGN.md` preserves human intent. `SPEC.md` is the only implementation work order: it says
exactly what to generate, which maintained routes support it, and how the real host will prove
it. Keep it readable by both the user and the authoring agent.

## What every current operation says

For each content element or existing-content change, write the applicable facts in ordinary
Markdown:

- name, content identity, surface, pool/registration/availability, ownership, and relationships;
- trigger, target, conditions, ordered effects, exact values, upgrades, calculation timing, and
  native result pile;
- state owner, transition timing, bounds, lifetime, reset, persistence, visibility, and consumers;
- exact English and Simplified Chinese player-facing text in the vanilla style of
  `reference/vanilla-text-style.md` (glossary terms, colors, line breaks, Chinese punctuation
  and measure words), including localization table/key intent, DynamicVar/SmartFormat names,
  variable parity, and hover tips for every named term;
- presentation, art choice, native consumers, and checked fallback;
- supported recipe/reference route;
- adapter outputs such as stable IDs, tables/keys, resources, and classes when known; and
- one or more autotest scenarios with a real host driver, exact post-state assertions, neutral
  or rejection cases, resets, and any headed observation that automation cannot establish.

Omit inapplicable fields rather than filling a generic schema with `none`. Do not put design
rationale, future ideas, verification outcomes, or stage status in SPEC.

## Implementation section

Every new or revised SPEC contains one short `## Implementation` section. It is both the
author's route list and the input to the one pre-Author machine check.

List each maintained route selected by the current work exactly once:

```markdown
## Implementation

- Support: `recipes/card.md`
- Support: `reference/card-computed-values.md`
```

For a model-hook participation, use the cataloged semantic capability, owning surface, catalog
shape, and the single maintained route:

```markdown
- Hook: modify_damage_multiplicative | surface: power | shape: value | route: reference/model-hook-participation.md
```

An operation with no maintained route adds one `- Mod-local: <operation> - <public
Owner.Member list>` line, grounded under `../sts2api/grounding.md` § Mod-local Routes.

The thin preflight fails a SPEC with no `Support`, `Hook`, or `Mod-local` line, requires each
`Mod-local` line to name a public `Owner.Member`, and otherwise checks only that each route
exists and that each Hook is cataloged, declared by its route, uses the catalog shape, is not
owned by another route, and can reach the selected surface. Do not add Markdown anchors: headings are documentation navigation, not capability
identity. An ordinary operation needs no invented capability ID.

## Surface and capability ownership

Read the selected recipe under `../sts2api/recipes/` for its exact SPEC fields,
authoring route, proof matrix, known limitations, and manual fallback. Use targeted `sts2api` references for the
selected operation. In particular:

- Card, Relic, Potion, Power, Orb, Enchantment, Monster/Encounter, Event, Character, Keyword,
  Affliction, Modifier, Global Effect, Rest Site, Act, Ancient, Reward, Card Pile, and Runtime UI
  inputs live in their matching recipe.
- Secondary resources use `reference/character-resource.md`.
- Computed Card values use `reference/card-computed-values.md`.
- Bounded state uses `reference/stateful-mechanics.md`.
- Standalone/Card/Relic/Modifier Rest Site options use `recipes/rest-site.md` and
  `reference/rest-site-options.md`.
- Quest Card forced Event mappings use `reference/forced-followup-event.md`.
- Custom Card Piles and Runtime UI use their matching recipes plus selected lifecycle references;
  advanced targeting, readability, Character presentation/dialogue/cues, vanilla overrides, and
  native Event presentation use their existing dedicated references.

For a multi-surface request, preserve each truthful owner and list every selected route once. Order
the implementation and SelfTest assertions by the real dependency flow; do not invent a combo
surface, collapse one owner's lifecycle into another, or use a deferred family as coordination.

The generalized variants remain supported. Write their full human-readable fields from the
owner page, including routes and hard boundaries, as ordinary Markdown.

## Pinned implementation boundary

Generated Mods target STS2 stable `0.107.1` and the RitsuLib `0.6.7` authoring/API baseline.
Scaffold pins the checked local compat and shared modules used to compile; the runtime manifest
floor remains `STS2-RitsuLib >= 0.6.7`. Generate only public RitsuLib routes or fixed reviewed
Adapters already documented by the pack. Never derive Harmony, reflection, Publicizer, or IL
from the prompt.

Framework class names, manifest structure, resource packing, and concrete API signatures belong
to the adapter, scaffold, recipe, and Build stages. The SPEC names their maintained route rather
than copying those details into another schema.

## Verification ownership

Build proves compilation, manifest/resource/localization/profile validity, and deployable
artifacts. Tier 1 proves the exact load marker with no fresh error block. Tier 2 proves behavior
only through a real STS2 host driver, structured post-state assertions, `selftest done`, and no
fresh error. Ordinary fired/used logs are diagnostics, not pass evidence. Mouse/controller UI,
animation, image framing, and subjective experience remain headed human observations when the
selected surface requires them.
