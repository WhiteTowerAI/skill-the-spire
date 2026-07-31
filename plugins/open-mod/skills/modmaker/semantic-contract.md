# Framework-neutral semantic contract

This file is the source-of-truth for the product-level `SPEC.md` envelope. It is
intentionally free of framework class names, namespaces, hook signatures, project
files, manifest fields, or resource-loader conventions. A SPEC describes what the
player should experience; an adapter decides how that intent is registered and
implemented.

## Contract identity

Every generated SPEC uses:

```text
contract: sts2-content-semantic/v1
host intent: Slay the Spire 2 stable 0.107.1
```

The contract version is independent of the game version and framework version. A
change to this envelope requires a contract-version bump and a migration note.

## Canonical envelope

Include these sections once per SPEC. Surface-specific blocks may add fields, but must
not replace or rename the shared sections.

```markdown
- **contract**: sts2-content-semantic/v1
- **content**:
  - name: <player-facing name>
    surface: card | relic | potion | power | keyword | enchantment | orb |
      enemy encounter | event | character
    logical id: <stable local stem, before adapter-specific id decoration>
    relations: <none | directed source -> dependent relationships>
- **registration**:
  - availability: shared | character:<name> | act:<name> | standalone | host-owned
  - ownership: player | enemy | room | run | combat
  - placement: <plain-language pool/act/room rule>
- **localization**:
  - fields: <title/description/flavor/prompt/name/etc.>
  - table intent: <cards/relics/... or in-code event/character text>
  - key rule: adapter derives stable content keys from logical id; SPEC records the
    resulting keys only after the adapter resolves them
  - formatting: plain | bounded vanilla rich text | SmartFormat values
  - variable tooltips: <none or value name -> localized title/description and optional icon>
- **effects**:
  - trigger: <play/use/turn/room/run/selection/encounter move>
  - target: <self/one enemy/all enemies/owner/room>
  - sequence: <ordered game-term operations and exact values>
  - scaling: <named values, upgrade deltas, and bounds>
  - calculated values: <none or named role/formula/inputs/integer domain/upgrade behavior/
    evaluation point>
- **state**:
  - lifetime: none | turn | combat | run
  - owner: <real content node or player state that owns it>
  - advance/check: <event and threshold order>
  - reset: <exact boundary>
  - persistence: none | ordinary | run save
  - visible state: <hidden or the exact player-readable summary>
- **presentation**:
  - assets: <consumer-specific profile or none>
  - text effects: <bounded semantic spans, never raw markup>
  - native presentation: <none or named supported consumer>
  - readability aids: <none or optional hand-emphasis / extra-badge semantic blocks>
- **fallback**:
  - missing asset: <checked built-in/placeholder behavior>
  - unavailable seam: <unchanged behavior or explicit unsupported boundary>
  - failure policy: <fail clearly, preserve fallback, or stop authoring>
- **proof**:
  - scenario: <CombatPlayer | CombatEnemy | MapNode | RunStart + Character | ...>
  - driver: <real source interaction>
  - invariants: <exact expected post-state and visible consumer>
  - boundary cases: <reset, save, zero/short/full, branch, or unsupported case>
```

The `effects`, `state`, and `proof` sections are semantic. For example, “at the
start of combat, double current energy” is valid; a particular method name is not.
Likewise, “shared relic pool” is valid; a pool attribute or registration call is
adapter detail.

Official RitsuLib tutorials are a product-semantics baseline. They may establish what a
feature Package communicates to the player and which public consumers belong to it. Exact
versioned symbols still come from the pinned adapter. Support and known limitations follow
`sts2-api/grounding.md`; they are never questions for the user and never semantic fields in
SPEC.

A calculated Card value is semantic data, not an implementation expression. It records
one deterministic formula, all live inputs, an integer domain, base/upgrade behavior, and
whether the intended state is observed before the Card plays or after its normal payment
and move. The same declared calculation owns the displayed value and effect request. If
those phases cannot observe equivalent state, authoring stops instead of keeping a second
display-only formula. Damage, Block, Energy icons, Star icons, raw typed Power, and applied
typed Power remain distinct roles because their normal game modifiers differ.

