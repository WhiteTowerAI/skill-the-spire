# Scaffold - create the local-runtime RitsuLib project

Generate the smallest pinned STS2 project for the accepted SPEC. Require .NET SDK 9 and Python 3.
Use the dedicated outer directory outside the skill repository that already holds `DESIGN.md` and
`SPEC.md` (and `PLAN.md`/`MEMORY.md` when present); its leaf name must differ from `<ModName>`.

```powershell
dotnet --version
python ${GAME_TOOLS_DIR}/scaffold.py `
  --project-dir <absolute-outer-directory> `
  --mod-name <ModName> `
  --author <Author> `
  --game-dir <STS2-install-directory> `
  --runtime-dir <optional-installed-RitsuLib-directory>
```

`<ModName>` is a C# identifier without spaces. The generator accepts a directory that holds only
those four files, leaves them untouched, refuses any other existing entry, and never overwrites a
project. It owns the csproj, the bundled build SDK, local game/RitsuLib references, the
`mod_manifest.json` dependency floor, path discovery, and the framework identity the load marker
reports; never hand-edit or copy those from another template, never add BaseLib or a
`PackageReference` to a framework, and never use the default beta-facing `STS2.RitsuLib` package.

## What you author into

- `<ModName>Code/`: all C# source. `MainFile.cs` holds the load marker and the self-test arming
  line; add content only through the `RegisterContent()` partial in `MainFile.Content.cs`.
- `<ModName>Code/SelfTestKit.cs`: the fixed Tier 2 kit; never edit it
  (`scaffold.py --refresh-selftest-kit` rewrites it). The Mod's own checks go in
  `SelfTestScenarios.cs`.
- `<ModName>/`: the resource tree (localization, images, scenes). When it gains any file, set
  `has_pck=true` in `mod_manifest.json`; Build packs it into the `.pck`.
- `mod_manifest.json`: keep its name and `affects_gameplay=true` (RitsuLib treats a Mod declaring
  `false` as local-only, so its models get no network identity and synced actions such as
  right-click never send).
- `skillthespire/vanilla-overrides.json`: the vanilla override manifest, pinned to the checked
  catalog with an empty `operations` array. Fill it only through the override references; it is a
  build-time input that stays in the project and is never deployed.

RitsuLib stays a separate runtime Mod, found in the game `mods/` directory or official Workshop
item `3747602295`. Install the complete matching folder only when neither exists (the root
`STS2-RitsuLib.dll` is just a loader; `compat/`, `shared/`, and `assets.zip` are required), and
never copy any RitsuLib file into `<ModName>`.

## When the installed RitsuLib changes

The Workshop item updates on its own; Build then stops instead of compiling against different
assemblies. Read the RitsuLib release notes for the versions in between, then re-pin:

```powershell
python ${GAME_TOOLS_DIR}/scaffold.py `
  --project-dir <existing-project-directory> `
  --mod-name <ModName> `
  --game-dir <STS2-install-directory> `
  --repin-runtime
```

Re-pinning rewrites only the recorded compile version and module digest, never the profile,
authored sources, or the player's minimum dependency. Build and Tier 2 run again before the Mod is
reported as working on the new runtime.

## Record state

Write the project path and profile to `MEMORY.md` § Project (template in `spec.md`), mark
`scaffold` done in `PLAN.md`, and continue to `author.md`. Build only after the selected content
and diagnostics are authored.
