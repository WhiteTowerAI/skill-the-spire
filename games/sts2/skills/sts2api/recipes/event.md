# Recipe: Custom Event (World Node)

> A grounded pattern for a normal map event in STS2. The playable unit is the event
> room plus at least one consequential option: register it, enter it through the
> `MapNode` scenario, click a real option, and observe the resulting run-state change.

This recipe creates a new Mod-owned Event. When the request instead changes an exact
existing vanilla Ancient's initial options or subsequent pages, resolve it through
`reference/vanilla-overrides.md` and use `reference/vanilla-ancient-overrides.md`; do not
subclass/register a second Ancient or copy this new-content lifecycle over the native one.
For a fresh unlock gate on an exact ordinary vanilla Event or shared `EVENT.DARV`, use
`reference/vanilla-availability-overrides.md`. That route requires one pinned epoch and
singleplayer scope; act-owned Ancients and permanent Event disable remain outside the availability routes.

For the full option-result vocabulary (blocking card selections, custom rewards,
conditional pages, and resumable/terminal special combat), also read
`reference/event-outcomes.md`. When SPEC selects the bounded normal-layout
`portrait_halo` profile, read `reference/event-vfx.md`. When page or option descriptions
use styled/animated vanilla text, read `reference/event-text-effects.md`. When enabled
options use typed Hover Tips, relic-backed presentation, or exact HP/Max HP warnings, read
  `reference/event-option-presentation.md`. When custom Quest Cards declare a finite
  prioritized mapping or sequence that can force this Event in selected acts, read
  `reference/forced-followup-event.md`. When an option selects
native Card/relic acquisition presentation, the bounded one-shot screen shake, or the
curated built-in `trial_noble` VFX, read `reference/event-native-presentation.md`.

## Registration (one content-pack route)

Subclass `STS2RitsuLib.Scaffolding.Content.ModEventTemplate`. Register it exactly once
through `.SharedEvent<T>()` for all-act placement or `.ActEvent<TAct,T>()` for an explicit
act. Do **not** add `[Pool]`, instantiate the canonical model, call `AddEvent`, or create a
second content pack for the same Event.

`EventModel.IsShared` is the game's room/resume semantic and is separate from the content
pack's shared-across-act registration. Override `IsAllowed(IRunState)` for run-state
eligibility. Events that enter special combat still set `IsShared => true` as required by
the public room lifecycle.

The test scenario uses the default all-act placement. It enters the event directly by
canonical model, so map RNG cannot make the proof flaky.

The bounded forced-follow-up exception deliberately overrides natural placement: its
target returns false from `IsAllowed`, and the carried Quest Card replaces both an Unknown
room roll and the following Event pull. Follow `reference/forced-followup-event.md`; do not
combine that target with ordinary pool placement.

## Known-good skeleton

```csharp
// <ModName>Code/Events/<Name>.cs
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Godot;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.Nodes.Rooms;
using MegaCrit.Sts2.Core.Runs;
using STS2RitsuLib.Scaffolding.Content;

namespace <ModName>.Events;

public sealed class <Name> : ModEventTemplate
{
    public const string FallbackPortraitPath = "res://images/events/this_or_that.png";
    public static string ModPortraitPath =>
        $"{MainFile.ResPath}/images/events/<slug>.png";

    private string DefaultInitialPortraitPath =>
        $"res://images/events/{Id.Entry.ToLowerInvariant()}.png";

    public override EventAssetProfile AssetProfile => new(
        InitialPortraitPath: ResourceLoader.Exists(ModPortraitPath)
            ? ModPortraitPath
            : FallbackPortraitPath);

    public override IEnumerable<string> GetAssetPaths(IRunState runState) =>
        base.GetAssetPaths(runState)
            .Where(path => path != DefaultInitialPortraitPath);

    protected override IReadOnlyList<EventOption> GenerateInitialOptions()
        => new[]
        {
            new EventOption(this, <OptionMethod>, InitialOptionKey("<OPTION_KEY>")),
        };

    private async Task <OptionMethod>()
    {
        var owner = Owner ?? throw new InvalidOperationException("Event has no owner");
        var before = owner.Gold;
        await PlayerCmd.GainGold(<amount>m, owner);
        var after = owner.Gold;

        MainFile.Logger.Info(
            $"[T2MOD-SELFTEST] <ModName> option chosen: gold {before} -> {after} delta={after - before}");
        SetEventFinished(PageDescription("<RESULT_PAGE_KEY>"));
    }
}
```

Register the class in the existing content pack:

