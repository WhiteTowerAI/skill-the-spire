# AGENTS.md

Repository guidance for coding agents working in open-mod.

## Project

open-mod is a free, open-source Codex plugin that turns a non-programmer's description
into a working game mod. The current target is Slay the Spire 2 (STS2). The strategy is
one game deep, then a reusable platform.

Read `documents/IMPLEMENTATION_PLAN.md` before substantive work. Completed evidence lives
under `documents/history/` and is not current instruction.

## Current Status

`0.6.0` is the unreleased RitsuLib-only development baseline for STS2 stable `0.107.1`
and RitsuLib `0.5.4`. The BaseLib-to-RitsuLib migration and external clean-workspace
Codex acceptance are closed; details live in
`documents/history/RITSULIB_MIGRATION_RESULTS.md`. R7 was canceled by the human lead and
did not pass.

The focused M6.5 Character art, theme, outline, and bounded combat-cue packages are
implemented. The fresh Prismwright acceptance is closed and retired by explicit
human-lead decision; its headed result and waived Tier 2 harness are recorded in
`documents/history/M65_FRESH_ACCEPTANCE_RESULTS.md`. Do not reopen that proof, start M7, or
prepare/claim a GitHub release without later lead instruction.

M6.6 is closed by explicit human-lead decision. Package 2A computed Card values,
Package 5 custom-Character dialogue in native Ancient scenes, the bounded Package 1
advanced creature-targeting slice, and the bounded Package 3 Relic-owned Rest Site option
slice are implemented in the generation pipeline. Package 1 supports single-target Cards,
single-target Potions, and multi-target Cards; custom multi-target Potions have a pinned
lifecycle limitation. Package 3
supports singleplayer Relic-owned options with free/fixed Gold, deterministic outcomes,
once-per-site/run repeatability, native stay/leave behavior, and checked custom/Heal-fallback
icons. Its human-led result, skipped log check, and strict Tier 2 exception are recorded in
`documents/history/M66_REST_SITE_OPTIONS_RESULTS.md`. Package 2B hand readability and
Package 2C Relic/Power corner-label authoring are implemented with bounded fixed-color hand
rules, up to three safe-corner Relic labels, and one top-left Power label. Their human-led
headed review and strict Tier 1 passed after the Power boundary was narrowed to fix crowded
row overflow; strict Tier 2 was not run. The result and exception are recorded in
`documents/history/M66_GAMEPLAY_READABILITY_RESULTS.md`. Intent corner-label authoring was removed
from M6.6 work by the human lead on 2026-07-30; Intent remains supported as part of the
public RitsuLib Extra Badges Package. Package 4 Custom Card Piles authoring is implemented
for the complete documented Package: combat/run scopes, headless/top-bar/bottom-corner/
ExtraHand styles, preset/custom anchors, public pile screens and view capabilities,
visibility/hotkeys, native Card movement, localization, and ExtraHand layout/manual play/
callbacks. Official RitsuLib `0.5.4` contains the native-Hand lifecycle repair missing from
`0.5.0`; the human lead accepted the focused unmodified-runtime result and promoted the
Package on 2026-08-02. The strict structured Tier 2 harness was waived, not run. Historical
and official-version proof records remain under `documents/history/` and
`games/sts2/experimental/card-pile-extra-hand/`.

