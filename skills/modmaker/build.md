# Build — compile to .dll + .pck + .json in mods/

Goal: run the R1 build. On success the `.dll`, `.pck`, and `.json` land in the
game's `mods/<ModName>/` automatically (the template's copy targets). On failure,
capture the real compiler error and go to `repair.md` (the bounded repair loop).

## Run

```bash
python scripts/build.py --project-dir <mod project path from MEMORY.md>
```

This wraps `dotnet build -c Release`. Path discovery (`Sts2PathDiscovery.props`)
resolves the game + mods folders from the registry — no override needed on the dev box.
(The tools are Python so they run the same on Windows/macOS/Linux; invoke with
`python`, not `python3` — on Windows the bare `python3` is often the Store shim.)

## Expect

- `0 warnings, 0 errors`.
- `mods/<ModName>/` now holds `<ModName>.dll`, `<ModName>.pck`, `<ModName>.json`
  (and `.pdb`). The script lists them and warns if the `.pck` is missing.

## If it fails

Go to `repair.md`. It reads the diagnostic lines `build.py` prints (and the full
`<ProjectDir>/.build.log` if needed), keys on the **compiler code + symbol**,
consults sts2-api `errors.md`, applies **one** fix, and rebuilds — bounded to 3
attempts, stopping if the same signature survives. Common M2/M3 hits it knows:

- **No `.pck`, only `.dll`** → PckPacker still commented in the csproj. Uncomment it
  (scaffold.md step 2), rebuild.
- **`CS8602` null deref on `Owner.PlayerCombatState`** → capture once with the
  null-forgiving operator: `var combat = Owner.PlayerCombatState!;`.
- **`CS0246`/`CS0117`/`CS1061` unknown type/member** → a guessed API. Do NOT guess
  again — find the real symbol in the sts2-api pack (the recipe's "Effect building
  blocks", `errors.md`, `reference/mechanics.md`). If the pack genuinely doesn't
  carry it, that's a **pack gap** — report it, don't invent a name.
- **`Slay the Spire 2 data not found`** → the game path didn't resolve; pass it or
  check `Sts2PathDiscovery.props`.

Do not thrash: one change per attempt, and if a fix doesn't move the error, step
back to a different cause rather than tweaking the same spot (see repair.md).

## On success

Mark `build` done in `PLAN.md`, note the mods path in `MEMORY.md`, go to `verify.md`.
