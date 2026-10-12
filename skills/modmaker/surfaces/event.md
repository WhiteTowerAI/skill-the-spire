# Surface: event (World Node)

Everything the pipeline needs for one Event, in one place: the SPEC fields it must declare,
the element class the author writes, and the proof its verification owes. Read this page at
the `spec.md`, `author.md`, and `verify.md` stages when `element: event`.

One semantic Event with nested pages/options; scenario is `MapNode`; supported outcomes
include blocking selections/rewards and one resumable or terminal special combat per mutable
Event instance; normal portraits and the bounded `portrait_halo` profile plus bounded vanilla
description rich text are supported, while custom phobia art, arbitrary VFX, and
custom/Ancient scenes are not.


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
  - art source: runtime-imagegen | vofy | byo-http | local-image (generate only)
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
    save claim: game-unobserved
- **forced-follow-up boundary**: solo; finite acyclic custom sequence; unchanged neutral
  return; no vanilla edits, duplicate-token rewards, fixed map node, cross-Mod composition,
  multiplayer, or observed save-roundtrip claim
- **option presentation gaps**: <locked-option tips, normal-layout relic image, or none>
- **unsupported transitions**: merchant, rest site, and treasure room
- **adapter output** (written to MEMORY after acceptance): resolved Event logical id,
  flat localization key list, and framework diagnostic record
