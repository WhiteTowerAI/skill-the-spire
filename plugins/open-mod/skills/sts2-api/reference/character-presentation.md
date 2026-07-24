# Character static and native presentation

Status: **pipeline-supported for eight static profiles on STS2 `0.107.1` /
RitsuLib `0.4.62`** by the 2026-07-23 Wayfinder headed proof. Selection
portrait/background, top-panel icon, non-Spine combat/rest/merchant bodies, five-layer
energy, and the compact card-energy icon are live-proven. Locked selection, map marker,
and native Ancient/Architect presentation remain unverified.

Use this page with `recipes/character.md` and `reference/art-contract.md`. Treat every
consumer independently: a valid path or successful PCK build is not render evidence.

## Profile and consumer matrix

| profile | RitsuLib surface | real consumer | status |
|---|---|---|---|
| selection portrait, 132x195 | `AssetProfile.Ui.CharacterSelectIconPath` | `NCharacterSelectButton.%Icon` and selected panel | visible and screenshot-proven |
| locked portrait, 132x195 | `AssetProfile.Ui.CharacterSelectLockedIconPath` | locked select view | grounded only |
| top-panel icon, 88x88 | both `Ui.IconTexturePath` and `Ui.IconPath` | `NRun.GlobalUi.TopBar.Portrait` | visible and screenshot-proven |
| map marker, 49x64 | `Ui.MapMarkerPath` | run map marker | grounded only |
| select background, 1920x1200 | `Ui.CharacterSelectBgPath` | character-select background | visible raw-scene consumer |
| combat body, 512x512 | `Scenes.VisualsPath` | player `NCreature.Visuals` | visible static non-Spine body |
| rest body, 512x512 | `Scenes.RestSiteAnimPath` | `NRestSiteCharacter` | visible raw-scene consumer |
| merchant body, 512x512 | `Scenes.MerchantAnimPath` | `NMerchantCharacter` | visible raw-scene consumer |
| full energy, five 256x256 layers | `Scenes.EnergyCounterPath` | one native `NEnergyCounter` | all five layers visible |
| compact energy, 24x24 | pool `BigEnergyIconPath` and `TextEnergyIconPath` | real hand `NCard.EnergyIcon` | visible checked texture |

## Asset profile

The promoted static profile is one declarative object:

```csharp
public override CharacterAssetProfile AssetProfile => new()
{
    Scenes = new()
    {
        VisualsPath = CharacterUi("combat.png"),
        EnergyCounterPath = CharacterScene("energy.tscn"),
        MerchantAnimPath = CharacterScene("merchant.tscn"),
        RestSiteAnimPath = CharacterScene("rest.tscn"),
    },
    Ui = new()
    {
        IconTexturePath = CharacterUi("icon.png"),
        IconPath = CharacterUi("icon.png"),
        CharacterSelectBgPath = CharacterScene("background.tscn"),
        CharacterSelectIconPath = CharacterUi("select.png"),
        CharacterSelectLockedIconPath = CharacterUi("select_locked.png"),
        MapMarkerPath = CharacterUi("map_marker.png"),
    },
};
```

Set both icon fields. `IconTexturePath` feeds the top panel; the plain PNG in
`IconPath` is accepted by RitsuLib's runtime factory for the Character icon control.
For the combat body, pass the checked PNG directly in `VisualsPath`; RitsuLib creates the
required `NCreatureVisuals`. The hosted node must report the exact 512x512 texture and
`HasSpineAnimation == false`.

Missing/unused rows resolve against the template's placeholder/native profile. Do not
invent a second getter path or patch. In particular, the RitsuLib Shop route does not need
the historical `NMerchantCharacter._Ready()` prefix.

## Raw scene contract

`build.py` packs raw Godot format-3 `.tscn` files through `pack_pck.py`; generated authors
need no Godot/MegaDot install. Keep wrappers minimal.

Selection background:

```ini
[gd_scene load_steps=2 format=3]
[ext_resource type="Texture2D" path="res://<ModName>/images/charui/background.png" id="1"]
[node name="CharacterSelectBackground" type="TextureRect"]
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
grow_horizontal = 2
grow_vertical = 2
mouse_filter = 2
texture = ExtResource("1")
expand_mode = 1
stretch_mode = 6
```

Rest and merchant are each one `Sprite2D` with the matching 512x512 texture:

```ini
[gd_scene load_steps=2 format=3]
[ext_resource type="Texture2D" path="res://<ModName>/images/charui/rest.png" id="1"]
[node name="CharacterRest" type="Sprite2D"]
texture = ExtResource("1")
```

The energy scene is a 128x128 `Control` with these exact native names:

```text
EnergyVfxBack (Node2D, unique)
Layers (Control, unique)
  Layer1..Layer3 (TextureRect)
RotationLayers (Control, unique)
  Layer4..Layer5 (TextureRect)
EnergyVfxFront (Node2D, unique)
Label (Label, centered)
StarAnchor (Node2D, unique)
```

Each layer fills its parent and references one distinct 256x256
`character_energy` output. A successful scene load alone is insufficient: the headed
proof must find one native counter and all five visible exact paths.

The compact icon stays separate from full energy. The card pool checks its 24x24 texture
before returning `BigEnergyIconPath` and `TextEnergyIconPath`; prove it in a real hand card.
The static proof is independent from the public resource/control proof; read
`character-resource.md` for its fixed control, offset, fallback, and non-overlap contract.

## Ancient boundary

`NAncientNameBanner`, Architect dialogue/speech color, and
`CharacterModel.GetArchitectAttackVfx()` are source-grounded. The Character still supplies
the abstract attack-VFX list and four Architect localization keys, but no headed custom-
Character Ancient run occurred. Do not claim native Ancient presentation or a custom
Ancient layout. The Foundation harness may initialize act 0 through the public test API
when its starter Ancient intentionally produces no map; that bypass is not an Ancient
consumer proof.

## Acceptance contract

For every selected visual:

1. normalize the exact profile through `gen_sprite.py import` and retain its checked
   fallback;
2. rebuild the PCK and enter the real consumer;
3. assert exact resource path, dimensions, native consumer type, and visibility;
4. capture a settled headed screenshot that visibly distinguishes it from fallback;
5. emit the final Foundation/static marker only after selection, combat, RestSite, and Shop
   all pass; then require `selftest done` and no fresh error.

The 2026-07-23 proof captured selection, combat, RestSite, and Shop. Structured state
proved exactly one selected Wayfinder, HP `72/72`, exact pools and starters, one native
energy counter/five layers, visible 24x24 card icon, `NRestSiteCharacter`, and
`NMerchantCharacter`, then emitted
`character foundation/static-presentation ... observed=all`. Strict RitsuLib-only Tier 2
passed with no fresh error.

## Unsupported extensions

- locked selection and map-marker presentation until their real hosts are visibly proved;
- custom Character Spine animation, combat states, trails, and animated transitions;
- custom materials/shaders and their lifecycle;
- remote-player hands, identity, ownership, rebuild, and Character UI;
- custom audio registration, mix, fallback, and cleanup;
- arbitrary top-bar or retained-card-zone UI;
- native custom-Character Ancient presentation and custom Ancient layouts.

Animation, materials, multiplayer presentation, and audio remain separate later tracks.
None is implied by these static profiles.
