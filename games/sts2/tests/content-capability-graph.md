# Current STS2 capability graph

This graph defines the active Skill the Spire `0.2.0` RitsuLib-only support boundary. A documented
public RitsuLib feature family is supported when its API exists in the pinned profile and the
shipped pack owns a truthful authoring route. Confirmed problems are recorded as the smallest known
limitation. Operations outside this graph may still be authored as Mod-local routes from pinned
public APIs (`sts2api/grounding.md` § Mod-local Routes); they stay unverified until Tier 2 passes.

Framework expression, shipped authoring guidance, Build, real-host behavior, and headed
presentation are separate facts. A source or static check never makes an unrun shape
game-observed. A broken maintained route is a pack defect to repair; a generated Mod may use a
grounded Mod-local route meanwhile, never an ungrounded approximation or private patch.

The workflow retains adaptive fast/co-design/revision routing, direct resume, Character-native
grammar, mechanic/content/balance planning, concise DESIGN intent/scope, and proportional human
review. Those authoring behaviors do not add runtime support rows. Progression, post-run Badge,
Settings, Telemetry, Multiplayer, Update Check, broad asset/scene/animation/audio expansion, and
named typed interoperability remain outside the generalized `0.2.0` authoring surface. Existing
explicitly listed routes in adjacent domains remain available at their stated boundaries.

## Supported

