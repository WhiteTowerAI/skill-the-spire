# R1 / R2 Feasibility: The Two Gating Risks

> Companion to PROJECT.md §12 and BASELINE_RESEARCH.md. These two risks decide
> whether the whole "one sentence → working, auto-tested mod" promise is
> achievable via a headless, no-human CLI pipeline. Analyzed 2026-07-01 from the
> actual ModTemplate-StS2 build files + BaseLib docs. Verdicts below are
> "achievable on paper"; each ends with a concrete on-machine prototype to run.

---

## R1 — Headless / CLI publish of `.dll` + `.pck` (no IDE)

### Verdict: LOW RISK. The template already does it headless.

The `.csproj` (`Godot.NET.Sdk/4.5.1`) settles it — Rider's "Publish" button just
triggers plain MSBuild targets. Key evidence from `CharMod.csproj`:

- **`GodotPublish` target runs Godot headless itself:**
  ```
  "$(GodotPath)" --headless --export-pack "BasicExport" "<ModsPath>/<Mod>.pck"
  ```
  It already passes `--headless`. No GUI. Fires `AfterTargets="Publish"`.
- **`CopyToModsFolderOnBuild`** (`AfterTargets="PostBuildEvent"`) copies
  `.dll` + `.json` (+ `.pdb`) into `<ModsPath>/<Mod>/` on a normal build.
- **`GodotPath` is a plain MSBuild property** in `Directory.Build.props`
  (default `C:/megadot/MegaDot_v4.5.1-stable_mono_win64.exe`), overridable with
  `/p:GodotPath=...`.
- **`Sts2PathDiscovery.props` auto-locates the game** via registry + Steam
  library, for **Windows / Linux / macOS**, computing `Sts2Path`, `ModsPath`,
  `Sts2DataDir`. Overridable with `/p:Sts2Path=...`.
- **`UpdateDependencyVersions`** auto-syncs the BaseLib `min_version` in the
  manifest to the actually-restored BaseLib version — removes a common footgun.
- **`CheckDependencyPaths` / `NeedGodotForPublish`** fail fast with clear errors
  if the game data or Godot path is missing — good signals for our error handler.

**So the whole publish is, in principle, one command:**
```
dotnet publish /p:GodotPath="<path to MegaDot exe>"
# → compiles .dll (copied to mods), then headless-exports .pck to mods
```
Code-only changes can use the faster `dotnet build` (just the `.dll`).

### The shortcut worth trying first: PckPacker (no Godot at all)
The csproj ships a commented-out package:
```
<PackageReference Include="BSchneppe.StS2.PckPacker" Version="0.1.1" PrivateAssets="All" />
```
Comment: *"Generates a .pck file when building if only using simple assets."*
For single-element mods (one card = a few PNGs + JSON), this likely suffices and
means **`dotnet build` alone produces `.dll`+`.pck` with NO MegaDot dependency**
(a `CopyQuickPck` target handles the copy). Huge simplification if it holds.

### Residual unknowns (only real-machine can answer)
1. Does `--export-pack "BasicExport"` succeed headless, or does it need export
   templates installed for MegaDot? (Preset name `BasicExport` comes from
   `export_presets.cfg`.)
2. Does PckPacker cover our asset set, or do we fall back to MegaDot?
3. Does `dotnet publish` on the SDK-style Godot project behave the same as the
   IDE "Publish" (esp. the `IsInnerGodotExport` re-entrancy guard)?

### Prototype R1 (do this first, needs game + .NET 9 + MegaDot installed)
1. `dotnet new install Alchyr.Sts2.Templates`
2. `dotnet new <content-template> -n ProbeMod` (name, no spaces)
3. `dotnet build` → confirm `ProbeMod.dll` + `ProbeMod.json` land in `mods/`.
4. `dotnet publish /p:GodotPath="…MegaDot…"` → confirm `ProbeMod.pck` appears.
5. Separately, uncomment PckPacker, `dotnet build`, and see if `.pck` appears
   WITHOUT MegaDot. Record which path we standardize on.
6. Launch the game, confirm ProbeMod shows in Settings → Mod Settings.

---

## R2 — Automated in-game verification (the headline differentiator)

### Verdict: MEDIUM–HIGH RISK, but a viable path exists. Prototype early.

