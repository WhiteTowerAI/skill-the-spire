# errors.md — STS2 mod error → fix catalog

> **Append-only, compounding asset.** Every failure the
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
  and rebuild. Plain `dotnet build -c Release` then emits both through PckPacker;
  no MegaDot step is needed.

### PckPacker skips a mod that contains raw `.tscn`
- **Signature:** `dotnet build` succeeds, PckPacker reports a skipped unsupported `.tscn`,
  and the installed PCK is absent or stale.
- **Cause:** upstream PckPacker 0.1.1 hardcodes `.tscn` as unsupported even though STS2
  0.107.1 loads bounded raw text scenes from the same format-v3 PCK.
- **Fix:** run `scripts/build.py`, not bare `dotnet build`/`publish`. It detects
  `<project>/<ModName>/**/*.tscn` and invokes bundled `pack_pck.py` automatically. Do not
  install Godot/MegaDot. `.gdshader`, `.gdscript`, and `.gdextension` remain unsupported.

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
  attempts. Ground the real symbol **in the pack**: query the **sts2-api** skill
  ("commands for <effect>" / "<Type>: real member for <X>"), check `recipes/relic.md`'s
  "Effect building blocks", `reference/mechanics.md`, and `reference/build-constraints.md`.
  Then use the exact name + namespace. Missing `using` for a confirmed type → add the
  namespace from the recipe's import block, not a new guess. If the symbol is genuinely
  absent from the pack, that's a **pack gap** — report it (the maintainer grounds new
  symbols offline per `grounding.md`); don't invent one at runtime.

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
- **Master reference:** the complete required-loc table (incl. characters/keywords)
  and the full analyzer diagnostic set live in `reference/build-constraints.md`. The
  analyzer defines exactly **STS001–STS004** (mined from `Sts2ModAnalyzers.dll` 0.1.9
  — no STS005+): STS001 missing required loc key (this entry, the only *error* of the
  loc rules), STS002 loc files not registered as analyzer additional files, STS003
  model doesn't inherit a `CustomModel`, STS004 poolable model (card/potion/relic,
  **not power**) missing `[Pool]` (see the PoolAttribute entry below).

### STS001: four `THE_ARCHITECT.talk.<CHAR_ID>` keys missing (a custom character)
- **Signature:** build fails on the character symbol and lists
  `THE_ARCHITECT.talk.<CHAR_ID>.0-0r.char`, `.0-0r.next`, `.0-1r.ancient`, and
  `.0-attack` as missing, even when the 14 `characters` values are supplied through
  `CharacterLoc`.
- **Cause:** `CharacterModel` localization spans two tables. `CharacterLoc` satisfies
  `characters`, but the analyzer independently requires four Architect conversation
  entries from `ancients`.
- **Fix:** add those exact four flat keys to `localization/eng/ancients.json`, using the
  character's final `Id.Entry`, then rebuild. See `recipes/character.md` and
  `reference/build-constraints.md` section 2a.

## Registration / load-time (godot.log)

> These are the load-time twins of build §1. A card/potion/relic model
> **self-registers in its constructor** (`CustomContentDictionary.AddModel(GetType())`),
> so BaseLib throws the moment the element is instantiated during load, aborting that
> mod's init. The complete throw set + the STS004-vs-throw relationship is in
> `reference/build-constraints.md` §3.

### Exception at registration: model must be marked with a PoolAttribute
- **Signature:** startup exception mentioning `Model <FullName> must be marked with a
  PoolAttribute to determine which pool to add it to` (thrown from
  `CustomContentDictionary.AddModel`).
- **Cause:** a `CustomCardModel` / `CustomPotionModel` / `CustomRelicModel` subclass
  has no `[Pool(...)]` attribute. BaseLib auto-registers these three poolable models in
  their ctor and requires the pool to be declared. (Build warning **STS004** flags this
  too but does not fail the build, so it can reach load — treat STS004 as load-bearing.
  **Powers are exempt**: `CustomPowerModel` doesn't self-register, so it never throws
  here.)
