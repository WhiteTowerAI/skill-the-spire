# Surface: relic

Everything the pipeline needs for one Relic, in one place: the SPEC fields it must
declare, the element class the author writes, and the proof its verification owes. Read
this page at the `spec.md`, `author.md`, and `verify.md` stages when `surface: relic`.

Shared declarations live in their own references: bounded state in
`reference/stateful-mechanics.md`, hook participation in `reference/model-hook-participation.md`,
and art in `reference/art-contract.md`. Shared proof machinery stays in `verify.md`.

## SPEC fields

```markdown
# SPEC — <Mod Name>

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
  - languages: [eng, zhs]
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
- **hook participation**: none | one or more; see `reference/model-hook-participation.md`
  - A Relic reaches the widest set (66 of 68): both run-scope and combat-scope. `Owner` is a
    `Player`, so a subject guard compares against `Owner.Creature` **and** `Owner.Osty` where
    an Osty can act. Rest Site contribution is not declared here — see § SPEC fields above.
- **state**: none | see `reference/stateful-mechanics.md`
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

When a Relic contributes a Rest Site action, add this block to the same Relic SPEC. The shared
route also supports standalone, exactly-one Card, and selected Modifier owners through their own
surface pages:

```markdown
- **owned Rest Site option**:
  - owner: relic
  - owner multiplicity: exactly one
  - state handle: host visit removal | saved owner bool
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

## Shared capability routes

Read `reference/model-capabilities.md` for separable behavior/state attached to this Relic,
`reference/lifecycle-state-rng.md` when it crosses callbacks, run/save/profile boundaries, or uses
gameplay RNG, and `reference/shared-effect-hooks.md` for reachable per-hit attack, healing,
Energy/Stars-gain response, or maximum-hand-size behavior. The Relic or its typed capability
remains the owner across its declared run/combat reachability.

Keep native trigger effects in `effects.sequence`. Append a shared-route SPEC block only for the
independent capability/service behavior, preserving cadence, phase/order, subject guard, neutral
case, persistence/reset, display refresh, and exact real-host assertions. Do not register a
process-wide listener for a Relic-owned rule.

## Ordinary effect projection

Choose the exact async Relic hook whose phase matches SPEC; the hook parameters provide its live
combat state, participant/subject, Card, or other trigger context. The mutable Relic supplies owner
Player `Owner` and owner Creature `Owner.Creature`, but it supplies no Card source and no general
`PlayerChoiceContext`. Read `reference/effect-primitives.md` and use only primitives whose inputs
the selected hook actually has. Resource gain, self Block/heal, and known combat-Card creation can
bind to `Owner` in a live combat hook; a target-dependent Power, draw/discard, Orb action, or Max
HP loss blocks unless that hook truthfully supplies its required context/target. Never manufacture
a `PlayerChoiceContext` merely because the Relic is in combat.

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
- For selected bounded state, follow `reference/stateful-mechanics.md`.
  A Relic run-save profile may use `SavedAttachedState<SpecificRelic, bool/int/string>`;
  combat-local native-turn timing may read `PlayerCombatState.TurnNumber`. Emit only declared
  transitions/consumers, and route every visible mutation through one refresh path.
- For a Rest Site action on this Relic, author one separate `ModRestSiteOptionTemplate` and
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

A Relic selecting the historical cadence profile uses that reference's multi-combat variant.
Other bounded-state profiles derive only their selected transition/reset/persistence checks.

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
- **For hook participation — assert the neutral case outside the guard.** The modified value
  alone passes for a Relic that modifies *every* event of that kind, which is a different relic
  from the declared one and usually a run-breaking one. Drive one event the guard should ignore
  and assert the host's value is unchanged. A `Player`-owned guard needs the Osty case too when
  the design says the Osty counts. For a collection edit, also assert that an entry placed in
  the list beforehand survives — vanilla `Midas` rebuilds the whole reward list, and an editor
  that clears it still passes "my entry is present".
- A Relic with bounded state owes only the selected transition/reset/persistence boundary;
  a run-save profile additionally owes its real save/fill round trip.
- For a Rest Site option on this Relic, follow `reference/rest-site-options.md`: require the
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
