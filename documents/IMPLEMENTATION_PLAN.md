# Implementation Plan: current execution

> Active plan after the M6 gameplay/programming core. Completed milestone detail and the
> previous full blueprint are archived in `history/IMPLEMENTATION_PLAN_THROUGH_M6.md`.

## Status

**M0-M6 gameplay/programming gates are complete. Direct next: M6 Art Expansion. M7 follows
after the new M6 content surfaces have grounded, honest art/presentation contracts.**

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

## M6 Art Expansion: direct next

M5.5 proved source-independent acquisition, normalization, placement, packaging, and live
visual inspection for four static families: card portraits plus relic/power/potion icons.
It does not cover the content families introduced by M6.

### Research inventory

Ground the real STS2/BaseLib asset and host contract for each surface before changing the
runtime skill:

| Surface | Current fallback | Research target |
|---|---|---|
| keyword / enchantment / orb | tooltip behavior, provisional icon/sprite | whether each owns a bitmap, atlas entry, material, or scene; exact path/size/render host |
| monster + encounter | built-in fallback creature | monster scene and Spine skeleton/atlas/animation requirements |
| event / World Node | verified vanilla portrait | custom portrait/scene ownership, dimensions, path, and room rendering lifecycle |
| character Foundation | template/built-in visuals | select icons, portraits, combat scene, Spine/animation, and any character frame assets |
| resource / ordered buffer UI | generic fallback Label | grounded native or open-mod-owned visual host, layout, lifecycle, and cleanup |

This is maintainer research: decompile/query the pinned game and BaseLib as needed, but do
not make runtime `/modmaker` sessions inspect local game assemblies.

### Implementation order

1. Extend the capability graph with exact asset registration, host, fallback, and proof for
   every M6 family.
2. Group by real asset shape rather than content name: static bitmap/icon first, then
   packed UI/scene assets, then Spine/animated actors.
3. Reuse `acquire_sprite.py` and `gen_sprite.py import` only where their bitmap contract
   actually fits. Add a new normalizer/spec only after the target format is grounded.
4. Wire source skill routing only after one type-matched hosted proof; regenerate plugin and
   portable payloads after source changes.
5. Preserve explicit fallback behavior for unsupported dynamic formats. Never present a
   vanilla/template fallback as generated custom art.

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

## M7: proactive interview for non-programmers

M7 is the next product milestone after M6 Art Expansion, not the direct current task.

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
