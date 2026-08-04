# Implementation plan: M7 design intelligence and user experience

## Status

Version `0.6.0` is an unreleased RitsuLib-only development baseline. The
BaseLib-to-RitsuLib migration and external clean-workspace Codex acceptance are closed;
the durable migration record is
`documents/history/RITSULIB_MIGRATION_RESULTS.md`.

The focused M6.5 Character art, theme, outline, and bounded combat-cue packages are
implemented. Their evidence is recorded in
`documents/history/M65_CHARACTER_QUALITY_FOCUSED_RESULTS.md`. The fresh Prismwright
acceptance and its explicit lead-approved verification exceptions are recorded in
`documents/history/M65_FRESH_ACCEPTANCE_RESULTS.md`; M6.5 is closed.

M6.6 is closed by explicit human-lead decision. Packages 1, 2A, 2B, 2C, 3, 4, and 5 are
implemented with their literal focused results and exceptions recorded under
`documents/history/` or the retained Package 4 official-version proof. Package 4 was
promoted on official RitsuLib `0.5.4` under the Package-level support rule. Per
`AGENTS.md`, official Package semantics plus a public API in the pinned profile are enough
for support, while confirmed problems are recorded as limitations.

M6.7 is closed by explicit human-lead decision on 2026-08-04. M6.7.0 through M6.7.5
implement the approved grounding, public Card, public visual, existing-Ancient,
availability, and non-Card data/behavior Packages. M6.7.6 was canceled and multiplayer
vanilla overrides moved to Future Outlook. The final regression passed `165/165`, plugin
and portable payloads were synchronized repeatably, an independent Mod built from the
reinstalled plugin, and the human lead reported that the representative in-game effects
passed. The consolidated result and literal exceptions are recorded in
`documents/history/M67_VANILLA_OVERRIDES_RESULTS.md`. Do not prepare or claim a GitHub
release.

M7 Design Intelligence and User Experience is selected for planning as the next milestone.
No M7 source Package, generated payload change, behavioral gate, or real-game acceptance has
started. M7 improves the design and authoring workflow while preserving the closed M6.7
runtime support boundary.

## Dependency Boundary

- Generated Mods target STS2 `0.107.1` and `STS2.RitsuLib.Compat.0.107.1` `0.5.4`.
- Runtime manifests depend only on `STS2-RitsuLib >= 0.5.4`.
- Generated Mods must not reference, package, or depend on BaseLib or use historical
  Alchyr templates. Offline BaseLib/Downfall checkouts remain research-only.

## Current Implemented Architecture

```text
idea -> interview -> semantic SPEC -> grounded recipe -> pinned scaffold
     -> author -> build/package -> Tier 1 -> hosted Tier 2 -> bounded repair
```

The official RitsuLib tutorial baseline supplies product semantics and documented feature-
Package membership. The pinned RitsuLib source/compat profile supplies exact versioned API
facts. The workflow stages above implement and verify the feature; they do not redefine
Package support.

The build wrapper validates project, restore, runtime variant, host version, manifest,
and deployed artifacts before verification.

The planned M7 authoring architecture is:

```text
idea
  -> infer fast / co-design / revision route
  -> load the relevant STS2-native design grammar
  -> adaptive interview
  -> DESIGN.md
  -> current deliverable slice + separately recorded future vision
  -> semantic SPEC.md
  -> existing grounded scaffold/author/build/verify/repair pipeline
  -> human playtest feedback
  -> bounded DESIGN.md / SPEC.md revision
```

This is a target, not the current shipped flow. M7 must retain a short path for an
unambiguous single Card or similarly narrow request.

## Verification Ownership

- `CombatPlayer`: content core, computed Card values, stateful cadence, Scry, and
  Character combat cues.
- `CombatEnemy`: Monster + Encounter and move vocabulary.
- `MapNode` / Character: Event behavior/presentation, bounded forced follow-up, and native
  Ancient/Architect dialogue.
- `RunStart` / Character: Foundation, static presentation, resource/UI, and ordered
  buffer.

Use local assertions for deterministic rules. Use one hosted proof per independent
lifecycle or presentation invariant. Fresh acceptance projects are disposable after
their result is recorded.

## Current Work

M7 planning is the selected current work. Begin with M7.0 behavioral evaluation; do not
rewrite `interview.md` first and then invent a passing rubric around the new behavior. No
implementation Package is authorized merely by this planning document: select and close
each Package against its recorded contract before starting the next.

No M6.7 development or acceptance work remains. Both generated payloads agree with
`games/sts2/`, and the installed-plugin acceptance is recorded in
`documents/history/M67_VANILLA_OVERRIDES_RESULTS.md`. The earlier grounding result remains
interim historical evidence.

The independent `VanillaReforged` workspace and deployment are retained because deletion
was not authorized. They are disposable evidence rather than maintained fixtures. Do not
recreate or rerun the M6.7 milestone gate, and do not begin a multiplayer follow-on or any
other Package without a later human-lead selection. Tier 1, Tier 2/SelfTest, the separate
current-catalog headed no-op, and every unselected route remain unrun rather than passed.

Post-acceptance feedback exposed two generation-quality defects: a vanilla Card
base-description replacement was silently downgraded to appended text, and two generated
files needed missing imports for `RegisterPatch<T>()` and `GoldLossType`. The source and both
repository payloads now fail closed on the first conflict and compile-check the second. This
maintenance repair does not reopen M6.7; its focused evidence is recorded in
`documents/history/M67_POST_ACCEPTANCE_GENERATION_QUALITY_REPAIR.md`.

