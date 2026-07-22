# RitsuLib adapter reference

This is the one lazy framework-specific reference for the migration target. Read it
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
fallback. Phase R2 implements this once in `scaffold.py`, `ritsu_profile.py`, and
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
```

The content-pack builder and registry are the shared registration boundary. A simple
surface must not initialize Character, Event, multiplayer, audio, materials, or other
unselected modules.

## Surface routing

| Semantic surface | RitsuLib public registration/template | Asset profile | Current migration status |
|---|---|---|---|
| Card | content-pack card registration; `ModCardTemplate` | `CardAssetProfile` | R3 complete; hosted Tier 2 proof |
| Relic | content-pack relic registration; `ModRelicTemplate` | `RelicAssetProfile` | R3 complete; hosted Tier 2 proof |
| Potion | content-pack potion registration; `ModPotionTemplate` | `PotionAssetProfile` | R3 complete; hosted Tier 2 proof |
| Power | content-pack power registration; `ModPowerTemplate` | `PowerAssetProfile` | R3 complete; hosted Tier 2 proof |
| Keyword | keyword registry/manifest entry | text-only tooltip fallback | R3 complete; hosted Tier 2 proof |
| Enchantment | enchantment registration; `ModEnchantmentTemplate` | `EnchantmentAssetProfile` | R3 complete; hosted Tier 2 proof |
| Orb | orb registration; `ModOrbTemplate` | `OrbAssetProfile` | R3 complete; hosted Tier 2 proof |
| Monster | monster registration; `ModMonsterTemplate` | `MonsterAssetProfile` | R1 mapped; R4 implementation/proof |
| Encounter | act/global encounter registration; `ModEncounterTemplate` | `EncounterAssetProfile` | R1 mapped; R4 implementation/proof |
| Event | shared/act event registration; `ModEventTemplate` | `EventAssetProfile` | R1 mapped; R4 implementation/proof |
| Character | character registration; `ModCharacterTemplate<...>` | `CharacterAssetProfile` | R1 mapped; R4 implementation/proof |

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
not replace that semantic hook. Put explicit Mod icon paths in `RelicAssetProfile` and
retain its empty-profile fallback.

### Potion, Power, Keyword, Enchantment, and Orb

These R3 surfaces use the same content-pack boundary; each is registered exactly once in
the selected scaffold's `RegisterContent()` hook and then resolved by its normalized public
entry. The surface recipe owns effect details, while this adapter owns the framework shape:

| Surface | Registration | Entry/profile contract | R3 proof invariant |
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

For both surfaces, the default public entry is `MOD_CATEGORY_TYPENAME`, with every segment
normalized to uppercase snake case by `ModContentRegistry`. Example: mod id
`RitsuCardProof`, `Jolt : CardModel` becomes `RITSU_CARD_PROOF_CARD_JOLT`; localization
uses that exact flat stem in `cards` or `relics`. Use `ModelPublicEntryOptions.FromStem`
only to preserve an already-published identity, never as a second naming system.

## Cross-cutting routes

| Semantic concern | Adapter input | RitsuLib route | Boundary |
|---|---|---|---|
| Run state | `state.lifetime=run`, owner, save fields | `RunSavedDataStore` | no new shared runtime; prove save round-trip |
| Lifecycle | semantic trigger and reset boundary | typed `SubscribeLifecycle<TEvent>` or the model's public hook | no guessed event type |
| Combat resource | nonnegative amount, payment, reset, UI fallback | secondary-resource registry/commands | does not replace native Energy |
| Asset | consumer profile and fallback | per-surface asset profile | retain current placeholder and unsupported consumers |
| Patch seam | exact target, version/fingerprint, risk, failure | `CreatePatcher` only when public APIs are insufficient | no arbitrary patches, C/D targets, or `OpenMod.Runtime` |
| Diagnostics | framework profile and proof route | shared marker fields from semantic contract | marker is not state proof |

## Unsupported/deferred seams

The presence of a RitsuLib API does not promote a capability. Keep these boundaries as
explicit gaps: vanilla editing, alternative Energy, retained-card custom zones,
arbitrary Event layouts/VFX, Ancient custom layouts, animation, materials, multiplayer
presentation, audio, direct merchant/rest/treasure transitions, and unproven save or
multiplayer claims. Scry remains a future open-mod-owned helper using native selection and
discard APIs, not a RitsuLib dependency.

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
