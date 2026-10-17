# Scaffold - create the local-runtime RitsuLib project

Goal: generate the smallest skill-the-spire-owned STS2 project from the semantic SPEC through the
single pinned RitsuLib adapter path.

## Authoring profile

```text
authoring profile: ritsulib-0.6.7-sts2-0.107.1
compile runtime: the checked local RitsuLib version (>= 0.6.7)
runtime Mod id: STS2-RitsuLib
host: STS2 stable 0.107.1
```

The default `STS2.RitsuLib` package follows the newest beta-facing game API and is a hard
failure here. Never add BaseLib, a template copied from another project, prompt-derived patches, or an
unvalidated packer fallback.

## 1. Toolchain and location

Require .NET SDK 9 and Python 3. Use the dedicated outer directory outside the skill
repository that already holds `DESIGN.md` and `SPEC.md` (and `PLAN.md`/`MEMORY.md` when
present). Its leaf name must differ from `<ModName>`; the Mod resource tree may later use
`<project-dir>/<ModName>/`.

```powershell
dotnet --version
python ${GAME_TOOLS_DIR}/scaffold.py `
  --project-dir <absolute-outer-directory> `
  --mod-name <ModName> `
  --author <Author> `
  --game-dir <STS2-install-directory> `
  --runtime-dir <optional-installed-RitsuLib-directory>
```

`<ModName>` is a C# identifier without spaces. The generator accepts a directory that holds
only `DESIGN.md`, `SPEC.md`, `PLAN.md`, and `MEMORY.md`, keeps them untouched, refuses any
other existing entry, and never overwrites an existing project.

## 2. Generated contract

The project contains:

- `<ModName>.csproj` with the bundled `Godot.NET.Sdk 4.5.1`, local game assembly references,
  `Sts2ApiCompat=0.107.1`, references to all five RitsuLib modules (`STS2-RitsuLib` and
  `STS2-RitsuLib.Runtime` from `compat/0.107.1/`, plus `STS2-RitsuLib.Shared`, `.Ui`, and
  `.Settings` from `shared/`), and a pinned local RitsuLib version and assembly-set digest;
- `skillthespire/sdk/Godot.NET.Sdk.4.5.1/`, copied from the skill asset and used only as a build
  input;
- `RitsuLibAutoCopy=false` and an empty `RitsuLibDeployDir`, so the consumer never bundles
  the framework DLL;
- `mod_manifest.json` with only `STS2-RitsuLib >= 0.6.7` and
  `min_game_version=0.107.1`,
  `has_dll=true`, `affects_gameplay=true`, and `has_pck=false` for the empty scaffold.
  Keep `affects_gameplay=true`: RitsuLib treats the models of a Mod that declares `false` as
  local-only, so they get no network identity and synced actions such as right-click never
  send;
- `Sts2PathDiscovery.props` plus optional `local.props` support; local Mods resolve beside
  the host executable, which is the game root on Windows/Linux and
  `SlayTheSpire2.app/Contents/MacOS/` on macOS;
- `skillthespire/vanilla-overrides.json` pinned to the checked `0.107.1` catalog with an empty
  `operations` array; authoring may fill it only through an authorable route family. It is
  a build-time input only — it stays in the project directory and is never deployed into
  `mods/<ModName>/`, because the game reads every `.json` there as a Mod manifest;
- `<ModName>Code/MainFile.cs`, whose exact load marker records the loaded RitsuLib Runtime
  module's version and `Sts2ApiCompat` assembly metadata.

RitsuLib remains a separate runtime Mod. Reuse the official Steam Workshop item
`3747602295` when it is already installed; `build.py` checks the game `mods/` directory
first and then that item in the Steam library that owns STS2. Only install the matching
compat zip or verified variant pack when neither source exists, and install the complete
folder: since RitsuLib 0.6.0 the root `STS2-RitsuLib.dll` is only a loader, and the
`compat/`, `shared/`, and `assets.zip` entries beside it are required. Never copy any RitsuLib
file into `<ModName>`.

The local runtime's compat and shared modules are the reproducible compile input for this
project. The project records the framework version and one digest over those five module
hashes, never a machine-specific absolute path. The manifest keeps the `0.6.7` player floor
because authoring remains inside the `0.6.7` API baseline even when the local compile runtime
is newer.

If the installed runtime changes after scaffold (the Workshop item updates on its own),
`build.py` stops instead of silently compiling against different assemblies. Review the
RitsuLib release notes for the versions in between, then re-pin the existing project:

```powershell
python ${GAME_TOOLS_DIR}/scaffold.py `
  --project-dir <existing-project-directory> `
  --mod-name <ModName> `
  --game-dir <STS2-install-directory> `
  --repin-runtime
```

Re-pinning rewrites only `RitsuLibCompileVersion`, `RitsuLibCompileAssemblySetSha256`, and
`MainFile.CompileFrameworkVersion`. It never changes the profile, authored sources, or the
player's minimum dependency. Build, Tier 1, and Tier 2 then run again before the Mod is
reported as working on the new runtime.

The Mod manifest is always named `mod_manifest.json`; `build.py` rejects any other name.

When authoring adds localization, images, or scenes, place them under
`<project-dir>/<ModName>/` and set `has_pck=true`. `build.py` packs that resource tree with
the shared skill-the-spire packer; there is no framework-specific PCK branch.

The override manifest is a loose build/deployment artifact, not a Godot resource and not
part of the PCK. Do not delete it from a new scaffold. For an accepted existing-model SPEC,
fill it only with the Card operations in `vanilla-card-overrides.md` and/or the
visual operations in `vanilla-visual-overrides.md` and/or the existing-Ancient
option/branch operations in `vanilla-ancient-overrides.md` and/or availability
operations in `vanilla-availability-overrides.md`; leave it empty for new content
and unlisted operations. Put every selected visual resource under
`<project-dir>/<ModName>/` and keep its required/optional flag literal.

## 3. Record state

Write the absolute project path and profile id to `MEMORY.md`, mark `scaffold` done in
`PLAN.md`, and continue to `author.md`. Do not build before the selected content and
diagnostics are authored.
