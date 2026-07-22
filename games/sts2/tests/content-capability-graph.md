# Current STS2 capability graph

This is the active support surface. Historical evidence rows and the M6 graph snapshot are
archived at `documents/history/content-capability-graph-through-m6.md`.

Support levels:

- **pipeline-supported:** natural-language intake through real hosted verification works;
- **scenario-verified:** a real host proof exists, but the generation/user path is not a
  current promise;
- **grounded:** API/host contract is known but not promoted;
- **unsupported:** preserve the idea as a pack gap.

Migration status is tracked independently from semantic support. As of 2026-07-22, R0-R3
are complete: the low-risk Card/Relic/Potion/Power/Keyword/Enchantment/Orb core has a
RitsuLib-only hosted proof. Monster/Encounter, Event, Character, state/resource, and buffer
rows retain their established semantic boundaries but are not RitsuLib-proven until R4/R5.

## Pipeline-supported

| Capability | Host | Required proof | Current boundary |
|---|---|---|---|
| card / relic / potion / power | `CombatPlayer` | real source play/use/hook changes state | RitsuLib content-pack registration and `Mod*Template`; explicit pool generic where applicable; checked asset-profile fallback |
| interaction | source host | source and dependent observations in dependency order | directed SPEC edge, not a `combo` type |
| keyword | `CombatPlayer` | membership, card text, no-icon hover tooltip, and named state change | RitsuLib-minted native keyword; text presentation supported; no owned bitmap/scene |
| enchantment | `CombatPlayer` | attachment, altered host behavior, and custom icon in card tab + tooltip | RitsuLib template/registration; one 64x64 loose PNG; checked missing-icon fallback |
| orb | `CombatPlayer` | channel/passive/evoke plus custom icon in smart tooltip + trigger flash | RitsuLib template/registration; one 100x100 loose icon; explicit Frost Spine scene/channel-SFX fallback |
| stateful relic cadence | multi-combat `CombatPlayer` | threshold/lifetime boundary; save round trip for run state | integer/bool relic state only |
| monster + encounter | `CombatEnemy` | encounter identity, move/history, exact state deltas, static body in combat+bestiary | one checked 360x360 loose PNG; explicit scene fallback; animation deferred |
| monster move vocabulary | multi-turn `CombatEnemy` | every declared cycle/branch and independent effect | deterministic/conditional branches |
| bounded content rich text | `CombatPlayer` | real Card body plus typed Card/relic/potion/power Hover Tip consumers; SmartFormat and auto-keyword composition | per-surface vanilla allowlists; titles/flavor/prompts plain; arbitrary markup deferred |
| event / World Node | `MapNode` | real UI for Cmd/page/selection/reward outcomes; custom encounter plus Resume/map semantics; visible portrait/VFX lifecycle; native rich-text host and page replacement; enabled typed option tips; exact-lethal HP/Max HP warning glow; native acquisition/shake/built-in VFX consumers | one special combat per Event instance; normal portraits, bounded `portrait_halo`, description rich text, typed enabled tips, lethal warnings, Card/relic acquisition presentation, `weak_short` shake, and curated `trial_noble` VFX supported; locked tips suppressed; normal-layout relic image, phobia/custom-layout/Ancient and arbitrary VFX deferred |
| bounded forced follow-up Event | `MapNode` via real Unknown MapPoint | no-token/wrong-act pass-through; forced room and target Event; visible target option; Quest token consumption; restored hook outputs | solo; one custom unplayable Quest Card, target Event, and specified act; target excluded from random pool; no arbitrary chains, fixed-node ordering, multiplayer, duplicate-token rewards, vanilla edits, or new save-roundtrip claim |
| character Foundation | `RunStart` + `CombatPlayer` | selection, pools/starters, HP/energy, hosted mechanic | static Character profiles are grounded and promoted independently; Foundation fallback remains valid |
| character static presentation | `RunStart` + `CombatPlayer` + `RestSite` + `Shop` | selection portrait/background, top-panel icon, static non-Spine combat/rest/merchant bodies, five-layer full energy, and compact counter icon | raw text scenes are packed by `build.py` without an editor; merchant uses one version-gated B-prefix; locked/map/Ancient retain explicit fallbacks or gaps |
| character resource/payment/UI | Character suite | gain/affordability/spend/rejection/reset plus fixed 220x32 icon+text counter and text-only fallback | combat-only, explicit payoff; not alternate Energy or arbitrary top-bar UI |
| ordered semantic buffer + dynamic output | Character suite | native source/compile destinations, visible order, overflow, output/history/effect/reset | semantic values only; source cards use native result piles |

