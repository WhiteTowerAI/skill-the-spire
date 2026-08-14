# Recipe: Runtime UI

Use this recipe for one local Mod-owned UI workflow. Select only the pieces named by SPEC, but every
public piece below is authorable. Keep registration and callbacks in a coordinator with explicit
cleanup; do not scatter static handles across generated content classes.

## Top bar and Toasts

Register the top-bar entry before `NTopBar._Ready`. `OnClick` is required. The local `Player` can be
`null`, and visibility/open/count providers run every frame, so they must be fast, pure, and safe
outside a run.

```csharp
ModContentPackBuilder.For(MainFile.ModId)
    .TopBarButtonOwned("codex", new ModTopBarButtonSpec
    {
        IconPath = "res://<ModName>/images/ui/codex.png",
        Order = 20,
        OnClick = context => RuntimeUi.Toggle(context),
        VisibleWhen = context => RuntimeUi.IsAvailable(context.Player),
        IsOpenWhen = _ => ReferenceEquals(ModScreenService.CurrentCapstoneScreen, RuntimeUi.Screen),
        CountProvider = context => context.Player is null ? -1 : RuntimeUi.Count(context.Player),
    })
    .Apply();
```

The qualified ID is `ModContentRegistry.GetQualifiedTopBarButtonId(modId, localStem)`. Ship matching
`static_hover_tips` `.title` and `.description` keys in `eng` and `zhs`. A missing icon uses the
framework's deck-icon fallback, but a requested custom icon still needs Build and headed proof.

Use `RitsuToastService.ShowInfo/ShowWarning/ShowError` for one-shot feedback. Use a tracked handle
when later code updates progress or closes the same Toast:

```csharp
RitsuToastHandle toast = RitsuToastService.ShowTracked(
    RitsuToastRequest.Info("Loading...", "<ModName>")
        .Persistent()
        .WithProgress(0f));
toast.Update(RitsuToastRequest.Info("Ready", "<ModName>").WithProgress(1f));
toast.ResetDuration(2d);
toast.Close();
```

Declare level, duration/persistence, optional live image, click/dismiss behavior, progress, update,
and terminal close in SPEC. Queued pre-host Toasts are supported; do not treat queuing as visible
proof. Close every persistent/owned tracked Toast on cancellation and owner cleanup.

## Runtime hotkey

The pinned signature takes `RuntimeHotkeyOptions`; the old guide's direct `id:` and `title:` named
arguments do not compile against `0.5.11`.

```csharp
IRuntimeHotkeyHandle handle = RuntimeHotkeyService.Register(
    RuntimeHotkeyService.ActionBinding("<mod_action>"),
    RuntimeUi.Toggle,
    new RuntimeHotkeyOptions
    {
        Id = "<modid>.toggle_codex",
        DisplayName = RuntimeHotkeyText.Dynamic(() => RuntimeUiText.ToggleName),
        Description = RuntimeHotkeyText.Dynamic(() => RuntimeUiText.ToggleDescription),
        Purpose = "open_runtime_ui",
        Category = "<ModName>",
        ExposeToSteamInput = true,
        MarkInputHandled = true,
        SuppressWhenTextInputFocused = true,
        SuppressWhenDevConsoleVisible = true,
    });
```

A hotkey may use one or several parsed binding strings. Retain its `IRuntimeHotkeyHandle` for
`TryRebind`, registration inspection, `Unregister`, and `Dispose`. `ExposeToSteamInput` only exposes
the selected local action; it is not a Settings binding or Multiplayer route.

## Local capstone screen

A custom capstone is a Godot `Node` implementing every `ICapstoneScreen` and `IScreenContext`
member. Only one capstone can be current; opening a different one replaces/destroys the previous
screen through the native host. Use `ModScreenService.Open`, `Toggle`, and `Close`, or the matching
top-bar context helpers.

```csharp
public sealed partial class ModCodexScreen : Control, ICapstoneScreen
{
    public NetScreenType ScreenType => NetScreenType.None;
    public bool UseSharedBackstop => true;
    public Control? DefaultFocusedControl => _firstItem;
    private Control? _firstItem;

    public void AfterCapstoneOpened() { }
    public void AfterCapstoneClosed() { }
}
```

`NetScreenType.None` is the required local-only value. Do not select another player's screen type,
publish remote state, or add Multiplayer behavior. Close/toggle through the service rather than
manually reparenting the screen.

## Catalog and floating window

Build Catalog filters before the browser enters the scene tree. Items may change later. IDs are
ordinal-unique and stable; there are at most 16,384 items and the search field accepts at most 512
characters. Keep filter predicates, lazy icon factories, detail factories, and quick actions fast,
main-thread safe, and free of hidden state mutation except the explicit action.

