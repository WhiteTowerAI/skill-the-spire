# Recipe: Custom Event (World Node)

> A grounded pattern for a normal map event in STS2. The playable unit is the event
> room plus at least one consequential option: register it, enter it through the
> `MapNode` scenario, click a real option, and observe the resulting run-state change.

For the full option-result vocabulary (blocking card selections, custom rewards,
conditional pages, and resumable/terminal special combat), also read
`reference/event-outcomes.md`. When SPEC selects the bounded normal-layout
`portrait_halo` profile, read `reference/event-vfx.md`. When page or option descriptions
use styled/animated vanilla text, read `reference/event-text-effects.md`. When enabled
options use typed Hover Tips, relic-backed presentation, or exact HP/Max HP warnings, read
`reference/event-option-presentation.md`. When a custom Quest Card should force this Event
in one specified act, read `reference/forced-followup-event.md`.

## Registration (automatic, no `[Pool]`)

Subclass `BaseLib.Abstracts.CustomEventModel`. Its default constructor calls
`CustomContentDictionary.AddEvent(this)`, so instantiating the canonical model registers
it. Do **not** add `[Pool]` and do not call `AddEvent` manually.

`CustomEventModel.Acts` controls natural placement:

- the default empty array makes it a BaseLib "shared custom event" available to every
  act (this means shared across act pools, not multiplayer `EventModel.IsShared`);
- a non-empty `Acts` array limits it to those acts;
- override `IsAllowed(IRunState)` for run-state eligibility.

The canary uses the default all-act placement. Its scenario enters the event directly by
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
using System.Threading.Tasks;
using BaseLib.Abstracts;
using Godot;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Context;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.Nodes.Rooms;

namespace <ModName>.<ModName>Code.Events;

public sealed class <Name> : CustomEventModel
{
    public const string FallbackPortraitPath = "res://images/events/this_or_that.png";
    public static string ModPortraitPath =>
        $"{MainFile.ResPath}/images/events/<slug>.png";

    public override string? CustomInitialPortraitPath =>
        ResourceLoader.Exists(ModPortraitPath) ? ModPortraitPath : FallbackPortraitPath;

    public override List<(string, string)> Localization => new EventLoc(
        "<Title>",
        new EventPageLoc(
            "INITIAL",
            "<Initial description>",
            new EventOptionLoc("<OPTION_KEY>", "<Option title>", "<Option description>")),
        new EventPageLoc(
            "<RESULT_PAGE_KEY>",
            "<Result description>"));

