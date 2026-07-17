# Recipe: Custom Event (World Node)

> A grounded pattern for a normal map event in STS2. The playable unit is the event
> room plus at least one consequential option: register it, enter it through the
> `MapNode` scenario, click a real option, and observe the resulting run-state change.

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

## Known-good skeleton

```csharp
// <ModName>Code/Events/<Name>.cs
using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using Godot;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Events;

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

`Owner` is null on the canonical model and non-null only after the mutable event enters a
run. Read it inside option methods / lifecycle hooks, never from the canonical instance.
Use game `Cmd`s for consequences (`PlayerCmd.GainGold`, card/relic/potion Cmds, creature
Cmds); do not mutate run fields directly.

## Art contract: normal initial portrait

Normal/default-layout event initial portraits are pipeline-supported as one loose opaque
PNG: `res://<ModName>/images/events/<slug>.png`, exactly **3440×1613**. Generate/import it
with `gen_sprite.py --spec event`; the `.pck` rebuild is required. The concrete event must
use the existence-checked override in the skeleton above because BaseLib returns
`CustomInitialPortraitPath` directly and does not provide the template fallback helper used
by cards/relics.

Placeholder remains the silent default: when the mod PNG is absent, return the live-proven
`res://images/events/this_or_that.png`. Do not return the missing custom path or rely on the
game to recover from its load error.

The 2026-07-17 `CanaryEvent` proof entered the real event room, observed the displayed
`%Portrait.Texture.ResourcePath` at the mod path and logical size 3440×1613, captured a
headed screenshot with the option UI over the custom portrait, clicked the option, and
passed strict Tier 2 with no fresh error block.

This does not cover a separate `_phobia_mode.png`, later-page portrait changes,
portrait-anchored VFX, custom layouts, or Ancient background scenes. Keep those as explicit
gaps rather than emitting guessed assets. Prompt composition and acquisition rules are in
`reference/art-contract.md`; event art keeps its focal subject left and UI space on the
right, unlike a centered card portrait.

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
- [ ] `EventLoc` includes title, `INITIAL`, every option, and every result page
- [ ] `Option(Method)` slug exactly matches its `EventOptionLoc` key
- [ ] option effect uses public Cmds and logs after the state change
- [ ] event ends with `SetEventFinished` or deliberately advances with `SetEventState`
- [ ] `CustomInitialPortraitPath` checks the mod portrait and falls back to
      `res://images/events/this_or_that.png`
- [ ] generated event portrait, when selected, is one opaque `3440×1613`
      `images/events/<slug>.png`; no guessed phobia/VFX/layout files
- [ ] `MapNode` proof enters room, reads nested loc, clicks UI, and asserts a run-state delta
