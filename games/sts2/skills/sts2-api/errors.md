# errors.md — STS2 mod error → fix catalog

> **Append-only, compounding asset** (IMPLEMENTATION_PLAN.md §3). Every failure the
> repair loop diagnoses becomes a permanent entry: an error *signature* (what you'd
> grep for, or the wrong behavior observed) → the *fix*. Over time this makes the
> repair loop faster and the game pack harder to replicate.
>
> Format per entry: **Signature** (build error text, `godot.log` line, or observed
> symptom) → **Cause** → **Fix**. Newest failures appended at the bottom of their
> section. Seeded from M1 (hand-building Gambler's Coin) and the M0/M1 API dig.

## Build-time (dotnet build / analyzer)

### No `.pck` is produced; only `.dll` copied to `mods/`
- **Signature:** build succeeds but `mods/<ModName>/` has `.dll` + `.json` but no
  `.pck`; localization/images don't show in-game.
- **Cause:** `BSchneppe.StS2.PckPacker` package reference is commented out in the
  csproj (the template ships it commented).
- **Fix:** uncomment
  `<PackageReference Include="BSchneppe.StS2.PckPacker" Version="0.1.1" PrivateAssets="All" />`
  and rebuild. Plain `dotnet build -c Release` then emits both. (No MegaDot needed
  — see sts2-dependency-decisions / M0_RESULTS.md.)

### MSB1008 when passing MSBuild properties
- **Signature:** `MSB1008: Only one project can be specified` on a `dotnet
  publish /p:GodotPath=...` command.
- **Cause:** the `/p:Name=Value` form gets mangled by shell quoting on this setup.
- **Fix:** use `--property:Name=Value` instead.

### Unknown type / member: CS0103, CS0246, CS0117, CS1061 (a guessed API)
- **Signature:** `CS0103: The name '<X>' does not exist in the current context`
  (a bare fabricated name, e.g. `EnergyCmd` — confirmed in M3 testing),
  `CS0246: The type or namespace name '<X>' could not be found`,
  `CS0117: '<Type>' does not contain a definition for '<member>'`, or
  `CS1061: '<Type>' does not contain a definition for '<method>'` — on an STS2 /
  BaseLib symbol you wrote (a Cmd, model, enum, or hook).
- **Cause:** the API name was **guessed from memory**, not confirmed. STS2's Cmd
  and model names don't always match intuition (e.g. energy is `PlayerCmd.GainEnergy`,
  not `EnergyCmd.Add`), and BaseLib wraps some of them.
