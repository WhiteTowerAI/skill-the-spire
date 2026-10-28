# Recipe: Custom Event (World Node)

Everything one new normal map Event needs: the SPEC fields, the class, its text and portraits,
and the `MapNode` proof. The playable unit is the Event room plus at least one consequential
option: register it, enter it through the `MapNode` scenario, click a real option, and observe
the run-state change. Supported: nested pages/options, blocking selections and rewards, and one
resumable or terminal special combat per mutable Event instance; normal portraits, the bounded
`portrait_halo` and `trial_noble` VFX, and bounded vanilla description rich text. Unsupported:
custom phobia art, arbitrary VFX, custom or Ancient scenes, and merchant/rest/treasure room
transitions.

Also read, only when SPEC selects it:

- the full outcome vocabulary (composed effects, blocking selections, custom rewards, locked and
  conditional pages, special combat, `Resume`, extra combat rewards):
  `reference/event-outcomes.md`, the authoritative contract;
- `portrait_halo`: `reference/event-vfx.md`;
- extra atmosphere: `reference/event-text-effects.md`;
- enabled typed Hover Tips, relic-backed presentation, or exact HP/Max HP warnings:
  `reference/event-option-presentation.md`;
- a Quest Card that forces this Event in selected Acts: `reference/forced-followup-event.md`;
- native Card/relic acquisition presentation, the one-shot screen shake, or `trial_noble`:
  `reference/event-native-presentation.md`;
- lifecycle outside the option callback, state outside the mutable Event, persistence, or
  gameplay randomness: `reference/lifecycle-state-rng.md`.

Changing an exact existing vanilla Ancient's options or pages uses
`reference/vanilla-overrides.md` and `reference/vanilla-ancient-overrides.md`, never a second
Ancient. A fresh unlock gate on an ordinary vanilla Event or shared `EVENT.DARV` uses
`reference/vanilla-availability-overrides.md` (one pinned epoch, singleplayer); act-owned Ancients
and permanent Event disable are outside the availability routes.

## SPEC fields

