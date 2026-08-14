# Current STS2 capability graph

This graph defines the active `0.7.0` RitsuLib-only support boundary. Historical framework
evidence is not an implementation option. A documented RitsuLib Package is supported when
its public API exists in the pinned profile. Confirmed problems are written as narrow known
limitations. Missing public routes are unsupported. Implementation and verification facts
are stated directly, without readiness levels or evidence badges.

M7 Design Intelligence and User Experience is closed authoring work, not a runtime capability.
The current workflow retains adaptive fast/co-design/revision routing, direct resume, pinned
Character-native grammar, mechanic/content/balance planning, concise DESIGN intent/scope, and
proportional human coherence review. These authoring behaviors do not add runtime support rows. A
future idea in DESIGN does not promote an unsupported operation into the current SPEC.

M7.6 closed through an external human-led Watcher whole-skill evaluation rather than a new
source Package. Its bounded build/Tier record, human observation that the Mod was playable
but not very good, overclaim findings, and unrun paths are recorded in
`documents/history/M76_WHOLE_SKILL_EVALUATION_RESULTS.md`. No copied-project observation
changes a support row without current pinned maintainer grounding.

M8 End-to-End Product Integrity is active. M8.0-M8.3 and M8.5 are closed; M8.5 retains unresolved
macOS installed-workflow and launcher-owned process cleanup exceptions. M8.7 closed by explicit
human-lead acceptance on 2026-08-14; its nine generalized families are preserved below. M8.8
closed by explicit human-lead acceptance on 2026-08-13 after its full RitsuLib `0.5.11` inventory,
WP1-WP5 implementation, WP8 source/static closeout, authorized plugin/portable payload delivery,
and final result record completed. Its newly generalized shapes remain game-unobserved.
M8.9 closed by explicit human-lead acceptance on 2026-08-14 after authoritative source/static
verification, synchronized payload delivery, and its result record completed. Its nine admitted
ordinary-effect families remain game-unobserved.
Progression, post-run Badge, Settings, Telemetry, Multiplayer, Update Check, WP6 asset/
scene/animation/audio/shared-presentation expansion, WP7 named typed interoperability, and new
interactions with those deferred groups are future work. Existing routes in those domains remain
preserved. M8.6 is eligible but remains unselected until its execution contract is explicitly
selected.

The current workflow uses one thin pre-Author check for shipped-route existence and raw model-hook
reachability. Build and real-host SelfTest prove implementation. Removing old workflow-management
schemas and validators changes no runtime row. A missing or broken maintained public/fixed route
blocks generation until repaired or narrowed instead of receiving a per-Mod approximation.

## Supported