```csharp
var filters = new[]
{
    new RitsuCatalogFilter("kind", RuntimeUiText.Kind, RuntimeUiText.All,
    [
        new RitsuCatalogFilterOption("known", RuntimeUiText.Known,
            item => RuntimeUi.IsKnown(item.Id)),
    ]),
};
var browser = new RitsuCatalogBrowser(new RitsuCatalogBrowserOptions
{
    Presentation = RitsuCatalogPresentation.Grid,
    DetailPresentation = RitsuCatalogDetailPresentation.Drawer,
    SearchPlaceholder = RuntimeUiText.Search,
    EmptyText = RuntimeUiText.Empty,
    DetailPlaceholderText = RuntimeUiText.SelectOne,
    DetailUnavailableText = RuntimeUiText.Unavailable,
    DetailFactory = item => RuntimeUi.CreateDetail(item),
}, filters);
browser.SetItems(RuntimeUi.BuildItems());
```

Each `RitsuCatalogItem` can supply title/subtitle/search text, a live icon or side-effect-free lazy
factory, a short row label, tooltip, accent, and one explicit icon quick action. The browser owns
and frees detail controls returned by `DetailFactory`; it does not own item/action textures.

Embed the browser or another unattached `Control` in a main-thread `RitsuFloatingWindow`:

```csharp
var window = new RitsuFloatingWindow(new RitsuFloatingWindowOptions
{
    Title = RuntimeUiText.Title,
    InitialSize = new Vector2(900f, 640f),
    MinimumSize = new Vector2(480f, 320f),
    Movable = true,
    Resizable = true,
    Closable = true,
    ConstrainToViewport = true,
});
Control? previous = window.SetContent(browser);
```

`SetContent` detaches but does not free the previous control; `TakeContent` does the same for the
current one. The owner must explicitly reuse or free detached controls. Configure only before the
window enters the tree; apply saved finite positive geometry only after it enters the tree. Close
hides and emits `Closed`; define whether the coordinator reuses or frees the window.

## Search expansion

Register a provider only when the Mod owns a real alternate-reading need. It can be called
concurrently and must be deterministic, thread-safe, non-blocking, and perform no file/network I/O
in metadata getters or `Expand`.

```csharp
sealed class ModSearchProvider : IRitsuSearchExpansionProvider
{
    public string Id => "<modid>.local_names";
    public string DisplayName => RuntimeUiText.SearchProvider;
    public bool EnabledByDefault => true;

    public IReadOnlyList<RitsuSearchExpansion> Expand(
        string text, RitsuSearchExpansionContext context) =>
        context.LanguageCode == "zhs"
            ? RuntimeUiSearch.ExpandLocal(text)
            : [];
}

RitsuSearchExpansionRegistration registration =
    RitsuSearchExpansionRegistry.Register(MainFile.ModId, new ModSearchProvider());
```

Return at most 64 useful unique expansions, 8,192 total expansion characters, and 512 characters
per item; use `Transliteration`, `AlternateReading`, or `Initialism`. Acquire changed local data
before `Invalidate()`. Dispose the registration before its provider owner unloads; a callback
already captured by another thread may finish after disposal. The framework may show provider
metadata in its own settings, but open-mod does not generate a Settings route or binding.

## Fixed node attachment and shell tokens

Use `ModNodeAttachmentRegistry.For(modId).RegisterReadyChild...` only for a SPEC-named stable public
Godot host. Declare exact parent/child types, duplicate policy, setup timing, order/insertion, and
cleanup. Prefer a factory or direct scene; use converted-scene registration only when its documented
conversion is actually required.

```csharp
ModNodeAttachmentRegistry.For(MainFile.ModId)
    .RegisterReadyChild<NTopBar, RuntimeUiCoordinator>(
        "runtime_ui",
        _ => new RuntimeUiCoordinator(),
        (parent, child) => child.Bind(parent),
        new NodeAttachmentOptions
        {
            Name = "<ModName>RuntimeUi",
            Order = 20,
            IncludeDerivedParentTypes = true,
            DuplicatePolicy = NodeAttachmentDuplicatePolicy.ReuseExistingByName,
            SetupTiming = NodeAttachmentSetupTiming.AfterAdd,
        });
```

Lookup through `TryGetAttached`; do not create a second node on a miss. The attachment follows the
parent tree lifetime, so its `_ExitTree` must close owned UI and dispose hotkey/search handles.

When coherent Mod-local styling is selected, parse a fixed Design Tokens Format Module object and
register only a Mod-namespaced branch such as `mods.<modid>` through
`RitsuShellThemeRuntime.RegisterModTokens`. Read it from `RitsuShellTheme.Current` or the `OnApply`
snapshot and update only this Mod's live controls. Unregister on owner unload. Never call
`ApplyThemeId` or use the token callback to restyle unrelated controls.

## SelfTest

Follow `surfaces/runtime-ui.md`. Drive the real top bar, input router, capstone/window, Catalog,
Toast host, and stable attachment; assert structured state separately from headed visual/controller
review. No WP5 route is game-observed from compile or direct construction alone.
