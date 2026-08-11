# Framework-neutral semantic contract

This file is the source-of-truth for the product-level `SPEC.md` envelope. `DESIGN.md` owns
creative intent and scope; SPEC owns only the exact current generation contract. It is
intentionally free of framework class names, namespaces, hook signatures, project
files, manifest fields, or resource-loader conventions. A SPEC describes what the
player should experience; an adapter decides how that intent is registered and
implemented.

## Contract identity

Every generated SPEC uses:

```text
contract: sts2-content-semantic/v2
host intent: Slay the Spire 2 stable 0.107.1
```

The contract version is independent of the game version and framework version. A
change to this envelope requires a contract-version bump and a migration note.

**Migration from v1.** The six surfaces that used a flat `- **element**: <slug>` opening
with ad-hoc top-level keys (potion, power, orb, monster, event, character) now use the same
canonical nested form as card and relic. A project SPEC written under v1 is still readable
and resumes unchanged under its own terms; only new or revised SPECs are written as v2. An
absent `contract:` line or a `sts2-content-semantic/v1` declaration signals a pre-v2 project;
resume it from its existing artifacts without rewriting the envelope.

**What changed in v2.** The nine shared section names (`content`, `registration`,
`localization`, `effects`, `state`, `presentation`, `fallback`, `proof`, and `adapter output`)
are the same for all surfaces. Surface-specific fields live inside these sections rather than
replacing them. The `element:` key is replaced by `content.surface`. `derived ids` is renamed
`adapter output` and moves to the end of each envelope, consistent across all surfaces. The
`observe:` key (used by monster, event, and character in v1) is replaced by `proof.invariants`,
consistent with card, relic, potion, power, and orb. Starting HP and energy per turn moved
from loose top-level keys into `content:` on the character surface. The capability-module,
character resource, and ordered semantic buffer blocks moved from `spec.md` into
`surfaces/character.md`, closing M8.0 mismatch 7.

## Canonical envelope

Include these sections once per SPEC. Surface-specific blocks may add fields, but must
not replace or rename the shared sections.

Before this envelope, include the `open-mod-spec-trace/v1` block from `spec.md`. Every
emitted semantic operation appears once with a stable `OP-###`, one or more current
`D-###` requirements, its semantic target, and its shipped supported route. The trace is a
generation allowlist: deferred/out-of-scope design items never appear in this envelope.