- **Fix:** add the `[Pool(typeof(<XPool>))]` matching the element type — relic →
  `[Pool(typeof(SharedRelicPool))]`, potion → `[Pool(typeof(SharedPotionPool))]`, card
  → `[Pool(typeof(ColorlessCardPool))]` (or a character card pool). `using BaseLib.Utils;`
  for the attribute; import the pool type from its namespace (e.g.
  `using MegaCrit.Sts2.Core.Models.RelicPools;`).

### Exception at registration: model assigned to incorrect / invalid pool type
- **Signature:** startup exception `Model <FullName> is assigned to incorrect type of
  pool <PoolFullName>.` **or** `... is assigned to <PoolFullName> which is not a valid
  pool type.` (both from `CustomContentDictionary.AddModel` / its `IsValidPool` check).
- **Cause:** the `[Pool]` attribute is present but wrong. "Incorrect type" = the pool
  belongs to a real family but the wrong one for this element (e.g. a card given a relic
  pool). "Not a valid pool type" = the `[Pool]` points at a type that isn't a pool at
  all (its base chain never reaches `CardPoolModel` / `RelicPoolModel` / `PotionPoolModel`).
- **Fix:** point `[Pool]` at a pool class that (a) actually derives from a `*PoolModel`
  base and (b) matches the element: cards → a `CardPoolModel` subclass, potions → a
  `PotionPoolModel` subclass, relics → a `RelicPoolModel` subclass. Don't pass an
  arbitrary type. See `reference/build-constraints.md` §3.

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