```csharp
RitsuLibFramework.CreateContentPack(ModId)
    .SharedEvent<<Name>>()
    .Apply();
```

## Nested localization (`events.json`)

Normal Event localization is a flat JSON table whose keys describe the nested page/option
shape. RitsuLib's normalized entry is `<MOD>_EVENT_<TYPE>`:

```text
<ID>.title
<ID>.pages.INITIAL.description
<ID>.pages.INITIAL.options.<OPTION_KEY>.title
<ID>.pages.INITIAL.options.<OPTION_KEY>.description
<ID>.pages.<RESULT_PAGE_KEY>.description
```

`InitialOptionKey("FOLLOW_THE_SIGN")` and
`ModOptionKey("PAGE", "OPTION")` build the exact namespaced key consumed by
`EventOption`. `PageDescription("PAGE")` resolves the matching description. Keep the
explicit upper-snake option name identical to the JSON segment; method names do not mint
localization keys automatically.

### Bounded rich text

Normal Event page descriptions and option descriptions are rendered by the game's existing
`MegaRichTextLabel`. They may use the vanilla-observed bounded tags from
`reference/event-text-effects.md`: `b`; `aqua`, `blue`, `gold`, `green`, `orange`,
`purple`, `red`; and the short motion tags `jitter` and `sine`.

Keep titles plain, balance/nest every tag, and do not emit arbitrary BBCode or parameters.
This path needs no C# helper or cleanup code; page changes replace the host label's text.

Ship `events.json` in the resource PCK; a DLL-only rebuild does not update it.

## Optional lifecycle, state, and RNG route

For lifecycle observation beyond the normal option callback, state owned outside the mutable Event
model, included persistence, or gameplay-random choice, read `reference/lifecycle-state-rng.md`.
Use the host-supplied RNG when available and otherwise one stable Mod stream at the authoritative
resolution point. The reference owns subscription disposal, state/save/profile rules, migrations,
neutral rejected/preview behavior, and hosted proof. It does not authorize Progression, Settings,
Telemetry, or Multiplayer behavior.

## Options and state transitions

- `GenerateInitialOptions()` returns the options shown on the initial page.
- `new EventOption(this, Method, InitialOptionKey(key))` creates an initial enabled option.
- Use `ModOptionKey(page, key)` on later pages. Passing `null` as the callback creates a
  locked option while retaining its typed data.
- `SetEventFinished(PageDescription(key))` shows the result text and replaces choices with
  the standard Proceed button.
- `SetEventState(description, options)` is the vanilla pattern for a multi-page event that
  presents another choice instead of finishing.

### Native option presentation

Enabled normal-Event options may pass typed Card/relic/potion/power tips through the
`EventOption` constructor. Construct only the selected types with the grounded
`HoverTipFactory` helpers in `reference/event-option-presentation.md`; the real option
button owns focus, display, and cleanup. A null-callback option retains its tip data but the native
button deliberately does not display it, so never promise locked-option tooltips or emit a
custom workaround.

Use `CreateModRelicOption<T>` when SPEC selects relic-backed presentation. It provides the normal
relic title, description, and metadata. The actual obtain effect remains a separate awaited
`RelicCmd.Obtain<T>` consequence. Normal-layout Event buttons do not render the relic image:
that consumer is gated to `AncientEventModel`, so preserve a requested normal-layout image
as a presentation gap rather than opening an Ancient layout.

For a choice whose consequence pays HP or Max HP, attach the exact cost when generating
the option:

```csharp
new EventOption(this, PayHp, ModOptionKey("PAGE", "PAY_HP"))
    .ThatDoesDamage(damage);
new EventOption(this, PayMaxHp, ModOptionKey("PAGE", "PAY_MAX_HP"))
    .ThatDecreasesMaxHp(maxHpLoss);
```

The later Cmd still owns payment. These helpers only drive the native warning and use
inclusive lethal boundaries: `CurrentHp <= damage` and `MaxHp <= maxHpLoss`. The value
must exactly match the decimal cost resolved for the Cmd; do not round, estimate, or use
red localization text as a substitute.

### Native acquisition and adjacent presentation

When a known Card is added to the deck, pass the exact awaited `CardPileCmd.Add` result to
`CardCmd.PreviewCardPileAdd`; do not grant or preview a second Card. A relic acquisition
uses exactly one awaited `RelicCmd.Obtain<T>` call, which already owns the inventory
animation. A named option may additionally select one preference-respecting allowlisted
`weak_short` or `strong_normal` screen shake. See `reference/event-native-presentation.md` for exact ordering,
allowed values, and the combined headed proof.