```markdown
# SPEC — <Mod Name>

- **mod id**: <stable mod identity>
- **author**: <author>
- **content**:
  - name: <shown Event name>
  - surface: event
  - logical id: <stable local stem, e.g. gilded_signpost>
  - relations: none | <the Quest Card that forces entry into this Event>
- **registration**:
  - availability: shared | act:<name>
  - ownership: room
  - placement: all acts | <Glory | Hive | Overgrowth | Underdocks>
- **localization**:
  - languages: [eng, zhs]
  - fields: title, initial page description, every option title/description and result page;
    all in `events.json` under Mod-local keys
  - table intent: flat `events.json` entries
  - formatting: vanilla text style (`reference/vanilla-text-style.md`): option descriptions
    color costs red, gains green, counts blue, and terms gold; titles plain
  - displayed values: none | <value name -> the option/page text that shows it; declare one
    name per number the player reads, and reference it as a placeholder>
  - extra atmosphere: none | <PAGE/OPTION_KEY -> exact phrase -> one or more of emphasis,
    aqua/blue/gold/green/orange/purple/red, jitter, sine; descriptions only; titles plain>
- **effects**:
  - trigger: option selection
  - target: player
  - options:
    - id: <stable option stem, e.g. follow_the_sign>
      title: <button title>
      description: <button consequence text>
      effect: <ordered game-term consequence with numbers, including any blocking overlay>
      availability: always | gated by <exact run-state condition>
      hover tips: none | enabled-only <content name + upgrade/amount state>
      relic presentation: none | <relic name; normal title/description/metadata; image gap>
      lethal warning: none | HP cost <exact decimal> | Max HP cost <exact decimal>
      acquisitions: none | ordered known Card/relic grants, each with matching native presentation
      screen shake: none | `weak_short` | `strong_normal`
      next: finish <RESULT_KEY> | page <PAGE_KEY> | special combat <ENCOUNTER>
  - special combat: none | <encounter logical id + monster/group HP and grounded move cycle>
  - combat completion: resume page <PAGE_KEY> | map (exactly one when combat exists)
  - extra combat rewards: none | <owned reward types and amounts>
  - scaling: <declared values referenced in options/pages, or none>
- **state**:
  - lifetime: run (mutable Event instance persists for run-progress tracking)
  - owner: the Event room
  - reset: none (state is consumed and replaced by `SetEventFinished`/`SetEventState`)
  - persistence: ordinary (mutable state survives save/resume)
  - visible state: option enabled/locked states plus any dynamic text substitution
- **presentation**:
  - assets: portrait slots; placeholder | generate (normal/default layout only; every
    selected slot is an opaque 3440x1613 PNG)
  - portrait slots:
    - initial: `<event-slug>`
    - `<PAGE_KEY>`: `<event-slug>_<page-key-lower>` (only when explicitly requested)
  - art source: host-tool | backend:<name> | local-image (generate only)
  - art subject/style: <opening situation; focal subject left, darker UI space right>
  - native presentation: standard Event room layout
  - event VFX: none | `portrait_halo` | `trial_noble`
  - VFX pages: <PAGE_KEY -> unique node name, color/mood; normal layout only>
- **fallback**:
  - missing asset: initial uses the verified vanilla portrait; absent page art retains
    the current portrait
  - unavailable seam: VFX cleanup frees owned named nodes before page/portrait/combat/
    finish transitions; Instant Fast Mode is static for `portrait_halo`
  - failure policy: preserve fallback or stop authoring
- **proof**:
  - scenario: MapNode
  - driver: enter the canonical custom event, then drive real option UI
  - invariants: custom event room entered; formatted text and real option UI; every declared
    option present with its declared enabled/locked state; exact outcome/selection/reward
    post-state; encounter identity; expected Resume page or direct map
  - boundary cases: each gated option driven both ways; special combat resume or map;
    forced follow-up entry through a real Unknown MapPoint (not the `event` shortcut)
- **forced follow-up mappings**: none | one or more
  - id: <stable mapping id>
    token: <custom Quest Card logical id; exactly one in owner deck>
    condition: token_in_owner_deck
    acts: [<one or more exact zero-based act indices>]
    priority: <globally unique integer>
    conflict: fail_closed
    sequence: [<finite ordered unique custom Event ids; first is target>]
    consumption: on_target_success | on_sequence_complete
    consume at: <target for one-step | final sequence Event>
    progress: saved_card_index
    target pool rule: every sequence Event excluded from ordinary placement
- **forced-follow-up boundary**: solo; finite acyclic custom sequence; unchanged neutral
  return; no vanilla edits, duplicate-token rewards, fixed map node, cross-Mod composition,
  or multiplayer
- **option presentation gaps**: <locked-option tips, normal-layout relic image, or none>
- **unsupported transitions**: merchant, rest site, and treasure room
- **adapter output** (written to MEMORY after acceptance): resolved Event logical id,
  flat localization key list, and framework diagnostic record
```

Each option id is stable semantic input; method and localization keys derive from it. Special
combat also owns its custom Monster and Encounter from `recipes/monster.md`; never leave
`<ENCOUNTER>` abstract.

## Registration (one content-pack route)

Subclass `ModEventTemplate` and register it exactly once with `.SharedEvent<T>()` for all-Act
placement or `.ActEvent<TAct,T>()` for one Act. Never add `[Pool]`, instantiate the canonical
model, call `AddEvent`, or create a second content pack.

```csharp
RitsuLibFramework.CreateContentPack(ModId)
    .SharedEvent<<Name>>()
    .Apply();
```

`EventModel.IsShared` is the game's room/resume semantic, separate from shared-across-Act
registration; an Event that enters special combat sets `IsShared => true`. Override
`IsAllowed(IRunState)` only for run-state eligibility. The test scenario enters the Event
directly by canonical model, so map RNG cannot make the proof flaky.

