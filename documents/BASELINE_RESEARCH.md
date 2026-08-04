# Current baseline

This file records the references that still inform active design after the RitsuLib
migration. Git history retains the earlier survey; the sections below keep only current
decisions and the evidence needed to apply them correctly.

## Active Runtime Baseline

open-mod targets:

- Slay the Spire 2 stable `0.107.1`;
- RitsuLib `0.5.4` and `STS2.RitsuLib.Compat.0.107.1`;
- .NET SDK 9;
- Codex plugin distribution plus a portable Agent Skills payload;
- cross-platform Python tools, with the complete loop currently verified on Windows.

`baselines/STS2-RitsuLib` is the maintainer checkout for API and compat research. Runtime
projects use the pinned package and installed runtime variant rather than copying that
checkout.

## Official RitsuLib Product-Semantics Baseline

The gitignored maintainer checkout `baselines/SlayTheSpire2ModdingTutorials` tracks
<https://github.com/GlitchedReme/SlayTheSpire2ModdingTutorials> at commit
`5a9110b3c1b1c428f9f349e51cd4a155266b92e3` (2026-07-26). It is the official tutorial
baseline for player-facing purpose, intended usage, examples, and documented RitsuLib
feature-Package membership.

The tutorial repository currently labels itself `public-beta`. It therefore does not
replace the stable `0.107.1` / RitsuLib `0.5.4` source and compat profile for exact symbols
or lifecycle behavior. Use the tutorial to answer "what product problem does this Package
solve?" and the pinned RitsuLib checkout to answer "does this exact public API exist on our
target?" Distill accepted findings into the shipped pack; generated Mods never read the
baseline or copy tutorial code.

The two directly relevant official pages establish:

