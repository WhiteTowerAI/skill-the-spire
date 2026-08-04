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

M7 Design Intelligence and User Experience is selected for planning. It has no implemented
source Package or release claim yet. M7 improves authoring quality and workflow without
changing the current RitsuLib/runtime capability boundary.

## User Experience

The desired interaction is:

```text
plain-language idea
  -> infer fast / co-design / revision route
  -> load only the relevant STS2-native design grammar
  -> adaptive clarification when a real design decision is missing
  -> DESIGN.md (intent, trade-offs, tuning, vision, current slice)
  -> semantic SPEC.md
  -> pinned scaffold and grounded recipes
  -> author and package
  -> real-game load proof
  -> hosted behavior proof or an honest manual boundary
  -> human playtest feedback and bounded design revision
```

The skill should preserve unusual mechanics instead of flattening them to the nearest easy
effect. It should recommend concrete defaults, avoid jargon, and tell the user when an idea
crosses the supported boundary. It should not ask the user to supply facts the pinned game
baseline can answer. A simple Card remains a fast interaction; a Character, content set, or
ambiguous mechanic receives deeper design help only where needed.

## Architecture

The product has three layers:

1. `modmaker` owns the staged workflow and resumable project state. Today that state is
   `SPEC.md`, `PLAN.md`, and `MEMORY.md`; M7 plans to add `DESIGN.md` before the semantic
   contract.
2. `sts2-api` owns lazy, grounded game knowledge: recipes, lifecycle contracts, art
   consumers, official-product-semantics distillations, verification hosts, and error
   fixes.
3. Python tools own deterministic scaffold, profile validation, build/package, launch,
   log parsing, and sprite normalization.

The semantic contract stays framework-neutral. RitsuLib details are concentrated in the
pinned scaffold/profile and the adapter/reference surface. Generated source is preferred
over a shared open-mod runtime until multiple independent consumers justify a versioned
binary.

The planned M7 artifact boundary is:

- `DESIGN.md`: player fantasy, pillars where useful, core decisions, rejected alternatives,
  system relationships, tuning knobs, open questions, future vision, and the currently
  deliverable slice;
- `SPEC.md`: only the exact framework-neutral operations the generator must build now;
- `PLAN.md`: execution-stage status;
- `MEMORY.md`: resolved technical identities, API choices, build facts, and repair history.

STS2 design grammar is separate from API grammar. It records checked native patterns such
as Character starter-deck composition, Basic Card naming/tags, archetype teaching cards,
rarity/upgrade relationships, and content-set roles. It must distinguish pinned facts,
observed conventions, and user-owned creative choices rather than converting every common
pattern into a hard rule.

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

M7 authoring quality is verified before runtime generation with behavioral prompt cases and
semantic artifact rubrics. Those checks evaluate question economy, decision preservation,
trade-off quality, native-design grounding, deliverable-slice honesty, and design-to-SPEC
traceability. They do not treat one preferred sentence or an AI-simulated player response
as proof. Real-player observations remain human-owned evidence.

## Distribution

The Codex plugin manifest is `plugins/open-mod/.codex-plugin/plugin.json`; the repo-local
marketplace is `.agents/plugins/marketplace.json`. Both skills and their tools are bundled
inside the plugin with relative paths, so installation is independent of the user's current
workspace.

The portable payload at `skills/` follows the Agent Skills layout. Both payloads are
generated from `games/sts2/` and committed because installers consume repository content
directly.

Generated projects keep the exact `0.5.4` Compat package as their reproducible compile
input while reusing a complete user NuGet cache across Codex sandbox identities. At
runtime, build preflight uses a validated game-local RitsuLib first or official Steam
Workshop item `3747602295` when local installation is absent; it accepts a newer framework
release only when the exact `0.107.1` variant contract remains intact.

## Product Boundaries

The current product supports the surfaces in
`games/sts2/tests/content-capability-graph.md`. The M6.7.0 grounding kernel identifies and
validates pinned vanilla targets, and the authoritative source now emits the promoted
M6.7.1 public Card, M6.7.2 complete public visual, M6.7.3 existing-Ancient, M6.7.4
availability, and M6.7.5 non-Card data/behavior override Packages. Generated plugin/
portable payloads are synchronized with that source. The human lead ended M6.7 source
development at M6.7.5 on 2026-08-03, canceled M6.7.6, and closed the milestone on
2026-08-04 after the independent representative acceptance passed. Multiplayer vanilla
overrides are future work outside this milestone. See
`documents/history/M67_VANILLA_OVERRIDES_RESULTS.md` for the literal result and unrun paths.
The post-acceptance generation-quality repair that blocks silent Card-description
downgrades and compile-checks per-file imports is recorded in
`documents/history/M67_POST_ACCEPTANCE_GENERATION_QUALITY_REPAIR.md`; it does not reopen the
milestone.
The current product does not imply arbitrary patching, retained-card zones, alternative
Energy, multiplayer UI, Spine/production Character motion or audio, behavior-bearing
arbitrary Event layouts beyond exact packaged public visual resources, or Workshop
publishing.

M7 may describe a larger future Mod vision, but it cannot promote any item in that vision
into `SPEC.md` without an existing supported route. General game-design research, CCGS
patterns, comparison projects, or vanilla analogies do not expand runtime support.

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

