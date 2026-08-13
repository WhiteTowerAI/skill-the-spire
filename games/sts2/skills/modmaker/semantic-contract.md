# SPEC authoring contract

`DESIGN.md` preserves human intent. `SPEC.md` is the only implementation work order: it says
exactly what to generate, which maintained routes support it, and how the real host will prove
it. Keep it readable by both the user and the authoring agent.

## What every current operation says

For each content element or existing-content change, write the applicable facts in ordinary
Markdown:

- content identity, surface, registration/availability, and ownership;
- trigger, target, conditions, ordered effects, exact values, upgrades, and native result pile;
- state owner, transition timing, bounds, lifetime, reset, persistence, and visibility;
- exact English and Simplified Chinese player-facing text, including DynamicVar/SmartFormat
  names and token parity;
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

Use one line per maintained route selected by the current work:

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

The thin preflight checks only that each route exists and that each Hook is cataloged, declared
by its route, uses the catalog shape, is not owned by another route, and can reach the selected
surface. Do not add Markdown anchors: headings are documentation navigation, not capability
identity. An ordinary operation needs no invented capability ID.

## Surface and capability ownership

Read the selected page under `surfaces/` for its exact SPEC fields, authoring route, proof
matrix, known limitations, and manual fallback. Use targeted `sts2-api` references for the
selected operation. In particular:

- Card, Relic, Potion, Power, Orb, Enchantment, Monster/Encounter, Event, Character, and
  Keyword inputs live in their matching surface page.
- Secondary resources use `reference/character-resource.md`.
- Computed Card values use `reference/card-computed-values.md`.
- Bounded state uses `reference/stateful-mechanics.md`.
- Card- or Relic-owned Rest Site options use `reference/rest-site-options.md`.
- Quest Card forced Event mappings use `reference/forced-followup-event.md`.
- Custom Card Piles, advanced targeting, readability, Character presentation/dialogue/cues,
  vanilla overrides, and native Event presentation use their existing dedicated references.

The M8.7 generalized variants remain supported. Write their full human-readable fields from the
owner page, including routes and hard boundaries; do not recreate `open-mod-surface-data` or
`open-mod-surface-contract` JSON. Existing v1/v2/v3 projects may retain old blocks as ignored
legacy text and resume without migration.

## Pinned implementation boundary

Generated Mods target STS2 stable `0.107.1` and the RitsuLib Compat `0.5.11` authoring/API
baseline. Scaffold pins the checked local Compat DLL used to compile; the runtime manifest floor
remains `STS2-RitsuLib >= 0.5.11`. Generate only public RitsuLib routes or fixed reviewed
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