    protected override IReadOnlyList<EventOption> GenerateInitialOptions()
        => new[] { Option(<OptionMethod>) };

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

The live canary is `GildedSignpost`: `FollowTheSign` grants 25 gold, then finishes on the
`FOLLOW_THE_SIGN` result page.

## Nested localization (prefer `EventLoc`)

Normal event localization is nested rather than the flat two/three-key shape used by
cards/relics/potions. BaseLib's in-code helpers generate the exact `events` table keys:

```text
<ID>.title
<ID>.pages.INITIAL.description
<ID>.pages.INITIAL.options.<OPTION_KEY>.title
<ID>.pages.INITIAL.options.<OPTION_KEY>.description
<ID>.pages.<RESULT_PAGE_KEY>.description
```

`EventLoc` supplies the title, `EventPageLoc` supplies each page description, and
`EventOptionLoc` supplies each option's title/description. `ModelLocPatch` prefixes every
relative key with the real `Id.Entry`, so do not include `<PREFIX>-<SLUG>` yourself in the
`EventLoc` tuples.

`Option(SomeMethod)` derives its option key by `StringHelper.Slugify(SomeMethod.Method.Name)`:

- method `FollowTheSign` -> key `FOLLOW_THE_SIGN`;
- the matching `EventOptionLoc` key must therefore be `FOLLOW_THE_SIGN`;
- `PageDescription("FOLLOW_THE_SIGN")` resolves the result page.

If these names disagree, the room can load but the UI shows missing/raw option text. This
method-name-to-loc relationship is the event equivalent of the usual `Id.Entry` footgun.

### Bounded rich text

Normal Event page descriptions and option descriptions are rendered by the game's existing
`MegaRichTextLabel`. They may use the vanilla-observed bounded tags from
`reference/event-text-effects.md`: `b`; `aqua`, `blue`, `gold`, `green`, `orange`,
`purple`, `red`; and the short motion tags `jitter` and `sine`.

Keep titles plain, balance/nest every tag, and do not emit arbitrary BBCode or parameters.
This path needs no C# helper or cleanup code; page changes replace the host label's text.

The recipe uses code localization because BaseLib already provides the nested EventLoc
types and the analyzer does not define an STS001 required-key row for `EventModel`. A mod
may instead ship `events.json`, but it must use the exact fully-prefixed keys above.

## Options and state transitions

- `GenerateInitialOptions()` returns the options shown on the initial page.
- `Option(Method)` creates an enabled option and binds the method as its effect.
- `LockedOption(key)` creates a disabled option with loc at the same page/key shape.
- `SetEventFinished(PageDescription(key))` shows the result text and replaces choices with
  the standard Proceed button.
- `SetEventState(description, options)` is the vanilla pattern for a multi-page event that
  presents another choice instead of finishing.

### Native option presentation

Enabled normal-Event options may pass typed Card/relic/potion/power tips through
`Option(Method, pageKey, tips)`. Construct only the selected types with the grounded
`HoverTipFactory` helpers in `reference/event-option-presentation.md`; the real option
button owns focus, display, and cleanup. `LockedOption` retains its tip data but the native
button deliberately does not display it, so never promise locked-option tooltips or emit a
custom workaround.

Use `RelicOption<T>` when SPEC selects relic-backed presentation. It provides the normal
relic title, description, and metadata. The actual obtain effect remains a separate awaited
`RelicCmd.Obtain<T>` consequence. Normal-layout Event buttons do not render the relic image:
that consumer is gated to `AncientEventModel`, so preserve a requested normal-layout image
as a presentation gap rather than opening an Ancient layout.

For a choice whose consequence pays HP or Max HP, attach the exact cost when generating
the option:

```csharp
Option(PayHp).ThatDoesDamage(damage);
Option(PayMaxHp).ThatDecreasesMaxHp(maxHpLoss);
```

The later Cmd still owns payment. These helpers only drive the native warning and use
inclusive lethal boundaries: `CurrentHp <= damage` and `MaxHp <= maxHpLoss`. The value
must exactly match the decimal cost resolved for the Cmd; do not round, estimate, or use
red localization text as a substitute.

`Owner` is null on the canonical model and non-null only after the mutable event enters a
run. Read it inside option methods / lifecycle hooks, never from the canonical instance.
Use game `Cmd`s for consequences (`PlayerCmd.GainGold`, card/relic/potion Cmds, creature
Cmds); do not mutate run fields directly.

This fast-path recipe shows one immediate effect. `reference/event-outcomes.md` is the
authoritative contract for composed effects, selection/reward overlays, locked options,
special-combat entry, `Resume`, optional combat rewards, and the one-combat-per-Event-
instance boundary. It also records that merchant/rest/treasure room transitions remain
unsupported.

## Art contract: normal and later-page portraits

Normal/default-layout event portraits are pipeline-supported as loose opaque PNGs, each
exactly **3440×1613**. The initial slot is
`res://<ModName>/images/events/<event-slug>.png`; an authored page slot uses
`res://<ModName>/images/events/<event-slug>_<page-key-lower>.png`. Generate/import each
selected slot with `gen_sprite.py --spec event`; every art change requires a `.pck`
rebuild. The concrete event must use the existence-checked initial override in the
skeleton above because BaseLib returns `CustomInitialPortraitPath` directly and does not
provide the template fallback helper used by cards/relics.

Placeholder remains the silent default: when the mod PNG is absent, return the live-proven
`res://images/events/this_or_that.png`. Do not return the missing custom path or rely on the
game to recover from its load error.

The 2026-07-17 `CanaryEvent` proof entered the real event room, observed the displayed
`%Portrait.Texture.ResourcePath` at the mod path and logical size 3440×1613, captured a
headed screenshot with the option UI over the custom portrait, clicked the option, and
passed strict Tier 2 with no fresh error block.

The 2026-07-20 extension kept that same room and click, then replaced the portrait with a
second mod PNG on the result page. The replacement path and 3440×1613 size were asserted,
the headed screenshot showed the new image, attached initial-page VFX had been removed,
and the same strict Tier 2 proof remained green. Use this bounded page-switch pattern:

The same date's acquisition acceptance submitted one approved `seedream-5.0-lite`
`21:9`/`2K` request with three randomly selected Event references. Its inspected wide
source normalized to 3440×1613, packed into this canary, rendered behind the real option
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

### Bounded VFX profile

Normal/default-layout Events may select the pipeline-supported `portrait_halo` profile in
`reference/event-vfx.md`. It uses public code-native Godot nodes through `OnRoomEnter` and
`NEventLayout.AddVfxAnchoredToPortrait`; it does not use an image backend or a `.pck` VFX
scene. The headed acceptance proved initial, later-page, combat cleanup, and resumed-page
presentation with Fast Mode handling and no fresh error.

Only that bounded profile is supported. BaseLib 3.3.5/3.3.6 declares
`CustomEventModel.CustomVfxPath` but does not consume it, so never override it as a route.
Arbitrary VFX, shaders, audio, custom/Ancient-layout animation, and other animation-bearing
families remain outside this recipe.

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
tips, preserve the locked-tip suppression boundary, inspect normal `RelicOption<T>`
metadata without claiming an image, and compare safe versus exact-lethal HP/Max HP native
glow before driving the semantic consequence.

For an Event with blocking overlays or special combat, use the extended `MapNode` driver
from `reference/event-outcomes.md`: execute only SPEC's independent branches, identify the
custom encounter, prove `Resume` or direct-map behavior, and emit one structured outcome-
family marker. Any Event VFX claim additionally follows `reference/event-vfx.md` and
requires headed screenshots plus explicit owned-node cleanup assertions.

Known-good live canary (2026-07-13, `CanaryEvent`): build 0/0, custom room entered,
`Gilded Signpost` and `Follow the sign` rendered from nested loc, the real option button was
clicked, gold changed `99 -> 124` (`delta=25`), result page resolved, and `selftest done`
appeared with zero mod-named errors.

## Manual fallback

During an active run, the dev-console command is:

```text
event <PREFIX>-<SLUG>
```

It is an exact uppercased `Id.Entry` match. In manual fallback, choose the option normally
and directly confirm the run-state consequence; the option marker is diagnostic only.

## Checklist

- [ ] subclass `CustomEventModel`; no `[Pool]`; no manual `AddEvent`
- [ ] decide all-act default vs. explicit `Acts`; add `IsAllowed` only when needed
- [ ] a forced follow-up target uses `IsAllowed(...) => false`; its unplayable Quest token
      owns the two public hook overrides and is consumed by one named completion option
- [ ] `EventLoc` includes title, `INITIAL`, every option, and every result page
- [ ] `Option(Method)` slug exactly matches its `EventOptionLoc` key
- [ ] enabled typed Hover Tips use only grounded factories; locked-option tips remain an
      explicit presentation gap
- [ ] `RelicOption<T>` is paired with the real obtain Cmd when acquisition is intended;
      normal-layout relic images are not claimed
- [ ] every HP/Max HP warning uses the exact Cmd cost and the matching native helper;
      inclusive exact-lethal boundaries are preserved
- [ ] option effect uses public Cmds and logs after the state change
- [ ] event ends with `SetEventFinished` or deliberately advances with `SetEventState`
- [ ] `CustomInitialPortraitPath` checks the mod portrait and falls back to
      `res://images/events/this_or_that.png`
- [ ] every selected initial/page portrait is an opaque `3440×1613`
      `images/events/<slot-slug>.png`; absent page art retains the current portrait
- [ ] Event/page option titles are plain; description rich text uses only balanced bounded
      tags from `reference/event-text-effects.md`
- [ ] blocking selection/reward Cmds are awaited before changing Event state
- [ ] every room-changing Event is shared; each mutable Event instance enters at most one
      special combat; `shouldResumeAfterCombat` matches the authored post-combat branch
- [ ] no guessed phobia/layout files and no merchant/rest/treasure room transitions
- [ ] VFX is `none` or the bounded normal-layout `portrait_halo`; every owned named node is
      explicitly freed before page/portrait/combat transitions
- [ ] `MapNode` proof enters the real room, drives every independent SPEC outcome family,
      reads nested loc, and asserts exact post-state plus every selected visible option
      presentation state