- **Fix:** do **not** guess a second name — that's how the repair loop burns its
  attempts. Ground the real symbol: query the **sts2-api** skill ("commands for
  <effect>" / "<Type>: real member for <X>"), check `recipes/relic.md`'s "Effect
  building blocks", or look it up in the decompiled `sts2.dll`
  (`D:\26summer_intern\decomp\sts2_full`) / BaseLib decompile. Then use the exact
  name + namespace. Missing `using` for a confirmed type → add the namespace from
  the recipe's import block, not a new guess.

### Nullable warning CS8602 on `Owner.PlayerCombatState`
- **Signature:** `warning CS8602: Dereference of a possibly null reference` on
  `Owner.PlayerCombatState.Energy` (template has `<Nullable>enable</Nullable>`).
- **Cause:** `Player.PlayerCombatState` is typed `PlayerCombatState?` (null outside
  combat), but is guaranteed non-null inside a combat hook.
- **Fix:** capture once with the null-forgiving operator:
  `var combat = Owner.PlayerCombatState!;` then use `combat.Energy`, `combat.TurnNumber`.

### STS001: Localization `<ID>.smartDescription` not found (a custom power)
- **Signature:** build fails with `error STS001: Localization <PREFIX>-<SLUG>.smartDescription
  not found for symbol '<PowerClass>'` — fires on `CustomPowerModel` subclasses, not
  on cards/potions/relics. (Confirmed M4 card round: two powers, both hit this; the
  two cards in the same mod did not.)
- **Cause:** the Alchyr `Sts2ModAnalyzers` package enforces a **required loc-key set
  per model type**, and **powers require three keys** — `.title`, `.description`,
  **and `.smartDescription`**. Writing only `.title/.description` (correct for a card)
  leaves a power short one key. At runtime `PowerModel.SmartDescription` falls back to
  `.description`, but the *build-time* analyzer does not — it hard-fails. Required
  keys by table (read from the analyzer DLL, v0.1.9):

  | table | required keys |
  |-------|---------------|
  | `cards` | `.title`, `.description` |
  | `potions` | `.title`, `.description` |
  | `relics` | `.title`, `.description`, `.flavor` |
  | **`powers`** | `.title`, `.description`, **`.smartDescription`** |

- **Fix:** add `<PREFIX>-<SLUG>.smartDescription` to `powers.json` for each custom
  power (same text as `.description` is fine), then rebuild. See recipes/power.md
  "Localization".

## Registration / load-time (godot.log)

### Exception at registration: model must be marked with a PoolAttribute
- **Signature:** startup exception mentioning `... must be marked with a
  PoolAttribute to determine which pool to add it to` (thrown from
  `CustomContentDictionary.AddModel`).
- **Cause:** a `CustomRelicModel` subclass has no `[Pool(...)]` attribute. BaseLib
  auto-registers custom models in their ctor and requires the pool to be declared.
- **Fix:** add `[Pool(typeof(SharedRelicPool))]` (or a character pool) to the class.
  `using BaseLib.Utils;` for the attribute, `using MegaCrit.Sts2.Core.Models.RelicPools;`
  for the pool types.

## Localization

### Relic shows blank / raw-key title or description in-game
- **Signature:** hover shows the loc key literally (e.g. `GAMBLERSCOIN-GAMBLERS_COIN.title`)
  or empty text instead of the intended string.
- **Cause:** the `relics.json` key doesn't match the relic's actual `Id.Entry`.
  Two common mistakes: (a) using nested JSON `{"MyRelic": {"title": ...}}` — the
  `relics` LocTable is a **flat** `Dictionary<string,string>`; (b) forgetting the
  BaseLib namespace prefix, or mis-deriving the CamelCase→UPPER_SNAKE slug.
- **Fix:** keys must be flat and exactly `<PREFIX>-<SLUG>.title` where
  `SLUG = Slugify(ClassName)` (CamelCase split + UPPERCASE) and
  `PREFIX = <first-namespace-segment>.ToUpperInvariant()`. Worked example: class
  `GamblersCoin` in namespace `GamblersCoin.*` → `GAMBLERSCOIN-GAMBLERS_COIN.title`.
  See recipes/relic.md "ID / loc-key derivation rule". To pin an exact id, use
  `[CustomID("...")]`.

### Relic icon is the generic placeholder, not the intended art
- **Signature:** `godot.log` line `Could not find relic image path: .../<name>.png`;
  relic shows the fallback `relic.png`.
- **Cause:** the icon file name must be the **prefix-stripped, lowercased** entry
  (`RemovePrefix().ToLowerInvariant()`), not the class name.
- **Fix:** place art at `images/relics/<slug>.png` where `<slug>` = the entry after
  removing the `PREFIX-` (e.g. `gamblers_coin.png`), plus `<slug>_outline.png` and
  `big/<slug>.png`. During early milestones, copying the template placeholder to
  that exact name silences the warning.

## Behavior (tier-2 / effect logic)

### Energy granted at combat start disappears
- **Signature:** relic meant to add energy at combat start has no effect; energy is
  whatever the normal turn-1 amount is.
- **Cause:** energy was granted in `BeforeCombatStart()`, which runs before the
  turn-1 energy reset (`PlayerCombatState` resets to max at turn start) — the grant
  is overwritten.
- **Fix:** grant in `AfterSideTurnStart` guarded by `TurnNumber <= 1` instead. This
  is exactly how vanilla `Lantern` does it.

### Relic effect fires for the wrong player / every turn
- **Signature:** in multiplayer the effect triggers off the wrong side; or a
  "combat start" effect re-fires each turn.
- **Cause:** missing guards in `AfterSideTurnStart` — the hook fires for every side
  and every turn.
- **Fix:** guard with both `participants.Contains(Owner.Creature)` (right owner) and
  `Owner.PlayerCombatState!.TurnNumber <= 1` (combat start only).

## Verification harness (launch / console)

### Dev console won't open in-game
- **Signature:** pressing the console key does nothing.
- **Cause/Fix:** open with **`` ` `` (backtick)** — also `'`, `*`, `^`, or `Shift+8`;
  close with `Esc`. Debug commands (like `relic add`) are only enabled when the
  game is **running modded** (`ModManager.IsRunningModded()`), which is true whenever
  at least one gameplay mod is loaded. If commands are missing, confirm the game
  actually loaded a mod (grep log for `RUNNING MODDED`).

### `relic add` says "Unable to create relic '<id>'"
- **Signature:** dev console `relic add <id>` returns the not-found message.
- **Cause:** the id doesn't match any `Id.Entry` (matching is `Contains`, uppercased).
- **Fix:** use the derived entry, e.g. `relic add GAMBLERSCOIN-GAMBLERS_COIN` (or a
  unique substring like `GAMBLERS`). Confirm the mod loaded first (grep log).

### Tier-1 verify: marker NOT FOUND but `RUNNING MODDED` = YES (mod loaded, logged nothing)
- **Signature:** `grep_log.ps1` reports `RUNNING MODDED flag : YES` and no
  mod-named errors, yet `Tier-1 load marker : NOT FOUND`. The mod loaded fine — it
  simply never logged `[T2MOD-SELFTEST] <ModName> loaded ok`.
- **Cause:** the load marker was **not injected** into `MainFile.Initialize()`. The
  Alchyr template's `MainFile.cs` logs nothing by default (this bit M2 — it was a
  doc bug in author.md). A second cause: the marker WAS added in source but the code
  change **wasn't rebuilt**, so the stale `.dll` in `mods/` has no marker.
