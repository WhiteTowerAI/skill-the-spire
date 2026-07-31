# Implementation plan: 0.6.0 stabilization

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

M6.6 is closed by explicit human-lead decision. Packages 1, 2A, 2B, 2C, 3, and 5 are
implemented with their literal focused results and exceptions recorded under
`documents/history/`. Package 4 remains a repository-only experiment because its working
implementation requires a private RitsuLib lifecycle repair; it is not supported or
published. M6.7 work is not implemented until its scheduled development gates pass. Per
`AGENTS.md`, official Package semantics plus a public API in the pinned profile are enough
for support, while confirmed problems are recorded as limitations.

Do not prepare or claim a GitHub release. Closing M6.6 does not start M6.7 automatically.

## Dependency Boundary

- Generated Mods target STS2 `0.107.1` and `STS2.RitsuLib.Compat.0.107.1` `0.5.0`.
- Runtime manifests depend only on `STS2-RitsuLib >= 0.5.0`.
- Generated Mods must not reference, package, or depend on BaseLib or use historical
  Alchyr templates. Offline BaseLib/Downfall checkouts remain research-only.

## Current Runtime Architecture

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

Continue triaging bugs found through real user testing. No M6.5 gate remains scheduled.
On 2026-07-29, the human lead reported the headed Prismwright acceptance successful,
explicitly waived the remaining Tier 2/self-test harness, and directed retirement. The
load marker and runtime profile matched; the strict log parser separately reported only
engine-shutdown resource-leak messages after the headed session. M6.5 is closed by that
lead decision rather than by claiming those omitted checks passed.

M6.6 Package 2A completed on 2026-07-29 with its omitted strict Tier 2 harness recorded as
an exception. Package 5's first headed Darv/Architect proof failed: both scenes stopped
after their first visible line. The proof fixture and pipeline contracts are repaired, and
the rebuilt proof passed the human lead's headed Darv and Architect recheck. The current
log confirms the PCK load, both native routes, clean progression, and no fresh error block;
the absent structured state marker and `selftest done` remain an explicit strict Tier 2
exception. The focused proof project and deployed Mod were retired after recording this
evidence. Package 1 then passed its human-lead mouse/controller host matrix, with exact
single- and multi-target trigger records and no fresh target-Mod error. Its absent automated
`selftest done` and unrun queued-target-invalidation cases remain explicit strict Tier 2
exceptions. Package 3 then passed its human-lead native Rest Site matrix for absence,
disabled/enabled state, payment, exact outcome, repeatability, native-option coexistence,
controller focus, custom framing, and Heal-icon fallback. Per lead instruction, no log read
was performed; the exact Tier 1 log gate and strict `selftest done` remain exceptions. Do
not reopen these retired proofs or Prismwright, and do not start M7. Package 2B/2C then
passed its human-led hand/Relic matrix and, after narrowing Power authoring to one top-left
label, its crowded 16:9/16:10 Power-row recheck. Strict Tier 1 passed; strict Tier 2 was not
run. See `documents/history/M66_GAMEPLAY_READABILITY_RESULTS.md`. Package 4 was implemented
and passed its focused matrix only with a private RitsuLib lifecycle repair. Official
RitsuLib `0.5.0` does not satisfy the required manual-play lifecycle, so the human lead
retained it as a repository experiment, removed it from formal skills and payloads, and
closed M6.6 without a Package 4 support claim.

## M6.6 - Capability Expansion (Closed)

M6.6 is closed. Its completed formal scope is Packages 1, 2A, 2B, 2C, 3, and 5. Package 4
is retained only as repository research and is excluded from the support inventory and
published skills.

### Shared implementation and promotion rules

Use the Package-level rule in `AGENTS.md` for support decisions. Once official product
semantics identify a RitsuLib Package and the pinned `0.5.0` profile confirms its public
members, all documented public consumers are supported. Record a confirmed problem as the
smallest known limitation.

Before finishing a selected implementation slice, it must have:

1. a semantic interview/SPEC shape that describes player-visible intent rather than C# API
   names, including owner, lifetime, initial state, transitions, localization, and fallback;
2. one grounded `sts2-api` recipe and pinned RitsuLib `0.5.0` adapter route, without
   BaseLib, copied baseline code, private patches, or arbitrary generated reflection;
3. deterministic checks for calculations, filtering, ordering, payment, and state rules,
   plus build/manifest checks that preserve the RitsuLib-only dependency boundary;
4. the nearest representative real-game proof for each materially different lifecycle or
   presentation risk selected for this implementation, with structured post-state evidence
   for behavior and a headed check where targeting, controller focus, text fit, color, or
   non-overlap is the actual evidence claimed; and
