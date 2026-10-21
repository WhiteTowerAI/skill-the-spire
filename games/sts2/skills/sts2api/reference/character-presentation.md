# Character static, combat-cue, and native presentation

This page covers nine static profiles, deterministic top-icon/generated-Relic outlines, the
bounded card/UI theme, private non-Spine Idle/Attack/Hit/Dead cues, and Character dialogue in
native Ancient/Architect scenes. The Character proof does not reach the locked selection
portrait or the map marker; report those two consumers as unverified.

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
| Idle/Attack/Hit/Dead cue bundle, 24x 512x512 | private set passed by `SetupCustomCombatAnimationStateMachine` | player `NCreature.Visuals` in combat only | full route and all-or-nothing fallback headed-review-proven |
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
    var visuals = RitsuGodotNodeFactories.CreateFromResource<NCreatureVisuals>(texture, style);
    FitBoundsToBody(visuals, texture);
    return visuals;
}

// The texture factory sizes Bounds to 1.1x the whole texture and ignores the style scale, so
// the health bar (Bounds width) would be far wider than the drawn body. Fit Bounds, intent,
// and center to the body's opaque pixels as the 0.80 / (0, -184) style draws them.
private static void FitBoundsToBody(NCreatureVisuals visuals, Texture2D texture)
{
    const float scale = 0.80f;
    const float offsetY = -184f;
    Rect2I used = texture.GetImage().GetUsedRect();
    float half = texture.GetWidth() / 2f;
    float left = (used.Position.X - half) * scale;
    float right = (used.End.X - half) * scale;
    float top = offsetY + (used.Position.Y - texture.GetHeight() / 2f) * scale;
    float bottom = offsetY + (used.End.Y - texture.GetHeight() / 2f) * scale;

    if (visuals.GetNodeOrNull<Control>("%Bounds") is { } bounds)
    {
        bounds.Position = new Vector2(left, top);
        bounds.Size = new Vector2(right - left, bottom - top);
    }
    if (visuals.GetNodeOrNull<Marker2D>("%IntentPos") is { } intent)
        intent.Position = new Vector2((left + right) / 2f, top - 70f);
    if (visuals.GetNodeOrNull<Marker2D>("%CenterPos") is { } center)
        center.Position = new Vector2((left + right) / 2f, top + (bottom - top) * 0.6f);
}
```

The health bar takes the `%Bounds` width. The proof asserts it equals the body's opaque width
times 0.80 (within 2 px), and headed review checks that the bar matches the body.

Use the corresponding `Godot`, `NCreatureVisuals`, RitsuLib Godot-factory, Character visual
definition, and `VisualNodeStyle` namespaces. Returning `null` is the missing-file route:
RitsuLib resumes the resolved profile fallback. A present hosted node must report the exact
512x512 texture and `HasSpineAnimation == false`.

The normalized combat alpha is contained by `(26,26)-(486,486)` with exclusive bottom
baseline `486`; empty alpha, any canvas-edge contact, bounds outside that box, and a wrong
baseline are contract failures. Headed review checks that the combat body stays inside the
`1920x1080` viewport, clear of top/bottom UI, the enemy lane, and the turn banner. Selection
fills all 132x195 pixels as a full-bleed close-up; headed review checks that it reads like the
vanilla buttons beside it, with no extra zoom, UI occlusion, or host clipping.

Missing/unused rows resolve against the explicitly selected base-game Ironclad profile. For
Energy this means `ironclad_energy_counter.tscn`; it must not be derived from the Character
theme or an `EnergyColorName` such as `red`. Do not invent a second getter path or patch. In
particular, the RitsuLib Shop route does not need an
`NMerchantCharacter._Ready()` prefix.

## Combat cue composition

The optional cue layer reuses the combat body's public scale/position but owns a fixed
Bounds/Intent/Center/Orb/Talk geometry. It accepts only the four sequences and timings in
`reference/character-combat-cues.md`. Require all twenty-four resources before constructing
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
anchors_preset = 8
anchor_left = 0.5
anchor_top = 0.5
anchor_right = 0.5
anchor_bottom = 0.5
offset_left = -960.0
offset_top = -540.0
offset_right = 960.0
offset_bottom = 540.0
grow_horizontal = 2
grow_vertical = 2
mouse_filter = 2
texture = ExtResource("1")
expand_mode = 1
stretch_mode = 6
```

Vanilla select backgrounds are anchored to the screen center rather than filling their
parent, whose size the scene does not control. Centering one 1920x1080 cover rect shows the
full 16:10 width and crops only a thin strip top and bottom.

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

Rest and merchant are each one `Sprite2D` with the matching 512x512 texture. The Rest Site
host is centered on the body, so the rest sprite stays centered:

```ini
[gd_scene load_steps=2 format=3]
[ext_resource type="Texture2D" path="res://<ModName>/images/charui/rest.png" id="1"]
[node name="CharacterRest" type="Sprite2D"]
texture = ExtResource("1")
```

The Shop host places its node at the feet, so the merchant sprite lifts its baseline (y 486
of the 512 canvas) onto the origin; a centered merchant sprite sinks half a body low:

```ini
[gd_scene load_steps=2 format=3]
[ext_resource type="Texture2D" path="res://<ModName>/images/charui/merchant.png" id="1"]
[node name="CharacterMerchant" type="Sprite2D"]
texture = ExtResource("1")
offset = Vector2(0, -230)
```

The energy scene follows the native counter's structure. RitsuLib converts it into a real
`NEnergyCounter` by these exact names, and the native counter spins every child of
`%RotationLayers` around that child's own `pivot_offset`:

