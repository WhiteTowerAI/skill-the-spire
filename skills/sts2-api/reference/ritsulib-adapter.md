# RitsuLib adapter reference

This is the one lazy framework-specific reference for the active target. Read it
after a semantic SPEC is complete and only for the selected surface. Do not copy this
mapping into every recipe and do not reintroduce a second historical-framework branch.

## Pinned profile

```text
framework: RitsuLib
framework version: 0.5.4
host: STS2 stable 0.107.1
compat target: 0.107.1
profile id: ritsulib-0.5.4-sts2-0.107.1
```

The compat package or variant must resolve `lib/0.107.1/STS2-RitsuLib.dll` and the
matching compat marker/hash. A default beta-facing package is a hard failure, not a
fallback. `scaffold.py`, `ritsu_profile.py`, and
`build.py`; surface recipes consume that profile and never regenerate dependency logic.

Framework identity uses public or standard runtime metadata:

- framework version: public `STS2RitsuLib.Const.Version`;
- actual loaded compat target: `AssemblyMetadataAttribute` key `Sts2ApiCompat` on
  `typeof(STS2RitsuLib.Const).Assembly`;
- host version: the build/launch profile validates the installed game's
  `release_info.json` before packaging or launch.

RitsuLib's own compat-label helper is internal. Do not call it through reflection or
copy its implementation. Reading assembly metadata is a small diagnostics-only adapter
and is also what prevents a compile-time `0.107.1` constant from hiding a wrong DLL at
runtime.

## Common entry points

Use public RitsuLib entry points first:

```text
RitsuLibFramework.CreateContentPack(modId)
RitsuLibFramework.CreatePatcher(modId, name)
RitsuLibFramework.SubscribeLifecycle<TEvent>(...)
RitsuLibFramework.GetRunSavedDataStore(modId)
RitsuLibFramework.GetSecondaryResourceRegistry(modId)
RitsuLibFramework.GetNodeAttachmentRegistry(modId)
RitsuLibFramework.RegisterSingleTargetType(...)
RitsuLibFramework.RegisterSingleTargetTypeWithContext(...)
RitsuLibFramework.RegisterMultiTargetType(...)
```

The content-pack builder and registry are the shared registration boundary. A simple
surface must not initialize Character, Event, multiplayer, audio, materials, or other
unselected modules.

## Surface routing