M6.7 is the closed milestone for version-bound overrides of existing vanilla content. Its
product goal is broader than numeric Card balance: generated Mods may eventually adjust
data and upgrades, alter acquisition/pools, compose behavior, or replace a grounded behavior
entry point while preserving the vanilla model identity and untouched assets. A pinned
version catalog, semantic override manifest, checked RitsuLib capability/adapter routes,
conflict diagnostics, and proportional real-host evidence are required before any category
is implemented. Support follows the same tutorial-plus-public-API rule as the rest of the
project; arbitrary prompt-generated Harmony/reflection/IL is not part of the design.

M6.7.0 source development implements that grounding kernel for STS2 `0.107.1`: a runtime
`ModelDb` collector, offline PE metadata collector, checked 1624-model catalog, exact internal and localized
display-title alias resolver across 14 pinned languages, semantic manifest and
expected-baseline/adapter/conflict validation, scaffold/build/deployment
wiring, and fail-closed diagnostics. Repeated localized-title collection passed its
collector-only literal checks. The current-catalog headed no-op remained intentionally
unrun. At closure, the full regression passed, generated payloads synchronized repeatably,
and a fresh nonempty Mod built from the reinstalled plugin in an independent workspace.
The human lead then reported that its representative in-game effects passed. Tier 1, Tier
2/SelfTest, and unselected routes remain explicit exceptions rather than passes.
The catalog now has 4165 reviewed, fingerprinted Adapter targets: the previous twenty plus
4145 M6.7.5 targets. It promotes five operation Packages.
`m6.7.1-public-card-overrides` covers the grounded non-asset public Card contributors,
capability-owned variables, and public play/owner-hook composition. Canonical DynamicVar
edits, base-description replacement/removal/hiding, destructive metadata edits, acquisition,
and transform carry-over remain outside that Package. Such description intent stops before
SPEC unless the user explicitly accepts before/after composition. `m6.7.2-public-visual-overrides`
covers all 44 public RitsuLib `0.5.4`
Card-material and external-asset providers across the 12 catalog target families that have
such a route. It checks exact Mod-local Material/texture/PackedScene/Spine/directory/list
resources, preserves vanilla fallback, rejects path/resource alternatives on one surface,
and records process-wide provider cleanup/cross-Mod conflict limits. RitsuLib exposes no
external vanilla Monster-body provider. Focused manifest/resource tests pass. Its earlier
Package-specific C# compile remained unrun, while the consolidated acceptance built and
included selected Card and Darv visual providers; the human lead accepted the Mod as a
whole, so no individual-provider observation is inferred.
`m6.7.3-existing-ancient-overrides`
covers the nine pinned native
Ancients through public multi-option append or one fixed complete initial-option replacement
Adapter. It includes nested conditions, visible/locked rules, fixed Gold/HP/Max HP costs,
typed Hover Tips and relic-backed presentation, ordered deterministic effects, deck
upgrade/remove/transform/enchant selection, fixed custom rewards, Mod-owned subsequent
pages, native `Done()` finish/choice history, full shipped-language `events.json`, and
separate M6.7.2 visual composition. The replacement and protected page/finish calls are the
three Ancient Adapter targets and fail closed on IL drift; `TheArchitect` is rejected
because it is an ordinary Event in `0.107.1`. Focused manifest/localization/catalog tests
pass. The consolidated Mod included one Darv replacement/page/portrait route and was
accepted as a whole; no individual-route observation is inferred, and other Ancient routes
remain unrun. `m6.7.4-availability` is the fourth promoted
Package. It covers the 57 pinned
public epoch IDs for Card, Character, ordinary Event, and shared `EVENT.DARV`, Relic/Potion
epoch or permanent-disable filters through fixed six-dependency Adapters, and Card/Relic/
Potion pool add/remove/move routes. Pool baselines are simulated in manifest order, require
the pinned primary pool, preserve existing instances, reject debug/empty transitions, and
are singleplayer-only. Focused manifest/catalog/document-route tests pass; representative
pool-move behavior was included in the consolidated Mod that was accepted as a whole. No
individual-route observation is inferred. Cache
timing, unlock UI, fresh-acquisition ordering/RNG, duplicate absence, and existing-save
variants remain unrun. `m6.7.5-non-card-data-behavior` is the fifth promoted
Package. It covers seven public typed owner-capability families with every pinned public
effect/numeric/decision hook and the four typed Orb callbacks, sixteen intrinsic data
routes, complete checked lifecycle/body replacements, Monster move graphs, paired
Encounter rosters, and ordinary Event options/pages. All operations are singleplayer.
Affliction synchronous apply/remove callbacks may only be suppressed with empty generated
effect lists; async `OnPlay` and owner hooks remain supported. Focused 40-test manifest/
catalog/localization/documentation checks and Python syntax pass. The consolidated Mod
included selected Relic, Monster, and Encounter routes and was accepted as a whole; no
individual-route observation is inferred, and unselected owner/lifecycle families and
ordinary Event routes remain unrun. The full regression and
payload synchronization passed at milestone closure. Other nonempty vanilla operations
remain rejected until a later Package promotes their grounded route.

M6.7 development stops at those five operation Packages. Multiplayer promotion is not a
sixth M6.7 Package; it remains a separate future systems track requiring identical peer
manifests, deterministic synchronized state/RNG, save/load, remote presentation, and
disconnect handling before any operation family can be promoted.