| Capability | Host / consumers | Active boundary and implementation |
|---|---|---|
| card / relic / potion / power | `CombatPlayer` | RitsuLib `Mod*Template`, exactly-once content-pack registration, explicit pools, checked art fallback |
| computed Card values | `CombatPlayer` | zero or more independently named bounded formulas with per-value preview/execution parity; computed Damage/Block, Energy/Star icons, raw/amount-given typed Power, localized variable tooltips; generalized combinations game-unobserved |
| ordinary effect primitives | truthful Card/Potion/attached/model/Monster/world callbacks | authorable through one shared lowering reference for attack/effect damage; Block/healing/bounded HP; Power application/change/removal; Energy/Stars/Gold/potion capacity; draw; known-Card discard/exhaust; known combat-Card creation; known Card/Relic/Potion run acquisition; and Orb channel/evoke/slots. Surface pages own exact callback/context/owner/source/target projections and block missing inputs. Generated-Mod Build and real-host combinations remain unrun |
| custom-content model hook participation | `CombatPlayer`, `CombatEnemy`, `RunStart` | authorable: 66 public hooks on Card/Relic/Potion/Modifier, 45 on Power/Orb/Monster/Affliction, 66 on Enchantment including five mandatory `Enchant*` replacements, 32 on Run Global Effect, and 45 on Combat Global Effect. Three declaration shapes are cataloged (54 scalar-return, 6 out-replacement, 8 collection-edit); dispatcher-derived reachability is enforced at thin preflight, including exact Global Effect scope. Two Rest Site hooks remain route-owned. All generated hook shapes remain game-unobserved |
| Affliction | attached Card in `CombatPlayer` | authorable: `.Affliction<T>()`, `ModAfflictionTemplate`, Card validity, integer amount/stacking, `AfterApplied`/`BeforeRemoved`, attached `OnPlay`, combat hooks/capabilities, `CardCmd.Afflict`/preview/clear, bilingual text/tips, and optional overlay. Combat-only attachment and visuals remain game-unobserved |
| Modifier | custom/daily selection, `RunStart`, combat | authorable: good/bad registration, deterministic before/after-list placement, merged mutual-exclusion groups, `ModModifierTemplate`, new-run versus load lifecycle, saved model properties, Neow option, run/combat hooks, text/tips/icon, and Rest Site ownership. Setup, save/load, behavior, and headed UI remain game-unobserved |
| Global Effect | nearest Run or Combat host | authorable: `.Singleton<T>()` plus one explicit `HookedSingletonModel` Run/Combat stream, dispatcher-checked hook participation, scoped attached/saved state, exact reset/neutral behavior, and no process-listener ownership shortcut. Real dispatcher/reset behavior remains game-unobserved |
| model capabilities and shared effect services | Card/Relic/Potion/Power/Orb/Enchantment/Affliction/Monster owners; Character state/display; nearest combat/run hosts | authorable: stable capability registration; typed/default/runtime attachment; state/clone/save/display; ordered owner hooks; merge/subtract/replace; bounded play/combat/turn lifetime and Card-transform carry-over. Owner-bound per-hit attack, healing passes, Energy/Stars-gain response, and maximum hand size use their dedicated public services rather than the raw model-hook catalog. Process-wide registration is Global Effect-only. Generated host combinations remain game-unobserved |
| Card play lifecycle composition | real Card play/transform/UI consumers | authorable: before/after owner `OnPlay` with suppression result, next-play/this-turn/rest-of-turn/current-combat/current-play free resolution, completed-transform listeners and capability carry-over, ordered localized type-text replacement/wrapping, exact phase/neutral/cleanup contracts. Real play, transform, cost UI, bilingual rendering, and headed layout remain unrun |
| lifecycle, state, persistence, and deterministic RNG | selected model/combat/run/player/profile owners | authorable for included features: typed lifecycle subscriptions with replay/disposal, `AttachedState`, model/capability save, run/per-player save, profile/global/InMemory `ModDataStore`, migrations/cache invalidation, supplied-host or stable Mod run/player RNG streams. Lobby sync and all Progression/Settings/Telemetry/Multiplayer/Update Check uses are excluded. Real save/load, profile switch, event delivery, and RNG host behavior remain game-unobserved |
| Reward | native rewards screen / combat-room end | authorable: Mod-owned dynamic type, `ModCustomReward` description/icon/order, deterministic claim/refusal, source-generated typed payload and pending combat-room reconstruction, blocking `RewardsCmd.OfferCustom`, combat extra-reward insertion, successful-claim/continue lifecycle, and bounded choose-one/take-all linked sets. Real claim/cancel/reload/UI remain game-unobserved; Multiplayer integration is deferred |
| advanced creature targeting | `CombatPlayer` | deterministic Mod-local live-creature filters; native mouse/controller selection for Card one/many and Potion one; execution-time resolution checks; no multi Potion |
| custom Card Piles | matching combat/run and UI hosts | authorable as an independent surface through the complete documented public feature: combat/run scopes; Headless/TopBarDeck/BottomLeft/BottomRight/ExtraHand; preset/custom anchors; icon/hover/open/view/visibility/hotkeys; awaited native movement; localization; ExtraHand layout/manual play/callbacks. Newly selected hosts remain game-unobserved |
| Runtime UI | real top bar/input/Toast/Capstone/window/Catalog and exact stable public attachment hosts | authorable as one local Mod-owned workflow: top-bar definition and pure null-player-safe providers; transient/tracked Toast lifecycle; retained runtime hotkeys; `NetScreenType.None` Capstone; bounded Catalog/filter/detail/action behavior; floating-window geometry/content ownership; deterministic bounded local search expansion; fixed node attachment; Mod-scoped shell tokens and explicit cleanup. Real UI, input, focus, controller, layout, animation, drag/resize, theme, and cleanup remain game-unobserved. No deferred-family UI or integration is included |
| RitsuLib Card Hand Glow | Card hand | generated ordered fixed-color gold/red/custom rules, priority/tie order, and unplayable visibility; normal combat-state refresh boundary; human-led focused host review and Tier 1 passed; strict Tier 2 unrun |
| RitsuLib Extra Badges | Power, Relic, and Intent | generated Relics: up to three distinct safe corners; generated Powers: one top-left label because preset bands overlap in crowded rows; bounded plain/color text and explicit refresh/removal; Intent authoring outside active plan; human-led crowded-row review and Tier 1 passed; strict Tier 2 unrun |
| keyword | `CombatPlayer` | RitsuLib-owned native keyword, real Card text and no-icon tooltip, named behavior |
| enchantment | `CombatPlayer` | template/registration, persistent Card attachment, checked 64x64 icon |
| orb | `CombatPlayer` | template/registration, passive/evoke, checked 100x100 icon; Frost body/SFX fallback |
| bounded state-driven mechanics | selected owner/listener hosts | bounded scalar schema, exact owner and transition listener, declared lifetime/reset/persistence/visibility/consumers/outputs; run-save limited to Card/Relic/Enchantment `bool`/`int`/`string`; historical Relic cadence observed, generalized combinations game-unobserved |
| Monster/Encounter graph | selected `CombatEnemy` variants | separate registrations, explicit actual/all-possible rosters, reused/multiple/repeated Monsters, positive HP ranges, deterministic/conditional/fixed-weight-random move vocabulary, checked 360x360 combat+bestiary body; generalized variants game-unobserved |
| bounded content rich text | content host | per-surface vanilla allowlists with SmartFormat/keyword composition |
| Event / World Node | `MapNode` | pages/options, public Cmds, selections/rewards, one special combat per instance, bounded rich text/VFX/native presentation |
| Act | real singleplayer act transition, map, and room consumers | authorable: `.Act<T>()` plus exactly one explicit force/uniform/weighted entry policy; every candidate rejects multiplayer; weighted candidate weights are relative to the existing chapter's fixed weight 1; complete `ModActTemplate` gameplay members, deterministic map RNG, nonempty weak/regular/elite/Boss pools, ordinary Event/Ancient relations, localization, and checked scene/map/chest/audio assets. Entry, rooms, save/load, UI, and presentation remain game-unobserved |
| Ancient | native Ancient room / `MapNode` | authorable: new `ModAncientEventTemplate` registered exactly once as Shared or Act-scoped; `IsValidForAct`; all/initial option sets, event-supplied RNG, public outcome/page/`Done()` flow, localization-driven first-visit/exact-Character/`ANY` dialogue, bilingual text, and checked Event/map/history/stage/audio presentation. Native room, dialogue, choices, history, save/load, and headed presentation remain game-unobserved |
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
| existing vanilla public visual overrides | nearest Card/CardPool, Relic/Power/Potion/Orb, Act, Event/Ancient, Encounter, Affliction/Enchantment/Modifier consumers | supported: complete 44-provider RitsuLib `0.6.7` profile; exact Mod-local Material/texture/PackedScene/Spine/directory/list resources; matching raster normalization; typed/path vanilla fallback; cleanup and same-surface conflicts; selected Card and Darv providers were included in the earlier `0.5.4` built Mod accepted as a whole, while other providers remain unrun; no vanilla Monster-body external provider |
| existing vanilla Ancient extensions | native Ancient room | supported: nine pinned `AncientEventModel` targets; public multi-option append or one fixed fingerprinted complete initial-option replacement; nested conditions, visible/locked choices, fixed Gold/HP/Max HP costs, typed tips/relic presentation, ordered fixed effects, deck selectors, custom rewards, Mod-owned pages, native finish/choice history, full-language `events.json`, and separate visual overrides; selected Darv replacement/page/portrait was included in an accepted built Mod, while other routes remain unrun; Architect rejected as ordinary Event |
| existing vanilla availability | `ModelDb` pools and unlock consumers | supported: public 57-epoch gates for Card, Character, ordinary Event, and shared `EVENT.DARV`; fixed Relic/Potion epoch or permanent-disable filters; Card/Relic/Potion pool add plus remove/move membership; complete baselines, ordered simulation, primary-pool checks, debug/empty-transition rejection, existing-instance preservation, and singleplayer scope; selected Card pool move was included in the built Mod accepted as a whole, while cache/order/RNG/duplicate/save variants remain unrun |
| existing vanilla non-Card data and behavior | combat/run owner streams, concrete lifecycle hosts, `CombatEnemy`, ordinary Event room | supported: Relic/Potion/Power/Orb/Enchantment/Affliction/Monster typed owner capabilities with all 100 async hooks, 26 numeric hooks, 28 decisions, and four typed Orb callbacks; sixteen intrinsic data routes; complete checked lifecycle/body replacements; Monster move graphs; paired actual/all-possible Encounter rosters; complete ordinary Event options/pages and full-language `events.json`; singleplayer; selected Relic/Monster/Encounter routes were included in the built Mod accepted as a whole, while unselected families remain unrun |