```

Each option id is stable semantic input; the adapter derives any method and localization
keys from it. If special combat exists, the spec also owns the custom monster + encounter
dependency from `surfaces/monster.md`; do not leave `<ENCOUNTER>` abstract.

## Shared lifecycle, state, and RNG route

Read `reference/lifecycle-state-rng.md` when an Event observes lifecycle outside its normal option
callback, owns state beyond the mutable Event model, persists included feature data, or makes a
gameplay-random choice. Prefer RNG supplied by the Event/Ancient/reward host; otherwise use one
stable Mod run/player stream at the authoritative resolution point.

Append the reference's game-term state/randomness block only when selected. Keep option behavior
and normal Event page state in this surface, validate all failure-prone choices before mutation,
await queued effects, and prove exact transition/order, neutral disabled/preview behavior,
deterministic replay, persistence/reset, and cleanup in `MapNode`. Do not use lifecycle observation
as cancellation or route deferred Progression, Telemetry, Settings, or Multiplayer behavior.

## Ordinary effect projection

An async Event option method supplies mutable run owner `Owner` only after the Event enters a run;
canonical models supply none. Read `reference/effect-primitives.md` for immediate Gold,
healing/HP, known run-content acquisition, and any other primitive whose exact inputs exist. The
bounded Event outcome route permits `ThrowingPlayerChoiceContext` for its documented HP/Max HP
commands, but it does not invent a combat target, combat piles, Energy/Stars, or Orb queue outside
a live combat-resume route. Preflight every cost/availability condition before the first mutation,
await the full sequence, inspect rejected acquisition results, and only then call
`SetEventFinished`, `SetEventState`, or enter/return from the selected special combat.

## Numbers the player reads should be declared values

The engine substitutes the Event's `DynamicVars` into every option title, option description,
and page description at render time. Vanilla depends on this: `TrashHeap` declares
`new HpLossVar(8m)` and `new GoldVar(100)`, and `SlipperyBridge` mutates
`DynamicVars["HpLoss"].BaseValue` as its HP cost escalates — one localization key serving
several different costs.

Write the number once as a declared value and reference it as a placeholder in the localized
text. A literal is acceptable only for a single fixed-cost option whose number appears in one
place. Prefer the declared value whenever:

- the cost or reward changes across pages or repeat visits;
- the same number appears in both the effect Cmd and the localized text, where they can
  silently diverge; or
- a `lethal warning` states a cost that must stay identical to the value the effect applies.

Record each one in `displayed values`.

## Author the element class

**Event / World Node** — create `<ModName>Code/Events/` and add `<Name>.cs` from
`recipes/event.md`:

- Extend `ModEventTemplate`; no `[Pool]`, constructor/manual registration, or second content
  pack. Use `.SharedEvent<T>()` for all-act placement or `.ActEvent<TAct,T>()` when scoped.
- Declare each SPEC `displayed value` in `CanonicalVars` (or compute it in `CalculateVars()`)
  and reference it as a placeholder in `events.json`, so text and effect share one source.
- For forced follow-ups, author the bounded mapping list exactly from
  `reference/forced-followup-event.md`: one unplayable Quest Card per mapping, Quest
  type/rarity, cost `-1`, no upgrades, bounded saved index, globally ordered priority, and
  the two public hooks guarded by the declared act set. Every sequence Event returns false
  from `IsAllowed`; do not place it in the ordinary Event pool. Source grants reject
  duplicates, and only the declared successful option advances or terminally removes the token.
- Ship flat `events.json` keys for the normalized Event entry, `INITIAL`, every explicit
  option key, and every result page. Use `InitialOptionKey`/`ModOptionKey`; callback method
  names do not mint localization keys.
- `GenerateInitialOptions()` returns the authored options. Each method uses the confirmed
  public Cmd/selection/reward vocabulary against `Owner`, awaits blocking overlays, logs
  the observed state delta, then follows SPEC with `SetEventFinished`, `SetEventState`, or
  one special-combat transition.
- If any option enters combat, author its monster + encounter dependency from
  `surfaces/monster.md`, set `IsShared => true`, and call
  `EnterCombatWithoutExitingEvent<TEncounter>(extraRewards, shouldResumeAfterCombat)`.
  A resumable branch overrides `Resume(AbstractRoom)` and restores its exact named page;
  a terminal branch proceeds to the map. Never emit a second combat from the same mutable
  Event instance or a direct merchant/rest/treasure room transition.
- Fill `EventAssetProfile.InitialPortraitPath` with the recipe's existence check: use the generated
  `images/events/<event-slug>.png` when present, otherwise the verified vanilla
  `this_or_that.png` fallback, and filter the missing convention-derived path from
  `GetAssetPaths`. For every explicitly requested page portrait, check
  `images/events/<event-slug>_<page-key-lower>.png` and call `NEventRoom.SetPortrait`
  immediately before the page transition; when absent, retain the current portrait. Clean
  owned portrait child nodes before a switch.
- When SPEC selects `portrait_halo`, emit the exact bounded helper from
  `reference/event-vfx.md`, attach page profiles through `OnRoomEnter`/the portrait host,
  honor Instant/Fast mode, and explicitly `QueueFreeSafely` every owned named root before
  page, portrait, combat, or finish transitions. Do not promote RitsuLib's arbitrary custom
  VFX/layout routes. Custom phobia
  art, arbitrary VFX, custom layouts, and Ancient background assets remain unsupported.
- Write every page and option string in the default style of
  `reference/vanilla-text-style.md`: option descriptions color costs `[red]`, heals and gains
  `[green]`, counts `[blue]`, and glossary terms and obtained Relic/Card names `[gold]`; pages
  are second-person narrative with paragraphs separated by `\n\n`; titles stay plain.
- When SPEC selects `extra atmosphere`, apply only the exact bounded tags from
  `reference/event-text-effects.md` around the named phrases in `events.json` page/option
  descriptions. Keep titles plain; emit no helper node or cleanup code.
- When an enabled option selects typed Hover Tips, pass the exact grounded
  `HoverTipFactory` values through `EventOption`; do not emit a locked-option workaround. For
  relic-backed presentation, use `CreateModRelicOption<T>` for native title/description/metadata and
  keep semantic acquisition in a separate awaited `RelicCmd.Obtain<T>`. Preserve the
  normal-layout relic image as a presentation gap rather than generating an Ancient Event.
- When a choice pays HP or Max HP, apply `ThatDoesDamage` or `ThatDecreasesMaxHp` to the
  generated option using the exact decimal cost used by its Cmd. The helper is warning-only,
  and its exact-cost boundary is inclusive; never substitute differently rounded values or
  warning-colored text.
- When a choice declares ordered acquisitions, await them in SPEC order. Pass each successful
  `CardPileCmd.Add` result to `CardCmd.PreviewCardPileAdd`; for each relic, emit exactly one
  awaited `RelicCmd.Obtain<T>`. Do not create duplicate models or custom preview holders.
- When SPEC selects `weak_short` or `strong_normal`, call only the matching allowlisted native
  strength/duration once after the named successful consequence and before its page transition.
  Never read or replace the player's multiplier.
- When SPEC selects `trial_noble`, emit the exact preloaded scene/portrait-host helper from
  `reference/event-native-presentation.md`, keep its vanilla `(292,68)` placement and
  inherited process mode, and `QueueFreeSafely` the owned named root before transitions.

Event mechanics route to `recipes/event.md`, full outcomes to
`reference/event-outcomes.md`, the optional halo to `reference/event-vfx.md`, and bounded
description style to `reference/vanilla-text-style.md`, extra atmospheric spans to
`reference/event-text-effects.md`. Enabled typed option tips, normal
relic-backed text/metadata, and exact HP/Max HP warnings route to
`reference/event-option-presentation.md`. A selected forced follow-up routes to
`reference/forced-followup-event.md`. Native Card/relic acquisition presentation,
allowlisted `weak_short`/`strong_normal` screen shake, and `trial_noble` route to
`reference/event-native-presentation.md`.

## Self-test driver body

**event** → the **`MapNode`** variant: enter the canonical custom event, then drive real
option UI. The focused body is in `reference/selftest-harness.md` § event.

## Proof matrix

- Require one real UI path per independent SPEC outcome family. Blocking card/reward overlays
  must finish before their post-state assertion.
- **Assert the option set before choosing.** The driver selects one option by exact title, so
  a `GenerateInitialOptions()` that produces fewer or more options than SPEC declares goes
  unnoticed. Assert that every declared option id is present on its page, with its declared
  enabled/locked state, before driving any of them.
- **Drive each gated option both ways.** For any option whose `availability` is gated, prove
  the locked state as well as the enabled one by changing the real run-state condition — the
  same standard a monster's conditional branch is held to. A predicate that never gates
  correctly otherwise passes.
- A special combat must identify the custom encounter and prove exactly one authored
  completion path: named `Resume` page or direct map. Use a fresh Event instance if SPEC
  independently exercises both forms; never start two combats from one mutable Event.
- The final structured marker lists identical expected/observed outcome families.

## Manual fallback (only when the harness cannot reach its scenario)

Grant it:

   - **event:** `event <PREFIX>-<SLUG>` enters the custom event (**exact** match; run in
     progress). Confirm the localized option appears before choosing it.

Trigger it:

   **event** → choose the specified options and confirm each exact Cmd/selection/reward
   consequence. For special combat, confirm the requested custom encounter and then the
   named return page or direct map. For `portrait_halo`, visually inspect configured pages
   and confirm no stale overlay survives a page switch or combat entry. For vanilla Event
   text effects, inspect the named colored/moving phrase on each authored page and confirm
   the prior page's text is gone after the transition.
   For native acquisition presentation, confirm the real Card preview and relic top-bar
   animation, and for `trial_noble` confirm its exact initial-page placement and absence on
   the result page. An allowlisted shake must terminate and must honor a disabled setting.
   A forced follow-up cannot be proved by the `event` console shortcut; if its automated
   real-Unknown driver cannot run, report Tier 1 rather than claiming the hook behavior.
