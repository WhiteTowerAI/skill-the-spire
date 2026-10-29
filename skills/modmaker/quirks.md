# Known Quirks — STS2 / RitsuLib gotchas

Non-obvious behaviors that silently break STS2 mods. Read before writing any C#.

This file and `errors.md` split by *when you need them*, and the split is load-bearing: this
one holds rules you follow **before** anything breaks, stated as constraints. `errors.md` holds
signatures you match **after** something breaks, stated as cause and fix. A rule here needs no
error code; a rule that only makes sense once you have a failing signature belongs there. Do
not restate the other file's half — a diagnostic in two homes drifts.

## Registration

- **Content registration is explicit and exactly once.** Add the matching `.Card`,
  `.Relic`, `.Potion`, `.Power`, `.Enchantment`, or `.Orb` step to the scaffold's partial
  content hook; keywords use `.CardKeywordOwnedByLocNamespace(...)`. Call `.Apply()` once
  for the pack.
- **Do not add `[Pool(...)]`.** The content-pack pool generic is the only availability
  declaration; a second path risks duplicate ownership and ids. Build rejects the attribute,
  along with raw Harmony, member reflection, Publicizer, and unreviewed patch targets.
- `Apply()` queues registration for RitsuLib's discovery window. It is normal for the
  actual `ModelDb` registration log to appear after the Mod initializer returns.

## Localization key derivation (the #1 silent failure)

- Model `Id.Entry` is `MOD_CATEGORY_TYPENAME`, with each segment normalized to
  uppercase snake case. `ExampleMod` + `Jolt` becomes
  `EXAMPLE_MOD_CARD_JOLT`.
- Surface localization keys are flat strings using that exact public entry. Power and Orb
  CLR suffixes remain part of the type name; keyword entries use `MOD_KEYWORD_STEM`.
- Get this wrong → the relic shows the raw key or blank text, with no error.
- Preserve an already-published id with `ModelPublicEntryOptions.FromStem(...)`; do not
  create another naming system.
- Custom art uses the matching explicit per-surface `*AssetProfile` resource paths.
  Empty fields retain the checked template/base-game fallback.

## Orb fallback

- A custom Orb icon is not its combat body. `ContentAssetProfiles.Orb("frost_orb")`
  preserves the Frost icon/Spine fallback, and the protected `ChannelSfx` must name the
  verified Frost event or a registered virtual event for the user's own sound
  (`../sts2api/reference/audio.md`).

## Combat hooks

- **Combat-start energy MUST use `AfterSideTurnStart` + `TurnNumber <= 1`**, never
  `BeforeCombatStart()`. The turn-1 energy reset wipes anything granted earlier.
  Vanilla `Lantern` does it this way.
- `AfterSideTurnStart` fires **for every side and every turn**. Always guard with
  `participants.Contains(Owner.Creature)` (right owner, matters in multiplayer) and,
  for "start of combat", `Owner.PlayerCombatState!.TurnNumber <= 1` (else it re-fires each turn).
- `AfterSideTurnStart` has **no `PlayerChoiceContext`**. A turn-start or combat-start effect
  that draws, selects, discards, or otherwise needs one overrides
  `AfterPlayerTurnStart(PlayerChoiceContext, Player)` with `player == Owner` (a Power:
  `Owner.Player`) plus the same `TurnNumber` guard. A combat-start Power goes on in
  `AfterRoomEntered(room)` with `room is CombatRoom`. See `recipes/relic.md` § Trigger hooks.
- Relics receive combat hooks automatically (`RelicModel.ShouldReceiveCombatHooks => true`).
  There is **no `ICombatHook` interface to implement** — just override the method.

## Nullable

- `Owner.PlayerCombatState` is `PlayerCombatState?` — null outside combat, non-null inside a
  combat hook. Capture once: `var combat = Owner.PlayerCombatState!;` then use
  `combat.Energy`, `combat.TurnNumber`. Outside that boundary, guard null explicitly.

## Multiplayer-safe by default

Every Mod is written for multiplayer; singleplayer is the one-player case of the same code. Each
peer runs the same queued actions and must reach the same state, and the host checksums combat
state after every action. Build rejects the checkable breakers (process-local randomness or
time, `LocalContext` player lookups and mutable statics in gameplay models); follow the rest:

- **Owner, not "me".** Gameplay reads the model's `Owner` (a Power: `Owner.Player`). `LocalContext`
  names this machine's player; use `LocalContext.IsMe(Owner)` only to gate local presentation.
- **Filter shared hooks.** Combat and run hooks fire for every player's models: guard with
  `player == Owner` or `participants.Contains(Owner.Creature)` (§ Combat hooks).
- **"All players" is explicit.** A run-level eligibility or effect that concerns the party
  iterates `runState.Players` as vanilla does (`Players.All(...)`); text says "you" for the owner
  and "all players"/"another player" only when the code targets them.
- **State lives in synchronized places.** Model fields, `SavedProperties`, and run/player
  saved-data slots travel with the run; a static, a process cache, or a UI node does not.
- **Input that changes gameplay is an action.** A button, hotkey, or Runtime UI control that
  changes run or combat state goes through a queued route (`reference/model-right-click.md`),
  never a direct command from the UI callback. Purely local display needs no action.

## RNG

- **Never `System.Random`** — it breaks determinism and seed sharing, and Build rejects it. Use
  `MegaCrit.Sts2.Core.Random.Rng`: `new Rng(Owner, base.Id)`; `.NextBool()` (50/50),
  `.NextInt(maxExcl)`. Add a mixin (`new Rng(Owner, base.Id, (uint)turn)`) if it may
  roll repeatedly and you want distinct results.

## Build / toolchain

- `build.py` packs the `<ModName>/` resource tree without a framework-specific pack target.
  Keep every authored resource inside that tree.
- Pass MSBuild properties as `--property:Name=Value`, never `/p:Name=Value`. The normal
  `dotnet build -c Release` path needs no properties at all.

## Dev console (verification)

- Open with **`` ` `` (backtick)** — also `'`, `*`, `^`, `Shift+8`; close with `Esc`.
- Debug commands (`relic add <id>`, `energy`, ...) are enabled only when the game is
  **running modded** (`ModManager.IsRunningModded()`), true whenever ≥1 gameplay mod
  loaded. If commands are missing, confirm the mod actually loaded (grep log for
  `RUNNING MODDED`).
- `relic add` matching is `Contains`, uppercased — a unique substring works.

## Feedback loop

New quirks discovered during a real build go into the project's `MEMORY.md` first.
Recurring ones get promoted here and into `errors.md` (append-only) by the skill maintainer.