- **Fix:** add `Logger.Info("[T2MOD-SELFTEST] <ModName> loaded ok");` at the end of
  `MainFile.Initialize()` (right after `harmony.PatchAll();`), per author.md step 2,
  then **rebuild** (`build.md`) so the fresh `.dll`/`.pck` reach `mods/`, and
  re-verify. Distinct from the log-rotation false-FAIL below: there the marker is
  present in the log but the grep sliced past it; here the marker was never written.

### Tier-1 verify reports [FAIL] "load marker missing" but the mod actually loaded
- **Signature:** `grep_log.ps1` says the `[T2MOD-SELFTEST] ... loaded ok` marker is
  missing, yet reading the raw `godot.log` shows the marker near the top and the mod
  works in-game. A non-programmer would wrongly conclude their mod is broken.
- **Cause:** slicing the log by a pre-launch **byte offset**. STS2 archives the
  previous log to `godot<timestamp>.log` and starts a **fresh** `godot.log` on every
  launch. An offset captured from the old file lands in the middle of the new file
  (past the startup lines where the marker is), so the grep reads only the tail.
  This bit us in two flavors: new file shorter than the offset (caught by a rotation
  guard) AND new file longer (the guard missed it → false FAIL).
- **Fix:** do NOT offset-slice. STS2's rotation guarantees the current `godot.log`
  holds exactly one run, so read the **whole current file**. `grep_log.ps1` now takes
  only `-ModName` (no `-SinceOffset`); `launch.ps1` no longer emits an offset.
