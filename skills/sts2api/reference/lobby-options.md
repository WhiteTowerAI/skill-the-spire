# Reference: lobby options

A lobby option is a choice made on the Character select before the run starts, in
singleplayer and in a multiplayer lobby: a run rule the host picks for the whole party, or a
loadout each player picks for itself. RitsuLib's run saved data carries the choice: the lobby
accessor stages it, `SyncLobbyOnChange` sends each player's contribution to the others, and the
new run's save commits it, so every peer reads the same value for the rest of the run.

Read `reference/lifecycle-state-rng.md` for run saved data in general and
`recipes/runtime-ui.md` § Fixed node attachment for the control.

## SPEC fields

```markdown
- **lobby option**: <name>
  - scope: host rule (one value for the run) | per player (one value each)
  - value: <plain JSON type, its default, and its allowed values>
  - control: <the lobby control, its label in English and Simplified Chinese, and its position>
  - consumer: <which element reads the value in the run, and when>
```

## Registration

Register the slots once, early, inside a mod-data registration scope; keep each key stable after
release. The payload is a plain class with public, defaulted properties.

```csharp
using STS2RitsuLib;
using STS2RitsuLib.RunData;

public sealed class <Name>Rules { public int BonusGold { get; set; } }
public sealed class <Name>Pick { public string? Banner { get; set; } }

internal static class <Name>Lobby
{
    internal static RunSavedData<<Name>Rules> Rules { get; private set; } = null!;
    internal static PlayerRunSavedData<<Name>Pick> Pick { get; private set; } = null!;

    internal static void Register()   // call from MainFile.RegisterContent()
    {
        using (RitsuLibFramework.BeginModDataRegistration(MainFile.ModId))
        {
            var store = RitsuLibFramework.GetRunSavedDataStore(MainFile.ModId);
            Rules = store.Register("rules", () => new <Name>Rules(),
                new RunSavedDataOptions { SyncLobbyOnChange = true });
            Pick = store.RegisterPerPlayer("pick", () => new <Name>Pick(),
                new RunSavedDataOptions { SyncLobbyOnChange = true });
        }
    }
}
```

## Choosing

Put the choice in one static method; the control and the SelfTest both call it.

- **Host rule.** Only the host's lobby value is committed, so a client never writes it:

  ```csharp
  internal static void ChooseBonusGold(StartRunLobby lobby, int gold)
  {
      if (lobby.NetService.Type == NetGameType.Client)
          return;
      Rules.Lobby.Modify(lobby, rules => rules.BonusGold = gold);
  }
  ```

- **Per player.** Each player writes its own entry, keyed by its net id:

  ```csharp
  internal static void ChooseBanner(StartRunLobby lobby, string banner)
      => Pick.Lobby.Modify(lobby, lobby.NetService.NetId, pick => pick.Banner = banner);
  ```

The control is a Godot node attached to `NCharacterSelectScreen` (the same screen hosts the
singleplayer and the multiplayer lobby) through the fixed node-attachment route, reading the
screen's public `Lobby` when the player uses it:

```csharp
ModNodeAttachmentRegistry.For(MainFile.ModId)
    .RegisterReadyChild<NCharacterSelectScreen, <Name>RulesToggle>(
        "rules_toggle", _ => new <Name>RulesToggle(), (screen, toggle) => toggle.Bind(screen),
        new NodeAttachmentOptions
        {
            Name = "<ModName>RulesToggle",
            DuplicatePolicy = NodeAttachmentDuplicatePolicy.ReuseExistingByName,
            SetupTiming = NodeAttachmentSetupTiming.AfterAdd,
        });

public sealed partial class <Name>RulesToggle : CheckButton
{
    private NCharacterSelectScreen? _screen;

    public void Bind(NCharacterSelectScreen screen)
    {
        _screen = screen;
        Text = <localized label>;
        Toggled += on => { if (_screen?.Lobby is { } lobby) <Name>Lobby.ChooseBonusGold(lobby, on ? 25 : 0); };
    }
}
```

A host-rule control on a client may stay visible but changes nothing; hide it when
`lobby.NetService.Type == NetGameType.Client` if SPEC says so.

## Reading

In the run, read the committed value from the run state on every peer:
`Rules.TryGet(runState, out var rules)` and `Pick.TryGet(runState, player.NetId, out var pick)`.
A missing value means the player never chose: use the payload's defaults. Never read the lobby
accessor after the run began, and never write a lobby value from a run hook.

## Verification

`plan.Lobby(lobby => ...)` in `SelfTestScenarios.cs` calls the choice methods on every peer just
before the player readies; a `plan.RunStart` scenario then asserts the committed values on
`t.Run` (the host rule, and every player's own entry). Both the singleplayer and the multiplayer
Tier 2 run it. The control itself (its label, position, and click) is headed review.

```csharp
plan.Lobby(lobby =>
{
    <Name>Lobby.ChooseBonusGold(lobby, 25);
    <Name>Lobby.ChooseBanner(lobby, lobby.NetService.Type == NetGameType.Client ? "client" : "host");
    return Task.CompletedTask;
});

plan.RunStart("lobby_choices_reach_the_run", t =>
{
    bool found = <Name>Lobby.Rules.TryGet(t.Run, out var rules);
    t.Proof(found && rules.BonusGold == 25, $"host rule expected=25 observed={(found ? rules.BonusGold : -1)}");
    foreach (var player in t.Run.Players)
    {
        var expected = player == t.Player ? "host" : "client";
        bool own = <Name>Lobby.Pick.TryGet(t.Run, player.NetId, out var pick);
        t.Proof(own && pick.Banner == expected, $"P{player.NetId} pick expected={expected} observed={(own ? pick.Banner : "absent")}");
    }
    return Task.CompletedTask;
});
```

## Limits

A lobby option is chosen before the run and fixed after it begins. Changing a run rule mid-run,
a Settings page, a lobby layout change beyond one attached control, and per-player values the
host overrides are not part of this route.
