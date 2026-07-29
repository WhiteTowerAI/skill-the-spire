# Implementation plan: 0.6.0 stabilization

## Status

Version `0.6.0` is an unreleased RitsuLib-only development baseline. The
BaseLib-to-RitsuLib migration and external clean-workspace Codex acceptance are closed;
the durable migration record is
`documents/history/RITSULIB_MIGRATION_RESULTS.md`.

The focused M6.5 Character art, theme, outline, and bounded combat-cue packages are
pipeline-supported. Their evidence is recorded in
`documents/history/M65_CHARACTER_QUALITY_FOCUSED_RESULTS.md`. The fresh Prismwright
acceptance and its explicit lead-approved verification exceptions are recorded in
`documents/history/M65_FRESH_ACCEPTANCE_RESULTS.md`; M6.5 is closed.

Do not prepare or claim a GitHub release. M6.6 and M6.7 planning below do not promote any
new surface into the supported boundary or automatically start implementation.

## Dependency Boundary

- Generated Mods target STS2 `0.107.1` and `STS2.RitsuLib.Compat.0.107.1` `0.4.62`.
- Runtime manifests depend only on `STS2-RitsuLib >= 0.4.62`.
- Generated Mods must not reference, package, or depend on BaseLib or use historical
  Alchyr templates. Offline BaseLib/Downfall checkouts remain research-only.

## Current Runtime Architecture

```text
idea -> interview -> semantic SPEC -> grounded recipe -> pinned scaffold
     -> author -> build/package -> Tier 1 -> hosted Tier 2 -> bounded repair
```

The build wrapper validates project, restore, runtime variant, host version, manifest,
and deployed artifacts before verification.

## Verification Ownership

- `CombatPlayer`: content core, stateful cadence, Scry, and Character combat cues.
- `CombatEnemy`: Monster + Encounter and move vocabulary.
- `MapNode`: Event behavior/presentation and bounded forced follow-up.
- `RunStart` / Character: Foundation, static presentation, resource/UI, and ordered
  buffer.

Use local assertions for deterministic rules. Use one hosted proof per independent
lifecycle or presentation invariant. Fresh acceptance projects are disposable after
their result is recorded.

## Current Work

Continue triaging bugs found through real user testing. No M6.5 gate remains scheduled.
On 2026-07-29, the human lead reported the headed Prismwright acceptance successful,
explicitly waived the remaining Tier 2/self-test harness, and directed retirement. The
load marker and runtime profile matched; the strict log parser separately reported only
engine-shutdown resource-leak messages after the headed session. M6.5 is closed by that
lead decision rather than by claiming those omitted checks passed.

Do not reopen Prismwright or start M7. The next planned milestone is the provisional M6.6
capability expansion below, followed by the planned M6.7 vanilla-content track. Their
presence in this document authorizes scope planning, not automatic implementation; the
human lead still selects when and in what order packages start.

## M6.6 - Capability Expansion (Provisional)

M6.6 is the next capability-improvement milestone. Its scope is deliberately provisional:
the human lead may add other suitable features before or during milestone planning. Any
addition must be written into this plan explicitly; do not infer extra scope from
RitsuLib's available APIs.

### Shared implementation and promotion rules

Treat every package, and every separately listed readability consumer, as an independent
support claim. Planning or finding a public RitsuLib API is not enough. Before promotion,
the selected slice must have:

1. a semantic interview/SPEC shape that describes player-visible intent rather than C# API
   names, including owner, lifetime, initial state, transitions, localization, and fallback;
2. one grounded `sts2-api` recipe and pinned RitsuLib `0.4.62` adapter route, without
   BaseLib, copied baseline code, private patches, or arbitrary generated reflection;
3. deterministic checks for calculations, filtering, ordering, payment, and state rules,
   plus build/manifest checks that preserve the RitsuLib-only dependency boundary;
