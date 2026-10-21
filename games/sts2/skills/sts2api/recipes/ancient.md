# Recipe: Custom Ancient

Use `ModAncientEventTemplate` for a new Ancient encounter with its own identity, dialogue, option
pool, outcomes, and map/run-history presentation. Editing an existing vanilla Ancient is a
different operation owned by `reference/vanilla-ancient-overrides.md`, never a shortcut here.

A new Ancient's option bodies may use the bounded public Event outcome and presentation
references for typed Hover Tips, costs, Cmds, page effects, or acquisitions, but it is not an
ordinary Event and never goes through `recipes/event.md`. Read `reference/lifecycle-state-rng.md`
when state crosses callbacks or an option is randomized. Settings, Progression, Telemetry,
Multiplayer, post-run Badge, and Update Check integrations are deferred. Global replacement of
native Ancient dialogue or the Ancient room, behavior outside the public
option/page/dialogue/presentation vocabulary, direct merchant/rest/treasure transitions, and
multiplayer presentation are unsupported.

## DESIGN and SPEC vocabulary

Settle and write:

- placement: Shared Ancient or scoped to one or more exact Acts, never both for one identity;
- the `IsValidForAct` rule, including the neutral rejected Act;
- every possible option, the exact initial subset/ordering rule, enabled/locked state, typed
  Hover Tips, costs, ordered outcomes, page transitions, and terminal `Done()` behavior;
- deterministic selection from the mutable event's supplied `Rng`; preview, disabled, or
  rejected paths consume no random value and mutate nothing;
- first-visit-ever, exact Character, and `ANY` dialogue groups; visit index, repeat mode,
  speaker, prompt, optional line SFX, dialogue color, and any `ANY` blacklist;
- English and Simplified Chinese title, epithet, page/option text, dialogue, and SmartFormat
  variable parity; stable page/option names are localization and run-history identities;
- layout/portrait/background/VFX, map and run-history icon pairs, optional procedural stage,
  ambient BGM, and explicit fallback (placeholder mode is the checked Darv profile in § Required
  explicit fallback, never empty profiles); and
- a real Ancient `MapNode` SelfTest plus headed dialogue/options/icons/controller proof.

## Registration

Register exactly once as either Shared or Act-scoped, never both for one model:

```csharp
ModContentPackBuilder.For(MainFile.ModId)
    .SharedAncient<<AncientName>>()
    // or .ActAncient<<ActName>, <AncientName>>()
    .Apply();
```

Shared registration still passes through `IsValidForAct(ActModel)`; return `false` for every Act
whose generated Ancient pool it must not enter. Act-scoped registration is a fixed relation that
the validity method may narrow further.

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
`AllPossibleOptions` lists every option the Ancient can ever generate; `GenerateInitialOptions`
returns the concrete initial subset and order for the mutable event. Use the event instance's
`Rng` for random subsets or shuffles, after all eligibility checks. Preview, locked, rejected, and
canonical-model paths consume no RNG and mutate nothing.

Use `InitialOptionKey("NAME")` or `ModOptionKey("PAGE", "NAME")` and keep both segments stable.
An option callback runs on the mutable Ancient and binds its owner Player through `Owner`. It
checks every cost and choice before the first mutation, lowers immediate effects through
`reference/effect-primitives.md`, awaits public commands in order, inspects nullable/result
outcomes, then calls `SetEventState(...)` for an explicitly modeled page or `Done()` to record
Ancient choice history and finish, returning a completed `Task`. It has no generic combat target
or context, so combat-pile, Energy/Stars, Orb, draw, or targeted Creature effects are blocked
unless a selected specialized route supplies them. `CreateModRelicOption<T>()` obtains a mutable
Relic for the owner and calls `Done()` by default; its overload takes a custom awaited callback.

## Dialogue and localization