### Nonnegative Counter appears at a negative amount after "consume up to N"
- **Signature:** after the consumer runs at zero stacks, `godot.log` shows a first
  application such as `[T2MOD-SELFTEST] Edge applied: -4 stacks`, followed by the
  Power's effect using that value (live example: repeated `Edge fired: added -4 attack
  damage`). Builds, Tier 1, and a happy-path Tier 2 with enough starting stacks can all
  pass before this appears.
- **Cause:** the consumer called `PowerCmd.Apply<Edge>(..., -4, ...)`. `Apply<T>` stacks
  an existing instance, but when none exists it creates a mutable Power and applies the
  negative amount directly. `PowerVar<T>` has no min/max API, and
  `AllowNegative => false` controls removal after modifying an existing Power; neither
  validates the first negative `Apply`.
- **Fix:** declare every custom Counter's amount domain in SPEC (default
  `[0, unbounded]`; signed only with explicit negative semantics). For nonnegative
  consumption, call `target.GetPower<T>()`; if absent, spend zero. Otherwise clamp the
  spend to `0..power.Amount` and pass the negative **clamped offset** to
  `PowerCmd.ModifyAmount(choiceContext, power, -spent, applier, cardSource)`. Never use
  a negative `PowerCmd.Apply<T>` to consume it. Tier 2 must cover zero, fewer than N,
  and at least N, asserting after each case that no `Amount < 0` instance exists.

### "Every N" relic loses progress after combat or save/resume
- **Signature:** the counter advances and may trigger inside one combat, but the next
  combat starts from zero; or an in-process `SavedProperties.From`/`Fill` round trip
  restores the default instead of the observed progress.
- **Cause:** run-lifetime state was stored in an ordinary field, was cleared from
  `AfterCombatEnd`/`AfterRoomEntered`, or used an unsupported `[SavedProperty]` value/
  holder. A plain field can look correct until the first save/resume.
- **Fix:** for a supported custom relic counter, expose an `int`/`bool` property marked
  `[SavedProperty]`, mutate it through an `AssertMutable()` setter, and never clear it at
  combat boundaries. Keep UI `Status` reset separate. Tier 2 must prove `N-1` in combat 1,
  carry-over/threshold in combat 2, and `SavedProperties.From`/`Fill`. See
  `reference/stateful-mechanics.md`.

### "On turn N" effect leaks across combats or fires on the wrong side
- **Signature:** the effect fires early/late in a new fight, counts enemy turns, or a
  second combat begins with a custom counter value from combat 1.
- **Cause:** code duplicated combat turn state in a field or omitted the owner-side guard.
- **Fix:** read `Owner.PlayerCombatState.TurnNumber` and compare `== N` (or `% N == 0`
  for periodic combat timing), with `participants.Contains(Owner.Creature)`. Do not add
  `[SavedProperty]`; the combat state owns the reset.

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
- **Signature:** `grep_log.py` reports `RUNNING MODDED flag : YES` and no
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
- **Signature:** `grep_log.py` says the `[T2MOD-SELFTEST] ... loaded ok` marker is
  missing, yet reading the raw `godot.log` shows the marker near the top and the mod
  works in-game. A non-programmer would wrongly conclude their mod is broken.
- **Cause:** slicing the log by a pre-launch **byte offset**. STS2 archives the
  previous log to `godot<timestamp>.log` and starts a **fresh** `godot.log` on every
  launch. An offset captured from the old file lands in the middle of the new file
  (past the startup lines where the marker is), so the grep reads only the tail.
  This bit us in two flavors: new file shorter than the offset (caught by a rotation
  guard) AND new file longer (the guard missed it → false FAIL).
- **Fix:** do NOT offset-slice. STS2's rotation guarantees the current `godot.log`
  holds exactly one run, so read the **whole current file**. `grep_log.py` now takes
  only `--mod-name` (no offset); `launch.py` no longer emits an offset.

### Self-test template fails to build: `TaskHelper` is unresolved
- **Signature:** `CS0103: The name 'TaskHelper' does not exist in the current context`
  on `TaskHelper.RunSafely(RunAsync())` in generated `SelfTest.cs`.
- **Cause:** stable v0.107.1 **does** expose the public
  `MegaCrit.Sts2.Core.Helpers.TaskHelper`; `CS0103` means its namespace/import was absent
  from that generated file, not that the game lacks the API. The harness's `RunAsync()`
  already catches and logs its own exceptions, so the helper is unnecessary here.
- **Fix:** start the task with the standard C# discard form: `_ = RunAsync();`. This
  remains fire-and-forget and does not block `Initialize()`. For other code that genuinely
  needs `TaskHelper`, import `MegaCrit.Sts2.Core.Helpers` rather than inventing a replacement.

### Tier verify reports only the known abandon-backup or Sentry shutdown cleanup block
- **Signature:** the only post-load error is either (a) deletion of
  `modded/profileN\\saves\\current_run.save.backup: Failed` with the full
  `RunSaveManager.DeleteCurrentRun → NMainMenu.AbandonRun → UiHelper.Click` stack, or
  (b) `Sentry: Failed to close native SDK cleanly. Error code: 1` with native close +
  `SentryService.Shutdown` stack.
- **Cause:** headed self-test cleanup, not element behavior. STS2 asks Godot to remove a
  backup that may not exist; the verification launcher also terminates the headed process
  after the terminal marker.
- **Fix:** none in generated mod code. Current `grep_log.py` reports and ignores only
  those exact stack-qualified blocks. A lookalike, a different file/error, or any other
  global/multiline error still fails and must be diagnosed normally.

### Self-test logs `InitProfileId must be called on SaveManager`
- **Signature:** `[ERROR] Failed to save progress: System.InvalidOperationException:
  InitProfileId must be called on SaveManager!`, with
  `ProgressSaveManager.SetFtuesEnabled → SaveManager.SetFtuesEnabled` and the mod's
  `SelfTest.RunAsync` in the stack. The harness may continue because the call was wrapped
  in `try/catch`, but strict verification still fails the fresh error block.
- **Cause:** `SelfTest.Arm()` runs during mod initialization, before profile state is ready.
  Calling `SaveManager.SetFtuesEnabled(false)` attempts to persist a user setting and logs
  the global save error before throwing to the caller.
- **Fix:** remove the call. Tutorial state is not required by the menu navigation, and a
  verification harness must not mutate a persistent user preference. Keep the run-UI
  timing gates from `reference/selftest-harness.md` instead.

### Placeholder custom monster logs a missing `creature_visuals/<mod>-<class>.tscn`
- **Signature:** Godot reports `Cannot open file` / `Failed loading resource` for
  `res://scenes/creature_visuals/<mod>-<class>.tscn`, followed by
  `Encountered exception loading the creature visuals ... Falling back to error scene`.
  The monster may still fight on the error visual, but strict verification fails.
