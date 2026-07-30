# Current STS2 capability graph

This graph defines the active `0.6.0` RitsuLib-only support boundary. Historical framework
evidence is not an implementation option. A documented RitsuLib Package is supported when
its public API exists in the pinned profile. Confirmed problems are written as narrow known
limitations. Missing public routes are unsupported. Implementation and verification facts
are stated directly, without readiness levels or evidence badges.

## Supported

| Capability | Host / consumers | Active boundary and implementation |
|---|---|---|
| card / relic / potion / power | `CombatPlayer` | RitsuLib `Mod*Template`, exactly-once content-pack registration, explicit pools, checked art fallback |
| computed Card values | `CombatPlayer` | one bounded formula for preview/execution; computed Damage/Block, Energy/Star icons, raw/amount-given typed Power, localized variable tooltip |
| advanced creature targeting | `CombatPlayer` | deterministic Mod-local live-creature filters; native mouse/controller selection for Card one/many and Potion one; execution-time resolution checks; no multi Potion |
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

## Supported With Known Limitations

- RitsuLib advanced creature targeting supports its documented Card and Potion consumers,
  but custom multi-target Potions have a pinned lifecycle limitation: queued resolution can
  reach an empty group only after normal Potion consumption. The generator therefore stops
  at Card one/many and Potion one rather than emitting an unsafe workaround.

## Unsupported

- Card/Modifier-owned Rest Site options, variable/non-Gold costs, post-payment choices,
  arbitrary transactions, same-site repeat, and multiplayer Rest Site extensions;
- retained played-card custom piles or custom-zone UI;
- alternative Energy hooks;
- run-persistent or remote-player Character resources/UI;
- multiplayer/replay Scry or global Scry modifiers/completion hooks;
- arbitrary object/Card/map targets or global custom-target interoperability registration;
- ungrounded patch targets or arbitrary generated Harmony/reflection/IL;
- planned M6.7 version-bound vanilla content overrides until a documented public route is
  recorded for each requested operation/category;
- custom locked-selection/map-marker presentation;
- custom Ancient models, backgrounds, layouts, options/rewards, line audio, global
  dialogue replacement, arbitrary Ancient VFX, and multiplayer presentation;
- production animation beyond the bounded Idle/Attack/Hit/Dead cues, Cast, Spine, trails,
  arbitrary materials beyond the bounded pool-frame helper,
  multiplayer presentation, and audio;
- arbitrary Event layouts/VFX, direct merchant/rest/treasure transitions, multiple
  special combats per mutable Event instance, or arbitrary forced chains;
- one-click Workshop publishing.

## Regression Rule

Add a case to the nearest host when practical. A separate project is allowed only when it
is the clearest maintainable shape. Fresh acceptance projects do not become permanent
fixtures automatically.