M6.7 is closed by explicit human-lead decision on 2026-08-04. It delivers version-bound
vanilla content overrides and behavior composition. M6.7.0 implements the grounding
kernel: the pinned `0.107.1` catalog contains 1624 vanilla models, checked title table/key
metadata plus localized display-title
aliases in all 14 pinned languages and exact assembly identity. M6.7.1
Public Card Overrides source development is implemented as the first promoted operation
Package, covering the grounded non-asset Card contributors and public behavior composition.
M6.7.2 Public Visual Overrides source development is also implemented as the second promoted
Package. It covers all 44 public RitsuLib `0.5.4` Card-material/external-asset providers
across Card/CardPool, Relic, Power, Potion, Orb, Act, Event/Ancient, Encounter, Affliction,
Enchantment, and Modifier targets, with exact Mod-local resources, typed/path alternatives,
fallback, cleanup, and same-surface conflicts. There is no vanilla Monster-body external
provider. Focused manifest/resource tests pass; a representative M6.7.2 C# compile was not
run in the sandbox. M6.7.3 Existing Ancient Extensions source development is implemented as
the third promoted Package. It supports public multi-option append and one fixed,
fingerprinted complete initial-option replacement Adapter for the nine pinned native
Ancients, plus Mod-owned subsequent pages, nested conditions, fixed Gold/HP/Max HP costs,
typed option presentation, deterministic effects, deck selections, fixed custom rewards,
native `Done()` choice history, and separate M6.7.2 visual composition. Three reviewed
Adapter targets fail closed on IL drift. `TheArchitect` is an ordinary Event in `0.107.1`
and is rejected by the Ancient routes. Focused manifest/localization/catalog tests pass;
one Darv replacement/page/portrait route was included in the consolidated Mod that the
human lead accepted as a whole; no individual-route observation is inferred, and unselected
Ancient behaviors and presentation paths remain unrun.
M6.7.4 Existing Vanilla Availability source development is implemented as the fourth
promoted Package. It supports the public 57-epoch gate for vanilla Cards, Characters,
ordinary Events, and shared `EVENT.DARV`; Relic/Potion epoch or permanent-disable filters
through six-dependency fixed Adapters; and Card/Relic/Potion pool add plus fixed
remove/move membership Adapters. Pool edits preserve vanilla model identity and existing
instances, require the pinned primary pool, reject debug/empty transitions, and are
singleplayer-only. Focused manifest/catalog/document-route tests pass. One representative
pool move was included in the consolidated Mod that the human lead accepted as a whole;
no individual-route observation is inferred, and unselected cache timing, unlock UI,
fresh-reward ordering/RNG, duplicate, and existing-save paths remain unrun.
M6.7.5 Existing Vanilla
Non-Card Data and Behavior source development is
implemented as the fifth promoted Package. It covers seven typed owner-capability families
with all 100 asynchronous `AbstractModel` hooks, 26 numeric hooks, 28 decision hooks, and
four typed Orb callbacks; sixteen intrinsic data routes; complete Relic/Potion/Power/Orb/
Enchantment/Affliction lifecycle bodies; Monster move graphs; paired runtime/all-possible
Encounter rosters; and complete ordinary Event initial options plus Mod-owned pages. Public
owner hooks compose, while complete suppression/replacement uses checked `0.107.1`
Adapters. The catalog now contains 4165 reviewed Adapter fingerprints, including 4145 for
M6.7.5. Affliction `AfterApplied`/`BeforeRemoved` are synchronous and can only be suppressed
with empty effect lists; async `OnPlay` and owner hooks retain their full routes. Focused
40-test manifest/catalog/localization/documentation checks and Python syntax pass.
Representative Relic, Monster, and Encounter routes were included in the consolidated Mod
that the human lead accepted as a whole; no individual-route observation is inferred, and
unselected non-Card families and ordinary Event paths remain unrun. On 2026-08-03
the human lead declared the approved
M6.7.0-M6.7.5 source-development matrix complete and canceled M6.7.6; multiplayer vanilla
overrides moved to Future Outlook and are not part of M6.7. The final regression passed
`165/165`, synchronized payloads were repeatable and identical, the installed-plugin
independent Mod built successfully, and the human lead reported the in-game effects passed.
Tier 1, Tier 2/SelfTest, the current-catalog headed no-op, and all unselected paths remain
explicitly unrun. The durable result is
`documents/history/M67_VANILLA_OVERRIDES_RESULTS.md`. Record a documented public route or
fixed reviewed Adapter for each requested operation/category before implementation; never
generate ungrounded Harmony, reflection, or IL from a prompt.

## Dependency Contract

- Generated Mods target STS2 `0.107.1` and `STS2.RitsuLib.Compat.0.107.1` `0.5.4`.
- Runtime manifests depend only on `STS2-RitsuLib >= 0.5.4`.
- Generated Mods must not reference, package, or depend on BaseLib.
- Do not use Alchyr templates or restore historical BaseLib implementation snippets.
- `baselines/BaseLib-StS2` and `baselines/downfall` are offline historical research only.
- `baselines/STS2-RitsuLib` is the maintainer research checkout; generated Mods consume
  the pinned package/runtime profile instead of copying it.
- `baselines/SlayTheSpire2ModdingTutorials` is the official-tutorial product-semantics
  checkout pinned at `5a9110b`. It establishes intended use and documented feature-Package
  membership, not stable-version signatures; exact APIs still come from RitsuLib `0.5.4`.
