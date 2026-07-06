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
        TaskHelper.RunSafely(RunAsync());   // fire-and-forget; never blocks Initialize
    }

    private static async Task RunAsync()
    {
        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(180));
        var ct = cts.Token;
        try
        {
            await WaitHelper.Until(() => NGame.Instance != null, ct, TimeSpan.FromSeconds(30), "no NGame");
            // Kill FTUE popups / speed things up so nav isn't blocked.
            SaveManager.Instance.SetFtuesEnabled(false);

            await NavigateToRunAsync(ct);
            await WaitHelper.Until(() => RunManager.Instance.IsInProgress, ct, TimeSpan.FromSeconds(30), "run not in progress");

            // RELIC ONLY: grant before combat so AfterSideTurnStart fires at TurnNumber 1.
            await BeforeCombat(ct);

            var encounter = ModelDb.Encounter<CorpseSlugsWeak>().ToMutable();   // minimal 2-slug fight
            await RunManager.Instance.EnterRoomDebug(RoomType.Monster, MegaCrit.Sts2.Core.Map.MapPointType.Unassigned, encounter);
            await WaitHelper.Until(() => CombatManager.Instance.IsInProgress, ct, TimeSpan.FromSeconds(30), "combat not started");

            var player = LocalContext.GetMe(RunManager.Instance.DebugOnlyGetState());
            var me = player.Creature;
            // Survivability so a slug can't kill us mid-test (AutoSlay does the same).
            await PowerCmd.Apply<PlatingPower>(new ThrowingPlayerChoiceContext(), me, 999m, me, null);

            // Wait until we're actually allowed to act.
            await WaitHelper.Until(
                () => player.PlayerCombatState?.Phase == PlayerTurnPhase.Play || !CombatManager.Instance.IsInProgress,
                ct, TimeSpan.FromSeconds(30), "play phase not reached");

            await InCombat(player, ct);

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
            var modal = (Node)NModalContainer.Instance.OpenModal;
            await UiHelper.Click(modal.GetNode<NButton>("VerticalPopup/YesButton"));
            await WaitHelper.Until(() => NModalContainer.Instance.OpenModal == null, ct, TimeSpan.FromSeconds(10), "abandon modal stuck");
        }

        await UiHelper.Click(mainMenu.GetNode<NButton>("MainMenuTextButtons/SingleplayerButton"));

        // Either the submenu ("Standard") or the character screen shows next.
        Control charSelect = null;
        NButton standard = null;
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

        var buttonContainer = charSelect.GetNode("CharSelectButtons/ButtonContainer");
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
    var card  = CombatManager.Instance.DebugOnlyGetState().CreateCard(model, player);
    await CardPileCmd.Add(card, PileType.Hand);
    Creature target = card.TargetType == TargetType.AnyEnemy
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
    var cs = player.Creature.CombatState;
    Creature target = potion.TargetType switch
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

### combo / multi-element — walk SPEC's interaction block in dependency order

The whole point of the interaction check: drive the **source** element, then assert the
**dependent** element's *own* marker fired. Each link asserts itself, so a broken link is
localized. Drive the source exactly as its element type above (a card that applies a
custom power → the `card` body); the dependent power's `AfterSideTurnStart`/apply hook
logs its own `fired:` marker. Add one line per SPEC interaction pair, source first:

```csharp
private static async Task InCombat(Player player, CancellationToken ct)
{
    // Link 1 (source): play the card that applies the custom power (as `card` above).
    await PlayerCmd.GainEnergy(3m, player);
    var model = ModelDb.AllCards.First(c => c.Id.Entry == "<CARD_PREFIX>-<CARD_SLUG>");
    var card  = CombatManager.Instance.DebugOnlyGetState().CreateCard(model, player);
    await CardPileCmd.Add(card, PileType.Hand);
    var target = card.CombatState?.HittableEnemies.FirstOrDefault();
    await CardCmd.AutoPlay(new BlockingPlayerChoiceContext(), card, target);
    // Link 2 (dependent): the applied power logs its OWN [T2MOD-SELFTEST] <Power> fired:
    // marker from its hook — give the turn a moment / end turn if it fires start-of-turn.
    await Task.Delay(500, ct);
    // If the dependent fires at the NEXT turn start, end the turn to trigger it:
    // if (player.PlayerCombatState?.Phase == PlayerTurnPhase.Play) PlayerCmd.EndTurn(player, canBackOut: false);
}
```

`verify.md` greps for **both** markers (`-Tier2Pattern "fired|used|selftest done"`); a
missing dependent marker after `selftest done` = the interaction link is broken (the exact
place raw-AI multi-element mods fail).

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
- [ ] Exactly one of `BeforeCombat`/`InCombat` filled per SPEC element (relic → BeforeCombat; card/potion/combo → InCombat).
- [ ] `<PREFIX>-<SLUG>` ids match the element's real `Id.Entry` (SPEC's derived ids).
- [ ] The element's own `fired/used` marker (author.md step 2) is present — the harness only *triggers*; the element logs the proof.
- [ ] Never claim tier-2 on a `selftest FAILED` line — that's a harness/setup miss, report tier-1 + manual fallback.
