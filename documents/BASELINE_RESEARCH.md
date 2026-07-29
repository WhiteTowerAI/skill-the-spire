# Current baseline

This file records the references that still inform active design after the RitsuLib
migration. Git history retains the earlier survey; the sections below keep only current
decisions and the evidence needed to apply them correctly.

## Active Runtime Baseline

open-mod targets:

- Slay the Spire 2 stable `0.107.1`;
- RitsuLib `0.4.62` and `STS2.RitsuLib.Compat.0.107.1`;
- .NET SDK 9;
- Codex plugin distribution plus a portable Agent Skills payload;
- cross-platform Python tools, with the complete loop currently verified on Windows.

`baselines/STS2-RitsuLib` is the maintainer checkout for API and compat research. Runtime
projects use the pinned package and installed runtime variant rather than copying that
checkout.

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
6. **A broad interface is an inventory, not presentation evidence.**
   `IYuWanCharacter` enumerates combat visuals, trail, top icon/outline, full energy,
   rest/merchant, selection portrait/background/locked portrait, map marker, transition,
   multiplayer hands, SFX, animation, and the cookie icon. The concrete Pig does not
   customize every row: map marker, locked selection, and trail fall back, while the
   outline currently reuses the normal icon. Those rows identify future consumers but do
   not justify a claim that the corresponding custom presentation works.
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

### M6.6 planning inputs

The human lead selected five provisional capability packages for M6.6. These research
findings identify product requirements only; pinned RitsuLib `0.4.62` and real hosted
proofs remain the API and support authority.

- **Advanced Card/Potion target types:** bound filtering, selection/cancel behavior,
  revalidation, ownership, and the resulting source-content lifecycle rather than exposing
  an arbitrary patch hook.
- **Gameplay readability:** independently prove computed previews, dynamic Energy/Star and
  typed Power amounts, variable tooltips, conditional hand emphasis, and bounded
  Relic/Power/Intent labels in their real consumers.
- **Custom Rest Site options:** `RoastPorkRestSiteOption` demonstrates the product shape of
  owned eligibility, localized title/description, custom icon, asynchronous outcome, and
  card-acquisition preview. The generated implementation must use RitsuLib's public Rest
  Site template rather than research-Mod code.
- **Combat-only CardPile/ExtraHand:** begin with a visible singleplayer Mod-local pile and
  explicit ordering, movement, capacity, interaction, and cleanup. Persistence,
  multiplayer, vanilla-pile replacement, and general retained-card semantics stay outside
  the first slice.
- **Custom-Character native Ancient dialogue:** RitsuLib's registered
  `AncientDialoguePopulateLocKeysPatch` appends localization-defined dialogue for Mod
  Characters to each native `AncientDialogueSet` once. The flat `ancients.json` contract
  covers ordered Ancient/Character lines, repeat and visit routing, transition prompts, and
  Architect attacker metadata. Open-mod still needs semantic intake, a pinned Ancient
  catalog, structural localization validation, and focused native-scene proof; the YuWan
  implementation is product evidence only and its private injection patch is not reusable.

### M6.7 vanilla-override planning inputs

The planned M6.7 track treats existing vanilla models as version-bound semantic targets,
not as permission for arbitrary generated patches. RitsuLib `0.4.62` provides enough public
composition surface for a broad design:

- `ConfigureDefaultModelCapabilities<TModel>` can attach generated capabilities to matching
  vanilla model types without replacing their identity;
- Card property contributors cover rarity/type/target/tags and local cost/result surfaces;
- `CardPlayCapability` can run before/after an owning Card and can suppress its original
  `OnPlay`, allowing a complete existing open-mod Card recipe to replace that behavior;
- typed owner capabilities extend vanilla Relic, Potion, Power, Orb, Enchantment,
  Affliction, and Monster hook streams; and
- the checked RitsuLib patcher remains a bounded fallback for cataloged original entry
  points that have no public suppression/override surface.

The implementation should therefore use a per-STS2-version catalog plus semantic
`adjust`/`compose`/`replace`/`availability` operations. It can cover common balance changes
across Cards, Relics, Potions, Powers, pools, Monsters/Encounters, and Events, while routing
unusual AI or scene state machines to maintained target adapters. Disabling content should
remove acquisition routes rather than unregistering a model required by old saves. Preserve
typed dynamic variables, normal modifiers, localization truth, deterministic RNG, and
multiplayer parity; fail closed on target/signature/baseline drift.

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
- **Multiplayer mechanics:** custom reliable messages, explicit serialization, targeted
  run locations, request timeouts, disconnect cleanup, and host-authoritative content
  settings demonstrate why multiplayer is a separate systems track. Singleplayer behavior
  cannot simply be marked multiplayer-compatible.
- **Modifiers, badges, interoperability, and complex UI:** these remain useful inventories
  of the downstream persistence, deterministic RNG, localization, networking, and real-
  host UI work each feature can require. Each needs its own bounded public-API research and
  hosted proof before it can enter the support graph.

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
- **STS2/game decompile:** exact public command, lifecycle, enum, and host signatures used
  by maintainers to improve the shipped pack;
- **image tool research:** acquisition is optional and source-independent; deterministic
  normalization and verified consumers matter more than the image backend.

## Archived Research

`baselines/BaseLib-StS2` and `baselines/downfall` are retained only as offline historical
research. They explain pre-migration behavior and implementation depth. YuWanCard is a
current same-version product-depth reference under the narrower rules above. None of these
three may be used to scaffold, author, build, repair, or run a generated Mod.

Claude-specific baseline repositories may remain locally for historical comparison, but
the product and publish flow now target Codex. They are not required to build or install
`0.6.0`.

## Decision Rules

1. Semantic intent is framework-neutral; RitsuLib owns the active adapter.
2. A successful build is not a behavior or presentation claim.
3. Public game/RitsuLib APIs are preferred; a private patch needs a separately grounded
   and hosted contract.
4. Do not add a helper unless an existing supported surface needs it and one focused proof
   can establish it.
5. Do not make a paid network call or switch image backends without explicit user choice.
6. Keep runtime sessions inside the shipped pack. Live decompilation and baseline research
   are maintainer work, not steps in `$modmaker`.
