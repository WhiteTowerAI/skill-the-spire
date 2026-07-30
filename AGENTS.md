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
and RitsuLib `0.4.62`. The BaseLib-to-RitsuLib migration and external clean-workspace
Codex acceptance are closed; details live in
`documents/history/RITSULIB_MIGRATION_RESULTS.md`. R7 was canceled by the human lead and
did not pass.

The focused M6.5 Character art, theme, outline, and bounded combat-cue packages are
implemented. The fresh Prismwright acceptance is closed and retired by explicit
human-lead decision; its headed result and waived Tier 2 harness are recorded in
`documents/history/M65_FRESH_ACCEPTANCE_RESULTS.md`. Do not reopen that proof, start M7, or
prepare/claim a GitHub release without later lead instruction.

M6.6 is the active provisional capability milestone. Package 2A computed Card values,
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
from active M6.6 work by the human lead on 2026-07-30; Intent remains supported as part of
the public RitsuLib Extra Badges Package. The combat-only singleplayer custom
CardPile/ExtraHand slice is the direct next development step but does not start until
selected. The package list may gain other lead-approved features.

M6.7 is the planned follow-on for version-bound vanilla content overrides and behavior
composition. Its intended scope includes data/upgrade/property edits, acquisition and pool
changes, behavior composition, and complete recipe-backed replacement across grounded
content categories. It does not start automatically after M6.6. Record a documented public
route for each requested operation/category before implementation; never generate
ungrounded Harmony, reflection, or IL from a prompt.

## Dependency Contract

- Generated Mods target STS2 `0.107.1` and `STS2.RitsuLib.Compat.0.107.1` `0.4.62`.
- Runtime manifests depend only on `STS2-RitsuLib >= 0.4.62`.
- Generated Mods must not reference, package, or depend on BaseLib.
- Do not use Alchyr templates or restore historical BaseLib implementation snippets.
- `baselines/BaseLib-StS2` and `baselines/downfall` are offline historical research only.
- `baselines/STS2-RitsuLib` is the maintainer research checkout; generated Mods consume
  the pinned package/runtime profile instead of copying it.
- `baselines/SlayTheSpire2ModdingTutorials` is the official-tutorial product-semantics
  checkout pinned at `5a9110b`. It establishes intended use and documented feature-Package
  membership, not stable-version signatures; exact APIs still come from RitsuLib `0.4.62`.
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
- The fixed Character resource control is 220x32 at offset 160 with a text fallback and
  must remain disjoint from native Energy.
- Custom locked-selection/map-marker presentation, custom Ancient models/backgrounds/
  layouts/options/rewards, production animation beyond the bounded cues, line audio,
  the custom multi-target Potion lifecycle limitation, arbitrary material/audio,
  remote-player UI, alternative Energy, retained-card zones, and one-click Workshop
  publishing retain their recorded boundaries. M6.7 categories are not generated until a
  documented public route is recorded for the requested operation/category.

For the exact active inventory, read
`games/sts2/tests/content-capability-graph.md`.

## Art Contract

`gen_sprite.py` is framework-neutral. RitsuLib `*AssetProfile` consumers own runtime
wiring. The verified Character profiles are selection portrait/background, top-panel
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
- `plugins/open-mod/`: generated Codex plugin payload from `publish.sh --plugin`.
- `skills/`: generated portable Agent Skills payload from `publish.sh --portable`.
- `.agents/plugins/marketplace.json`: repo-local Codex marketplace entry.

Edit source under `games/sts2/`; never hand-edit generated payload contents. Regenerate
both committed payloads after source changes.

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
and RitsuLib `0.4.62`. Use PowerShell syntax for normal commands. Invoke `publish.sh`
through an explicit Git Bash executable when needed; do not mix Bash path syntax into
PowerShell commands.

## Active Documents

- `documents/PROJECT.md`
- `documents/IMPLEMENTATION_PLAN.md`
- `documents/BASELINE_RESEARCH.md`
- `games/sts2/tests/README.md`
- `games/sts2/tests/content-capability-graph.md`

Migration results are in `documents/history/RITSULIB_MIGRATION_RESULTS.md`.