**Multiplayer.** By default (`IsShared` false) every player gets its own copy of the Event and
chooses for itself; an option's effects act on `Owner`, the player whose copy it is. With
`IsShared => true` the players vote and the winning option runs for every player. Run-level
eligibility in `IsAllowed` is about the party: write it as vanilla does,
`runState.Players.All(p => <condition>)`. The multiplayer Tier 2 drives the host's choice and
the client checks the host's copy; a shared Event's vote is cast by both peers.

A forced follow-up target deliberately overrides natural placement: it returns false from
`IsAllowed`, and the carried Quest Card replaces an Unknown room roll and the following Event
pull. Follow `reference/forced-followup-event.md` exactly: one unplayable Quest Card per mapping
(Quest type/rarity, cost `-1`, no upgrades), a bounded saved index, globally ordered priority, the
two public hooks guarded by the declared Act set, duplicate-rejecting source grants, and only the
declared successful option advancing or terminally removing the token.

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
        "res://<ModName>/images/events/<slug>.png";

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

## Options and state transitions

- `GenerateInitialOptions()` returns the initial page's options.
- `new EventOption(this, Method, InitialOptionKey(key))` creates an enabled initial option; use
  `ModOptionKey(page, key)` on later pages. A `null` callback creates a locked option that keeps
  its typed data.
- `SetEventFinished(PageDescription(key))` shows the result text and the standard Proceed button.
- `SetEventState(description, options)` presents another page of choices instead of finishing.

`Owner` is null on the canonical model and non-null only after the mutable Event enters a run;
read it inside option methods and lifecycle hooks. Lower immediate Gold, healing/HP, known
run-content acquisition, and other primitives whose exact inputs exist through
`reference/effect-primitives.md`; never mutate run fields directly. The bounded outcome route
permits `ThrowingPlayerChoiceContext` for its documented HP/Max HP commands, but it never invents
a combat target, combat piles, Energy/Stars, or an Orb queue outside a live combat-resume route.
Preflight every cost and availability condition before the first mutation, await the full
sequence (blocking selection and reward overlays included), inspect rejected acquisition results,
log the observed delta, and only then call `SetEventFinished`, `SetEventState`, or the one special
combat transition.

### Special combat

An option that enters combat authors its Monster and Encounter from `recipes/monster.md`, sets
`IsShared => true`, and calls `EnterCombatWithoutExitingEvent<TEncounter>(extraRewards,
shouldResumeAfterCombat)`. A resumable branch overrides `Resume(AbstractRoom)` and restores its
exact named page; a terminal branch proceeds to the map. Never start a second combat from the same
mutable Event instance or a direct merchant/rest/treasure room transition.

### Numbers the player reads should be declared values

The engine substitutes the Event's `DynamicVars` into every option title, option description,
and page description at render time. Vanilla `TrashHeap` declares `new HpLossVar(8m)` and
`new GoldVar(100)`, and `SlipperyBridge` mutates `DynamicVars["HpLoss"].BaseValue` as its HP cost
escalates, one localization key serving several costs. Declare each SPEC displayed value in
`CanonicalVars` (or compute it in `CalculateVars()`) and reference it as a placeholder, so text
and effect share one source. A literal is acceptable only for a single fixed-cost option whose
number appears in one place; prefer the declared value whenever the number changes across pages
or visits, appears in both the Cmd and the text, or feeds a `lethal warning`.

### Native option presentation

Enabled options may pass typed Card/relic/potion/power tips through the `EventOption`
constructor, built only with the grounded `HoverTipFactory` helpers in
`reference/event-option-presentation.md`; the real option button owns focus, display, and
cleanup. A null-callback option keeps its tip data but the native button deliberately hides it,
so never promise locked-option tooltips or emit a workaround.

