# Surface: relic

Everything the pipeline needs for one Relic, in one place: the SPEC envelope it must
declare, the element class the author writes, and the proof its verification owes. Read
this page at the `spec.md`, `author.md`, and `verify.md` stages when `surface: relic`.

Shared declarations that several surfaces use — stateful mechanics, interaction contracts,
the art plan — stay in `spec.md`. Shared proof machinery stays in `verify.md`.

## SPEC envelope

```markdown
# SPEC — <Mod Name>

- **contract**: sts2-content-semantic/v1
- **mod id**: <stable mod identity>
- **author**: <author>
- **content**:
  - name: <shown name>
  - surface: relic
  - logical id: <stable local stem, e.g. gamblers_coin>
  - rarity: Common | Uncommon | Rare | Shop | Event | Ancient | Starter
- **registration**:
  - availability: shared | character:<name>
  - ownership: player
  - placement: <plain-language drop/pool rule>
- **localization**:
  - fields: title=<shown name>; description=<hover text>; flavor=<flavor line>
  - formatting: plain | bounded vanilla rich text
  - text spans: <description phrase -> semantic color intent>
  - displayed values: none | <value name -> declared scaling name; literal or placeholder>
- **effects**:
  - trigger: <plain-language event and boundary, e.g. start of combat>
  - cadence: once per combat | once per turn | every trigger | once per run
  - target: owner
  - sequence: <ordered game-term effect with exact values>
  - scaling: <named values and bounds, or none>
- **state**: none | see the stateful-mechanic contract below
- **presentation**:
  - assets: relic icon; placeholder | generate
  - art source: runtime-imagegen | vofy | byo-http | local-image (generate only)
  - native presentation: standard relic display
  - keyword tips: none | <native or mod keyword named in the description>
  - extra badges: none | one to three
    - meaning: <player-facing auxiliary value, e.g. charges remaining>
      value: <state value or bounded display rule>
      corner: top-left | top-right | bottom-left (one label per corner)
      format: plain | bounded color rich text; at most 4 visible characters
      refresh: <state change that updates it>
      remove: <condition that hides/removes it>
- **fallback**:
  - missing asset: checked template relic icon
  - unavailable seam: preserve behavior or stop with an explicit unsupported boundary
- **proof**:
  - scenario: CombatPlayer
  - driver: <real trigger, e.g. enter combat>
  - invariants: <exact expected/observed state plus visible trigger>
  - cadence case: <the observation that separates the declared cadence from every-trigger;
    required whenever cadence is not "every trigger">
  - boundary cases: <owner guard/reset/save cases, or none>
- **adapter output** (written to MEMORY after acceptance): resolved content id,
  localization keys, asset profile, and framework diagnostic record
```

`cadence` and the matching cadence case are mandatory, not optional detail. They exist
because the trigger hook a Relic overrides usually fires more often than the design wants,
so the guard is the Relic's identity — see § Proof matrix.

When a Relic contributes a Rest Site action, add this block to the same Relic SPEC. The
current slice does not accept a Card or Modifier owner:

```markdown
- **owned Rest Site option**:
  - owner: relic
  - title: <localized button title>
  - description: <localized hover description>
  - eligibility: <when the owned relic contributes the option>
  - repeatability: once per Rest Site | once per run
  - enabled rule: always | can pay fixed Gold cost
  - cost: free | <nonnegative integer> Gold
  - outcome: <ordered deterministic game-term operations and exact values>
  - after success: leave | keep remaining options available
  - icon: checked native fallback | generate
  - multiplayer: singleplayer only
  - proof: absent owner; present disabled/enabled; stale-render failed payment with no
    mutation; exact successful cost/outcome/history; no duplicate; stay/leave; second visit;
    custom icon and missing-icon fallback
```

Absence and disabled are separate. `eligibility` controls contribution; `enabled rule`
controls the native gray/clickable state. A fixed-Gold outcome must be completely
preflightable before its first mutation. Stop authoring for a post-payment selection,
random branch, or other result that would require rollback.

## Displayed values the engine keeps current

`RelicModel` runs SmartFormat/DynamicVar substitution over the description and its Hover
Tip, so a value declared in `CanonicalVars` renders live and in native `[blue]` presentation.
Vanilla relies on this: `WingedBoots` declares `new DynamicVar("Rooms", 3m)` and its
localized description reads `… [blue]{Rooms}[/blue] times.`

A literal number in the localized text is acceptable **only** when the value can never
change and appears in exactly one place. Declare a scaling name and use a `{Placeholder}`
whenever either is false:

- the value is modified at runtime, or by upgrade, save state, or another element;
- the same number also appears in the effect code, where the two can silently diverge; or
- the design intends the native colored presentation vanilla uses.

Record the choice in `localization.displayed values` so the decision is reviewable rather
than accidental.

## Keyword tips are not automatic here

