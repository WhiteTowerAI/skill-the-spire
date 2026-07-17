# Implementation Plan: current execution

> Active plan after the M6 gameplay/programming core. Completed milestone detail and the
> previous full blueprint are archived in `history/IMPLEMENTATION_PLAN_THROUGH_M6.md`.

## Status

**M0-M6 gameplay/programming gates are complete. Direct next: M6 Static Art Expansion.
M7 follows after the new M6 content surfaces have grounded, honest static art/presentation
contracts. Animation is a later, non-blocking expansion.**

The current pipeline supports the bounded surfaces listed in `../AGENTS.md` and
`../games/sts2/tests/content-capability-graph.md`. The player-found Wayfinder correction is
part of the current boundary: ordered card mechanics store semantic values while source
cards use native result piles. Retained-card custom zones are not supported.

## Product direction

open-mod should feel like a knowledgeable collaborator for a beginner:

- accept a one-line idea without requiring programming vocabulary;
- ask only the few follow-ups that materially affect the result;
- offer a concrete default with each question;
- preserve unusual mechanics instead of flattening them to the nearest easy effect;
- build and observe the result in the real game;
- report unsupported seams honestly.

The project remains one game deep before extracting a multi-game platform.

## Runtime architecture

```text
natural-language idea
  -> interview
  -> semantic SPEC.md
  -> game-pack recipe/capability selection
  -> scaffold + generated domain code
  -> build/package
  -> Tier 1 load proof
  -> hosted Tier 2 state proof
  -> bounded repair
```

Files are state: `SPEC.md`, `PLAN.md`, and `MEMORY.md` allow resume after context
compaction. The game pack is runtime knowledge; live decompilation remains maintainer-only.

BaseLib/public commands are the default. A non-public adapter is eligible only when the
pack records its exact version/fingerprint, conflict/failure behavior, and hosted proof.
Do not create `OpenMod.Runtime` until multiple independent current consumers justify a
shared boundary.

## Verification architecture

Verification is organized by cost and host, not by a requirement to create one project per
capability.

### Contract checks

Use lightweight tests/assertions for deterministic logic such as formulas, capacity,
payment floors, and reset rules. Do not start the game merely to re-prove pure arithmetic.

### Hosted live suites

Reuse the nearest existing host:

| Host | Owns |
|---|---|
| `CombatPlayer` | card/relic/potion/power, keywords, enchantments, orbs, cadence |
| `CombatEnemy` | monster/encounter and move vocabulary |
| `MapNode` | events and real option UI |
| `RunStart` / Character | character selection, pools/starters, resource/UI, ordered semantic buffers |

A separate project remains allowed when it is simpler or isolates a genuinely different
host/toolchain risk. There is no hard project limit. Prefer extending the owning suite over
copying scaffold/harness code.

### Acceptance runs

Fresh natural-language mods prove the full pipeline. They are not permanent regression
fixtures by default. After durable evidence is recorded, one-off sources and installed
copies may be removed; the canonical hosted suite remains.

### Presentation rule

If open-mod takes ownership of UI, animation, card placement, or cleanup, player-visible
state is part of the proof. Model state alone cannot advance support. Prefer native game
lifecycle plus semantic state over custom presentation ownership.

## M6 Static Art Expansion: direct next

M5.5 proved source-independent acquisition, normalization, placement, packaging, and live
visual inspection for four static families: card portraits plus relic/power/potion icons.
The first M6 Static Art Expansion slices added the normal event initial portrait, enchantment
icon, and keyword presentation proof. Event proof covers one opaque 3440x1613 PNG, checked
vanilla fallback, real `%Portrait` path/size, headed screenshot, and strict `MapNode` Tier 2.
Enchantment proof
covers one transparent 64x64 PNG, checked missing-icon fallback, the same custom path in
the real card tab and hover tooltip, headed screenshot, preserved Block behavior, and
strict `CombatPlayer` Tier 2. Keyword proof covers `AutoKeywordPosition.After` text on the
real hand card, localized hover title/description, an intentional null tooltip icon, headed
screenshot, and preserved Block behavior. It adds no bitmap or `gen_sprite.py` spec. All
three passed on 2026-07-17. The orb slice then promoted one transparent 100x100 icon: the
same custom path rendered in the real smart tooltip and trigger flash, while the persistent
body remained the explicit Frost Spine scene/channel-SFX fallback. Passive/evoke behavior
stayed Block `0 -> 2 -> 7`, strict `CombatPlayer` Tier 2 passed, and custom Spine scene
generation is assigned to the later animation expansion. The monster slice then promoted
one transparent 360x360 static body through BaseLib's `NCreatureVisuals` factory. The same
custom path rendered in combat and a real default bestiary layout with non-Spine 396x396
bounds, correct floor/intent placement, and no crop; the full two-cycle behavior proof
remained green with no fresh error. Missing art uses the explicit built-in scene fallback.
Direct next after this completed monster slice: curate the Event reference pool and finish
the remaining static event portrait/layout sub-surfaces, followed by character static
assets and then richer character-mechanic UI.

