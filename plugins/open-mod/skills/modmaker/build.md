# Build - compile and deploy the pinned RitsuLib Mod

Goal: validate the selected framework profile, build the Mod, and deploy only its own
artifacts to the stable host.

## Run

```bash
python ${CLAUDE_PLUGIN_ROOT}/tools/build.py --project-dir <project path from MEMORY.md> --mod-name <ModName>
```

Before MSBuild, the tool verifies:

- project package `STS2.RitsuLib.Compat.0.107.1` is exactly `0.4.62`;
- no BaseLib/Alchyr dependency appears in the project or manifest;
- the manifest depends only on `STS2-RitsuLib >= 0.4.62` and targets host `0.107.1`;
- the installed host's `release_info.json` is stable `0.107.1`;
- `mods/STS2-RitsuLib` contains the matching direct compat runtime or a variant-pack
  `lib/0.107.1/STS2-RitsuLib.dll` with matching marker and manifest hash.

After the build it checks the NuGet lock resolved the exact compat package, copies the
Mod's DLL/manifest/PDB through the generated MSBuild target, packs
`<project-dir>/<ModName>/` when resources exist, and rejects a generated directory that
contains `STS2-RitsuLib.dll`, `BaseLib.dll`, or `BaseLib.pck`.

`--runtime-dir <path>` may point at an explicitly selected runtime folder or release zip.
`--skip-runtime-check` is a compile-only escape hatch and can never satisfy Tier 1.

## Expect

- build summary: `0 warnings, 0 errors`;
- profile lines report `frameworkVersion=0.4.62`, `host=0.107.1`, and `compat=0.107.1`;
- `mods/<ModName>/` contains `<ModName>.dll`, `<ModName>.json`, optional PDB, and a PCK
  only when the Mod owns resources;
- RitsuLib remains in its separate `mods/STS2-RitsuLib/` folder.

## Failure classes

- `required compile asset ... Do not use the default beta-facing package` means the
  project selected a floating/main package. Restore the pinned compat reference.
- `host ... required stable 0.107.1` means the installed game branch is wrong. Stop; do
  not compile against another host.
- `no matching 0.107.1 RitsuLib variant` means the runtime asset is missing/wrong. Install
  the compat zip or verified variant pack; do not fall back to a root beta DLL.
- ordinary `CS*`/`MSB*` diagnostics go to `repair.md`, keyed by exact code and symbol.

On success, mark `build` done in `PLAN.md`, record the resolved Mods path and profile in
`MEMORY.md`, and continue to `verify.md`.
