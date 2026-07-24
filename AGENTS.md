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
and RitsuLib `0.4.62`. R0-R6 completed the semantic contract, pinned scaffold/build
profile, supported content migration, Character Foundation/static presentation,
state/resource/buffer/UI composition, and generated-Mod-local singleplayer Scry helper.

R7 was canceled by the human lead. It did not pass and must never be described as passed.
R8 completed repository cleanup, active documentation, Codex/portable payload generation,
and maintainer validation. The lead's subsequent clean-workspace Codex test produced a
working in-game Mod and passed external acceptance. The BaseLib-to-RitsuLib migration is
complete at the supported boundary.

Do not reopen migration proof projects, start M7, or open an expansion track unless the
lead gives a later instruction. The next work is bug fixing and content-quality
improvement from user-test feedback. Do not prepare or claim a GitHub release yet.

## Dependency Contract

- Generated Mods target STS2 `0.107.1` and `STS2.RitsuLib.Compat.0.107.1` `0.4.62`.
- Runtime manifests depend only on `STS2-RitsuLib >= 0.4.62`.
- Generated Mods must not reference, package, or depend on BaseLib.
- Do not use Alchyr templates or restore historical BaseLib implementation snippets.
- `baselines/BaseLib-StS2` and `baselines/downfall` are offline historical research only.
- `baselines/STS2-RitsuLib` is the maintainer research checkout; generated Mods consume
  the pinned package/runtime profile instead of copying it.

## Supported Boundary

Pipeline-supported surfaces include:

- card, relic, potion, power, keyword, enchantment, and orb;
- generated-Mod-local singleplayer top-X Scry with normal selection/discard history/hooks;
- monster + encounter and the complete grounded move vocabulary;
- Event / World Node outcomes, bounded rich text/VFX/native presentation, and one bounded
  solo Quest Card -> forced Event composition;
- playable Character Foundation and eight checked static art profiles;
- stateful relic cadence, combat-only secondary resources, all-or-nothing payment, public
  fixed combat UI, and ordered semantic buffers using normal Play -> Discard.

Preserve these important boundaries:

- Route stores semantic direction values, never retained played Card instances.
- A source Card follows STS2's normal result pile lifecycle.
- Scry is singleplayer and Mod-local; it is not a global interoperability service.
- The fixed Character resource control is 220x32 at offset 160 with a text fallback and
  must remain disjoint from native Energy.
- Locked selection, map marker, native custom-Character Ancient presentation, production
  animation/material/audio, remote-player UI, alternative Energy, vanilla editing,
  retained-card zones, and one-click Workshop publishing remain unsupported.

For the exact active inventory, read
`games/sts2/tests/content-capability-graph.md`.

## Art Contract

`gen_sprite.py` is framework-neutral. RitsuLib `*AssetProfile` consumers own runtime
wiring. The verified Character profiles are selection portrait/background, top-panel
icon, combat/rest/merchant static bodies, five full-energy layers, and the compact icon.

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
3. Use a fresh natural-language acceptance Mod for pipeline acceptance, then retire it
   after durable evidence is recorded.

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
