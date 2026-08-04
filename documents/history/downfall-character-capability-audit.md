# Downfall Character Capability Audit

> Maintainer-only research input. Audited 2026-07-15 from the gitignored
> `baselines/downfall/` checkout at commit
> `ee2f8018635110569f2f5125aef6a45754b62280` (Downfall `0.0.30`, STS2
> `0.107.1`, BaseLib `3.3.5`, MIT). This file records engineering patterns; it
> does not promote any open-mod support claim by itself.

## Scope and evidence rules

- The audit covers programming mechanics, state, hooks, UI hosts, save/network
  contracts, and patch boundaries. Character art, animation quality, audio, and
  content balance are intentionally outside the current Character Systems phase.
- Downfall is a maintainer baseline, not a runtime dependency. The published
  skill must not read this checkout, require GDRE, or copy extracted game assets.
- MIT code can be adapted with its license notice. Prefer a minimal independent
  implementation over copying a Downfall subsystem with its project-specific
  registries and transitive dependencies.
- A working Downfall implementation is strong grounding evidence for an STS2
  seam, but open-mod advances a capability only after its own Type and Scenario
  canaries pass. Collector and Gremlins are source-present but excluded from the
  current combined `Downfall.csproj` compile, so they are design/grounding inputs,
  not current-release behavior evidence.

## Shared architecture worth moving upstream

Downfall's strongest architectural choice is a shared kernel with thin character
modules. Character modules register domain callbacks; the shared kernel owns the
Harmony seam, UI host, dispatch order, and patch diagnostics.

| Downfall surface | What it does | open-mod abstraction | Initial risk |
|---|---|---|---|
| `DownfallCharacterModel` | Centralizes character paths, pools, selection/combat shell | `CharacterShell` contract generated per mod | A: BaseLib/public |
| `DownfallHook` | Dispatches, aggregates, gates, and tracks modifiers across combat listeners | typed `HookBus` primitives, not one interface per named character | A: public hook iteration |
| `CardExecutionRegistry` | Adds before/after card-play extension points once | shared card lifecycle seam | D: IL transpiler |
| `CustomPile` + combat-pile registry | Adds semantic card zones and optional UI buttons | `CardZone<TState>` plus host-specific UI adapter | A for state, B/C for UI |
| `CardResource` | Owns a player resource, reset rules, affordability, spending, and counter UI | `CharacterResource` with lifetime/payment/UI contracts | A for state, B/C for payment/UI |
| `CombatUiHooks` / top-bar registry | Lets character systems attach UI without each patching the game | descriptor-based UI host registry | B: postfix on UI initialization |
| `SavedSpireField` + serializers | Saves run-level scalars, model ids, cards, and structured party state | typed run-state store with explicit serializer | A/C depending on holder |
| `ModPatcher` | Applies selected patches once and logs zero-target/failure results | versioned patch registry with mandatory Tier-1 markers | B-D by patch |

Patch risk bands used in this audit:

- **A - public/BaseLib:** public commands, models, hooks, custom piles, saved
  fields. Prefer this whenever it expresses the mechanic.
- **B - structural postfix/prefix:** inject before/after a stable lifecycle
  method without rewriting its control flow.
- **C - internal access:** Publicizer, reflection, private fields, or internal
  setters. Version-gate and assert the member exists.
- **D - transpiler:** rewrites IL inside a game method. Highest maintenance and
  compatibility risk; require an exact method fingerprint and a dedicated canary.

## Per-character decomposition

### Automaton - custom zones and dynamic composition

Mechanic chain:

`card -> EncodeCard -> FunctionSequence pile -> threshold -> FunctionCard -> execute merged encodings`

- `EncodePile` and `StashPile` are custom combat zones with different visibility
  and draw rules.
- `AutomatonCmd` moves real card instances into a sequence, snapshots and clears
  it at a threshold, creates a dynamic `FunctionCard`, and merges typed
  `Encodable` effects and dynamic variables.
