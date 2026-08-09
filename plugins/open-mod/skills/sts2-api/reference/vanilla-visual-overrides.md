# Public visual overrides for existing vanilla models

Use this reference after `vanilla-overrides.md` resolves an exact target whose request is
visual. These routes are pinned to STS2 `0.107.1` and RitsuLib `0.5.4` and cover all 44 public
providers in `ExternalCardMaterialOverrideRegistry` and `ExternalAssetOverrideRegistry`;
the number of headed examples does not narrow this Package.

## Contents

- [Promoted provider matrix](#promoted-provider-matrix)
- [Manifest resources](#manifest-resources)
- [Resource authoring](#resource-authoring)
- [Registration and fallback](#registration-and-fallback)
- [Conflicts and cleanup](#conflicts-and-cleanup)
- [Boundaries and checks](#boundaries-and-checks)

## Promoted provider matrix

Every row is one public route. `path` providers return a checked `res://` string;
`texture`, `material`, and `scene` providers load the typed Godot resource. The target is
always the exact catalog type, not a second registered model.

| Target | Route id | Surface | Public registration method | Resource kind |
|---|---|---|---|---|
| Card | `visual.card.frame-material` | `card.frame_material` | `ExternalCardMaterialOverrideRegistry.RegisterFrameProvider` | `material` |
| Card | `visual.card.portrait-material` | `card.portrait_material` | `ExternalCardMaterialOverrideRegistry.RegisterPortraitProvider` | `material` |
| Card | `visual.card.banner-material` | `card.banner_material` | `ExternalCardMaterialOverrideRegistry.RegisterBannerProvider` | `material` |
| CardPool | `visual.card-pool.frame-material` | `card_pool.frame_material` | `ExternalCardMaterialOverrideRegistry.RegisterPoolFrameProvider` | `material` |
| Relic | `visual.relic.icon-path` | `relic.icon` | `ExternalAssetOverrideRegistry.RegisterRelicIconPathProvider` | `texture` |
| Relic | `visual.relic.icon-outline-path` | `relic.icon_outline` | `ExternalAssetOverrideRegistry.RegisterRelicIconOutlinePathProvider` | `texture` |
| Relic | `visual.relic.icon-texture` | `relic.icon` | `ExternalAssetOverrideRegistry.RegisterRelicIconTextureProvider` | `texture` |
| Relic | `visual.relic.icon-outline-texture` | `relic.icon_outline` | `ExternalAssetOverrideRegistry.RegisterRelicIconOutlineTextureProvider` | `texture` |
| Relic | `visual.relic.big-icon-texture` | `relic.big_icon` | `ExternalAssetOverrideRegistry.RegisterRelicBigIconTextureProvider` | `texture` |
| Power | `visual.power.icon-path` | `power.icon` | `ExternalAssetOverrideRegistry.RegisterPowerIconPathProvider` | `texture` |
| Power | `visual.power.icon-texture` | `power.icon` | `ExternalAssetOverrideRegistry.RegisterPowerIconTextureProvider` | `texture` |
| Power | `visual.power.big-icon-texture` | `power.big_icon` | `ExternalAssetOverrideRegistry.RegisterPowerBigIconTextureProvider` | `texture` |
| Potion | `visual.potion.image-path` | `potion.image` | `ExternalAssetOverrideRegistry.RegisterPotionImagePathProvider` | `texture` |
| Potion | `visual.potion.outline-path` | `potion.outline` | `ExternalAssetOverrideRegistry.RegisterPotionOutlinePathProvider` | `texture` |
| Potion | `visual.potion.image-texture` | `potion.image` | `ExternalAssetOverrideRegistry.RegisterPotionImageTextureProvider` | `texture` |
| Potion | `visual.potion.outline-texture` | `potion.outline` | `ExternalAssetOverrideRegistry.RegisterPotionOutlineTextureProvider` | `texture` |
| Orb | `visual.orb.icon-path` | `orb.icon` | `ExternalAssetOverrideRegistry.RegisterOrbIconPathProvider` | `texture` |
| Orb | `visual.orb.icon-texture` | `orb.icon` | `ExternalAssetOverrideRegistry.RegisterOrbIconTextureProvider` | `compressed_texture` |
| Orb | `visual.orb.visuals-scene-path` | `orb.visuals_scene` | `ExternalAssetOverrideRegistry.RegisterOrbVisualsScenePathProvider` | `packed_scene` |
| Act | `visual.act.background-scene-path` | `act.background_scene` | `ExternalAssetOverrideRegistry.RegisterActBackgroundScenePathProvider` | `packed_scene` |
| Act | `visual.act.rest-site-background-path` | `act.rest_site_background` | `ExternalAssetOverrideRegistry.RegisterActRestSiteBackgroundPathProvider` | `packed_scene` |
| Act | `visual.act.map-top-background-path` | `act.map_top_background` | `ExternalAssetOverrideRegistry.RegisterActMapTopBgPathProvider` | `texture` |
| Act | `visual.act.map-mid-background-path` | `act.map_mid_background` | `ExternalAssetOverrideRegistry.RegisterActMapMidBgPathProvider` | `texture` |
| Act | `visual.act.map-bot-background-path` | `act.map_bot_background` | `ExternalAssetOverrideRegistry.RegisterActMapBotBgPathProvider` | `texture` |
| Event | `visual.event.background-scene-path` | `event.background_scene` | `ExternalAssetOverrideRegistry.RegisterEventBackgroundScenePathProvider` | `packed_scene` |
| Event | `visual.event.layout-scene-path` | `event.layout_scene` | `ExternalAssetOverrideRegistry.RegisterEventLayoutScenePathProvider` | `packed_scene` |
| Event | `visual.event.initial-portrait-texture` | `event.initial_portrait` | `ExternalAssetOverrideRegistry.RegisterEventInitialPortraitTextureProvider` | `texture` |
| Event | `visual.event.background-scene` | `event.background_scene` | `ExternalAssetOverrideRegistry.RegisterEventBackgroundSceneProvider` | `packed_scene` |
| Event | `visual.event.vfx-scene` | `event.vfx_scene` | `ExternalAssetOverrideRegistry.RegisterEventVfxSceneProvider` | `packed_scene` |
| Encounter | `visual.encounter.scene-path` | `encounter.scene` | `ExternalAssetOverrideRegistry.RegisterEncounterScenePathProvider` | `packed_scene` |
| Encounter | `visual.encounter.background-scene-path` | `encounter.background_scene` | `ExternalAssetOverrideRegistry.RegisterEncounterBackgroundScenePathProvider` | `packed_scene` |
| Encounter | `visual.encounter.background-layers-directory` | `encounter.background_layers` | `ExternalAssetOverrideRegistry.RegisterEncounterBackgroundLayersDirectoryProvider` | `directory` |
| Encounter | `visual.encounter.boss-node-path` | `encounter.boss_node` | `ExternalAssetOverrideRegistry.RegisterEncounterBossNodePathProvider` | `spine_resource` |
| Encounter | `visual.encounter.map-node-asset-paths` | `encounter.map_node_assets` | `ExternalAssetOverrideRegistry.RegisterEncounterMapNodeAssetPathsProvider` | `resource[]` |
| Encounter | `visual.encounter.run-history-icon-path` | `encounter.run_history_icon` | `ExternalAssetOverrideRegistry.RegisterEncounterRunHistoryIconPathProvider` | `texture` |
| Encounter | `visual.encounter.run-history-icon-outline-path` | `encounter.run_history_icon_outline` | `ExternalAssetOverrideRegistry.RegisterEncounterRunHistoryIconOutlinePathProvider` | `texture` |
| Ancient Event | `visual.ancient.map-icon-path` | `ancient.map_icon` | `ExternalAssetOverrideRegistry.RegisterAncientMapIconPathProvider` | `texture` |
| Ancient Event | `visual.ancient.map-icon-outline-path` | `ancient.map_icon_outline` | `ExternalAssetOverrideRegistry.RegisterAncientMapIconOutlinePathProvider` | `texture` |
| Ancient Event | `visual.ancient.run-history-icon-path` | `ancient.run_history_icon` | `ExternalAssetOverrideRegistry.RegisterAncientRunHistoryIconPathProvider` | `texture` |
| Ancient Event | `visual.ancient.run-history-icon-outline-path` | `ancient.run_history_icon_outline` | `ExternalAssetOverrideRegistry.RegisterAncientRunHistoryIconOutlinePathProvider` | `texture` |
| Affliction | `visual.affliction.overlay-path` | `affliction.overlay` | `ExternalAssetOverrideRegistry.RegisterAfflictionOverlayPathProvider` | `packed_scene` |
| Affliction | `visual.affliction.overlay-scene` | `affliction.overlay` | `ExternalAssetOverrideRegistry.RegisterAfflictionOverlaySceneProvider` | `packed_scene` |
| Enchantment | `visual.enchantment.icon-path` | `enchantment.icon` | `ExternalAssetOverrideRegistry.RegisterEnchantmentIconPathProvider` | `texture` |
| Modifier | `visual.modifier.icon-path` | `modifier.icon` | `ExternalAssetOverrideRegistry.RegisterModifierIconPathProvider` | `texture` |

Ordinary Event routes accept every exact `EVENT.*` model, including Ancient subtypes.
Ancient-only icon routes additionally require catalog `content_kind: ancient`. There is no
public external override registry for a vanilla Monster body's visuals in this profile; do
not invent a Monster route from `MonsterAssetProfile`, which belongs to new Mod models.

## Manifest resources

The checked catalog promotes `m6.7.2-public-visual-overrides`. Every operation uses mode
`visual`, the matrix surface, exact category/type/content-kind baseline, and one Mod-owned
resource. For example:

```json
{
  "order": 0,
  "operation_id": "lost-wisp.icon",
  "target_model_id": "RELIC.LOST_WISP",
  "mode": "visual",
  "surface": "relic.icon",
  "route": {
    "class": "public",
    "id": "visual.relic.icon-texture",
    "fingerprint": null
  },
  "expected_baseline": {
    "category": "RELIC",
    "type": "MegaCrit.Sts2.Core.Models.Relics.LostWisp",
    "content_kind": "relic"
  },
  "semantics": {
    "resource": {
      "kind": "texture",
      "path": "res://ExampleMod/images/vanilla/relics/lost_wisp.png",
      "required": true
    }
  }
}
```

`material`, `texture`, `compressed_texture`, `packed_scene`, `spine_resource`, and
`directory` routes use the same single `resource` object. The map-node list route instead
uses a nonempty `resources` array of `{kind: resource, path, required}` objects. Paths must
use forward slashes, remain under exact `res://<ModId>/`, contain no dot/traversal segment,
and select a data/resource extension rather than code or script.

`required: true` makes a missing project file fail before MSBuild. `required: false` means
the generated provider may omit that path at runtime and preserve the vanilla resource.
It does not mean an unchecked missing resource is a pass. A selected background-layer
directory must exist when present, contain at least one direct `.tscn` layer, and contain no
script/executable resource. A resource list omits missing optional entries and returns
`null` when none remain.

## Resource authoring

For a raster role already owned by `art-contract.md`, acquire or import one image and run
the matching deterministic `gen_sprite.py import` normalization. Reuse its exact output
dimensions and outline behavior for Relic, Power, Potion, Orb, Enchantment, and other
matching icon roles. A visual override may use runtime image generation only through the
normal art-source selection and approval rules; the provider route itself never calls an
image model.

Do not pretend a PNG is a Card material, PackedScene, Spine resource, or scene directory.
Those inputs must be already-authored local Godot resources with their referenced assets
packaged under the same Mod namespace. Material resources are `.tres`/`.res`; PackedScene
resources are `.tscn`/`.scn`/`.res`; texture routes accept Godot-supported image or texture
resources. Keep visual scenes declarative and presentation-only. Do not attach generated
GDScript/C# behavior, load remote files, or use a scene as a hidden gameplay patch.

The operation changes only the named surface. It does not infer matching outlines, big
icons, map layers, VFX, or other variants. Add each requested surface as its own ordered
operation and resource. Preserve every omitted vanilla surface.

## Registration and fallback

Register providers once from the Mod's normal initialization path. Use one stable,
globally specific Mod key, consolidate all targets for the same provider surface into one
provider, and return `null` for every non-target type. Match the catalog's exact concrete
type; never register another vanilla model.

```csharp
using Godot;
using MegaCrit.Sts2.Core.Models.Relics;
using STS2RitsuLib.Scaffolding.Content.Patches;

private const string VisualProviderKey = $"{ModId}:m672-visual-overrides";
private const string LostWispIcon =
    "res://ExampleMod/images/vanilla/relics/lost_wisp.png";

private static T? LoadResource<T>(string path) where T : Resource =>
    ResourceLoader.Exists(path) ? ResourceLoader.Load<T>(path) : null;

private static void RegisterVisualOverrides()
{
    ExternalAssetOverrideRegistry.RegisterRelicIconTextureProvider(
        VisualProviderKey,
        model => model.GetType() == typeof(LostWisp)
            ? LoadResource<Texture2D>(LostWispIcon)
            : null);
}
```

For string providers, return the path only when `ResourceLoader.Exists(path)` is true. For
`Material`, `Texture2D`, `CompressedTexture2D`, or `PackedScene` providers, load the exact
typed resource after that check. For a directory, require `DirAccess.Open(path)` to succeed.
For a path list, filter each entry through `ResourceLoader.Exists`. Even a build-required
resource retains this runtime check so a broken import or deployment falls back instead of
replacing vanilla presentation with `null`.

## Conflicts and cleanup

Only one operation may own one exact target/surface in a generated Mod. Path and loaded-
resource alternatives are the same surface and conflict: Relic icon path vs texture, Event
background path vs scene, and Affliction overlay path vs scene cannot both be emitted.

RitsuLib provider registries are process-wide. Another Mod's provider order and semantic
overlap are not visible to the manifest, so open-mod cannot claim cross-Mod conflict
diagnosis. A globally specific key prevents accidental same-key replacement, and exact-type
guards minimize overlap, but neither establishes priority with another Mod.

If the host supplies a reload/unload cleanup path, call
`ExternalAssetOverrideRegistry.Unregister(VisualProviderKey)`. For selected Card material
surfaces, call the corresponding `UnregisterFrameProvider`, `UnregisterPortraitProvider`,
`UnregisterBannerProvider`, or `UnregisterPoolFrameProvider` with the same key. Never call
either registry's `Clear()`, because that removes other Mods' providers.

## Boundaries and checks

A focused manifest/resource test and a representative compile establish the manifest and the
build, nothing more. A successful manifest, resource existence check, PCK pack, or compile is
not headed visual proof — only the real presentation host is.

Group routes by their nearest real consumer when verifying: Card hand/full view and CardPool;
Relic/Power/Potion/Orb combat UI and previews; Act map/rest/background; Event/Ancient;
Encounter room/map/history; and Affliction/Enchantment/Modifier consumers. Verify fallback
by removing one optional resource and confirm untouched surfaces remain vanilla. Keep
unvisited consumers and unrun multiplayer/cross-Mod cases as explicit exceptions.