4. the nearest focused real-game proof for every independent lifecycle and presentation
   invariant, using structured post-state evidence for behavior and a headed check where
   targeting, controller focus, text fit, color, or non-overlap is the actual claim; and
5. updated source documentation and support graph, followed by regeneration and parity
   validation of both committed payloads.

Do not change `games/sts2/tests/content-capability-graph.md` from unsupported to supported
until that slice's recipe and focused host proof both exist. Ordinary package work does not
schedule another fresh natural-language acceptance Mod; add such a gate to this plan first
if the milestone later needs one.

### Package 1 - Advanced Card and Potion target types

**Semantic intake.** Add a bounded target declaration that records whether the consumer is
a Card or Potion, whether it selects one or affects many, a stable Mod-local target ID, and
a declarative creature predicate. Single-target rules may combine candidate state, acting
player state, and source Card/Potion state; multi-target rules may use candidate and acting
player state. Every predicate must remain deterministic at selection and execution time.
Prefer reusable named families such as attacking enemies, blocking or nonblocking enemies,
tied highest/lowest-HP enemies, full-life enemies, anyone, or everyone over generated
one-off predicate code.

**RitsuLib route and lifecycle.** Register deterministic Mod-scoped single- or multi-target
`TargetType` values through `CustomTargetType`. For single-target registration, use
`CustomTargetContext` only when the predicate genuinely needs the source Card/Potion in
addition to the candidate creature and acting player; do not imply source-aware
multi-target registration. This surface targets live combat `Creature` objects; it does not
target Cards in hand, corpses, map objects, or arbitrary game objects.

- A single-target consumer must filter candidates consistently for mouse and controller,
  allow normal cancellation, handle no legal candidates, and revalidate the selected
  creature when play/use resolves.
- A multi-target Card or Potion executes once with no selected creature. Its effect must
  call the appropriate `GetTargets(...)` extension at resolution time and apply the effect
  exactly once to each returned creature.
- Cancellation or loss of all valid targets must not spend resources, consume a Potion, or
  strand a Card outside its normal lifecycle. Successful execution must retain the normal
  Card result-pile and Potion-use behavior.

**First proof matrix.** Prove at least one single-target and one multi-target family. If the
package claims both Card and Potion support, include a real consumer of each rather than
inferring Potion behavior from a Card test. Cover zero, one, and multiple legal candidates;
mouse/controller selection where applicable; cancellation; a candidate becoming invalid;
and an exact structured list of affected creature IDs and state deltas. Visually check the
reticle/selection affordance and confirm that invalid creatures cannot be selected.

**Not in the first slice.** Arbitrary object targeting, selecting Cards or map nodes,
retargeting dead creatures, global interoperability registration for other Mods, and custom
targeting UI layouts remain unsupported unless separately planned and proved.

### Package 2 - Gameplay readability

This package contains three independent subpackages. They may be implemented and promoted
separately; completing one does not support the other two.

#### 2A. Computed previews, icon variables, and variable tooltips

Extend semantic card text so one declared calculation feeds both the displayed dynamic
value and the live effect. Route damage and block through `ComputedDamage` and
`ComputedBlock` so previews continue to receive normal Strength, Dexterity, Vulnerable,
Frail, enchantment, and preview-hook adjustments. Use an untyped plain computed value only
for numbers that intentionally do not pass through damage/block or Power-application hooks.

- Add `ComputedEnergy` and `ComputedStars` for runtime-changing Energy and Star icon counts.
  Ground localization on the pinned formatter contract (`energyIcons()` and `starIcons()`),
  and resolve the current local `{X:stars()}` wording mismatch before generating recipes.
- Use `ComputedPower<T>` for a typed Power value and
  `ComputedPowerAmountGiven<T>` when the number means Power applied to a creature and must
  receive normal Power amount-given hooks.
- Allow `.WithSharedTooltip(...)` only from a declared localization entry. Dynamic-variable
  tooltip text and any optional icon belong in `static_hover_tips` localization and need a
  deterministic fallback when the icon is omitted.
