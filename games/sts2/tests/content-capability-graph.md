# M6 Content Capability Graph

> **Maintainer-only. NOT shipped.** `publish.sh` renders only
> `games/sts2/skills/{modmaker,sts2-api}`; this `tests/` tree is outside both the
> Claude plugin and portable payloads. This graph is an engineering inventory and
> proof ledger, not a user-facing promise of support.
>
> **Scope rule:** a BaseLib class is not a playable capability by itself. Each row
> names its real host, the scenario that can exercise it, and the observable proof
> required before support advances. Do not add a recipe merely because a type can
> register.

## Support ladder and proof rule

`inventoried → grounded → build-verified → scenario-verified → pipeline-supported`

- **inventoried** — the STS2/BaseLib surface exists; no user promise.
- **grounded** — constructor, registration, localization, host relationship, and one
  STS2 vanilla analog are recorded from engineering evidence.
- **build-verified** — a **Type Canary** builds with 0 warnings/errors, packages,
  loads, and registers in the real game.
- **scenario-verified** — a **Scenario Canary** exercises the content through its
  real host and observes the intended state or behavior change.
- **pipeline-supported** — natural-language intake → common SPEC → scaffold/author →
  Type + Scenario proofs works. **Only this level may be advertised as supported.**

A Scenario Canary follows one contract:

`setup → enter → drive → observe → terminal marker`

The terminal marker proves that the driver completed; it is **not** the behavior
proof. A separate type-specific marker/state assertion must prove the observable
invariant. One vertical-slice canary may cover inseparable types (for example,
monster + encounter).

## Existing baseline

| Capability / family | Registration mode | Host / dependency | Scenario | Observable proof | Art contract | Composes with | Support | Evidence | Next proof / blocker |
|---|---|---|---|---|---|---|---|---|---|
| `card` | pooled; `[Pool(CardPoolModel)]` | player deck/hand; card pool | `CombatPlayer` | card is created, played, and its command changes target/player state | 1000×760 `card_portraits/big/<slug>.png` | power, keyword, enchantment, orb | **pipeline-supported** | E1, E2, E3 | Keep CanaryCard live-green |
| `relic` | pooled; `[Pool(RelicPoolModel)]` | player relic collection + lifecycle hook | `CombatPlayer` | relic is obtained and its hook changes combat state | two 256×256 icons: normal + `big/` | card, power, run-start mechanics | **pipeline-supported** | E1, E2, E3 | Keep CanaryRelic live-green |
| `potion` | pooled; `[Pool(PotionPoolModel)]` | potion inventory + player-selected target | `CombatPlayer` | potion is procured/used and target state changes | one 256×256 loose PNG | creature, power, card | **pipeline-supported** | E1, E2, E3 | Keep CanaryPotion live-green |
| `power` | auto-discovered; no `[Pool]` | creature; normally applied by card/relic/potion/monster | `CombatPlayer` (later `CombatEnemy`) | host applies power; its hook/stack changes dependent state | two 256×256 icons: normal + `big/` | every combat content family | **pipeline-supported** | E1, E2, E3 | Keep card→power interaction live-green |
| multi-element interaction | directed SPEC edge; not a registered content type | source element + dependent element | scenario selected by source/host | independent source and dependent **state proofs** occur in order; trigger markers are diagnostic only | union of member contracts | all supported families | **pipeline-supported** | E2, E3 | Preserve explicit `elements` + `interactions` contract; historical canary project is named `CanaryCombo` |
| run-persistent relic cadence | state on pooled relic; `[SavedProperty] int/bool` | owner relic + run save | multi-combat `CombatPlayer` | `N-1` no-fire state, save round trip, second-combat carry-over and exact threshold delta | relic icon contract | cards/powers/character run rhythm | **pipeline-supported** | E2, E3, E14 | Keep `CadenceCanary` green; profile/meta persistence remains unsupported |
| combat-local turn cadence | state read from `PlayerCombatState.TurnNumber` | owner relic + current combat | multi-combat `CombatPlayer` | fires on specified combat turn; next combat starts at turn 1 with no leaked activation | relic icon contract | cards/powers/enemy pacing | **pipeline-supported** | E2, E3, E14 | Keep `CadenceCanary` green; adjacent turn-local/once/previous-turn rows remain grounded in `mechanic-capability-audit.md` |