## Scenario-verified infrastructure

| Capability | Boundary |
|---|---|
| typed capability kernel | Exact STS2 0.107.1 MVID-gated B postfix on `NCombatUi.Activate(CombatState)`; self-contained; no shared runtime |

## M6 Character presentation closeout

The custom-art pipeline is pipeline-supported for card, relic, power, potion, enchantment,
orb icons, static monster bodies, and normal event initial/page portraits. The Event slice
is complete at its grounded boundary, including one three-reference acquisition and real
headed render acceptance plus bounded host-native description rich text. Native-presentation
items 1-3 were closed by the 2026-07-20 `CanaryPresentation` proof: cross-content rich
text; enabled Event option Hover Tips and normal relic-backed text/metadata (locked tips and
normal-layout relic images remain deferred); and exact-lethal HP/Max HP warnings. Items 4-6
closed together in the final 2026-07-21 `CanaryNativePresentation` run: native Card/relic
acquisition previews, preference-respecting one-shot shake, and the curated built-in
`trial_noble` noncombat Event VFX. The final Character pass promoted selection, top-panel
icon, static non-Spine combat body, and compact resource icon profiles through the same
deterministic import path and a real headed Wayfinder run. That run also promoted the fixed
220x32 icon+text resource/ordered-buffer control with a checked text-only fallback. The
Event reference pool contains six reviewed, attributed samples selected from the actual
55-image local wiki.gg inventory.

The wider Downfall/BaseLib inventory is now explicit rather than implied. Locked selection
and map marker still need visible-host evidence. Select background, rest, merchant, and
background/rest/merchant consumers use raw text scenes packed by the bundled no-editor
fallback, while full energy uses BaseLib's loose-PNG legacy factory. The native Ancient name-banner, Architect speech
color, attack VFX, and four localization keys are source-grounded but not headed-proven for
a custom Character. M6's requested Ancient/Architect **research** gate is complete; those
runtime claims remain gaps, as do custom Ancient layouts and all Character animation.
Spine, move animation, arbitrary animated VFX, and animated transitions belong to the
later presentation expansion's animation track and do not block M6 or M7. Materials,
multiplayer presentation, and audio are parallel later tracks. The one code-native normal-Event
`portrait_halo` profile is already promoted through its existing `MapNode` host.

The separate `CanaryForcedEvent` proof added only the bounded public-hook follow-up row
above. With every remaining Character surface either promoted or assigned an exact
blocker/fallback, M7 is the next milestone.

Each promoted static family needs a copyable path/size/format contract, deterministic import and
placement into the `.pck`, and real headed visual proof in its existing host. If a dynamic
scene is animation-bearing, retain its fallback and route it to the later expansion rather
than claiming support.

### Pinned contract inventory

This inventory is grounded against STS2 `0.107.1`, BaseLib `3.3.5`, and the current game
`.pck`. `grounded` below is not a support claim: every candidate still needs the headed
proof listed in the last column. A single model may feed multiple independent player-visible
consumers; enumerate those consumers before deciding how many files and proofs it needs.

