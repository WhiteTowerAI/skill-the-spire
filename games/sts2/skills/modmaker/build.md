# Build - compile and deploy the pinned RitsuLib Mod

Goal: validate the selected framework profile, build the Mod, and deploy only its own
artifacts to the stable host.

## Run

```bash
python ${GAME_TOOLS_DIR}/build.py --project-dir <project path from MEMORY.md> --mod-name <ModName>
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
  operations the current catalog promotes. Each override family is accepted by its own
  reference, and every route outside them fails closed:
  - `reference/vanilla-card-overrides.md` — exact public Card routes;
  - `reference/vanilla-visual-overrides.md` — the 44 exact visual routes, plus their
    required/optional Mod-local resources;
  - `reference/vanilla-ancient-overrides.md` — existing-Ancient option append/replacement
    and page-flow routes, exact Adapter/dependency fingerprints, and complete per-language
    `events.json` keys;
  - `reference/vanilla-availability-overrides.md` — epoch and Card/Relic/Potion pool routes,
    complete pool baselines, Relic/Potion override dependencies, and ordered primary-pool
    checks;
  - `reference/vanilla-non-card-overrides.md` — non-Card data and behavior routes, including
    owner-hook streams and checked lifecycle replacements.

Before querying MSBuild, the tool reuses an explicit `--nuget-packages-dir`, the
`NUGET_PACKAGES` environment value, or a complete pinned package in the real user's
`~/.nuget/packages` cache. This keeps isolated Codex `dotnet` profiles from downloading a
second copy. If none is complete, normal first-use restore remains available.

After the build it checks the NuGet lock resolved the exact compat package, copies the
Mod's DLL/manifest/PDB through the generated MSBuild target, packs
`<project-dir>/<ModName>/` when resources exist, and rejects a generated directory that
contains `STS2-RitsuLib.dll`, `BaseLib.dll`, or `BaseLib.pck`.
It also keeps the deployed Mod free of any loose `.json` other than `<ModName>.json`: the
game parses every `.json` under a Mod directory, at any depth, as a Mod manifest and logs a
load error for each one without an `id`. `openmod/vanilla-overrides.json` is a build-time
input that stays in the project directory; a copy left by an older build is deleted, and any
other deployed non-manifest `.json` fails the build. Authored JSON belongs inside the `.pck`.
Legacy projects without a source override manifest remain valid.

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

## On failure

Read `${STS2_API_SKILL_DIR}/errors.md` § Build And Profile and match the exact signature
before changing anything. It carries the cause and fix for every profile, manifest, pack,
Ancient-dialogue, and vanilla-override failure this stage can emit.

Before applying a fix, classify the observed difference through `repair.md`, write the active
PLAN route, and run `repair_trace.py`. A compiler or grounded package-path correction is usually
implementation-equivalent, but a proposed fix that changes the accepted operation is not.

Two rules that decide *where* the fix goes, and are not in the catalog:

- A `RitsuLib profile FAILED` / `RitsuLib restore FAILED` contract error is fixed in the
  package, manifest, host, or runtime variant chosen at `scaffold.md`. Never enter a C#
  repair loop for one.
- Ordinary `CS*`/`MSB*` diagnostics go to `repair.md`, keyed by exact code and symbol, after
  classification.

On success, mark `build` done in `PLAN.md`, record the resolved Mods path and profile in
`MEMORY.md`, and continue to `verify.md`. If `--skip-runtime-check` was used, record that
the runtime profile was not checked.
