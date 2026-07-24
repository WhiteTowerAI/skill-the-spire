# Current STS2 capability graph

This graph defines the active `0.6.0` RitsuLib-only support boundary. Historical framework
evidence is not an implementation option.

Support levels:

- **pipeline-supported:** natural-language intake through real hosted verification works;
- **scenario-verified:** a real proof exists, but the user pipeline does not select it;
- **unsupported:** preserve the idea as a gap.

## Pipeline-Supported

| Capability | Host | Active boundary |
|---|---|---|
| card / relic / potion / power | `CombatPlayer` | RitsuLib `Mod*Template`, exactly-once content-pack registration, explicit pools, checked art fallback |
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
| Character static art | Character hosts | selection portrait/background, top icon, combat/rest/merchant bodies, five-layer energy, compact icon |
| Character resource/payment/UI | two-combat Character | RitsuLib Secondary Resource, bool payment, public 220x32 fixed UI at offset 160, text fallback |
| ordered semantic buffer | two-combat Character | combat-attached semantic values, overflow/order/output/reset, normal source Play -> Discard |

## Static Art Contract

| Family | Normalized output | Verified consumers |
|---|---|---|
| card | card portrait profile | real Card views |
| relic / power / potion | content icon profiles | model and standard tooltip/inventory views |
| enchantment | 64x64 transparent PNG | Card tab and tooltip |
| orb | 100x100 transparent PNG | tooltip and trigger flash |
| monster | 360x360 transparent PNG | combat and default bestiary |
| Event | 3440x1613 opaque PNG | initial and explicit later page portraits |
| Character selection | 132x195 portrait; 1920x1200 background | real selection screen |
| Character identity/body | 88x88 top icon; 512x512 combat/rest/merchant | top panel and real hosts |
| Character energy | five 256x256 layers plus 24x24 compact icon | native energy scene and real hand Card |

Character custom-art acquisition uses one `CharacterArtBundle` as the source of dimensions,
alpha policy, output path, fallback, consumer, and review metadata. Selection art may
bootstrap the approved identity; every later Character acquisition requires that identity
alongside its type-matched style references. Bundle validation produces a labeled contact
sheet and a deterministic five-layer Energy composite outside runtime assets. This quality
contract does not promote the optional locked-selection or map-marker slots.

Every promoted family requires deterministic import, a checked fallback, packaging, and
headed evidence in the real consumer. A path assertion or successful `.pck` is not visual
proof. `gen_sprite.py` is framework-neutral; RitsuLib asset profiles own consumption.

## Scenario-Verified Only

The historical version-gated patch is not selectable by the current pipeline. Public
RitsuLib UI attachment and static Character profiles supersede its former active consumers.
Do not generate it.

## Unsupported

- retained played-card custom piles or custom-zone UI;
- alternative Energy hooks;
- run-persistent or remote-player Character resources/UI;
- multiplayer/replay Scry or global Scry modifiers/completion hooks;
- vanilla content editing or ungrounded patch targets;
- locked-selection/map-marker and native custom-Character Ancient presentation;
- production animation, materials, multiplayer presentation, and audio;
- arbitrary Event layouts/VFX, direct merchant/rest/treasure transitions, multiple
  special combats per mutable Event instance, or arbitrary forced chains;
- one-click Workshop publishing.

## Regression Rule

Add a case to the nearest host when practical. A separate project is allowed only when it
is the clearest maintainable shape. Fresh acceptance projects do not become permanent
fixtures automatically.