5. updated source documentation and support graph, followed by regeneration and parity
   validation of both committed payloads.

An explicit human-lead decision may accept a focused manual host result in place of a
scheduled automated gate. Record that omission as a verification exception; never relabel
it as a strict Tier 2 pass.

Update `games/sts2/tests/content-capability-graph.md` when support or a known limitation is
grounded. State unfinished authoring or unrun verification directly instead of inventing a
status for it. Ordinary package work does not schedule another fresh natural-language
acceptance Mod; add such a gate to this plan first if the milestone later needs one.

### Package 1 - Advanced Card and Potion target types

**Implemented as of 2026-07-29 for Card one/many and Potion one.** Semantic
intake, SPEC, authoring, deterministic contract tests, pinned RitsuLib routes, and focused
real-host mouse/controller review cover the bounded slice. The human lead accepted zero-
target rejection, valid-target filtering, cancellation/payment behavior, native reticles,
normal result-pile/Potion lifecycle, exact observed deltas, and post-resolution cleanup.
The proof had Tier 1 and no fresh target-Mod error, but no automated `selftest done`;
queued selected-target invalidation and a queued multi Card losing every candidate were not
run and remain explicit verification exceptions. See
`documents/history/M66_ADVANCED_TARGETING_RESULTS.md`.

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
- A multi-target Card executes once with no selected creature. Its effect must call the
  appropriate `GetTargets(...)` extension at resolution time and apply the effect exactly
  once to each returned creature.
- Cancellation or loss of all valid targets must not spend resources, consume a Potion, or
  strand a Card outside its normal lifecycle. Successful execution must retain the normal
  Card result-pile and Potion-use behavior.

**Pinned-profile boundary found during implementation research.** On STS2 `0.107.1` with
RitsuLib `0.4.67`, `potion + many` cannot satisfy the zero-target consumption rule:
`UsePotionAction` accepts the multi-target `null` target and does not recheck
`PassesCustomUsabilityCheck` before `OnUseWrapper` removes the Potion. The first slice
therefore supports single-target Card, single-target Potion, and multi-target Card only.
Custom multi-target Potion authoring has a pinned lifecycle limitation until a grounded
RitsuLib change and version update add execution-time zero-target cancellation. Generated
Mods must not compensate with Harmony, reflection, IL, or remove-then-restore behavior.

**First proof matrix.** Prove a source-aware single-target Card, a single-target Potion, and
a player-aware multi-target Card rather than inferring one lifecycle from another. Cover
zero, one, and multiple legal candidates; mouse/controller selection where applicable;
cancellation; a candidate becoming invalid; and an exact structured list of affected
creature IDs and state deltas. Visually check the reticle/selection affordance and confirm
that invalid creatures cannot be selected.

**Not in the first slice.** Arbitrary object targeting, selecting Cards or map nodes,
retargeting dead creatures, global interoperability registration for other Mods, and custom
targeting UI layouts remain unsupported because no matching documented public route is
grounded in the pinned profile. A future API review may add supported routes before any
implementation work is scheduled.

### Package 2 - Gameplay readability

This planning group contains three separately scheduled feature Packages. Implementing one
does not implement another. Support still follows the documented RitsuLib Package boundary
rather than per-consumer proof gates.

#### 2A. Computed previews, icon variables, and variable tooltips

**Implemented as of 2026-07-29.** Semantic intake, SPEC, authoring, a
grounded RitsuLib `0.4.67` recipe, and deterministic contract checks now cover this slice.
The focused `ComputedValuesProof` host established live changing text, modifier-aware
Damage/Block, neutral Energy/Star gains, typed Poison amount-given behavior, formatter
boundaries, reflow, and localized null-icon tooltips. The human lead accepted every headed
and behavior case. No structured `selftest done` harness was run, so strict Tier 2 remains
an explicit exception. This promotion does not include 2B or 2C.

Extend semantic card text so one declared calculation feeds both the displayed dynamic
value and the live effect. Route damage and block through `ComputedDamage` and
`ComputedBlock` so previews continue to receive normal Strength, Dexterity, Vulnerable,
Frail, enchantment, and preview-hook adjustments. Use an untyped plain computed value only
for numbers that intentionally do not pass through damage/block or Power-application hooks.

