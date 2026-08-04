# M0 De-Risk Results

> Companion to IMPLEMENTATION_PLAN.md §5–7. Records the outcome of the M0
> de-risk step: manual, on-machine validation of the two gating risks (R1, R2)
> before committing to the full skill build. Run 2026-07-01 on a Windows box
> with STS2 v0.107.1 + .NET 9.0.300 + MegaDot 4.5.1 + BaseLib installed.

## Verdict: M0 GATE PASSED

Both gating risks are now **empirically confirmed**, not just "achievable on
paper." R1 (CLI build of `.dll`+`.pck`) and R2 tier-1 (load verification via log
marker) both work end-to-end, headlessly and scriptably. → Proceed to M1.

## Method

A throwaway probe mod was scaffolded (outside this repo) with the official
template:
```
dotnet new install Alchyr.Sts2.Templates
dotnet new alchyrsts2contentmod -n ProbeMod -M OpenMod
```
Note: the template puts `ProbeMod.csproj` / props / `ProbeModCode/` at the
project ROOT; the `ProbeMod/` subfolder holds only resources (localization,
placeholder images). The probe registers **no actual content** — it is an empty
but structurally complete mod, enough to prove "builds + loads + initializes."

## R1 — CLI build/publish of `.dll` + `.pck`

**Verdict: LOW RISK, confirmed. Two working paths.**

### Path A — PckPacker (recommended; no MegaDot)
Uncomment in the `.csproj`:
```xml
<PackageReference Include="BSchneppe.StS2.PckPacker" Version="0.1.1" PrivateAssets="All" />
```
Then a plain build emits **both** `.dll` and `.pck` into the game `mods/` folder:
```
dotnet build ProbeMod.csproj -c Release
```
No dependency on the 1.5 GB MegaDot editor. The `.pck` contains only resources.
This is the intended main path for single-element mods.

### Path B — MegaDot publish (fallback for complex assets)
```
dotnet publish ProbeMod.csproj -c Release --property:GodotPath=D:/Megadot/MegaDot_v4.5.1-stable_mono_win64.exe
```
Works, with two caveats:
1. A real `.sln` must exist, or Godot's export warns "no solution file" and the
   export target exits with code -1 (non-fatal — `ContinueOnError="WarnAndContinue"`).
   Create one: `dotnet new sln -n ProbeMod && dotnet sln ProbeMod.sln add ProbeMod.csproj`.
2. Godot's export bundles the `.cs` source files into the `.pck` too (larger pck).

### Gotchas recorded
- Pass MSBuild props as `--property:Name=Value`. The `/p:Name=Value` form gets
  mangled by shell quoting on this setup (fails with MSB1008).
- STS2 path auto-discovery (`Sts2PathDiscovery.props`) correctly located the game
  at `D:\Steam` via the registry — no `Sts2Path` override needed.
- Only the default `GodotPath` (`C:/megadot/...`) is wrong for our layout
  (`D:\Megadot\...`); override it or edit `Directory.Build.props`.

## R2 tier 1 — load verification via log marker

**Verdict: LOW RISK, confirmed. Works end-to-end.**

1. Injected a marker at the end of `MainFile.Initialize()`:
   ```csharp
   Logger.Info("[T2MOD-SELFTEST] ProbeMod loaded ok");
   ```
2. Created `steam_appid.txt` containing `2868840` in the game dir, launched
   `SlayTheSpire2.exe` directly (no Steam), waited, then closed it.
3. Grepped `%APPDATA%\SlayTheSpire2\logs\godot.log`. The full load chain appeared,
   with zero ProbeMod errors:
   ```
   Found mod manifest file ...\mods\ProbeMod\ProbeMod.json
   Loading assembly DLL ...\ProbeMod\ProbeMod.dll
   Loading Godot PCK ...\ProbeMod\ProbeMod.pck
   Calling initializer method ...MainFile for ProbeMod
   [ProbeMod] [T2MOD-SELFTEST] ProbeMod loaded ok
   Finished mod initialization for 'ProbeMod' (ProbeMod).
   [BaseLib] Mod ProbeMod that modifies gameplay ... gameplay modification enabled.
   ```

This proves the "installs + loads + registered" tier — the exact class of failure
that makes raw-AI mods fail — can be verified automatically. The marker appears
**after** BaseLib's own load lines, so grep the whole log, not just a prefix.

### Observed in-game (expected)
STS2's Mod Settings menu lists only mods with content/config (BaseLib appears;
ProbeMod does not, because it registers nothing). ProbeMod **does** appear in the
"loaded mods" indicator. "Loaded" and "has content" are distinct: M0 validates
loading; content is M1's job.

## What is NOT yet validated

- **R2 tier 2 — behavior verification** ("did the effect actually fire?"). This is
  the headline differentiator and remains the next frontier. Candidate mechanisms
  (to pick during M1): a Godot `SceneTree` test script vs. reusing STS2MCP live
  state. Never claim an effect was verified when only load was.

## Next step: M1

Hand-build ONE complete relic mod end to end (the "Gambler's Coin" example):
scaffold → author a real relic (inheriting BaseLib's `CustomRelicModel`) →
build → loads in-game → self-test passes → effect works. This becomes the
reference the recipe is distilled from.
