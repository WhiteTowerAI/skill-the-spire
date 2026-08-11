# Current STS2 capability graph

This graph defines the active `0.6.0` RitsuLib-only support boundary. Historical framework
evidence is not an implementation option. A documented RitsuLib Package is supported when
its public API exists in the pinned profile. Confirmed problems are written as narrow known
limitations. Missing public routes are unsupported. Implementation and verification facts
are stated directly, without readiness levels or evidence badges.

M7 Design Intelligence and User Experience is closed authoring work, not a runtime
capability. The human lead canceled standalone M7.0 and distributed behavioral cases to
the Packages that changed those behaviors. M7.1 adaptive Interview and routing is
implemented with fast,
co-design, revision, direct resume, and its six semantic routing scenarios. M7.2 native
design grammar is implemented with lazy Character-only grounding, a checked five-Character
starter inventory, exact native-shaped proposals, explicit fact/convention/decision
separation, and deliberate-departure handling. M7.3 mechanic, content-set, and balance
planning is implemented with independently lazy references, a compact planning capsule,
directed content relationships, formula/economy sensitivity, explicit open hypotheses, and
a Mod-forward working-value bias bounded by meaningful choices and real costs. These three
Packages change no row in this runtime graph. M7.4 adaptive DESIGN and design-to-SPEC
traceability are implemented with current/future scope dispositions, blocking gaps, and a
deterministic generation allowlist; M7.4 also changes no runtime row. A future vision
recorded in `DESIGN.md` does not promote an unsupported operation into the current
deliverable or `SPEC.md`. M7.5 proportional coherence review is implemented with accepted
identity anchors, six selected expression surfaces, fail-closed conflicts, deliberate
tension, and bounded revision impact queues. It also changes no runtime row and cannot
promote a new art, localization, Event, Character, or other operation.

M7.6 closed through an external human-led Watcher whole-skill evaluation rather than a new
source Package. Its bounded build/Tier record, human observation that the Mod was playable
but not very good, overclaim findings, and unrun paths are recorded in
`documents/history/M76_WHOLE_SKILL_EVALUATION_RESULTS.md`. No copied-project observation
changes a support row without current pinned maintainer grounding.

M8 End-to-End Product Integrity is active: M8.0 skill structure restructuring, M8.1 literal
deliverable contract, and M8.2 exact semantic capability conformance are closed; M8.3 is next
selectable. M8.0 reorganized shipped-pack structure, M8.1 added an artifact claim plus settlement
ledger, and M8.2 added maintained hook-participation authoring and static preflight. None changed a
runtime support row, and no surface gained or lost support through them.
M8.4 was removed; M8.5 and M8.6 retain their numbers. Deliverable, capability-preflight,
backtracking, and platform work add no runtime row by themselves. The Watcher observations
make Card behavior metadata, deck inspection/selection/movement, mechanic Hover Tips,
incoming/outgoing scalar modifiers, and launcher-owned process cleanup explicit M8 audit
inputs. A copied-project approximation or missing player-facing surface is not promotion
evidence. Runtime support remains the table below until pinned maintainer research, an exact
public/fixed route, semantic-conformance coverage, documentation, and payload validation
ground a selected reusable capability Package. M8 may also find that an existing row's
generated route fails its maintained contract; that route must then block generation until
repaired or recorded as the smallest exact limitation rather than being approximated per
Mod.

## Supported