```markdown
- **contract**: sts2-content-semantic/v2
- **content**:
  - name: <player-facing name>
    surface: card | relic | potion | power | keyword | enchantment | orb |
    custom card pile | enemy encounter | event | character | vanilla model override
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

`keyword` and `enchantment` are contract surface identities for adapter routing and keep their
own Surface-inputs rows below, but neither is standalone content: a keyword owns shared
vocabulary whose named behavior lives in a host element, and an enchantment is always attached
to a host Card. Both are therefore declared as nested blocks inside their host Card's
`content:` section rather than as their own top-level block. `orb` is real content with its own
identity and slot lifecycle, so it keeps a full block even though every one of its behaviors
runs through a host. See `surfaces/keyword.md`, `surfaces/enchantment.md`, and
`surfaces/orb.md`.

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

An existing vanilla model override starts with exact target resolution from
`reference/vanilla-overrides.md` and records the user's target name, exact resolved model
identity, untouched-surface preservation, and ordered semantic operations. Each operation
states adjust/compose/replace/availability/visual intent, the player-facing surface and
desired result, expected current behavior, upgrade/localization effect, timing, multiplayer
scope, and compatibility criticality. The adapter owns the catalog digest, concrete type,
baseline subset, public route id, capability identity, and manifest encoding. A prompt never
provides a method name or implementation body. The override routes permit the non-asset Card surfaces
in `reference/vanilla-card-overrides.md`. They permit every visual surface in the
44-provider `reference/vanilla-visual-overrides.md` matrix. A visual operation additionally
records the player-facing resource role, generate-versus-local authoring intent, whether it
is required, and exact vanilla fallback; paths and Godot types remain adapter output. An
exact existing Ancient may use the initial-option append or complete replacement
routes in `reference/vanilla-ancient-overrides.md`. Record append/replace intent, rule
condition/priority/dedup behavior, every ordered option and reachable page, visible/enabled
conditions, one fixed cost, typed hover/relic presentation, ordered consequences, and each
stay/page/finish edge. Preserve the original Ancient model, room, opening dialogue, save
identity, allowance gate, and native finish history. They permit pinned availability
operations in `reference/vanilla-availability-overrides.md`: public epoch requirements for
Cards, Characters, ordinary Events, and shared Darv; Relic/Potion epoch filters; and
Card/Relic/Potion pool add/remove/move. Record the full source membership baseline,
singleplayer/preserve-instance scope, fixed Adapter dependencies, and simulated primary
pool after each ordered transition. Do not turn weighting, act-owned Ancient filtering,
permanent Card/Character/Event disable, or multiplayer into an invented route. Non-Card data/behavior overrides
permits the exact non-Card matrix in `reference/vanilla-non-card-overrides.md`: public
owner-hook composition/replacement for Relic, Potion, Power, Orb, Enchantment, Affliction,
and Monster; checked intrinsic data; and complete lifecycle, Monster move, Encounter roster,
or ordinary Event option/page replacement. Record exact trigger/scope/order, final data,
or the whole replacement graph and preserve untouched wrappers/identity. An operation
outside these five Packages remains an explicit gap rather than a partial edit.

The adapter must preserve the user's operation mode; it cannot turn `replace` into
`compose` to fit an available route. In particular, replacing, removing, or hiding a
vanilla Card's original description is a base-description replacement and is unsupported
by the pinned RitsuLib `0.5.4` Package. Stop and obtain explicit acceptance of a
before/after fragment alternative before changing the semantic intent. Finalized values or
an instruction not to repeat questions never authorizes a different player-facing result.

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

The Custom Card Piles Package is a Mod-level surface. Record every pile's local identity,
combat/run scope, headless/top-bar/bottom-left/bottom-right/ExtraHand style, default/preset/
custom anchor, icon and hover behavior, visibility, open/view/hotkey behavior, every
explicit Card movement, localization, and state transition. ExtraHand declarations also
record layout, manual-play/glow behavior, and requested visual callbacks. The adapter owns
qualified IDs, `PileType` values, public registration, native pile commands, persistence,
and UI wiring; framework names and raw callbacks never enter SPEC.

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
| Custom card pile | identity, combat/run scope, UI style/anchor, open/view/visibility/hotkeys, movement/order, localization, optional ExtraHand behavior | matching combat/run/card-pile UI host |
| Enemy encounter | HP, group, ordered moves, conditions, encounter placement | `CombatEnemy` |
| Event | acts, pages/options, public outcomes, bounded presentation, combat completion | `MapNode` |
| Character | identity, HP, starter content, pools, hosted mechanic, selected static profiles | `RunStart` + `CombatPlayer` |
| Character combat cues | enabled/disabled fixed Idle/Attack/Hit/Dead contract, shared footprint/anchors, static fallback | `RunStart` + `CombatPlayer` |
| Character combat resource | name, gain/spend/payoff, nonnegative domain, combat reset, fixed UI/fallback | two-combat Character / `CombatPlayer` |
| Ordered semantic buffer | value/order, capacity/overflow, normal source destination, formula/output | two-combat Character / `CombatPlayer` |
| Character Ancient dialogue | cataloged natural target, first/explicit/repeat visit, ordered speaker/text/prompts, Architect attackers | native Ancient + production Architect |
| Card Scry helper | top-X amount, discard-any choice, upgrade delta, singleplayer boundary | `CombatPlayer` with visible native selector |
| Advanced creature targeting | consumer, one/many mode, stable Mod-local target id, declarative live-Creature predicate, zero-target lifecycle | `CombatPlayer` plus headed mouse/controller targeting |
| Existing vanilla model override | exact resolved identity, ordered operation intent, preserved surfaces; visual role/source/requirement/fallback when selected | nearest real consumer for each promoted operation; deferred during source development |
| Existing Ancient initial options | append or complete replacement; rule condition/priority/dedup; ordered options/pages; visibility/lock/cost/tips/relic/effects; stay/page/finish graph | native Ancient room and choice-history lifecycle; deferred during source development |

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

The first compile profile is `ritsulib-0.5.4-sts2-0.107.1`. The actual runtime may be a
newer RitsuLib release when it retains the checked `0.107.1` compat variant. There is no
fallback to the historical framework and no beta-facing variant selection. If the profile
cannot be resolved, authoring stops with an actionable diagnostic and the
placeholder/fallback remains the documented outcome.

## Diagnostic envelope

Build, load, and Tier-2 records use the same fields. The existing exact load marker is
retained so current verification tools remain compatible.

```text
[OPENMOD-FRAMEWORK] phase=<build|load|tier2> mod=<mod-id> framework=RitsuLib frameworkVersion=<actual-loaded-version> host=0.107.1 compat=0.107.1 adapter=<surface>/<contract-version> status=<selected|resolved|fallback|failed>
[T2MOD-SELFTEST] <ModName> loaded ok
[T2MOD-SELFTEST] <ModName> state proof: framework=RitsuLib frameworkVersion=<actual-loaded-version> host=0.107.1 compat=0.107.1 expected=<...> observed=<...>
```

`status=failed` must include a short reason such as `missing-compat-asset` or
`host-mismatch`. A framework marker never substitutes for a concrete state proof.

## Simple gate examples

The following two semantic descriptions are compact v1-era examples retained for
illustration: they show a complete, framework-free description. Real generated SPECs use the
v2 nested envelope from the surface pages. The contract line here marks these as pre-v2
sketches, not current output.

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
