# Recipe: Rest Site

Use for an independently requested native Rest Site action. This recipe chooses the truthful
owner; `reference/rest-site-options.md` owns the option implementation and host lifecycle.

## Owner selection

- standalone action: one Run `HookedSingletonModel`, registered through `.Singleton<T>()`;
- Card action: the exact single mutable Card instance in the owner's deck;
- Relic action: the exact owned Relic instance; or
- Modifier action: the selected mutable instance already in `RunState.Modifiers`.

Each owner overrides `TryModifyRestSiteOptions` and, only for keep-remaining behavior,
`ShouldDisableRemainingRestSiteOptions`. The option extends `ModRestSiteOptionTemplate` and is not
registered separately. Do not declare these as raw Hook lines; the shared reference owns their
bounded transaction and UI lifecycle.

Standalone registration is:

```csharp
RitsuLibFramework.CreateContentPack(ModId)
    .Singleton<RestSite.<OptionOwner>>()
    .Apply();
```

```csharp
public sealed class <OptionOwner> : HookedSingletonModel
{
    private static readonly AttachedState<Player, bool> KeepRemainingOnce = new();

    public <OptionOwner>() : base(HookType.Run) { }

    // Contribute <Option> from TryModifyRestSiteOptions.
    // Store/consume the one-shot keep signal on the concrete Player, never on this singleton.
}
```

Modifier ownership uses the same option flow but no singleton: the run listener set already walks
the selected Modifier. Persistent once-per-run state belongs to that Modifier's saved model state
or a declared run/player saved slot; transient per-visit signaling uses attached state.

## Boundary and proof

Read and follow `reference/rest-site-options.md` completely: singleplayer, free/fixed Gold,
eligibility versus affordability, duplicate ID rejection, stale-button final recheck, every
failure check before mutation, deterministic no-cancel outcome, once-per-site/run, leave or keep
other options, localization, custom/native fallback icon, and the exact real Rest Site matrix.
