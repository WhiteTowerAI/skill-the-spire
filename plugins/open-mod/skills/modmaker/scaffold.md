# Scaffold - create the pinned RitsuLib project

Goal: generate the smallest open-mod-owned STS2 project from the semantic SPEC. One
adapter-owned path (`INV-7`).

## Pinned profile

```text
profile: ritsulib-0.5.4-sts2-0.107.1
compile package: STS2.RitsuLib.Compat.0.107.1 0.5.4
runtime Mod id: STS2-RitsuLib
host: STS2 stable 0.107.1
```

The default `STS2.RitsuLib` package follows the newest beta-facing game API and is a hard
failure here. Its fallbacks are the ones `INV-7` names, plus the PckPacker target.

## 1. Toolchain and location

Require .NET SDK 9 and Python 3. Choose a dedicated empty outer directory outside the
skill repository. Its leaf name must differ from `<ModName>`; the Mod resource tree may
later use `<project-dir>/<ModName>/`.

```powershell
dotnet --version
python ../modmaker/scripts/scaffold.py `
  --project-dir <absolute-empty-outer-directory> `
  --mod-name <ModName> `
  --author <Author>
```

`<ModName>` is a C# identifier without spaces. The generator refuses a nonempty directory
and never overwrites an existing project.

## 2. Generated contract

The project contains:

- `<ModName>.csproj` with the exact compat package and `Sts2ApiCompat=0.107.1`;
- `RitsuLibAutoCopy=false` and an empty `RitsuLibDeployDir`, so the consumer never bundles
  the framework DLL;
- `<ModName>.json` with only `STS2-RitsuLib >= 0.5.4`, `min_game_version=0.107.1`,
  `has_dll=true`, and `has_pck=false` for the empty scaffold;
- `Sts2PathDiscovery.props` plus optional `local.props` support;
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

The exact Compat NuGet package remains the reproducible compile input. It is distinct from
the runtime installation. `build.py` reuses `NUGET_PACKAGES` or a complete user-level
`~/.nuget/packages` cache even when `dotnet` runs under an isolated Codex sandbox profile.

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