### Research inventory

Ground the real STS2/BaseLib asset and host contract for each surface before changing the
runtime skill:

| Surface | Current fallback | Research target |
|---|---|---|
| keyword | live text-only card/tooltip presentation; no bitmap/icon | maintain auto-positioned card text plus localized no-icon tooltip across generated mods |
| enchantment | custom 64x64 icon; missing-icon fallback | maintain the shared card-tab/tooltip consumer contract across generated mods |
| orb | custom 100x100 tooltip/flash icon; Frost Spine scene/SFX fallback | no remaining M6 static work; custom body is later animation expansion |
| monster + encounter | custom 360x360 static combat+bestiary body; built-in scene fallback | maintain checked factory/fallback and no-animation boundary |
| event / World Node | custom normal initial portrait; vanilla fallback | remaining static phobia/later-page portraits and custom/Ancient layouts; animated VFX later |
| character Foundation | template/built-in visuals | select icons, portraits, static combat body, backgrounds, and frame assets; animation later |
| resource / ordered buffer UI | generic fallback Label | grounded native or open-mod-owned visual host, layout, lifecycle, and cleanup |

This is maintainer research: decompile/query the pinned game and BaseLib as needed, but do
not make runtime `/modmaker` sessions inspect local game assemblies.

### Implementation order

1. Extend the capability graph with exact asset registration, host, fallback, and proof for
   every M6 family.
2. Group by real asset shape rather than content name: static bitmap/icon first, then
   non-animated packed UI/scene assets. Do not open animation work in M6.
3. Reuse `acquire_sprite.py` and `gen_sprite.py import` only where their bitmap contract
   actually fits. Add a new normalizer/spec only after the target format is grounded.
4. Wire source skill routing only after one type-matched hosted proof; regenerate plugin and
   portable payloads after source changes.
5. Preserve explicit fallback behavior for unsupported dynamic formats. Never present a
   vanilla/template fallback as generated custom art.

The optional host-native acquisition edge (`runtime-imagegen`; Codex `image_gen`) applies
only to the eight live static specs: card, relic, power, potion, enchantment, orb icon,
monster body, and the normal event initial portrait. It produces a local source file and reuses `gen_sprite.py import`; it does not
advance any other M6 art family. Detect the callable tool itself rather than a model name
or installed skill file, and keep the placeholder when the tool is absent or fails. A
universal native-tool claim still requires acceptance on the specific first-party runtime
surface.

Reference-capable acquisition now has separate real-game pools for card, relic, power,
potion, enchantment, orb, and monster. The tools select by `--spec` and randomly sample
three distinct images; monster's fixed pool is Axebot, Ceremonial Beast, and Crossbow Ruby
Raider. Enchantment, orb, and monster also own independent, source-observed prompt
templates rather than inheriting Card composition. Event remains the only live static spec
without a bundled type-matched reference pool.

The ignored local baseline at
`baselines/spire-codex/backend/static/images/events/` currently contains 56 canonical,
deduplicated wiki.gg PNGs plus a download manifest. These are research candidates, not
shipped pipeline samples: the Event slice must review their contracts and attribution,
then promote only the appropriate pool into `reference/art-samples/event` before wiring
three-reference sampling or claiming Card-level acquisition maturity.