Intent is supported because it belongs to the documented Extra Badges API and its
public API exists. Its absence from the current implementation schedule does not change
that. An Intent badge adds information to one intent; it does not replace a separate effect
icon or the native multi-attack count.

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
Character applies the reviewed public RitsuLib `VisualNodeStyle`; missing custom art returns to
the resolved profile fallback. Generated Mods keep automatic shader/path/size/resource
assertions, exact main/outline wiring, split Energy consumers, and the private combat cue set.
They never expose combat cues through `CharacterAssetProfile.VisualCues`, which would affect
merchant/rest playback.
This quality contract does not promote custom locked-selection or map-marker presentation.

Every promoted family requires deterministic import, a checked fallback, packaging, and
headed evidence in the real consumer. A path assertion or successful `.pck` is not visual
evidence. `gen_sprite.py` is framework-neutral; RitsuLib asset profiles own consumption.

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
  A complete lifecycle replacement can suppress them only with empty effect lists;
  async `OnPlay` replacement and public owner-hook composition retain their full routes.

## Unsupported

- variable/non-Gold Rest Site costs, post-payment choices, arbitrary transactions, same-site
  repeat, and multiplayer Rest Site extensions;
- alternative Energy hooks;
- remote-player Character resources/UI;
- arbitrary object/Card/map targets or global custom-target interoperability registration;
- ungrounded patch targets or arbitrary generated Harmony/reflection/IL;
- every vanilla override operation outside the promoted public Card, public visual,
  existing-Ancient, availability, and non-Card data/behavior routes until its specific
  public/adapter route and semantic recipe are maintained; vanilla
  Monster-body visual override has no public external route in RitsuLib `0.6.7`;
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
- behavior-bearing arbitrary Event layouts/VFX beyond the maintained visual resources,
  direct merchant/rest/treasure transitions, multiple
  special combats per mutable Event instance, or arbitrary forced chains;
- one-click Workshop publishing.

## Regression Rule

Add a case to the nearest host when practical. A separate project is allowed only when it
is the clearest maintainable shape. Fresh acceptance projects do not become permanent
fixtures automatically.