| Capability | Host / consumers | Active boundary and implementation |
|---|---|---|
| card / relic / potion / power | `CombatPlayer` | RitsuLib `Mod*Template`, exactly-once content-pack registration, explicit pools, checked art fallback |
| computed Card values | `CombatPlayer` | one bounded formula for preview/execution; computed Damage/Block, Energy/Star icons, raw/amount-given typed Power, localized variable tooltip |
| custom-content model hook participation | `CombatPlayer`, `CombatEnemy`, `RunStart` | supported: 66 public `AbstractModel` hooks on Card/Relic/Potion, 45 on Power/Orb/Monster, 61 plus five mandatory `Enchant*` replacements on Enchantment, in three declaration shapes (54 scalar-return, 6 out-replacement, 8 collection-edit); reachability is decided per surface by the dispatching iterator's listener set and enforced at preflight, so a hook the surface cannot receive blocks instead of shipping as a method that never fires; declared guard/value/neutral-return plus `DynamicVar` rules-text binding; two Rest Site hooks route through `reference/rest-site-options.md` instead. **Both real-host proofs are unrun** — no generated override has been observed firing in a game, so every route here is implemented-and-unproved |
| advanced creature targeting | `CombatPlayer` | deterministic Mod-local live-creature filters; native mouse/controller selection for Card one/many and Potion one; execution-time resolution checks; no multi Potion |
| custom Card Piles | matching combat/run and UI hosts | complete documented public Package: combat/run scopes; Headless/TopBarDeck/BottomLeft/BottomRight/ExtraHand; preset/custom anchors; icon/hover/open/view/visibility/hotkeys; awaited native movement; localization; ExtraHand layout/manual play/callbacks |
| RitsuLib Card Hand Glow | Card hand | generated ordered fixed-color gold/red/custom rules, priority/tie order, and unplayable visibility; normal combat-state refresh boundary; human-led focused host review and Tier 1 passed; strict Tier 2 unrun |
| RitsuLib Extra Badges | Power, Relic, and Intent | generated Relics: up to three distinct safe corners; generated Powers: one top-left label because preset bands overlap in crowded rows; bounded plain/color text and explicit refresh/removal; Intent authoring outside active plan; human-led crowded-row review and Tier 1 passed; strict Tier 2 unrun |
| keyword | `CombatPlayer` | RitsuLib-owned native keyword, real Card text and no-icon tooltip, named behavior |
| enchantment | `CombatPlayer` | template/registration, persistent Card attachment, checked 64x64 icon |
| orb | `CombatPlayer` | template/registration, passive/evoke, checked 100x100 icon; Frost body/SFX fallback |
| stateful relic cadence | multi-combat `CombatPlayer` | saved attached run state plus native combat turn state |
| singleplayer Scry | `CombatPlayer` | generated-Mod-local top-X selector, stable retain/discard order, normal history/hooks; no global service |
| Monster + Encounter | `CombatEnemy` | templates, deterministic/conditional move vocabulary, checked 360x360 combat+bestiary body |
| bounded content rich text | content host | per-surface vanilla allowlists with SmartFormat/keyword composition |
| Event / World Node | `MapNode` | pages/options, public Cmds, selections/rewards, one special combat per instance, bounded rich text/VFX/native presentation |
| bounded forced Event | `MapNode` | solo Quest Card, one Unknown MapPoint, one target Event and act, token consumption/restored hooks |
| Character Foundation | `RunStart` + `CombatPlayer` | typed Character and pools, exact starters/HP/Energy, Foundation fallback |
| Character static art | Character hosts | selection portrait/background, top icon, combat/rest/merchant bodies, five-layer energy, distinct large/text Energy icons; reviewed selection/combat visible footprint |
| Character card/UI theme | Character select + `CombatPlayer` | four named colors, cached deterministic pool-frame material, distinct 256x256 card and 24x24 rich-text Energy consumers |
| Character/Relic outlines | `CombatPlayer` | deterministic 3% opaque-white alpha expansion, inset-safe main normalization, exact main/outline wiring in real top-panel and Relic hosts |
| Character combat cues | `CombatPlayer` | private non-Spine Idle4/Attack4/Hit4/Dead6 sequences, shared geometry, one-shot/terminal routing, cleanup, all-or-nothing static fallback |
| Character dialogue in native Ancient scenes | `MapNode` / Character | nine pinned vanilla targets, Character-scoped first/visit/repeat groups, RitsuLib localization population, native scene/options/outcomes, complete Architect routing and attackers |
| Relic-owned Rest Site option | real Rest Site / `MapNode` | singleplayer; absent versus native-disabled; free/fixed Gold; deterministic preflightable outcome; once per site/run; native stay/leave; checked custom/Heal-fallback icon |
| Character resource/payment/UI | two-combat Character | RitsuLib Secondary Resource, bool payment, public 220x32 fixed UI at offset 160, text fallback |
| ordered semantic buffer | two-combat Character | combat-attached semantic values, overflow/order/output/reset, normal source Play -> Discard |
| vanilla override grounding kernel | offline metadata + `ModelDb`/localization host | supported: pinned `0.107.1` catalog with 1624 vanilla models, 1580 stable title sources, checked display titles across 14 languages, and exact assembly identity; exact internal/localized-title alias resolution with explicit ambiguity; semantic manifest; baseline/fingerprint/conflict validation; final regression/payload/installed-plugin build passed, while the separate current-catalog headed no-op remains unrun |
| existing vanilla Card public overrides | `CombatPlayer` plus Card library/reward views | supported: public type/rarity/target, appended tags, evaluated Energy/Star cost, playability/result pile, title/description/type text, hover tips, native gold/red glow, capability variables, `OnPlay` before/after/replacement, and owner draw/discard/exhaust composition; representative Strike routes were included in the built Mod accepted as a whole, while unselected operations remain unrun |
| existing vanilla public visual overrides | nearest Card/CardPool, Relic/Power/Potion/Orb, Act, Event/Ancient, Encounter, Affliction/Enchantment/Modifier consumers | supported: complete 44-provider RitsuLib `0.5.4` Package; exact Mod-local Material/texture/PackedScene/Spine/directory/list resources; matching raster normalization; typed/path vanilla fallback; cleanup and same-surface conflicts; selected Card and Darv providers were included in the built Mod accepted as a whole, while other providers remain unrun; no vanilla Monster-body external provider |
| existing vanilla Ancient extensions | native Ancient room | supported: nine pinned `AncientEventModel` targets; public multi-option append or one fixed fingerprinted complete initial-option replacement; nested conditions, visible/locked choices, fixed Gold/HP/Max HP costs, typed tips/relic presentation, ordered fixed effects, deck selectors, custom rewards, Mod-owned pages, native finish/choice history, full-language `events.json`, and separate M6.7.2 visuals; selected Darv replacement/page/portrait was included in the built Mod accepted as a whole, while other routes remain unrun; Architect rejected as ordinary Event |
| existing vanilla availability | `ModelDb` pools and unlock consumers | supported: public 57-epoch gates for Card, Character, ordinary Event, and shared `EVENT.DARV`; fixed Relic/Potion epoch or permanent-disable filters; Card/Relic/Potion pool add plus remove/move membership; complete baselines, ordered simulation, primary-pool checks, debug/empty-transition rejection, existing-instance preservation, and singleplayer scope; selected Card pool move was included in the built Mod accepted as a whole, while cache/order/RNG/duplicate/save variants remain unrun |
| existing vanilla non-Card data and behavior | combat/run owner streams, concrete lifecycle hosts, `CombatEnemy`, ordinary Event room | supported: Relic/Potion/Power/Orb/Enchantment/Affliction/Monster typed owner capabilities with all 100 async hooks, 26 numeric hooks, 28 decisions, and four typed Orb callbacks; sixteen intrinsic data routes; complete checked lifecycle/body replacements; Monster move graphs; paired actual/all-possible Encounter rosters; complete ordinary Event options/pages and full-language `events.json`; singleplayer; selected Relic/Monster/Encounter routes were included in the built Mod accepted as a whole, while unselected families remain unrun |