- `baselines/Sts2-YuWanCard` is a same-game-version Character/content-depth research
  checkout pinned at `07d7daa`. Its gameplay and Character framework is self-built with
  Harmony/Publicizer; RitsuLib is optional settings UI only. Use it to inventory consumers
  and study product behavior, never as RitsuLib API authority or a source of shipped code,
  art, audio, Spine, shader, or other assets.

## Supported Boundary

Use one simple Package-level rule: when the official tutorials document a RitsuLib
feature's player-facing use and Package, and the needed public API exists in the pinned
RitsuLib/compat profile, all documented public consumers in that Package are supported.
They do not need separate support declarations, recipes, tests, or real-game proofs first.
Record a confirmed API or lifecycle problem as the smallest known limitation. Call a
feature unsupported only when the pinned profile has no documented public route, a required
public member is absent, or the only route requires forbidden Harmony, reflection,
Publicizer, or IL generation.

Missing recipes, validators, builds, Tier 1/Tier 2 runs, or headed reviews mean only that
implementation or verification is missing; state that directly. Do not add readiness levels
or evidence badges. Verification remains literal under the rules below, and skipped checks
or waivers remain exceptions rather than passes.

Surfaces open-mod currently generates include:

- card, relic, potion, power, keyword, enchantment, and orb;
- computed Card Damage/Block, Energy/Star icon counts, raw and amount-given typed Power
  values, and localized DynamicVar tooltips under one preview/execution formula;
- deterministic Mod-local live-creature filters for single-target Cards/Potions and
  multi-target Cards, with native mouse/controller selection and resolution-time checks;
- generated-Mod-local singleplayer top-X Scry with normal selection/discard history/hooks;
- monster + encounter and the complete grounded move vocabulary;
- Event / World Node outcomes, bounded rich text/VFX/native presentation, and one bounded
  solo Quest Card -> forced Event composition;
- playable Character Foundation, nine checked static art profiles, and bounded private
  `Idle`/`Attack`/`Hit`/`Dead` combat cues;
- custom-Character localization dialogue across the nine cataloged native Ancient and
  Architect scenes while preserving their native models, layouts, options, and outcomes;
- singleplayer Relic-owned custom Rest Site options with free/fixed Gold, deterministic
  preflightable outcomes, once-per-site/run use, native stay/leave behavior, and checked
  256x169 custom/Heal-fallback icons;
- stateful relic cadence, combat-only secondary resources, all-or-nothing payment, public
  fixed combat UI, and ordered semantic buffers using normal Play -> Discard.
- complete documented Custom Card Piles Package authoring across combat/run lifetime,
  headless/top-bar/bottom-corner/ExtraHand presentation, public screens/views/hotkeys,
  deterministic visibility, native Card movement, localization, and ExtraHand interaction.
- the M6.7.0 vanilla grounding kernel: checked `0.107.1` catalog, exact internal and
  localized-display-title alias resolver,
  empty semantic manifest, expected-baseline/fingerprint/conflict validation, and no-op
  scaffold/build/deployment wiring.
- M6.7.1 Public Card Overrides for type/rarity/target, appended tags, evaluated Energy/Star
  costs, conditional playability, result piles, title/description/type-text composition,
  hover tips, native gold/red glow, capability-owned variables, recipe-backed `OnPlay`
  before/after/replacement, and owner draw/discard/exhaust composition.
- M6.7.2 Public Visual Overrides for all 44 public Card-material/external-asset providers:
  exact vanilla Card/CardPool, Relic, Power, Potion, Orb, Act, Event/Ancient, Encounter,
  Affliction, Enchantment, and Modifier targets; Mod-local Material/texture/PackedScene/
  Spine/directory/list resources; deterministic raster normalization where an established
  `gen_sprite.py` role matches; typed/path fallback; same-surface conflicts; and cleanup.
- M6.7.3 Existing Ancient Extensions for the nine pinned `AncientEventModel` targets:
  public multi-option append or one fixed complete initial-option replacement; nested
  conditions, visible/locked rules, fixed Gold/HP/Max HP costs, typed Hover Tips and
  relic-backed presentation, ordered deterministic outcomes, deck upgrade/remove/
  transform/enchant selection, fixed custom rewards, Mod-owned subsequent pages, native
  finish/choice history, full shipped-language `events.json`, and separate M6.7.2 visuals.
