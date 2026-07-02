# Build — compile to .dll + .pck + .json in mods/

Goal: run the R1 build. On success the `.dll`, `.pck`, and `.json` land in the
game's `mods/<ModName>/` automatically (the template's copy targets). On failure,
report the error clearly — **do not loop blindly**; the automated repair loop is M3.

## Run

```powershell
pwsh ${GAME_TOOLS_DIR}/build.ps1 -ProjectDir <mod project path from MEMORY.md>
```

This wraps `dotnet build -c Release`. Path discovery (`Sts2PathDiscovery.props`)
resolves the game + mods folders from the registry — no override needed on the dev box.

## Expect

- `0 warnings, 0 errors`.
- `mods/<ModName>/` now holds `<ModName>.dll`, `<ModName>.pck`, `<ModName>.json`
  (and `.pdb`). The script lists them and warns if the `.pck` is missing.

## If it fails

Read the compiler output and consult the **sts2-api** `errors.md` (query:
"errors.md build-time <signature>"). Common M2 hits:

- **No `.pck`, only `.dll`** → PckPacker still commented in the csproj. Uncomment it
  (scaffold.md step 2), rebuild.
- **`CS8602` null deref on `Owner.PlayerCombatState`** → capture once with the
  null-forgiving operator: `var combat = Owner.PlayerCombatState!;`.
- **`Slay the Spire 2 data not found`** → the game path didn't resolve; pass it or
  check `Sts2PathDiscovery.props`.

Apply the known fix, rebuild **once**. If it still fails, stop and hand the user a
clear summary of the error and what you tried — don't thrash.

## On success

Mark `build` done in `PLAN.md`, note the mods path in `MEMORY.md`, go to `verify.md`.
