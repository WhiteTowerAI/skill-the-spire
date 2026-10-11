# Build - compile and deploy the local-runtime RitsuLib Mod

Goal: validate the selected framework profile, build the Mod, and deploy only its own
artifacts to the stable host.

## Run

```bash
python ../modmaker/scripts/build.py --project-dir <project path from MEMORY.md> --mod-name <ModName>
```

Before MSBuild, the tool verifies:

- the generated project has no framework `PackageReference`, uses the bundled
  `Godot.NET.Sdk 4.5.1`, and references local STS2/RitsuLib assemblies;
- no BaseLib/Alchyr dependency appears in the project or manifest;
- the manifest keeps the authoring API floor `STS2-RitsuLib >= 0.6.7` and targets host
  `0.107.1` even when the scaffold-pinned local compile runtime is newer;
- `has_pck` is `true` exactly when the authored Mod resource tree is non-empty;
- when localization tables exist, require both `eng` and `zhs` directories with
  identical table names, keys, and SmartFormat tokens plus nonempty localized values;
- the installed host's `release_info.json` is stable `0.107.1`;
- the game `mods/STS2-RitsuLib` directory or official Steam Workshop item `3747602295`
  is a complete RitsuLib 0.6 runtime folder: loader `STS2-RitsuLib.dll`, schema-2
  `ritsulib-variants.manifest`, a `compat/0.107.1/` variant with its marker, and the
  `shared/` modules, with every module hash matching the manifest and the whole compile
  assembly set matching the scaffold pin;
- any generated Character `ancients.json` uses the pinned vanilla target catalog,
  contiguous dialogue/line structure, valid visit/repeat/Architect metadata, matching
  Character entries, and identical keys across `eng` and `zhs`;
- when present, `skillthespire/vanilla-overrides.json` has the pinned host/profile/catalog
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

The skill supplies the small `Godot.NET.Sdk 4.5.1` import files. `GodotSharp`,
`System.IO.Hashing`, STS2, Harmony, and RitsuLib resolve from the checked local game/runtime
installation. Build never downloads a framework package and never substitutes a newer local
RitsuLib version for the one scaffold recorded. After a Workshop update, re-pin explicitly
with `scaffold.py --repin-runtime` (see `scaffold.md`).

After the build it rejects a restore that reintroduced a framework package, copies the Mod's
DLL/manifest/PDB through the generated MSBuild target, packs
`<project-dir>/<ModName>/` when resources exist, and rejects a generated directory that
contains `STS2-RitsuLib.dll`, `BaseLib.dll`, or `BaseLib.pck`.
It also keeps the deployed Mod free of any loose `.json` other than `mod_manifest.json`: the
game parses every `.json` under a Mod directory, at any depth, as a Mod manifest and logs a
load error for each one without an `id`. `skillthespire/vanilla-overrides.json` is a build-time
input that stays in the project directory, and any deployed non-manifest `.json` fails the
build. Authored JSON belongs inside the `.pck`. A project without the override manifest builds
with no vanilla overrides.

`--runtime-dir <path>` may point at an explicitly selected installed runtime folder. A release
zip can be inspected separately but cannot be used to compile until it is installed.

## Expect

- build summary: `0 warnings, 0 errors`;
- profile lines report the exact scaffold-pinned compile version, exact `host=0.107.1`, and
  exact `compat=0.107.1`;
- `mods/<ModName>/` contains `<ModName>.dll`, `mod_manifest.json`, optional PDB, and a PCK
  only when the Mod owns resources;
- RitsuLib remains separate in the game `mods/` directory or its official Workshop item.

## On failure

Read `../sts2api/errors.md` § Build And Profile and match the exact signature
before changing anything. It carries the cause and fix for every profile, manifest, pack,
Ancient-dialogue, and vanilla-override failure this stage can emit.

Before applying a fix, follow `repair.md` from the observed signature. A compiler or grounded
package-path correction normally fixes the project directly, but a proposed fix that changes
the accepted operation returns to DESIGN and SPEC for user acceptance.

Two rules that decide *where* the fix goes, and are not in the catalog:

- A `RitsuLib profile FAILED` / `RitsuLib restore FAILED` contract error is fixed in the
  local runtime, bundled SDK, manifest, host, or runtime profile chosen at `scaffold.md`.
  Never enter a C# repair loop for one.
- Ordinary `CS*`/`MSB*` diagnostics go to `repair.md`, keyed by exact code and symbol.

On success, mark `build` done in `PLAN.md`, record the resolved Mods path and profile in
`MEMORY.md`, and continue to `verify.md`.