| Semantic surface | RitsuLib public registration/template | Asset profile | Current boundary |
|---|---|---|---|
| Card | content-pack card registration; `ModCardTemplate` | `CardAssetProfile` | generated; hosted Tier 2 |
| Relic | content-pack relic registration; `ModRelicTemplate` | `RelicAssetProfile` | generated; hosted Tier 2 |
| Potion | content-pack potion registration; `ModPotionTemplate` | `PotionAssetProfile` | generated; hosted Tier 2 |
| Power | content-pack power registration; `ModPowerTemplate` | `PowerAssetProfile` | generated; hosted Tier 2 |
| Keyword | keyword registry/manifest entry | text-only tooltip fallback | generated; hosted Tier 2 |
| Enchantment | enchantment registration; `ModEnchantmentTemplate` | `EnchantmentAssetProfile` | generated; hosted Tier 2 |
| Orb | orb registration; `ModOrbTemplate` | `OrbAssetProfile` | generated; hosted Tier 2 |
| Monster | monster registration; `ModMonsterTemplate` | `MonsterAssetProfile` | generated; combat/bestiary proof |
| Encounter | act/global encounter registration; `ModEncounterTemplate` | `EncounterAssetProfile` | generated; real room proof |
| Event | shared/act event registration; `ModEventTemplate` | `EventAssetProfile` | generated; `MapNode` behavior/presentation proof |
| Character | character/starter registration; `ModCharacterTemplate<...>` | `CharacterAssetProfile` | generated; selection/combat/RestSite/Shop proof |
| Character combat cues | `SetupCustomCombatAnimationStateMachine` + private `VisualCueSet` | all-or-nothing static combat fallback | generated; Idle/Attack/Hit/Dead + cleanup proof |
| Stateful relic cadence | `SavedAttachedState<SpecificRelic, int/bool>` plus native model hooks | normal relic counter/fallback | generated; save round trip + two-combat Tier 2 |
| Relic-owned Rest Site option | owner `TryModifyRestSiteOptions` + `ModRestSiteOptionTemplate` | `RestSiteOptionAssetProfile` with explicit native fallback | generated; bounded singleplayer native Rest Site proof |
| Combat resource | `ModSecondaryResourceRegistry` + `SecondaryResourceCmd` | registered icons plus fixed counter fallback | generated; payment/reset + two-combat Tier 2 |
| Ordered semantic buffer | `AttachedState<PlayerCombatState,TState>` + native Card lifecycle | composed live counter text | generated; order/overflow/output/reset Tier 2 |
| Combat UI attachment | `RegisterCombatUi` + `ModNodeAttachmentRegistry` | 220x32 icon+text control at offset 160 | generated; public attachment + geometry proof |
| Advanced creature targeting | Mod-scoped custom `TargetType` registration + Card/Potion target extensions | native selection/reticles | generated for Card one/many and Potion one; multi Potion has a known lifecycle limitation |
| Card Hand Glow | `ShouldGlowGoldInternal` / `ShouldGlowRedInternal`; `CardHandOutline<TCard>(ModCardHandOutlineRules<TCard>)` | native hand outline | generated with ordered fixed-color rules; headed host result remains literal |
| Extra Badges | Power/Relic/Intent extra-label providers and change sources with `ExtraIconAmountLabelSpec` | native Power/Relic/Intent corners | Relic: up to three safe corners; Power: one top-left label because preset bands overlap in crowded rows; Intent supported but not scheduled |
| Custom Card Piles | `.CardPileOwned(...)` + `ModCardPileSpec` + native `CardPileCmd` | headless, top-bar, bottom-corner, ExtraHand, and pile-screen consumers | complete documented Package; selected behavior uses `reference/card-piles.md` |
| Existing vanilla Card behavior | vanilla catalog/resolver + one registered default `CardCapability` per target | preserve vanilla identity and untouched consumers | `reference/vanilla-card-overrides.md`; public package promoted |
| Existing vanilla visual surface | vanilla catalog/resolver + exact-type provider in the public Card-material/external-asset registries | checked Mod-local resource with vanilla fallback | `reference/vanilla-visual-overrides.md`; complete 44-provider Package promoted |
| Existing vanilla Ancient options | public `AncientOption<TAncient>` append or one fixed fingerprinted retained-list replacement Adapter; fixed `SetEventState`/`Done` flow access | native Ancient room, Mod-local pages, choice history, and optional composed visuals | `reference/vanilla-ancient-overrides.md`; append/replacement Package promoted |
| Existing vanilla availability | public `RequireEpoch` plus `ModHelper.AddModelToPool`; fixed Relic/Potion unlock filters and Card/Relic/Potion membership adapters | preserve vanilla model identity and existing instances while changing fresh acquisition | `reference/vanilla-availability-overrides.md`; singleplayer epoch/pool Package promoted |
| Other existing vanilla operation | vanilla catalog/resolver plus a later selected public capability or reviewed adapter | preserve vanilla identity and untouched consumers | `reference/vanilla-overrides.md`; grounding only until its package is promoted |

Registration remains data-driven: pool/act/availability comes from the semantic
`registration` section and is translated once by the adapter. Do not add a parallel
recipe tree for RitsuLib.

### Custom Card Piles

When SPEC declares any custom pile, read `reference/card-piles.md` and lower the complete
selected Package surface through `.CardPileOwned(...)`. That reference owns combat/run
lifetime, every public style and anchor, icon/hover/open/view/visibility/hotkey behavior,
native movement, localization, and ExtraHand presentation/manual play/callbacks. Official
RitsuLib `0.5.4` owns its internal native-Hand bridge; generated Mods emit no lifecycle
patch. Package support is not limited by which consumers appeared in the focused proof.