| Surface | Grounded asset and registration contract | Independent visible consumers | Honest fallback / current gate |
|---|---|---|---|
| keyword | No owned bitmap or scene. BaseLib's rich custom-keyword tooltip deliberately constructs `HoverTip(..., Texture2D: null)`; auto text is localized rich text. | Card description insertion and keyword hover tooltip. | **Presentation-supported:** `CanaryKeyword` rendered `Resonant` after the real hand-card description and the localized title/description in its hover tooltip, asserted `Icon == null`, captured both together, preserved Block `0 -> 7`, and passed strict Tier 2 with no fresh error on 2026-07-17. No `gen_sprite.py` spec is appropriate. |
| enchantment | One loose `64x64` `Texture2D` through an existence-checked `CustomEnchantmentModel.CustomIconPath`; `gen_sprite.py --spec enchantment` writes `images/enchantments/<slug>.png`. | Repeated `NCard` contexts use the same enchantment tab/amount renderer; `EnchantmentModel.Icon` also feeds the card hover tooltip. | **Pipeline-supported:** `CanaryEnchantment` rendered the custom path/size in the real hand-card tab and tooltip, captured both together, preserved Block `0 -> 5`, and passed strict Tier 2 with no fresh error on 2026-07-17. A null custom path retains `MissingIconPath`; nonstandard `160x150` special icons remain outside the normal generated profile. |
| orb | Loose `100x100` icon through an existence-checked `CustomIconPath`, plus a separate `PackedScene`/`Node2D` through `CustomSpritePath` or `CreateCustomSprite()`. | Icon: smart hover tooltip and trigger flash particle. Scene: persistent combat orb body. | **Icon pipeline-supported:** `CanaryOrb` rendered the same custom path/size in tooltip + flash, captured both with the real orb, preserved Block `0 -> 2 -> 7`, and passed strict Tier 2 on 2026-07-17. The body remains the explicit Frost scene with `SpineSkeleton`; `CustomChannelSfx` also uses Frost to avoid a missing debug-audio error. Custom Spine body work is in the later presentation expansion's animation track. |
| monster + encounter | `CreateCustomVisuals()` existence-checks one `images/monsters/<slug>.png` and passes it to `NodeFactory<NCreatureVisuals>.CreateFromResource`; `CustomVisualPath` remains `creature_visuals/fallback`. The factory creates a foot-aligned `Sprite2D`, Bounds, Intent, and Center nodes; `NCreature` skips animator setup without a Spine body. | Static combat body plus bounds/intent placement; default bestiary body/title/move-list view. Animation states and a separate phobia body are independent later contracts. | **Static body pipeline-supported:** `CanaryMonsterVocabulary` rendered the same 360x360 custom path in combat and a real `NBestiary` default layout; both had non-Spine 396x396 bounds and intent `(0,-466)`. Headed screenshots showed floor alignment, unobscured intent, title/move list, and no crop; the full behavior cycle passed strict Tier 2 with no fresh error on 2026-07-17. Missing PNG returns `null` to the explicit scene fallback; `HasDeathSfx=false`; animation/phobia variants are later. |
| normal event / World Node | Initial loose portrait through `CustomInitialPortraitPath`; later pages switch a checked loose texture through `NEventRoom.SetPortrait`. Every portrait slot is opaque `3440x1613`. The bounded code-native `portrait_halo` and curated built-in `trial_noble` scene use the observed portrait host; BaseLib `CustomVfxPath` is unused. Normal page/option descriptions reuse `MegaRichTextLabel`. Enabled options reuse typed `HoverTipFactory`/`RelicOption<T>` data; native lethal helpers own only warning presentation. Card/relic acquisition reuses public Cmd consumers, and `weak_short` reuses the preference-scaled native shake host. Optional phobia art is inferred at the private engine path `<full-id>_phobia_mode.png`; custom/Ancient layouts are scenes. | Initial and authored later-page portraits; Cmd/page/selection/reward option results; resumable and terminal custom combat; halo or `trial_noble` on named pages; bounded color/emphasis/`jitter`/`sine` spans; enabled typed tips; exact-lethal HP/Max HP glow; native acquisition and shake; explicit cleanup/replacement on transitions. | **Portraits + bounded VFX + rich text + option/native presentation + outcome vocabulary pipeline-supported:** checked portrait paths retain the existing fallback rules. The 2026-07-20 Event/Presentation runs proved outcomes, rich text, enabled tips, locked-tip suppression, normal relic metadata without an image, and inclusive safe/lethal glow boundaries. The final 2026-07-21 `CanaryNativePresentation` run added exact Card/relic `+1/+1` native consumers, preference index 2 shake movement/return, exact `trial_noble` path/position/inherited process mode, and preview/VFX cleanup in 35 seconds with strict Tier 2. **Still deferred:** normal-layout relic images, custom phobia art, custom/Ancient layouts, arbitrary VFX/shaders/audio, more than one combat per Event instance, and direct merchant/rest/treasure room transitions. |
| character Foundation | Static seams are select unlocked+locked `132x195`, background `1920x1200`, top-panel icon `88x88`, map marker `49x64`, non-Spine combat/rest/merchant bodies `512x512`, five full-energy layers `256x256`, and compact resource icon `24x24`. `build.py` packs minimal raw `.tscn` wrappers without Godot/MegaDot; full energy uses `CustomEnergyCounter`; static merchant gates its getter on the exact `NMerchantCharacter._Ready()` B-prefix. `NAncientNameBanner` installs `RichTextAncientBanner`; Architect consumers use `SpeechBubbleColor`, `GetArchitectAttackVfx()`, and four required localization keys. | Character select normal/locked and background, top-panel icon, map marker, static combat body, compact/full energy, rest site, merchant, native Ancient banner/dialogue. Trail, transition, attack animation, and multiplayer views are later. | **Pipeline-supported subset:** the final 2026-07-21 Wayfinder runs visibly proved selection portrait/background, top-panel identity, exact static combat/rest/merchant textures, five-layer native energy plus compact icon, full Foundation/resource/buffer behavior, and the merchant prefix `targets/owned=1/1`; strict Tier 2 reached `selftest done` with no fresh error. **Grounded gaps:** locked/map need visible-host proof and Ancient/Architect needs its real headed host. All retain template/native fallbacks; custom Ancient layout and animation remain deferred. |
| resource / ordered buffer UI | The local host is `NCombatUi.EnergyCounterContainer` through the exact MVID-gated `NCombatUi.Activate(CombatState)` postfix. The promoted open-mod node is a fixed 220x32 `HBoxContainer` with an optional checked 24x24 icon and 188x32 live Label. | Initial zero/empty, gain/append, successful and rejected spend, overflow, compile/clear, second-combat reset, layout cleanup; local player only. | **Pipeline-supported:** Wayfinder observed exact custom icon path/size, composed `Ink: N | Route: ...` text, resource/lifetime metadata, fixed layout, and reset while preserving native card destinations. Missing icon keeps the live text. This does not support top-bar, retained-card-zone, animated, or remote-player UI. |