The selected post-closure installation repair now reuses official Steam Workshop RitsuLib
item `3747602295`, preserves local-before-Workshop duplicate precedence, accepts runtime
versions `>= 0.5.4` only with the exact `0.107.1` variant contract, and reuses a complete
real-user NuGet cache when Codex isolates `dotnet` under another profile. The compile
package remains exactly `0.5.4`; this tooling work does not reopen M6.7 or float its API
baseline.

Continue triaging bugs found through real user testing, but do not reopen the retired M6.5,
M6.6, or M6.7 proofs. Their literal results, waivers, and unrun checks remain historical
evidence, not M7 gates.

## M7 - Design Intelligence and User Experience (Planned)

### Goal and boundary

M7 should make open-mod a better game-design collaborator before it writes a better Mod.
It owns question selection, alternatives and trade-offs, STS2-native defaults, content-set
planning, balance hypotheses, scope control, design-to-SPEC translation, and playtest-led
revision. Interview is a router and decision surface, not the whole milestone.

M7 does not add runtime APIs, multiplayer, settings, arbitrary patches, new RitsuLib
Packages, or previously unsupported effects. `DESIGN.md` may preserve a larger future
vision, but `SPEC.md` and the current build must stay inside the existing capability graph.
The skill must state that difference rather than silently simplifying the vision or
pretending future work is currently deliverable.

General design advice and STS2-native design facts are different knowledge classes:

- **pinned fact:** exact `0.107.1` content identity, localized display title, Card data,
  public lifecycle, or supported operation;
- **observed convention:** a recurring native pattern that informs a recommendation but can
  be deliberately broken;
- **creative decision:** player fantasy, theme, mechanic, trade-off, and acceptable
  departure selected by the user.

The skill should answer facts from checked references, recommend conventions with reasons,
and ask the user only for creative decisions or meaningful departures.

### Authoring routes and artifacts

Route selection is inferred and briefly stated; it is not another mandatory questionnaire:

- **fast:** a clear, narrow request receives defaults and at most one compact clarification
  round before a short design capsule and SPEC;
- **co-design:** an ambiguous mechanic, Character, archetype, or content set receives
  alternatives with concrete player-facing trade-offs and incremental decisions;
- **revision:** an existing Mod, DESIGN/SPEC pair, or real playtest report produces a delta,
  impact analysis, and bounded update instead of restarting the interview.

All routes produce a durable `DESIGN.md`, but its depth is adaptive. A fast-path capsule may
contain only intent, one key decision, tuning values, current slice, and explicit gaps. A
full design may add player fantasy, falsifiable pillars, core loop, rules, formulas,
counterplay, edge cases, content roles, rejected alternatives, and a playtest hypothesis.

Artifact ownership remains strict:

- `DESIGN.md` explains what experience is intended, why choices were made, what can be
  tuned, what is deferred, and what evidence would change the design;
- `SPEC.md` freezes only the exact framework-neutral operations generated now;
- `PLAN.md` tracks pipeline stages, not game-design rationale;
- `MEMORY.md` records resolved model/API/resource identities and build/repair facts, not
  creative intent.

### STS2-native design grammar

M7 must add lazy, version-aware design references instead of relying on model pretraining or
one retired proof Mod. Character Foundation is the first mandatory slice because the current
skill knows how to register an exact deck but lacks a reliable native design policy.

The pinned/native research shows these Character starter patterns:

| Character | Native starter shape | Identity teaching cards |
| --- | --- | --- |
| Ironclad | 5 Strike, 4 Defend, 1 identity Card | Bash teaches Vulnerable |
| Silent | 5 Strike, 5 Defend, 2 identity Cards; 12 total | Neutralize and Survivor teach Weak/discard |
| Defect | 4 Strike, 4 Defend, 2 identity Cards | Zap and Dualcast teach Orbs |
| Necrobinder | 4 Strike, 4 Defend, 2 identity Cards | Bodyguard and Unleash teach Osty |
| Regent | 4 Strike, 4 Defend, 2 identity Cards | Falling Star and Venerate teach debuffs/Stars |

Across all five, the player-facing Basic Cards are literally `Strike` / `打击` and
`Defend` / `防御`, while their internal types are Character-specific. Their pinned base
shape is 1 Energy, `6 -> 9` damage with `CardTag.Strike`, and 1 Energy, `5 -> 8` Block with
`CardTag.Defend`. A custom Character should normally preserve those display names and tags,
then use one or two low-complexity Basic Cards plus the Starter relic to teach its core
mechanic. A deliberate departure is allowed after the skill explains its onboarding,
compatibility, and balance consequences.

The observed counts are a design range, not a universal `4/4/2` rule. The skill must propose
an exact deck based on the Character's intended early decisions and explain why, without
asking the user to name ten cards manually. Version-bound facts promoted into the shipped
reference must be checked against the pinned `0.107.1` catalog/game substrate; maintainer
data such as `baselines/spire-codex` is research input, not sole authority.

Later grammar slices may cover Card rarity/upgrade bands, archetype and card-pool roles,
Starter relic responsibilities, resource economies, encounter teaching order, Event
risk/reward, and Monster intent readability. Add each only with a bounded source inventory
and behavioral evaluation case.

### Delivery packages