- **Cause:** a `CustomMonsterModel` left `CustomVisualPath` null while no convention-named
  custom scene exists. BaseLib lets the vanilla path convention run; the game logs
  the failed load before recovering.
- **Fix:** keep `CustomVisualPath => SceneHelper.GetScenePath("creature_visuals/fallback")`.
  For supported static art, existence-check `images/monsters/<slug>.png` in
  `CreateCustomVisuals()` and return
  `NodeFactory<NCreatureVisuals>.CreateFromResource(ModVisualPath)` only when present;
  otherwise return `null` so the explicit scene fallback loads. Do not point
  `CustomVisualPath` at the PNG. See `recipes/monster.md`.

### Custom orb channels but logs missing `debug_audio/<custom-id>_channel.mp3`
- **Signature:** channeling succeeds, but strict verification finds `No loader found for
  resource: res://debug_audio/<custom-id>_channel.mp3` from
  `OrbModel.PlayChannelSfx -> OrbCmd.Channel`.
- **Cause:** a `CustomOrbModel` left `CustomChannelSfx` null/empty. Channeling always plays
  SFX; the base class then probes a convention-named debug file that a packaged mod does
  not ship.
- **Fix:** set `CustomChannelSfx` to a verified vanilla fallback event alongside the
  explicit vanilla `CustomSpritePath`. The supported Frost fallback is
  `event:/sfx/characters/defect/defect_frost_channel`. Also existence-check the custom
  100x100 `CustomIconPath` and return the Frost icon when absent. See `recipes/orb.md`.

### A resumed Event starts a second special combat and `RecordInitialState` fails
- **Signature:** `InvalidOperationException: RecordInitialState must be called first`
  from `CombatReplayWriter`, after a special combat has already returned to the same
  mutable Event instance.
- **Cause:** the Event calls `EnterCombatWithoutExitingEvent` a second time from the same
  instance. The grounded Event replay/lifecycle supports one special combat per mutable
  Event; the first resumable or terminal transition works, while the second leaves replay
  setup inconsistent.
- **Fix:** generate at most one special-combat transition per Event instance. After a
  resumable fight, continue with Cmd/page/selection/reward outcomes and finish the Event.
  If verification must exercise an independent terminal-combat branch, click Proceed/open
  the map and `EnterRoomDebug` a **fresh** canonical Event instance. See
  `reference/event-outcomes.md` and the extended `MapNode` section of
  `reference/selftest-harness.md`.

### Static Character merchant logs `Expected BoundObject to be a SpineSprite`
- **Signature:** the custom 512x512 merchant `Sprite2D` appears, but strict verification
  finds `InvalidOperationException: Expected BoundObject to be a SpineSprite` from
  `NMerchantCharacter._Ready()`.
- **Cause:** BaseLib 3.3.5 converts the static raw scene to `NMerchantCharacter`, but the
  game's `_Ready()` unconditionally constructs `MegaSprite(GetChild(0))` before BaseLib's
  guarded `PlayAnimation` patch can help.
- **Fix:** select the version/MVID-gated `NMerchantCharacter._Ready()` B-prefix from
  `reference/capability-kernel.md`. Skip the original only when child 0 is `Sprite2D`, and
  gate `CustomMerchantAnimPath` on successful patch status plus resource existence. On any
  mismatch, keep the inherited Spine scene.

### Custom Character cannot enter Shop: `Can't generate valid rarity for merchant card type`
- **Signature:** `EnterRoomDebug(RoomType.Shop)` throws before the Shop UI, naming
  `Attack`, `Skill`, or `Power` and an undersized custom card list.
- **Cause:** the native colored merchant always fills `Attack, Attack, Skill, Skill,
  Power`; it excludes Basic cards and excludes the first result before filling the second
  same-type slot.
- **Fix:** ensure the unlocked Character pool has at least two eligible non-Basic Attacks,
  two eligible non-Basic Skills, and one eligible non-Basic Power. These should be real
  authored cards, not no-op fillers. Then rerun the real Shop proof.