`CreateModRelicOption<T>` provides the normal relic title, description, and metadata; the
actual obtain stays a separate awaited `RelicCmd.Obtain<T>`. Normal-layout buttons do not render
the relic image (that consumer is gated to `AncientEventModel`), so a requested image is a
presentation gap, never a reason to open an Ancient layout.

For a choice that pays HP or Max HP, attach the exact cost when generating the option:

```csharp
new EventOption(this, PayHp, ModOptionKey("PAGE", "PAY_HP"))
    .ThatDoesDamage(damage);
new EventOption(this, PayMaxHp, ModOptionKey("PAGE", "PAY_MAX_HP"))
    .ThatDecreasesMaxHp(maxHpLoss);
```

The later Cmd still owns payment; these helpers only drive the native warning, with inclusive
lethal boundaries `CurrentHp <= damage` and `MaxHp <= maxHpLoss`. The value must equal the exact
decimal cost the Cmd resolves: never round, estimate, or substitute red text.

### Native acquisition and adjacent presentation

Await declared acquisitions in SPEC order. Pass each successful `CardPileCmd.Add` result to
`CardCmd.PreviewCardPileAdd`, never a second Card. A relic uses exactly one awaited
`RelicCmd.Obtain<T>`, which already owns the inventory animation. A named successful option may
add one preference-respecting `weak_short` or `strong_normal` shake, called once after the
consequence and before its page transition; never read or replace the player's multiplier.
`reference/event-native-presentation.md` owns ordering, allowed values, and the combined headed
proof.

## Localization (`events.json`)

Normal Event localization is a flat table whose keys describe the nested page/option shape.
RitsuLib's normalized entry is `<MOD>_EVENT_<TYPE>`:

```text
<ID>.title
<ID>.pages.INITIAL.description
<ID>.pages.INITIAL.options.<OPTION_KEY>.title
<ID>.pages.INITIAL.options.<OPTION_KEY>.description
<ID>.pages.<RESULT_PAGE_KEY>.description
```

`InitialOptionKey("FOLLOW_THE_SIGN")` and `ModOptionKey("PAGE", "OPTION")` build the exact keys
`EventOption` consumes, and `PageDescription("PAGE")` resolves a page description. Keep the
upper-snake segment identical to the JSON; method names never mint keys. Ship `events.json` in
the resource PCK; a DLL-only rebuild does not update it.

Page and option descriptions follow the Event rows of `reference/vanilla-text-style.md`:

```json
{
  "<EVENT>.pages.INITIAL.description": "A cracked shrine hums in the dark.\n\nSomething [gold]glitters[/gold] beneath the altar.",
  "<EVENT>.pages.INITIAL.options.PRAY.title": "Pray",
  "<EVENT>.pages.INITIAL.options.PRAY.description": "Lose [red]{HpLoss}[/red] HP. [gold]Upgrade[/gold] a random card.",
  "<EVENT>.pages.INITIAL.options.REST.description": "Heal [green]{Heal}[/green] HP."
}
```

```json
{
  "<EVENT>.pages.INITIAL.description": "一座破裂的神龛在黑暗中嗡嗡作响。\n\n祭坛下有什么东西在[gold]闪烁[/gold]。",
  "<EVENT>.pages.INITIAL.options.PRAY.title": "祈祷",
  "<EVENT>.pages.INITIAL.options.PRAY.description": "失去[red]{HpLoss}[/red]点生命。随机[gold]升级[/gold]一张牌。",
  "<EVENT>.pages.INITIAL.options.REST.description": "回复[green]{Heal}[/green]点生命。"
}
```

Option descriptions color costs `[red]`, heals and gains `[green]`, counts `[blue]`, and glossary
terms plus obtained Relic/Card names `[gold]`. Pages are second-person narrative with paragraphs
separated by `\n\n`. Titles stay plain. Extra atmosphere, only when SPEC selects it, adds the
bounded tags from `reference/event-text-effects.md` around the named phrases (`b`; `aqua`, `blue`,
`gold`, `green`, `orange`, `purple`, `red`; `jitter`, `sine`), balanced and unparameterized; it
needs no C# helper or cleanup, because page changes replace the host label's text.

