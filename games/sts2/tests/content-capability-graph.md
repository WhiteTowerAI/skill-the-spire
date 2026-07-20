# Current STS2 capability graph

This is the active support surface. Historical evidence rows and the M6 graph snapshot are
archived at `documents/history/content-capability-graph-through-m6.md`.

Support levels:

- **pipeline-supported:** natural-language intake through real hosted verification works;
- **scenario-verified:** a real host proof exists, but the generation/user path is not a
  current promise;
- **grounded:** API/host contract is known but not promoted;
- **unsupported:** preserve the idea as a pack gap.

## Pipeline-supported

| Capability | Host | Required proof | Current boundary |
|---|---|---|---|
| card / relic / potion / power | `CombatPlayer` | real source play/use/hook changes state | pooled registration rules; power auto-discovery |
| interaction | source host | source and dependent observations in dependency order | directed SPEC edge, not a `combo` type |
| keyword | `CombatPlayer` | membership, card text, no-icon hover tooltip, and named state change | text presentation supported; no owned bitmap/scene |
| enchantment | `CombatPlayer` | attachment, altered host behavior, and custom icon in card tab + tooltip | one 64x64 loose PNG; checked missing-icon fallback |
| orb | `CombatPlayer` | channel/passive/evoke plus custom icon in smart tooltip + trigger flash | one 100x100 loose icon; explicit Frost Spine scene/channel-SFX fallback |
| stateful relic cadence | multi-combat `CombatPlayer` | threshold/lifetime boundary; save round trip for run state | integer/bool relic state only |
| monster + encounter | `CombatEnemy` | encounter identity, move/history, exact state deltas, static body in combat+bestiary | one checked 360x360 loose PNG; explicit scene fallback; animation deferred |
| monster move vocabulary | multi-turn `CombatEnemy` | every declared cycle/branch and independent effect | deterministic/conditional branches |
| event / World Node | `MapNode` | real UI for Cmd/page/selection/reward outcomes; custom encounter plus Resume/map semantics; visible portrait/VFX lifecycle; native rich-text host and page replacement | one special combat per Event instance; normal portraits, bounded `portrait_halo`, and vanilla-observed description rich text supported; phobia/custom-layout/Ancient and arbitrary VFX deferred |
| character Foundation | `RunStart` + `CombatPlayer` | selection, pools/starters, HP/energy, hosted mechanic | placeholder character visuals |
| character resource/payment/UI | Character suite | gain/affordability/spend/rejection/reset and live Label | combat-only, explicit payoff; not alternate Energy |
| ordered semantic buffer + dynamic output | Character suite | native source/compile destinations, visible order, overflow, output/history/effect/reset | semantic values only; source cards use native result piles |

## Scenario-verified infrastructure

| Capability | Boundary |
|---|---|
| typed capability kernel | Exact STS2 0.107.1 MVID-gated B postfix on `NCombatUi.Activate(CombatState)`; self-contained; no shared runtime |

## Direct next: M6 native presentation, then art coverage

