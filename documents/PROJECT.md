# open-mod project

## Product

open-mod gives non-programmers a credible path from one sentence to a working game mod.
It is a Codex plugin, not a web form or a code-snippet generator. The agent collaborates
with the user, records a semantic contract, writes the project, builds it, runs the real
game, and reports what was actually verified.

The first game is Slay the Spire 2. The project stays one game deep until the workflow and
support model are mature enough to extract a reusable platform.

## Release State

Version `0.6.0` is the first RitsuLib-only, externally accepted development baseline:

- host: STS2 stable `0.107.1`;
- compile package: `STS2.RitsuLib.Compat.0.107.1` `0.5.4`;
- runtime dependency: `STS2-RitsuLib >= 0.5.4`;
- primary runtime: Codex plugin;
- secondary distribution: portable Agent Skills payload.

BaseLib is no longer an implementation option. Historical BaseLib and Downfall checkouts
are offline research archives, not generated dependencies or runtime inputs.

The migration and clean-workspace Codex acceptance are complete; the migration record is
archived in `documents/history/RITSULIB_MIGRATION_RESULTS.md`. `0.6.0` remains unreleased
while user-test bugs are fixed. M6.5 closed through the lead-approved Prismwright headed
acceptance recorded in `documents/history/M65_FRESH_ACCEPTANCE_RESULTS.md`; no GitHub
release is currently planned.

## User Experience

The desired interaction is:

```text
plain-language idea
  -> one compact clarification round when needed
  -> plain-language plan
  -> semantic SPEC.md
  -> pinned scaffold and grounded recipes
  -> author and package
  -> real-game load proof
  -> hosted behavior proof or an honest manual boundary
```

The skill should preserve unusual mechanics instead of flattening them to the nearest easy
effect. It should recommend concrete defaults, avoid jargon, and tell the user when an idea
crosses the supported boundary.

## Architecture

The product has three layers:

1. `modmaker` owns the staged workflow and resumable project state (`SPEC.md`, `PLAN.md`,
   `MEMORY.md`).
2. `sts2-api` owns lazy, grounded game knowledge: recipes, lifecycle contracts, art
   consumers, official-product-semantics distillations, verification hosts, and error
   fixes.
3. Python tools own deterministic scaffold, profile validation, build/package, launch,
   log parsing, and sprite normalization.

The semantic contract stays framework-neutral. RitsuLib details are concentrated in the
pinned scaffold/profile and the adapter/reference surface. Generated source is preferred
over a shared open-mod runtime until multiple independent consumers justify a versioned
binary.

## Verification Philosophy

A documented RitsuLib feature Package is supported when the official tutorials establish
its player-facing use and its public API exists in the pinned profile. This applies to all
documented public consumers in the Package; confirmed defects become narrow limitations,
while only missing public routes are unsupported. Recipes and host runs tell us what the
generator currently implements and what we actually observed, not whether the Package is
supported.

Compilation is necessary but insufficient. Use the lightest proof that establishes the
changed invariant:

- local assertions for pure calculations;
- a hosted real-game scenario for lifecycle and behavior;
- visible evidence when open-mod owns presentation;
- a fresh natural-language Mod only for an explicitly scheduled end-to-end acceptance
  gate.

Tier 1 means loaded with no fresh error. Tier 2 means a structured post-state marker plus
`selftest done`. Record only the checks that actually ran; none is silently inferred from
another.

## Distribution

The Codex plugin manifest is `plugins/open-mod/.codex-plugin/plugin.json`; the repo-local
marketplace is `.agents/plugins/marketplace.json`. Both skills and their tools are bundled
inside the plugin with relative paths, so installation is independent of the user's current
workspace.

The portable payload at `skills/` follows the Agent Skills layout. Both payloads are
generated from `games/sts2/` and committed because installers consume repository content
directly.

## Product Boundaries

The current product supports the surfaces in
`games/sts2/tests/content-capability-graph.md`. It deliberately does not imply vanilla
editing, arbitrary patching, retained-card zones, alternative Energy, multiplayer UI,
Spine/production Character motion or audio, arbitrary Event layouts, or Workshop
publishing.

The focused M6.5 Character art and presentation packages are implemented:
role-based identity references without a separate Character sheet, corrected
selection/combat visible footprints, a structured card/UI theme, alpha-derived
Character/Relic outlines, one Character-specific Energy layer plus four fixed templates,
and geometry-stable non-Spine `Idle`/`Attack`/`Hit`/`Dead` combat cues. The fresh
natural-language Prismwright acceptance is closed with its explicit lead-approved
verification exceptions recorded in `documents/history/M65_FRESH_ACCEPTANCE_RESULTS.md`.
Characters keep the game-native shared map-marker fallback; locked selection, Character
card trails, and a `Cast` cue remain unsupported.

M6.6 is closed by explicit human-lead decision. Package 2A computed Card
values, Package 5 custom-Character dialogue in native Ancient scenes, Package 1 advanced
creature targeting, and the bounded Package 3 Relic-owned Rest Site option slice are
implemented. Package 1 covers single-target Cards, single-target Potions, and
multi-target Cards through deterministic Mod-local live-creature filters and native
mouse/controller selection; multi-target Potions have a pinned lifecycle limitation.
Package 3 covers
singleplayer Relic-owned options with free/fixed Gold, deterministic preflightable outcomes,
once-per-site/run repeatability, native stay/leave behavior, and checked custom/Heal-fallback
button art. Its human-lead acceptance, skipped log check, and omitted strict Tier 2 harness
are recorded in `documents/history/M66_REST_SITE_OPTIONS_RESULTS.md`.

Package 2B/2C authoring is implemented in the generation pipeline: Cards may declare
ordered fixed-color hand-emphasis rules with priority and explicit unplayable visibility,
Relics may declare up to three bounded supplemental labels in distinct safe corners, and
Powers may declare one top-left label with explicit refresh/removal. The Power boundary was
narrowed after multiple un-clipped preset bands overflowed an adjacent Power in the human
lead's crowded 16:9 row. The rebuilt proof passed the human-led 16:9/16:10 recheck and strict
Tier 1; strict Tier 2 was not run. The result is recorded in
`documents/history/M66_GAMEPLAY_READABILITY_RESULTS.md`. Package 4 Custom Card Piles is
implemented across the complete documented public Package on official RitsuLib `0.5.4`.
It includes combat/run scopes, all five UI styles, preset/custom anchors, public pile-screen
capabilities, visibility/hotkeys, native movement/localization, and ExtraHand layout/manual
play/callbacks. The human lead accepted the focused unmodified-runtime ExtraHand recheck;
strict structured Tier 2 was waived rather than run. Intent belongs to Extra Badges but was removed from M6.6
work by the human lead on 2026-07-30; current generated 2C authoring is Relic/Power only.
Optional Mod settings with Global/Profile/run-owned persistence remain future outlook
outside the closed M6.6 scope.

M6.7 is the planned follow-on for version-bound overrides of existing vanilla content. Its
product goal is broader than numeric Card balance: generated Mods may eventually adjust
data and upgrades, alter acquisition/pools, compose behavior, or replace a grounded behavior
entry point while preserving the vanilla model identity and untouched assets. A pinned
version catalog, semantic override manifest, checked RitsuLib capability/adapter routes,
conflict diagnostics, and proportional real-host evidence are required before any category
is implemented. Support follows the same tutorial-plus-public-API rule as the rest of the
project; arbitrary prompt-generated Harmony/reflection/IL is not part of the design.