- `AutomatonCombatModel` draws from Stash at hand-draw time and emits normal
  history/hook events so the custom draw composes with other content.
- Reusable primitives: **custom zone**, **ordered recipe/threshold**, **dynamic
  card synthesis**, **custom draw lifecycle**, **zone UI**.
- Main evidence: `AutomatonCode/{Piles,Encode,Core,Events,Vfx}`.

### Awakened - threshold transformation and rotating spellbook

Mechanic chain:

`play Powers -> combat meter 0..7 -> Awaken once -> upgrade/refresh spellbook behavior`

- `AwakenedModel` owns combat-local threshold state and a one-shot transition;
  it updates a status bar and dispatches an `OnAwaken` event.
- `AwakenedPile` is a private spellbook zone whose contents can be extended at
  runtime, shuffled deterministically, consumed, and refreshed.
- Chant reads ordered card-play history; Conjure combines a tag/enchantment with
  dynamic zone output.
- Reusable primitives: **threshold meter**, **one-shot phase transition**,
  **private generated pool**, **history predicate**, **mechanic-triggered
  enchantment**, **creature-anchored UI**.
- Main evidence: `AwakenedCode/{Core,Piles,Enchantments,Events,Displays}`.

### Champ - finite-state character mode with charges

Mechanic chain:

`enter stance -> mutable stance state + 3 charges -> Skills consume bonuses -> Finisher exits/transitions`

- `ChampStanceModel` is an owner-bound mutable state object with enter/exit,
  charge, skill-bonus, and finisher contracts.
- `ChampModel` owns the active state per player and performs typed transitions.
- Card tags, keywords, and small interfaces declare entry, combo, and finisher
  behavior; the common handler interprets them after play.
- Reusable primitives: **finite-state machine**, **state-local counters**,
  **entry/exit actions**, **declarative card triggers**, **choice-driven state
  transition**, **state UI**.
- Main evidence: `ChampCode/{Core,Stance,Events,Interfaces,Vfx}`.

### Guardian - timed zone, persistent card attachments, and hosted run choices

Mechanic chain:

`card -> Stasis slots/counter -> per-turn Tick -> free return or exhaust`

and:

`Gem card -> rest-site selection -> persistent card modifier -> replayed gem effect`

- `GuardianCombatModel` combines a mode FSM, per-player slot count, and per-card
  countdown state.
- `GuardianCmd` owns zone capacity, enter/return rules, ticking, acceleration,
  and mode changes.
- `GemModel` is a mutable card attachment with custom text, behavior, cloning,
  and save handling.
- `GemRestSiteOption` and `GemFinderReward` prove that character mechanics can
  extend non-combat hosts and synchronize player choices.
- Reusable primitives: **bounded timed zone**, **per-instance card state**,
  **persistent attachment/socket**, **rest-site action**, **custom reward**,
  **multiplayer-synchronized selection**, **mode FSM**.
- Main evidence: `GuardianCode/{Core,Piles,Gems,RestSiteOptions,Rewards,Events}`.

### Hermit - hand-position semantics and pre-mutation snapshots

Mechanic chain:

`card is visually/model-middle in hand -> snapshot before play moves it -> Dead On effect/history`

- `HermitCmd` derives a semantic condition from card order in the real hand pile.
- `DeadOnPatch` captures that condition before `OnPlayWrapper` moves the card.
- hand add/remove/layout postfixes repair model-to-visual ordering after engine
  transitions.
- a custom history entry makes the semantic event independently observable.
- Reusable primitives: **zone-position predicate**, **pre-transition snapshot**,
  **model/UI order reconciliation**, **custom semantic history event**.
- Main evidence: `HermitCode/{Core,Patches,History,Events}`.

### Hexaghost - ordered circular state machine

Mechanic chain:

`active wheel node -> condition progress -> ignite effect -> move around ring -> reset/replace node`

- `HexaghostModel` stores an owner-bound array of mutable `GhostflameModel`
  instances plus a current index.
