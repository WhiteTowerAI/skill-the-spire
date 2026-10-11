# Recipe: Custom Act

Use `ModActTemplate` for a complete chapter. Register the model and its singleplayer entry policy
in the Mod's one content pack. These are separate requirements: `.Act<T>()` alone creates an
unreachable model because the template defaults `AllowInRandomActList` to `false`.

## Registration and entry

Choose exactly one entry mode for the selected slot:

```csharp
ModContentPackBuilder.For(MainFile.ModId)
    .Act<<ActName>>()
    .ActEnterForce<<ActName>>(
        slotIndex: <0|1|2>,
        priority: <integer>,
        eligibility: static ctx => !ctx.IsMultiplayer && <plain condition>)
    .Apply();
```

Uniform selection includes the existing chapter automatically:

```csharp
.ActEnterUniformPool(<slot>)
.ActEnterUniformPoolCandidate<<ActName>>(
    <slot>, static ctx => !ctx.IsMultiplayer && <condition>)
```

Weighted selection also includes the existing chapter, at fixed weight 1; only candidate weights
are configurable. Express "the existing chapter is twice as likely" as candidate weight `0.5`.
Declare the pool first, then its candidates; non-finite or nonpositive weights are ignored:

```csharp
.ActEnterWeightedPool(<slot>)
.ActEnterWeightedPoolCandidate<<ActName>>(
    <slot>,
    static ctx => !ctx.IsMultiplayer && <condition>,
    static ctx => <positive double>)
```

A Mod declares one mode per slot; another Mod's uniform and weighted contributions to the same
slot coexist with it. To replace the slot with one of several Acts and never keep the existing
chapter, use a force rule over a weighted candidate set:

```csharp
.ActEnterForcePool(
    slotIndex: <slot>,
    priority: <integer>,
    eligibility: static ctx => !ctx.IsMultiplayer && <condition>,
    (typeof(<ActA>), <positive double>),
    (typeof(<ActB>), <positive double>))
```

Higher force priority wins; equal priority uses earlier registration. The resolver supplies
`ActEnterResolveContext` with `RunState`, `UnlockState`, `EnteringActIndex`, `IsMultiplayer`, and
the run's `Rng.Niche`. Uniform/weighted selection consumes that supplied RNG. Never roll with
`System.Random`, consume RNG in a preview/eligibility check, or set `AllowInRandomActList` true:
that last path has no singleplayer predicate and is deferred with Multiplayer interaction.

## Required model contract

The template wires assets but does not implement `ActModel` gameplay. Override every required
member:

- identity/selection: `Index` (`0..2`), `IsDefault => false`, and
  `IsUnlocked(UnlockState) => true` while new Progression integration is deferred;
- room shape: positive `BaseNumberOfRooms`, optional `NumberOfWeakEncounters`, and
  `GetMapPointTypes(Rng mapRng)` using only `mapRng`;
- content: `GenerateAllEncounters()`, `BossDiscoveryOrder`, `AllEvents`, `AllAncients`, and
  `GetUnlockedAncients(UnlockState)`;
- discovery: `ApplyActDiscoveryOrderModifications(UnlockState)`; keep it empty unless the SPEC
  explicitly defines a non-Progression ordering rule;
- map: `MapTraveledColor`, `MapUntraveledColor`, and `MapBgColor`;
- audio: `BgMusicOptions`, `MusicBankPaths`, `AmbientSfx`, and `ChestOpenSfx`; and
- chest: `ChestSpineSkinNameNormal` and `ChestSpineSkinNameStroke`, plus the profile's exact
  `ChestSpineResourcePath`.

`GenerateAllEncounters()` must leave the derived weak, regular, elite, and Boss groups nonempty.
List every canonical referenced model with `ModelDb.*<T>()`; RitsuLib's `.ActEncounter`,
`.ActEvent`, and `.ActAncient` registrations are appended dynamically, but the final runtime pools
still owe that invariant. A compile-successful Act with an empty group fails during room creation.

Register related nodes exactly once:

```csharp
.Monster<<Monster>>()
.ActEncounter<<ActName>, <Encounter>>()
.ActEvent<<ActName>, <Event>>()
.ActAncient<<ActName>, <Ancient>>()
```

Use `recipes/monster.md`, `recipes/event.md`, and `recipes/ancient.md` for those node contracts.

## Assets and localization

Ship identical-key `localization/eng/acts.json` and `localization/zhs/acts.json`:

```json
{
  "<MOD>_ACT_<ACT>.title": "<title>"
}
```

`ActAssetProfile` owns background scene, Rest Site scene, top/middle/bottom map textures, chest
Spine resource, and optional combat-background layer directory. Explicit Mod-local `res://` paths
are preferred. `ContentAssetProfiles.FromVanillaActId("hive")` derives paths from a vanilla
folder name, not a model ID; validate every derived resource. In particular, base-game chest
resources use numbered paths (`act_1`, `act_2`, `act_3`), so do not assume a folder-derived chest
path exists. Override that profile field with the exact selected vanilla or Mod-local resource and
use matching skin names and SFX.

Missing/invalid Act scenes, layers, map textures, chest Spine/skins, music banks, or events are
Build- or runtime-visible failures, not acceptable implicit fallbacks. Reusing an exact checked
vanilla profile is the placeholder route; custom presentation remains headed proof.

## SelfTest

Follow `surfaces/act.md`. Registration/model lookup, calling an entry predicate, or inspecting a
generated list cannot prove a playable Act. The real host must enter the selected slot, generate
the map and all required room families, traverse representative consumers, verify deterministic
selection and save/load identity, and keep the deferred Multiplayer route absent.
