using System.Text.Json;
using Godot;
using MegaCrit.Sts2.Core.Entities.Multiplayer;
using MegaCrit.Sts2.Core.Nodes.CommonUi;
using MegaCrit.Sts2.Core.Nodes.Screens.Capstones;
using MegaCrit.Sts2.Core.Nodes.Screens.ScreenContext;
using STS2RitsuLib.RuntimeInput;
using STS2RitsuLib.Scaffolding.Content;
using STS2RitsuLib.Scaffolding.Godot.NodeAttachments;
using STS2RitsuLib.Screens;
using STS2RitsuLib.Search;
using STS2RitsuLib.TopBar;
using STS2RitsuLib.Ui.Catalog;
using STS2RitsuLib.Ui.Shell.Theme;
using STS2RitsuLib.Ui.Toast;
using STS2RitsuLib.Ui.Windows;

namespace M88CompileProbes;

internal static class RuntimeUiProbe
{
    private const string ModId = "M88_RUNTIME_UI_PROBE";

    internal static void Register()
    {
        ModContentPackBuilder.For(ModId)
            .TopBarButtonOwned("catalog", new ModTopBarButtonSpec
            {
                IconPath = "res://M88RuntimeUiProbe/images/catalog.png",
                Order = 10,
                OnClick = context => context.ToggleCapstoneScreen(new ProbeCapstoneScreen()),
                VisibleWhen = context => context.Player != null,
                IsOpenWhen = _ => ModScreenService.IsCapstoneOpen,
                CountProvider = context => context.Player is null ? -1 : 1,
            })
            .Apply();

        var tracked = RitsuToastService.ShowTracked(
            RitsuToastRequest.Info("Loading", "Probe").Persistent().WithProgress(0f));
        tracked.UpdateBody("Ready");
        tracked.ResetDuration(1d);
        tracked.Close();

        IRuntimeHotkeyHandle hotkey = RuntimeHotkeyService.Register(
            "Ctrl+Shift+M",
            static () => { },
            new RuntimeHotkeyOptions
            {
                Id = "m88.runtime_ui.toggle",
                DisplayName = RuntimeHotkeyText.Literal("Toggle probe"),
                Description = RuntimeHotkeyText.Literal("Open or close the probe screen"),
                Purpose = "open_runtime_ui",
                Category = RuntimeHotkeyText.Literal("Probe"),
                ExposeToSteamInput = true,
                MarkInputHandled = true,
            });
        hotkey.Dispose();

        using JsonDocument tokens = JsonDocument.Parse(
            """{"mods":{"m88_runtime_ui_probe":{"accent":{"$type":"color","$value":"#33aa88"}}}}""");
        RitsuShellThemeRuntime.RegisterModTokens(ModId, tokens.RootElement,
            static theme => _ = theme.GetColor("mods.m88_runtime_ui_probe.accent"));

        using RitsuSearchExpansionRegistration search =
            RitsuSearchExpansionRegistry.Register(ModId, new ProbeSearchProvider());
        search.Invalidate();

        ModNodeAttachmentRegistry.For(ModId)
            .RegisterReadyChild<NTopBar, ProbeRuntimeUiCoordinator>(
                "runtime_ui",
                static _ => new ProbeRuntimeUiCoordinator(),
                static (_, child) => child.BuildUi(),
                new NodeAttachmentOptions
                {
                    Name = "M88RuntimeUiProbe",
                    Order = 10,
                    IncludeDerivedParentTypes = true,
                    DuplicatePolicy = NodeAttachmentDuplicatePolicy.ReuseExistingByName,
                    SetupTiming = NodeAttachmentSetupTiming.AfterAdd,
                });
    }
}

public sealed partial class ProbeRuntimeUiCoordinator : Control
{
    internal void BuildUi()
    {
        var filters = new[]
        {
            new RitsuCatalogFilter("kind", "Kind", "All",
            [
                new RitsuCatalogFilterOption("known", "Known", static item => item.Id == "entry"),
            ]),
        };
        var browser = new RitsuCatalogBrowser(new RitsuCatalogBrowserOptions
        {
            Presentation = RitsuCatalogPresentation.Grid,
            DetailPresentation = RitsuCatalogDetailPresentation.Drawer,
            SearchPlaceholder = "Search",
            EmptyText = "No entries",
            DetailPlaceholderText = "Select one",
            DetailUnavailableText = "No details",
            DetailFactory = static item => new Label { Text = item.Title },
        }, filters);
        browser.SetItems([new RitsuCatalogItem("entry", "Entry", "Subtitle", "alternate")]);
        browser.SelectItem("entry");
        browser.Refresh();

        var window = new RitsuFloatingWindow(new RitsuFloatingWindowOptions
        {
            Title = "Probe",
            InitialSize = new Vector2(900f, 640f),
            MinimumSize = new Vector2(480f, 320f),
            Movable = true,
            Resizable = true,
            Closable = true,
            ConstrainToViewport = true,
        });
        _ = window.SetContent(browser);
        AddChild(window);
        _ = window.CaptureGeometry();
        window.Close();
    }
}

public sealed partial class ProbeCapstoneScreen : Control, ICapstoneScreen, IScreenContext
{
    public NetScreenType ScreenType => NetScreenType.None;
    public bool UseSharedBackstop => true;
    public Control? DefaultFocusedControl => null;

    public void AfterCapstoneOpened() { }
    public void AfterCapstoneClosed() { }
}

internal sealed class ProbeSearchProvider : IRitsuSearchExpansionProvider
{
    public string Id => "m88.runtime_ui.local_names";
    public string DisplayName => "Probe local names";
    public bool EnabledByDefault => true;

    public IReadOnlyList<RitsuSearchExpansion> Expand(string text, RitsuSearchExpansionContext context) =>
        context.LanguageCode == "zhs" && text.Length > 0
            ? [new RitsuSearchExpansion(text.ToLowerInvariant(), RitsuSearchExpansionKind.Transliteration)]
            : [];
}