### Card

Author the model with `ModCardTemplate` and an explicit constructor that calls its
five-argument base constructor. Register it once in the scaffold's partial content hook:

```csharp
// <ModName>Code/MainFile.Content.cs
using MegaCrit.Sts2.Core.Models.CardPools;
using STS2RitsuLib;

namespace <ModName>;

public static partial class MainFile
{
    static partial void RegisterContent()
    {
        RitsuLibFramework.CreateContentPack(ModId)
            .Card<ColorlessCardPool, Cards.<CardName>>()
            .Apply();
    }
}
```

Do not add a historical pool attribute. The content-pack generic pool argument is the
single registration/availability source. Put explicit Mod art paths in `CardAssetProfile`;
leave it empty for the template/base-game fallback.

### Relic

Author the model with `ModRelicTemplate` and register it through the same content pack:

```csharp
RitsuLibFramework.CreateContentPack(ModId)
    .Relic<SharedRelicPool, Relics.<RelicName>>()
    .Apply();
```

The normal combat hooks remain game model overrides. A combat-start Energy relic uses
`AfterSideTurnStart`, the owner/participant guard, and `TurnNumber <= 1`; RitsuLib does
not replace that semantic hook. Put explicit main, derived-outline, and big Mod icon paths
in `RelicAssetProfile`; RitsuLib checks each override and retains its fallback. Leave the
profile empty in placeholder mode.

For run-persistent state owned by a concrete relic instance, declare a
`private static readonly SavedAttachedState<SpecificRelic, int/bool>` handle. Include
`ModId` in its supplied name, mutate the handle from the mutable relic, and call
`InvokeDisplayAmountChanged()` when the shown value changes. RitsuLib discovers the static
handle and bridges it through the relic's normal `SavedProperties` path. Do not put
relic-owned cadence in `RunSavedDataStore`; reserve that store for state naturally owned by
the run/player. Combat-local cadence continues to read
`Owner.PlayerCombatState.TurnNumber` and does not allocate attached saved state.

The R5 `RitsuStateProof` advanced real player turns in two combats, restored progress `2`
and `used=true` through `SavedProperties.From`/`Fill`, crossed the run cadence on combat 2
turn 1 without repeating the bool one-shot, and proved a separate turn-2 combat-local
effect reset to turn 1. It reached `selftest done`,
strict Tier 2, and no fresh error with the historical framework absent. See
`stateful-mechanics.md` for the
generated shape and proof contract.

For an optional Relic-owned Rest Site action, keep normal Relic content-pack registration
and add the public host hook described in `rest-site-options.md`. The owner contributes one
`ModRestSiteOptionTemplate` only when it is eligible, rejects an existing stable
Mod-namespaced `OptionId`, and hides in every non-singleplayer mode. `IsEnabled` and
`OnSelect` share the same fixed-Gold predicate; `OnSelect` repeats the complete check before
the first mutation because native buttons snapshot clickability at creation.

The first slice accepts free or fixed Gold cost, one deterministic preflightable outcome,
once-per-site or `SavedAttachedState<SpecificRelic,bool>` once-per-run use, and normal
leave or one-shot preservation of other options. The optional `RestSiteOptionAssetProfile`
must resolve a missing Mod texture to `res://images/ui/rest_site/option_heal.png`; a
custom `OptionId` has no usable implicit vanilla icon. Card/Modifier ownership,
post-payment choices, rollback transactions, same-site repeat, and multiplayer are not
adapter routes. The bounded surface is implemented after the focused native Rest
Site matrix passed.

### Potion, Power, Keyword, Enchantment, and Orb

These surfaces use the same content-pack boundary; each is registered exactly once in
the selected scaffold's `RegisterContent()` hook and then resolved by its normalized public
entry. The surface recipe owns effect details, while this adapter owns the framework shape:

| Surface | Registration | Entry/profile contract | Hosted invariant |
|---|---|---|---|
| Potion | `.Potion<SharedPotionPool, TPotion>()` | `MOD_POTION_TYPENAME`; checked `PotionAssetProfile` or template fallback | `EmberDraft` procures, uses on an enemy, and deals exact `4` damage |
| Power | `.Power<TPower>()` | `MOD_POWER_TYPENAME` retains CLR suffix; checked `PowerAssetProfile` or fallback | `ChargePower` applies as `Counter` and mutates `2 -> 3` |
| Keyword | `.CardKeywordOwnedByLocNamespace(stem, iconPath: null, ...)` | `MOD_KEYWORD_STEM`; native `CardKeyword`, text-only null-icon tooltip | `Resonant` is in the Card's native set and localizes |
| Enchantment | `.Enchantment<TEnchantment>()` | `MOD_ENCHANTMENT_TYPENAME`; checked 64x64 `EnchantmentAssetProfile` or fallback | `Guarded` attaches at `5` and changes Block `7 -> 12` |
| Orb | `.Orb<TOrb>()` | `MOD_ORB_TYPENAME`; 100x100 icon profile plus explicit Frost body/SFX fallback | `ShelterOrb` channels, passively blocks `2`, evokes `5`, and is removed |

Do not add a historical pool attribute, custom historical model bases, reflection
auto-discovery, or a second registration path. Keyword behavior stays in its host
Card/Power; the keyword itself owns
only the native vocabulary and localized tooltip. An Orb icon never promotes its persistent
combat body or animation contract.

### Advanced creature targeting

When the semantic target has a custom live-creature filter, route to
`reference/advanced-targeting.md`. Register its stable Mod-local target value immediately
at the start of `MainFile.RegisterContent()`, before the deferred content pack constructs
the consuming Card/Potion models. Single-target source rules use `CustomTargetContext` only
when declared; multi-target rules can read candidate and acting player only.

Cards resolve through `CardModelTargetingExtensions.GetTargets`; Potions expose the matching
`PotionModelTargetingExtensions.GetTargets`. The pinned adapter supports Card one/many and
Potion one. It rejects `potion + many` because the host does not recheck an empty group
before removing a queued Potion. Do not add a generated patch or remove-then-restore path.

The focused `M66TargetingProof` host passed the human lead's zero-, single-, and
multi-candidate mouse/controller matrix. Current-run logs recorded exact single Card/Potion
Block deltas and two multi Card resolutions over creature IDs `1,2`, with matching Tier 1
and no fresh target-Mod error. No automated `selftest done` ran, and queued-target
invalidation was not exercised; preserve those as verification exceptions rather than a
strict Tier 2 pass.

### Monster and Encounter

Author the fought enemy as one vertical slice. Register the monster and encounter once in
the same content pack; select an act registration when the semantic contract names one act,
or a global registration plus `IsValidForAct` when availability spans acts:

```csharp
RitsuLibFramework.CreateContentPack(ModId)
    .Monster<Monsters.<MonsterName>>()
    .ActEncounter<Glory, Encounters.<EncounterName>>()
    .Apply();
```

The monster extends `ModMonsterTemplate`; the encounter extends `ModEncounterTemplate` and
declares `RoomType` explicitly. Static art uses `MonsterAssetProfile` for the checked
`creature_visuals/fallback` scene and overrides `TryCreateCreatureVisuals()` to call
`RitsuGodotNodeFactories.CreateFromResource<NCreatureVisuals>(texture)` only after the
loose 360x360 PNG exists. This one factory path feeds both combat and the default bestiary.
Do not add historical constructor registration, pool attributes, or a second visual path.

The R4 `RitsuMonsterProof` registered `BattleFocus`, `CanarySentinel`, and its global
encounter through one content pack. A RitsuLib-only headed run traversed both sides of its
two-cycle move vocabulary, rendered the same static body in combat and a real bestiary,
reached `selftest done`, and passed strict Tier 2 with no fresh error.