Unlike a Card, a Relic gets no keyword tooltip from naming a keyword in its description.
`ModRelicTemplate` surfaces tips only through its explicitly declared `RegisteredKeywordIds`
and `AdditionalHoverTips`. If the description names a native or mod keyword, declare it in
`presentation.keyword tips` and register it, or the player reads a term with nothing to
hover.

## Author the element class

**Relic** — add `<ModName>Code/Relics/<RelicName>.cs`. Use the recipe skeleton, then:

- Set `Rarity` from SPEC.
- Extend `ModRelicTemplate` and add exactly one `.Relic<TPool,TRelic>()` step to
  `MainFile.Content.cs`. The content-pack pool generic is the availability contract.
- Override the hook matching SPEC's trigger (recipe's "Trigger hooks" table). For
  combat-start: `AfterSideTurnStart` + `participants.Contains(Owner.Creature)` +
  `Owner.PlayerCombatState!.TurnNumber <= 1` guards. That last guard **is** the declared
  cadence; the hook fires every turn without it.
- Declare a SPEC displayed value in `CanonicalVars` and reference it as a placeholder in the
  localized text; use a literal only under § Displayed values the engine keeps current.
- Declare every keyword named in the description through `RegisteredKeywordIds`.
- Fill **only** the effect block with the confirmed Cmds/RNG from the recipe. `await`
  every Cmd. Use `Rng`, never `System.Random`. Call `Flash()` when it visibly triggers.
- For stateful relics, follow `reference/stateful-mechanics.md`: run-lifetime progress is
  a `SavedAttachedState<SpecificRelic, int/bool>` whose name includes the Mod id and is
  never cleared at combat end; combat-local fixed/periodic turns read
  `PlayerCombatState.TurnNumber`. Any visible mutation calls
  `InvokeDisplayAmountChanged()` after updating the attached value.
- For a Relic-owned Rest Site action, author one separate `ModRestSiteOptionTemplate` and
  contribute it through the owner's `TryModifyRestSiteOptions`. Separate `ShouldOffer`
  from `CanPay`, reject duplicate `OptionId`, share `CanPay` between `IsEnabled` and the
  first line of `OnSelect`, and mutate repeatability only after the awaited deterministic
  outcome. Resolve missing custom art to the native Heal option image explicitly.
- For extra badges, implement `IRelicExtraIconAmountLabelSpecsProvider`; return only active
  bounded specs in SPEC order, never exceeding three distinct safe corners, and add
  `IRelicExtraIconAmountLabelsChangeSource` only when the label state changes without
  `InvokeDisplayAmountChanged()`.

## Self-test driver body

**relic** → `BeforeCombat` (grant it, its `AfterSideTurnStart` fires on its own);

The focused body is in `reference/selftest-harness.md` § relic: grant the relic in
`BeforeCombat` before `EnterRoomDebug`, then assert SPEC state in `InCombat`.

A **stateful relic** uses that reference's multi-combat cadence variant instead, which
already asserts `N-1`, threshold, and reset/carry-over across combats.

## Proof matrix

- Assert the declared effect's exact expected/observed state plus its visible trigger.
- **Assert the cadence.** The `InCombat` assertion alone runs inside turn 1, so it cannot
  distinguish "once per combat" from "every turn": deleting the `TurnNumber <= 1` guard
  still passes it. Whenever `cadence` is not `every trigger`, advance past the boundary and
  assert the value did **not** change again — one more turn for a per-combat relic, a second
  combat for a per-run relic. A relic declaring `every trigger` records that and needs no
  extra case.
- **Assert each declared keyword tip resolves.** A Relic gets no tooltip from merely naming a
  keyword, so a description naming one without a matching `RegisteredKeywordIds` entry leaves
  the player hovering a term with nothing behind it. No effect assertion observes that. Assert
  the registered id is present and its title/description resolve to shipped localization rather
  than a raw key.
- **Assert each declared displayed value renders live.** A value declared in
  `localization.displayed values` must reach the real description through substitution. Assert
  the rendered text contains the current value, not the placeholder token and not a stale
  literal — an unresolved `{Placeholder}` and a diverged hardcoded number both pass every
  state assertion.
- A stateful relic additionally owes the reset/carry-over and save round trip from
  `reference/stateful-mechanics.md`.
- For a Relic-owned Rest Site option, follow `reference/rest-site-options.md`: require the
  real native room, absent/disabled/enabled states, final click-time payment rejection with
  no deltas, exact successful Gold/outcome/history deltas, no duplicate after rebuild,
  declared stay/leave and second-visit repeatability, explicit singleplayer mode, custom
  icon, and missing-icon native fallback. Model-generated option lists are diagnostics,
  not hosted proof.

## Manual fallback (only when the harness cannot reach its scenario)

Grant it:

   - **relic:** `relic add <PREFIX>-<SLUG>` (`add` is default; matching is substring `Contains`).

Trigger it:

   **relic** → enter a combat. For a non-`every trigger` cadence, end the turn and confirm
   the effect did not fire again.