Advanced creature targeting is an optional Card/Potion surface extension. Keep it in
player-facing terms and add one declaration with `consumer: card | potion`, `mode: one |
many`, a stable local target id, candidate conditions, acting-player conditions, optional
single-source conditions, zero-target behavior, and exact resolution semantics. The
adapter owns the dynamic enum and predicate APIs. Under the pinned profile, `potion + many`
is a known lifecycle limitation rather than a semantic fallback.

A Relic-owned Rest Site option is an optional Relic surface extension. Record the
localized title/description, owner, eligibility, repeatability, enabled rule, fixed Gold
cost, deterministic outcome, after-success behavior, optional icon, and singleplayer
boundary. Eligibility controls absence; affordability controls visible-but-disabled state.
The adapter owns the option class, contribution hook, stable option ID, saved run-use state,
and native UI lifecycle. Card/Modifier owners and arbitrary transactional outcomes are
unsupported adapter results in the first slice.

Gameplay readability uses two optional presentation extensions:

- **hand emphasis:** record one or more ordered rules. Each rule owns an actionable
  player-facing meaning, activation condition, semantic color (`gold`, `red`, or a
  requested custom color), integer priority, and whether it remains visible while the Card
  is unplayable. Highest active priority wins; ties use the later listed rule. Never put
  predicates, registry calls, polling, or framework color objects in SPEC.
- **extra badge:** record up to three Relic labels in distinct top-left/top-right/bottom-left
  corners, or one top-left Power label. Each has one auxiliary meaning, bounded
  value/formatter, plain/bounded-color intent, refresh event, and removal condition. Relic
  text is at most 4 visible characters and Power text at most 6. It supplements rather than
  replaces the native main amount; raw markup, arbitrary rectangles, and bottom-right
  authoring are not semantic inputs.

The public Extra Badges Package also includes Intent. Its official meaning is auxiliary
same-intent information such as additional triggered hits. Intent recipe work is not in the
current pipeline scope, so normal generated SPEC intake exposes only Relic and Power badge
blocks. A separate debuff/effect remains a separate native intent, and an ordinary repeated
identical attack remains a native multi-attack intent.

A combat-only visible Card pile is an optional cross-surface capability. Record one stable
local name, local-Player/combat ownership, explicit entry and non-play exit triggers,
Top/Bottom insertion, a positive capacity with non-destructive overflow, repeated-model
policy, visible empty state, manual-play choice, normal successful result pile, fixed
compact above-Hand layout intent, native-Hand-only numbered shortcuts, and singleplayer
boundary. The adapter owns the qualified pile ID,
native holders, temporary backend-Hand bridge, cancellation restoration, and combat cleanup.
This is distinct from an ordered semantic record: it stores explicitly moved Card instances
but never intercepts an already played source Card or changes unrelated result piles.

## Surface inputs

These are the only surface-specific inputs the adapter needs from a normal SPEC:

| Surface | Semantic inputs | Current proof route |
|---|---|---|
| Card | cost, kind, rarity, target, scaling values, optional calculated value contract, upgrade deltas, effect sequence | `CombatPlayer` |
| Card hand emphasis | ordered actionable rules, conditions, semantic colors, priority/tie order, unplayable visibility | `CombatPlayer` plus headed hand review |
| Relic | rarity, availability, trigger, owner guard, effect sequence, state contract | `CombatPlayer` |
| Relic-owned Rest Site option | title/description, eligibility, repeatability, enabled rule, free/fixed Gold cost, deterministic outcome, stay/leave, optional icon, singleplayer boundary | real Rest Site / `MapNode` |
| Potion | rarity, usage window, target, effect sequence | `CombatPlayer` |
| Power | buff/debuff, stack domain, trigger, amount mutation, display fields | `CombatPlayer` |
| Relic/Power extra badge | host, Relic up to three distinct safe-corner values or Power one top-left value, format intent, refresh/removal | matching real Relic/Power consumer plus headed review |
| Keyword | shared rule, host cards, display title/description, behavior proof | `CombatPlayer` |
| Enchantment | compatible host, persistent change, display/icon fallback | `CombatPlayer` |
| Orb | channel host, passive, evoke, icon and combat fallback | `CombatPlayer` |
| Enemy encounter | HP, group, ordered moves, conditions, encounter placement | `CombatEnemy` |
| Event | acts, pages/options, public outcomes, bounded presentation, combat completion | `MapNode` |
| Character | identity, HP, starter content, pools, hosted mechanic, selected static profiles | `RunStart` + `CombatPlayer` |
| Character combat cues | enabled/disabled fixed Idle/Attack/Hit/Dead contract, shared footprint/anchors, static fallback | `RunStart` + `CombatPlayer` |
| Character combat resource | name, gain/spend/payoff, nonnegative domain, combat reset, fixed UI/fallback | two-combat Character / `CombatPlayer` |
| Ordered semantic buffer | value/order, capacity/overflow, normal source destination, formula/output | two-combat Character / `CombatPlayer` |
| Combat-only visible Card pile | name/text, explicit entry/exit and Top/Bottom order, capacity/overflow, repeated-model rule, manual play, fixed layout, normal result pile | two-combat `CombatPlayer` plus headed interaction/layout review |
| Character Ancient dialogue | cataloged natural target, first/explicit/repeat visit, ordered speaker/text/prompts, Architect attackers | native Ancient + production Architect |
| Card Scry helper | top-X amount, discard-any choice, upgrade delta, singleplayer boundary | `CombatPlayer` with visible native selector |
| Advanced creature targeting | consumer, one/many mode, stable Mod-local target id, declarative live-Creature predicate, zero-target lifecycle | `CombatPlayer` plus headed mouse/controller targeting |

