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
part of the published skill). **Three hard rules — skip any and you get a split,
polluted layout that costs several tool calls to untangle (real M4 rework):**

1. **The template outputs into the CURRENT directory, not a subfolder.** So `cd`
   into a dedicated **empty** outer folder first, then run `dotnet new` there. Never
   run it from a directory that already holds other projects (it scatters the csproj,
   `<ModName>Code/`, manifest, `project.godot` across that directory).
2. **The outer folder name must NOT equal `<ModName>`.** The template creates a
   *resource* subdir also named `<ModName>` (holding `localization/`, `images/`), so
   an outer folder of the same name collides on case-insensitive filesystems
   (Windows/macOS). Use a distinct name like `<modname>-mod` (M1's `m1-gamblers-coin`
   ≠ `GamblersCoin` is why it worked).
3. **If SPEC/PLAN/MEMORY were written in step 2, put them in that outer folder** and
   `cd` in before scaffolding — don't create a `<ModName>/` dir for them (it clashes
   with rule 2 and the template's resource subdir).

```powershell
mkdir <modname>-mod            # dedicated, empty, name != <ModName>
cd <modname>-mod               # template writes into CWD
# Character Foundation:
dotnet new alchyrsts2charmod -n <ModName> -M <Author>
# Every other supported element:
dotnet new alchyrsts2contentmod -n <ModName> -M <Author>
```

Run exactly one template command based on SPEC; do not scaffold both into one directory.

- `<ModName>`: PascalCase, **no spaces** (from SPEC `mod name`). Becomes the
  csproj/assembly name, the `mods/<ModName>/` folder, and the manifest `id`.
- `-M <Author>`: author string (SPEC `author`, default `OpenMod`).

The template lays out (confirmed from the M1 golden mod):
- For `element: character`, `alchyrsts2charmod` additionally scaffolds
  `<ModName>Code/Character/` with the `PlaceholderCharacterModel` shell and all three
  `Custom*PoolModel` classes, character-scoped card/relic/potion bases, `characters.json`,
  `ancients.json`, and placeholder character UI images. Keep that structure and follow
  `recipes/character.md`; never add a manual `AddCharacter` call.
- If SPEC selects a separately grounded advanced capability adapter, keep the same chosen
  template. AUTHOR may add `<ModName>Code/CapabilityKernel/` plus thin `Domain/` code per
  `reference/capability-kernel.md`; do not scaffold or depend on `OpenMod.Runtime`.
- A selected character resource adds only its `Domain/` module, gain/spend host cards,
  and the exact `CapabilityKernel/` combat-UI adapter. A selected custom zone adds
  `Zones/`, its `Domain/` transition/composition module, and source/output cards. Do not
  add a generic capability framework or unselected module.
- `<ModName>.csproj`, `<ModName>.json` (manifest), `project.godot`, `Sts2PathDiscovery.props` at the ROOT.
- For the content template, `<ModName>Code/` is C# source with `MainFile.cs` and per-type folders
  (`Relics/`, `Cards/`, `Powers/`, ...). `<ModName>Code/Relics/<ModName>Relic.cs`
  is the mod's relic base class (resolves image paths); your concrete relic
  extends it. `<ModName>Code/Cards/<ModName>Card.cs` is the mod's **card base
  class** (also scaffolded — resolves card portrait paths); your concrete card
  extends it. **Note:** the content template has **no `Potions/` folder or base class** — a potion
  mod creates both in `author.md` (see `recipes/potion.md` "Scaffold difference").
  The character template already includes its character-scoped potion base.
  Powers need no base class (auto-discovered; see `recipes/power.md`). Events are not
  scaffolded either: an event mod creates `<ModName>Code/Events/` and its
  `CustomEventModel` class in `author.md` (see `recipes/event.md`); no shared event base
  class is needed.
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