| Capability | Host / consumers | Active boundary and implementation |
|---|---|---|
| card / relic / potion / power | `CombatPlayer` | RitsuLib `Mod*Template`, exactly-once content-pack registration, explicit pools, checked art fallback |
| computed Card values | `CombatPlayer` | zero or more independently named bounded formulas with per-value preview/execution parity; computed Damage/Block, Energy/Star icons, raw/amount-given typed Power, localized variable tooltips; generalized combinations game-unobserved |
| ordinary effect primitives | truthful Card/Potion/attached/model/Monster/world callbacks | authorable through one shared lowering reference for attack/effect damage; Block/healing/bounded HP; Power application/change/removal; Energy/Stars/Gold/potion capacity; draw; known-Card discard/exhaust; known combat-Card creation; known Card/Relic/Potion run acquisition; and Orb channel/evoke/slots. Surface pages own exact callback/context/owner/source/target projections and block missing inputs. Grouped pinned compile probe passed with 0 warnings/errors; generated-Mod Build and every real-host/game-observed combination remain unrun |
| custom-content model hook participation | `CombatPlayer`, `CombatEnemy`, `RunStart` | authorable: 66 public hooks on Card/Relic/Potion/Modifier, 45 on Power/Orb/Monster/Affliction, 66 on Enchantment including five mandatory `Enchant*` replacements, 32 on Run Global Effect, and 45 on Combat Global Effect. Three declaration shapes are cataloged (54 scalar-return, 6 out-replacement, 8 collection-edit); dispatcher-derived reachability is enforced at thin preflight, including exact Global Effect scope. Two Rest Site hooks remain route-owned. All generated hook shapes remain game-unobserved |
| Affliction | attached Card in `CombatPlayer` | authorable: `.Affliction<T>()`, `ModAfflictionTemplate`, Card validity, integer amount/stacking, `AfterApplied`/`BeforeRemoved`, attached `OnPlay`, combat hooks/capabilities, `CardCmd.Afflict`/preview/clear, bilingual text/tips, and optional overlay. Compile probe passed with 0 warnings/errors; combat-only attachment and visuals remain game-unobserved |
| Modifier | custom/daily selection, `RunStart`, combat | authorable: good/bad registration, deterministic before/after-list placement, merged mutual-exclusion groups, `ModModifierTemplate`, new-run versus load lifecycle, saved model properties, Neow option, run/combat hooks, text/tips/icon, and Rest Site ownership. Compile probe passed; setup, save/load, behavior, and headed UI remain game-unobserved |
| Global Effect | nearest Run or Combat host | authorable: `.Singleton<T>()` plus one explicit `HookedSingletonModel` Run/Combat stream, dispatcher-checked hook participation, scoped attached/saved state, exact reset/neutral behavior, and no process-listener ownership shortcut. Compile probe passed; all real dispatcher/reset behavior remains game-unobserved |
| model capabilities and shared effect services | Card/Relic/Potion/Power/Orb/Enchantment/Affliction/Monster owners; Character state/display; nearest combat/run hosts | authorable: stable capability registration; typed/default/runtime attachment; state/clone/save/display; ordered owner hooks; merge/subtract/replace; bounded play/combat/turn lifetime and Card-transform carry-over. Owner-bound per-hit attack, healing passes, Energy/Stars-gain response, and maximum hand size use their dedicated public services rather than the raw model-hook catalog. Process-wide registration is Global Effect-only. Pinned compile probe passed with 0 warnings/errors; all generated host combinations remain game-unobserved |
| Card play lifecycle composition | real Card play/transform/UI consumers | authorable: before/after owner `OnPlay` with suppression result, next-play/this-turn/rest-of-turn/current-combat/current-play free resolution, completed-transform listeners and capability carry-over, ordered localized type-text replacement/wrapping, exact phase/neutral/cleanup contracts. Pinned compile probe passed; real play, transform, cost UI, bilingual rendering, and headed layout remain unrun |
| lifecycle, state, persistence, and deterministic RNG | selected model/combat/run/player/profile owners | authorable for included features: typed lifecycle subscriptions with replay/disposal, `AttachedState`, model/capability save, run/per-player save, profile/global/InMemory `ModDataStore`, migrations/cache invalidation, supplied-host or stable Mod run/player RNG streams. Lobby sync and all Progression/Settings/Telemetry/Multiplayer/Update Check uses are excluded. Compile probe passed; real save/load, profile switch, event delivery, and RNG host behavior remain game-unobserved |
| Reward | native rewards screen / combat-room end | authorable: Mod-owned dynamic type, `ModCustomReward` description/icon/order, deterministic claim/refusal, source-generated typed payload and pending combat-room reconstruction, blocking `RewardsCmd.OfferCustom`, combat extra-reward insertion, successful-claim/continue lifecycle, and bounded choose-one/take-all linked sets. Pinned compile probe passed; real claim/cancel/reload/UI remain game-unobserved; Multiplayer integration is deferred |
| advanced creature targeting | `CombatPlayer` | deterministic Mod-local live-creature filters; native mouse/controller selection for Card one/many and Potion one; execution-time resolution checks; no multi Potion |
| custom Card Piles | matching combat/run and UI hosts | authorable as an independent surface through the complete documented public Package: combat/run scopes; Headless/TopBarDeck/BottomLeft/BottomRight/ExtraHand; preset/custom anchors; icon/hover/open/view/visibility/hotkeys; awaited native movement; localization; ExtraHand layout/manual play/callbacks. `0.5.11` compile probe passed; newly selected hosts remain game-unobserved |
| Runtime UI | real top bar/input/Toast/Capstone/window/Catalog and exact stable public attachment hosts | authorable as one local Mod-owned workflow: top-bar definition and pure null-player-safe providers; transient/tracked Toast lifecycle; retained runtime hotkeys; `NetScreenType.None` Capstone; bounded Catalog/filter/detail/action behavior; floating-window geometry/content ownership; deterministic bounded local search expansion; fixed node attachment; Mod-scoped shell tokens and explicit cleanup. Pinned `0.5.11` compile probe passed with 0 warnings/errors; real UI, input, focus, controller, layout, animation, drag/resize, theme, and cleanup remain game-unobserved. No deferred-family UI or integration is included |
| RitsuLib Card Hand Glow | Card hand | generated ordered fixed-color gold/red/custom rules, priority/tie order, and unplayable visibility; normal combat-state refresh boundary; human-led focused host review and Tier 1 passed; strict Tier 2 unrun |
| RitsuLib Extra Badges | Power, Relic, and Intent | generated Relics: up to three distinct safe corners; generated Powers: one top-left label because preset bands overlap in crowded rows; bounded plain/color text and explicit refresh/removal; Intent authoring outside active plan; human-led crowded-row review and Tier 1 passed; strict Tier 2 unrun |
| keyword | `CombatPlayer` | RitsuLib-owned native keyword, real Card text and no-icon tooltip, named behavior |
| enchantment | `CombatPlayer` | template/registration, persistent Card attachment, checked 64x64 icon |
| orb | `CombatPlayer` | template/registration, passive/evoke, checked 100x100 icon; Frost body/SFX fallback |
| bounded state-driven mechanics | selected owner/listener hosts | bounded scalar schema, exact owner and transition listener, declared lifetime/reset/persistence/visibility/consumers/outputs; run-save limited to Card/Relic/Enchantment `bool`/`int`/`string`; historical Relic cadence observed, generalized combinations game-unobserved |
| Monster/Encounter graph | selected `CombatEnemy` variants | separate registrations, explicit actual/all-possible rosters, reused/multiple/repeated Monsters, positive HP ranges, deterministic/conditional/fixed-weight-random move vocabulary, checked 360x360 combat+bestiary body; generalized variants game-unobserved |
| bounded content rich text | content host | per-surface vanilla allowlists with SmartFormat/keyword composition |
| Event / World Node | `MapNode` | pages/options, public Cmds, selections/rewards, one special combat per instance, bounded rich text/VFX/native presentation |
| Act | real singleplayer act transition, map, and room consumers | authorable: `.Act<T>()` plus exactly one explicit force/uniform/weighted entry policy; every candidate rejects multiplayer; weighted selection declares the existing-chapter baseline; complete `ModActTemplate` gameplay members, deterministic map RNG, nonempty weak/regular/elite/Boss pools, ordinary Event/Ancient relations, localization, and checked scene/map/chest/audio assets. Compile probe passed; entry, rooms, save/load, UI, and presentation remain game-unobserved |
| Ancient | native Ancient room / `MapNode` | authorable: new `ModAncientEventTemplate` registered exactly once as Shared or Act-scoped; `IsValidForAct`; all/initial option sets, event-supplied RNG, public outcome/page/`Done()` flow, localization-driven first-visit/exact-Character/`ANY` dialogue, bilingual text, and checked Event/map/history/stage/audio presentation. Compile probe passed; native room, dialogue, choices, history, save/load, and headed presentation remain game-unobserved |
| bounded forced Event | `MapNode` | finite prioritized Quest Card act-set/custom-Event mappings or sequences, saved index, exact terminal consumption, target pool exclusion, neutral hook returns, fail-closed conflicts; generalized variants game-unobserved |
| Character Foundation | `RunStart` + `CombatPlayer` | typed Character and pools, exact current-SPEC HP/Gold/MaxEnergy/Orb slots and starter Card/Relic/Potion multisets, Foundation fallback; generalized starts game-unobserved |
| Character static art | Character hosts | selection portrait/background, top icon, combat/rest/merchant bodies, five-layer energy, distinct large/text Energy icons; reviewed selection/combat visible footprint |
| Character card/UI theme | Character select + `CombatPlayer` | four named colors, cached deterministic pool-frame material, distinct 256x256 card and 24x24 rich-text Energy consumers |
| Character/Relic outlines | `CombatPlayer` | deterministic 3% opaque-white alpha expansion, inset-safe main normalization, exact main/outline wiring in real top-panel and Relic hosts |
| Character combat cues | `CombatPlayer` | private non-Spine Idle4/Attack4/Hit4/Dead6 sequences, shared geometry, one-shot/terminal routing, cleanup, all-or-nothing static fallback |
| Character dialogue in native Ancient scenes | `MapNode` / Character | nine pinned vanilla targets, Character-scoped first/visit/repeat groups, RitsuLib localization population, native scene/options/outcomes, complete Architect routing and attackers |
| Standalone/Card/Relic/Modifier Rest Site option | real Rest Site / `MapNode` | singleplayer; truthful exact owner/state handle; absent versus native-disabled; free/fixed Gold; deterministic preflightable outcome; once per site/run; native stay/leave; checked custom/Heal fallback. Standalone lowers to Run singleton with Player/run state; Modifier uses its selected run instance. Relic route observed; standalone/Card/Modifier game-unobserved |
| Secondary resources/payment/UI | selected Character/combat lifecycle | one or more bounded RitsuLib resources; combat/run and turn-start policies; fixed/X required/optional/extra payment ledger; selected built-in counter row/Card line or checked UI; generalized variants game-unobserved |
| Native custom-Card costs | `CombatPlayer` and Card UI | independent native Energy/fixed-or-X Star cost declarations and upgrades; no parallel Star store; combined/X variants game-unobserved |
| Event acquisition/shake profiles | `MapNode` | ordered unique known Card/relic acquisition with matching native consumer; one optional `weak_short`/`strong_normal` setting-respecting shake; generalized list/strong profile game-unobserved |
| ordered semantic buffer | two-combat Character | combat-attached semantic values, overflow/order/output/reset, normal source Play -> Discard |
| vanilla override grounding kernel | offline metadata + `ModelDb`/localization host | supported: pinned `0.107.1` catalog with 1624 vanilla models, 1580 stable title sources, checked display titles across 14 languages, and exact assembly identity; exact internal/localized-title alias resolution with explicit ambiguity; semantic manifest; baseline/fingerprint/conflict validation; final regression/payload/installed-plugin build passed, while the separate current-catalog headed no-op remains unrun |
| existing vanilla Card public overrides | `CombatPlayer` plus Card library/reward views | supported: public type/rarity/target, appended tags, evaluated Energy/Star cost, playability/result pile, title/description/type text, hover tips, native gold/red glow, capability variables, `OnPlay` before/after/replacement, and owner draw/discard/exhaust composition; representative Strike routes were included in the built Mod accepted as a whole, while unselected operations remain unrun |
| existing vanilla public visual overrides | nearest Card/CardPool, Relic/Power/Potion/Orb, Act, Event/Ancient, Encounter, Affliction/Enchantment/Modifier consumers | supported: complete 44-provider RitsuLib `0.5.11` profile; exact Mod-local Material/texture/PackedScene/Spine/directory/list resources; matching raster normalization; typed/path vanilla fallback; cleanup and same-surface conflicts; selected Card and Darv providers were included in the earlier `0.5.4` built Mod accepted as a whole, while other providers remain unrun; no vanilla Monster-body external provider |
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

- variable/non-Gold Rest Site costs, post-payment choices, arbitrary transactions, same-site
  repeat, and multiplayer Rest Site extensions;
- alternative Energy hooks;
- remote-player Character resources/UI;
- arbitrary object/Card/map targets or global custom-target interoperability registration;
- ungrounded patch targets or arbitrary generated Harmony/reflection/IL;
- every M6.7 vanilla override operation outside the promoted M6.7.1 public Card, M6.7.2
  public visual, M6.7.3 existing-Ancient, M6.7.4 availability, and M6.7.5 non-Card data/
  behavior routes until its specific public/adapter route, semantic recipe, and operation
  package are promoted; vanilla
  Monster-body visual override has no public external route in RitsuLib `0.5.11`;
- global acquisition weighting, Card/Character/Event permanent disable, act-owned Ancient
  epoch gating, multiplayer availability edits, and any reward/source weighting without an
  individually grounded route;
- custom locked-selection/map-marker presentation;
- global native Ancient dialogue/room replacement, new-Ancient behavior outside the public
  option/page/dialogue/presentation vocabulary, direct merchant/rest/treasure transitions,
  arbitrary behavior-bearing VFX, and multiplayer presentation;
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