| Package | Planned product result | Required closure evidence |
| --- | --- | --- |
| M7.0 - behavioral evaluation baseline | A representative prompt corpus, semantic output contracts, rubric, and current-behavior baseline before prompt edits | deterministic fixture/structure checks plus reviewed behavioral scores and documented current failures; no runtime claim |
| M7.1 - adaptive Interview and routing | Fast, co-design, and revision routes; questions only for decisions that materially change the Mod; resumable progress without re-asking settled facts | prompt scenarios for clear, ambiguous, contradictory, unsupported, resume, and revision inputs; question-economy and decision-preservation review |
| M7.2 - STS2-native design grammar | Lazy pinned-fact/convention references beginning with Character Foundation and starter decks; defaults with explicit departure handling | checked source inventory, exact fact tests, native-analogy cases, and no retired proof identity in generic shipped instructions |
| M7.3 - mechanic, content-set, and balance planning | Player fantasy, meaningful decisions, risk/reward, counterplay, formulas, tuning knobs, archetype/card-role coverage, interaction and dominant-strategy checks | focused design cases for one mechanic, one Character/content set, and one numeric/economy problem; absent data stays an open hypothesis |
| M7.4 - scope and design-to-SPEC translation | `DESIGN.md`, future/current split, MUST/placeholder/defer/out-of-scope decisions, and traceability from every generated operation to a supported SPEC route | artifact schema/trace tests, unsupported-route fail-closed cases, and fast-path compactness review |
| M7.5 - theme, narrative, presentation, and coherence | Mechanics, names, localization, visuals, Event text, and Character identity reinforce the selected design; changes produce an impact/re-evaluation queue | cross-artifact conflict cases and one revision delta proving accepted/rejected decisions are preserved |
| M7.6 - playtest and tuning loop | A human-executable hypothesis-led playtest plan, observation capture, design-versus-implementation triage, tuning delta, and targeted backtracking | no fabricated observations; one focused human-led tuning exercise only if explicitly selected, with literal runtime checks for any generated behavior changed |

### M7.0 evaluation model

The initial corpus must include at least:

1. one unambiguous single Card that should not trigger a long interview;
2. one vague mechanic requiring two or three materially different options;
3. one Character whose starter deck is unspecified;
4. one Character/content-set request with a mechanic, archetype, and balance tension;
5. one request combining supported and unsupported operations;
6. one request whose future vision is larger than the current deliverable slice;
7. one existing Mod plus playtest feedback requiring a revision delta;
8. one user decision that conflicts with a native convention but remains implementable.

The rubric evaluates question economy, native-fact accuracy, alternative distinctness,
trade-off reasoning, user-decision preservation, player-facing coherence, supported-route
grounding, future/current separation, design-to-SPEC traceability, and literal evidence
wording. Tests must not enforce a preferred paragraph or treat an LLM judge as the sole
pass/fail authority. Missing formulas, playtest data, or source facts must remain explicit
unknowns rather than confident inventions.

### Wayfinder cleanup and migration

The current source and both payloads contain `Wayfinder`/`RitsuWayfinderProof` in generic
Character verification and API references; `Pathfinder` is absent. Some lines encode exact
HP, pool counts, `5 Strike + 5 Guard`, Compass, or proof log markers. Those values belong to
a retired proof, not to a generated Character contract.

During M7.0/M7.2 implementation:

1. inventory every proof-specific identity in `games/sts2/skills/`;
2. replace generic verification with exact values read from the current `SPEC.md`;
3. replace design defaults with pinned native grammar, not another named demo Character;
4. retain durable proof facts only under `documents/history/` or repository-only evidence;
5. regenerate both payloads and assert that retired proof identities do not reappear in
   generic shipped instructions.

This cleanup changes authoring guidance, not the historical truth of the old proof.

### Milestone verification policy

Documentation and prompt-only work uses contract, corpus, and payload checks. A Package that
changes generated runtime source receives the closest proportional real host; it does not
inherit M6.7's closed batching exception. Do not schedule a fresh full-pipeline Mod until a
specific M7 Package or the human lead selects that gate. Human playtest evidence remains
literal and cannot be replaced by simulated personas, screenshots, build success, or Tier 2
state alone.

## M6.6 - Capability Expansion (Closed)

M6.6 is closed. Keep only its active support and limitation summary here; the linked history
files own exact proof steps, headed observations, waivers, and unrun checks.

| Package | Implemented support | Retained boundary and evidence |
| --- | --- | --- |
| 1 - advanced targeting | Mod-local deterministic single-target Cards/Potions and multi-target Cards with native selection, cancellation, and resolution-time checks | Custom `potion + many` retains the pinned queued-consumption limitation. See `documents/history/M66_ADVANCED_TARGETING_RESULTS.md`. |
| 2A - computed values | One preview/execution formula for computed Damage, Block, Energy, Stars, raw typed Power, amount-given Power, and localized DynamicVar tooltips | Literal headed result and omitted strict Tier 2 are in `documents/history/M66_COMPUTED_VALUES_RESULTS.md`. |
| 2B/2C - readability | Ordered fixed-color Card hand emphasis, up to three safe-corner Relic labels, and one top-left Power label | Intent remains a supported public Extra Badges consumer but has no generated authoring route. Strict Tier 2 was not run. See `documents/history/M66_GAMEPLAY_READABILITY_RESULTS.md`. |
| 3 - Rest Site options | Singleplayer Relic-owned options with free/fixed Gold, deterministic outcomes, once-per-site/run repeatability, native stay/leave behavior, and checked custom/Heal-fallback icons | Card/Modifier owners, variable or non-Gold costs, arbitrary transactions, same-site repeat, and multiplayer remain outside the slice. See `documents/history/M66_REST_SITE_OPTIONS_RESULTS.md`. |
| 4 - Custom Card Piles | Complete documented RitsuLib `0.5.4` Package across combat/run scopes, five presentation styles including ExtraHand, public views/hotkeys, native movement, localization, and callbacks | Generated Mods use only the public framework route and never recreate the native-Hand bridge. The accepted focused result and strict verification exceptions are in `documents/history/M66_CARD_PILE_EXTRA_HAND_RESULTS.md`. |
| 5 - Character dialogue | Character-local dialogue across the nine cataloged native Ancient and Architect scenes while preserving native models, layouts, options, and outcomes | This is Character contribution, not global dialogue or Ancient replacement. See `documents/history/M66_ANCIENT_DIALOGUE_RESULTS.md`. |

