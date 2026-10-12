# Recipe: Custom Ancient

Use `ModAncientEventTemplate` for a new Ancient identity. Register it exactly once as either shared
or Act-scoped:

```csharp
ModContentPackBuilder.For(MainFile.ModId)
    .SharedAncient<<AncientName>>()
    // or .ActAncient<<ActName>, <AncientName>>()
    .Apply();
```

Do not combine both registrations for one model. Shared registration still passes through
`IsValidForAct(ActModel)`; return `false` for every Act where it must not enter the generated
Ancient pool. Act-scoped registration expresses a fixed relation and the validity method may
further narrow it.

## Options and deterministic lifecycle

Override both option views:

```csharp
private EventOption LeaveOption => new(
    this,
    () =>
    {
        Done();
        return Task.CompletedTask;
    },
    InitialOptionKey("LEAVE"));

public override IEnumerable<EventOption> AllPossibleOptions => [LeaveOption];

protected override IReadOnlyList<EventOption> GenerateInitialOptions() => [LeaveOption];
```

`EventOption` requires a `Func<Task>` callback while `Done()` returns `void`; wrap it as above.
`AllPossibleOptions` lists every option the Ancient can ever generate. `GenerateInitialOptions`
returns the concrete initial subset/order for the mutable event. Use the event instance's `Rng`
for random subsets or shuffles, after all eligibility checks. Preview, locked, rejected, and
canonical-model paths consume no RNG and mutate nothing.

Use `InitialOptionKey("NAME")` or `ModOptionKey("PAGE", "NAME")`. Keep both segments stable.
Option callbacks check every cost/choice before the first mutation, await public commands in
order, then either call `SetEventState(...)` for an explicitly modeled page or `Done()` to record
Ancient choice history and finish. A callback that calls `Done()` directly must still return a
completed `Task`. `CreateModRelicOption<T>()` obtains a mutable Relic for the owner and calls
`Done()` by default; its overload accepts a custom awaited callback.

Read only the selected Event outcome/presentation references for typed Hover Tips, costs, public
Cmds, page effects, or acquisitions. They do not turn this into an ordinary Event or authorize a
deferred Settings/Progression/Telemetry/Multiplayer integration.

For an option's immediate child effects, read `reference/effect-primitives.md`, bind the mutable
Ancient's owner Player, await the exact sequence, and finish/page only after all required results
succeed. This recipe retains the Ancient option/dialogue/presentation transaction.

## Dialogue and localization

The template's `DefineDialogues()` loads `ancients.json`; override it only when the localization
format genuinely cannot express the requested structure. Ship matching `eng` and `zhs` keys for:

```json
{
  "<ENTRY>.title": "<name>",
  "<ENTRY>.epithet": "<epithet>",
  "<ENTRY>.pages.INITIAL.description": "<description>",
  "<ENTRY>.pages.INITIAL.options.LEAVE.title": "<title>",
  "<ENTRY>.pages.INITIAL.options.LEAVE.description": "<description>",
  "<ENTRY>.pages.DONE.description": "<finished text>",
  "<ENTRY>.talk.firstVisitEver.0-0.ancient": "<line>",
  "<ENTRY>.talk.firstVisitEver.0-0.next": "<prompt>",
  "<ENTRY>.talk.firstVisitEver.0-1.ancient": "<last line>",
  "<ENTRY>.talk.ANY.0-0.ancient": "<line>"
}
```

`.next` is the button that advances to the following line, so only a non-terminal line has
one; vanilla never puts `.next` on a dialogue's last line, and Build rejects it.

Title and epithet stay plain. Page and option descriptions follow the Event rows of
`reference/vanilla-text-style.md` (`Lose [red]{HpLoss}[/red] HP. Obtain [gold]{Relic}[/gold].`);
dialogue follows `reference/ancient-dialogue.md` and keeps its spoken voice.

Character dialogue uses `<ENTRY>.talk.<CHARACTER_ENTRY>.<dialogue>-<line>.<ancient|char>`.
Dialogue and line indices start at zero and remain contiguous; an `r` after the line index marks
a repeating dialogue, consistently for every line in that dialogue. Add `.next` only where the
real UI should advance, and optional `.sfx` beside the line key. The loader uses the first
`firstVisitEver` sequence, exact Character groups, then `ANY` fallback. Override
`AnyCharacterDialogueBlacklist` only for explicitly excluded canonical Characters.

## Presentation

`EventAssetProfile` owns layout, initial portrait, background scene, and VFX scene.
`AncientEventPresentationAssetProfile` separately owns map icon/outline, run-history icon/outline,
and optional `StageProcedural` from `ModAncientStageVisuals.Stage()`. `DialogueColor`, optional
`AmbientBgm`, and the normal event `ButtonColor` are model properties. Prefer explicit Mod-local
paths; a vanilla helper is valid only when every derived resource is checked.

### Required explicit fallback

Never leave both profiles empty. Unset fields fall back to the pinned `AncientEventModel`
convention, which derives every path from the new Ancient's own id:
`scenes/events/background_scenes/<entry>.tscn`,
`images/packed/map/ancients/ancient_node_<entry>.png` (+ `_outline`), the run-history
icon/outline, and `images/events/<entry>.png`. None of those exist for a new id, so the room or
map would load missing resources. Point every field at checked vanilla resources instead. The
default fallback borrows the shared vanilla Ancient Darv:

```csharp
using MegaCrit.Sts2.Core.Helpers;
using STS2RitsuLib.Scaffolding.Content;

public override EventAssetProfile AssetProfile => new(
    InitialPortraitPath: "res://images/events/this_or_that.png",
    BackgroundScenePath: SceneHelper.GetScenePath("events/background_scenes/darv"));

public override AncientEventPresentationAssetProfile AncientPresentationAssetProfile => new(
    MapIconPath: ImageHelper.GetImagePath("packed/map/ancients/ancient_node_darv.png"),
    MapIconOutlinePath: ImageHelper.GetImagePath("packed/map/ancients/ancient_node_darv_outline.png"),
    RunHistoryIconPath: ImageHelper.GetImagePath("ui/run_history/darv.png"),
    RunHistoryIconOutlinePath: ImageHelper.GetImagePath("ui/run_history/darv_outline.png"));
```

This exact profile entered a real Ancient room on the pinned host (Tier 2 passed; headed
review saw the dialogue and room). Its map and run-history icons were not yet
headed-reviewed.

A custom Ancient look needs Mod-local resources the user supplies: a background
`PackedScene` and PNG icons. `gen_sprite.py` has no Ancient background or Ancient icon spec,
so image generation cannot produce them. Check each Mod-local path with
`ResourceLoader.Exists` and keep the Darv fallback for every missing field. Record the
borrowed look as a presentation choice in SPEC so the user knows the room shares Darv's
background and icons.

No asset path, parsed dialogue key, or direct option call proves the native Ancient room. Follow
`surfaces/ancient.md` for exact `MapNode`, choice-history, dialogue, controller, icon, audio, and
cleanup proof. The SelfTest driver is `reference/selftest-harness.md` § The Ancient `MapNode`
scenario.

Game-observed so far: one Shared Ancient with the Darv fallback profile, a two-line
`firstVisitEver` plus one `ANY` dialogue, two initial options, and one Gold-gain option ending in
`Done()`. Its registration, parsed dialogue, both-language title/epithet/options, Gold, and
completion passed Tier 2, and headed review saw the dialogue display. Act-scoped
registration, `IsValidForAct` rejection, page transitions, Character-specific dialogue,
repeat visits, choice history, and map/run-history icons remain game-unobserved.
