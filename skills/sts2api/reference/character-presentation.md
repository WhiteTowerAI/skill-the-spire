# Character static, combat-cue, and native presentation

Status: **implemented for nine static profiles, deterministic top-icon/generated-
Relic outlines, the bounded card/UI theme, private non-Spine Idle/Attack/Hit/Dead cues, and
Character dialogue in native Ancient/Architect scenes on STS2 `0.107.1`**.

Locked selection and map marker remain unverified consumers.

Use this page with `recipes/character.md` and `reference/art-contract.md`; also read
`reference/character-combat-cues.md` when cues are selected. Treat every consumer
independently: a valid path or successful PCK build is not render evidence.

## Profile and consumer matrix

The sizes in this matrix are a readable view of the code-owned art contract, projected into
`reference/catalogs/art-contract-sts2-0.107.1.json`. That catalog also carries each slot's
output path, alpha policy, required/optional status, fallback, and generation-call budget.
The status column below is this page's own: it records how strongly each consumer has been
observed, which is not something the contract holds.

| profile | RitsuLib surface | real consumer | status |
|---|---|---|---|
| selection portrait, 132x195 | `AssetProfile.Ui.CharacterSelectIconPath` | `NCharacterSelectButton.%Icon` and selected panel | visible and screenshot-proven |
| locked portrait, 132x195 | `AssetProfile.Ui.CharacterSelectLockedIconPath` | locked select view | grounded only |
| top-panel main + outline, 88x88 each | `Ui.IconTexturePath`, `Ui.IconOutlineTexturePath`, and raw-scene `Ui.IconPath` | `NRun.GlobalUi.TopBar.Portrait` | main and derived outline visible and headed-review-proven |
| map marker, 49x64 | `Ui.MapMarkerPath` | run map marker | grounded only |
| select background, 1920x1200 | `Ui.CharacterSelectBgPath` | character-select background | visible raw-scene consumer |
| combat body, 512x512 | existence-checked resource factory | player `NCreature.Visuals` | visible static non-Spine body with reviewed public style |
| Idle/Attack/Hit/Dead cue bundle, 18x 512x512 | private set passed by `SetupCustomCombatAnimationStateMachine` | player `NCreature.Visuals` in combat only | full route and all-or-nothing fallback headed-review-proven |
| rest body, 512x512 | `Scenes.RestSiteAnimPath` | `NRestSiteCharacter` | visible raw-scene consumer |
| merchant body, 512x512 | `Scenes.MerchantAnimPath` | `NMerchantCharacter` | visible raw-scene consumer |
| full energy, five 256x256 layers | `Scenes.EnergyCounterPath` | one native `NEnergyCounter` | all five layers visible |
| large energy, 256x256 | pool `BigEnergyIconPath` | `EnergyIconHelper.GetPath` -> real hand `NCard.%EnergyIcon` | visible and headed-review-proven |
| text energy, 24x24 | pool `TextEnergyIconPath` | `EnergyIconsFormatter` rich-text image | visible and headed-review-proven |

## Asset profile

The promoted static profile is one declarative object:

```csharp
public override string? PlaceholderCharacterId => "ironclad";

public override CharacterAssetProfile AssetProfile => new()
{
    Scenes = new()
    {
        EnergyCounterPath = CharacterScene("energy.tscn"),
        MerchantAnimPath = CharacterScene("merchant.tscn"),
        RestSiteAnimPath = CharacterScene("rest.tscn"),
    },
    Ui = new()
    {
        IconTexturePath = CharacterUi("icon.png"),
        IconOutlineTexturePath = CharacterUi("icon_outline.png"),
        IconPath = CharacterScene("icon.tscn"),
        CharacterSelectBgPath = CharacterScene("background.tscn"),
        CharacterSelectIconPath = CharacterUi("select.png"),
        CharacterSelectLockedIconPath = CharacterUi("select_locked.png"),
        MapMarkerPath = CharacterUi("map_marker.png"),
    },
};
```

Set all three icon fields. The raw `IconPath` scene is the supported top-panel Control and
layers the two exact textures. `IconTexturePath` and `IconOutlineTexturePath` also expose
the correct `CharacterModel` texture properties; RitsuLib validates each resource and
retains its checked fallback when absent. Do not leave `IconPath` on the main PNG for the
outline route: RitsuLib's texture-to-Control fallback creates only one TextureRect.
Leave `Scenes.VisualsPath` unset so the resolved Character profile retains its checked
fallback scene. Wire the optional combat PNG through an existence-checked factory with the
reviewed public style:

```csharp
private static string CombatVisualPath => CharacterUi("combat.png");

protected override NCreatureVisuals? TryCreateCreatureVisuals()
{
    if (!ResourceLoader.Exists(CombatVisualPath))
        return null;

    Texture2D texture = ResourceLoader.Load<Texture2D>(CombatVisualPath);
    VisualNodeStyle style = VisualNodeStyle.Empty
        .WithScale(0.80f)
        .WithPosition(new Vector2(0f, -184f));
    return RitsuGodotNodeFactories.CreateFromResource<NCreatureVisuals>(texture, style);
}
```

Use the corresponding `Godot`, `NCreatureVisuals`, RitsuLib Godot-factory, Character visual
definition, and `VisualNodeStyle` namespaces. Returning `null` is the missing-file route:
RitsuLib resumes the resolved profile fallback. A present hosted node must report the exact
512x512 texture and `HasSpineAnimation == false`.

The normalized combat alpha is contained by `(26,26)-(486,486)` with exclusive bottom
baseline `486`; empty alpha, any canvas-edge contact, bounds outside that box, and a wrong
baseline are contract failures. Headed review checks that the combat body stays inside the
`1920x1080` viewport, clear of top/bottom UI, the enemy lane, and the turn banner. Selection
retains 132x195 pixels while fitting the entire opaque source composition inside
`(6,8)-(126,187)`; headed review checks that the real button stays inside the viewport with
no extra zoom, UI occlusion, or host clipping.

Missing/unused rows resolve against the explicitly selected base-game Ironclad profile. For
Energy this means `ironclad_energy_counter.tscn`; it must not be derived from the Character
theme or an `EnergyColorName` such as `red`. Do not invent a second getter path or patch. In
particular, the RitsuLib Shop route does not need an
`NMerchantCharacter._Ready()` prefix.

## Combat cue composition

The optional cue layer reuses the combat body's public scale/position but owns a fixed
Bounds/Intent/Center/Orb/Talk geometry. It accepts only the four sequences and timings in
`reference/character-combat-cues.md`. Require all eighteen resources before constructing
the set; otherwise keep the static body and mount no cue playback node.

The set is deliberately private to `SetupCustomCombatAnimationStateMachine`, which passes
it directly to `ModAnimStateMachines.StandardCue`. Leave
`CharacterAssetProfile.VisualCues` unset. That profile-level value is also consulted by
RitsuLib for merchant/rest playback and can incorrectly replace those static textures with
combat frames. Cast, Spine, trails, audio, and animated world-host bodies stay unsupported.

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

Top-panel icon (outline first so the main icon draws over its filled interior):

```ini
[gd_scene load_steps=3 format=3]
[ext_resource type="Texture2D" path="res://<ModName>/images/charui/icon_outline.png" id="1"]
[ext_resource type="Texture2D" path="res://<ModName>/images/charui/icon.png" id="2"]
[node name="CharacterIcon" type="Control"]
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
grow_horizontal = 2
grow_vertical = 2
mouse_filter = 2
[node name="Outline" type="TextureRect" parent="."]
layout_mode = 1
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
grow_horizontal = 2
grow_vertical = 2
mouse_filter = 2
texture = ExtResource("1")
expand_mode = 1
stretch_mode = 5
[node name="Icon" type="TextureRect" parent="."]
layout_mode = 1
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
grow_horizontal = 2
grow_vertical = 2
mouse_filter = 2
texture = ExtResource("2")
expand_mode = 1
stretch_mode = 5
```

`gen_sprite.py` creates `icon_outline.png` from final main alpha using the shared
opaque-white 3% max-filter rule (3 pixels at 88x88). Main normalization reserves the same
3-pixel inset so the derived outline is not clipped; it does not acquire another image.

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