The adapter may require additional technical inputs internally, but those belong in
the selected adapter reference and generated source, never in the semantic fields.

## Adapter boundary

The adapter is selected after the semantic SPEC is frozen. It consumes the envelope and
returns four implementation records:

1. **registration plan** - template/base choice, pool or standalone registration,
   lifecycle subscriptions, and any selected public host seam;
2. **localization and assets** - resolved content keys, asset profile, exact dimensions,
   and checked fallback;
3. **diagnostics** - framework/compat/host identity and adapter status;
4. **proof route** - the closest hosted suite and the structured invariant it must emit.

The first target profile is `ritsulib-0.4.67-sts2-0.107.1`. There is no compatibility
fallback to the historical framework and no beta-facing variant selection. If the
profile cannot be resolved, authoring stops with an actionable diagnostic and the
placeholder/fallback remains the documented outcome.

## Diagnostic envelope

Build, load, and Tier-2 records use the same fields. The existing exact load marker is
retained so current verification tools remain compatible.

```text
[OPENMOD-FRAMEWORK] phase=<build|load|tier2> mod=<mod-id> framework=RitsuLib frameworkVersion=0.4.67 host=0.107.1 compat=0.107.1 adapter=<surface>/<contract-version> status=<selected|resolved|fallback|failed>
[T2MOD-SELFTEST] <ModName> loaded ok
[T2MOD-SELFTEST] <ModName> state proof: framework=RitsuLib frameworkVersion=0.4.67 host=0.107.1 compat=0.107.1 expected=<...> observed=<...>
```

`status=failed` must include a short reason such as `missing-compat-asset` or
`host-mismatch`. A framework marker never substitutes for a concrete state proof.

## Simple gate examples

The following two semantic descriptions are complete and contain no
framework vocabulary. The RitsuLib adapter reference maps them to implementation data.

```markdown
# SPEC - Ember Coin
- contract: sts2-content-semantic/v1
- content: surface=relic; logical id=ember_coin
- registration: availability=shared; ownership=player; placement=any character
- localization: fields=title,description,flavor; formatting=plain
- effects: trigger=start of combat; target=owner; sequence=double current energy
- state: lifetime=none
- presentation: assets=relic icon; native presentation=none
- fallback: missing asset=template relic icon; unavailable seam=unchanged effect
- proof: scenario=CombatPlayer; driver=enter combat; invariants=energy doubles on turn 1
```

```markdown
# SPEC - Ember Strike
- contract: sts2-content-semantic/v1
- content: surface=card; logical id=ember_strike
- registration: availability=shared; ownership=player; placement=any character
- localization: fields=title,description; formatting=SmartFormat values
- effects: trigger=play; target=one enemy; sequence=deal 6 damage
- state: lifetime=none
- presentation: assets=card portrait; native presentation=none
- fallback: missing asset=template card portrait; unavailable seam=unchanged effect
- proof: scenario=CombatPlayer; driver=play the card; invariants=target loses 6 HP
```

The adapter may add resolved ids, code symbols, or asset paths to `MEMORY.md` after
selection. Those derived values are implementation records, not semantic input.
