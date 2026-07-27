# RitsuLib adapter reference

This is the one lazy framework-specific reference for the active target. Read it
after a semantic SPEC is complete and only for the selected surface. Do not copy this
mapping into every recipe and do not reintroduce a second historical-framework branch.

## Pinned profile

```text
framework: RitsuLib
framework version: 0.4.62
host: STS2 stable 0.107.1
compat target: 0.107.1
profile id: ritsulib-0.4.62-sts2-0.107.1
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
```

The content-pack builder and registry are the shared registration boundary. A simple
surface must not initialize Character, Event, multiplayer, audio, materials, or other
unselected modules.

## Surface routing

| Semantic surface | RitsuLib public registration/template | Asset profile | Support status |
|---|---|---|---|
| Card | content-pack card registration; `ModCardTemplate` | `CardAssetProfile` | pipeline-supported; hosted Tier 2 |
| Relic | content-pack relic registration; `ModRelicTemplate` | `RelicAssetProfile` | pipeline-supported; hosted Tier 2 |
| Potion | content-pack potion registration; `ModPotionTemplate` | `PotionAssetProfile` | pipeline-supported; hosted Tier 2 |
| Power | content-pack power registration; `ModPowerTemplate` | `PowerAssetProfile` | pipeline-supported; hosted Tier 2 |
| Keyword | keyword registry/manifest entry | text-only tooltip fallback | pipeline-supported; hosted Tier 2 |
| Enchantment | enchantment registration; `ModEnchantmentTemplate` | `EnchantmentAssetProfile` | pipeline-supported; hosted Tier 2 |
| Orb | orb registration; `ModOrbTemplate` | `OrbAssetProfile` | pipeline-supported; hosted Tier 2 |
| Monster | monster registration; `ModMonsterTemplate` | `MonsterAssetProfile` | pipeline-supported; combat/bestiary proof |
| Encounter | act/global encounter registration; `ModEncounterTemplate` | `EncounterAssetProfile` | pipeline-supported; real room proof |
| Event | shared/act event registration; `ModEventTemplate` | `EventAssetProfile` | pipeline-supported; `MapNode` behavior/presentation proof |
| Character | character/starter registration; `ModCharacterTemplate<...>` | `CharacterAssetProfile` | pipeline-supported; selection/combat/RestSite/Shop proof |
| Stateful relic cadence | `SavedAttachedState<SpecificRelic, int/bool>` plus native model hooks | normal relic counter/fallback | pipeline-supported; save round trip + two-combat Tier 2 |
| Combat resource | `ModSecondaryResourceRegistry` + `SecondaryResourceCmd` | registered icons plus fixed counter fallback | pipeline-supported; payment/reset + two-combat Tier 2 |
| Ordered semantic buffer | `AttachedState<PlayerCombatState,TState>` + native Card lifecycle | composed live counter text | pipeline-supported; order/overflow/output/reset Tier 2 |
| Combat UI attachment | `RegisterCombatUi` + `ModNodeAttachmentRegistry` | 220x32 icon+text control at offset 160 | pipeline-supported; public attachment + geometry proof |

Registration remains data-driven: pool/act/availability comes from the semantic
`registration` section and is translated once by the adapter. Do not add a parallel
recipe tree for RitsuLib.

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

For the bounded Character card-frame theme, `TypeListCardPoolModel` already implements
`IModCardPoolFrameMaterial`. Return one cached
`MaterialUtils.CreateReplaceHueShaderMaterial(r, g, b, brightness)` from
`PoolFrameMaterial`; RitsuLib applies it to the pool's vanilla frame texture and ignores
the path-based material while the direct material is non-null. Keep the four game-owned
color properties and both icon paths in the same Character-local theme contract. Do not
copy YuWanCard's private shader/patch route or add a custom shader.

The 2026-07-23 RitsuLib-only Wayfinder run proved exactly one selected Character, HP
`72/72`, exact Card/Relic/Potion pools plus one supporting Power, exact starter multisets,
Energy `3/4`, and every promoted static consumer in selection, combat, top panel, a real
hand Card, RestSite, and Shop. It reached
`character foundation/static-presentation ... observed=all`, `selftest done`, and no fresh
error. Locked selection, map marker, and Ancient remain outside this proof. The separate R5
composition below adds resource/buffer/UI parity without broadening those R4 boundaries.

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
its global rect does not intersect the native 128x128 energy counter. The proof observed
resource rect `(260,828,220,32)` and energy rect `(100,828,128,128)`. Do not emit a
Harmony postfix or separate patch module for this public RitsuLib route.

