# Reference: the tier-2 self-test harness (`SelfTest.cs`)

> A copy-adaptable, **known-good** in-process harness that makes tier-2 ("the effect
> actually fires") automatic — no human at the keyboard, no dev-console typing. Every
> API here was confirmed against decompiled `sts2.dll` (M5 grounding) — not guessed.
>
> **What it is:** one `SelfTest.cs` file compiled into the generated mod, **dormant
> unless launched with `--t2selftest`**. When that arg is present, it drives the game
> from the main menu into the hosted scenario required by the SPEC with zero interaction,
> fires the element's effect, independently asserts a concrete post-effect state invariant,
> then logs `[T2MOD-SELFTEST] <ModName> state proof: ...` with the observed before/after
> values. `verify.md` accepts only that structured proof, never a hook/preview log.
>
> **Ship-safety:** the arg gate (`CommandLineHelper.HasArg("t2selftest")`) means a normal
> user launch never arms it — no menu or room driving and no scenario side effects. It is
> inert.

## Why in-process, and why it drives its own navigation

- **In-process (not keystroke injection / external MCP):** the harness *is* mod code, so
  it calls the game's own public Cmds directly. No OS automation, no second process.
- **It drives navigation itself** (main menu → run → hosted room), so it knows exactly
  when the scenario is reachable. Combat drivers use the game's own **poll pattern** — the
  same code `CombatRoomHandler` (MegaCrit's AutoSlay) uses — then wait for the **Play** phase
  before acting. The `MapNode` event driver instead waits for the real `EventRoom` and
  option UI. Both paths poll observable game state rather than guessing timing.

## The one correction that matters (do NOT regress)

`NDevConsole.Instance` exists, but its inner `DevConsole` is a **private field** — so the
string-in `ProcessCommand("fight …")` / `"card …"` path is **NOT reachable** from a mod
assembly. Do not try to reflect into it. Instead the harness calls the **public Cmds**
that each console command wraps (all confirmed `public static`, shipped in `sts2.dll`):

| Console command | Public API the harness calls instead |
|---|---|
| `fight <id>` | `RunManager.Instance.EnterRoomDebug(RoomType.Monster, MapPointType.Unassigned, encounter.ToMutable())` |
| `event <id>` | `RunManager.Instance.EnterRoomDebug(RoomType.Event, MapPointType.Unknown, ModelDb.Event<T>())` |
| `relic add <id>` | `RelicCmd.Obtain(relic.ToMutable(), player)` |
| `card <ID>` | `CombatManager.Instance.DebugOnlyGetState().CreateCard(card, player)` + `CardPileCmd.Add(c, PileType.Hand)` |
| `energy N` | `PlayerCmd.GainEnergy(3m, player)` |
| `potion <ID>` | `PotionCmd.TryToProcure(potion.ToMutable(), player)` |
| (play the card) | `CardCmd.AutoPlay(new BlockingPlayerChoiceContext(), card, target)` |
| (use the potion) | `potion.EnqueueManualUse(target)` *(not a Cmd — a method on the model)* |

## The load-bearing timing gate (proven on the dev box, do NOT regress)

The first live end-to-end run (CanaryCard, tier-2 PASS) exposed this race before combat;
keep the gate below. Do **not** call `SaveManager.SetFtuesEnabled(false)`: tutorial state is
not required for navigation, the call persists a user setting, and before profile setup its
internal save reports a global error even if the caller catches an exception.

**`IsInProgress` is NOT enough to call `EnterRoomDebug`.** `RunManager.Instance.
   IsInProgress` flips at the **run-state** level, but `EnterRoomDebug` reaches into the run
   **UI node** (`NRun.Instance.GlobalUi.TopBar.RoomIcon…`, and its `?.` only guards
   `NRun.Instance`, not `GlobalUi`). `GlobalUi` is wired in `NRun._Ready`, which runs
   **after** `IsInProgress` is already true. Entering a room in that window NREs *inside*
   `EnterRoomDebug`. Gate on the UI node before entering:
   `await WaitHelper.Until(() => NRun.Instance?.GlobalUi != null, …, "run UI not ready");`.
   (The `fight` console command never hits this because a human types it only once the map
   is visible — i.e. long after `_Ready`.)

> Debugging tip proven useful: async PDB line numbers are unreliable across state-machine
> resumes (the stack top can point at a `try/catch` line that cannot throw). If a harness
> fails mid-flight, add a `Stage(string)` breadcrumb (`MainFile.Logger.Info` per step) and
> read the trail — it tells you the exact step, which the stack trace won't.

For a Character Foundation `RunStart` driver, keep one further ordering constraint:
after character-select Confirm and `RunManager.Instance.IsInProgress`, wait for
`NRun.Instance?.GlobalUi != null`, then continue polling until
`LocalContext.GetMe(RunManager.Instance.DebugOnlyGetState())` is non-null. A single read
after the UI gate is still racy: the R6 Scry proof's first setup attempt reached a ready
`GlobalUi` before the local Player was injected. The earlier Character canary likewise
proved that the run-state flag can become true while the local player is unavailable. Also
normalize `\\` to `/` on both the template's character-select
icon path and Godot's texture `ResourcePath`; Windows template helpers may return a mixed
separator `res://` path even though the correct button is present.

## Proof and control signals for verify/repair

The harness and element expose three signals so `verify.md`/`repair.md` can tell setup
failure from a real effect bug:

- `[T2MOD-SELFTEST] <ModName> state proof: <invariant>; observed <before> -> <after>` —
  the harness independently compared real post-effect state with the SPEC and the assertion
  passed. This is the **only** Tier-2 behavior proof accepted by `grep_log.py`.
- `[T2MOD-SELFTEST] <ModName> selftest done` — the scenario driver completed after its
  assertions. This terminal marker is necessary control flow, but is never behavior proof.
- `[T2MOD-SELFTEST] <ModName> selftest FAILED: <stage>: <reason>` — harness couldn't reach
  or drive the scenario (navigation/timeout). **This is a harness/setup problem, NOT an
  effect bug** —
  `verify.md` falls back to the manual guide and reports tier-1 only.
- the element's own type-specific `[T2MOD-SELFTEST]` diagnostic marker (for example
  `played:`, `attacked:`, or `option chosen:` from author.md step 2) — useful for locating
  the trigger, but **not proof**: calculation/preview hooks can emit it without a committed
  state change.

## Gameplay-readability proof additions

For a Card with hand emphasis, also read `reference/card-hand-emphasis.md`. A focused
`CombatPlayer` driver must place the real Card in hand, mutate the actual condition state,
and independently assert no-active, single-active, conflict winner, playability, and hand
entry/exit states. Do not claim the outline color from predicate or model state alone; the
real hand consumer remains a headed or exact live-node observation.

For Relic/Power supplemental labels, also read `reference/extra-corner-labels.md`. The
driver must assert the exact zero/one Power sequence and zero/one/bounded-multiple Relic
sequence, visible text, selected safe corners, refresh source, removal condition, and
unchanged native main amount. Provider data alone is not a presentation proof; exact
live-node observation or headed review owns readability, overlap, and cleanup.

When the human lead reserves headed review, build and deploy the focused proof but do not
launch the game. Give the lead the exact console setup and observation matrix. Record the
reported visible result separately, and keep unrun structured checks as exceptions rather
than converting manual observation into strict Tier 2.

## Shared scaffold and scenario-specific room driver

Emit this as `<ModName>Code/SelfTest.cs`. The arg gate, menu→run navigation, timeout, and
terminal markers are shared. The scaffold below is the `CombatPlayer` baseline: its
**`BeforeCombat` / `InCombat`** DRIVER bodies change per combat element. `CombatEnemy`
replaces the encounter entry and combat driver; `MapNode` replaces combat entry entirely
with the event room/UI driver documented below. `<ModName>` / `<PREFIX>-<SLUG>` are
substituted exactly as elsewhere.

```csharp
using System;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using Godot;
using MegaCrit.Sts2.Core.AutoSlay.Helpers;   // UiHelper, WaitHelper (public, shipped)
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Context;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Encounters;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.Nodes;
using MegaCrit.Sts2.Core.Nodes.CommonUi;
using MegaCrit.Sts2.Core.Nodes.GodotExtensions;
using MegaCrit.Sts2.Core.Nodes.Screens.CharacterSelect;
using MegaCrit.Sts2.Core.Rooms;
using MegaCrit.Sts2.Core.Runs;

namespace <ModName>.<ModName>Code;   // SAME namespace as MainFile.cs (scaffold nests <ModName>Code)

// Verification-only. Dormant unless the game is launched with --t2selftest.
// Gated in MainFile.Initialize(): if (CommandLineHelper.HasArg("t2selftest")) SelfTest.Arm();
internal static class SelfTest
{
    private static bool _armed;

    private static void StateProof(bool condition, string observation)
    {
        if (!condition)
            throw new InvalidOperationException($"state proof failed: {observation}");
        MainFile.Logger.Info($"[T2MOD-SELFTEST] <ModName> state proof: {observation}");
    }

    public static void Arm()
    {
        if (_armed) return;
        _armed = true;
        _ = RunAsync();   // fire-and-forget; never blocks Initialize
    }

    private static async Task RunAsync()
    {
        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(180));
        var ct = cts.Token;
        try
        {
            await WaitHelper.Until(() => NGame.Instance != null, ct, TimeSpan.FromSeconds(30), "no NGame");
            await NavigateToRunAsync(ct);
            await WaitHelper.Until(() => RunManager.Instance.IsInProgress, ct, TimeSpan.FromSeconds(30), "run not in progress");

            // IsInProgress flips at the RUN-STATE level, but EnterRoomDebug (below) touches
            // the run UI node (NRun.Instance.GlobalUi.TopBar…), which is only wired in
            // NRun._Ready — AFTER IsInProgress. Racing in here NREs inside EnterRoomDebug.
            // Gate on the run UI node being ready before entering a room.
            await WaitHelper.Until(() => NRun.Instance?.GlobalUi != null, ct, TimeSpan.FromSeconds(30), "run UI not ready");

            // RELIC ONLY: grant before combat so AfterSideTurnStart fires at TurnNumber 1.
            await BeforeCombat(ct);

            var encounter = ModelDb.Encounter<CorpseSlugsWeak>().ToMutable();   // minimal 2-slug fight
            await RunManager.Instance.EnterRoomDebug(RoomType.Monster, MegaCrit.Sts2.Core.Map.MapPointType.Unassigned, encounter);
            await WaitHelper.Until(() => CombatManager.Instance.IsInProgress, ct, TimeSpan.FromSeconds(30), "combat not started");

            var player = LocalContext.GetMe(RunManager.Instance.DebugOnlyGetState()!);
            var me = player!.Creature;
            // Survivability so a slug can't kill us mid-test (AutoSlay does the same).
            await PowerCmd.Apply<PlatingPower>(new ThrowingPlayerChoiceContext(), me, 999m, me, null);

            // Wait until we're actually allowed to act.
            await WaitHelper.Until(
                () => player!.PlayerCombatState?.Phase == PlayerTurnPhase.Play || !CombatManager.Instance.IsInProgress,
                ct, TimeSpan.FromSeconds(30), "play phase not reached");

            await InCombat(player!, ct);

            MainFile.Logger.Info("[T2MOD-SELFTEST] <ModName> selftest done");
        }
        catch (Exception e)
        {
            MainFile.Logger.Info($"[T2MOD-SELFTEST] <ModName> selftest FAILED: {e.GetType().Name}: {e.Message}");
        }
    }

    // Ported verbatim from AutoSlayer.PlayMainMenuAsync (node paths are version-sensitive;
    // re-mine on a game version bump — same habit as build-constraints).
    private static async Task NavigateToRunAsync(CancellationToken ct)
    {
        var root = ((SceneTree)Engine.GetMainLoop()).Root;
        var mainMenu = await WaitHelper.ForNode<Control>(root, "/root/Game/RootSceneContainer/MainMenu", ct, TimeSpan.FromSeconds(30));

        var abandon = mainMenu.GetNode<NButton>("MainMenuTextButtons/AbandonRunButton");
        if (abandon.Visible)   // an old run is open — abandon it first
        {
            await UiHelper.Click(abandon);
            await WaitHelper.Until(() => NModalContainer.Instance?.OpenModal != null, ct, TimeSpan.FromSeconds(10), "no abandon modal");
            var modal = (Node)NModalContainer.Instance!.OpenModal!;
            await UiHelper.Click(modal.GetNode<NButton>("VerticalPopup/YesButton"));
            await WaitHelper.Until(() => NModalContainer.Instance.OpenModal == null, ct, TimeSpan.FromSeconds(10), "abandon modal stuck");
        }

        await UiHelper.Click(mainMenu.GetNode<NButton>("MainMenuTextButtons/SingleplayerButton"));

        // Either the submenu ("Standard") or the character screen shows next.
        Control? charSelect = null;
        NButton? standard = null;
        await WaitHelper.Until(() =>
        {
            charSelect = mainMenu.GetNodeOrNull<Control>("Submenus/CharacterSelectScreen");
            standard = mainMenu.GetNodeOrNull<NButton>("Submenus/SingleplayerSubmenu/StandardButton");
            return (charSelect?.Visible ?? false) || (standard?.Visible ?? false);
        }, ct, TimeSpan.FromSeconds(10), "neither submenu nor char select");

        if ((standard?.Visible ?? false) && !(charSelect?.Visible ?? false))
        {
            await UiHelper.Click(standard);
            await WaitHelper.Until(() => mainMenu.GetNodeOrNull<Control>("Submenus/CharacterSelectScreen")?.Visible ?? false,
                ct, TimeSpan.FromSeconds(10), "char select never showed");
            charSelect = mainMenu.GetNode<Control>("Submenus/CharacterSelectScreen");
        }

        var buttonContainer = charSelect!.GetNode("CharSelectButtons/ButtonContainer");
        var chars = UiHelper.FindAll<NCharacterSelectButton>(buttonContainer);
        foreach (var b in chars) b.UnlockIfPossible();
        var pick = chars.First(b => !b.IsLocked);   // deterministic: first unlocked
        pick.Select();
        await Task.Delay(100);

        var confirm = await WaitHelper.ForNode<NButton>(mainMenu, "Submenus/CharacterSelectScreen/ConfirmButton", ct, TimeSpan.FromSeconds(10));
        await UiHelper.Click(confirm);
    }

    // ===== DRIVER (per element type — fill exactly one of these two) =====
    private static Task BeforeCombat(CancellationToken ct) => Task.CompletedTask;   // <see element table>
    private static Task InCombat(Player player, CancellationToken ct) => Task.CompletedTask;   // <see element table>
}
```

## The DRIVER bodies (fill per SPEC element type)

Every driver must snapshot the SPEC's observable state, drive the real source element,
assert the exact expected post-state, and call `StateProof` with concrete observed values.
The element's own marker is diagnostic only: passive hooks such as damage modifiers can run
during previews. Branch on SPEC's `element` and adapt the shown invariant to the effect:

### relic — grant before combat, then just wait

A relic's `AfterSideTurnStart` fires on its own at combat start (`TurnNumber <= 1`), so
there's nothing to drive in-combat — grant it *before* `EnterRoomDebug` and let the
existing wait-for-Play-phase give it time to fire.

```csharp
private static async Task BeforeCombat(CancellationToken ct)
{
    var player = LocalContext.GetMe(RunManager.Instance.DebugOnlyGetState());
    var relic = ModelDb.AllRelics.First(r => r.Id.Entry == "<PREFIX>-<SLUG>");
    await RelicCmd.Obtain(relic.ToMutable(), player);
}
private static Task InCombat(Player player, CancellationToken ct)
{
    // Energy-relic example. For another effect, assert its SPEC state instead.
    int observed = player.PlayerCombatState!.Energy;
    StateProof(observed == <EXPECTED_ENERGY>,
        $"relic energy expected=<EXPECTED_ENERGY> observed={observed}");
    return Task.CompletedTask;
}
```

### stateful relic cadence — prove the lifetime, not only one trigger

The normal relic DRIVER proves one combat-start effect. A stateful relic needs a
multi-combat variant. Replace the scaffold's one `EnterRoomDebug` + `InCombat` block
with a scenario that owns the live mutable relic, advances real player turns, finishes
the first combat through the public combat flow, and enters a second combat. Add
`using MegaCrit.Sts2.Core.Saves.Runs;` for the save round trip.

Shared helpers (live-proven by `CadenceCanary` on 2026-07-15):

```csharp
private static async Task EnterMinimalCombat(CancellationToken ct)
{
    var encounter = ModelDb.Encounter<CorpseSlugsWeak>().ToMutable();
    await RunManager.Instance.EnterRoomDebug(RoomType.Monster,
        MegaCrit.Sts2.Core.Map.MapPointType.Unassigned, encounter);
    await WaitHelper.Until(() => CombatManager.Instance.IsInProgress, ct,
        TimeSpan.FromSeconds(30), "combat not started");
}

private static async Task WaitForPlayTurn(Player player, int turn, CancellationToken ct)
{
    await WaitHelper.Until(
        () => player.PlayerCombatState?.Phase == PlayerTurnPhase.Play &&
              player.PlayerCombatState.TurnNumber == turn,
        ct, TimeSpan.FromSeconds(45), $"player turn {turn} not reached");
}

private static async Task FinishCombat(CancellationToken ct)
{
    var enemies = CombatManager.Instance.DebugOnlyGetState()!.Enemies
        .Where(enemy => enemy.IsAlive).ToList();
    await CreatureCmd.Kill(enemies, force: true);
    await CombatManager.Instance.CheckWinCondition();
    await WaitHelper.Until(() => !CombatManager.Instance.IsInProgress, ct,
        TimeSpan.FromSeconds(30), "first combat did not finish");
}
```

**Run-persistent periodic counter (Happy Flower shape):** let the first combat
advance the real `SavedAttachedState` progress to `N - 1`, verify no effect, serialize and
fill a fresh mutable instance, then let turn 1 of the second combat cross the threshold.
For `N=3` and an energy effect:

```csharp
var player = LocalContext.GetMe(RunManager.Instance.DebugOnlyGetState()!)
    ?? throw new InvalidOperationException("local player missing");
var live = await RelicCmd.Obtain<<RelicName>>(player);

await EnterMinimalCombat(ct);             // turn 1: Progress 0 -> 1
await WaitForPlayTurn(player, 1, ct);
StateProof(live.Progress == 1,
    $"cadence first event expected=1 observed={live.Progress}");

PlayerCmd.EndTurn(player, canBackOut: false);
await WaitForPlayTurn(player, 2, ct);      // turn 2: Progress 1 -> 2, no fire
StateProof(live.Progress == 2 && player.PlayerCombatState!.Energy ==
        player.PlayerCombatState.MaxEnergy,
    $"cadence below threshold expected progress=2/no effect " +
    $"observed={live.Progress}/{player.PlayerCombatState.Energy}");

var saved = SavedProperties.From(live)
    ?? throw new InvalidOperationException("saved counter missing");
var restored = (<RelicName>)ModelDb.Relic<<RelicName>>().ToMutable();
saved.Fill(restored);
StateProof(restored.Progress == 2,
    $"cadence save round trip expected=2 observed={restored.Progress}");

await FinishCombat(ct);
await EnterMinimalCombat(ct);             // new combat turn 1: Progress 2 -> 0, fire
await WaitForPlayTurn(player, 1, ct);
int expectedEnergy = player.PlayerCombatState!.MaxEnergy + <ENERGY_GAIN>;
StateProof(live.Progress == 0 && player.PlayerCombatState.Energy == expectedEnergy,
    $"cadence cross-combat threshold expected progress=0 energy={expectedEnergy} " +
    $"observed={live.Progress}/{player.PlayerCombatState.Energy}");
```

For another threshold, advance real turns until `N - 1`; do not set `Progress` from the
harness. Replace the energy observations with the SPEC's real HP/block/stack state.
The save round trip and second combat are separate proofs and both are required.

**Combat-local fixed/periodic turn (Stone Calendar shape):** in combat 1, assert no
effect at turn 1, advance to the specified turn using `PlayerCmd.EndTurn`, and assert the
exact effect delta. Finish combat, enter combat 2, wait for turn 1, then assert
`TurnNumber == 1` and that the effect has not fired again. Read the game's turn number;
do not mutate a custom counter to simulate reset. A diagnostic activation count may help
localize the test, but Tier-2 still needs the actual gameplay delta.

The live canary combined both relics and proved: run progress `1 -> 2 -> 0` across two
combats, energy `3 -> 4` at the threshold, save restoration `2 -> 2`, combat-local turn-2
Block, and a new-combat `TurnNumber=1` with no second activation. One structured proof per
invariant makes a wrong lifetime distinguishable from a wrong effect.

### card — spawn into hand, add energy, AutoPlay

```csharp
private static Task BeforeCombat(CancellationToken ct) => Task.CompletedTask;
private static async Task InCombat(Player player, CancellationToken ct)
{
    await PlayerCmd.GainEnergy(3m, player);                       // headroom for cost
    var model = ModelDb.AllCards.First(c => c.Id.Entry == "<PREFIX>-<SLUG>");
    var card  = CombatManager.Instance.DebugOnlyGetState()!.CreateCard(model, player);
    await CardPileCmd.Add(card, PileType.Hand);
    Creature? target = card.TargetType == TargetType.AnyEnemy
        ? card.CombatState?.HittableEnemies.FirstOrDefault()
        : null;                                                   // Self/AllEnemies → null
    // Attack example. Snapshot Block/Power/orb state instead for other card effects.
    int hpBefore = target?.CurrentHp
        ?? throw new InvalidOperationException("attack target missing");
    await CardCmd.AutoPlay(new BlockingPlayerChoiceContext(), card, target);
    int hpAfter = target.CurrentHp;
    StateProof(hpBefore - hpAfter == <EXPECTED_DAMAGE>,
        $"card damage expected=<EXPECTED_DAMAGE> observed={hpBefore - hpAfter}; " +
        $"target hp {hpBefore} -> {hpAfter}");
}
```
(`TargetType` is `MegaCrit.Sts2.Core.Models` — already imported. For an attack the
`card.CombatState.HittableEnemies` list is the slugs from the minimal encounter.)

### calculated-value Card — preview, raw request, final state, and headed text

Read `card-computed-values.md` and keep all cases in one disposable `CombatPlayer` suite.
For each behavior case, set deterministic combat state, call
`card.UpdateDynamicVarPreview(CardPreviewMode.Normal, target, card.DynamicVars)`, record the
matching `PreviewValue`, then play the real hand Card and assert the exact HP, Block,
Energy, Stars, or Power delta. Also inspect the raw execution request through the matching
`Compute*Value` extension. This distinguishes a wrong formula from a hook applied zero or
two times.

Cover zero/positive/changing inputs and an upgraded mutable Card. Apply
Strength/Vulnerable for Damage and Dexterity/Frail for Block, one modifier family at a
time, and require the final preview to equal the observed result. For Power, obtain
`SneckoSkull`, use raw Poison 2, and separately prove raw `ComputedPower<PoisonPower>` 2,
amount-given preview 3, and final target Poison 3. Neutral Energy/Stars cases assert the
exact requested gain; their normal gain hooks are a separate effect boundary.

The structured state proof does not establish presentation. In the same headed combat,
the reviewer must inspect the real hand Card at zero, positive, changed, and upgraded
states; confirm Energy 0 is `0` plus one Energy icon while Stars 0 is empty; inspect
multiple icons, maximum-count reflow, no clipping/stale glyphs, localized variable tooltip,
and the omitted-icon fallback. A mutable hand Card displaying the tooltip also exercises
DynamicVar clone preservation. End only after all structured cases pass and the harness
emits `selftest done`.

### potion — procure, then EnqueueManualUse (NOT a Cmd)

```csharp
private static Task BeforeCombat(CancellationToken ct) => Task.CompletedTask;
private static async Task InCombat(Player player, CancellationToken ct)
{
    var model  = ModelDb.AllPotions.First(p => p.Id.Entry == "<PREFIX>-<SLUG>");
    var potion = model.ToMutable();
    await PotionCmd.TryToProcure(potion, player);
    var cs = player.Creature!.CombatState;
    Creature? target = potion.TargetType switch
    {
        TargetType.AnyEnemy  => cs?.HittableEnemies.FirstOrDefault(),
        TargetType.AnyAlly   => cs?.PlayerCreatures.FirstOrDefault(c => c.IsAlive),
        TargetType.AnyPlayer => cs?.PlayerCreatures.FirstOrDefault(c => c.IsAlive),
        TargetType.Self      => cs?.PlayerCreatures.FirstOrDefault(c => c.IsAlive),
        _ => null,
    };
    // Damage-potion example. Snapshot the SPEC's concrete state for another effect.
    int hpBefore = target?.CurrentHp
        ?? throw new InvalidOperationException("potion target missing");
    potion.EnqueueManualUse(target);        // drives the potion's OnUse → its used: marker
    await Task.Delay(500, ct);              // let the enqueued use resolve before observing
    int hpAfter = target.CurrentHp;
    StateProof(hpBefore - hpAfter == <EXPECTED_DAMAGE>,
        $"potion damage expected=<EXPECTED_DAMAGE> observed={hpBefore - hpAfter}; " +
        $"target hp {hpBefore} -> {hpAfter}");
}
```

### advanced Card/Potion targeting — prove each lifecycle separately

Read `advanced-targeting.md` and keep its current three-consumer matrix in one disposable
`CombatPlayer` proof: source-aware single Card, single Potion, and player-aware multi Card.
Do not add a multi Potion or infer its lifecycle from another consumer.

Use at least two live enemies and establish deterministic zero/one/multiple candidate
states through public combat Cmds. For each consumer, assert the exact registered target
kind, resolved creature combat IDs, before/after values, and diagnostic target id. Drive a
single Card/Potion with its selected creature; drive the multi Card once with `null` and
assert one effect delta per `GetTargets()` result.

Snapshot Energy, Stars, Potion belt membership, and the source Card pile before boundary
cases. Normal cancel and a queued target becoming invalid must leave payment/Potion state
unchanged; a successful Card must reach its normal result pile. Predicate-only assertions,
model-only `GetTargets()` output, and trigger logs are diagnostics, not the hosted behavior
proof. Keep mouse and controller selection, invalid-target rejection, and multi reticles as
the separate headed checks in `advanced-targeting.md`.

### multi-element interactions — drive the real source type, then observe each edge

There is no `combo` model or DRIVER type. Drive the **source** exactly as its real element
type above, then walk SPEC's `interactions` in dependency order and assert each dependent
state invariant. Emit one `StateProof` per edge so a broken relationship is localized.
For the live-verified card→custom-power shape, assert both application and the power's
turn-start consequence; its own `fired:` log remains diagnostic:

```csharp
private static async Task InCombat(Player player, CancellationToken ct)
{
    // Link 1 (source): play the card that applies the custom power (as `card` above).
    await PlayerCmd.GainEnergy(3m, player);
    var model = ModelDb.AllCards.First(c => c.Id.Entry == "<CARD_PREFIX>-<CARD_SLUG>");
    var card  = CombatManager.Instance.DebugOnlyGetState()!.CreateCard(model, player);
    await CardPileCmd.Add(card, PileType.Hand);
    var target = card.CombatState?.HittableEnemies.FirstOrDefault()
        ?? throw new InvalidOperationException("interaction target missing");
    await CardCmd.AutoPlay(new BlockingPlayerChoiceContext(), card, target);
    int applied = target.GetPower<<PowerName>>()?.Amount ?? 0;
    StateProof(applied == <EXPECTED_STACKS>,
        $"card -> power expected=<EXPECTED_STACKS> observed={applied}");

    // If the power fires at a SIDE's turn start (AfterSideTurnStart), it won't fire on
    // OUR turn. End the turn, then assert the dependent's real state consequence.
    int hpBefore = target.CurrentHp;
    await Task.Delay(500, ct);
    if (player.PlayerCombatState?.Phase == PlayerTurnPhase.Play)
        PlayerCmd.EndTurn(player, canBackOut: false);   // returns void — do NOT await it
    await Task.Delay(1500, ct);
    int hpAfter = target.CurrentHp;
    StateProof(hpBefore - hpAfter == <EXPECTED_POWER_DAMAGE>,
        $"power trigger expected=<EXPECTED_POWER_DAMAGE> observed={hpBefore - hpAfter}; " +
        $"target hp {hpBefore} -> {hpAfter}");
}
```

> **Proven on the dev box (historical project name `CanaryCombo`, tier-2 PASS):** a debuff
> power whose hook is `AfterSideTurnStart` fires at the **enemy's** turn start, so the
> **required**, not optional — without it `Charge played:` appears but `Signal fired:` never
> does. `PlayerCmd.EndTurn` returns `void` (awaiting it is a CS4008 compile error). If instead
> the dependent power fires immediately on apply (not at a turn start), drop the `EndTurn` and
> the second delay — the first `Task.Delay(500)` is enough.

`verify.md` asks `grep_log.py` for the scenario's **state-proof** vocabulary, for example
`--tier2-pattern "card damage.*observed=6"`. The verifier considers only structured
`<ModName> state proof:` lines and separately requires `selftest done`. Broad
`played|fired|used` logs plus the terminal marker therefore fail. A missing dependent proof
localizes a broken interaction edge (the exact place raw-AI multi-element mods fail).

## State-consuming Counter interactions — test the amount domain

A `consumes` edge for a nonnegative Counter needs more than the normal happy path. The
driver must exercise zero stacks, fewer than N, and at least N in the same hosted scenario,
and reject any retained amount outside the SPEC domain after every case. A finite upper
bound constrains the final hook-modified state, not merely the requested offset. Drive the
real source each time; do not test a helper while bypassing the card/relic/potion that owns
the consumption behavior.

For a card that says "consume up to 4", factor the normal card DRIVER into
`PlayConsumerCard`, then add this sequence (replace the type/id and adapt the numbers from
SPEC). A damaging source may be played three times, so the setup gives all enemies enough
Block to keep the hosted target alive; add `MegaCrit.Sts2.Core.ValueProps` for `ValueProp`.

```csharp
private static async Task PlayConsumerCard(Player player)
{
    await PlayerCmd.GainEnergy(10m, player);
    var model = ModelDb.AllCards.First(c => c.Id.Entry == "<CARD_PREFIX>-<CARD_SLUG>");
    var card = CombatManager.Instance.DebugOnlyGetState()!.CreateCard(model, player);
    await CardPileCmd.Add(card, PileType.Hand);
    Creature? target = card.TargetType == TargetType.AnyEnemy
        ? card.CombatState?.HittableEnemies.FirstOrDefault()
        : null;
    await CardCmd.AutoPlay(new BlockingPlayerChoiceContext(), card, target);
}

private static async Task ExerciseConsumeBoundaries(Player player)
{
    var owner = player.Creature;
    if (owner.GetPower<<PowerName>>() is { } initial)
        await PowerCmd.Remove(initial); // establish the zero-stack precondition

    foreach (var enemy in CombatManager.Instance.DebugOnlyGetState()!.HittableEnemies)
        await CreatureCmd.GainBlock(enemy, 999m, ValueProp.Unpowered, null);

    // 0 stacks: consuming is a no-op and must not create an instance.
    await PlayConsumerCard(player);
    var afterZero = owner.GetPower<<PowerName>>();
    StateProof(afterZero is null,
        $"counter zero consume expected=missing observed={afterZero?.Amount.ToString() ?? "missing"}");

    // Fewer than N (2 < 4): consume the available amount and remove at zero.
    await PowerCmd.Apply<<PowerName>>(new ThrowingPlayerChoiceContext(), owner,
        2m, owner, null);
    await PlayConsumerCard(player);
    var afterFewer = owner.GetPower<<PowerName>>();
    StateProof(afterFewer is null,
        $"counter fewer-than-N 2 -> 0; observed={afterFewer?.Amount.ToString() ?? "missing"}");

    // At least N (6 >= 4): consume exactly N and preserve the remainder.
    await PowerCmd.Apply<<PowerName>>(new ThrowingPlayerChoiceContext(), owner,
        6m, owner, null);
    await PlayConsumerCard(player);
    var remaining = owner.GetPower<<PowerName>>();
    StateProof(remaining?.Amount == 2,
        $"counter at-least-N 6 -> 2; observed={remaining?.Amount.ToString() ?? "missing"}");
}
```

Call `ExerciseConsumeBoundaries(player)` from the source's `InCombat` body instead of
playing the consumer only once. If N is 1, zero is also the only fewer-than-N integer case;
keep the zero case plus an at-least-N remainder case. The successful terminal marker still
comes only after all boundary assertions pass.

### Scry card - one focused visible-selector run

When the Card selects the R6 Scry helper, use the exact driver contract in
`scry-helper.md` instead of proving only its final pile. In one `CombatPlayer` run, assert
zero and empty Draw no-ops; use `CardSelectCmd.UseSelector` for the short-Draw case; then
play the real Card without immediately awaiting its task. Wait for a visible
`NSimpleCardSelectScreen`, assert the play task is incomplete, select known
`NGridCardHolder`s, capture one screenshot, confirm, and await completion. The terminal
assertion covers seen/discarded/unselected order, source result pile, exact
`CardDiscardedEntry` count, and a known `AfterCardDiscarded` consequence.

Assert `NetGameType.Singleplayer` before the scenario. Do not simulate remote ownership,
add a local multiplayer fallback, or promote global Scry hooks. The accepted marker is
`R6 scry helper complete expected=all observed=all` followed by `selftest done`.

## The `CombatEnemy` scenario (monster + encounter; one- and multi-move live)

Enemy-side content (monster + encounter) does not fit the card/relic/potion drivers above:
the harness must enter the **custom encounter**, confirm the **custom monster** spawned, make
the enemy **act**, and observe a **state delta** — through the enemy, not the player. This is
the first non-`CombatPlayer` scenario and reuses the same menu→run navigation
(`NavigateToRunAsync`) and run-UI timing gate; only the room entered and the
in-combat body differ.

The `CombatEnemy` in-combat body (replaces the `InCombat` in the scaffold; do NOT apply
`PlatingPower` — we WANT the enemy's hit to land so the delta is observable):

```csharp
// SelfTest.RunAsync enters the CUSTOM encounter (not CorpseSlugsWeak):
var encounter = ModelDb.Encounter<<Name>Encounter>().ToMutable();
await RunManager.Instance.EnterRoomDebug(RoomType.Monster, MapPointType.Unassigned, encounter);
await WaitHelper.Until(() => CombatManager.Instance.IsInProgress, ct, TimeSpan.FromSeconds(30), "combat not started");
var player = LocalContext.GetMe(RunManager.Instance.DebugOnlyGetState()!);
await InCombat(player!, ct);

// ... and InCombat proves the four CombatEnemy signals:
private static async Task InCombat(Player player, CancellationToken ct)
{
    var combatState = CombatManager.Instance.DebugOnlyGetState()!;

    // ENTER: the custom monster spawned via the custom encounter.
    var mob = combatState.Enemies.FirstOrDefault(e => e.Monster is <Name>)
        ?? throw new InvalidOperationException("<Name> not found in Enemies after entering <Name>Encounter");
    MainFile.Logger.Info("[T2MOD-SELFTEST] <ModName> encounter started: custom encounter ok");
    MainFile.Logger.Info($"[T2MOD-SELFTEST] <ModName> monster present: <Name> hp={mob.CurrentHp}");

    await WaitHelper.Until(
        () => player.PlayerCombatState?.Phase == PlayerTurnPhase.Play || !CombatManager.Instance.IsInProgress,
        ct, TimeSpan.FromSeconds(30), "play phase not reached");
    if (!CombatManager.Instance.IsInProgress) throw new InvalidOperationException("combat ended before player could act");

    // DRIVE: end the player turn → the enemy takes its move.
    int hpBefore = player.Creature.CurrentHp;
    int turnBefore = player.PlayerCombatState!.TurnNumber;
    PlayerCmd.EndTurn(player, canBackOut: false);   // returns void — do NOT await

    // OBSERVE: wait for the player turn to resume (enemy has acted), then assert the delta.
    await WaitHelper.Until(
        () => (player.PlayerCombatState?.Phase == PlayerTurnPhase.Play &&
               player.PlayerCombatState.TurnNumber > turnBefore) ||
              !CombatManager.Instance.IsInProgress,
        ct, TimeSpan.FromSeconds(45), "player play phase not resumed after enemy turn");
    int hpAfter = player.Creature.CurrentHp;
    int delta = hpBefore - hpAfter;
    StateProof(delta == <EXPECTED_DAMAGE>,
        $"enemy attack expected=<EXPECTED_DAMAGE> observed={delta}; " +
        $"player hp {hpBefore} -> {hpAfter}");
}
```

The monster's own move body still logs `attacked:` for diagnosis; verify uses the independent
state proof, for example `"enemy attack.*observed=6"`.

### Multi-turn move vocabulary

The one-turn body above is the fast path for a one-move self-loop. For a multi-move SPEC,
drive the real enemy turn repeatedly and use combat history to prove which move and how many
hits actually resolved. Do not call move bodies, `PerformMove`, `SetMoveImmediate`, or
`ForceCurrentState` from the harness; those bypass normal enemy turn selection.

Add these namespaces:

```csharp
using MegaCrit.Sts2.Core.Combat.History.Entries;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.MonsterMoves.Intents;
using MegaCrit.Sts2.Core.ValueProps;
```

Reusable turn driver:

```csharp
private readonly record struct EnemyTurnObservation(
    string MoveId, int PlayerHpDelta, int HitCount, decimal UnblockedDamage);

private static async Task<EnemyTurnObservation> DriveEnemyTurn(
    Player player, Creature monster, string expectedMoveId, CancellationToken ct)
{
    await WaitHelper.Until(
        () => player.PlayerCombatState?.Phase == PlayerTurnPhase.Play ||
              !CombatManager.Instance.IsInProgress,
        ct, TimeSpan.FromSeconds(30), $"play phase not reached before {expectedMoveId}");
    if (!CombatManager.Instance.IsInProgress)
        throw new InvalidOperationException($"combat ended before {expectedMoveId}");
    var monsterModel = monster.Monster
        ?? throw new InvalidOperationException("enemy creature has no monster model");

    StateProof(monsterModel.NextMove.Id == expectedMoveId,
        $"enemy next move expected={expectedMoveId} observed={monsterModel.NextMove.Id}");

    var history = CombatManager.Instance.History;
    int movesBefore = history.Entries.OfType<MonsterPerformedMoveEntry>()
        .Count(e => ReferenceEquals(e.Monster, monsterModel));
    int attacksBefore = history.Entries.OfType<CreatureAttackedEntry>()
        .Count(e => ReferenceEquals(e.Actor, monster));
    int turnBefore = player.PlayerCombatState!.TurnNumber;
    int hpBefore = player.Creature.CurrentHp;

    PlayerCmd.EndTurn(player, canBackOut: false);   // void -- do NOT await

    // Phase alone can still be the old Play frame. TurnNumber must also advance.
    await WaitHelper.Until(
        () => (player.PlayerCombatState?.Phase == PlayerTurnPhase.Play &&
               player.PlayerCombatState.TurnNumber > turnBefore) ||
              !CombatManager.Instance.IsInProgress,
        ct, TimeSpan.FromSeconds(45), $"player turn not resumed after {expectedMoveId}");
    if (!CombatManager.Instance.IsInProgress)
        throw new InvalidOperationException($"combat ended during {expectedMoveId}");

    var moves = history.Entries.OfType<MonsterPerformedMoveEntry>()
        .Where(e => ReferenceEquals(e.Monster, monsterModel))
        .Skip(movesBefore).ToList();
    StateProof(moves.Count == 1 && moves[0].Move.Id == expectedMoveId,
        $"enemy move history expected={expectedMoveId} " +
        $"observed={string.Join(",", moves.Select(e => e.Move.Id))}");

    var attacks = history.Entries.OfType<CreatureAttackedEntry>()
        .Where(e => ReferenceEquals(e.Actor, monster))
        .Skip(attacksBefore).ToList();
    int hitCount = attacks.Sum(e => e.DamageResults.Count);
    decimal unblocked = attacks.SelectMany(e => e.DamageResults)
        .Sum(r => r.UnblockedDamage);

    return new EnemyTurnObservation(
        expectedMoveId, hpBefore - player.Creature.CurrentHp, hitCount, unblocked);
}
```

For the representative cycle in `recipes/monster.md` (`MUSTER -> PRESSURE -> FLURRY ->
HEALTH_BRANCH -> GUARD|RECOVER -> MUSTER`), the driver body is:

```csharp
var monsterModel = mob.Monster
    ?? throw new InvalidOperationException("enemy creature has no monster model");
var musterIntent = monsterModel.NextMove.Intents.OfType<BuffIntent>().Count() == 1;
StateProof(musterIntent, "monster MUSTER intent expected=buff observed=match");
await DriveEnemyTurn(player, mob, "MUSTER", ct);
var buff = mob.GetPower<<CustomBuff>>();
StateProof(buff?.Amount == 2,
    $"monster self power expected=2 observed={buff?.Amount.ToString() ?? "missing"}");

var pressureIntents = monsterModel.NextMove.Intents;
StateProof(pressureIntents.OfType<SingleAttackIntent>().Count() == 1 &&
           pressureIntents.OfType<DebuffIntent>().Count() == 1,
    "monster PRESSURE intents expected=attack+debuff observed=match");
var pressure = await DriveEnemyTurn(player, mob, "PRESSURE", ct);
var weak = player.Creature.GetPower<WeakPower>();
StateProof(pressure.PlayerHpDelta == 5 && weak?.Amount == 2,
    $"monster attack+debuff expected=5/2 observed={pressure.PlayerHpDelta}/" +
    $"{weak?.Amount.ToString() ?? "missing"}");

var multi = monsterModel.NextMove.Intents.OfType<MultiAttackIntent>().SingleOrDefault();
StateProof(multi?.Repeats == 2,
    $"monster FLURRY intent repeats expected=2 observed={multi?.Repeats.ToString() ?? "missing"}");
var flurry = await DriveEnemyTurn(player, mob, "FLURRY", ct);
StateProof(flurry.HitCount == 2 && flurry.PlayerHpDelta == 8,
    $"monster multi-attack expected=2/8 observed={flurry.HitCount}/{flurry.PlayerHpDelta}");

// At full health the branch must choose GUARD.
int blockBefore = mob.Block;
await DriveEnemyTurn(player, mob, "GUARD", ct);
StateProof(mob.Block - blockBefore == 5,
    $"monster healthy branch expected=GUARD block+5 observed={mob.Block - blockBefore}");

// Change the branch's real input through a public Cmd, without forcing a move state.
int woundedHp = Math.Max(1, mob.MaxHp / 2 - 1);
int setupDamage = mob.CurrentHp - woundedHp;
await CreatureCmd.Damage(new ThrowingPlayerChoiceContext(), mob, setupDamage,
    ValueProp.Unblockable | ValueProp.Unpowered, player.Creature, null);
StateProof(mob.CurrentHp == woundedHp,
    $"monster branch setup expectedHp={woundedHp} observed={mob.CurrentHp}");

// Traverse the explicit cycle again. The stacked buff must change later attack damage.
await DriveEnemyTurn(player, mob, "MUSTER", ct);
buff = mob.GetPower<<CustomBuff>>();
StateProof(buff?.Amount == 4,
    $"monster self power stacked expected=4 observed={buff?.Amount.ToString() ?? "missing"}");

pressure = await DriveEnemyTurn(player, mob, "PRESSURE", ct);
weak = player.Creature.GetPower<WeakPower>();
StateProof(pressure.PlayerHpDelta == 7 && weak?.Amount == 2,
    $"monster buff downstream+debuff expected=7/2 observed={pressure.PlayerHpDelta}/" +
    $"{weak?.Amount.ToString() ?? "missing"}");

flurry = await DriveEnemyTurn(player, mob, "FLURRY", ct);
StateProof(flurry.HitCount == 2 && flurry.PlayerHpDelta == 12,
    $"monster stacked multi-attack expected=2/12 observed={flurry.HitCount}/{flurry.PlayerHpDelta}");

int hpBeforeRecover = mob.CurrentHp;
blockBefore = mob.Block;
await DriveEnemyTurn(player, mob, "RECOVER", ct);
StateProof(mob.CurrentHp - hpBeforeRecover == 3 && mob.Block - blockBefore == 4,
    $"monster wounded branch heal+block expected=3/4 observed=" +
    $"{mob.CurrentHp - hpBeforeRecover}/{mob.Block - blockBefore}");

StateProof(true,
    "monster vocabulary complete expected=all observed=all; " +
    "cycle=twice branches=GUARD,RECOVER");
```

Adapt move ids, numbers, Power types, and branch setup to SPEC. The important invariants are:

- inspect `NextMove` intents before the turn and the matching
  `MonsterPerformedMoveEntry` afterward;
- prove self Power attachment **and** a later changed result;
- assert target debuff amount immediately after the composite move;
- wound through a public Cmd, then assert exact heal/Block deltas;
- prove multi-hit with `CreatureAttackedEntry.DamageResults.Count` (HP total alone is not a
  repeat count);
- drive every advertised branch through its real predicate and traverse enough turns to
  demonstrate the explicit cycle.

> **RitsuLib hosted proof (`RitsuMonsterProof`, 2026-07-22):** the consumer registered
> `BattleFocus`, `CanarySentinel`, and its global encounter through one content pack using
> `ModPowerTemplate`, `ModMonsterTemplate`, and `ModEncounterTemplate`. A headed
> RitsuLib-only run observed Power `2 -> 4`, attack/debuff `5/2 -> 7/2`, two-hit totals
> `8 -> 12`, healthy Block `+5`, wounded HP/Block `+3/+4`, both branch exits, and the
> complete two-cycle marker. The same checked 360x360 PNG rendered with 396x396 bounds and
> intent `(0,-466)` in combat and the default bestiary. It reached `selftest done`, passed
> strict Tier 2, and had no fresh error.

> **Live-proven (`CanaryEncounter`, tier-2 PASS):** the `PlayerCmd.EndTurn` gate is the same
> as `CombatRoomHandler`'s AutoSlay loop — after the enemy turn, control returns to the
> player at `Phase == Play`. The one bug this surfaced: the monster's attack must use
> `DamageCmd.Attack(n).FromMonster(this).Execute(null)`. Using the card `.Targeting(target)`
> chain hangs the enemy turn and the second gate times out (`selftest FAILED: player play
> phase not resumed after enemy turn`). `recipes/monster.md` documents this.
> Needs `using MegaCrit.Sts2.Core.Map;` for `MapPointType`.

## The `RunStart` + `CombatPlayer` scenario (Character Foundation, RitsuLib live 2026-07-23)

A character is not proven by `ModelDb` registration alone. The harness must select its
real UI button, start a run as it, assert the starter ecosystem, then enter combat and
prove one hosted mechanic. Replace the baseline's first-unlocked selection with:

```csharp
var registered = ModelDb.AllCharacters.OfType<<CharacterName>>().ToList();
StateProof(registered.Count == 1,
    $"content-pack registration expected=1 observed={registered.Count}");
var canonical = registered.Single();
var expectedIconPath = <CharacterName>.CharacterUi("<select-file>.png")
    .Replace('\\', '/');
var buttons = UiHelper.FindAll<NCharacterSelectButton>(
    charSelect!.GetNode("CharSelectButtons/ButtonContainer"));
var pick = buttons.SingleOrDefault(button =>
    button.GetNodeOrNull<TextureRect>("%Icon")?.Texture?.ResourcePath.Replace('\\', '/') ==
    expectedIconPath);
StateProof(pick?.Character is <CharacterName> && !pick.IsLocked,
    $"character select expected=<CharacterName>/unlocked " +
    $"observed={(pick == null ? "missing" : pick.Character.GetType().Name + "/locked=" + pick.IsLocked)}");
pick!.UnlockIfPossible();
pick.Select();
await Task.Delay(100, ct);
await UiHelper.Click(await WaitHelper.ForNode<NButton>(mainMenu,
    "Submenus/CharacterSelectScreen/ConfirmButton", ct, TimeSpan.FromSeconds(10)));
```

After `IsInProgress`, wait for `NRun.Instance?.GlobalUi != null`, get the local player,
and assert concrete runtime state rather than only canonical model declarations:

```csharp
var player = LocalContext.GetMe(RunManager.Instance.DebugOnlyGetState()!)
    ?? throw new InvalidOperationException("local player missing");
var character = player.Character;
StateProof(character is <CharacterName> &&
           player.Creature.CurrentHp == <HP> && player.Creature.MaxHp == <HP>,
    $"run start expected character=<CharacterName> hp=<HP>/<HP> " +
    $"observed={character.GetType().Name} hp={player.Creature.CurrentHp}/{player.Creature.MaxHp}");

// Also assert concrete CardPool/RelicPool/PotionPool types plus AllCards/AllRelics/
// AllPotions membership, then the exact player.Deck.Cards and player.Relics multisets.
```

Enter the minimal combat as in `CombatPlayer`, wait for `PlayerTurnPhase.Play`, and
assert both designed energy and the independent starter behavior. The live canary used
a turn-1 starter relic:

```csharp
var combat = player.PlayerCombatState!;
StateProof(combat.MaxEnergy == 3 && combat.Energy == 4,
    $"combat energy expected max/current=3/4 observed={combat.MaxEnergy}/{combat.Energy}");
StateProof(true,
    "character foundation/static-presentation expected=<selected-contract> observed=all");
```

When static presentation is selected, do not stop at model properties. In the same run,
assert the visible 132x195 selection portrait and 1920x1200 background; 512x512 non-Spine
combat body; normal and outlined 88x88 top-panel textures under the same real
`NTopBarPortrait`; one native counter with five 256x256 energy layers; and the 24x24 compact
icon in a real hand card. Also assert each generated Relic's exact 256x256 main/outline
textures under the same real `NRelic`, plus its explicit big-icon path. Compare the
CharacterModel main/outline texture properties to the same top-icon paths so a decorative
proof-only node cannot hide broken RitsuLib wiring. Then finish combat and enter RestSite and Shop
to assert the real `NRestSiteCharacter` and `NMerchantCharacter` with their 512x512 bodies.
Capture settled selection, combat/top-panel/energy, RestSite, and Shop screenshots.

For the M6.5 card/UI theme, replace the shared compact-icon assertion with two
independent consumers. Assert the Character/card-pool properties equal all four theme
colors; `PoolFrameMaterial` is the cached theme `ShaderMaterial` with exact
`target_color`/`brightness`; `BigEnergyIconPath` and `TextEnergyIconPath` are distinct,
existing, and load as 256x256/24x24 textures; a visible real `NCard.%EnergyIcon` uses the
large path; and a real formatted card description embeds the text path. Emit
`character theme expected=colors/frame/large-icon/text-icon observed=all` only after every
assertion succeeds. Automatic node/property proof is required even when the maintainer
chooses to perform the focused visual review manually.

For bounded Character combat cues, read `reference/character-combat-cues.md` and keep the
proof independent from the static/theme marker. Assert all eighteen exact 512x512 paths,
shared style plus Bounds/Intent/Center/Orb/Talk geometry,
Idle advance/loop, Attack trigger and return to Idle, damage-triggered Hit and return to
Idle, first-combat playback-node cleanup, and Dead's contracted duration/final-frame hold
in a fresh combat. Emit
`character combat cues complete expected=Idle/Attack/Hit/Dead/cleanup observed=all` only
after every assertion succeeds.

Run one separate missing-frame variant. Omit exactly one expected frame and assert that the
entire private cue set is unavailable, the exact static 512x512 `combat.png` is mounted,
no cue playback node exists, and no surviving action frame appears. Its marker is
`combat cue fallback expected=one-missing-disables-all/static-combat512/no-playback observed=all`.
The user performs both headed observations; do not infer motion or fallback from model-only
state. `CharacterAssetProfile.VisualCues` must remain unset so merchant/rest retain their
static textures.

> **R4 live-proven (Wayfinder, build 0/0 + strict Tier 2 PASS, 2026-07-23):** RitsuLib
> content-pack registration count was 1; the exact custom icon button was selected; the run
> started at HP `72/72`, Gold `99`, exact pools `7/1/1/1`, starter deck `5 Strike + 5
> Guard`, and one Compass. Combat observed Energy `3/4`, the exact non-Spine body,
> top-panel icon, five layers, and compact icon. Selection, combat, RestSite, and Shop all
> produced settled screenshots; the final marker reported
> `character foundation/static-presentation ... observed=all`, followed by `selftest done`
> and no fresh error.

## Advanced `CombatPlayer` capabilities (R5 RitsuLib live 2026-07-23)

The Character Foundation checks still run for a generated character, but they do not
replace each selected capability's own invariant. Read the capability page and add its
driver after combat reaches `PlayerTurnPhase.Play`.

### Resource/UI

Use `reference/character-resource.md`. Resolve the public RitsuLib attachment, drive the
real gain and spender cards, then enter a second combat. Before the terminal marker assert
all of:

1. `RegisterCombatUi` mounted the control and `SecondaryResourceCmd.Get` starts at zero;
2. the checked icon path/24x24 size or text-only fallback, 220x32 root, 188x32 Label,
   `(160,0)` offset, and non-intersection with native Energy are exact;
3. gain changes state and counter;
4. one affordable and one unaffordable check return the expected values;
5. successful spend changes amount and payoff exactly once;
6. rejected spend changes neither amount nor payoff and never creates debt;
7. combat 2 has a distinct `PlayerCombatState`, amount zero, and reset counter.

Finish with:

```csharp
StateProof(true, "resource UI complete expected=all observed=all");
```

`RitsuResourceProof` observed amount `0 -> 3 -> 1`, Block `+4` only on payment, a rejected
second cost at amount `1`, and distinct-combat amounts `1/0`. The final
`RitsuWayfinderProof` observed Ink `0 -> 4 -> 0`, resource rect `(260,828,220,32)` disjoint
from energy rect `(100,828,128,128)`, and combat-2 Ink `0` with native Energy `3/4`.

### Ordered semantic buffer/dynamic output

Use `reference/ordered-card-buffer.md`. Drive real source cards through normal visual/result
pile behavior, compile through the generated domain method, play the produced card, and
enter a second combat. Assert all of:

1. the `AttachedState<PlayerCombatState,TState>` buffer and player-visible state start empty;
2. accepted semantic values preserve exact order and every source reaches its normal
   result pile;
3. capacity overflow leaves the buffer/resource unchanged while its source still resolves;
4. the compile card resolves normally, clears state, and refreshes visible text;
5. the output stores the ordered snapshot and exact deterministic `DynamicVars`;
6. exactly one matching `CardGeneratedEntry` exists and the output effect fires;
7. rejected output payment leaves amount and payoff unchanged;
8. combat 2 owns a distinct attached state, empty route, reset resource, and reset UI.

Finish with:

```csharp
StateProof(true, "ordered buffer complete expected=all observed=all");
```

The final Wayfinder suite observed four source Cards plus the compile Card in Discard,
route text `- -> N>E>S>W -> -`, rejected overflow, generated history `1`, configured and
actual Block `20`, successful Ink `4 -> 0`, rejected payment at `0`, and a distinct empty
second-combat state. Finish the composed suite with
`wayfinder R5 parity complete expected=all observed=all`. Retained-card custom piles are
not covered by this supported path.

## The `MapNode` scenario (event / World Node - RitsuLib live 2026-07-23)

An event is not proven by registration alone. The harness must enter its real `EventRoom`,
wait for the nested event UI, click an actual `NEventOptionButton`, and observe the option's
run-state consequence. Reuse the fixed menu-to-run navigation and `NRun.GlobalUi` timing
gate. Before debug-entering an Event, wait until the normal startup has generated its map
and created its first room; this prevents terminal Event/combat paths from opening a half-
initialized `NMapScreen`:

```csharp
await WaitHelper.Until(
    () => RunManager.Instance.DebugOnlyGetState()?.Map is not NullActMap &&
          (NRun.Instance?.EventRoom?.Layout != null || NRun.Instance?.MapRoom != null),
    ct, TimeSpan.FromSeconds(30), "initial map and room did not finish loading");

var canonical = ModelDb.Event<<Name>>();
await RunManager.Instance.EnterRoomDebug(RoomType.Event, MapPointType.Unknown, canonical);

EventRoom? room = null;
await WaitHelper.Until(() =>
{
    room = RunManager.Instance.DebugOnlyGetState()?.CurrentRoom as EventRoom;
    return room?.LocalMutableEvent is <Name> && NEventRoom.Instance?.Layout != null;
}, ct, TimeSpan.FromSeconds(30), "custom event room not entered");

var mutableEvent = (<Name>)room!.LocalMutableEvent;
NEventOptionButton? choice = null;
await WaitHelper.Until(() =>
{
    var eventRoomNode = NEventRoom.Instance;
    if (eventRoomNode == null) return false;
    choice = UiHelper.FindAll<NEventOptionButton>(eventRoomNode)
        .SingleOrDefault(button =>
            !button.Option.IsLocked
            && button.Option.Title.GetFormattedText() == "<Option title>");
    return choice is { IsEnabled: true, Visible: true };
}, ct, TimeSpan.FromSeconds(30), "event option not available");

// ENTER/LOC: prove title + nested option localization before driving the choice.
var title = mutableEvent.Title.GetFormattedText();
var optionTitle = choice!.Option.Title.GetFormattedText();
var optionDescription = choice.Option.Description.GetFormattedText();
if (title != "<Title>" || optionTitle != "<Option title>" || optionDescription.Length == 0)
    throw new InvalidOperationException(
        $"Nested event localization mismatch: title='{title}', option='{optionTitle}', description='{optionDescription}'");
MainFile.Logger.Info($"[T2MOD-SELFTEST] <ModName> event entered: title='{title}' option='{optionTitle}'");

// DRIVE/OBSERVE: click the game's real option UI and assert the SPEC consequence.
var player = LocalContext.GetMe(RunManager.Instance.DebugOnlyGetState()!)
    ?? throw new InvalidOperationException("local player not found");
var before = player.Gold;
await UiHelper.Click(choice);
await WaitHelper.Until(
    () => player.Gold == before + <amount> && mutableEvent.IsFinished,
    ct, TimeSpan.FromSeconds(30), "event option consequence not observed");

var resultDescription = mutableEvent.Description?.GetFormattedText() ?? string.Empty;
if (resultDescription.Length == 0)
    throw new InvalidOperationException("result page localization missing");
StateProof(player.Gold - before == <amount> && mutableEvent.IsFinished,
    $"event gold expected=<amount> observed={player.Gold - before}; " +
    $"gold {before} -> {player.Gold}; resultLoc={resultDescription.Length > 0}");
```

Required namespaces beyond the fixed scaffold: the event type; `MegaCrit.Sts2.Core.Map`;
`MegaCrit.Sts2.Core.Nodes.Events`; `MegaCrit.Sts2.Core.Nodes.Rooms`; and
`MegaCrit.Sts2.Core.Rooms`. `System.Linq` is already used by the navigation code.

Select the button by the SPEC option's formatted title, not merely "the only unlocked
option". The fast path drives one specified consequence; the extended path below drives
each independent outcome family declared by SPEC.
The event option method logs its own `option chosen:` marker **after** the Cmd changes run
state. The harness independently asserts the same state and emits `state proof:`. Verify
with a pattern such as `"event gold.*observed=25"`; the verifier still requires the exact
load marker and `selftest done`.

### Extended outcomes, special combat, VFX, and rich text

When SPEC uses the full Event vocabulary, read `reference/event-outcomes.md` and drive one
real UI path per independent semantic invariant. Do not create one harness project per
outcome. The supported combined shape is:

1. immediate Cmd and `SetEventState`;
2. a blocking `CardSelectCmd` overlay, then its exact deck mutation;
3. a resumable special combat, then the named `Resume` page;
4. a blocking `RewardsCmd.OfferCustom` overlay, then its exact reward state;
5. click the standard proceed option and confirm the real map opens;
6. enter a fresh mutable Event instance for a terminal special-combat branch;
7. finish combat and confirm the map opens without `Resume`.

Each mutable Event instance starts at most one special combat. This is a runtime boundary,
not just a test simplification.

Wait for the standard Event completion option by semantics, never localized English text:

```csharp
NEventOptionButton? proceed = null;
await WaitHelper.Until(() =>
{
    var eventRoom = NEventRoom.Instance;
    if (eventRoom == null)
        return false;
    proceed = UiHelper.FindAll<NEventOptionButton>(eventRoom)
        .SingleOrDefault(button => button.Option.IsProceed);
    return proceed is { IsEnabled: true, Visible: true };
}, ct, TimeSpan.FromSeconds(30), "event proceed option not available");
await UiHelper.Click(proceed!);
```

For a resumable combat, retain the first mutable Event reference and require all of:

```csharp
await WaitHelper.Until(
    () => RunManager.Instance.DebugOnlyGetState()?.CurrentRoom is EventRoom &&
          NEventRoom.Instance?.Layout != null &&
          mutableEvent.ResumeCount == 1,
    ct, TimeSpan.FromSeconds(30), "event did not resume after special combat");
```

For a terminal branch, require an open map, zero resumes on the fresh Event instance, and
no live `NEventRoom`. Identify every combat through its mutable custom encounter type; a
generic `CombatRoom` is not proof of the requested fight.

If SPEC selects `portrait_halo`, follow `reference/event-vfx.md`. Assert the named root is
visible and animating (or intentionally static in Instant mode), then prove it is freed on
page/combat transitions. Delay screenshots until the option UI and room fade are visibly
settled; a node path or near-black transition frame is not visual evidence.

If SPEC selects bounded Event rich text, follow `reference/event-text-effects.md` in this
same `MapNode` run. Resolve `%EventDescription` as a BBCode-enabled `MegaRichTextLabel`,
assert every required allowed host effect type is installed and the exact balanced tags reached its raw text,
then switch to a second authored page and prove the same label contains the new tags but
none of the prior page's tagged span. Capture both settled player-visible states; do not
create a text-only Event project or re-run the other outcome families separately.

If SPEC selects native Card/relic acquisition, `weak_short`, or built-in `trial_noble`,
follow `reference/event-native-presentation.md` in this same `MapNode` run. Wait for the
initial Event description to reach full `VisibleRatio` and opacity, assert the exact
built-in scene parent/position/inherited process mode, then click the real option. Observe
the matching `NCard` in the native preview container and the matching
`NRelicInventoryHolder`; assert exact deck/relic deltas and no duplicates. Sample the
public shake target until it moves and returns when the preference is nonzero, or remains
still at preference index zero. Finish only after the Card preview and owned VFX are gone
and the result page is readable. One marker may cover all selected profiles.

> **Live-proven (`CanaryNativePresentation`, strict Tier-2 PASS, 2026-07-21):** one
> 35-second headed run observed `cardDelta=1 relicDelta=1`, preference index `2` with
> movement and return, exact `trial_noble` scene/host/position/process mode, Card-preview
> and VFX cleanup, three settled screenshots, `selftest done`, and no fresh error.

> **Live-proven (`CanaryEvent`, strict tier-2 PASS, 2026-07-20):** one hosted run drove
> page Cmd, upgrade selection, resumable custom combat, custom Gold reward, terminal custom
> combat from a fresh Event instance, and VFX cleanup. The structured proof reported
> `expected=pageCmd+cardSelection+resumableCombat+customReward+terminalCombat+vfxCleanup`
> with the identical observed value, `resumes=1/0`, `selftest done`, and no fresh error.
> Headed screenshots showed the initial/page/resumed portrait halos and the actual special
> combat after its room fade.

> **R4 close (RitsuLib `0.4.67`, strict Tier-2 PASS, 2026-07-23):** one combined headed
> run repeated core pages/Cmds, option/lethal/native presentation, outcomes, rich text,
> portrait-halo lifecycle, and forced follow-up against stable `0.107.1`. It reached every
> structured family marker, `selftest done`, and no fresh error.

### Bounded forced follow-up Event variant

When SPEC selects `reference/forced-followup-event.md`, replace direct canonical Event
entry with one compact real-map proof. Reuse the same run/map startup gate above, then:

1. call `Hook.ModifyUnknownMapPointRoomTypes` and `Hook.ModifyNextEvent` without the Quest
   token and require unchanged inputs;
2. add one run-created token to `PileType.Deck` with `skipVisuals: true` as proof setup;
3. require unchanged inputs in the wrong act;
4. enter the specified act and require `{ RoomType.Event }` plus the target canonical
   Event from the two hooks;
5. call `EnterMapPointInternal(..., MapPointType.Unknown, ..., saveGame: false)`, wait for
   the target mutable Event and real option button, then capture one settled screenshot;
6. click the completion option, require the token count to become zero, and require both
   hooks to return their ordinary inputs again.

Do not debug-enter the target Event: that skips both invariants this variant exists to
prove. Keep all guards, the real room, UI click, consumption, and restoration in one headed
run and one structured marker. Required additional namespaces are
`MegaCrit.Sts2.Core.Hooks`, `MegaCrit.Sts2.Core.Models.Events`, and the Quest Card/target
Event types.

> **R4 live-proven (strict Tier-2 PASS, 2026-07-23):** the combined RitsuLib Event run
> reported `noToken=True wrongAct=True roomForced=True eventForced=True entered=true
> seals=1->0 restored=True`, reached `selftest done`, and had no fresh error. The screenshot
> showed the real `Sealed Archive` room and `Break the seal` option.

## Relic-owned Rest Site option focused host

Use `reference/rest-site-options.md` for the supported contract. This proof is not a
`CombatPlayer` substitute: it must enter the real Rest Site through
`RunManager.Instance.EnterRoomDebug(RoomType.RestSite, MapPointType.RestSite)` or the
equivalent `room RESTSITE` dev-console command.

The focused proof Mod should expose diagnostic snapshots, but the reviewer drives the
native buttons. Before each selection, record Gold, Current HP, Max HP, the owner's saved
use flag, current option IDs, and current map-history Rest Site choices. After selection,
emit one structured line only when all expected deltas match:

```text
[T2MOD-SELFTEST] <ModName> state proof: framework=RitsuLib frameworkVersion=0.4.67 host=0.107.1 compat=0.107.1 expected=rest-site gold=-30 maxHp=+5 history=1 repeat=hidden observed=rest-site gold=-30 maxHp=+5 history=1 repeat=hidden
```

The required matrix is:

1. no owner produces no custom option;
2. owner plus insufficient Gold produces one disabled option;
3. an enabled button whose Gold becomes insufficient after rendering calls `OnSelect`,
   returns false, and preserves Gold, Max HP, saved use, history, and every option ID;
4. success produces exact fixed-Gold and deterministic-outcome deltas, one history entry,
   and no second custom option in the rebuilt same-visit list;
5. native options either clear normally or remain according to SPEC, with the selected
   custom option removed in both cases;
6. a second visit matches once-per-site or once-per-run semantics;
7. explicit non-singleplayer generation produces no custom option;
8. the custom-icon and missing-icon builds both preload without a fresh error.

Button color, localization, image framing, hover, and controller focus are headed
observations. A model-generated list cannot prove them. When the human lead reserves this
headed run, do not launch the game automatically; provide the exact console route and keep
an unrun strict `selftest done` as an explicit verification exception.

## Deferred: the headless / menu-skip path (design seam, not built in M5)

The fragile part is `NavigateToRunAsync` (scene-tree paths shift across versions). The
game's own **menu-skip** sequence removes it entirely — `NSceneBootstrapper.StartNewRun`
does `RunState.CreateForNewRun(...)` → `RunManager.Instance.SetUpNewSingleplayer(runState,
false, null)` → `Launch()` → `EnterRoomDebug(...)`, no UI at all. When headless is taken
up (M5 follow-on), swap `NavigateToRunAsync` for that; the rest of the harness is
unchanged. Not built now — it touches `_game.RootSceneContainer`/`SetActInternal`, which
need their own mod-reachability grounding first.

## Checklist

- [ ] `SelfTest.cs` emitted in `<ModName>Code/`, in the same namespace as `MainFile.cs` (`<ModName>.<ModName>Code`) so `MainFile.Logger` resolves.
- [ ] `MainFile.Initialize()` has, after the load marker: `if (CommandLineHelper.HasArg("t2selftest")) SelfTest.Arm();`
- [ ] Exactly one source driver is filled per SPEC (relic → `BeforeCombat`; card/potion → `InCombat`; monster+encounter → `CombatEnemy`; event → `MapNode` real room + all independent option outcomes); a forced follow-up Event enters through one real Unknown MapPoint instead of direct canonical entry; multi-element interactions reuse that real source driver and add observations.
- [ ] Native Event presentation proves the real Card/relic consumers, preference-aware
      shake movement/return, settled text, exact built-in VFX placement/process mode, and
      preview/VFX cleanup in one `MapNode` run.
- [ ] `<PREFIX>-<SLUG>` ids match the element's real `Id.Entry` (SPEC's derived ids).
- [ ] The element's own type-specific marker (author.md step 2) is present for diagnosis.
- [ ] The harness snapshots concrete state, asserts the SPEC's exact post-state, and calls
      `StateProof`; broad trigger/preview markers are never used as Tier-2 proof.
- [ ] A multi-move `CombatEnemy` waits for `TurnNumber` to advance, asserts `NextMove`
      intents + `MonsterPerformedMoveEntry`, and traverses every declared cycle/branch outcome.
- [ ] Multi-hit proof counts `CreatureAttackedEntry.DamageResults`; self Power proof includes
      its downstream changed result; Block/Heal/debuff assertions read exact live state.
- [ ] Every nonnegative Counter `consumes` edge runs zero/fewer-than-N/at-least-N cases
      and asserts after each that no negative instance exists.
- [ ] Never claim tier-2 on a `selftest FAILED` line — that's a harness/setup miss, report tier-1 + manual fallback.