### Event

Author a normal Event with `ModEventTemplate` and register it once as shared across act
pools or scoped to one act:

```csharp
RitsuLibFramework.CreateContentPack(ModId)
    .SharedEvent<Events.<EventName>>()
    // Or: .ActEvent<Glory, Events.<EventName>>()
    .Apply();
```

Nested localization is a flat `events.json` table under the normalized
`MOD_EVENT_TYPENAME` entry. Build enabled/locked options explicitly with `EventOption`,
`InitialOptionKey`, and `ModOptionKey`; use `CreateModRelicOption<T>` only for the grounded
normal relic-backed presentation. `EventAssetProfile.InitialPortraitPath` owns the checked
initial portrait/fallback. Filter the convention-derived missing portrait from
`GetAssetPaths` when the profile selects a differently named loose PNG. Later pages may
switch one checked texture through the public `NEventRoom` host.

The 2026-07-23 RitsuLib-only Event run registered all proof Events through one content pack
and drove core Cmd/pages, typed option/lethal presentation, native acquisition/shake/VFX,
selection/reward/special-combat outcomes, `portrait_halo`, rich text, and the bounded forced
follow-up in one `MapNode` suite. It reached `selftest done` and strict Tier 2 with no fresh
error. This does not promote arbitrary RitsuLib Event layout/VFX APIs or Ancient layouts.

### Character

Use the typed template and public type-list pools, then register the Character, starters,
and every pool member through the same content pack:

```csharp
RitsuLibFramework.CreateContentPack(ModId)
    .Character<Characters.<CharacterName>>(character => character
        .AddStartingCard<Cards.<Strike>>(5, order: 10)
        .AddStartingCard<Cards.<Guard>>(5, order: 20)
        .AddStartingRelic<Relics.<StarterRelic>>(1, order: 0))
    .Card<Characters.<CardPool>, Cards.<Strike>>()
    .Relic<Characters.<RelicPool>, Relics.<StarterRelic>>()
    .Potion<Characters.<PotionPool>, Potions.<Potion>>()
    .Power<Powers.<Power>>()
    .Apply();
```

The model extends `ModCharacterTemplate<TCardPool,TRelicPool,TPotionPool>`; the pools extend
`TypeListCardPoolModel`, `TypeListRelicPoolModel`, and `TypeListPotionPoolModel`. There is
no constructor auto-registration, pool attribute, or historical character template. Before
Shop proof, register at least two eligible non-Basic Attacks, two Skills, and one Power.

`CharacterAssetProfile` owns the promoted static fallback and scene paths. Leave
`Scenes.VisualsPath` unset for a generated combat PNG; an existence-checked
`TryCreateCreatureVisuals()` passes the texture and reviewed
`VisualNodeStyle` (`scale=0.80`, `position=(0,-184)`) to RitsuLib's public resource factory,
and returns `null` when absent so the resolved profile fallback resumes. Raw `.tscn`
wrappers own the layered top icon, selection background, RestSite, Shop, and the five-layer
native energy counter. Set `Ui.IconTexturePath` to `icon.png`,
`Ui.IconOutlineTexturePath` to the deterministic 88x88 `icon_outline.png`, and
`Ui.IconPath` to the raw icon scene that layers outline behind main. The card pool splits
its Energy consumers through the same public pool model:
`BigEnergyIconPath` checks a 256x256
`energy_large.png`, while `TextEnergyIconPath` independently checks a 24x24
`energy_text.png`. `EnergyIconHelper.GetPath` owns the large `NCard` consumer and
`EnergyIconsFormatter` owns the rich-text consumer.

The bounded non-Spine combat route builds its Idle/Attack/Hit/Dead `VisualCueSet` only when
all eighteen 512x512 resources exist, then passes that private set directly to
`ModAnimStateMachines.StandardCue` from `SetupCustomCombatAnimationStateMachine`. Keep
`CharacterAssetProfile.VisualCues` unset: RitsuLib also consults it for merchant/rest
playback. An incomplete set selects static `combat.png`, or the resolved profile fallback
when the static file is absent. Read `reference/character-combat-cues.md` for timing,
geometry, cleanup, and proof.