- Never maintain a display-only copy of a formula. The recipe should generate one semantic
  calculation or shared helper consumed by description rendering and effect execution.

Contract tests should cover zero, positive, and changing values; upgrade/base forms; relevant
combat modifiers; and the difference between raw computed numbers and hook-aware damage,
block, or Power amounts. The hosted proof must show the card text changing before play and
then record an outcome equal to that final preview. For Energy/Stars, prove zero icons,
multiple icons, tooltip rendering, and text reflow without clipping or stale glyphs.

#### 2B. Conditional hand glow and outline

Add declarative hand emphasis only when it communicates an actionable state. Use gold glow
for an active bonus or stronger effect line and red glow for a warning or unavailable
condition. Outlines may be fixed, switch-based, or dynamically colored; every rule needs a
stable priority because the highest-priority active rule wins. Whether a rule remains visible
while the Card is unplayable must be an explicit semantic choice, not an adapter default.

Keep dynamic predicates cheap and side-effect-free because outline state may refresh every
frame. The recipe must define no-active-rule, one-active-rule, and conflicting-rule results.
Prove activation, deactivation, priority resolution, changes in Card playability, hover/drag,
and hand enter/leave cleanup. A headed check must confirm that the emphasis is legible but
does not obscure cost, art, text, rarity, selection, or native playable-state feedback.

#### 2C. Extra corner amount labels

Allow bounded supplemental labels on Relic, Power, and Intent hosts through their public
provider surfaces. These labels supplement, rather than replace, the vanilla amount/value
counter. The semantic shape must declare host, corner/custom slot, plain or rich text,
update trigger, and removal condition. Set conservative limits on label count and text
length before exposing multiple slots.

Use the RitsuLib invalidation events when underlying state changes without a normal host
display event; do not poll every frame. Prove zero/one/multiple labels, rich-text formatting,
state-driven update, removal, host destruction, and combat transition cleanup. Headed checks
must cover common aspect ratios and crowded Relic/Power/Intent cases, preserve the vanilla
counter, and reject overlap with native icons, tooltips, or adjacent labels.

### Package 3 - Owned custom Rest Site options

**Semantic intake.** Model the option as an action contributed by one generated-Mod-local
Card, Relic, or Modifier. Declare its localized title/description, owner, eligibility,
repeatability, enabled/disabled rule, optional icon, cost, and asynchronous outcome. Separate
absence (the owner is ineligible) from visible-but-disabled (the option exists but cannot be
paid for or used now).

**RitsuLib route and outcome.** Implement the action with `ModRestSiteOptionTemplate` and
have the owner contribute it through `TryModifyRestSiteOptions`. Prevent duplicate insertion
when the host rebuilds or revisits its option list. `IsEnabled` must match the same payment
predicate used at click time, and a disabled option must use the native grayed-out state.
Resolve cost and outcome atomically: if payment or final eligibility fails, neither side may
partially apply. Await the complete outcome before returning control to the Rest Site, then
apply the declared stay/leave behavior. A missing or invalid custom icon must fall back to a
checked native presentation rather than hiding or breaking the option.

**First proof matrix.** In the real Rest Site host, prove absent, present-and-disabled, and
present-and-enabled states; a failed payment; a successful click with structured resource
and outcome deltas; option-list rebuild without duplication; return to or departure from the
Rest Site; and a second visit according to the repeatability contract. Headed checks cover
localization, icon fallback, gray state, controller focus, and coexistence with native Rest
Site options. This first package does not claim remote-player ownership or multiplayer
coordination.

### Package 4 - Combat-only custom CardPile / ExtraHand

This is the highest-risk package because it combines Card ownership, command ordering,
targeting/payment, UI, cancellation, and combat cleanup. Keep the first slice singleplayer,
generated-Mod-local, visible, and strictly `ModCardPileScope.CombatOnly`.