- each node declares its own trigger predicate, threshold, intent/preview, and
  effect while shared commands own movement, wraparound, ignition, and reset.
- hooks can modify effect intensity, repeats, and trigger predicates without
  hard-coding individual cards.
- Reusable primitives: **ordered/ring FSM**, **polymorphic state nodes**,
  **state-local progress**, **automatic turn transition**, **replaceable node**,
  **preview derived from runtime state**.
- Main evidence: `HexaghostCode/{Core,Ghostflames,Events,Vfx}`.

### Slime Boss - owned minion roster and command protocol

Mechanic chain:

`Split -> create owned monster/pet -> bounded queue -> Command -> evict/Absorb -> player payoff`

- `SlimeQueue` owns slots, order, creation, eviction, removal, and layout for
  custom monster instances attached as player pets.
- each `SlimeModel` exposes a command instead of taking normal monster turns.
- lifecycle patches bypass incompatible death animation and vanilla pet-specific
  behavior; direct `_pets` access is a Publicizer/internal boundary.
- Reusable primitives: **owned entity roster**, **capacity/eviction policy**,
  **minion command protocol**, **pet-owner targeting**, **death interception**,
  **entity layout adapter**.
- Main evidence: `SlimeBossCode/{Core,Slimes,Patches,Events}`.

### Snecko - run setup choices and cross-character pool composition

Mechanic chain:

`act start -> synchronized character-pool choices -> saved ModelIds -> rewards/generation use selected pools`

- `SneckoModel` saves selected external card pools with a custom serializer and
  reconstructs the content source after load.
- `SneckoPoolSelection` reserves deterministic choice ids and mirrors local and
  remote decisions.
- Muddle mutates energy cost with owned RNG, explicit constraints, hook vetoes,
  animation, and a custom history entry.
- Reusable primitives: **run-start configuration**, **saved model references**,
  **cross-pool composition**, **multiplayer choice protocol**, **constrained RNG
  mutation**, **acquisition-triggered reward choice**.
- Main evidence: `SneckoCode/{Core,Events,History,Vfx}`.

### Collector - persistent collection and alternate economy (source-only)

Mechanic chain:

`defeat enemy -> post-combat capture reward -> spend persistent Essence -> add serialized collectible -> combat custom pile`

- `CollectorModel` records defeated monster models and injects post-combat
  rewards based on room type.
- `CollectiblesModel` persists serialized cards and sends a custom network
  message for acquisition.
- `CollectorEnergy` can supplement or replace normal energy and owns
  affordability/spending rules.
- top-bar and custom-pile UI expose persistent currency and collection state.
- Reusable primitives: **post-combat observation**, **persistent secondary
  collection**, **custom currency**, **alternative payment**, **custom reward
  serialization**, **top-bar UI**, **capture-to-card mapping**.
- Main evidence: `CollectorCode/{Core,Piles,Rewards,Vfx}`. Source is currently
  excluded from `Downfall.csproj`; treat as grounded design, not live support.

### Gremlins - multi-body playable party (source-only)

Mechanic chain:

`saved roster -> create sub-creatures -> active/bench rotation -> swap HP identity -> death promotes next member`

- `GremlinState` owns active/bench order; `GremlinsRunModel` persists each
  member's model id, current HP, and max HP across combats/save.
- swapping copies HP between the active sub-creature and the player shell.
- death interception replaces the active body, while synchronized overlay
  choices select manual swaps.
- Reusable primitives: **multi-body character**, **party roster**, **active/bench
  rotation**, **per-member persistent health**, **death replacement**,
  **identity/stat projection**, **synchronized party choice**.
- Main evidence: `GremlinsCode/{Core,Events,Vfx}`. Source is currently excluded
  from `Downfall.csproj`; treat as grounded design, not live support.

## Capability families for open-mod

The role names above must not become recipe branches. Their mechanisms reduce to
the following composable families:

