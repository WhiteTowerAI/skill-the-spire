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
pipeline-supported. The fresh Prismwright acceptance is closed and retired by explicit
human-lead decision; its headed result and waived Tier 2 harness are recorded in
`documents/history/M65_FRESH_ACCEPTANCE_RESULTS.md`. Do not reopen that proof, start M7, or
prepare/claim a GitHub release without later lead instruction.

M6.6 is the active provisional capability milestone. Package 2A computed Card values,
Package 5 custom-Character dialogue in native Ancient scenes, and the bounded Package 1
advanced creature-targeting slice are pipeline-supported. Package 1 supports single-target
Cards, single-target Potions, and multi-target Cards; its mouse/controller result and
strict Tier 2 exception are recorded in
`documents/history/M66_ADVANCED_TARGETING_RESULTS.md`. Custom multi-target Potions remain
unsupported on the pinned profile. Package 3 owned custom Rest Site options is the direct
next step in the approved order, but it does not start automatically. The remaining
gameplay-readability surfaces and combat-only singleplayer custom CardPile/ExtraHand slice
remain planned and unsupported until individually selected and proved. The package list may
gain other lead-approved features.

M6.7 is the planned follow-on for version-bound vanilla content overrides and behavior
composition. Its intended scope includes data/upgrade/property edits, acquisition and pool
changes, behavior composition, and complete recipe-backed replacement across grounded
content categories. It does not start automatically after M6.6. Until individual M6.7
operation/category gates pass, vanilla editing remains unsupported; never generate
ungrounded Harmony, reflection, or IL from a prompt.

## Dependency Contract

- Generated Mods target STS2 `0.107.1` and `STS2.RitsuLib.Compat.0.107.1` `0.4.62`.
- Runtime manifests depend only on `STS2-RitsuLib >= 0.4.62`.
- Generated Mods must not reference, package, or depend on BaseLib.
- Do not use Alchyr templates or restore historical BaseLib implementation snippets.
- `baselines/BaseLib-StS2` and `baselines/downfall` are offline historical research only.
- `baselines/STS2-RitsuLib` is the maintainer research checkout; generated Mods consume
  the pinned package/runtime profile instead of copying it.
- `baselines/Sts2-YuWanCard` is a same-game-version Character/content-depth research
  checkout pinned at `07d7daa`. Its gameplay and Character framework is self-built with
  Harmony/Publicizer; RitsuLib is optional settings UI only. Use it to inventory consumers
  and study product behavior, never as RitsuLib API authority or a source of shipped code,
  art, audio, Spine, shader, or other assets.

## Supported Boundary

Pipeline-supported surfaces include:

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
- stateful relic cadence, combat-only secondary resources, all-or-nothing payment, public
  fixed combat UI, and ordered semantic buffers using normal Play -> Discard.

Preserve these important boundaries:

- Route stores semantic direction values, never retained played Card instances.
- A source Card follows STS2's normal result pile lifecycle.
- Scry is singleplayer and Mod-local; it is not a global interoperability service.
- The fixed Character resource control is 220x32 at offset 160 with a text fallback and
  must remain disjoint from native Energy.
- Custom locked-selection/map-marker presentation, custom Ancient models/backgrounds/
  layouts/options/rewards, production animation beyond the bounded cues, line audio,
  custom multi-target Potions, arbitrary material/audio, remote-player UI, alternative
  Energy, retained-card zones, one-click Workshop publishing, and all unproved M6.7 vanilla
  override categories remain unsupported.

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
