# Scaffold - create the pinned RitsuLib project

Goal: generate the smallest open-mod-owned STS2 project from the semantic SPEC.
This is one adapter-owned path, not a second copy of the historical BaseLib recipes.

## Pinned profile

```text
profile: ritsulib-0.4.62-sts2-0.107.1
compile package: STS2.RitsuLib.Compat.0.107.1 0.4.62
runtime Mod id: STS2-RitsuLib
host: STS2 stable 0.107.1
```

The default `STS2.RitsuLib` package follows the newest beta-facing game API and is a
hard failure here. Do not use an Alchyr template, BaseLib package, BaseLib runtime, or
PckPacker target as a fallback.

## 1. Toolchain and location

Require .NET SDK 9 and Python 3. Choose a dedicated empty outer directory outside the
skill repository. Its leaf name must differ from `<ModName>`; the Mod resource tree may
later use `<project-dir>/<ModName>/`.

```powershell
dotnet --version
python ${CLAUDE_PLUGIN_ROOT}/tools/scaffold.py `
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
- `<ModName>.json` with only `STS2-RitsuLib >= 0.4.62`, `min_game_version=0.107.1`,
  `has_dll=true`, and `has_pck=false` for the empty scaffold;
- `Sts2PathDiscovery.props` plus optional `local.props` support;
- `<ModName>Code/MainFile.cs`, whose exact load marker records public RitsuLib version
  metadata and the actual loaded `Sts2ApiCompat` assembly metadata.

RitsuLib is installed as its own runtime Mod from either the matching
`STS2.RitsuLib.Compat.0.107.1.0.4.62.github.zip` or the verified variant pack. Never copy
`STS2-RitsuLib.dll` into `<ModName>`.

When authoring adds localization, images, or scenes, place them under
`<project-dir>/<ModName>/` and set `has_pck=true`. `build.py` packs that resource tree with
the shared open-mod packer; there is no framework-specific PCK branch.

## 3. Record state

Write the absolute project path and profile id to `MEMORY.md`, mark `scaffold` done in
`PLAN.md`, and continue to `author.md`. Do not build before the selected content and
diagnostics are authored.