- Add `ComputedEnergy` and `ComputedStars` for runtime-changing Energy and Star icon counts.
  Ground localization on the pinned formatter contract (`energyIcons()` and `starIcons()`);
  the obsolete local `{X:stars()}` wording must never return to generated recipes.
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
then record an outcome equal to that final preview. For Energy/Stars, prove zero-valued
rendering, multiple icons, tooltip rendering, and text reflow without clipping or stale
glyphs.

#### 2B. Conditional hand glow and outline

The official Card Hand Glow tutorial defines conditional vanilla gold/red meaning,
arbitrary colors, priority, and the unplayable-Card visibility choice. The pinned RitsuLib
source confirms the public family, so it is supported. The work below adds the open-mod
authoring route and verifies it in game.

**Implementation status (2026-07-30):** semantic intake, the grounded authoring reference,
Card recipe/author routing, and static contract coverage are implemented. The focused
real-host review is reserved for the human lead and remains open; no headed or strict Tier 2
result is claimed yet.

Add declarative hand emphasis only when it communicates an actionable state. Use gold glow
for an active bonus or stronger effect line and red glow for a warning or unavailable
condition. The generated slice uses ordered fixed-color rules; every rule needs a stable
priority because the highest-priority active rule wins, with later-listed rules winning a
tie. Whether a rule remains visible while the Card is unplayable must be an explicit
semantic choice, not an adapter default.

Keep predicates cheap and side-effect-free. Generated fixed rules do not poll every frame;
their conditions must change through normal combat-state refreshes. The recipe must define
no-active-rule, one-active-rule, and conflicting-rule results.
Prove activation, deactivation, priority resolution, changes in Card playability, hover/drag,
and hand enter/leave cleanup. A headed check must confirm that the emphasis is legible but
does not obscure cost, art, text, rarity, selection, or native playable-state feedback.

#### 2C. Relic and Power extra corner amount labels

Extra Badges is supported for Power, Relic, and Intent: the official tutorial supplies
product semantics for all three consumers and the pinned source confirms their public
provider/change-source surfaces. This implementation covers Relic and Power only. Intent
remains outside the schedule by human-lead decision.

**Implementation status (2026-07-30):** semantic intake, the grounded Relic/Power reference,
recipes/author routing, static contract coverage, and focused host review are complete. The
human-led review passed the hand-emphasis and Relic cases, then found that multiple Power
preset bands overflowed an adjacent Power in a crowded 16:9 row. Power authoring was
narrowed to one top-left supplemental label; the rebuilt proof passed the 16:9/16:10
Power-row recheck and strict Tier 1. Strict Tier 2 was not run. See
`documents/history/M66_GAMEPLAY_READABILITY_RESULTS.md`.

Allow bounded supplemental labels on Relic and Power hosts through their public provider
surfaces. These labels supplement, rather than replace, the vanilla amount/value
counter. The generated semantic shape declares host, one of three distinct safe preset
corners, plain or bounded-color text, update trigger, and removal condition. It permits at
most three labels, limits visible text to 4 characters on Relics and 6 on Powers, and does
not expose bottom-right or arbitrary custom rectangles through normal authoring.

Use the RitsuLib invalidation events when underlying state changes without a normal host
display event; do not poll every frame. Relics may use up to three distinct
top-left/top-right/bottom-left labels. Powers may use one top-left supplemental label; the
pinned preset bands are not clipped, so do not combine Power corners or generate a custom
rectangle as an unproved workaround. Prove Relic zero/one/multiple and Power zero/one,
rich-text formatting, state-driven update, removal, host destruction, and combat transition
cleanup. Headed checks must cover common aspect ratios and crowded Relic/Power cases,
preserve the vanilla counter, and reject overlap with native icons, tooltips, or adjacent
labels.

Intent authoring remains removed from active M6.6 work by human-lead decision on 2026-07-30;
that scheduling decision does not make the public Extra Badges consumer unsupported. Its official
meaning is auxiliary same-intent information such as additional triggered hits. A separate
debuff or other visible effect keeps its own native intent, and an ordinary repeated
identical attack keeps the native multi-attack intent. Adding an Intent recipe remains a
future pipeline task and does not start with this Relic/Power implementation.

### Package 3 - Owned custom Rest Site options

**Semantic intake.** Model the first supported slice as an action contributed by one
generated-Mod-local Relic. Declare its localized title/description, owner, eligibility,
repeatability, enabled/disabled rule, optional icon, cost, and asynchronous outcome.
Separate absence (the owner is ineligible) from visible-but-disabled (the option exists but
cannot be paid for or used now). Card/Modifier owners remain outside this slice.

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