The focused `ComputedValuesProof` host covered base/upgrade and live-input changes,
Strength/Vulnerable, Dexterity/Frail, Energy/Star zero and maximum formatting, exact neutral
resource gains, Snecko Skull raw-versus-applied Poison, tooltip fallback, clone survival,
and real hand-Card reflow. The human lead accepted the complete manual matrix. The proof
had a matching Tier 1 profile and no fresh target-Mod error, but no structured `selftest
done`; strict Tier 2 is a recorded exception, not a pass. See
`documents/history/M66_COMPUTED_VALUES_RESULTS.md`.

The first headed `M66AncientProof` Darv/Architect run exposed three proof defects and
stopped after the first visible lines. After repair, the human lead observed Mod-local text
and normal native progression in both routes. The current log confirmed the mounted PCK,
two Darv entries, the production Architect transition, clean run progression, and no fresh
error block. The structured state proof and `selftest done` were absent, so strict Tier 2
is a recorded exception rather than a pass. See
`documents/history/M66_ANCIENT_DIALOGUE_RESULTS.md`.

The focused `M66TargetingProof` host covered zero, one, and multiple legal candidates,
invalid-creature rejection, normal cancellation/payment, exact single Card/Potion deltas,
two-creature multi Card resolution, mouse/controller reticles, normal Card/Potion lifecycle,
and post-resolution cleanup. The human lead accepted all six headed groups. The current log
had matching Tier 1, exact target IDs/counts, and no fresh target-Mod error. It had no
automated `selftest done`, and queued-target invalidation was not run; strict Tier 2 is a
recorded exception, not a pass. See
`documents/history/M66_ADVANCED_TARGETING_RESULTS.md`.

The official RitsuLib `0.5.4` Package 4 proof used no consumer lifecycle patch. Setup
asserted native-Hand/ExtraHand holder separation, capacity, and overflow; the human lead
accepted target-cancel restoration, numbered-shortcut isolation, and consecutive mouse play
of all three ExtraHand Cards. A host save-backup cleanup error prevented strict Tier 1, and
no structured `selftest done` ran; strict Tier 2 was waived. Under the Package-level rule,
these verification facts do not narrow support to the one exercised UI consumer. See
`games/sts2/experimental/card-pile-extra-hand/official-v054-proof/RESULTS.md`.