## Art contract: normal and later-page portraits

Normal-layout portraits are loose opaque PNGs, each exactly **3440×1613**: the initial slot is
`res://<ModName>/images/events/<event-slug>.png` and a requested page slot is
`res://<ModName>/images/events/<event-slug>_<page-key-lower>.png`. Generate or import each slot
with `gen_sprite.py --spec event` (prompt rules in `reference/art-contract.md`: focal subject
left, UI space right); every art or localization change needs a `.pck` rebuild.

The skeleton's `InitialPortraitPath` uses the Mod PNG when present and otherwise the verified
`res://images/events/this_or_that.png`, and `GetAssetPaths` filters the missing
convention-derived path. Never return the missing custom path or rely on the game recovering
from its load error.

For a requested page portrait, call this immediately before `SetEventState` or
`SetEventFinished`; when the PNG is absent it does nothing and the current portrait stays:

```csharp
public static string ResultPortraitPath =>
    "res://<ModName>/images/events/<event-slug>_<page-key-lower>.png";

private void ShowResultPortraitIfPresent()
{
    if (!LocalContext.IsMe(Owner) || !ResourceLoader.Exists(ResultPortraitPath))
        return;

    var room = NEventRoom.Instance;
    room?.Layout?.RemoveNodesOnPortrait();
    room?.SetPortrait(ResourceLoader.Load<Texture2D>(ResultPortraitPath));
}
```

No separate `_phobia_mode.png`, custom layout, or Ancient background scene is covered.

### Bounded VFX profiles

Only two profiles exist. `portrait_halo` (`reference/event-vfx.md`) builds public code-native
Godot nodes through `OnRoomEnter` and `NEventLayout.AddVfxAnchoredToPortrait`, with no image
backend or `.pck` scene: attach page profiles through `OnRoomEnter`/the portrait host, honor
Instant/Fast Mode, and `QueueFreeSafely` every owned named root before page, portrait, combat, or
finish transitions. `trial_noble` (`reference/event-native-presentation.md`) preloads the exact
vanilla Trial scene, instantiates one inherited-process node at the vanilla `(292,68)` portrait
position, and frees that owned node before transitions. RitsuLib's other custom Event VFX/layout
routes stay unused; arbitrary VFX, shaders, audio, and custom/Ancient-layout animation are outside
this recipe.

## Checklist

- [ ] `ModEventTemplate` registered once with `.SharedEvent` or `.ActEvent`; `IsAllowed` only
      for run-state eligibility; a forced follow-up target returns false and its Quest token
      owns the two public hooks and is consumed by one named completion option.
- [ ] Flat `events.json` has the Event title, `INITIAL`, every option, and every result page;
      every `InitialOptionKey`/`ModOptionKey` segment matches the JSON exactly.
- [ ] Option effects use public Cmds, await blocking selection/reward Cmds before changing Event
      state, log after the state change, and end with `SetEventFinished` or `SetEventState`.
- [ ] Typed Hover Tips use grounded factories only; `CreateModRelicOption<T>` pairs with the real
      obtain Cmd; every HP/Max HP warning uses the exact Cmd cost.
- [ ] Each acquisition uses one semantic Cmd and its native preview; screen shake is `none` or
      one allowlisted call on a named successful option.
- [ ] Every room-changing Event is shared, enters at most one special combat per mutable
      instance, and `shouldResumeAfterCombat` matches the authored branch.
- [ ] The portrait profile checks the Mod PNG, falls back to `this_or_that.png`, and filters the
      derived path; every selected slot is an opaque `3440×1613` PNG.
- [ ] VFX is `none`, `portrait_halo`, or `trial_noble`, with every owned named node freed before
      transitions.