The Package-level support rule, dependency boundary, and literal verification rules now live
in `AGENTS.md`. Do not reopen M6.6 implementation details in this active plan unless a
confirmed regression changes the current support boundary.

## M6.7 - Version-Bound Vanilla Content Overrides and Behavior Composition (Closed)

M6.7 is the closed milestone for generated Mods that intentionally alter existing
base-game content. It is not limited to Card numbers: the target is a broad semantic system
for data, availability, behavior, and presentation changes across Cards, Relics, Potions,
Powers, Monsters/Encounters, and Events where the current authoring vocabulary and a grounded
host adapter can express the requested result.

The human lead selected M6.7 on 2026-08-02, started M6.7.0 on 2026-08-03, and closed the
milestone on 2026-08-04. The no-op grounding source surface and first five operation
Packages through M6.7.5 Non-Card Data and Behavior are implemented and delivered. The
scope may be refined as the version catalog reveals real model shapes, but do not shrink the
product goal to a small handwritten target whitelist merely because some operations need
reusable, maintained adapters.

### Grounded route classes and first operation matrix

Classify every operation/category pair before authoring it:

- **Public:** official tutorial semantics and a direct public RitsuLib `0.5.4` route apply to
  the vanilla consumer.
- **Probe:** a public route appears type-compatible with vanilla models, but the documented
  examples do not establish that use; run one focused real-host probe before promotion.
- **Adapter:** open-mod owns one reviewed STS2 `0.107.1` implementation with an exact target,
  signature, semantic baseline, and structural fingerprint. Prompts select a cataloged
  operation; they never generate a patch body.
- **Not generated:** no complete grounded route exists yet. Research may later move that
  cell into one of the three classes above.