The template's `DefineDialogues()` loads `ancients.json`; override it only when the localization
format cannot express the requested structure. Ship matching `eng` and `zhs` keys:

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
  "<ENTRY>.talk.ANY.0-0r.ancient": "<line>",
  "<ENTRY>.talk.ANY.0-visit": "0"
}
```

Keep at least one repeating group (the `r` suffix) that every Character can reach. The native room
picks one valid dialogue per visit and throws when none is left, so a Mod with only first-visit
and fixed-visit groups breaks after its scripted visits; the kit's roll call reports it for every
Character.

`.next` is the button that advances to the following line, so only a non-terminal line has one;
vanilla never puts `.next` on a dialogue's last line, and Build rejects it.

Character dialogue uses `<ENTRY>.talk.<CHARACTER_ENTRY>.<dialogue>-<line>.<ancient|char>`.
Dialogue and line indices start at zero and stay contiguous; an `r` after the line index marks a
repeating dialogue, consistently for every line in it. Add optional `.sfx` beside a line key. The
loader uses the first `firstVisitEver` sequence, then exact Character groups, then `ANY`.
Override `AnyCharacterDialogueBlacklist` only for explicitly excluded canonical Characters.

Title and epithet stay plain. Page and option descriptions follow the Event rows of
`reference/vanilla-text-style.md` (`Lose [red]{HpLoss}[/red] HP. Obtain [gold]{Relic}[/gold].`);
dialogue follows `reference/ancient-dialogue.md` and keeps its spoken voice.

## Presentation

`EventAssetProfile` owns layout, initial portrait, background scene, and VFX scene.
`AncientEventPresentationAssetProfile` owns the map icon/outline, run-history icon/outline, and
optional `StageProcedural` from `ModAncientStageVisuals.Stage()`. `DialogueColor`, optional
`AmbientBgm`, and the normal event `ButtonColor` are model properties. Prefer explicit Mod-local
paths; a vanilla helper is valid only when every derived resource is checked.

### Required explicit fallback

Never leave both profiles empty. Unset fields fall back to the `AncientEventModel` convention,
which derives every path from the new Ancient's own id
(`scenes/events/background_scenes/<entry>.tscn`,
`images/packed/map/ancients/ancient_node_<entry>.png` and its outline, the run-history
icon/outline, `images/events/<entry>.png`). None exist for a new id, so the room or map would load
missing resources. Point every field at checked vanilla resources; the default borrows the shared
vanilla Ancient Darv:

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

A custom Ancient look needs Mod-local resources the user supplies: a background `PackedScene` and
PNG icons. `gen_sprite.py` has no Ancient background or icon spec, so image generation cannot
produce them. Check each Mod-local path with `ResourceLoader.Exists` and keep the Darv fallback for
every missing field. Record the borrowed look in SPEC so the user knows the room shares Darv's
background and icons.

## Self-test driver body

A new Ancient's room uses `NAncientEventLayout`, plays a dialogue, and is recorded as an Ancient
map point. `plan.Ancient<TAncient>(name, body)` enters it the way the game's own `event <ID>`
console command does for an Ancient (`MapPointType.Ancient`), confirms the layout, and advances the
dialogue through the real `%DialogueHitbox` until the options are enabled. The roll call already
resolved its title, epithet, and initial page, and proved a valid dialogue remains for every
Character on a first and a late visit.

```csharp
plan.Ancient<EmberOracle>("ember_oracle_gift_gives_30_gold", async t =>
{
    var shared = ModelDb.AllSharedAncients.OfType<EmberOracle>().Count();
    t.Proof(shared == 1, $"ancient registration expected=shared:1 observed=shared:{shared}");
    var open = t.EventOptions().Where(option => !option.IsLocked).Select(option => option.TextKey).ToList();
    t.Proof(open.Count == 2, $"oracle options expected=GIFT,LEAVE observed={string.Join(",", open)}");
    int gold = t.Player.Gold;
    await t.ChooseEventOption("GIFT");
    await t.WaitUntil(() => t.Event.IsFinished, "oracle did not finish after GIFT");
    t.Proof(t.Player.Gold - gold == 30, $"gift gold expected=+30 observed=+{t.Player.Gold - gold}");
});
```

Assert the SPEC's `DialogueSet` shape when it selects dialogue (`((AncientEventModel)t.Event)
.DialogueSet.FirstVisitEverDialogue?.Lines.Count`, `AgnosticDialogues.Count`). The options can be
enabled while the dialogue is still on screen, so the kit may advance with zero clicks; the
`DialogueSet` assertion proves the data and headed review proves the display. To reach the room
by hand, start a run and enter `event <ENTRY>` in the dev console.

## Proof matrix

1. Assert exactly one registered identity, inclusion in every accepted Act pool, and exclusion
   from a rejected Act.
2. Assert `AllPossibleOptions`, the generated initial subset/order, enabled/locked states, and no
   duplicate text keys.
3. Select every reachable option and branch through its real UI path, wait for queued commands,
   and assert exact cost/outcome/page/history state plus a no-mutation rejection case.
4. Assert first-visit-ever, Character-specific, `ANY`, repeat/visit routing, speaker order,
   prompts, optional SFX paths, and blacklist behavior from the real localization consumer.
5. Leave/re-enter or save/load as selected and assert no stale options, repeated reward, or
   duplicate dialogue registration.
6. Headed review checks name/epithet, portrait/stage, map and run-history icons, speech
   direction/color, option layout, mouse/controller progression, ambient audio, and cleanup.

Build, direct `GenerateInitialOptions()` calls, asset paths, and localization parsing are not
game observation.