- M6.7.4 Existing Vanilla Availability for pinned epoch gates and Card/Relic/Potion pool
  add/remove/move membership, with Relic/Potion fixed epoch/disable filters, complete
  baseline simulation, primary-pool checks, singleplayer scope, and existing-instance
  preservation.
- M6.7.5 Existing Vanilla Non-Card Data and Behavior for Relic/Potion/Power/Orb/
  Enchantment/Affliction/Monster public owner-hook composition; all pinned public effect,
  numeric, decision, and typed Orb callbacks; sixteen intrinsic data routes; complete
  checked lifecycle/body replacements; Monster move graphs; paired Encounter rosters; and
  ordinary Event options/pages with full shipped-language `events.json`.

Generated readability APIs include conditional Card Hand Glow, up to three safe-corner
Relic labels, and one top-left Power label from the RitsuLib Extra Badges family. Intent
remains a supported public Extra Badges consumer, but Intent authoring is not scheduled.

Preserve these important boundaries:

- Route stores semantic direction values, never retained played Card instances.
- A source Card follows STS2's normal result pile lifecycle.
- Scry is singleplayer and Mod-local; it is not a global interoperability service.
- Rest Site options are Relic-owned and singleplayer-only; Card/Modifier owners, variable
  or non-Gold costs, post-payment choices, arbitrary transactions, same-site repeat, and
  multiplayer remain unsupported.
- Custom Card Piles use official public RitsuLib APIs only. Generated Mods must not recreate
  the framework's native-Hand bridge, patch pile internals, or narrow the documented Package
  merely because a selected consumer lacks a focused proof.
- Pinned Affliction `AfterApplied()` and `BeforeRemoved()` are synchronous `void` methods.
  A complete M6.7.5 lifecycle replacement may suppress them only with empty generated
  effect lists; async `OnPlay` and public owner-hook composition remain available.
- The fixed Character resource control is 220x32 at offset 160 with a text fallback and
  must remain disjoint from native Energy.
- Custom locked-selection/map-marker presentation, new Ancient models, global native
  dialogue/room replacement, Ancient behavior outside the fixed M6.7.3 option/page/effect
  vocabulary, randomized outcome/RNG rewrites, special combat and direct merchant/rest/
  treasure transitions,
  production animation beyond the bounded cues, line audio,
  the custom multi-target Potion lifecycle limitation, global acquisition weighting,
  Card/Character/Event permanent disable without a reviewed route, behavior-bearing scene/material
  generation outside the promoted M6.7.2 resource routes, audio,
  remote-player UI, alternative Energy, retained-card zones, and one-click Workshop
  publishing retain their recorded boundaries. Outside the promoted M6.7.1 public Card,
  M6.7.2 public visual, M6.7.3 existing-Ancient, M6.7.4 availability, and M6.7.5 non-Card
  data/behavior routes, nonempty M6.7 operations are not generated until their delivery
  package records and promotes a documented public/fixed-Adapter route for the requested
  operation/category. Source-specific weighting and unpromoted disable surfaces remain
  unsupported. Multiplayer vanilla overrides are future work outside M6.7 and remain
  unsupported until a separately selected track promotes them.

For the exact active inventory, read
`games/sts2/tests/content-capability-graph.md`.

## Art Contract

`gen_sprite.py` is framework-neutral. RitsuLib `*AssetProfile` consumers or an exact
M6.7.2 external visual provider own runtime wiring. The verified Character profiles are
selection portrait/background, top-panel
main/outline icons, combat/rest/merchant static bodies, five full-energy layers, and
distinct large/text Energy icons. Optional combat cues are a private combat-only frame
set, not a profile-global animation replacement.

Host-native image generation is optional. Use it only when a callable raster tool returns
a local image. Do not infer availability from a text-model name or installed skill, and do
not silently select a paid backend. Every acquisition path converges on deterministic
`gen_sprite.py import` normalization and retains the supported fallback.

## Architecture

- `games/sts2/skills/modmaker/`: interview -> spec -> scaffold -> author -> build ->
  verify -> bounded repair.
- `games/sts2/skills/sts2-api/`: lazy recipes, references, and error catalog.
- `games/sts2/tools/`: cross-platform Python build/launch/log/art wrappers.
- `games/sts2/tests/`: current support graph and verification ownership.
- `games/sts2/experimental/`: repository-only implementation research excluded from formal
  skills and generated payloads.
