# Build - compile and deploy the pinned RitsuLib Mod

Goal: validate the selected framework profile, build the Mod, and deploy only its own
artifacts to the stable host.

## Run

```bash
python ../modmaker/scripts/build.py --project-dir <project path from MEMORY.md> --mod-name <ModName>
```

Before MSBuild, the tool verifies:

- project package `STS2.RitsuLib.Compat.0.107.1` is exactly `0.5.4`;
- no BaseLib/Alchyr dependency appears in the project or manifest;
- the manifest depends only on `STS2-RitsuLib >= 0.5.4` and targets host `0.107.1`;
- `has_pck` is `true` exactly when the authored Mod resource tree is non-empty;
- the installed host's `release_info.json` is stable `0.107.1`;
- the game `mods/STS2-RitsuLib` directory or official Steam Workshop item `3747602295`
  contains RitsuLib `>= 0.5.4` with a matching direct compat runtime or variant-pack
  `lib/0.107.1/STS2-RitsuLib.dll`, marker, and manifest hash;
- any generated Character `ancients.json` uses the pinned vanilla target catalog,
  contiguous dialogue/line structure, valid visit/repeat/Architect metadata, matching
  Character entries, and identical keys across shipped languages.
- when present, `openmod/vanilla-overrides.json` has the pinned host/profile/catalog
  digest, matching Mod id, grounded baselines/routes, no same-Mod conflict, and only
  operations promoted by the current catalog. M6.7.1 accepts the exact public Card routes
  in `reference/vanilla-card-overrides.md`; M6.7.2 accepts the 44 exact visual routes and
  validates their required/optional Mod-local resources through
  `reference/vanilla-visual-overrides.md`; M6.7.3 accepts exact existing-Ancient option
  append/replacement/page-flow routes in `reference/vanilla-ancient-overrides.md`, including
  exact Adapter/dependency fingerprints and complete per-language `events.json` keys.
  M6.7.4 accepts the exact epoch and Card/Relic/Potion pool routes in
  `reference/vanilla-availability-overrides.md`, including complete pool baselines,
  Relic/Potion override dependencies, and ordered primary-pool checks. Every other nonempty
  route still fails closed.

Before querying MSBuild, the tool reuses an explicit `--nuget-packages-dir`, the
`NUGET_PACKAGES` environment value, or a complete pinned package in the real user's
`~/.nuget/packages` cache. This keeps isolated Codex `dotnet` profiles from downloading a
second copy. If none is complete, normal first-use restore remains available.

After the build it checks the NuGet lock resolved the exact compat package, copies the
Mod's DLL/manifest/PDB through the generated MSBuild target, packs
`<project-dir>/<ModName>/` when resources exist, and rejects a generated directory that
contains `STS2-RitsuLib.dll`, `BaseLib.dll`, or `BaseLib.pck`.
For a new scaffold it also requires the deployed override manifest and compares its bytes
with the source document that passed preflight. Legacy projects without a source override
manifest remain valid.

`--runtime-dir <path>` may point at an explicitly selected runtime folder or release zip.
`--nuget-packages-dir <path>` may select a shared NuGet global-packages directory.
`--skip-runtime-check` is a compile-only escape hatch and can never satisfy Tier 1.

## Expect

- build summary: `0 warnings, 0 errors`;
- profile lines report the actual `frameworkVersion>=0.5.4`, exact `host=0.107.1`, and
  exact `compat=0.107.1`;
- `mods/<ModName>/` contains `<ModName>.dll`, `<ModName>.json`, optional PDB, and a PCK
  only when the Mod owns resources;
- RitsuLib remains separate in the game `mods/` directory or its official Workshop item.

## Failure classes

- `required compile asset ... Do not use the default beta-facing package` means the
  project selected a floating/main package. Restore the pinned compat reference.
- `host ... required stable 0.107.1` means the installed game branch is wrong. Stop; do
  not compile against another host.
- `RitsuLib runtime was not found` means neither the local runtime nor official Workshop
  item is installed. Subscribe to item `3747602295` or install the compat/variant pack.
- `no matching 0.107.1 RitsuLib variant` means the discovered runtime is incompatible.
  Do not fall back to a root beta DLL.
- `[ancient-dialogue]` or an Ancient localization detail in the profile failure means the
  generated flat table is structurally unsafe. Fix the reported semantic group/key; do not
  bypass the preflight or enable the debug missing-Architect fallback.
- `[vanilla-overrides]` with an Ancient target/route/page/localization/fingerprint detail
  means the M6.7.3 manifest, generated flow, or `events.json` drifted. Fix the named
  semantic operation or generated source; never relax the catalog or swap in a guessed
  patch target.
- `manifest has_pck must be ...` means authored localization/art/scenes and the manifest
  disagree. Set the boolean to match the resource tree before rebuilding.
- ordinary `CS*`/`MSB*` diagnostics go to `repair.md`, keyed by exact code and symbol.

On success, mark `build` done in `PLAN.md`, record the resolved Mods path and profile in
`MEMORY.md`, and continue to `verify.md`. If `--skip-runtime-check` was used, record that
the runtime profile was not checked.