**Registration and semantics.** Register the pile with `.CardPileOwned(...)` under a stable
ID. Supply `.title`, `.description`, and `.empty` hover-tip localization. The SPEC must state
how Cards enter and leave, top/bottom ordering, whether duplicates are allowed, fixed
capacity, overflow behavior, what an empty pile displays, and where each non-play result
goes. Move Cards through normal CardPile/command lifecycle APIs; do not retain played Card
instances in an ad hoc collection or mutate backend piles directly.

**ExtraHand presentation and play.** Use RitsuLib's native Card holders, hover/tooltips,
controller focus, and playable glow. Start with one fixed reviewed anchor and either the
default `VanillaHand` layout or one bounded Horizontal/Vertical layout; do not expose
arbitrary layout callbacks in the first recipe. Manual play is optional per pile. When it is
enabled, preserve normal targeting, payment, play hooks, action queue, and result-pile
processing, including RitsuLib's temporary bridge through the backend vanilla Hand.

**Cancellation and cleanup.** If targeting is canceled or a queued play is canceled before
commit, restore the exact Card to its source pile at a deterministic position without
double payment, duplicated triggers, or a lost Card. On success, follow the declared normal
result pile rather than returning the Card automatically. Combat end must clear the pile,
detach UI and subscriptions, and leave no state for the next combat; a second combat is a
required clean-start proof.

**First proof matrix.** Cover empty/one/full/overflow states; deterministic add, remove, and
order; non-play movement; mouse/controller hover and focus; playable/unplayable glow;
single- and multi-target manual play if both are claimed; payment failure; target cancel;
queued-action cancel; successful Play -> result pile; combat-end cleanup; and second-combat
reset. Structured evidence proves Card IDs, pile membership/order, payment, hooks, and result
pile. Headed checks prove anchor stability, text/tooltips, expanded layout, targeting, and no
overlap with native Hand, Energy, draw/discard piles, powers, or the fixed Character resource
control.

**Not in the first slice.** `RunPersistent` piles, multiplayer or remote-player UI, vanilla
pile replacement, arbitrary custom layout callbacks, hidden retained-card zones, and changes
to the normal lifecycle of unrelated source Cards remain unsupported.

### Package 5 - Custom Character dialogue in native Ancient scenes

This package adds Character-specific dialogue to cataloged vanilla Ancient encounters while
preserving their native event model, scene, background, options, rewards, and progression.
It is a Character capability, not an M6.7 vanilla replacement: the generated Mod contributes
a new dialogue branch for its own Character instead of changing dialogue used by existing
Characters. Keep the first slice singleplayer and separate from custom Ancient creation or
layout authoring.

**Semantic intake.** Add an optional Character dialogue block keyed by a natural-language
Ancient name resolved through a pinned STS2 `0.107.1` Ancient catalog. Each dialogue group
declares its first/repeat or explicit visit rule and contains ordered lines with speaker
(`Character` or `Ancient`), text, and the transition prompt after each non-terminal line.
Architect groups additionally declare the bounded start/end attacker presentation as
`None`, `Player`, `Architect`, or `Both`. The SPEC stores these meanings, not raw localization
keys, line indexes, `r` suffixes, or enum strings.

**RitsuLib route and localization.** Compile the semantic groups into the flat
`ancients.json` shape
`<ANCIENT_ENTRY>.talk.<CHARACTER_ENTRY>.<DIALOGUE_INDEX>-<LINE_INDEX>.<speaker>` and matching
`.next`, repeat, visit, and Architect attacker entries. Rely on RitsuLib's registered
`AncientDialoguePopulateLocKeysPatch` to append these lines to the native
`AncientDialogueSet`; generated Mods must not emit their own Harmony/reflection injection.
Continue supplying the Character's public `NameColor`, `GetArchitectAttackVfx()`, and a
complete Architect dialogue. The debug-only missing-Architect fallback is diagnostic
recovery, not a production fallback.