`Owner` is null on the canonical model and non-null only after the mutable event enters a
run. Read it inside option methods / lifecycle hooks, never from the canonical instance.
Use `reference/effect-primitives.md` for ordinary consequences and do not mutate run fields
directly. `reference/event-outcomes.md` continues to own selection/reward/special-combat
transactions and Event-specific presentation around those primitives.

This fast-path recipe shows one immediate effect. `reference/event-outcomes.md` is the
authoritative contract for composed effects, selection/reward overlays, locked options,
special-combat entry, `Resume`, optional combat rewards, and the one-combat-per-Event-
instance boundary. It also records that merchant/rest/treasure room transitions remain
unsupported.

## Art contract: normal and later-page portraits

Normal/default-layout event portraits are implemented as loose opaque PNGs, each
exactly **3440×1613**. The initial slot is
`res://<ModName>/images/events/<event-slug>.png`; an authored page slot uses
`res://<ModName>/images/events/<event-slug>_<page-key-lower>.png`. Generate/import each
selected slot with `gen_sprite.py --spec event`; every art or localization change requires
a `.pck` rebuild. The concrete Event uses `EventAssetProfile.InitialPortraitPath` and
filters the missing convention-derived path from `GetAssetPaths` as shown above.

Placeholder remains the silent default: when the mod PNG is absent, return the verified
`res://images/events/this_or_that.png`. Do not return the missing custom path or rely on the
game to recover from its load error.

Proof for a custom portrait asserts that the displayed `%Portrait.Texture.ResourcePath` is the
Mod path at logical size 3440×1613, with a headed screenshot of the option UI over it. A
later-page switch asserts the replacement path and size the same way, plus removal of any
initial-page VFX. Use this bounded page-switch pattern:

The same date's acquisition acceptance submitted one approved `seedream-5.0-lite`
`21:9`/`2K` request with three randomly selected Event references. Its inspected wide
source normalized to 3440×1613, packed into the test Mod, rendered behind the real option
UI, and passed the same strict proof with no fresh error. This closes the reference-prompt
path for normal Event portraits; it does not extend the deferred scene/VFX surfaces.

```csharp
public static string ResultPortraitPath =>
    $"{MainFile.ResPath}/images/events/<event-slug>_<page-key-lower>.png";

private void ShowResultPortraitIfPresent()
{
    if (!LocalContext.IsMe(Owner) || !ResourceLoader.Exists(ResultPortraitPath))
        return;

    var room = NEventRoom.Instance;
    room?.Layout?.RemoveNodesOnPortrait();
    room?.SetPortrait(ResourceLoader.Load<Texture2D>(ResultPortraitPath));
}
```

Call it from the option method immediately before `SetEventState` or
`SetEventFinished`. If the PNG is absent, do nothing and retain the current portrait.
This does not cover a separate `_phobia_mode.png`, custom layouts, or Ancient background
scenes. Prompt composition and acquisition rules are in `reference/art-contract.md`;
event art keeps its focal subject left and UI space on the right, unlike a centered card
portrait.

### Bounded VFX profiles

Normal/default-layout Events may select the implemented `portrait_halo` profile in
`reference/event-vfx.md`. It uses public code-native Godot nodes through `OnRoomEnter` and
`NEventLayout.AddVfxAnchoredToPortrait`; it does not use an image backend or a `.pck` VFX
scene. The headed acceptance proved initial, later-page, combat cleanup, and resumed-page
presentation with Fast Mode handling and no fresh error.

The separately grounded built-in `trial_noble` profile is also supported through
`reference/event-native-presentation.md`. It preloads the exact vanilla Trial scene,
instantiates one inherited-process node at the vanilla portrait-local position, and frees
that owned node before transitions. It does not open other built-in scenes.

Only those two bounded profiles are supported. RitsuLib exposes custom Event VFX/layout
routes, but their presence does not promote arbitrary assets. Keep them unused unless a
separate real-host proof expands this contract. Arbitrary VFX, shaders, audio,
custom/Ancient-layout animation, and other animation-bearing families remain outside this
recipe.

## Type + Scenario proof (`MapNode`)

1. **Type:** clean build/package/load; `ModelDb.Event<T>()` resolves the custom event;
   exact load marker appears with no mod-named errors.
2. **Scenario:** enter the real event room and click its real option UI:

```csharp
var canonical = ModelDb.Event<<Name>>();
await RunManager.Instance.EnterRoomDebug(RoomType.Event, MapPointType.Unknown, canonical);

var room = (EventRoom)RunManager.Instance.DebugOnlyGetState()!.CurrentRoom!;
var mutableEvent = (<Name>)room.LocalMutableEvent;

var choice = UiHelper.FindAll<NEventOptionButton>(NEventRoom.Instance!)
    .Single(button =>
        !button.Option.IsLocked
        && button.Option.Title.GetFormattedText() == "<Option title>");
var before = mutableEvent.Owner!.Gold;
await UiHelper.Click(choice);

await WaitHelper.Until(
    () => mutableEvent.Owner!.Gold == before + <amount> && mutableEvent.IsFinished,
    ct, TimeSpan.FromSeconds(30), "event option consequence not observed");
```

The harness also reads the formatted title, option title/description, and result-page text,
so registration plus a gold mutation cannot hide broken nested localization. See
`reference/selftest-harness.md` section `MapNode` for the full driver contract.

When SPEC selects native option presentation, extend that same headed `MapNode` run as
specified in `reference/event-option-presentation.md`: focus and unfocus enabled typed
tips, preserve the locked-tip suppression boundary, inspect normal `CreateModRelicOption<T>`
metadata without claiming an image, and compare safe versus exact-lethal HP/Max HP native
glow before driving the semantic consequence.

For an Event with blocking overlays or special combat, use the extended `MapNode` driver
from `reference/event-outcomes.md`: execute only SPEC's independent branches, identify the
custom encounter, prove `Resume` or direct-map behavior, and emit one structured outcome-
family marker. Any Event VFX claim additionally follows its owning reference and requires
headed screenshots plus explicit owned-node cleanup assertions. Native acquisition,
screen-shake, or `trial_noble` claims use the combined proof in
`reference/event-native-presentation.md`.

## Manual fallback

During an active run, the dev-console command is:

```text
event <MOD>_EVENT_<TYPE>
```

It is an exact uppercased `Id.Entry` match. In manual fallback, choose the option normally
and directly confirm the run-state consequence; the option marker is diagnostic only.

## Checklist

- [ ] subclass `ModEventTemplate`; register once with `.SharedEvent` or `.ActEvent`
- [ ] no `[Pool]`, constructor registration, manual `AddEvent`, or second content pack
- [ ] add `IsAllowed` only when run-state eligibility needs it
- [ ] a forced follow-up target uses `IsAllowed(...) => false`; its unplayable Quest token
      owns the two public hook overrides and is consumed by one named completion option
- [ ] flat `events.json` includes the normalized Event title, `INITIAL`, every option, and every result page
- [ ] every explicit `InitialOptionKey`/`ModOptionKey` segment matches JSON exactly
- [ ] enabled typed Hover Tips use only grounded factories; locked-option tips remain an
      explicit presentation gap
- [ ] `CreateModRelicOption<T>` is paired with the real obtain Cmd when acquisition is intended;
      normal-layout relic images are not claimed
- [ ] every HP/Max HP warning uses the exact Cmd cost and the matching native helper;
      inclusive exact-lethal boundaries are preserved
- [ ] every Card/relic acquisition uses one semantic Cmd and its matching native preview;
      no duplicate grant or custom holder/card node is emitted
- [ ] screen shake is `none` or one `weak_short` call on a named successful option and
      never changes the player's setting/multiplier
- [ ] option effect uses public Cmds and logs after the state change
- [ ] event ends with `SetEventFinished` or deliberately advances with `SetEventState`
- [ ] `EventAssetProfile.InitialPortraitPath` checks the mod portrait, falls back to
      `res://images/events/this_or_that.png`, and filters the missing derived path
- [ ] every selected initial/page portrait is an opaque `3440×1613`
      `images/events/<slot-slug>.png`; absent page art retains the current portrait
- [ ] Event/page option titles are plain; description rich text uses only balanced bounded
      tags from `reference/event-text-effects.md`
- [ ] blocking selection/reward Cmds are awaited before changing Event state
- [ ] every room-changing Event is shared; each mutable Event instance enters at most one
      special combat; `shouldResumeAfterCombat` matches the authored post-combat branch
- [ ] no guessed phobia/layout files and no merchant/rest/treasure room transitions
- [ ] VFX is `none`, `portrait_halo`, or the curated built-in `trial_noble`; every owned
      named node is explicitly freed before page/portrait/combat transitions
- [ ] `MapNode` proof enters the real room, drives every independent SPEC outcome family,
      reads nested loc, and asserts exact post-state plus every selected visible option
      presentation state