A three-image `seedream-5.0-lite` acceptance on 2026-07-17 exercised those pools and prompts
for an enchantment, orb, and monster. All three produced visually type-appropriate exact-size
RGBA previews. The orb exposed nonuniform chroma debris, so the new three cut-out profiles
now apply centered-subject fragment cleanup before their final fit. This advances acquisition
quality only; the prior headed game proofs remain the support evidence for real consumers.

### Verification and exit bar

- Assert exact source dimensions/format and final `res://` path or scene reference.
- Rebuild the `.pck` and enter the existing real host (`CombatPlayer`, `CombatEnemy`,
  `MapNode`, or Character).
- Capture headed visual evidence and, where possible, a resource/node assertion that proves
  the intended custom asset rendered instead of the fallback.
- Reuse hosted suites; a separate project is allowed when it isolates a genuinely distinct
  scene/toolchain risk, with no numerical project limit.
- Finish with every M6 surface either pipeline-supported for art or explicitly deferred with
  a grounded blocker and verified fallback. Do not leave a provisional claim ambiguous.
- Animation is not an M6 exit requirement. Keep every animation-bearing surface on its
  current fallback and list it under the later expansion.

## M7: proactive interview for non-programmers

M7 is the next product milestone after M6 Static Art Expansion, not the direct current task.

### Experience goal

The interview should proactively help a beginner think through:

- trigger and lifecycle;
- edge cases and failure behavior;
- balance-relevant tradeoffs;
- interactions with authored elements and the base game;
- future extension points;
- archetype identity and run rhythm for character-scale requests.

Ask one or two relevant questions at a time in plain language. Offer a recommended default.
Do not turn the one-line fast path into a questionnaire.

### Interaction ladder

1. **Technical dependency:** one element creates/applies/consumes another.
2. **Resource loop:** generation and spending create a meaningful choice.
3. **Archetype identity:** multiple elements reinforce a recognizable play pattern.
4. **Run rhythm and risk/reward:** the design changes decisions across fights and rewards.

Levels 3-4 are now unblocked by M6 Character support. The Wayfinder player run is the
first design-advisor lesson: a working state machine is not enough when the player cannot
read or choose within the mechanic.

### M7 implementation sequence

1. Extract applicable design questions from `BASELINE_RESEARCH.md` into a compact,
   queryable game-pack reference.
2. Update interview routing so element/host inference happens before questions.
3. Add concern selection: raise only concerns that apply to the current SPEC.
4. Offer defaults and preserve the one-line fast path.
5. Add character-scale questions for resource loop, archetype identity, and run rhythm.
6. Run beginner-oriented acceptance sessions and measure question count, corrections, and
   whether the generated SPEC captures the user's actual intent.

### M7 acceptance bar

- A simple relic/card request still reaches SPEC after at most one short clarification.
- A multi-element request records directed interactions and independently observable
  consequences.
- A character request receives relevant resource/archetype/rhythm guidance without asking
  every possible question.
- The interview surfaces lifecycle/presentation choices when custom zones or remembered
  state are implied.
- Generated SPECs preserve unsupported ideas as explicit gaps rather than silent
  simplifications.
- At least one beginner acceptance run completes build + Tier 1 + Tier 2 with no manual
  code editing.

## Later work

### Animation expansion

Animation is deliberately postponed and does not block M6 or M7. Its scope is custom orb
Spine bodies; monster skeleton/atlas and attack/hurt/cast/death/phobia/bestiary previews;
character combat animation, trails, and animated select transitions; event portrait VFX
or animation-bearing layouts; and optional UI motion. Until this expansion is opened,
static art or the documented built-in/template fallback is the supported result.

M6 Extras remain non-blocking and should be added by user value and host reuse:

- reward;
- rest-site option;
- pet/owned entity;
- run configuration/save choice;
- Act (separate ecosystem-sized milestone).

Other deferred work after the art-coverage decisions: retained-card zone UI,
alternative-energy hooks, vanilla editing, macOS/Linux live verification, registry
discoverability, and Workshop publishing.

## Publish and regression

After source changes:

```bash
./publish.sh --plugin
./publish.sh --portable
python -m unittest discover -s games/sts2/tools/tests -p "test_*.py"
python -m compileall -q games/sts2/tools scripts/publish \
  plugins/open-mod/tools skills/modmaker/scripts
git diff --check
```

Generated payloads must be idempotent and obey their placeholder/path contracts.
