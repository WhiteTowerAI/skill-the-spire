# M8.5 Cross-Platform Reproducible Installed Workflow Result

Date: 2026-08-12

Status: closed by explicit human-lead decision on 2026-08-12 with unresolved exceptions. No
M8.5 execution contract was ever drafted. This record does not authorize M8.6.

## Result

The human lead closed M8.5 after two bounded maintenance repairs improved generated-project
portability. New projects now use the host-discovered canonical manifest name, macOS paths point
at the executable-adjacent app-bundle layout, and generated builds use validated local framework
inputs rather than framework package references.

This is not a successful cross-platform installed-workflow proof. The intended M8.5 outcome was
that a committed installed skill would reproduce on Windows and macOS and clean up only the
process tree it started. That outcome was not demonstrated, and the process-tree portion was not
implemented.

## Implemented Maintenance

1. Generated projects compile against the validated local RitsuLib Compat DLL and local
   game/runtime assemblies using the bundled `Godot.NET.Sdk 4.5.1` import set. Their runtime
   manifest still requires only `STS2-RitsuLib >= 0.5.4`.
2. New scaffolds generate, include, and deploy canonical `mod_manifest.json`.
3. Existing projects with one legacy `<ModName>.json` remain compatible. A project containing
   both canonical and legacy manifests fails closed before MSBuild.
4. macOS generated `ModsPath` and scaffold-time local RitsuLib discovery resolve to
   `SlayTheSpire2.app/Contents/MacOS/mods/`.
5. macOS host validation accepts
   `SlayTheSpire2.app/Contents/Resources/release_info.json`.
6. macOS `steam_appid.txt` resolves beside the inner executable under `Contents/MacOS/`.
7. Three stale regression fixtures were updated to use the current canonical manifest contract.

The authoritative implementation is under `games/sts2/`. Before the closure instruction, the
source changes had already been regenerated into the plugin and portable payload trees. The
closure step did not generate another payload and did not edit an installed payload.

## Checks Run

- Full `games/sts2/tools/tests` regression: `395/395` passed.
- One Windows reference-only scaffold C# compile against the checked local Compat DLL passed.
- Python compilation passed for the changed Python tools and tests.
- Source/plugin/portable copies of the changed shipped scripts matched by SHA-256.
- `git diff --check` passed after closure status synchronization.

These checks are static and Windows compile evidence. They do not establish macOS behavior,
installed-workflow reproducibility, runtime loading, gameplay, or cleanup of an actual game
process tree.

## Unresolved Exceptions

- No macOS host or installed-workflow run occurred.
- `launch.py` still starts a macOS app through `open -a`. The returned `Popen` owns the helper
  invocation, not a tracked game-process tree.
- `stop_process()` terminates or kills only that held `Popen`. Launcher-owned descendant
  discovery, scoped graceful shutdown, forced tree cleanup, and proof that no owned child remains
  are unimplemented.
- Restore/offline behavior was not run on Windows or macOS.
- No Tier 1, Tier 2, headed, or game run occurred.
- No fresh natural-language Mod, installed-payload acceptance, or M8.6 hook-participation proof
  was run.

Closing M8.5 records the human-lead decision and these exceptions literally. It does not relabel
the maintenance checks as cross-platform proof and does not satisfy the remaining human-selection
condition for M8.6.

## Files And Documents

Authoritative source changes are in `games/sts2/tools/scaffold.py`, `ritsu_profile.py`,
`launch.py`, `collect_vanilla_catalog.py`, their focused regression tests, and the affected
modmaker/API guidance. Generated copies changed under `plugins/open-mod/skills/` and `skills/`
before the no-new-payload closure instruction.

Current documents changed because M8.5 status or its evidence boundary changed: `AGENTS.md`,
`README.md`, `documents/IMPLEMENTATION_PLAN.md`, `documents/PROJECT.md`,
`documents/BASELINE_RESEARCH.md`, `documents/history/README.md`,
`games/sts2/tests/README.md`, and `games/sts2/tests/content-capability-graph.md`. All current
documents required by the closure protocol were updated; none were reviewed and left unchanged.