There is **no headless test mode** for STS2 and BaseLib provides **no test/QA
API** (confirmed from BaseLib's Features list). Unlike GodotMaker (which uses
`godot --headless` + gdUnit4 + screenshots), we must verify by launching the
real client and observing. What we DO have (all confirmed):

- **Launch without Steam:** `steam_appid.txt` = `2868840` in the game dir → run
  `SlayTheSpire2.exe` directly (scriptable).
- **Logs are the observation channel:** `godot.log` at
  `%appdata%/SlayTheSpire2/logs` (Win). Mods log via
  `MainFile.Logger.Info(...)`. BaseLib logs missing-localization as an **error
  rather than crashing** → errors are greppable, not fatal.
- **Dev console** can spawn any content (`` ` ``, then `card`, `relic`, …) — but
  it's key-driven and stateful (need to be in a run).
- **Rich launch args:** `-nomods`, `-fastmp …`.

### The design that makes R2 tractable: self-test markers + log assertion
Do NOT rely on scripting the dev console (fragile key injection). Instead, have
**the generated mod prove itself through the log**, in two tiers:

**Tier 1 — Load verification (cheap, high value, almost certainly works):**
- Our scaffolding injects a tiny self-check in `MainFile` init: after
  registering the new element, log a unique marker, e.g.
  `MainFile.Logger.Info("[T2MOD-SELFTEST] registered relic=GamblersCoin ok")`,
  and log any registration exception.
- Pipeline: launch game headless-ish → wait → read `godot.log` → assert the
  marker is present AND no error/exception lines reference our mod → quit.
- This alone catches the overwhelming majority of failures (won't load, missing
  localization, bad manifest, null refs at registration) — i.e. exactly the
  "doesn't install / doesn't run" problems that make raw-AI mods fail.

**Tier 2 — Behavior verification (harder, do after Tier 1):**
- Options, roughly increasing fidelity/effort:
  a. **In-mod effect hook logs a marker** when the effect actually fires
     (e.g. log inside the relic's `OnCombatStart`), then drive the game into a
     minimal combat to trigger it. Still needs *some* way to reach combat.
  b. **Dev-console automation** to spawn the element and step a turn — either
     via a BaseLib debug command, or OS-level input scripting (fragile).
  c. **A dedicated test harness mod** that, under a launch flag, boots a
     synthetic combat, injects our element, ticks the relevant lifecycle event,
     and logs pass/fail markers — the most robust, most work.
- Investigate whether the community dev console has a scriptable/batch entry
  (e.g. run a command file on launch). If yes, (b) becomes much stronger.

### Residual unknowns (real-machine / more research)
1. How far can the game boot "headfully but unattended" on a CI-like machine
   (needs a GPU/display)? Does it run in a minimal/offscreen mode at all?
2. Is there any launch arg or dev-console batch-file mechanism to reach a
   combat state deterministically without human clicks?
3. Does the dev console expose a command to force-add a specific relic/card and
   start a scripted encounter? (Check dev console `help` output on a real box.)
4. Can we ship a reusable "test harness" companion mod that sets up state,
   rather than driving the UI?

### Prototype R2 (do right after R1)
1. Build ProbeMod with a `[T2MOD-SELFTEST]` marker logged at registration.
2. Create `steam_appid.txt`; launch `SlayTheSpire2.exe` from a script; wait N s;
   kill it; grep `godot.log` for the marker and for error lines → this is the
   Tier-1 loop end to end.
3. Explore the dev console `help` list for spawn + scripted-encounter commands;
   determine if Tier-2b is viable or if we need the harness-mod (Tier-2c).
4. Decide MVP scope: **ship Tier 1 as the guaranteed verification; treat Tier 2
   as best-effort** and be honest in the UX about which was checked.

---

## Bottom line for the plan
- **R1 is essentially solved by the existing template** — reduce it to a
  one-command `dotnet publish` (or `dotnet build` + PckPacker). Prototype to
  confirm the two residual unknowns, then wrap it in our build skill.
- **R2 is the real research.** A **Tier-1 load-verification loop (self-test
  marker + log assertion) is low-risk and already delivers our core
  differentiator** over raw-AI modding ("it actually loads and registered").
  **Tier-2 behavior verification is the open frontier** — scope MVP around
  Tier 1, invest in Tier 2 as a fast follow, and never claim an effect was
  verified when only load was.