## Self-test driver body

Use the **`MapNode`** host: `plan.Event<TEvent>(name, body)` enters the real `EventRoom` as an
Unknown map point, waits for the nested Event UI and its option buttons, and hands over.
`t.ChooseEventOption(key)` clicks the real `NEventOptionButton` whose `Option.TextKey` is the key
or ends with `.<key>` (never English text) and waits until the host took it; `"proceed"` clicks
the option whose `IsProceed` is set. Assert each option's run-state consequence and the page it
leads to:

```csharp
plan.Event<EmberShrine>("ember_shrine_offer_gives_25_gold", async t =>
{
    var keys = string.Join(",", t.EventOptions().Select(option => option.TextKey));
    t.Proof(t.EventOptions().Count == 2, $"initial options expected=OFFER,BLESS observed={keys}");
    int gold = t.Player.Gold;
    await t.ChooseEventOption("OFFER");
    await t.WaitUntil(() => t.Event.IsFinished, "shrine did not finish after OFFER");
    t.Proof(t.Player.Gold - gold == 25, $"offer gold expected=+25 observed=+{t.Player.Gold - gold}");
    await t.ChooseEventOption("proceed");
});
```

A page that presents another choice (`SetEventState`) is a second `ChooseEventOption` after
`t.WaitUntil(() => t.EventOptions().Any(option => option.TextKey.EndsWith(".CONTINUE")), ...)`.
The kit's roll call resolves the Event's title and initial page in both languages, so broken
nested localization cannot hide behind a Gold mutation; resolve a later page's
`t.Event.Description` and each option's `Title`/`Description` in the scenario when SPEC selects
them. An Event with blocking overlays or special combat uses the extended driver in
`reference/event-outcomes.md` § Verification contract; selected VFX, text effects, and native
presentation extend the same run through their own references.

## Proof matrix

- Require one real UI path per independent SPEC outcome family; blocking Card/reward overlays
  finish before their post-state assertion.
- **Assert the option set before choosing.** Assert every declared option id is present on its
  page with its declared enabled/locked state before driving any of them.
- **Drive each gated option both ways** by changing the real run-state condition.
- A special combat identifies the custom Encounter and proves exactly one authored completion
  path, named `Resume` page or direct map; use a fresh Event instance to exercise both.
- A custom portrait asserts the displayed `%Portrait.Texture.ResourcePath` is the Mod path at
  logical size 3440×1613, with a headed screenshot of the option UI over it; a page switch asserts
  the replacement path and size plus removal of initial-page VFX.
- Native option presentation extends the same headed run (`reference/event-option-presentation.md`):
  focus/unfocus enabled typed tips, keep the locked-tip suppression boundary, inspect
  `CreateModRelicOption<T>` metadata without claiming an image, and compare safe versus
  exact-lethal HP/Max HP glow before driving the consequence.
- Any VFX, acquisition, shake, or `trial_noble` claim follows its owning reference with headed
  screenshots and explicit owned-node cleanup assertions.
- The final structured marker lists identical expected/observed outcome families.

## Manual fallback (only when the harness cannot reach its scenario)

Grant it: `event <MOD>_EVENT_<TYPE>` enters the custom Event (exact uppercased `Id.Entry` match;
run in progress); confirm the localized option appears before choosing it. Trigger it: choose the
specified options and confirm each exact consequence. For special combat, confirm the custom
Encounter and then the named return page or direct map. For `portrait_halo`, inspect configured
pages and confirm no stale overlay survives a page switch or combat entry; for text effects,
confirm the prior page's text is gone after the transition. For native acquisition presentation,
confirm the real Card preview and relic top-bar animation; for `trial_noble`, its initial-page
placement and absence on the result page. An allowlisted shake must terminate and honor a disabled
setting. A forced follow-up cannot be proved by the `event` shortcut, which skips the forcing
behavior; if its real-Unknown driver cannot run, report Tier 1 only.