The custom-art pipeline is pipeline-supported for card, relic, power, potion, enchantment,
orb icons, static monster bodies, and normal event initial/page portraits. The Event slice
is complete at its grounded boundary, including one three-reference acquisition and real
headed render acceptance plus bounded host-native description rich text. Before M7, cover
six bounded native-host candidates in order: cross-content rich text; Event option Hover
Tips/relic images; lethal-choice warnings; acquisition previews; one-shot screen shake;
and curated built-in noncombat Event VFX. Then cover Character select/combat static art and
the Ancient opening name-banner/Architect presentation research before improving
character-mechanic UI. The Event reference pool contains six reviewed, attributed samples
selected from the actual 55-image local wiki.gg inventory.
Spine, move animation, arbitrary animated VFX, and animated transitions belong to the
later animation expansion and do not block M6 or M7. The one code-native normal-Event
`portrait_halo` profile is already promoted through its existing `MapNode` host.

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
| orb | Loose `100x100` icon through an existence-checked `CustomIconPath`, plus a separate `PackedScene`/`Node2D` through `CustomSpritePath` or `CreateCustomSprite()`. | Icon: smart hover tooltip and trigger flash particle. Scene: persistent combat orb body. | **Icon pipeline-supported:** `CanaryOrb` rendered the same custom path/size in tooltip + flash, captured both with the real orb, preserved Block `0 -> 2 -> 7`, and passed strict Tier 2 on 2026-07-17. The body remains the explicit Frost scene with `SpineSkeleton`; `CustomChannelSfx` also uses Frost to avoid a missing debug-audio error. Custom Spine body work is in the later animation expansion. |
| monster + encounter | `CreateCustomVisuals()` existence-checks one `images/monsters/<slug>.png` and passes it to `NodeFactory<NCreatureVisuals>.CreateFromResource`; `CustomVisualPath` remains `creature_visuals/fallback`. The factory creates a foot-aligned `Sprite2D`, Bounds, Intent, and Center nodes; `NCreature` skips animator setup without a Spine body. | Static combat body plus bounds/intent placement; default bestiary body/title/move-list view. Animation states and a separate phobia body are independent later contracts. | **Static body pipeline-supported:** `CanaryMonsterVocabulary` rendered the same 360x360 custom path in combat and a real `NBestiary` default layout; both had non-Spine 396x396 bounds and intent `(0,-466)`. Headed screenshots showed floor alignment, unobscured intent, title/move list, and no crop; the full behavior cycle passed strict Tier 2 with no fresh error on 2026-07-17. Missing PNG returns `null` to the explicit scene fallback; `HasDeathSfx=false`; animation/phobia variants are later. |
| normal event / World Node | Initial loose portrait through `CustomInitialPortraitPath`; later pages switch a checked loose texture through `NEventRoom.SetPortrait`. Every portrait slot is opaque `3440x1613`. The bounded code-native `portrait_halo` uses `OnRoomEnter` plus `AddVfxAnchoredToPortrait`; BaseLib `CustomVfxPath` is unused. Normal page/option descriptions reuse `MegaRichTextLabel`. Optional phobia art is inferred at the private engine path `<full-id>_phobia_mode.png`; custom/Ancient layouts are scenes. | Initial and authored later-page portraits; Cmd/page/selection/reward option results; resumable and terminal custom combat; halo on initial/page/resumed states; bounded color/emphasis/`jitter`/`sine` spans; explicit cleanup/replacement on transitions. | **Portraits + bounded VFX + rich text + outcome vocabulary pipeline-supported:** checked portrait paths retain the existing fallback rules. The final 2026-07-20 `CanaryEvent` run added `richText` to the identical expected/observed marker, resolved the real BBCode label and required effect types, showed styled initial and fully settled later-page text, kept `resumes=1/0`, reached `selftest done`, and had no fresh error. The halo retained native Fast Mode/cleanup behavior, and the separate portrait acquisition remains green. **Still deferred:** custom phobia art, custom/Ancient layouts, arbitrary VFX/shaders/audio, more than one combat per Event instance, and direct merchant/rest/treasure room transitions. |
| character Foundation | Static seams include select unlocked+locked `132x195`, top-panel icon+outline `85x85`, map marker `49x64`, and a possible non-Spine combat texture. This phase also owns research for the Ancient opening name banner/Architect presentation, whose `RichTextAncientBanner` is installed only by the dedicated name-banner node. Other seams own card trail, energy counter, rest-site and merchant scenes, select background, transition material, multiplayer hand textures, and audio. | Character select normal/locked, select background, top-panel icon/outline, map marker, static combat body, Ancient opening banner, trail, energy counter, rest site, merchant, multiplayer hands/remote presentation. Animation/transitions are later. | `PlaceholderCharacterModel` explicitly supplies Ironclad/template fallbacks. Promote static subsets independently; the Ancient banner needs its dedicated host and headed proof and is not covered by normal Event rich text. Production animation/transitions are later, while remote-player UI and each static scene/material family need separate decisions. |
| resource / ordered buffer UI | The grounded host is local `NCombatUi.EnergyCounterContainer` through the exact MVID-gated `NCombatUi.Activate(CombatState)` postfix. The current open-mod-owned node is a generic `Label`. | Initial zero/empty, gain/append, successful and rejected spend, overflow, compile/clear, second-combat reset, layout cleanup; local player only. | Keep the Label. A richer icon/control must preserve the same host, lifecycle, semantic card buffer, and native card destinations; prove every state without introducing retained-card zone UI. |

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

## Later animation expansion

This is explicitly non-blocking for M6 and M7:

- orb Spine combat bodies and `idle_loop` assets;
- monster Spine skeleton/atlas plus attack, hurt, cast, death, phobia, and bestiary move previews;
- character Spine combat animation, animated select transitions, trails, and animated scene polish;
- arbitrary event portrait VFX and any animation-bearing custom/Ancient layout (the bounded
  normal-layout `portrait_halo` is already supported);
- open-mod-owned UI entry/exit or transition animation.

Static fallbacks remain the supported behavior until that expansion is deliberately opened.

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

## Current regression ownership

Use `README.md` in this directory. Add a case to the nearest host suite when practical; a
separate project is allowed when it is the simpler maintainable choice. Fresh acceptance
projects do not become permanent fixtures automatically.