`RitsuResourceProof` independently proved default/reset, affordability, successful and
rejected all-or-nothing payment, public attachment, icon/text fallback, and two real
combats. `RitsuWayfinderProof` then proved Ink `0 -> 4 -> 0`, the disjoint UI composition,
native Energy `3/4`, and combat-2 Ink `0`. Both reached `selftest done`, strict Tier 2, and
no fresh error with the historical framework absent. See `character-resource.md` for the
copyable contract.

### Ordered semantic buffer

Use `AttachedState<PlayerCombatState,TState>` for combat-owned semantic values. Reject
capacity overflow before mutation, append only the immutable semantic value, and let every
source Card complete STS2's normal Play -> Discard lifecycle. Snapshot and clear the values
at the compile point, refresh the public combat UI, configure one mutable output Card, and
add it through `CardPileCmd.AddGeneratedCardToCombat`.

The final proof observed `N>E>S>W`, non-destructive overflow, source and compile Cards in
Discard, one `CardGeneratedEntry`, one Hand output with dynamic Block `20`, and a distinct
empty combat-2 attached state. Retained Card instances, `CustomPile`, `Vector2.Zero` layout,
and `skipVisuals: true` lifecycle are not adapter routes. See `ordered-card-buffer.md`.

### Open-mod Scry helper

When the semantic Card effect is top-X Scry, emit the generated-Mod-local
`OpenModScry.Execute` implementation from `scry-helper.md`. RitsuLib `0.4.62` has no public
equivalent. The helper uses STS2's public `CardSelectCmd.FromSimpleGrid`, `CardPileCmd.Add`,
discard history, and `Hook.AfterCardDiscarded`; it returns requested/seen/discarded Cards
and preserves unselected Draw order. Nonpositive, missing/ending-combat, and empty-Draw
inputs return an empty result without opening UI.

This adapter is singleplayer-only and throws clearly in multiplayer/replay. It does not
register a global Scry modifier/completion hook or cross-Mod service. `RitsuHelpersProof`
passed visible overlay, await, zero/empty/short/full, order, history, and discard-hook
invariants in one `CombatPlayer` run, ending at
`R6 scry helper complete expected=all observed=all`, strict Tier 2, and no fresh error.

## Cross-cutting routes

| Semantic concern | Adapter input | RitsuLib route | Boundary |
|---|---|---|---|
| Relic-owned run state | `state.lifetime=run`, concrete relic owner, `int`/`bool` | `SavedAttachedState<SpecificRelic,T>` | current support is concrete custom Relics only; prove save round-trip |
| Other run state | `state.lifetime=run`, run/player owner, save fields | `RunSavedDataStore` | not pipeline-supported; no new shared runtime |
| Lifecycle | semantic trigger and reset boundary | typed `SubscribeLifecycle<TEvent>` or the model's public hook | no guessed event type |
| Combat resource | nonnegative amount, payment, reset, UI fallback | secondary-resource registry/commands + public `RegisterCombatUi` | combat-only; does not replace native Energy |
| Ordered buffer | semantic value, capacity, compile/output | `AttachedState<PlayerCombatState,TState>` + native result piles | no retained Card instances or custom zone |
| Scry | top-X amount and discard-any selection | generated-Mod-local `OpenModScry` + native selector/pile/history/hooks | singleplayer only; no global modifier/completion hooks |
| Asset | consumer profile and fallback | per-surface asset profile | retain current placeholder and unsupported consumers |
| Patch seam | exact target, version/fingerprint, risk, failure | `CreatePatcher` only when public APIs are insufficient | no arbitrary patches, C/D targets, or `OpenMod.Runtime` |
| Diagnostics | framework profile and proof route | shared marker fields from semantic contract | marker is not state proof |

## Unsupported/deferred seams

The presence of a RitsuLib API does not promote a capability. Keep these boundaries as
explicit gaps: vanilla editing, alternative Energy, retained-card custom zones,
arbitrary Event layouts/VFX, Ancient custom layouts, animation, materials, multiplayer
presentation, audio, run-persistent Character resources, direct merchant/rest/treasure
transitions, and unproven save or
multiplayer claims. The promoted Scry helper remains singleplayer-only and generated-Mod
local; it does not broaden those multiplayer or interoperability boundaries.

## Adapter record

For each generated mod, record this small implementation-only block in `MEMORY.md`:

```markdown
- framework profile: ritsulib-0.4.62-sts2-0.107.1
- adapter: <surface>/<contract-version>
- registration route: <shared/act/standalone/host-owned>
- asset profile: <profile or fallback>
- diagnostic status: <selected/resolved/fallback/failed>
- proof route: <suite and invariant>
- residual risk: <one short sentence>
```
