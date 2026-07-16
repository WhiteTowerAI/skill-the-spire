# M1 Golden Mod Results

> Companion to IMPLEMENTATION_PLAN.md §5 (M1) and M0_RESULTS.md. Records the
> outcome of M1: hand-building ONE complete relic mod end to end — the
> "Gambler's Coin" — to serve as the reference the `recipes/relic.md` pattern is
> distilled from and the acceptance target for the skill. Run 2026-07-01 on the
> same Windows box as M0 (STS2 v0.107.1 + .NET 9.0.300 + BaseLib 3.3.2).

## Verdict: M1 GATE PASSED — tier-1 AND tier-2

For the first time, hand-authored gameplay content was verified **loading and
actually firing in a real combat** — not "it compiled." This clears the headline
differentiator (behavior verification on observed reality) that M0 left open.

- **R1 build:** clean, PckPacker path, `.dll`+`.pck` in `mods/`.
- **R2 tier-1 (loads):** load-marker greppable, 0 errors, 245 BaseLib patches OK.
- **R2 tier-2 (effect fires):** in-combat log proof, matched what the user saw.

## The mod: "Gambler's Coin"

A **Common** relic. At the start of each combat (turn 1), flip a seeded coin:
- **Heads** → double your current Energy.
- **Tails** → lose all your Energy.

Chosen because it exercises the three hardest things a relic can need — a
combat-lifecycle hook, energy mutation, and seeded RNG — in one small, legible
element. Project (outside this repo, like the M0 probe):
`D:\26summer_intern\m1-gamblers-coin`, scaffolded with
`dotnet new alchyrsts2contentmod -n GamblersCoin -M OpenMod`.

## Method — scaffold → author → build → verify

### Author (the real work)
All APIs were confirmed against the **decompiled `sts2.dll`** (3425 files via
`ilspycmd` → `D:\26summer_intern\decomp\sts2_full`) and **BaseLib 3.3.2**, not
guessed. The vanilla relic `Lantern` is a near-exact structural twin (combat-start
energy grant) and was used as the template; `FurCoat` confirmed the RNG idiom. The
full API reference is distilled into `sts2-api/recipes/relic.md`.

The concrete relic overrides `AfterSideTurnStart`, guards on
`participants.Contains(Owner.Creature) && Owner.PlayerCombatState.TurnNumber <= 1`,
flips `new Rng(Owner, Id).NextBool()`, then either `PlayerCmd.GainEnergy(current,
Owner)` (double) or `PlayerCmd.SetEnergy(0m, Owner)` (bust). It carries a
`[Pool(typeof(SharedRelicPool))]` attribute (required by BaseLib) and a
`relics.json` with the prefixed flat loc keys.

### Build (R1)
`dotnet build -c Release` with `BSchneppe.StS2.PckPacker` uncommented in the
csproj → **0 warnings, 0 errors**; `.dll` + `.pck` + `.json` + `.pdb` auto-copied
to `D:\Steam\...\Slay the Spire 2\mods\GamblersCoin\`. The build target also
auto-resolved the manifest's BaseLib `min_version` to the active `3.3.2`.

### Verify tier-1 (loads)
Launched `SlayTheSpire2.exe` via the M0 `steam_appid.txt` (no Steam). Game-dir
`mods/` auto-discovery picked it up exactly like the M0 ProbeMod. Log chain:
```
Found mod manifest file ...\mods\GamblersCoin\GamblersCoin.json
Loading assembly DLL ...\GamblersCoin\GamblersCoin.dll
Loading Godot PCK ...\GamblersCoin\GamblersCoin.pck
Calling initializer method ...MainFile for GamblersCoin
[GamblersCoin] [T2MOD-SELFTEST] GamblersCoin loaded ok
Finished mod initialization for 'GamblersCoin' (GamblersCoin).
 --- RUNNING MODDED! --- Loaded 4 mods (4 total)
[BaseLib] Applied 245 patches successfully, 0 failed
```

### Verify tier-2 (effect fires) — the headline
STS2 ships a **dev console** that auto-enables debug commands when running modded
(`NDevConsole`: `shouldAllowDebugCommands = ... || ModManager.IsRunningModded()`).
Opened with the **`` ` `` (backtick)** key (also `'`, `*`, `^`, or `Shift+8`),
closed with `Esc`. In an active run, `relic add GAMBLERSCOIN-GAMBLERS_COIN`
granted the relic, then entering combat produced, at turn 1:
```
DevConsole: relic add GAMBLERSCOIN-GAMBLERS_COIN
[GamblersCoin] [T2MOD-SELFTEST] GamblersCoin fired: TAILS (bust) energy 3 -> 0
```
The relic flashed and energy dropped 3 → 0 in-game, matching the log. **This is
the first empirical proof of an effect firing**, achieved with a code-injected
marker on observed state (`before -> after`), not an assumption.

## Findings that shaped the game pack

- **The `dev console` is the cheap tier-2 lever.** `relic add <fuzzy-id>`,
  `energy`, etc. are all live when modded. Scripting console commands is far
  lighter than a SceneTree harness or STS2MCP for behavior tests — this reshapes
  the M5 tier-2 mechanism decision toward "drive the dev console."
- **Localization key derivation is a real footgun** and the single most likely
  silent failure for an LLM: `Id.Entry` = `Slugify(ClassName)` uppercased, then
  BaseLib prepends `<ROOT_NAMESPACE_UPPER>-`. See `recipes/relic.md` +
  `errors.md`.
- **`[Pool]` is mandatory** — BaseLib throws at registration without it. Easy to
  omit; now a checklist item in the recipe.

## What is NOT yet validated

- **The HEADS (double) branch.** RNG is deterministic per (run seed, relic id),
  so the observed flip was TAILS; the double path is written and type-correct but
  has not been observed firing. A follow-up (force the seed or run multiple
  combats) should capture `HEADS (double) energy X -> 2X` to close the loop.
- **Natural drop.** The relic was granted via console, not dropped from a reward;
  pool membership is asserted by `[Pool]` + BaseLib registration but not yet seen
  organically.

## Next step: M2

Distill the pipeline into the skeleton skill (orchestrator `SKILL.md` +
interview/spec/scaffold/author/build/verify stages) driving the seeded
`recipes/relic.md`, and reproduce this exact relic from one sentence with no
repair needed.