## M6 Core — playable vertical slices

| Capability / family | Registration mode | Host / dependency | Scenario | Observable proof | Art contract | Composes with | Support | Evidence | Next proof / blocker |
|---|---|---|---|---|---|---|---|---|---|
| `keyword` | generated custom enum: `[CustomEnum]` static `CardKeyword`; optional `[KeywordProperties]`; BaseLib `GenEnumValues` maps id→loc key | card text/tooltip plus a Card/Power/helper that implements the named rule | `CombatPlayer` | host contains the custom keyword **and** the named mechanic changes state; tooltip alone is insufficient | none | card, power, character vocabulary | **pipeline-supported** | E1, E3, E4, E6, E7 | Keep CanaryKeyword and one-sentence Card+Keyword path green |
| `enchantment` | auto-discovered `CustomEnchantmentModel`; attached to a compatible Card via `CardCmd.Enchant<T>` | a card instance; enchantment modifies card text/state/hooks | `CombatPlayer` | card holds the enchantment/amount and altered play behavior causes a state delta | BaseLib `CustomIconPath`; documented default convention plus 64×64 extracted hint, custom live render still unverified | card, event/rest-site/reward source | **pipeline-supported** | E1, E3, E4, E5, E6, E8 | Keep CanaryEnchantment and one-sentence host+enchantment path green; live-render icon later |
| `orb` | auto-discovered `CustomOrbModel`; constructor adds instance to `RegisteredOrbs` | orb-capable player; `OrbCmd.Channel` adds a slot when both base/current capacity are zero | `CombatPlayer` | queue contains custom orb; passive and evoke each cause independent state deltas | `CustomIconPath` + `CustomSpritePath`/`CreateCustomSprite`; 100×100 icon hint, full custom live visual unverified | card, power/Focus, Minimal Character | **pipeline-supported** | E1, E3, E4, E5, E6, E9 | Keep CanaryOrb and one-sentence Card+Orb path green; live-render icon+sprite later |
| `monster` + `encounter` | `CustomMonsterModel`: no `[Pool]`, constructor auto-`RegisterType`; `CustomEncounterModel(RoomType, autoAdd:true)`: constructor auto-`AddEncounter`; required overrides — monster: `MinInitialHp`, `MaxInitialHp`, `GenerateMoveStateMachine()`; encounter: `AllPossibleMonsters`, `GenerateMonsters()`, `IsValidForAct()` | monster must be spawned by its encounter via `GenerateMonsters()` returning `(model.ToMutable(), slot?)` | `CombatEnemy` (first earned seam 2026-07-10) | 4 independent proof signals: encounter entered, custom monster present in `CombatState.Enemies`, deterministic attack executed (`PECK` via `MoveState`), player HP delta > 0 | monster: no custom visual → fallback to `creature_visuals/fallback` (provisional); Spine/scene + custom visual contract not yet authored | enemy power/intent, act pool, reward | **pipeline-supported (basic attack scope)** | E1, E4, E10, E11 | Direct next: complete the grounded Monster Move Vocabulary row below; custom monster art remains provisional |
| monster move vocabulary | behavior on the existing `CustomMonsterModel`; no separate registration | monster `MoveState` bodies, intents, transitions, and combat state | multi-turn `CombatEnemy` | self Power amount + downstream consequence; player Debuff amount; monster Block/HP delta; multi-hit count; chosen deterministic/conditional transition | no new art contract; intent icons are game UI | power, encounter pacing, multi-monster composition | **grounded** | E15 | **DIRECT NEXT:** recipe + interview/SPEC/author routing, multi-turn action canary, then fresh natural-language acceptance |
| `event` / map node | `CustomEventModel` constructor auto-`AddEvent`; no `[Pool]`; empty `Acts` = all-act placement | event room/map entry; nested pages/options | `MapNode` (earned 2026-07-13) | canonical event room opens; formatted title/option/result loc resolves; real option UI is clicked; consequence changes run state | verified vanilla `res://images/events/this_or_that.png` placeholder; custom portrait/background generation provisional | act, card/relic/reward consequences | **pipeline-supported** | E1, E3, E4, E12, E13 | Keep CanaryEvent and one-sentence Event path green; custom event art remains provisional |
| `character` + starter ecosystem | explicit `AddCharacter` | character select + valid pools, starter deck/relic, run initialization | `RunStart` | selectable character starts a run with expected HP/energy/deck/relic and one mechanic works | portrait/UI/energy/character scene set unknown | all Core capabilities | **inventoried** | E1, E4 | Ground character template and minimum valid asset/loc/pool set |