| Family | Semantic contract | Representative Downfall systems |
|---|---|---|
| Character shell | identity, pools, starter ecosystem, run entry | all characters |
| Scoped state | owner, lifetime, reset, save, UI meaning | Awaken meter, stance, wheel, Essence |
| State machine | states/nodes, transition, entry/exit, condition | Champ, Guardian, Hexaghost |
| Card zone | membership, order, capacity, visibility, transition | Automaton, Awakened, Guardian, Collector |
| Dynamic content | source parts -> generated/mutated card/model | Automaton functions, Awakened spells, Guardian gems |
| Resource/payment | gain, spend, cap/floor, reset, alternative payment | Collector Energy/Essence, stance charges |
| Owned entities | roster, capacity, command, death, owner projection | Slime Boss, Gremlins, Collector Torchhead |
| Run configuration | synchronized choices, saved model references, content routing | Snecko pool selection |
| Hosted choices | reward/rest/overlay source, sync, serialization, consequence | Guardian, Snecko, Collector |
| Semantic hook | event timing, listeners, aggregation/order, history proof | every character via `DownfallHook` |
| UI adapter | host node, visibility predicate, refresh signal, no-art fallback | top bar, combat pile, creature display |
| Patch bridge | target, risk band, version/fingerprint, conflict and failure markers | shared patches, Hermit, Slime Boss |

The SPEC should describe these semantics rather than a named implementation. An
unusual user idea may compose existing families in a new way; it should not be
collapsed into the nearest simple BaseLib content type.

## Upstream layout decision for open-mod

Use three boundaries:

1. **Generated domain code:** the character's named states, transitions, cards,
   resource rules, and mechanic-specific assertions. This stays inside the mod.
2. **Capability modules:** maintained source templates/contracts for state,
   zones, resources, choices, pets, and scenario drivers. The author stage emits
   only the selected modules.
3. **Optional `OpenMod.Runtime`:** one automatically installed game-mod
   dependency for shared Harmony/Publicizer patch seams and registries when a
   capability cannot stay BaseLib/public. This avoids every generated mod
   patching the same game method independently. Do not create this runtime until
   the first two real advanced canaries establish the shared boundary.

BaseLib remains the first choice, not the feature ceiling. A capability that
needs Harmony is acceptable when it has:

- an exact target and supported game-version range;
- idempotent application and a unique patch id;
- zero-target/failure diagnostics at load time;
- an explicit state/save/multiplayer contract;
- Type + Scenario proof, including the semantic outcome rather than only
  "patch applied";
- a conflict/fallback story if another mod patches the same method.

## Character Systems proof program

1. **Foundation canary:** auto-registration through the
   `CustomCharacterModel` constructor, selection, run start, pools, HP/energy,
   starter deck/relic, and one public/BaseLib mechanic.
2. **Patch-kernel canary:** apply one stable B-level postfix through the proposed
   registry and prove both the patch marker and its hosted state consequence.
3. **Resource/UI canary:** gain/spend/reset a character resource, render a generic
   counter without custom art, and prove affordability plus exact state.
4. **Zone/dynamic-content canary:** move cards through a bounded custom zone and
   produce a deterministic output whose source composition is asserted.
5. **Advanced acceptance character:** begin from a fresh natural-language idea
   not named after a Downfall role; compose at least two capability families and
   cross one non-BaseLib seam with zero manual coding.
6. **Later depth cells:** run setup/save round-trip, owned entities, hosted
   reward/rest choices, and finally D-level transpilers. Each advances
   independently on the support ladder; none inherits support merely because
   Downfall contains an example.

Steps 3 and 4 passed their open-mod Type + Scenario canaries on 2026-07-16. Step 5 then
passed through the fresh spatial-route `WayfinderAcceptance`: first source compile 0/0,
strict Tier 1, and isolated two-combat Tier 2 with both families plus the exact 6c UI seam.
The bounded Character Program is pipeline-supported; step 6 remains a set of independent
later depth cells rather than part of the M6 gate.

Art is not a gate for these cells. Use built-in/fallback visuals, generated
Godot nodes, or generic open-mod-owned scene templates until the programming
contract is live-green.