- `plugins/open-mod/`: generated Codex plugin payload from `publish.sh --plugin`.
- `skills/`: generated portable Agent Skills payload from `publish.sh --portable`.
- `.agents/plugins/marketplace.json`: repo-local Codex marketplace entry.

Edit source under `games/sts2/`; never hand-edit generated payload contents. Regenerate and
validate both committed payloads after source changes. The M6.7 closure payloads were
synchronized from that source and accepted through the reinstalled plugin.

## Verification

Keep verification proportional:

1. Contract checks for deterministic calculations and state rules.
2. Reuse the closest hosted scenario (`CombatPlayer`, `CombatEnemy`, `MapNode`, or
   `RunStart`/Character) for live behavior.
3. For an ordinary feature or bug fix that affects generated-Mod behavior or presentation,
   stop after the changed behavior is proved in the nearest real game host. Reuse a
   maintained scenario when possible, or create one narrow disposable proof; do not run a
   complete demo Mod after every change.
4. Use a fresh natural-language acceptance Mod only when the current
   `documents/IMPLEMENTATION_PLAN.md` explicitly schedules a full-pipeline gate or the
   human lead asks for one. Record durable evidence, then retire the acceptance Mod.

M6.7 used a temporary milestone-level batching exception approved by the human lead on
2026-08-03 and closed on 2026-08-04 after one final source regression, synchronized
payloads, an independent installed-plugin build, and the lead's representative in-game
acceptance. Do not rerun that milestone gate or expand it into an exhaustive provider/hook
matrix. Preserve the unrun Tier 1, Tier 2/SelfTest, current-catalog no-op, and unselected
paths recorded in `documents/history/M67_VANILLA_OVERRIDES_RESULTS.md`.

Do not turn a focused change into an unscheduled end-to-end acceptance exercise. Local
documentation or tooling changes that cannot affect generated runtime behavior need only
the proportionate non-game checks. Historical evidence stays immutable: do not modify an
archived acceptance project or reopen a retired migration proof to test new work.

Verification does not decide Package support. Preserve exact Tier 1/Tier 2/headed wording
and record missing checks as exceptions even when the surrounding Package is supported.

Tests protect semantic behavior, generated artifacts, and dependency boundaries. Do not
assert exact adapter API symbols or recipe wording merely to prove that a recipe uses
RitsuLib rather than BaseLib; enforce that product contract at scaffold, build, manifest,
and runtime-package boundaries. Assert a specific symbol or phrase only when it is itself
a pinned compatibility or output contract.

Tier 1 requires the exact load marker and no fresh error block. Tier 2 requires a
structured post-state proof plus `selftest done`. Trigger logs and model-only state do not
prove behavior or presentation. Run one armed harness at a time and preserve unrelated
user Mods.

Current commands:

```powershell
python games/sts2/tools/scaffold.py --project-dir <outer-dir> --mod-name <ModName> --author <Author>
python games/sts2/tools/build.py --project-dir <outer-dir> --mod-name <ModName>
python games/sts2/tools/launch.py
python games/sts2/tools/grep_log.py --mod-name <ModName>
python games/sts2/tools/launch.py --self-test --mod-name <ModName>
python games/sts2/tools/grep_log.py --mod-name <ModName> --tier2-pattern "<structured proof>"
```

The outer project directory name must differ from the Mod name.

## Branch And Commits

- Work on `Henry's_cc`.
- Never merge or open a PR to `main`.
- `Henry's_branch` is snapshot-only; merge `Henry's_cc` into it only when asked.
- Preserve unrelated dirty-worktree changes.
- Wait to be asked before committing.
- Use Conventional Commits and an appropriate AI co-author trailer.
- Stage specific files, never `git add .`.

## Windows

The verified environment uses PowerShell, STS2 `0.107.1`, .NET SDK `9.0.300`, Python 3,
and RitsuLib `0.5.4`. Use PowerShell syntax for normal commands. Invoke `publish.sh`
through an explicit Git Bash executable when needed; do not mix Bash path syntax into
PowerShell commands.

## Active Documents

- `documents/PROJECT.md`
- `documents/IMPLEMENTATION_PLAN.md`
- `documents/BASELINE_RESEARCH.md`
- `games/sts2/tests/README.md`
- `games/sts2/tests/content-capability-graph.md`

Migration results are in `documents/history/RITSULIB_MIGRATION_RESULTS.md`.
