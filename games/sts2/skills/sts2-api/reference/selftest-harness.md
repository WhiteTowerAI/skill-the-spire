# Reference: the tier-2 self-test harness (`SelfTest.cs`)

> A copy-adaptable, **known-good** in-process harness that makes tier-2 ("the effect
> actually fires") automatic — no human at the keyboard, no dev-console typing. Every
> API here was confirmed against decompiled `sts2.dll` (M5 grounding) — not guessed.
>
> **What it is:** one `SelfTest.cs` file compiled into the generated mod, **dormant
> unless launched with `--t2selftest`**. When that arg is present, it drives the game
> from the main menu into the hosted scenario required by the SPEC with zero interaction,
> fires the element's effect, and logs the same `[T2MOD-SELFTEST]` effect marker the manual
> path used.
> `verify.md` then greps that marker — the effect is proven, not eyeballed.
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

The harness and element expose three signals so `verify.md`/`repair.md` can tell setup
failure from a real effect bug:

- `[T2MOD-SELFTEST] <ModName> selftest done` — reached the hosted scenario, drove the
  effect, and observed its result.
- `[T2MOD-SELFTEST] <ModName> selftest FAILED: <stage>: <reason>` — harness couldn't reach
  or drive the scenario (navigation/timeout). **This is a harness/setup problem, NOT an
  effect bug** —
  `verify.md` falls back to the manual guide and reports tier-1 only.
- the element's own type-specific `[T2MOD-SELFTEST]` effect marker (for example
  `played:`, `attacked:`, or `option chosen:` from author.md step 2) — this is the actual
  tier-2 proof; absent-after-`done` = effect didn't fire (real bug).

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

The element's own type-specific effect marker (author.md step 2) is what proves tier-2 — the
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

## State-consuming Counter interactions — test the amount domain

A `consumes` edge for a nonnegative Counter needs more than the normal happy path. The
driver must exercise zero stacks, fewer than N, and at least N in the same hosted scenario,
and reject any negative instance after every case. Drive the real source each time; do not
test a helper while bypassing the card/relic/potion that owns the consumption behavior.

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

private static void AssertNoNegativePower(Creature owner, string stage)
{
    var power = owner.GetPower<<PowerName>>();
    if (power is { Amount: < 0 })
        throw new InvalidOperationException(
            $"<PowerName> amount-domain violation after {stage}: {power.Amount}");
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
    if (owner.GetPower<<PowerName>>() is not null)
        throw new InvalidOperationException("zero-stack consume created <PowerName>");
    AssertNoNegativePower(owner, "zero-stack consume");
    MainFile.Logger.Info("[T2MOD-SELFTEST] <PowerName> consume boundary: zero ok");

    // Fewer than N (2 < 4): consume the available amount and remove at zero.
    await PowerCmd.Apply<<PowerName>>(new ThrowingPlayerChoiceContext(), owner,
        2m, owner, null);
    await PlayConsumerCard(player);
    if (owner.GetPower<<PowerName>>() is not null)
        throw new InvalidOperationException("fewer-than-N consume did not remove <PowerName>");
    AssertNoNegativePower(owner, "fewer-than-N consume");
    MainFile.Logger.Info("[T2MOD-SELFTEST] <PowerName> consume boundary: 2 -> 0 ok");

    // At least N (6 >= 4): consume exactly N and preserve the remainder.
    await PowerCmd.Apply<<PowerName>>(new ThrowingPlayerChoiceContext(), owner,
        6m, owner, null);
    await PlayConsumerCard(player);
    var remaining = owner.GetPower<<PowerName>>();
    if (remaining?.Amount != 2)
        throw new InvalidOperationException(
            $"normal consume expected 2 <PowerName>, got {remaining?.Amount.ToString() ?? "missing"}");
    AssertNoNegativePower(owner, "normal consume");
    MainFile.Logger.Info("[T2MOD-SELFTEST] <PowerName> consume boundary: 6 -> 2 ok");
}
```

Call `ExerciseConsumeBoundaries(player)` from the source's `InCombat` body instead of
playing the consumer only once. If N is 1, zero is also the only fewer-than-N integer case;
keep the zero case plus an at-least-N remainder case. The successful terminal marker still
comes only after all boundary assertions pass.

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

## The `MapNode` scenario (event / World Node — earned seam, live 2026-07-13)

An event is not proven by registration alone. The harness must enter its real `EventRoom`,
wait for the nested event UI, click an actual `NEventOptionButton`, and observe the option's
run-state consequence. Reuse the fixed menu-to-run navigation and `NRun.GlobalUi` timing
gate; replace the combat entry/driver with this body:

```csharp
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
MainFile.Logger.Info(
    $"[T2MOD-SELFTEST] <ModName> option observed: gold {before} -> {player.Gold} delta={player.Gold - before}");
```

Required namespaces beyond the fixed scaffold: the event type; `MegaCrit.Sts2.Core.Map`;
`MegaCrit.Sts2.Core.Nodes.Events`; `MegaCrit.Sts2.Core.Nodes.Rooms`; and
`MegaCrit.Sts2.Core.Rooms`. `System.Linq` is already used by the navigation code.

Select the button by the SPEC option's formatted title, not merely "the only unlocked
option"; multi-option events are valid and the scenario drives one specified consequence.
The event option method logs its own `option chosen:` marker **after** the Cmd changes run
state. The harness independently reads the same state and logs `option observed:`. Verify
with a pattern such as `"event entered|option chosen|option observed"`; the verifier still
requires the exact load marker and `selftest done`.

> **Live-proven (`CanaryEvent`, tier-2 PASS):** `GildedSignpost` entered through
> `EnterRoomDebug(..., ModelDb.Event<GildedSignpost>())`; formatted title and option loc
> resolved; `UiHelper.Click` selected `Follow the sign`; the event and harness independently
> observed gold `99 -> 124` (`delta=25`); the result page resolved; zero mod-named errors.
> The portrait is the provisional vanilla `This or That?` placeholder, not custom event art.

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
- [ ] Exactly one source driver is filled per SPEC (relic → `BeforeCombat`; card/potion → `InCombat`; monster+encounter → `CombatEnemy`; event → `MapNode` real room + option UI click); multi-element interactions reuse that real source driver and add observations.
- [ ] `<PREFIX>-<SLUG>` ids match the element's real `Id.Entry` (SPEC's derived ids).
- [ ] The element's own type-specific effect marker (author.md step 2) is present — the harness only *triggers*; the element logs the proof.
- [ ] Every nonnegative Counter `consumes` edge runs zero/fewer-than-N/at-least-N cases
      and asserts after each that no negative instance exists.
- [ ] Never claim tier-2 on a `selftest FAILED` line — that's a harness/setup miss, report tier-1 + manual fallback.