- **[Card Hand Glow](https://tutorials.sts2modding.com/en/docs/04-ritsulib/04-19-hand-outline/):**
  vanilla yellow/red conditions plus conditional arbitrary-color glow,
  priority, and the option to hide the outline while a Card is unplayable;
- **[Extra Badges](https://tutorials.sts2modding.com/en/docs/04-ritsulib/04-22-1-extra-badge/):**
  additional/dual Power values, a separate Relic charge value, and
  auxiliary Intent information such as additional triggered hits, including refresh and
  occupied-corner guidance.

These are product semantics, not merely symbol examples. Under the Package-level rule in
`AGENTS.md`, the documented Package and all public consumers confirmed in the pinned source
are supported together. Missing recipe or real-host work is stated directly where relevant
and does not create another support classification.

## YuWanCard Character Baseline

The gitignored maintainer checkout `baselines/Sts2-YuWanCard` tracks
<https://github.com/YuWan886/Sts2-YuWanCard> at commit
`07d7daa64538e33137684a3af06e74e9b30e0678` (2026-07-25), Mod version `v0.5.11`, for
STS2 `0.107.1`. The surveyed tree contains 688 C# files, 525 PNGs, 27 Godot scenes, Spine
resources, audio, shaders, and custom UI. No automated test project was found. This makes
it useful as a large, same-version product and Character-consumer baseline, not as proof
that open-mod can generate or support those surfaces.

### Correct framework classification

YuWanCard is not a RitsuLib-authored Character implementation at the pinned revision:

- `YuWanCard.csproj` has no RitsuLib package/reference, and `YuWanCard.json` declares no
  RitsuLib runtime dependency;
- its README calls RitsuLib optional and says installing it only enables the settings UI;
- `ConfigRegistrar` detects RitsuLib at runtime and emits settings-provider types through
  reflection;
- Character registration, asset routing, energy icons, card-frame material, scenes, and
  many other features are implemented by its own registries, Node conversion, Publicizer,
  and Harmony patches.

Therefore this checkout may answer "what does a mature Character Mod need to present?"
and "what product patterns are worth researching?" It may not answer "which RitsuLib API
should a generated Mod call?" The latter remains owned by the pinned
`baselines/STS2-RitsuLib` checkout plus open-mod's focused live proofs.

### Findings that refine M6.5

1. **Treat theming as one structured Character contract.** `Pig`, `PigCardPool`, and the
   pool patches coordinate `NameColor`, `EnergyLabelOutlineColor`,
   `DeckEntryCardColor`, `EnergyOutlineColor`, a card-frame HSV color, and distinct large
   and text energy icons. open-mod should derive these values from one palette/motif brief
   instead of choosing each consumer independently.
2. **Do not spend an image-generation call on a complete card frame.** YuWanCard applies
   an HSV shader to a fixed frame material. The implementation is a private Harmony route
   and must not be copied, but it supports a cheaper product design: use RitsuLib's public
   pool-material surface with a reviewed deterministic frame/material template and theme
   parameters.
3. **Keep large and inline energy icons separate.** YuWanCard's
   `BigEnergyIconPath` is a 256x256 image shared with the energy counter's identity layer;
   `TextEnergyIconPath` is a separate 24x24 image. They have different consumers even
   when their visual identity matches. This confirms that open-mod's currently proven
   shared compact fallback is only a minimum and that the existing M6.5 split needs
   independent sizing and hosted proofs.
4. **The one-generated-energy-layer decision is credible, with a boundary.**
   `pig_energy_counter.tscn` supplies only one Character-specific `Layer1` and reuses
   vanilla Ironclad front/back VFX. This is evidence that the identity-bearing layer can
   carry most of the customization. It is not proof for RitsuLib's checked five-layer
   scene contract, so open-mod still keeps the lead-supplied fixed templates for layers
   2-5 and proves all five actual consumers.
5. **Animation needs geometry as well as cue names.** `Pig.CreateCreatureAnimator` uses a
   looping idle, one-shot attack/hit states that return to idle, and a non-looping terminal
   death state; missing states fall back to idle. Its combat scene also defines the visual
   baseline, bounds, and `IntentPos`, `CenterPos`, `OrbPos`, and `TalkPos` anchors. M6.5
   should contract frame order/duration, fallback and terminal behavior, plus stable
   geometry/anchors so the body and game UI remain aligned.
6. **A broad interface is Package inventory, not presentation proof.**
   `IYuWanCharacter` enumerates combat visuals, trail, top icon/outline, full energy,
   rest/merchant, selection portrait/background/locked portrait, map marker, transition,
   multiplayer hands, SFX, animation, and the cookie icon. The concrete Pig does not
   customize every row: map marker, locked selection, and trail fall back, while the
   outline currently reuses the normal icon. Those rows identify consumers, but YuWanCard
   is not an official RitsuLib Package baseline and does not establish RitsuLib support.
   Even for an official Package, the interface can establish membership while a headed
   review records only what was actually seen.
7. **Pixel dimensions and visible footprint are different contracts.** YuWanCard's
   selection portrait is the same 132x195 expected by open-mod and is assigned directly;
   its subject occupies 128 of 132 horizontal pixels. Its combat Character instead uses a
   scene with an explicit visual position, bounds, and UI anchors. This confirms that the
   current over-large open-mod results should be corrected through subject composition,
   transparent-canvas fill, and a public node transform, not smaller output files. The
   Pig-specific numbers are not reusable; open-mod still grounds and visibly proves its
   own selection/combat footprint against vanilla hosts.
8. **Relic outline acquisition should be deterministic.** The surveyed YuWanCard tree has
   66 relic PNGs and no separate outline PNGs; `YuWanRelicModel` returns the main icon path
   for `PackedIconOutlinePath`. This shows that a second AI image is unnecessary, but
   reusing an unchanged icon is not a real outline. RitsuLib exposes
   `RelicAssetProfile.IconOutlinePath`, so open-mod should derive a white/approved-color
   expanded silhouette from the normalized icon alpha and wire that distinct path.

M6.5 is closed. Its conclusions do not reopen custom locked selection/map-marker
presentation, trail, `Cast`, Spine, audio, or multiplayer presentation. Characters keep
the checked game-native shared map marker instead of copying or resizing one from a
research Mod.

### M6.6 closure

The human lead closed M6.6 after evaluating its provisional capability packages. Official
tutorial semantics plus pinned RitsuLib `0.5.4` public source determine Package support.
Recipes, builds, and real hosted proofs show what open-mod has implemented and observed.
Packages 2A computed Card values, 5
custom-Character dialogue in native Ancient scenes, 1 bounded advanced targeting, and 3
bounded Relic-owned Rest Site options have passed their focused gates. Their records live
under `documents/history/`.

- **Advanced Card/Potion target types (promoted):** deterministic Mod-local creature
  filtering now covers Card one/many and Potion one with native selection/cancellation,
  execution-time checks, and normal source-content lifecycle. Multi-target Potions remain
  a pinned lifecycle limitation.
- **Computed Card readability (promoted):** one formula now drives preview and execution
  for dynamic Damage/Block, Energy/Star icon counts, typed Power amounts, and variable
  tooltips in their real Card consumers.
- **Gameplay readability (promoted):** Card Hand Glow and
  Extra Badges are supported from the official semantics and pinned public APIs. Open-mod
  now lowers ordered fixed-color Card hand rules, up to three safe-corner Relic labels, and
  one top-left Power label. Multiple Power preset bands are not clipped and overflowed in a
  crowded 16:9 host row, so the generated Power boundary is intentionally narrower. The
  rebuilt proof passed the human-led 16:9/16:10 recheck and strict Tier 1; strict Tier 2 was
  not run. Intent
  is a supported Extra Badges consumer but its recipe was removed
  from current M6.6 work by the human lead on 2026-07-30. A badge may describe auxiliary
  same-intent information; it must not replace a separate debuff intent, and ordinary
  repeated identical attacks keep the native multi-attack intent.
- **Custom Rest Site options (promoted, bounded):** the product references established
  owned eligibility, localized title/description, custom icon, and asynchronous outcome.
  Open-mod now supports the narrower public RitsuLib route for a singleplayer Relic owner,
  free/fixed Gold, deterministic preflightable outcomes, once-per-site/run use, native
  stay/leave behavior, and explicit Heal-icon fallback. Card/Modifier ownership and the
  research Mod's card-acquisition preview remain outside the supported slice.
- **Custom Card Piles Package (promoted):** official RitsuLib `0.5.4` supplies the public
  registration, combat/run persistence, all documented UI styles and anchors, pile-screen
  capabilities, visibility/hotkeys, native movement/localization, and ExtraHand layout,
  callbacks, and native manual-play lifecycle. The human lead accepted the focused official-
  runtime cancellation/shortcut/consecutive-play recheck and promoted the complete Package
  under the repository's Package-level rule. Strict structured Tier 2 was waived, not run;
  the earlier private-repair experiment remains historical research rather than shipped code.
- **Custom-Character native Ancient dialogue (promoted):** RitsuLib's registered
  `AncientDialoguePopulateLocKeysPatch` appends localization-defined dialogue for Mod
  Characters to each native `AncientDialogueSet` once. The flat `ancients.json` contract
  covers ordered Ancient/Character lines, repeat and visit routing, transition prompts, and
  Architect attacker metadata. Open-mod now owns semantic intake, a pinned nine-target
  catalog, structural localization validation, and focused native-scene proof. The initial
  native-scene attempt exposed missing resource mounting, Event UI assets, and Darv Dusty
  Tome registration; the repaired Darv and Architect recheck passed. The YuWan
  implementation remains product evidence only and its private injection patch is not
  reusable.

### M6.7 vanilla-override grounding and planning inputs

The closed M6.7 track treats existing vanilla models as version-bound semantic targets,
not as permission for arbitrary generated patches. RitsuLib `0.5.4` provides enough public
composition surface for a broad design:

- `ConfigureDefaultModelCapabilities<TModel>` can attach generated capabilities to matching
  vanilla model types without replacing their identity;
- Card property contributors cover rarity/type/target/tags and local cost/result surfaces;
- `CardPlayCapability` can run before/after an owning Card and can suppress its original
  `OnPlay`, allowing a complete existing open-mod Card recipe to replace that behavior;
- typed owner capabilities extend vanilla Relic, Potion, Power, Orb, Enchantment,
  Affliction, and Monster hook streams; and
- RitsuLib `0.5.4` exposes four Card/CardPool material providers through
  `ExternalCardMaterialOverrideRegistry` plus 40 non-Card/public asset providers through
  `ExternalAssetOverrideRegistry`; and
- the checked RitsuLib patcher remains a bounded fallback for cataloged original entry
  points that have no public suppression/override surface.

The implementation should therefore use a per-STS2-version catalog plus semantic
`adjust`/`compose`/`replace`/`availability` operations. It can cover common balance changes
across Cards, Relics, Potions, Powers, pools, Monsters/Encounters, and Events, while routing
unusual AI or scene state machines to maintained target adapters. Disabling content should
remove acquisition routes rather than unregistering a model required by old saves. Preserve
typed dynamic variables, normal modifiers, localization truth, deterministic RNG, and
multiplayer parity; fail closed on target/signature/baseline drift.

M6.7.0 now implements the non-gameplay grounding layer. The `0.107.1` collectors observed
the exact `sts2.dll` SHA-256
`a1f9e653f1e28e4076558fee1e60d218619cb7e057b887c6417f62c62c6d7a52`, 3883 model-namespace
metadata types, and 1624 concrete vanilla `ModelDb` entries. Repeated host collection
produced the same runtime snapshot hash. RitsuLib `0.5.4`
`ModelTitleExtensions.TryGetTitleLocStringSource` supplies public stable table/key mappings
for 14 model families, and the game's documented public `LocManager.SetLanguage` temporarily
loads a requested language without updating the player's saved setting. The collector uses
that route, restores the original language, and fails if machine-local localization
overrides are active. The resulting catalog records 1580 stable title sources and 1537
English plus 1537 Simplified Chinese titles across the 14 pinned language columns. Exact
display titles are resolver aliases; duplicate titles remain explicit ambiguities, and this
does not make the resolver a general free-form language parser. The merged catalog now has
4165 reviewed Adapter fingerprints: the previous twenty for Ancient, availability, and pool
membership plus 4145 M6.7.5 non-Card targets. M6.7.0 initially emitted only a pinned empty
manifest and rejected every nonempty operation; M6.7.1 through M6.7.5 promote the first five
checked operation Packages. These grounding facts alone do
not prove a vanilla behavior, flow, availability, or visual edit.
By human-lead decision on 2026-08-03, source development stopped at the complete approved
M6.7.0-M6.7.5 matrix. The separate current-catalog headed no-op stayed unrun. The later
closure passed the full regression, synchronized both payloads, built an independent Mod
from the installed plugin, and received the lead's representative in-game acceptance.

M6.7.1 Public Card Overrides source development is complete. Default Card capabilities now
cover the grounded non-asset public contributor surface, capability-owned variables,
recipe-backed `OnPlay` composition/replacement, and owner draw/discard/exhaust hooks. The
exact routes, effect vocabulary, and exclusions are recorded in
`sts2-api/reference/vanilla-card-overrides.md`. Focused tests and a representative
compile-only check pass; selected Card text/play behavior was included in the consolidated
Mod that the human lead accepted as a whole. No individual-route observation is inferred.

M6.7.2 Public Visual Overrides source development is complete against upstream RitsuLib
`0.5.4` commit `8b971a79`. The complete public surface is 44 providers: four Card/CardPool
Material providers and 40 external providers for Relic, Power, Potion, Orb, Act, ordinary/
Ancient Event, Encounter, Affliction, Enchantment, and Modifier consumers. The manifest
requires exact target category/type/content kind and Mod-local typed resources; build
preflight checks required/optional files, directories, lists, traversal/script exclusions,
and path-vs-loaded-resource conflicts. Providers retain vanilla fallback and stable Mod-key
cleanup. No external registry exists for a vanilla Monster body, and cross-Mod provider
overlap remains outside same-Mod diagnostics. Focused manifest/resource tests pass. No AI
image generation or Package-specific representative C# compile ran. The consolidated
acceptance included selected Card and Darv visual providers; the human lead accepted the
Mod as a whole, so no individual-provider observation is inferred. Full regression and
payload synchronization passed at closure. Unselected providers remain unrun.

M6.7.4 Existing Vanilla Availability source development is complete. The public
`RequireEpoch` route is grounded for 57 pinned epoch IDs across vanilla Cards, Characters,
ordinary Events, and shared `EVENT.DARV`. Relic and Potion epoch/permanent-disable filters
use six fixed character/shared pool override dependencies each. Card, Relic, and Potion
pool add routes use `ModHelper.AddModelToPool`; remove/move membership uses fixed getter
Adapters. Complete `ModelDb` pool baselines, ordered membership simulation, primary-pool
acknowledgement, debug/empty-transition rejection, `existing_instances: preserve`, and
singleplayer scope are validated. No global weighting route exists, and Card/Character/
Event permanent disable remains unpromoted. Focused manifest/catalog/document-route tests
pass. The consolidated Mod included one Card pool move and was accepted as a whole; no
individual-route observation is inferred. Cache timing, unlock UI, fresh-acquisition
order/RNG, duplicate absence, and existing-save variants remain unrun; regression and
payload synchronization passed at closure.

M6.7.3 Existing Ancient Extensions source development is complete for the nine pinned
`AncientEventModel` targets. RitsuLib's public `AncientOption<TAncient>` route supports a
single rule returning multiple appended options with conditions, priority, and duplicate-
text policy. Complete initial-option replacement uses one reviewed postfix on
`GenerateInitialOptionsWrapper`: the original method creates and retains `_generatedOptions`,
then the Adapter clears and refills that same list before RitsuLib's append postfix runs.
This preserves native `Done()` choice-history reads and permits other Mods' public append
rules to compose after replacement. Protected `SetEventState` and `Done` calls are the only
two flow dependencies and are fixed `UnsafeAccessor` bindings, not prompt-derived patches.

The semantic Package includes nested owner/run/deck/model conditions, visible versus native-
locked options, one fixed Gold/HP/Max HP/no cost, typed Card/Relic/Potion/Power Hover Tips,
relic-backed presentation, ordered damage/heal/Gold/Max HP/model grants, deck upgrade/
remove/transform/enchant selectors, fixed custom rewards, bounded `weak_short` shake,
Mod-owned page graphs, and native finish. Text is Mod-local `events.json` in every shipped
language; `ancients.json` remains the Character-dialogue table. M6.7.2 existing-Ancient
visual routes compose as separate operations. `TheArchitect` is rejected because the pinned
game models it as an ordinary `EventModel`. New Ancient models, native opening-dialogue or
room replacement, line audio, randomized/RNG rewrites, special combat, direct merchant/
rest/treasure transitions, and multiplayer remain outside M6.7.3. Focused manifest,
localization, catalog, and route-documentation tests pass. No AI image generation or
Package-specific representative C# compile ran. The consolidated Mod included one Darv
replacement/page/portrait route and was accepted as a whole; no individual-route
observation is inferred, and other Ancient routes remain unrun.

M6.7.5 Existing Vanilla Non-Card Data and Behavior source development is complete. The
pinned RitsuLib surface provides typed owner capabilities for Relic, Potion, Power, Orb,
Enchantment, Affliction, and Monster. The promoted public vocabulary includes every 0.107.1
public `AbstractModel` hook collected from the exact assembly: 100 asynchronous callbacks,
26 scalar modifiers, 28 `Should*` decisions, plus four typed Orb callbacks. Composition
runs through default capabilities; complete owner-hook replacement uses fixed run/combat
stream Adapters and conflicts with every same-target composition rule.

The checked PE inventory adds sixteen intrinsic data routes and complete fingerprinted
body routes for Relic/Potion/Power/Orb/Enchantment/Affliction lifecycles, Monster move state
machines, Encounter `GenerateMonsters` plus `AllPossibleMonsters`, and ordinary Event
initial options plus Mod-owned pages. The catalog contains 4141 target-specific M6.7.5
method fingerprints and four shared stream/flow boundaries, for 4145 M6.7.5 and 4165 total
Adapters. Ordinary Event localization uses `<MOD_ID>_EVENT_*` in every shipped `events.json`;
Ancient keys remain separate. Affliction `AfterApplied()` and `BeforeRemoved()` are
synchronous `void`, so a complete replacement can suppress them only with empty effect
lists; async `OnPlay` and public owner hooks remain available. All promoted operations are
singleplayer. Focused 40-test manifest/catalog/localization/documentation checks and Python
syntax pass. The consolidated Mod included selected Relic, Monster, and Encounter routes
and was accepted as a whole; no individual-route observation is inferred. Unselected
lifecycle/intent/ordinary-Event and save/load variants remain unrun; full regression and
payload synchronization passed at closure.

The human lead canceled M6.7.6 on 2026-08-03 and declared M6.7 source development complete
at M6.7.5. On 2026-08-04 the lead reported that the independent-session representative
effects passed and explicitly closed M6.7. The exact result and exceptions are in
`documents/history/M67_VANILLA_OVERRIDES_RESULTS.md`. Multiplayer vanilla overrides are
future research rather than pending M6.7 implementation.

### Future research value

- **Mod settings and persistence:** this remains future outlook outside the provisional
  M6.6 list. The page/section/subpage model, toggles, sliders, custom entries, localization,
  persistence scopes, and immediate side effects form a useful product checklist. Because
  open-mod already requires RitsuLib, any future recipe should use its pinned public
  settings and persistence APIs directly rather than YuWanCard's reflection-emission
  bridge.
- **Character skins:** the repository keeps a stable skin ID, persists the selection,
  previews the real combat visuals on both normal and custom-run selection screens, and
  resolves skin-specific combat, merchant, and icon assets with per-slot fallback. A
  future open-mod design would need a declared skin bundle and explicit consumer coverage,
  not merely a second combat image.
- **Multiplayer mechanics and vanilla overrides:** the canceled M6.7.6 concept belongs to
  a separately selected future systems track. Custom reliable messages, identical override
  manifests on every peer, explicit serialization, deterministic state/RNG and choices,
  targeted run locations, save/load, remote presentation, request timeouts, disconnect
  cleanup, and host-authoritative content settings are the minimum promotion questions for
  an already-proved singleplayer operation family. Singleplayer behavior cannot simply be
  marked multiplayer-compatible.
- **Modifiers, badges, interoperability, and complex UI:** official Package documentation
  plus pinned public source can establish support before implementation. The generator
  still needs bounded semantic intake and recipes, and behavior/presentation claims still
  require proportional host verification.

### What not to carry forward

Do not copy YuWanCard's self-built `ContentRegistry`, Character getter patches,
assembly-wide patch discovery, NodeFactory, Publicizer/private-member access, wildcard
NuGet version, or optional reflection bridge into generated Mods. Do not add its telemetry
or update checker to open-mod output. The repository's main source license is MIT, but its
tree also records separately licensed third-party code/assets, and individual image,
audio, Spine, and shader provenance cannot be inferred from the root license. Study
behavior and code shape; do not redistribute or use those assets as generation references.

## Reused Design Ideas

The active architecture still borrows these durable ideas from the initial survey:

- **godogen:** file-based staged skills, publish-time rendering, progressive disclosure,
  and resumable state files;
- **spire-codex:** content facts and vanilla analogs, never C# API authority or a runtime
  dependency;
- **official RitsuLib tutorials:** product semantics and documented Package membership,
  never stable-version signature authority or a runtime dependency;
- **STS2/game decompile:** exact public command, lifecycle, enum, and host signatures used
  by maintainers to improve the shipped pack;
- **image tool research:** acquisition is optional and source-independent; deterministic
  normalization and verified consumers matter more than the image backend.

## Archived Research

`baselines/BaseLib-StS2` and `baselines/downfall` are retained only as offline historical
research. They explain pre-migration behavior and implementation depth. YuWanCard is a
current same-version product-depth reference under the narrower rules above. The official
tutorial checkout is an active semantics baseline, but remains maintainer-only. None of
these checkouts may be used to scaffold, author, build, repair, or run a generated Mod.

Claude-specific baseline repositories may remain locally for historical comparison, but
the product and publish flow now target Codex. They are not required to build or install
`0.6.0`.

## Decision Rules

1. Semantic intent is framework-neutral; RitsuLib owns the active adapter.
2. Support follows the Package-level rule in `AGENTS.md`; missing recipe or proof does not
   by itself make a documented public Package unsupported.
3. A successful build is not a behavior or presentation claim.
4. Public game/RitsuLib APIs are preferred; a private patch needs a separately grounded
   and hosted contract.
5. Do not add a helper unless an existing supported surface needs it and one focused proof
   can establish it.
6. Do not make a paid network call or switch image backends without explicit user choice.
7. Keep runtime sessions inside the shipped pack. Live decompilation and baseline research
   are maintainer work, not steps in `$modmaker`.