The pool icons stay separate from full energy and from one another. The card pool checks
`energy_large.png` before returning `BigEnergyIconPath` and independently checks
`energy_text.png` before returning `TextEnergyIconPath`. The large route must resolve the
256x256 texture in a real hand card's `%EnergyIcon`. The text route must resolve the 24x24
path in a real card description using `EnergyIconsFormatter`; seeing the large icon does
not prove the rich-text consumer. When either custom file is absent, map the stable custom
pool prefix to the corresponding original Ironclad resource: `EnergyIconHelper.GetPath("ironclad")`
(`energy_ironclad.tres`) or
`res://images/packed/sprite_fonts/ironclad_energy_icon.png`. Never synthesize the fallback
from a palette label such as `red`.
The static proof is independent from the public resource/control proof; read
`character-resource.md` for its fixed control, offset, fallback, and non-overlap contract.

## Card/UI theme

One Character-local theme contract owns `NameColor`, `EnergyLabelOutlineColor`,
`DeckEntryCardColor`, `EnergyOutlineColor`, frame target RGB/brightness, both Energy-icon
paths, and the semantic palette/motif used to acquire the two icons. The card pool returns
one cached `MaterialUtils.CreateReplaceHueShaderMaterial(...)` instance through its public
`PoolFrameMaterial` property; this recolors the vanilla card-frame texture without a
generated frame image, custom shader, or `.tres` file.

The focused verification contract asserts the four exact `Color` values, the material's
`target_color` and `brightness` shader parameters, distinct existing icon paths, exact
256x256/24x24 resources, a visible large-icon TextureRect under a real `NCard`, and the
small path embedded in a real formatted card description. Headed review then checks that
the named color consumers, frame, large icon, and inline icon are legible and visually
coherent rather than merely present.

## Ancient boundary

`NAncientNameBanner`, Character/Ancient speech styling, native option restoration,
Architect dialogue/speech color, and `CharacterModel.GetArchitectAttackVfx()` are real-host
proved for the dedicated localization route in `reference/ancient-dialogue.md`. The focused
Wayfarer run covered one ordinary Ancient and the production Architect transition. This
supports a generated Character's dialogue in those native scenes; it does not support a
custom Ancient model, background, layout, options/rewards, or global dialogue replacement.

## Acceptance contract

For every selected visual:

1. normalize the exact profile through `gen_sprite.py import` and retain its checked
   fallback;
2. rebuild the PCK and enter the real consumer;
3. assert exact resource path, dimensions, native consumer type, and visibility;
4. for the top icon, assert both 88x88 paths, the `CharacterModel` main/outline texture
   properties, and both visible TextureRects under the same real `NTopBarPortrait`;
5. for every generated Relic, assert its exact 256x256 main/outline pair under one real
   `NRelic`, plus its explicit `RelicAssetProfile` big path;
6. for selection/combat, also assert the normalized content box/baseline, public combat
   transform, resulting screen bounds, and named UI exclusion regions;
7. when cues are selected, assert all four routes, one-shot returns/terminal pose, stable
   geometry, cleanup, and the separate one-missing-frame static fallback;
8. capture settled headed screenshots that visibly distinguish custom presentation from fallback;
9. emit the final Foundation/static marker only after selection, combat, RestSite, and Shop
   all pass; then require `selftest done` and no fresh error.

The focused proof captured selection, combat, RestSite, and Shop. Structured state must
derive the selected Character identity, HP, pools, and starters from the current `SPEC.md`,
then assert one native energy counter/five layers, the visible 24x24 card icon,
`NRestSiteCharacter`, and `NMerchantCharacter` before emitting
`character foundation/static-presentation ... observed=all`. Strict RitsuLib-only Tier 2
passed with no fresh error.

## Unsupported extensions

- locked selection and map-marker presentation until their real hosts are visibly proved;
- Character combat cues beyond Idle/Attack/Hit/Dead, including Cast;
- custom Character Spine animation, trails, and animated transitions;
- arbitrary custom materials/shaders and their lifecycle beyond the bounded pool-frame helper;
- remote-player hands, identity, ownership, rebuild, and Character UI;
- custom audio registration, mix, fallback, and cleanup;
- arbitrary top-bar or retained-card-zone UI;
- custom Ancient models, backgrounds, layouts, options/rewards, global dialogue
  replacement, line audio, arbitrary VFX, and multiplayer presentation.

Production animation, materials, multiplayer presentation, and audio remain separate later
tracks. None is implied by the bounded frame-sequence support.