## M6 Extras — do not block M7

| Capability / family | Registration mode | Host / dependency | Scenario | Observable proof | Art contract | Composes with | Support | Evidence | Next proof / blocker |
|---|---|---|---|---|---|---|---|---|---|
| `run modifier` | auto-discovered `CustomModifierModel`; `Alignment` routes to `ModelDb.GoodModifiers` / `BadModifiers` | run setup/modifier selection UI; not a Card attachment | `RunStart` candidate (deferred from Mechanic Vocabulary) | modifier is selectable/active, exclusivity holds, and its run rule changes state | modifier UI icon/art contract unknown | character/run rules, mutually-exclusive modifiers | **grounded** | E1, E6 | Define user value and Modifier UI scenario separately; never merge with enchantment |
| `reward` | attached `CustomReward`; exact injection path to ground | encounter outcome / reward screen | `PostCombat` | reward appears, can be selected/skipped, and selection mutates run inventory/state | reward icon/UI contract unknown | encounter, event, card/relic/potion | **inventoried** | E1 | Ground injection lifecycle after Core |
| rest-site option | attached `CustomRestSiteOption` | rest-site room/menu | `MapNode` | option appears, eligibility is honored, choice changes run state | option icon/UI contract unknown | enchantment, deck/relic state | **inventoried** | E1 | Event has earned MapNode; ground the distinct rest-site host/injection lifecycle when Extras are prioritized |
| `pet` | `CustomPetModel`; exact discovery/attachment path to ground | player/character and combat lifecycle | scenario undecided (`CombatPlayer` candidate) | pet appears and one pet action causes a state delta | Spine/scene contract unknown | character, power, card | **inventoried** | E1 | Define host ownership and stable observable before adapter choice |

## Deferred ecosystem — outside the M6 completion gate

| Capability / family | Registration mode | Host / dependency | Scenario | Observable proof | Art contract | Composes with | Support | Evidence | Next proof / blocker |
|---|---|---|---|---|---|---|---|---|---|
| `act` / map ecosystem | explicit `AddAct` | encounters, events, map generation, boss and progression ecosystem | `ActMap` (deferred) | enter generated act, traverse representative nodes, reach progression boundary | broad map/background/UI/audio set unknown | every world/run capability | **inventoried** | E1, E4 | Separate milestone after node + encounter capabilities exist |
| `Ancient` content | explicit `AddAncient` | Ancient encounter/dialogue/card ecosystem | deferred | real Ancient host presents content and consequence | 606×852 Ancient full-art path known; wider contract unknown | card, dialogue/event, character | **inventoried** | E1, E5 | Not M6; do not conflate with normal cards/events |

## Evidence ledger

### STS2 engineering evidence — may advance support