The focused `M66RestSiteProof` host covered absent, gray, enabled, successful payment and
exact outcome, rebuilt native options, once-per-run hiding, controller focus, custom
256x169 framing, and native Heal-icon fallback. The human lead accepted the complete headed
matrix. Per lead instruction, no post-session log read or automated `selftest done` ran, so
the exact Tier 1 log gate and strict Tier 2 are recorded exceptions, not passes. The pinned
console ignores negative `gold` amounts; normal Shop spending established the low-Gold
state. See `documents/history/M66_REST_SITE_OPTIONS_RESULTS.md`.

Intent is supported because it belongs to the documented Extra Badges Package and its
public API exists. Its absence from the current implementation schedule does not change
that. An Intent badge adds information to one intent; it does not replace a separate effect
icon or the native multi-attack count.

M6.7.0 is infrastructure rather than a vanilla-edit claim. Its runtime collector produced
the same 1624-model snapshot and SHA-256 on repeated `0.107.1` host runs, strict Tier 1 and
structured Tier 2 passed, and an earlier pre-localization no-op scaffold built, deployed,
and passed Tier 1. The representative closure did not repeat a separate headed no-op for
the current localized catalog; the fresh nonempty acceptance Mod owns installed-plugin
scaffold/author/build, and that omitted no-op host remains an explicit unrun check.
The checked catalog currently has 4165 adapter fingerprints and promotes
`m6.7.1-public-card-overrides`, `m6.7.2-public-visual-overrides`,
`m6.7.3-existing-ancient-overrides`, `m6.7.4-availability`, and
`m6.7.5-non-card-data-behavior`. Of those fingerprints, 4141 are target-specific M6.7.5
methods and four are shared stream/flow boundaries. The final regression passed `165/165`;
Python compilation and six skill-root validations passed; plugin and portable payloads
were repeatable with 161 effective files each and zero differences; and the independent
installed-plugin Mod built with zero warnings/errors. On 2026-08-04 the human lead reported
that the representative Mod's effect test passed and explicitly closed M6.7; no individual
Card, Relic, Darv, Monster, or Encounter observation is inferred. Tier 1, Tier 2/SelfTest,
the current-catalog headed no-op, and all unselected
providers/hooks/families/availability/Event/save/multiplayer/cross-Mod paths remain unrun.
See `documents/history/M67_VANILLA_OVERRIDES_RESULTS.md` for the consolidated result,
`documents/history/M67_GROUNDING_KERNEL_RESULTS.md` for interim kernel evidence, and the
five `sts2-api/reference/vanilla-*-overrides.md` Package files for promoted contracts.

## Static Art Contract

| Family | Normalized output | Verified consumers |
|---|---|---|
| card | card portrait profile | real Card views |
| relic / power / potion | content icon profiles | model and standard tooltip/inventory views; exact generated Relic main/outline pair |
| enchantment | 64x64 transparent PNG | Card tab and tooltip |
| orb | 100x100 transparent PNG | tooltip and trigger flash |
| monster | 360x360 transparent PNG | combat and default bestiary |
| Event | 3440x1613 opaque PNG | initial and explicit later page portraits |
| Rest Site option | 256x169 opaque PNG | real native-button custom framing and Heal fallback |
| Character selection | 132x195 portrait; 1920x1200 background | real selection screen |
| Character identity/body | 88x88 top-icon main/outline; 512x512 combat/rest/merchant | top panel and real hosts |
| Character energy | five 256x256 layers, 256x256 large icon, 24x24 text icon | native energy scene, real hand Card, and formatted Card description |
| Character combat cues | eighteen 512x512 frames from four action sheets | combat-only Idle/Attack/Hit/Dead state machine; static `combat.png` fallback |

