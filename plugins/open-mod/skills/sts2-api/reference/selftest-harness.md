# Reference: the tier-2 self-test harness (`SelfTest.cs`)

> A copy-adaptable, **known-good** in-process harness that makes tier-2 ("the effect
> actually fires") automatic — no human at the keyboard, no dev-console typing. Every
> API here was confirmed against decompiled `sts2.dll` (M5 grounding) — not guessed.
>
> **What it is:** one `SelfTest.cs` file compiled into the generated mod, **dormant
> unless launched with `--t2selftest`**. When that arg is present, it drives the game
> from the main menu into a minimal combat with zero interaction, fires the element's
> effect, and logs the same `[T2MOD-SELFTEST] … fired/used` marker the manual path used.
> `verify.md` then greps that marker — the effect is proven, not eyeballed.
>
> **Ship-safety:** the arg gate (`CommandLineHelper.HasArg("t2selftest")`) means a normal
> user launch never arms it — no menu driving, no `CombatSetUp` side effects. It is inert.

## Why in-process, and why it drives its own navigation

- **In-process (not keystroke injection / external MCP):** the harness *is* mod code, so
  it calls the game's own public Cmds directly. No OS automation, no second process.
- **It drives navigation itself** (main menu → run → jump to combat), so it knows exactly
  when combat is reachable. That means it uses the game's own **poll pattern** — the same
  code `CombatRoomHandler` (MegaCrit's AutoSlay) uses — not an event subscription:
  `WaitHelper.Until(() => CombatManager.Instance.IsInProgress)`, then wait for the **Play**
  phase before playing a card. Race-free.

## The one correction that matters (do NOT regress)

`NDevConsole.Instance` exists, but its inner `DevConsole` is a **private field** — so the
string-in `ProcessCommand("fight …")` / `"card …"` path is **NOT reachable** from a mod
assembly. Do not try to reflect into it. Instead the harness calls the **public Cmds**
that each console command wraps (all confirmed `public static`, shipped in `sts2.dll`):

| Console command | Public API the harness calls instead |
|---|---|
| `fight <id>` | `RunManager.Instance.EnterRoomDebug(RoomType.Monster, MapPointType.Unassigned, encounter.ToMutable())` |
| `relic add <id>` | `RelicCmd.Obtain(relic.ToMutable(), player)` |
| `card <ID>` | `CombatManager.Instance.DebugOnlyGetState().CreateCard(card, player)` + `CardPileCmd.Add(c, PileType.Hand)` |
| `energy N` | `PlayerCmd.GainEnergy(3m, player)` |
| `potion <ID>` | `PotionCmd.TryToProcure(potion.ToMutable(), player)` |
| (play the card) | `CardCmd.AutoPlay(new BlockingPlayerChoiceContext(), card, target)` |
| (use the potion) | `potion.EnqueueManualUse(target)` *(not a Cmd — a method on the model)* |

## Two timing gates that are load-bearing (proven on the dev box, do NOT regress)

The first live end-to-end run (CanaryCard, tier-2 PASS) exposed two race conditions that
crashed the harness before it reached combat. Both are now baked into the scaffold above —
keep them:

1. **FTUE-disable must be best-effort.** `SaveManager.Instance` (and its FTUE state) is
   **not reliably up** when `Initialize()` runs `Arm()` — even `WaitHelper.Until(() =>
   SaveManager.Instance != null)` does not make `SetFtuesEnabled` safe. Calling it unguarded
   throws `NullReferenceException` and kills the whole self-test. It is **non-essential**
   (worst case: a tutorial popup that nav dismisses), so wrap it:
   `try { SaveManager.Instance?.SetFtuesEnabled(false); } catch { }`. Never let it abort.

2. **`IsInProgress` is NOT enough to call `EnterRoomDebug`.** `RunManager.Instance.
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

## Marker vocabulary (three-way signal for verify/repair)

The harness logs one of three terminal lines so `verify.md`/`repair.md` can tell setup
failure from a real effect bug:

- `[T2MOD-SELFTEST] <ModName> selftest done` — reached combat, drove the effect, finished.
- `[T2MOD-SELFTEST] <ModName> selftest FAILED: <stage>: <reason>` — harness couldn't reach
  combat (navigation/timeout). **This is a harness/setup problem, NOT an effect bug** —
  `verify.md` falls back to the manual guide and reports tier-1 only.
- the element's own `[T2MOD-SELFTEST] <Element> fired/used: …` (from author.md step 2) —
  this is the actual tier-2 proof; absent-after-`done` = effect didn't fire (real bug).

## The fixed scaffold (identical for every mod — do not hand-edit per element)

Emit this as `<ModName>Code/SelfTest.cs`. Only the **`BeforeCombat` / `InCombat`** bodies
(the "DRIVER" region) change per element type — fill them from the table further down.
`<ModName>` / `<PREFIX>-<SLUG>` are substituted exactly as elsewhere.

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
using MegaCrit.Sts2.Core.Saves;

namespace <ModName>.<ModName>Code;   // SAME namespace as MainFile.cs (scaffold nests <ModName>Code)

// Verification-only. Dormant unless the game is launched with --t2selftest.
// Gated in MainFile.Initialize(): if (CommandLineHelper.HasArg("t2selftest")) SelfTest.Arm();
internal static class SelfTest
{
    private static bool _armed;

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
            // Kill FTUE popups so they can't block nav. BEST-EFFORT ONLY: SaveManager (and
            // its FTUE state) is NOT reliably up at Initialize time — calling it unguarded
            // NREs and kills the whole run. Skipping it is harmless (a stray tutorial popup
            // at worst, which nav dismisses). Never let it abort the self-test.
            try { SaveManager.Instance?.SetFtuesEnabled(false); } catch { /* FTUE not ready — ignore */ }

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

The element's own `fired/used` marker (author.md step 2) is what proves tier-2 — the
driver's only job is to *make it fire*. Branch on SPEC's `element`:

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
private static Task InCombat(Player player, CancellationToken ct) => Task.CompletedTask;
```

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
    await CardCmd.AutoPlay(new BlockingPlayerChoiceContext(), card, target);
}
```
(`TargetType` is `MegaCrit.Sts2.Core.Models` — already imported. For an attack the
`card.CombatState.HittableEnemies` list is the slugs from the minimal encounter.)

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
    potion.EnqueueManualUse(target);        // drives the potion's OnUse → its used: marker
    await Task.Delay(500, ct);              // let the enqueued use resolve before `done`
}
```

### multi-element interactions — drive the real source type, then observe each edge

There is no `combo` model or DRIVER type. Drive the **source** exactly as its real element
type above, then walk SPEC's `interactions` in dependency order and assert the dependent's
own marker/state invariant. Each edge proves itself, so a broken relationship is localized.
For the live-verified card→custom-power example, use the `card` body; the dependent power's
`AfterSideTurnStart`/apply hook logs its own `fired:` marker:

```csharp
private static async Task InCombat(Player player, CancellationToken ct)
{
    // Link 1 (source): play the card that applies the custom power (as `card` above).
    await PlayerCmd.GainEnergy(3m, player);
    var model = ModelDb.AllCards.First(c => c.Id.Entry == "<CARD_PREFIX>-<CARD_SLUG>");
    var card  = CombatManager.Instance.DebugOnlyGetState()!.CreateCard(model, player);
    await CardPileCmd.Add(card, PileType.Hand);
    var target = card.CombatState?.HittableEnemies.FirstOrDefault();
    await CardCmd.AutoPlay(new BlockingPlayerChoiceContext(), card, target);
    // Link 2 (dependent): the applied power logs its OWN [T2MOD-SELFTEST] <Power> fired:
    // marker from its hook. If the power fires at a SIDE's turn start (AfterSideTurnStart),
    // it won't fire on OUR turn — end the turn so the enemy's turn starts and triggers it.
    await Task.Delay(500, ct);
    if (player.PlayerCombatState?.Phase == PlayerTurnPhase.Play)
        PlayerCmd.EndTurn(player, canBackOut: false);   // returns void — do NOT await it
    await Task.Delay(1500, ct);                         // let the enemy turn start + power fire
}
```

> **Proven on the dev box (historical project name `CanaryCombo`, tier-2 PASS):** a debuff
> power whose hook is `AfterSideTurnStart` fires at the **enemy's** turn start, so the
> **required**, not optional — without it `Charge played:` appears but `Signal fired:` never
> does. `PlayerCmd.EndTurn` returns `void` (awaiting it is a CS4008 compile error). If instead
> the dependent power fires immediately on apply (not at a turn start), drop the `EndTurn` and
> the second delay — the first `Task.Delay(500)` is enough.

`verify.md` asks `grep_log.py` for the type-specific **effect** vocabulary only (for
example `--tier2-pattern "fired|used|played"`). The verifier separately requires the
successful `selftest done` terminal marker and excludes all terminal/load lines from effect
matching. A terminal `done` therefore proves only that the driver completed; it can never
make a missing effect marker pass.
A missing dependent marker after `selftest done` means the interaction link is broken (the
exact place raw-AI multi-element mods fail).

## The `CombatEnemy` scenario (monster + encounter — earned seam, live 2026-07-10)

Enemy-side content (monster + encounter) does not fit the card/relic/potion drivers above:
the harness must enter the **custom encounter**, confirm the **custom monster** spawned, make
the enemy **act**, and observe a **state delta** — through the enemy, not the player. This is
the first non-`CombatPlayer` scenario and reuses the same menu→run navigation
(`NavigateToRunAsync`) and the same two timing gates; only the room entered and the
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
    PlayerCmd.EndTurn(player, canBackOut: false);   // returns void — do NOT await

    // OBSERVE: wait for the player turn to resume (enemy has acted), then assert the delta.
    await WaitHelper.Until(
        () => player.PlayerCombatState?.Phase == PlayerTurnPhase.Play || !CombatManager.Instance.IsInProgress,
        ct, TimeSpan.FromSeconds(45), "player play phase not resumed after enemy turn");
    int hpAfter = player.Creature.CurrentHp;
    int delta = hpBefore - hpAfter;
    if (delta <= 0 && CombatManager.Instance.IsInProgress)
        throw new InvalidOperationException($"enemy did not attack: hp {hpBefore} -> {hpAfter}");
    MainFile.Logger.Info($"[T2MOD-SELFTEST] <ModName> action advanced: player hp {hpBefore} -> {hpAfter} delta={delta}");
}
```

The monster's own move body logs the `attacked:` effect marker (author.md), so verify greps
a pattern like `"attacked|action advanced|encounter started|monster present"`.

> **Live-proven (`CanaryEncounter`, tier-2 PASS):** the `PlayerCmd.EndTurn` gate is the same
> as `CombatRoomHandler`'s AutoSlay loop — after the enemy turn, control returns to the
> player at `Phase == Play`. The one bug this surfaced: the monster's attack must use
> `DamageCmd.Attack(n).FromMonster(this).Execute(null)`. Using the card `.Targeting(target)`
> chain hangs the enemy turn and the second gate times out (`selftest FAILED: player play
> phase not resumed after enemy turn`). `recipes/monster.md` documents this.
> Needs `using MegaCrit.Sts2.Core.Map;` for `MapPointType`.

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
- [ ] Exactly one source driver is filled per SPEC (relic → `BeforeCombat`; card/potion → `InCombat`; monster+encounter → the `CombatEnemy` `InCombat` that enters the custom encounter and ends the turn); multi-element interactions reuse that real source driver and add observations.
- [ ] `<PREFIX>-<SLUG>` ids match the element's real `Id.Entry` (SPEC's derived ids).
- [ ] The element's own `fired/used` marker (author.md step 2) is present — the harness only *triggers*; the element logs the proof.
- [ ] Never claim tier-2 on a `selftest FAILED` line — that's a harness/setup miss, report tier-1 + manual fallback.