| ID | Source | What it establishes | Confidence / limit |
|---|---|---|---|
| **E1** | BaseLib v3.3.x registration surface: `CustomContentDictionary` entry points plus the `Abstracts/` model family, summarized in `documents/IMPLEMENTATION_PLAN.md` §5 M6 | three pooled families; explicit `AddEncounter`/`AddAncient`/`AddEvent`/`AddAct`/`AddCharacter`; broader custom model inventory | **High** for inventory/registration family. Re-mine exact API against the current BaseLib version before grounding a slice. |
| **E2** | `games/sts2/tests/canary.md` + `canary-results.md` | real Type and Scenario evidence for card/relic/potion/power plus a card→power interaction | **High, live verified** on the recorded STS2/BaseLib versions. |
| **E3** | shipped recipes, `reference/build-constraints.md`, `reference/mechanics.md`, `reference/selftest-harness.md`, `reference/art-contract.md` | current pipeline, analyzer, host hooks, harness and live art contracts | **High** only for the types explicitly documented/verified there. |
| **E4** | local maintainer baseline `baselines/spire-codex/data/*.json` and `backend/app/parsers/` | STS2 vanilla analogs and content relationships: character starter ecosystem; encounter→monsters; event→options/pages; enchantment applicability; orb passive/evoke | **Medium–high for content/design structure. Not API, registration, build, or mod compatibility proof.** Never ship or depend on this local baseline at runtime. |
| **E5** | extracted STS2 asset dimensions summarized in `reference/art-contract.md` / project research | orb 100×100 and enchantment 64×64 dimensions; normal vs Ancient card distinction | **Medium** until each custom type's exact BaseLib path/getter is grounded and live rendered. |
| **E6** | BaseLib v3.3.x decompile: `Patches/Content/{CustomEnumAttribute,KeywordPropertiesAttribute,GenEnumValues}.cs`; `Abstracts/{CustomEnchantmentModel,CustomModifierModel,CustomOrbModel,OrbLoc}.cs`; STS2 `OrbCmd` and vanilla model analogs | exact registration families and first host/API seams for keyword, card enchantment, run modifier and orb | **High for the inspected symbols.** Required overrides, loc/attachment calls and custom resource rendering still need build/live canaries before recipe claims. |
| **E7** | `CanaryKeyword` (2026-07-10): Card+custom enum+`card_keywords` built 0/0, packaged/loaded, then `CombatPlayer` observed `Resonant present=True` and Block `0 -> 7` | custom Keyword Type + hosted behavior Scenario proof and pipeline recipe shape | **High, live verified.** Visual tooltip text is grounded by loc/keyword membership; dedicated screenshot/eyeball was not used as behavior proof. |
| **E8** | `CanaryEnchantment` (2026-07-10): custom `Guarded` + host `Etched Strike` built 0/0, packaged/loaded; `CardCmd.Enchant` observed attached=True Amount=5, then `OnPlay` Block `0 -> 5` | custom Card Enchantment Type, attachment edge, and altered host behavior Scenario proof | **High, live verified.** Custom icon rendering remains unverified and is not part of this support claim. |
| **E9** | `CanaryOrb` (2026-07-10): custom `ShelterOrb` + host `Take Shelter` built 0/0, packaged/loaded; queue presence true capacity=1, passive Block `0 -> 2`, evoke Block `2 -> 7` | custom Orb Type plus channel/passive/evoke Scenario proof and zero-slot host behavior | **High, live verified.** Custom icon/combat sprite rendering remains unverified and is not part of this support claim. |
| **E10** | `CanaryEncounter` (2026-07-10): `CanaryMite : CustomMonsterModel` + `CanaryMiteEncounter : CustomEncounterModel` built 0/0, packaged/loaded via `EnterRoomDebug`; 4 independent CombatEnemy signals — encounter entered, monster in `Enemies`, PECK executed via `MoveState`, player HP delta=6 | custom Monster + Encounter Type plus first earned CombatEnemy Scenario proof; key correction: monster attack uses `.FromMonster(this).Execute(null)`, NOT `.Targeting()` | **High, live verified.** Monster visual falls back to `creature_visuals/fallback`; Spine/custom scene contract remains provisional and is excluded from this support claim. |
| **E11** | User acceptance run (2026-07-13): plain-language Enemy Encounter intake completed the published open-mod 0.5.0 pipeline and produced a working mod; the run also exposed the generated self-test template's nonexistent `TaskHelper`, corrected to standard `_ = RunAsync();` fire-and-forget | closes the natural-language intake → SPEC → generation → build → real verification gate for Monster + Encounter | **High for pipeline acceptance, user-observed.** Exact generated mod details/log markers were not retained in this repo; E10 remains the reproducible Type + Scenario evidence. |
| **E12** | `CanaryEvent` (2026-07-13): `GildedSignpost : CustomEventModel` built 0/0, packaged/loaded, entered via `ModelDb.Event<GildedSignpost>()`; nested title/option/result loc resolved; real `NEventOptionButton` clicked; event and harness independently observed Gold `99 -> 124` (`delta=25`) | custom Event Type plus first earned `MapNode` Scenario proof; confirms constructor auto-registration, all-act default, `Option(Method)` slug contract, and real UI choice consequence | **High, live verified.** Uses a verified vanilla portrait placeholder; custom event portrait/background generation remains provisional and is excluded from this support claim. |
| **E13** | Fresh natural-language acceptance (2026-07-14): “an event called Forgotten Cache where opening the cache gives 30 gold” generated a separate `ForgottenCache` project from SPEC through scaffold/author/build/verify; build 0/0, Tier 1 PASS, Tier 2 PASS, zero repair; event and harness both observed Gold `99 -> 129` (`delta=30`) | closes the natural-language intake → SPEC → generation → build → real `MapNode` verification gate for Event / World Node | **High, live verified.** Acceptance source/state is in gitignored `.claude/acceptance-forgotten-cache`; E12 remains the minimal reproducible Type + Scenario canary. |
| **E14** | `CadenceCanary` (2026-07-15): two custom relics built 0/0 and loaded; real combat 1 observed run progress `1 -> 2` plus combat-turn-2 effect; `SavedProperties.From/Fill` restored `2`; real combat 2 observed run threshold `2 -> 0`, Energy `3 -> 4`, and combat reset `TurnNumber=1` with no second local activation | custom-relic run save support plus the distinct Happy Flower vs Stone Calendar lifetime contracts and a reusable multi-combat proof shape | **High, live verified** for relic `int` run cadence and combat turn cadence. Does not promote profile state, arbitrary saved holders/types, or the adjacent grounded-only families in `mechanic-capability-audit.md`. |
| **E15** | STS2 stable-v0.107.1 decompile: `BruteRubyRaider` alternates `SingleAttackIntent` with `BuffIntent` and applies self `StrengthPower`; `FrogKnight` combines Buff/attack/Debuff moves plus `ConditionalBranchState`; intent inventory includes `BuffIntent`, `DebuffIntent`, `DefendIntent`, `HealIntent`, and `MultiAttackIntent` | exact vanilla substrate for self Power, target Debuff, richer intents, deterministic cycles, and conditional monster transitions | **High for grounding only.** No custom-monster Type/Scenario canary yet; this evidence cannot promote richer actions beyond the current basic-attack support scope. |