Character custom-art acquisition uses one `CharacterArtBundle` as the source of dimensions,
alpha policy, output path, fallback, consumer, and reference-family metadata. The required
selection portrait is the only identity bootstrap: combat/rest/merchant use it alongside
type-matched style references, while background/icon/Energy use a description-plus-portrait
palette/motif brief without passing the portrait as an image reference. Bundle validation
produces a labeled contact sheet and deterministic five-layer Energy composite outside
runtime assets. Energy layer 1 has one Character-specific generation call; the four
lead-supplied templates in `reference/energy_template/` map byte-for-byte to layers 2-5.
Selection normalization preserves the complete opaque source inside the 132x195 safe box.
Combat normalization pins alpha to the 512x512 content box/baseline and the generated
Character applies the reviewed public RitsuLib `VisualNodeStyle`; missing custom art still
returns to the resolved profile fallback. The focused Meridian host proof asserted exact
resource/alpha/screen bounds, clear UI regions, settled selection/combat screenshots, Tier
1, and no fresh error block.
The focused Meridian theme proof established the four named colors, deterministic cached
frame material, and both split Energy consumers; the maintainer's headed review passed all
seven visible checks. Generated Mods keep the automatic shader/path/size/real-consumer
assertions.
The focused Meridian outline proof established one shared alpha-derived rule, inset-safe
normalization, exact CharacterModel and asset-profile paths, both visible top-panel layers,
and the exact main/outline textures under one real `NRelic`; the maintainer's seven-point
headed review passed. Generated Mods retain these automatic resource/property/native-host
assertions.
The focused Meridian combat-cue proof established the four fixed frame/timing routes,
shared body/anchor geometry, Attack/Hit return to Idle, terminal Dead pose, cleanup, and the
one-missing-disables-all static fallback. The complete and fallback headed checks both
passed. Generated Mods keep the private combat set and never expose it through
`CharacterAssetProfile.VisualCues`, which would affect merchant/rest playback.
This quality contract does not promote custom locked-selection or map-marker presentation.

Every promoted family requires deterministic import, a checked fallback, packaging, and
headed evidence in the real consumer. A path assertion or successful `.pck` is not visual
proof. `gen_sprite.py` is framework-neutral; RitsuLib asset profiles own consumption.

## Retired Proof

The historical version-gated patch is not selectable by the current pipeline. Public
RitsuLib UI attachment and static Character profiles supersede its former active consumers.
Do not generate it.

The retired Character acceptance identity is not a reusable design, default deck,
verification marker, or player-facing example. Pre-M7 maintenance replaced it and its exact
proof values with `SPEC.md`-driven assertions while preserving historical evidence outside
the shipped generic instructions. A static regression prevents retired identities from
returning to the current skill source or payloads.

## Supported With Known Limitations

- RitsuLib advanced creature targeting supports its documented Card and Potion consumers,
  but custom multi-target Potions have a pinned lifecycle limitation: queued resolution can
  reach an empty group only after normal Potion consumption. The generator therefore stops
  at Card one/many and Potion one rather than emitting an unsafe workaround.
- Existing vanilla Card public overrides may append tags and compose description fragments
  before or after the original body. Canonical variable edits, tag removal, and
  base-description replacement remain unsupported because the pinned profile has no public
  route for those operations.
- Pinned Affliction `AfterApplied()` and `BeforeRemoved()` are synchronous `void` callbacks.
  A complete M6.7.5 lifecycle replacement can suppress them only with empty effect lists;
  async `OnPlay` replacement and public owner-hook composition retain their full routes.

## Unsupported

- Card/Modifier-owned Rest Site options, variable/non-Gold costs, post-payment choices,
  arbitrary transactions, same-site repeat, and multiplayer Rest Site extensions;
- alternative Energy hooks;
- run-persistent or remote-player Character resources/UI;
- multiplayer/replay Scry or global Scry modifiers/completion hooks;
- arbitrary object/Card/map targets or global custom-target interoperability registration;
- ungrounded patch targets or arbitrary generated Harmony/reflection/IL;
- every M6.7 vanilla override operation outside the promoted M6.7.1 public Card, M6.7.2
  public visual, M6.7.3 existing-Ancient, M6.7.4 availability, and M6.7.5 non-Card data/
  behavior routes until its specific public/adapter route, semantic recipe, and operation
  package are promoted; vanilla
  Monster-body visual override has no public external route in RitsuLib `0.5.4`;
- global acquisition weighting, Card/Character/Event permanent disable, act-owned Ancient
  epoch gating, multiplayer availability edits, and any reward/source weighting without an
  individually grounded route;
- custom locked-selection/map-marker presentation;
- new Ancient models, native opening-dialogue/room replacement, line audio, randomized
  outcome/RNG rewrites, special combat, direct merchant/rest/treasure transitions, Ancient
  behavior beyond the fixed M6.7.3 option/page/effect vocabulary, arbitrary behavior VFX,
  and multiplayer presentation;
- production animation beyond the bounded Idle/Attack/Hit/Dead cues, Cast, Spine, trails,
  generated or behavior-bearing materials/scenes outside exact promoted public resources,
  multiplayer presentation, and audio;
- behavior-bearing arbitrary Event layouts/VFX beyond exact M6.7.2 visual resources,
  direct merchant/rest/treasure transitions, multiple
  special combats per mutable Event instance, or arbitrary forced chains;
- one-click Workshop publishing.

## Regression Rule

Add a case to the nearest host when practical. A separate project is allowed only when it
is the clearest maintainable shape. Fresh acceptance projects do not become permanent
fixtures automatically.
