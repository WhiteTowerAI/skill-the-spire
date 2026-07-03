# Scaffold — create the mod project skeleton

Goal: produce a compilable, empty STS2 content-mod project via the Alchyr
template, wire the manifest, and enable the `.pck` build. No effect logic yet.

## 0. Toolchain check (once)

```powershell
dotnet --version          # need 9.0+
dotnet new list | Select-String alchyr   # is the template installed?
```

If the template is missing, install it once:

```powershell
dotnet new install Alchyr.Sts2.Templates
```

## 1. Scaffold

Pick a work location OUTSIDE this skill repo (the mod is the user's artifact, not
part of the published skill). Then:

```powershell
dotnet new alchyrsts2contentmod -n <ModName> -M <Author>
```

- `<ModName>`: PascalCase, **no spaces** (from SPEC `mod name`). Becomes the
  csproj/assembly name, the `mods/<ModName>/` folder, and the manifest `id`.
- `-M <Author>`: author string (SPEC `author`, default `OpenMod`).

The template lays out (confirmed from the M1 golden mod):
- `<ModName>.csproj`, `<ModName>.json` (manifest), `project.godot`, `Sts2PathDiscovery.props` at the ROOT.
- `<ModName>Code/` — C# source, with `MainFile.cs` and per-type folders
  (`Relics/`, `Cards/`, `Powers/`, ...). `<ModName>Code/Relics/<ModName>Relic.cs`
  is the mod's relic base class (resolves image paths); your concrete relic
  extends it. `<ModName>Code/Cards/<ModName>Card.cs` is the mod's **card base
  class** (also scaffolded — resolves card portrait paths); your concrete card
  extends it. **Note:** there is **no `Potions/` folder or base class** — a potion
  mod creates both in `author.md` (see `recipes/potion.md` "Scaffold difference").
  Powers need no base class (auto-discovered; see `recipes/power.md`).
- `<ModName>/` — resources: `localization/eng/*.json`, `images/...`.

## 2. Enable the `.pck` (PckPacker)

The template ships the PckPacker package reference **commented out**. Localization
and images only reach the game through the `.pck`, so uncomment it in the csproj:

```xml
<PackageReference Include="BSchneppe.StS2.PckPacker" Version="0.1.1" PrivateAssets="All" />
```

(This is errors.md's first entry — "no .pck produced". Do it now, not after a
failed verify.) No MegaDot needed; plain `dotnet build` then emits the `.pck`.

## 3. Manifest (`<ModName>.json`)

Confirm/set:
- `id`, `name` = `<ModName>`; `author` = SPEC author.
- `description` = a one-line human description of the mod.
- `has_pck: true`, `has_dll: true`, `affects_gameplay: true`.
- `dependencies`: keep the `BaseLib` entry. The csproj auto-resolves `min_version`
  to the installed BaseLib at build time — don't hand-edit it.
- `min_game_version`: leave the template default unless the user targets a specific build.

## 4. Record the path

Write the project's absolute path into `MEMORY.md` (build/verify need it). Mark
`scaffold` done in `PLAN.md`, then go to `author.md`.

Do NOT build yet — there's no effect and no marker until `author.md`.