`spire-codex` is a queryable **maintainer research input**, not part of the game
pack. Useful structures observed in M6.0:

- `data/characters.json`: HP, gold, energy, orb slots, starter deck/relics;
- `data/encounters.json`: room type, act/tags, and encounter→monster membership;
- `data/events.json`: nested options/pages and displayed consequences;
- `data/enchantments.json`: applicability, card type, stackability, extra card text;
- `data/orbs.json`: distinct passive and evoke contracts;
- matching `backend/app/parsers/`: field-discovery aids only.

Do not copy its data, parsers, or assets into published payloads. Confirm upstream
licensing before any future redistribution; M6.0 distills only relationships and
verification questions.

### STS1 / cross-game design analogy — never advances support

These principles help choose a meaningful host, composition edge, and observable
invariant. They are design guidance, **not STS2 engineering evidence**:

- **Risk versus reward:** events and rewards need a consequential choice, not merely a
  registered screen.
- **Enabler → payoff → glue:** keyword/orb/card combinations should prove a resource
  loop, not three isolated models.
- **Archetype over isolated card:** Minimal Character is a starter ecosystem and small
  mechanic vocabulary, not only a selectable class.
- **Encounter as composition:** enemy interest comes from monster roles, intent cadence,
  and group composition; a monster that only spawns proves too little.
- **Scaling and constraints:** observable checks should include lifecycle/limits where
  relevant, not only a one-time numeric spike.

Primary design-source URLs and attribution remain in
`documents/BASELINE_RESEARCH.md` (“MegaCrit design language”). Any STS1 analogy must
be re-validated against STS2 behavior before entering the engineering ledger.

## M6.0 completion boundary

M6.0 completes when this graph exists, the support claims match current evidence,
and the Tier-2 tools accept only asserted post-state, never terminal or preview/trigger logs.
It deliberately adds **no** new recipe, canary, schema/registry, or hypothetical
scenario-adapter framework. The next step is Mechanic Vocabulary; its first real
canary earns the minimum `CombatPlayer` scenario seam it actually needs.