Validate target and Character entry IDs, contiguous dialogue and line indexes, one repeat
mode per group, a transition prompt for every non-terminal line, no orphan metadata, bounded
supported rich-text tags, and identical structural keys across shipped languages. Resolve
unknown or ambiguous Ancient names as interview/build errors. Do not expose line-level SFX
in the first slice because production audio remains unsupported.

**First proof matrix.** Contract checks load each generated localization table through the
pinned parser and assert exact dialogue count, line order/speaker, visit routing, repeat
mode, transition prompts, and Architect start/end attackers. A maintained `RunStart` or
`MapNode` Ancient harness must select the exact custom Character and sweep every cataloged
vanilla Ancient target, proving that its Character-specific dialogue resolves once and that
the encounter returns to its normal options/outcome after the final line. Cover first and
repeat visits and a missing/invalid-key negative case without relying on the debug fallback.

Use headed review for one normal Ancient and The Architect. Confirm the native name banner,
Ancient/Character speech styling and Character color, text fit, mouse/controller progression,
normal option restoration, and untouched scene/background. The Architect proof additionally
checks the selected attack presentation, every referenced attack VFX, and clean run-end
progression. This promotes only dialogue in native Ancient scenes; custom Ancient models,
backgrounds/layouts, option/reward authoring, audio, and remote-player presentation remain
unsupported unless separately planned and proved.

### Proposed sequence and M6.6 completion

The preferred order is 2A computed previews and dynamic values, Package 5 native Ancient
dialogue, Package 1 targeting, Package 3 Rest Site options, 2B/2C hand and corner
presentation, then Package 4 CardPile / ExtraHand. This starts with semantic calculations
and localization-driven Character dialogue that have the smallest new lifecycle,
establishes reusable targeting before manual ExtraHand play, and leaves the combined
Card/UI/cancellation work until its prerequisites and proof patterns are stable. The human
lead may reorder packages or add other M6.6 features by updating this section first.

M6.6 may close only after every feature retained in its final approved scope is either
promoted through its own gate or explicitly removed/deferred by the human lead; all payloads
and active documents agree with the final support graph; outstanding verification exceptions
are recorded rather than counted as passes; and the human lead explicitly closes the
milestone. Until then, each unproved slice remains unsupported even if another slice in the
same package has shipped.

## M6.7 - Version-Bound Vanilla Content Overrides and Behavior Composition

M6.7 is the planned follow-on milestone for generated Mods that intentionally alter existing
base-game content. It is not limited to Card numbers: the target is a broad semantic system
for data, availability, behavior, and presentation changes across Cards, Relics, Potions,
Powers, Monsters/Encounters, and Events where the current authoring vocabulary and a grounded
host adapter can express the requested result.

M6.7 planning does not start implementation, and no M6.7 surface is currently supported.
Begin it only after the human lead selects the milestone. The scope may be refined as the
version catalog reveals real model shapes, but do not shrink the product goal to a small
handwritten whitelist merely because some targets need maintained adapters.

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
4. **Availability:** add, remove, move, or reweight an existing model in a declared pool,
   reward source, unlock surface, or multiplayer-availability surface.
5. **Disable acquisition:** stop new runs from obtaining content while retaining the model
   so old saves and existing run state remain readable. This is not physical model deletion.

Each operation must declare target model/category, operation mode, affected surface, desired
value or behavior, base and upgrade forms where applicable, localization effect, multiplayer
scope, and whether it is required or explicitly optional compatibility. `set` and `delta`
are distinct conflict semantics and must not be inferred from wording after SPEC approval.

### Version catalog and target grounding

Build a generated, reviewable vanilla-content catalog for every supported STS2 version. The
first catalog targets the existing pinned `0.107.1` host; supporting a later patch requires a
new catalog and proof, not silent reuse of old targets. The catalog should record, where
applicable:

- stable `ModelId`, concrete model type, content category, pool/source membership, rarity,
  costs, tags/keywords, target/result behavior, and multiplayer constraint;