**Implemented (2026-07-30).** The bounded Relic-owned singleplayer slice is available.
`M66RestSiteProof` passed the human lead's native absent/gray/enabled/payment/outcome/list-
rebuild/repeatability/controller/custom-icon/fallback matrix. The `gold` console command on
the pinned host ignores negative values, so the lead used normal Shop spending to establish
the insufficient-Gold state. No post-session log read or strict structured harness ran;
those remain explicit exceptions. See
`documents/history/M66_REST_SITE_OPTIONS_RESULTS.md`.

### Package 4 - Combat-only custom CardPile / ExtraHand (repository experiment)

The bounded implementation and focused evidence are retained under
`games/sts2/experimental/card-pile-extra-hand/` and
`documents/history/M66_CARD_PILE_EXTRA_HAND_RESULTS.md`. Its correct native manual-play
lifecycle requires a private RitsuLib repair. Because open-mod will not modify or ship
RitsuLib and official `0.5.0` does not provide that behavior, Package 4 is unsupported,
absent from formal `modmaker`/`sts2-api` routing, and excluded from plugin and portable
payloads. Commit `436f6cb` preserves the complete implementation snapshot for research.

### Package 5 - Custom Character dialogue in native Ancient scenes

**Implemented as of 2026-07-29 after repaired headed recheck.** The
semantic intake, pinned nine-target catalog, flat localization lowering, build preflight,
RitsuLib route, and deterministic contract checks are implemented. The first
`M66AncientProof` headed run exposed an unmounted localization PCK, an invalid proof-only
Energy asset prefix that broke native Event controls, and no Ancient Card for Darv's
unchanged Dusty Tome option. The repair mounts the PCK, uses a checked native proof asset,
registers a Mod-local Ancient Card, and adds regression contracts. In the rebuilt proof,
the human lead observed Mod-local text and normal progression through Darv and the
production Architect path. The current log confirms the PCK mount, two Darv entries, the
real final-act Architect transition, and no fresh error block. It does not contain the
structured state marker or `selftest done`, so strict Tier 2 is an explicit exception. This
package does not include custom Ancient content or global dialogue replacement.

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
unsupported because the current baseline has no matching documented public route. A future
API review may add supported routes before any implementation plan is added.

### M6.6 completion

Packages 1, 2A, 2B, 2C, 3, and 5 are complete with their literal verification results and
exceptions recorded. The human lead explicitly removed Package 4 from the formal support
and publication boundary and closed M6.6. The repository experiment is not a deferred
support promise. M6.7 remains planned and starts only after explicit human-lead selection.

## M6.7 - Version-Bound Vanilla Content Overrides and Behavior Composition

M6.7 is the planned follow-on milestone for generated Mods that intentionally alter existing
base-game content. It is not limited to Card numbers: the target is a broad semantic system
for data, availability, behavior, and presentation changes across Cards, Relics, Potions,
Powers, Monsters/Encounters, and Events where the current authoring vocabulary and a grounded
host adapter can express the requested result.

M6.7 planning does not start implementation, and no M6.7 surface is currently generated.
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
before finishing an earlier layer. Do not claim broad "vanilla editing" from one sample
Card: record the exact documented Package, operation families, model categories, and
verification that actually ran.

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
matrix remain unimplemented. Support them only after the official semantics and pinned
public route are known.

## Current Boundaries

M6.5 has no separate Character-sheet generation, locked-selection route, custom map
marker, Character trail, or `Cast` cue. Characters keep the checked game-native shared
map-marker fallback. Full-energy acquisition uses one Character-specific layer plus four
fixed templates. Combat cues remain the private, combat-only, all-or-nothing
`Idle`/`Attack`/`Hit`/`Dead` set; they do not promote Spine, animated merchant/rest-site
bodies, production audio/materials, or multiplayer presentation.

Locked-selection presentation, Character-specific card trails, additional combat cue
states, custom Ancient models/backgrounds/layouts/options/rewards, Ancient line audio and
global dialogue replacement, alternative Energy, arbitrary Event layouts/chains, and one-
click Workshop publishing retain their current unsupported boundaries. Remaining M6.6 work
and all planned M6.7 vanilla-override work are not yet implemented; missing proof alone does
not decide Package support.
Unversioned target guessing and arbitrary generated Harmony/reflection/IL remain outside
M6.7 entirely.

## Future Outlook

Optional Mod settings and persistence remain a later possibility outside the provisional
M6.6 package list. A future design may cover settings pages with toggles, sliders, choices,
and key bindings plus RitsuLib's Global, Profile, and run-owned save scopes. Generate these
only when a Mod request actually needs configuration or durable state; do not add a settings
page to every simple Mod. No implementation package is currently scheduled.