For the bounded Character card-frame theme, `TypeListCardPoolModel` already implements
`IModCardPoolFrameMaterial`. Return one cached
`MaterialUtils.CreateReplaceHueShaderMaterial(r, g, b, brightness)` from
`PoolFrameMaterial`; RitsuLib applies it to the pool's vanilla frame texture and ignores
the path-based material while the direct material is non-null. Keep the four game-owned
color properties and both icon paths in the same Character-local theme contract. Do not
copy YuWanCard's private shader/patch route or add a custom shader.

The generated Character proof derives identity, HP, Card/Relic/Potion pools, supporting
models, starter multisets, and MaxEnergy from the current `SPEC.md`, then checks every
promoted static consumer in selection, combat, top panel, a real hand Card, RestSite, and
Shop before `selftest done`. Locked selection, map marker, and Ancient remain outside this
proof. The resource/buffer/UI composition below does not broaden those Foundation
boundaries.

For registered model surfaces, the default public entry is `MOD_CATEGORY_TYPENAME`, with every segment
normalized to uppercase snake case by `ModContentRegistry`. Example: mod id
`RitsuCardProof`, `Jolt : CardModel` becomes `RITSU_CARD_PROOF_CARD_JOLT`; localization
uses that exact flat stem in `cards` or `relics`. Use `ModelPublicEntryOptions.FromStem`
only to preserve an already-published identity, never as a second naming system.

### Combat resource and public UI attachment

Use RitsuLib Secondary Resources as the single amount store. Register a
`SecondaryResourceDefinition` through
`RitsuLibFramework.GetSecondaryResourceRegistry(ModId)` with explicit default/minimum,
turn-start policy, combat persistence, and checked icon paths. Use
`SecondaryResourceCmd.Get`, `Gain`, and `Spend`; keep an explicit semantic `CanAfford`
helper, and apply the payoff only when `Spend` returns true. Do not add a duplicate integer,
manual combat reset, run-save property, or alternative-Energy hook.

Mount the live control through the same registry's public `RegisterCombatUi` method and a
`NodeAttachmentOptions.AttachParentSelector` that selects
`NCombatUi.EnergyCounterContainer`. Resolve the mounted node through
`RitsuLibFramework.GetNodeAttachmentRegistry(ModId).TryGetAttached`; update composed state
with `SecondaryResourceUiRuntime.UpdateCombatUi`. The generated control is fixed at 220x32,
contains an optional checked 24x24 icon plus a minimum 188x32 Label, and retains identical
live text when the icon is missing.

The final Character composition places the control at `(160,0)`. Tier 2 must assert that
its global rect does not intersect the native 128x128 energy counter. Do not emit a Harmony
postfix or separate patch module for this public RitsuLib route.

The maintained two-combat proof derives resource identity, amounts, payoff, and reset values
from the current `SPEC.md`, then verifies affordability, successful and rejected
all-or-nothing payment, public attachment, icon/text fallback, disjoint UI, and reset before
`selftest done`. See `character-resource.md` for the copyable contract.

### Ordered semantic buffer

Use `AttachedState<PlayerCombatState,TState>` for combat-owned semantic values. Reject
capacity overflow before mutation, append only the immutable semantic value, and let every
source Card complete STS2's normal Play -> Discard lifecycle. Snapshot and clear the values
at the compile point, refresh the public combat UI, configure one mutable output Card, and
add it through `CardPileCmd.AddGeneratedCardToCombat`.

The final proof derives semantic order, capacity, source and compile result piles, generated
history, output fields/effect, payment, and combat-2 reset from the current `SPEC.md`.
Retained Card instances, `CustomPile`, `Vector2.Zero` layout, and `skipVisuals: true`
lifecycle are not adapter routes. See `ordered-card-buffer.md`.