- canonical named dynamic variables, their concrete types/value properties, base values,
  upgrade deltas, and localization placeholders;
- acquisition/unlock hosts, common public behavior entry points, and whether an existing
  open-mod recipe can express a complete replacement;
- checked target signatures and structural fingerprints for the narrow patch adapters that
  remain necessary; and
- known special consumers such as generated token Cards, Powers applied by a Card, enemy
  move/intent pairs, Event scenes, and cached pool/reward views.

Resolve natural-language names through this catalog and fail on ambiguity. A required edit
must check its expected target and baseline fingerprint before applying. Missing types,
changed signatures, unexpected canonical values, or incompatible variable types fail closed
with a useful diagnostic; do not guess a replacement target after a game update. Catalog
metadata is research/compatibility data, not permission to copy game source or assets into a
generated Mod.

### Layer 1 - Data, metadata, upgrade, and presentation overrides

The first promoted layer should cover broad balance-style edits rather than a few named
Cards:

- Card Energy/Star cost, named base and upgraded values, ordinary rarity, card type, tags,
  keywords, replay count, and other cataloged properties;
- target type and result pile only when the unchanged or replacement behavior is compatible
  with the new target/result lifecycle;
- ordinary Relic, Potion, Power, Monster, and move/intent values when they are exposed as
  properties or named variables, with maintained adapters for common literal-value shapes;
- generated-token and applied-Power routing, so a request against a source Card can resolve
  the actual model that owns the number; and
- matching title/description/tooltip changes when the original text does not already consume
  the modified variable.

Preserve the original typed `DamageVar`, `BlockVar`, computed value, and Power amount route so
normal Strength, Dexterity, Vulnerable, Frail, enchantment, and preview hooks still apply.
Baseline cost edits must occur before normal temporary/global cost modifiers rather than
overwriting their final result. Base, upgrade preview, upgraded instance, downgrade, clone,
transform, save/load, and card-library/reward consumers must all observe the same override.
Never ship a text-only or effect-only numeric edit.

Use RitsuLib default model capabilities and property contributors where they express the
semantic layer. Where no public property/variable override exists, route through a maintained
version-catalog adapter registered with `IPatchMethod`; do not generate a new patch shape for
each prompt.

### Layer 2 - Pool, reward, unlock, and availability overrides

Support declarative add/remove/move/reweight operations for cataloged content pools and
acquisition sources, including character/Colorless pools, Relic tiers, Potion/reward sources,
Neow/Ancient-style sources where grounded, unlock requirements, and bounded multiplayer
availability. Treat pool membership, appearance weight, unlock state, and owned-instance
behavior as separate fields.

This layer may edit existing availability and unlock metadata already owned by a cataloged
vanilla model or acquisition source. It does not schedule authoring new Story or Epoch
content, new progression tracks, or new unlock systems; those would be separate new-content
capabilities with their own persistence, presentation, and compatibility contracts.

Disabling newly added vanilla content removes its future acquisition routes but leaves the
model registered for existing saves. Moving or reweighting content must not duplicate it,
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
- **Relics, Potions, Powers, and Monsters:** use typed owner capabilities for additional
  hook behavior. A complete replacement must suppress only the cataloged original hook/use/
  move entry points through a maintained adapter, then run the generated hook vocabulary
  exactly once.
- **Conditions and cadence:** provide reusable semantic filters such as Card type, target
  side, source, threshold, first/Nth time per turn/combat, at most/exactly N, and enabled
  singleplayer/multiplayer scope. These cover common balance changes without target-specific
  code.
- **Monster/Encounter behavior:** support move damage, intent, sequence, fixed-turn openings,
  and bounded conditional selection through the existing grounded move vocabulary. Unusual
  AI state machines or animation-coupled transitions may use a cataloged target adapter.
- **Events:** support option eligibility, costs, rewards, and generated outcomes through the
  current Event recipes. Scene/layout replacement, unusual chains, or private async state
  machines remain target-adapter work rather than free-form patch generation.

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

