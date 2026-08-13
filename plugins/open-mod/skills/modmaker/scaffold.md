# Scaffold - create the local-runtime RitsuLib project

Goal: generate the smallest open-mod-owned STS2 project from the semantic SPEC through the
single pinned RitsuLib adapter path.

## Authoring profile

```text
authoring profile: ritsulib-0.5.11-sts2-0.107.1
compile runtime: the checked local RitsuLib version (>= 0.5.11)
runtime Mod id: STS2-RitsuLib
host: STS2 stable 0.107.1
```

The default `STS2.RitsuLib` package follows the newest beta-facing game API and is a hard
failure here. Never restore BaseLib, a historical template, prompt-derived patches, or an
unvalidated packer fallback.

## 1. Toolchain and location

Require .NET SDK 9 and Python 3. Choose a dedicated empty outer directory outside the
skill repository. Its leaf name must differ from `<ModName>`; the Mod resource tree may
later use `<project-dir>/<ModName>/`.

```powershell
dotnet --version
python ../modmaker/scripts/scaffold.py `
  --project-dir <absolute-empty-outer-directory> `
  --mod-name <ModName> `
  --author <Author> `
  --game-dir <STS2-install-directory> `
  --runtime-dir <optional-installed-RitsuLib-directory>
```

`<ModName>` is a C# identifier without spaces. The generator refuses a nonempty directory
and never overwrites an existing project.

## 2. Generated contract

The project contains:

- `<ModName>.csproj` with the bundled `Godot.NET.Sdk 4.5.1`, local game assembly references,
  `Sts2ApiCompat=0.107.1`, and a pinned local RitsuLib version/assembly hash;
- `openmod/sdk/Godot.NET.Sdk.4.5.1/`, copied from the skill asset and used only as a build
  input;
- `RitsuLibAutoCopy=false` and an empty `RitsuLibDeployDir`, so the consumer never bundles
  the framework DLL;
- `mod_manifest.json` with only `STS2-RitsuLib >= 0.5.11` and
  `min_game_version=0.107.1`,
  `has_dll=true`, and `has_pck=false` for the empty scaffold;
- `Sts2PathDiscovery.props` plus optional `local.props` support; local Mods resolve beside
  the host executable, which is the game root on Windows/Linux and
  `SlayTheSpire2.app/Contents/MacOS/` on macOS;
- `openmod/vanilla-overrides.json` pinned to the checked `0.107.1` catalog with an empty
  `operations` array; authoring may fill it only through a promoted operation package. It is
  a build-time input only — it stays in the project directory and is never deployed into
  `mods/<ModName>/`, because the game reads every `.json` there as a Mod manifest;
- `<ModName>Code/MainFile.cs`, whose exact load marker records public RitsuLib version
  metadata and the actual loaded `Sts2ApiCompat` assembly metadata.

RitsuLib remains a separate runtime Mod. Reuse the official Steam Workshop item
`3747602295` when it is already installed; `build.py` checks the game `mods/` directory
first and then that item in the Steam library that owns STS2. Only install the matching
compat zip or verified variant pack when neither source exists. Never copy
`STS2-RitsuLib.dll` into `<ModName>`.

The local runtime Compat DLL is the reproducible compile input for this project. The project
records its framework version and SHA-256 but never writes a machine-specific absolute path.
The manifest keeps the `0.5.11` player floor because authoring remains inside the `0.5.11` API
baseline even when the local compile runtime is newer. If the installed runtime changes after
scaffold, `build.py` stops and requires an explicit runtime-profile migration; it never silently
changes either recorded identity or the player's minimum dependency.

New projects use the canonical `mod_manifest.json` name. A project created by an older
open-mod scaffold may retain its single `<ModName>.json`; `build.py` accepts that legacy form
but fails when both names exist, because choosing one silently would make deployment ambiguous.

When authoring adds localization, images, or scenes, place them under
`<project-dir>/<ModName>/` and set `has_pck=true`. `build.py` packs that resource tree with
the shared open-mod packer; there is no framework-specific PCK branch.

The override manifest is a loose build/deployment artifact, not a Godot resource and not
part of the PCK. Do not delete it from a new scaffold. For an accepted existing-model SPEC,
fill it only with the Card operations in `vanilla-card-overrides.md` and/or the
visual operations in `vanilla-visual-overrides.md` and/or the existing-Ancient
option/branch operations in `vanilla-ancient-overrides.md` and/or availability
operations in `vanilla-availability-overrides.md`; leave it empty for new content
and unpromoted operations. Put every selected visual resource under
`<project-dir>/<ModName>/` and keep its required/optional flag literal. Legacy projects
created before M6.7.0 may remain without this file.

## 3. Record state

Write the absolute project path and profile id to `MEMORY.md`, mark `scaffold` done in
`PLAN.md`, and continue to `author.md`. Do not build before the selected content and
diagnostics are authored.