## Cross-cutting routes

| Semantic concern | Adapter input | RitsuLib route | Boundary |
|---|---|---|---|
| Relic-owned run state | `state.lifetime=run`, concrete relic owner, `int`/`bool` | `SavedAttachedState<SpecificRelic,T>` | current support is concrete custom Relics only; prove save round-trip |
| Other run state | `state.lifetime=run`, run/player owner, save fields | `RunSavedDataStore` | not implemented; no new shared runtime |
| Lifecycle | semantic trigger and reset boundary | typed `SubscribeLifecycle<TEvent>` or the model's public hook | no guessed event type |
| Combat resource | nonnegative amount, payment, reset, UI fallback | secondary-resource registry/commands + public `RegisterCombatUi` | combat-only; does not replace native Energy |
| Ordered buffer | semantic value, capacity, compile/output | `AttachedState<PlayerCombatState,TState>` + native result piles | no retained Card instances or custom zone |
| Advanced target | consumer/mode/id and pure creature predicate | custom target registration + `GetTargets` at resolution | Card one/many, Potion one; multi Potion has a known limitation |
| Card hand emphasis | ordered meanings/conditions/colors/priorities and unplayable visibility | vanilla glow override for one gold/red rule or one typed `CardHandOutline<TCard>` ruleset | fixed colors only; normal combat-state refresh; headed result remains literal |
| Relic/Power extra badge | Relic up to three safe-corner values or Power one top-left value, format, refresh/removal | typed extra-label specs provider plus host display or independent change source | Power preset bands overlap in crowded rows; no bottom-right/arbitrary rectangle; native main amount remains |
| Relic-owned Rest Site option | eligibility, repeatability, free/fixed Gold, deterministic outcome, stay/leave | `ModRestSiteOptionTemplate` + owner hooks + optional saved bool | singleplayer only; no Card/Modifier owner or arbitrary transaction |
| Custom Card Piles | pile identity/scope/style/anchor/open/view/visibility/hotkeys, movement, localization, ExtraHand behavior | `.CardPileOwned(...)`, `ModCardPileSpec`, `CardPileCmd`, `GetPile` | complete documented public Package; verify the consumers selected by SPEC |
| Asset | consumer profile and fallback | per-surface asset profile | retain current placeholder and unsupported consumers |
| Patch seam | exact target, version/fingerprint, risk, failure | `CreatePatcher` only when public APIs are insufficient | no arbitrary patches, C/D targets, or `OpenMod.Runtime` |
| Diagnostics | framework profile and proof route | shared marker fields from semantic contract | marker is not state proof |

## Unsupported, planned, and limited seams

Official product semantics plus a public API in this pinned profile support the documented
Package and its public consumers. Missing authoring work or verification does not change
that. Keep actual no-route boundaries explicit: alternative Energy, behavior-bearing
arbitrary Event layouts/VFX, new Ancient models and global native-dialogue/room replacement,
Ancient flow outside the fixed option/page vocabulary, animation beyond packaged
public resources, multiplayer
presentation, audio, run-persistent Character resources,
and direct merchant/rest/treasure transitions. Existing-Card operations, public
visual operations, existing-Ancient option/branch operations, and pinned
epoch/pool availability operations are generated. Global weighting, unpromoted permanent
disable surfaces, and every other vanilla operation remain gated by a later grounded
Package. Custom multi-target Potions retain a known limitation until the pinned host/framework can cancel
an empty queued group before consumption.

## Adapter record

For each generated mod, record this small implementation-only block in `MEMORY.md`:

```markdown
- framework profile: ritsulib-0.5.4-sts2-0.107.1
- adapter: <surface>/<contract-version>
- registration route: <shared/act/standalone/host-owned>
- asset profile: <profile or fallback>
- diagnostic status: <selected/resolved/fallback/failed>
- proof route: <suite and invariant>
- residual risk: <one short sentence>
```