- `%RotationLayers` sits **inside** `%Layers` and holds only Layer2 (swirl) and Layer3
  (core), each with `pivot_offset = Vector2(64, 64)`;
- Layer1 is drawn below it, and Layer4 (ring) and Layer5 (edge) stay fixed above it;
- every layer uses the base-game `energy_orb_dark` material, which dims the counter at zero
  Energy; `%EnergyVfxBack`/`%EnergyVfxFront` may stay empty (no particles).

A sibling `RotationLayers` holding Layer4/5, or a missing per-layer pivot, spins the fixed
ring around its top-left corner so it swings off the counter like a stray effect. Use this
template (`<ModName>` and the label outline from the theme contract):

```ini
[gd_scene load_steps=8 format=3]
[ext_resource type="Texture2D" path="res://<ModName>/images/charui/orb_layer_1.png" id="1"]
[ext_resource type="Texture2D" path="res://<ModName>/images/charui/orb_layer_2.png" id="2"]
[ext_resource type="Texture2D" path="res://<ModName>/images/charui/orb_layer_3.png" id="3"]
[ext_resource type="Texture2D" path="res://<ModName>/images/charui/orb_layer_4.png" id="4"]
[ext_resource type="Texture2D" path="res://<ModName>/images/charui/orb_layer_5.png" id="5"]
[ext_resource type="Material" path="res://materials/ui/energy_orb_dark.tres" id="dark"]
[ext_resource type="FontVariation" path="res://themes/kreon_bold_shared.tres" id="font"]
[node name="EnergyCounter" type="Control"]
layout_mode = 3
anchors_preset = 0
offset_right = 128.0
offset_bottom = 128.0
pivot_offset = Vector2(64, 64)
[node name="EnergyVfxBack" type="Node2D" parent="."]
unique_name_in_owner = true
position = Vector2(64, 64)
[node name="Layers" type="Control" parent="."]
unique_name_in_owner = true
layout_mode = 1
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
grow_horizontal = 2
grow_vertical = 2
mouse_filter = 2
[node name="Layer1" type="TextureRect" parent="Layers"]
material = ExtResource("dark")
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
[node name="RotationLayers" type="Control" parent="Layers"]
unique_name_in_owner = true
layout_mode = 1
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
grow_horizontal = 2
grow_vertical = 2
mouse_filter = 2
[node name="Layer2" type="TextureRect" parent="Layers/RotationLayers"]
material = ExtResource("dark")
layout_mode = 1
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
grow_horizontal = 2
grow_vertical = 2
pivot_offset = Vector2(64, 64)
mouse_filter = 2
texture = ExtResource("2")
expand_mode = 1
stretch_mode = 5
[node name="Layer3" type="TextureRect" parent="Layers/RotationLayers"]
material = ExtResource("dark")
layout_mode = 1
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
grow_horizontal = 2
grow_vertical = 2
pivot_offset = Vector2(64, 64)
mouse_filter = 2
texture = ExtResource("3")
expand_mode = 1
stretch_mode = 5
[node name="Layer4" type="TextureRect" parent="Layers"]
material = ExtResource("dark")
layout_mode = 1
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
grow_horizontal = 2
grow_vertical = 2
mouse_filter = 2
texture = ExtResource("4")
expand_mode = 1
stretch_mode = 5
[node name="Layer5" type="TextureRect" parent="Layers"]
material = ExtResource("dark")
layout_mode = 1
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
grow_horizontal = 2
grow_vertical = 2
mouse_filter = 2
texture = ExtResource("5")
expand_mode = 1
stretch_mode = 5
[node name="EnergyVfxFront" type="Node2D" parent="."]
unique_name_in_owner = true
position = Vector2(64, 64)
[node name="Label" type="Label" parent="."]
layout_mode = 1
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
offset_left = 16.0
offset_top = -29.0
offset_right = -16.0
offset_bottom = 29.0
grow_horizontal = 2
grow_vertical = 2
theme_override_colors/font_color = Color(1, 0.964706, 0.886275, 1)
theme_override_colors/font_shadow_color = Color(0, 0, 0, 0.188235)
theme_override_colors/font_outline_color = <EnergyLabelOutlineColor as Color(r, g, b, 1)>
theme_override_constants/shadow_offset_x = 3
theme_override_constants/shadow_offset_y = 2
theme_override_constants/outline_size = 16
theme_override_constants/shadow_outline_size = 16
theme_override_fonts/font = ExtResource("font")
theme_override_font_sizes/font_size = 36
text = "3/3"
horizontal_alignment = 1
vertical_alignment = 1
```

Each layer references one distinct 256x256 `character_energy` output. A successful scene
load alone is insufficient: the proof must find one native counter, all five exact paths,
and a settled screenshot.

The pool icons stay separate from full energy and from one another. The card pool checks
`energy_large.png` before returning `BigEnergyIconPath` and independently checks
`energy_text.png` before returning `TextEnergyIconPath`. The large route must resolve the
256x256 texture in a real hand card's `%EnergyIcon`. The text route must resolve the 24x24
path in a real card description using `EnergyIconsFormatter`; seeing the large icon does
not prove the rich-text consumer. When either custom file is absent, map the stable custom
pool prefix to the corresponding original Ironclad resource as a literal path:
`res://images/atlases/ui_atlas.sprites/card/energy_ironclad.tres` or
`res://images/packed/sprite_fonts/ironclad_energy_icon.png`. Do not call
`EnergyIconHelper.GetPath` from the pool getter (`recipes/character.md` § Character-wide
theme), and never synthesize the fallback from a palette label such as `red`.
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