The initial matrix is grounded in the official tutorial pages for
[Capabilities](https://tutorials.sts2modding.com/04-18-add-capability/),
[Lifecycle Events](https://tutorials.sts2modding.com/04-23-lifecycle-events/),
[Patch System](https://tutorials.sts2modding.com/04-24-patch-system/), and
[Content Registry](https://tutorials.sts2modding.com/04-27-content-registry/), plus the exact
public source and docs in the pinned `baselines/STS2-RitsuLib` `0.5.4` checkout. Tutorial
semantics do not override a missing or incompatible pinned signature.

Official capability guidance establishes that `ModelCapability` can attach to concrete
vanilla `AbstractModel` types and that owner hooks can compose before or after the owner.
Lifecycle events are primarily observation surfaces, not a general replacement mechanism,
and the normal content registries register Mod-owned types rather than rewrite vanilla
pools. The pinned source further establishes these narrower facts:

- Card property contributors can override type, rarity, and target; Card tags can only be
  appended and deduplicated. Energy/Star contributors alter evaluated local cost, not a
  canonical printed field. Title fragments can replace the base title, while description
  contributors append/prepend fragments rather than replace the vanilla base description.
- Capability-owned dynamic variables are separate from variables owned by the vanilla
  model. `CardPlayCapability` can publicly suppress the owner's `OnPlay`; no equally general
  public suppression route is confirmed for Relic, Potion, Power, Monster, or Event bodies.
- `ExternalCardMaterialOverrideRegistry` explicitly accepts base-game Cards. The external
  asset registry covers Relic, Power, Potion, Orb, Act, Event, Encounter, Ancient,
  Affliction, Enchantment, and Modifier consumers. It does not expose a vanilla Monster-body
  provider.
- `AncientOption<TAncient>(ModAncientOptionRule)` publicly appends options to an existing
  Ancient with condition, priority, and duplicate-text handling. The fixed `0.107.1`
  `GenerateInitialOptionsWrapper` retained-list postfix provides complete initial-option
  replacement without replacing the event class, while the protected `SetEventState` and
  `Done` targets provide Mod-owned pages and native choice-history completion. All three
  Adapter IL bodies are cataloged and fail closed on drift.

The first reviewed matrix is:

| Content | Adjust data | Compose behavior | Replace behavior | Availability | Visual |
| --- | --- | --- | --- | --- | --- |
| Card | Public for type/rarity/target, appended tags, evaluated Energy/Star cost, play state/result, title, and description fragments; no promoted route for canonical variables, tag removal, or base-description replacement | Public | Public for `OnPlay`; Adapter for other entry points | Public pinned-epoch gate and pool add; fixed pool remove/move Adapter; no permanent disable or global weighting | Public |
| Character | Not generated | Not generated | Not generated | Public pinned-epoch gate; no permanent disable or pool Adapter | Public |
| Relic / Potion | Adapter | Public typed owner hooks | Adapter | Public pool add; fixed pool remove/move and epoch/disable Adapters | Public |
| Power / Orb | Adapter | Public typed owner hooks | Adapter | Source-specific Adapter; no generic acquisition pool | Public |
| Enchantment / Affliction | Adapter | Public typed owner hooks | Adapter | Source-specific Adapter | Public |
| Monster | Adapter for stats and cataloged move/intent values | Public typed owner hooks | Adapter for move/AI entry points | Encounter/source Adapter | Public for Encounter assets; Monster body is not generated |
| Existing Ancient | Adapter for cataloged initial-choice data only | Public multi-option append plus Mod-owned pages | Fixed Adapter replaces the complete initial option list while preserving the native event class/lifecycle | Public pinned-epoch gate only for shared `EVENT.DARV`; act-owned Ancients unchanged | Public |
| Ordinary Event | Adapter for cataloged options/outcomes | Only through a grounded target route | Adapter | Public pinned-epoch gate; no permanent disable or source weighting | Public |
| Act / Modifier | No generic first-wave data route | Not generated | Not generated | Not generated | Public |

This matrix is the initial implementation boundary, not a claim of completed support. Expand
it by reusable operation shape and content category, not by silently special-casing one named
vanilla object.

### Product model and semantic operations

A generated Mod selects an existing vanilla model by stable game-version identity, preserves
that model's ID and untouched assets, and declares one or more semantic operations. The SPEC
must never contain arbitrary method names, reflection expressions, Harmony bodies, or IL.
Expose these operation families:

1. **Adjust:** set or add a delta to a declared property, canonical value, upgrade value, or
   named gameplay variable while preserving its typed damage/block/Power semantics.
2. **Compose:** keep the original behavior and run a declared generated effect before or
   after it, optionally under a bounded trigger, cadence, target, or state predicate.
3. **Replace:** suppress one declared original behavior entry point and execute a complete
   generated recipe in its place. Unrelated lifecycle, identity, assets, and save data remain
   vanilla.
4. **Availability:** add, remove, move, or apply a source-specific weighting operation to an
   existing model in a declared pool, reward source, unlock surface, or multiplayer surface.
5. **Visual:** replace one public, cataloged material, texture, scene, or icon consumer while
   preserving the vanilla model identity and unrelated presentation.

Disable acquisition is an Availability mode: stop new runs from obtaining content while
retaining the model so old saves and existing run state remain readable. It is not physical
model deletion.

Each operation must declare target model/category, operation mode, affected surface, desired
value or behavior, base and upgrade forms where applicable, localization effect, multiplayer
scope, and whether it is required or explicitly optional compatibility. `set` and `delta`
are distinct conflict semantics and must not be inferred from wording after SPEC approval.

### Version catalog and target grounding

Build a deterministic, reviewable vanilla-content catalog for every supported STS2 version.
The first catalog targets the pinned `0.107.1` host; supporting a later patch requires a new
catalog and proof, not silent reuse of old targets. Produce it from two bounded collectors:

- a game-host collector for `ModelDb` identity, pool/source membership, public properties,
  canonical dynamic-variable observations, and base/upgrade runtime snapshots; and
- an offline assembly collector for exact adapter method signatures, metadata identity, and
  structural/IL fingerprints without copying game implementation into generated Mods.

The merged catalog should record, where applicable:

- stable `ModelId`, concrete model type, content category, pool/source membership, rarity,
  costs, tags/keywords, target/result behavior, and multiplayer constraint;
- stable title localization table/key pairs and checked display-title aliases for every
  language exposed by the pinned game host, without retaining machine-local overrides;
- canonical named dynamic variables, their concrete types/value properties, base values,
  upgrade deltas, and localization placeholders;
- acquisition/unlock hosts, common public behavior entry points, and whether an existing
  open-mod recipe can express a complete replacement;
- checked target signatures and structural fingerprints for the narrow patch adapters that
  remain necessary; and
- known special consumers such as generated token Cards, Powers applied by a Card, enemy
  move/intent pairs, Event scenes, and cached pool/reward views.

Resolve exact internal names and localized display titles through this catalog and fail on
ambiguity. This does not imply free-form grammar, synonyms, or gameplay-description
understanding. A required edit
must check its expected target and baseline fingerprint before applying. Missing types,
changed signatures, unexpected canonical values, or incompatible variable types fail closed
with a useful diagnostic; do not guess a replacement target after a game update. Catalog
metadata is research/compatibility data, not permission to copy game source or assets into a
generated Mod.

Every generated override Mod emits a semantic manifest containing the pinned host/profile,
resolved `ModelId`, operation ID and mode, expected baseline, chosen public route or adapter,
scope, ordering, and compatibility criticality. M6.7.0 requires repeatable catalog output,
useful failures for ambiguous/missing names, fail-closed version/fingerprint drift,
overlap detection, and a no-op manifest that validates through scaffold/build preflight.
The separate current-localized-catalog no-op build/load remains intentionally unrun; payload
delivery passed through the consolidated M6.7 closure.

### Layer 1 - Data, metadata, upgrade, and presentation overrides

The first promoted layer should cover broad balance-style edits rather than a few named
Cards:

- public Card type, rarity, target, appended tags, evaluated Energy/Star cost, playability,
  result pile, title replacement, and description/tooltip fragments;
- canonical Card variables, upgrade deltas, tag/keyword removal, replay count, and base-text
  replacement only after a cataloged Adapter owns the exact vanilla storage/consumer route;
- ordinary Relic, Potion, Power, Monster, and move/intent values when they are exposed as
  cataloged properties or named variables, through maintained adapters for reusable model
  shapes rather than a universal property contributor;
- generated-token and applied-Power routing, so a request against a source Card can resolve
  the actual model that owns the number; and
- matching title/description/tooltip changes when the original text does not already consume
  the modified variable.

Preserve the original typed `DamageVar`, `BlockVar`, computed value, and Power amount route so
normal Strength, Dexterity, Vulnerable, Frail, enchantment, and preview hooks still apply.
Baseline cost edits must occur before normal temporary/global cost modifiers rather than
overwriting their final result. Base, upgrade preview, upgraded instance, downgrade, clone,
transform, save/load, and card-library/reward consumers must all observe the same override.
Never ship a text-only or effect-only numeric edit. Treat a public Energy/Star contributor as
an evaluated local-cost operation unless a separate Adapter proves a canonical baseline edit;
do not describe the contributor as mutating the vanilla printed field.

Use RitsuLib default model capabilities and property contributors where they express the
semantic layer. Capability-owned dynamic variables do not overwrite variables owned by the
vanilla model. Where no public property/variable override exists, route through a maintained
version-catalog Adapter registered with `IPatchMethod`; do not generate a new patch shape for
each prompt.

### Layer 2 - Pool, reward, unlock, and availability overrides

Start with a focused probe of `ModUnlockRegistry.RequireEpoch<TModel, TEpoch>` against
cataloged vanilla Card, Relic, Potion, and room-Event targets. Its implementation appears to
filter by `ModelId`, but official examples establish Mod-owned content only. Promote vanilla
disable/re-gating only for the target families whose fresh-run and existing-save behavior the
probe proves.

Implement Card, Relic, and Potion pool add/remove/move through fixed-version Adapters over
their canonical `AllCards`, `AllRelics`, and `AllPotions` hosts. Preserve `ModelDb`
registration, identity, and old-save readability; update or reject affected cached IDs and
Card pool resolution; and prevent duplicate membership. Do not register a vanilla type as
Mod-owned content through the ordinary content registry.

Appearance weighting is source-specific. Many sources use rarity, uniform lists, or their
own deterministic RNG rather than one shared weight field. Add a weighting operation only
after cataloging that exact reward/shop/Ancient/other source and its RNG consumption. Treat
pool membership, source weight, unlock state, and owned-instance behavior as separate fields.

This layer may edit existing availability and unlock metadata already owned by a cataloged
vanilla model or acquisition source. It does not schedule authoring new Story or Epoch
content, new progression tracks, or new unlock systems; those would be separate new-content
capabilities with their own persistence, presentation, and compatibility contracts.

Disabling vanilla content removes its future acquisition routes but leaves the model
registered for existing saves. Moving or source-specific weighting must not duplicate it,
must preserve deterministic selection/RNG consumption, and must specify whether current runs
are affected. Prove card library/compendium views, rewards, shops or source-specific choices,
fresh runs, and loading a save that already owns the disabled content.

### Layer 3 - Behavior composition and complete replacement

Reuse the existing open-mod semantic recipes instead of treating vanilla behavior as opaque
IL. A replacement keeps the vanilla identity/presentation layers requested by the user, then
runs the same grounded Card/Relic/Potion/Power/Monster/Event commands that would be used for
new content.

- **Cards:** attach a default `CardPlayCapability`. Composition runs before/after the owning
  Card; replacement uses the public suppression result to prevent the original `OnPlay` and
  runs one complete generated effect. Generate matching variables, description, target,
  payment, upgrade, result-pile, preview, and applied-Power behavior together.
- **Relics, Potions, Powers, Orbs, Enchantments, Afflictions, and Monsters:** use typed owner
  capabilities for additional hook behavior. Public hooks compose; they do not imply owner
  suppression. A complete replacement must suppress only the cataloged original hook/use/
  move entry points through a maintained Adapter, then run the generated hook vocabulary
  exactly once.
- **Conditions and cadence:** provide reusable semantic filters such as Card type, target
  side, source, threshold, first/Nth time per turn/combat, at most/exactly N, and enabled
  singleplayer/multiplayer scope. These cover common balance changes without target-specific
  code.
- **Monster/Encounter behavior:** support move damage, intent, sequence, fixed-turn openings,
  and bounded conditional selection through the existing grounded move vocabulary. Unusual
  AI state machines or animation-coupled transitions may use a cataloged target adapter.
- **Existing Ancients:** use public `AncientOption<TAncient>` rules for appended options or
  the one fixed retained-list Adapter for complete initial-option replacement. Support
  nested conditions, visibility/lock state, fixed Gold/HP/Max HP costs, typed option
  presentation, ordered deterministic outcomes, deck selectors, fixed custom rewards, and
  Mod-owned page branches. Finish through native `Done()` so the original event model,
  room, save identity, allowance gate, and Ancient choice history remain intact.
- **Ordinary Events:** option eligibility, costs, rewards, and generated outcomes require a
  cataloged target Adapter; lifecycle observation alone is not a general option replacement
  route. Scene/layout replacement, unusual chains, or private async state machines remain
  target-specific work rather than free-form patch generation.

When the current game has removed a model or required asset entirely, recreating it is new
content, not a vanilla override. It may reuse the normal authoring pipeline only when the
requested implementation and assets are independently available; do not recover or package
removed game code/assets from historical builds.

### Adapter, conflict, and multiplayer contract

Prefer RitsuLib registries, model capabilities, owner hooks, and public contributors. The
fallback patch layer is allowed because M6.7 explicitly targets existing game behavior, but
it remains a reviewed adapter library:

- every patch has a stable ID, exact target/signature, version fingerprint, criticality, and
  structured startup diagnostic;
- use required patchers for behavior promised by the generated Mod and optional patches only
  for explicitly optional compatibility;
- prefer a method-boundary prefix/postfix or task wrapper; use checked Harmony IL helpers only
  when no narrower public or method-boundary route exists; and
- never emit arbitrary reflection, private-field names, or ad hoc IL directly from a user's
  prompt.

Within one generated Mod, operations apply in approved SPEC order. Baseline adjustments run
before normal temporary/run modifiers; composed effects run at their declared owner-hook
order. Detect overlapping `set`, `replace`, and acquisition-removal operations and reject an
ambiguous plan. `delta` may compose only when the target variable and ordering are known.

At runtime, report the target, operation, expected baseline, resolved adapter, and any other
patch owners found on required targets. Do not promise automatic compatibility when another
Mod also replaces the same behavior. A conflicting required replacement should fail visibly
rather than become silent last-writer-wins behavior.

Detect all overlapping operations inside one generated Mod. External visual registries use
provider order and key replacement but expose no public complete provider inventory or
priority contract across Mods, so cross-Mod visual conflict diagnostics are best-effort and
must not be described as complete. Required behavior replacements still use whatever patch-
owner information is publicly inspectable and fail visibly on a known conflict.

All promoted M6.7 operations remain singleplayer. Multiplayer promotion is outside this
milestone and is recorded under Future Outlook rather than as a pending delivery Package.

### Delivery packages

1. **M6.7.0 - Grounding Kernel (complete):** both
   catalog collectors, the exact name/alias resolver, runtime semantic snapshots,
   expected-baseline/signature/fingerprint checks,
   semantic override manifest, same-Mod conflict detection, and fail-closed diagnostics are
   implemented. The checked `0.107.1` catalog contains 1624 vanilla models, 1580 stable
   title sources, 1537 English and Simplified Chinese titles, all 14 pinned language
   columns and exact assembly identity. It now includes 4165 reviewed Adapter fingerprints:
   the previous twenty plus 4145 M6.7.5 targets. It promotes M6.7.1 through M6.7.5. Repeated
   localized-title collector runs produced the
   same snapshot hash and
   passed their collector-only strict Tier 1/Tier 2 check. The separate current-catalog
   headed no-op remains intentionally unrun; final regression and payload delivery passed
   through the consolidated closure. It makes no gameplay change. See the interim record
   in `documents/history/M67_GROUNDING_KERNEL_RESULTS.md`.
2. **M6.7.1 - Public Card Overrides (complete):** the
   checked Package covers the grounded non-asset public Card contributors,
   capability-owned variables, public `OnPlay` composition/replacement, and owner lifecycle
   hooks. Focused tests and a compile-only check pass; selected Card routes were included
   in the built consolidated Mod that the human lead accepted as a whole. Canonical
   DynamicVar edits, destructive
   metadata edits, assets, acquisition, and transform carry-over remain outside this
   Package.
3. **M6.7.2 - Public Visual Overrides (complete):**
   the checked Package covers all 44 public Card-material/external-asset providers across
   Card/CardPool, Relic, Power, Potion, Orb, Act, Event/Ancient, Encounter, Affliction,
   Enchantment, and Modifier targets. Exact Mod-local Material/texture/PackedScene/Spine/
   directory/list resources, deterministic raster normalization where a current spec
   matches, runtime fallback, cleanup, and same-surface conflicts are implemented in the
   skill/manifest pipeline. There is no vanilla Monster-body external provider. Focused
   manifest/resource tests pass; selected Card and Darv visual providers were included in
   the built consolidated Mod that the human lead accepted as a whole. No individual-
   provider observation is inferred. Other providers and AI image generation were not run.
   Preserve the documented limit on cross-Mod provider conflict diagnosis.
4. **M6.7.3 - Existing Ancient Extensions (complete):** support public multi-option append
   and one fixed fingerprinted complete
   initial-option replacement Adapter for the nine pinned native Ancients. Lower nested
   conditions, visible/locked choices, fixed Gold/HP/Max HP costs, typed Hover Tips,
   relic-backed presentation, ordered fixed outcomes, deck upgrade/remove/transform/
   enchant selection, fixed custom rewards, bounded shake, Mod-owned subsequent pages, and
   native `Done()` finish/choice history. Localize all option/page text through Mod-local
   `events.json`; compose requested existing-Ancient visuals through M6.7.2. Preserve the
   native class, room, opening dialogue, save identity, allowance gate, and ambient audio.
   Focused tests pass; the selected Darv route was included in the built consolidated Mod
   that the human lead accepted as a whole. Other Ancient routes remain unrun.
5. **M6.7.4 - Availability (complete):** promote the
   public `RequireEpoch` route for 57 pinned vanilla epochs across Card, Character, ordinary
   Event, and shared `EVENT.DARV`; fixed Relic/Potion epoch or permanent-disable filters;
   and Card/Relic/Potion pool add plus remove/move membership Adapters. Pool manifests copy
   complete `ModelDb` baselines, simulate ordered transitions, require the pinned primary
   pool, preserve existing instances, reject debug/empty transitions, and remain
   singleplayer-only. Focused manifest/catalog/document-route tests pass; one Card pool move
   was included in the built consolidated Mod that the human lead accepted as a whole.
   Cache timing, unlock UI,
   fresh-acquisition order/RNG, duplicates, and existing-save variants remain unrun. Global
   weighting and Card/Character/Event permanent disable remain outside this Package.
6. **M6.7.5 - Non-Card Data and Behavior (complete):** promote all public owner-hook
   consumers for Relic/Potion/Power/Orb/
   Enchantment/Affliction/Monster, including all 100 asynchronous `AbstractModel` hooks,
   26 numeric hooks, 28 decisions, and four typed Orb callbacks. Add sixteen intrinsic data
   routes and complete checked lifecycle/body replacement for those families, complete
   Monster move graphs, paired runtime/all-possible Encounter rosters, and complete ordinary
   Event options plus Mod-owned pages. The checked catalog contains 4141 target-specific
   M6.7.5 method fingerprints and four shared stream/flow boundaries. All operations remain
   singleplayer. Focused 40-test manifest/catalog/localization/documentation checks and
   Python syntax pass; selected Relic, Monster, and Encounter routes were included in the
   built consolidated Mod that the human lead accepted as a whole. Unselected owner/
   lifecycle families and ordinary
   Event routes remain unrun. Affliction synchronous apply/remove callbacks are the one
   narrow lifecycle limitation recorded in the Package reference.
This sequence is a dependency order, not a requirement to wait for every content category
before finishing an earlier layer. Do not claim broad "vanilla editing" from one sample
Card: record the exact documented Package, operation families, model categories, and
verification that actually ran.

### Proof and M6.7 completion

The human lead selected and completed a representative, not exhaustive, acceptance. The
final source regression passed `165/165`; Python compilation and six skill-root validations
passed; plugin and portable payloads were reproducible with 161 effective files each and
zero differences; and the local plugin was reinstalled with zero file-hash differences
from the repository payload.

The fresh independent `VanillaReforged` Mod used that installed payload and built with zero
warnings and zero errors. Its 13 semantic operations sampled three concise groups:

1. **Run and player combat:** Ironclad Strike text/variables/complete play replacement,
   Card frame plus optional missing-banner fallback, Ironclad-to-Silent pool move, and a
   Burning Blood owner hook.
2. **Native Ancient room:** Darv complete initial options, fixed Gold effect, Mod-owned
   page/native finish, and initial portrait override.
3. **Enemy combat:** Fuzzy Wurm Crawler fixed HP and complete move graph plus the weak
   Encounter's paired runtime/all-possible roster.

On 2026-08-04 the human lead reported that the independent-session effect test passed and
explicitly closed M6.7. Tier 1, Tier 2/SelfTest, the separate current-catalog headed no-op,
and every unselected visual provider, hook, family, availability mode, ordinary Event,
save/load, multiplayer, and cross-Mod path remain unrun. The exact build evidence, literal
human report, hashes, and exceptions are in
`documents/history/M67_VANILLA_OVERRIDES_RESULTS.md`. Do not rerun or expand this closed
milestone gate. Targets outside the delivered matrix still require official semantics and
a pinned public or fixed-Adapter route before promotion.

## Current Boundaries

M6.5 has no separate Character-sheet generation, locked-selection route, custom map
marker, Character trail, or `Cast` cue. Characters keep the checked game-native shared
map-marker fallback. Full-energy acquisition uses one Character-specific layer plus four
fixed templates. Combat cues remain the private, combat-only, all-or-nothing
`Idle`/`Attack`/`Hit`/`Dead` set; they do not promote Spine, animated merchant/rest-site
bodies, production audio/materials, or multiplayer presentation.

Locked-selection presentation, Character-specific card trails, additional combat cue
states, new Ancient models, global native Ancient dialogue/room replacement, Ancient line
audio, randomized outcome/RNG rewrites, special combat, direct merchant/rest/treasure
transitions, Ancient behavior outside the fixed M6.7.3 option/page/effect vocabulary,
alternative Energy, arbitrary Event behavior/chains, and one-click Workshop publishing
retain their current unsupported boundaries. M6.7.3 replaces a complete initial option list
only through its fixed reviewed Adapter; it does not replace the Ancient model or enable
arbitrary prompt-derived patching.

Only the promoted M6.7.1 public Card, M6.7.2 public visual, M6.7.3 existing-Ancient, M6.7.4
availability, and M6.7.5 non-Card data/behavior operations are generated. Every other
nonempty M6.7 operation waits for its delivery Package to promote a grounded route. Missing
implementation or verification means exactly that and does not redefine an official
RitsuLib Package boundary.
Unversioned target guessing and arbitrary generated Harmony/reflection/IL remain outside
M6.7 entirely.

## Future Outlook

Multiplayer vanilla overrides are future work, not M6.7.6. The human lead canceled that
Package on 2026-08-03 so M6.7 development ends at M6.7.5. A future separately selected
track may promote an already-proved singleplayer operation family only after every peer
uses an identical manifest and real-host evidence covers deterministic state and RNG,
choices, save/load, remote presentation, targeted synchronization, timeouts/disconnect
cleanup, and host authority where relevant. Singleplayer evidence must never be relabeled
as multiplayer support.

Optional Mod settings and persistence remain a later possibility outside the closed M6.6
scope and closed M6.7 matrix. A future design may cover settings pages with toggles, sliders,
choices, and key bindings plus RitsuLib's Global, Profile, and run-owned save scopes. Generate
these only when a Mod request actually needs configuration or durable state; do not add a
settings page to every simple Mod. No implementation package is currently scheduled.