### Consumer-completeness rule

Before promoting an art spec:

1. Trace every model getter/property and every UI node that consumes it. Distinct getters
   or resource paths require distinct outputs even when they show the same subject.
2. Record secondary views such as inspect/detail, hover tooltip, notification/flash,
   locked/select, phobia, bestiary, and reset/cleanup states. Mark a view deferred rather
   than silently omitting it.
3. Distinguish shared consumers from independent contracts. Repeated `NCard` contexts may
   reuse one enchantment texture; an orb icon and orb combat scene may not be collapsed.
4. Require headed evidence that identifies the custom asset and excludes the fallback.
   A path assertion, successful `.pck`, or model-only state is insufficient.

## Later presentation expansion

Animation, materials, multiplayer presentation, and audio are independent, explicitly
non-blocking tracks for M6 and M7:

- orb Spine combat bodies and `idle_loop` assets;
- monster Spine skeleton/atlas plus attack, hurt, cast, death, phobia, and bestiary move previews;
- character Spine combat/rest/merchant animation and animated select transitions;
- character card-trail/transition materials, shaders, parameters, fallback, and cleanup;
- remote-player hands, Character identity/indicators, ownership, rebuild, and cleanup;
- character voice/combat/energy/UI/scene audio IDs, preference/mix behavior, fallback, and
  one-shot/loop cleanup;
- arbitrary event portrait VFX and any animation-bearing custom/Ancient layout (the bounded
  normal-layout `portrait_halo` is already supported);
- open-mod-owned UI entry/exit or transition animation.

Static/native fallbacks remain the supported behavior until each track is deliberately
opened and proven through its real consumers.

Positioned Event speech/thought bubbles are future outlook only, not an M6/M7 commitment;
the normal portrait layout has no verified `Creature` speaker/anchor contract.

## Grounded / later depth

- run configuration and saved model references;
- owned entity / party roster;
- reward and rest-site option hosts;
- pet;
- run modifier;
- additional versioned patch bridges.

## Unsupported

- retained played-card `CustomPile` gameplay or custom zone UI;
- hidden card retention without a grounded presentation lifecycle;
- alternative-energy engine hooks;
- run-persistent or multiplayer character resources;
- vanilla content editing;
- novel Publicizer/transpiler targets generated from intuition;
- Act generation as part of the current Character/Core promise.
- direct Event transitions into merchant, rest-site, or treasure rooms;
- more than one special combat from the same mutable Event instance.
- arbitrary forced Event chains, fixed-node ordering guarantees, multiplayer ownership, or
  a save-roundtrip claim for the bounded Quest Card follow-up.

## Current regression ownership

Use `README.md` in this directory. Add a case to the nearest host suite when practical; a
separate project is allowed when it is the simpler maintainable choice. Fresh acceptance
projects do not become permanent fixtures automatically.