Singleplayer proofs come first, but multiplayer is an intended M6.7 surface rather than a
permanent exclusion. Promote multiplayer per edit family only after all peers use an
identical override manifest and real-host evidence proves deterministic state, choices,
RNG, saves, remote presentation, and disconnect behavior where relevant.

### Proposed delivery sequence

1. Build the version catalog, name resolver, expected-baseline/fingerprint checks, and an
   emitted override manifest with no gameplay changes.
2. Promote Card data/metadata/upgrade edits, then matching localization and all normal Card
   consumers.
3. Promote acquisition disable plus Card/Relic/Potion pool movement and deterministic
   weighting.
4. Promote Card behavior composition/replacement by reusing current Card, Power, target,
   payment, and result-pile recipes.
5. Promote Relic/Potion/Power numeric and hook behavior, including reusable cadence/filter
   templates and checked suppression adapters.
6. Promote Monster/Encounter move edits, followed by bounded Event option/outcome edits.
7. Add multiplayer promotion per already-proved edit family; leave exceptional content on
   named catalog adapters instead of blocking the broad generic layers.

This sequence is a dependency order, not a requirement to wait for every content category
before promoting an independently proved earlier layer. Do not claim broad "vanilla editing"
from one sample Card: record the exact operation families and model categories that passed.

### Proof and M6.7 completion

Each promoted edit family needs deterministic before/after snapshots plus the nearest real
host. Data edits prove base/upgrade display and live effect, normal modifiers, clones,
downgrade, save/load, and a later combat. Availability edits prove fresh acquisition views,
RNG/order, duplicate absence, and existing-save survival. Behavior replacement proves the
original body was suppressed exactly once, the replacement executed exactly once, and
normal payment, targeting, hooks, history, result piles, rewards, and cleanup remain intact.
Monster/Event edits also require intent/option presentation and transition-state evidence.

Add negative tests for ambiguous names, wrong host version, baseline drift, missing patch
targets, overlapping edits, unsupported variable types, and conflicting replacements. A
headed check is required only for actual presentation claims; do not schedule a fresh full
acceptance Mod unless this plan is later amended to require one.

M6.7 may close when the final approved operation/category matrix is implemented, documented,
and represented accurately in the support graph; retained target adapters have current-host
proof; verification exceptions are recorded rather than counted as passes; generated
payloads agree; and the human lead explicitly closes the milestone. Targets outside that
matrix remain unsupported even though the architecture may make future adapters possible.

## Current Boundaries

M6.5 has no separate Character-sheet generation, locked-selection route, custom map
marker, Character trail, or `Cast` cue. Characters keep the checked game-native shared
map-marker fallback. Full-energy acquisition uses one Character-specific layer plus four
fixed templates. Combat cues remain the private, combat-only, all-or-nothing
`Idle`/`Attack`/`Hit`/`Dead` set; they do not promote Spine, animated merchant/rest-site
bodies, production audio/materials, or multiplayer presentation.

Locked-selection presentation, Character-specific card trails, additional combat cue
states, planned native custom-Character Ancient dialogue/presentation, custom Ancient
layouts, alternative Energy, arbitrary Event layouts/chains, and one-click Workshop
publishing remain unsupported. All provisional M6.6 surfaces and all planned M6.7
vanilla-override surfaces remain unsupported until their individual promotion gates pass.
Unversioned target guessing and arbitrary generated Harmony/reflection/IL remain outside
M6.7 entirely.

## Future Outlook

Optional Mod settings and persistence remain a later possibility outside the provisional
M6.6 package list. A future design may cover settings pages with toggles, sliders, choices,
and key bindings plus RitsuLib's Global, Profile, and run-owned save scopes. Generate these
only when a Mod request actually needs configuration or durable state; do not add a settings
page to every simple Mod. No implementation package is currently scheduled.
