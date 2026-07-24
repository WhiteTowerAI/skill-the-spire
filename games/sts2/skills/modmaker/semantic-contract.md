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
- **effects**:
  - trigger: <play/use/turn/room/run/selection/encounter move>
  - target: <self/one enemy/all enemies/owner/room>
  - sequence: <ordered game-term operations and exact values>
  - scaling: <named values, upgrade deltas, and bounds>
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

## Surface inputs

These are the only surface-specific inputs the adapter needs from a normal SPEC:

| Surface | Semantic inputs | Current proof route |
|---|---|---|
| Card | cost, kind, rarity, target, scaling values, upgrade deltas, effect sequence | `CombatPlayer` |
| Relic | rarity, availability, trigger, owner guard, effect sequence, state contract | `CombatPlayer` |
| Potion | rarity, usage window, target, effect sequence | `CombatPlayer` |
| Power | buff/debuff, stack domain, trigger, amount mutation, display fields | `CombatPlayer` |
| Keyword | shared rule, host cards, display title/description, behavior proof | `CombatPlayer` |
| Enchantment | compatible host, persistent change, display/icon fallback | `CombatPlayer` |
| Orb | channel host, passive, evoke, icon and combat fallback | `CombatPlayer` |
| Enemy encounter | HP, group, ordered moves, conditions, encounter placement | `CombatEnemy` |
| Event | acts, pages/options, public outcomes, bounded presentation, combat completion | `MapNode` |
| Character | identity, HP, starter content, pools, hosted mechanic, selected static profiles | `RunStart` + `CombatPlayer` |
| Character combat resource | name, gain/spend/payoff, nonnegative domain, combat reset, fixed UI/fallback | two-combat Character / `CombatPlayer` |
| Ordered semantic buffer | value/order, capacity/overflow, normal source destination, formula/output | two-combat Character / `CombatPlayer` |
| Card Scry helper | top-X amount, discard-any choice, upgrade delta, singleplayer boundary | `CombatPlayer` with visible native selector |

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

The first target profile is `ritsulib-0.4.62-sts2-0.107.1`. There is no compatibility
fallback to the historical framework and no beta-facing variant selection. If the
profile cannot be resolved, authoring stops with an actionable diagnostic and the
placeholder/fallback remains the documented outcome.

## Diagnostic envelope

Build, load, and Tier-2 records use the same fields. The existing exact load marker is
retained so current verification tools remain compatible.

```text
[OPENMOD-FRAMEWORK] phase=<build|load|tier2> mod=<mod-id> framework=RitsuLib frameworkVersion=0.4.62 host=0.107.1 compat=0.107.1 adapter=<surface>/<contract-version> status=<selected|resolved|fallback|failed>
[T2MOD-SELFTEST] <ModName> loaded ok
[T2MOD-SELFTEST] <ModName> state proof: framework=RitsuLib frameworkVersion=0.4.62 host=0.107.1 compat=0.107.1 expected=<...> observed=<...>
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
