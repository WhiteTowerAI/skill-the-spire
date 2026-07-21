# Character static and native presentation

Status: **pipeline-supported for eight static profiles on STS2 0.107.1 / BaseLib 3.3.5**
by the 2026-07-21 `WayfinderAcceptance` headed runs. Selection portrait/background,
top-panel icon, non-Spine combat/rest/merchant bodies, full energy, and compact resource
icon are live-proven. Locked selection, map marker, and the native Ancient/Architect flow
remain unverified and keep their inherited fallbacks.

Use this page together with `recipes/character.md` and `reference/art-contract.md` when a
Character SPEC selects static presentation. The Foundation remains valid with template
assets when no custom profile is selected.

## Getter and consumer matrix

Treat every row independently. A working resource path does not prove that its real host
rendered it.

| profile | Character/BaseLib surface | real consumer | status and fallback |
|---|---|---|---|
| selection portrait, 132x195 | `CustomCharacterSelectIconPath` | `NCharacterSelectButton.%Icon` and selected-character panel | **live-proven loose PNG**; inherit the template portrait when absent |
| locked portrait, 132x195 | `CustomCharacterSelectLockedIconPath` | locked character-select view | grounded, not live-proven; inherit the template locked portrait |
| top-panel icon, 88x88 | `CustomIconTexturePath` plus `CustomIcon` | selected-character identity/global UI | **live-proven loose PNG**; inherit the template icon when absent |
| map marker, 49x64 | `CustomMapMarkerPath` | map player marker | grounded, not live-proven; inherit the template marker |
| select background, 1920x1200 | `CustomCharacterSelectBg` | character-select background scene | **live-proven raw `.tscn` + PNG**; inherit the template scene when either asset is absent |
| combat body, 512x512 | `CreateCustomVisuals()` | `NCreatureVisualsFactory` / player `NCreature` | **live-proven loose PNG**, static and non-Spine; return `null` to retain the inherited scene when absent |
| rest body, 512x512 | `CustomRestSiteAnimPath` | rest-site Character scene | **live-proven raw `.tscn` + PNG**; inherit the template scene when absent |
| merchant body, 512x512 | `CustomMerchantAnimPath` | merchant Character scene | **live-proven raw `.tscn` + PNG** with the verified static-merchant prefix; use the inherited Spine scene if the patch or asset is unavailable |
| full energy counter, five 256x256 layers | `CustomEnergyCounter` | native `NEnergyCounter` | **live-proven loose PNG factory**; return `null` unless every layer exists, retaining the inherited counter |
| compact resource icon, 24x24 | card-pool `TextEnergyIconPath` or a checked `charui` texture | card text and the bounded resource counter | **live-proven loose PNG**; omit the texture and keep text-only UI when absent |

`CustomIcon` is a `Control`, not only a path. The proven implementation creates it from
the checked texture and fills its parent:

```csharp
public override Control CustomIcon
{
    get
    {
        var icon = NodeFactory<Control>.CreateFromResource(CustomIconTexturePath);
        icon.SetAnchorsAndOffsetsPreset(Control.LayoutPreset.FullRect);
        return icon;
    }
}
```

For the combat body, do not point a scene getter at the PNG. Let BaseLib construct the
static visuals and retain `null` as the checked fallback:

```csharp
public override NCreatureVisuals? CreateCustomVisuals()
{
    string path = CharacterUi("combat.png");
    return ResourceLoader.Exists(path)
        ? NodeFactory<NCreatureVisuals>.CreateFromResource(path)
        : null;
}
```

The headed proof resolved a `Sprite2D` with the exact 512x512 custom texture and
`HasSpineAnimation == false`. This does not support attack, hurt, cast, death, phobia,
trail, transition, or remote-player animation.

## No-editor scene and energy contract

The upstream PckPacker package skips `.tscn`, but open-mod's bundled `build.py` detects a
standard `<project>/<ModName>/**/*.tscn` tree and automatically rebuilds the PCK through
`pack_pck.py`. The fallback writes Godot 4.5.1 format-v3 PCKs, PNG CTEX/import remaps, and
raw text scenes. Generated-mod authors do not install Godot or MegaDot. `.gdshader`,
`.gdscript`, and `.gdextension` remain rejected because their import/compile contracts are
not implemented.

Use the smallest wrapper matching the real consumer. Selection background:

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

Rest and merchant wrappers are each one `Sprite2D`; BaseLib converts them to their native
types:

```ini
[gd_scene load_steps=2 format=3]
[ext_resource type="Texture2D" path="res://<ModName>/images/charui/rest.png" id="1"]
[node name="CharacterRest" type="Sprite2D"]
texture = ExtResource("1")
```

Use `merchant.png` and name the merchant root `Visuals`. Check both the PNG and scene before
returning their getter; otherwise return `base.Custom*Path`.

BaseLib 3.3.5's merchant factory accepts the static node, but
`NMerchantCharacter._Ready()` still assumes child 0 is Spine. Select the exact versioned
B-prefix from `capability-kernel.md`; it skips only the static instance and leaves vanilla/
Spine instances unchanged:

```csharp
private static bool Prefix(NMerchantCharacter __instance) =>
    __instance.GetChildCount() == 0 || __instance.GetChild(0) is not Sprite2D;
```

Gate `CustomMerchantAnimPath` on successful patch status as well as resource existence.
The exact target is public `NMerchantCharacter._Ready()`, STS2 `0.107.1`, MVID
`97f10687-c306-4798-ab75-8b9f23f34dfb`; target mismatch keeps the inherited merchant scene.

Full energy is not scene-backed. Normalize five `character_energy` outputs as
`orb_layer_1.png` through `orb_layer_5.png`, each 256x256, and use BaseLib's legacy factory:

```csharp
public override CustomEnergyCounter? CustomEnergyCounter
{
    get
    {
        var paths = Enumerable.Range(1, 5).Select(EnergyLayer).ToArray();
        return paths.All(path => ResourceLoader.Exists(path))
            ? new CustomEnergyCounter(EnergyLayer, outlineColor, burstColor)
            : null;
    }
}

private static string EnergyLayer(int layer) =>
    CharacterUi($"orb_layer_{layer}.png");
```

BaseLib builds the native 128x128 `NEnergyCounter`, number label, two rotating layers,
darkened zero-energy state, and burst hooks. Do not replace this with `CustomEnergyCounterPath`
for static art.

## Bounded resource and buffer UI

The supported richer UI remains under the exact verified
`NCombatUi.EnergyCounterContainer` adapter from `capability-kernel.md`. It replaces the
plain-label presentation with one fixed `HBoxContainer`:

```text
InkCounterControl (HBoxContainer, minimum 220x32, separation 6)
  Icon (TextureRect, minimum 24x24, KeepAspectCentered)
  ValueLabel (Label, minimum 188x32, vertically centered)
```

Use `MouseFilter.Ignore` on the root and children. Load the 24x24 icon only after
`ResourceLoader.Exists`; the checked failure mode is the same live text without an icon.
The label composes resource and optional ordered-buffer state, for example
`Ink: 3 | Route: N>E>S`, and retains resource/lifetime metadata. Refresh after mount,
gain, successful or rejected spend, append, overflow feedback, compile/clear, and combat
reset. Guard refreshes with the local player and `IsInsideTree()`.

The 2026-07-21 proof observed the exact custom icon path/size, root size, text, metadata,
and two-combat reset while preserving the resource and ordered-buffer semantic contract.
This is not a top-bar resource, alternative Energy, arbitrary custom-zone UI, animation,
or remote-player presentation.

## Ancient opening and Architect research

The native opening is not normal Event rich text:

- `NAncientEventLayout.InitializeVisuals()` creates the fixed Ancient background and an
  `NAncientNameBanner` from `ui/ancient_name_banner`.
- The banner installs `RichTextAncientBanner` and renders the uppercase
  `AncientEventModel.Title` plus `AncientEventModel.Epithet`.
- Architect dialogue uses the selected Character's `SpeechBubbleColor`.
- Architect player attacks consume `CharacterModel.GetArchitectAttackVfx()`.
- Generated Characters already supply the four required
  `THE_ARCHITECT.talk.<CHAR_ID>` keys listed in `recipes/character.md`.

These contracts are source-grounded but **not headed-proven for a custom Character**.
Until a real Ancient/Architect acceptance enters that host and observes the banner,
dialogue, color, and attack VFX selection, do not claim native Ancient presentation as
pipeline-supported. Custom Ancient layouts/backgrounds remain deferred independently.

## Acceptance contract

For each selected loose-PNG profile:

1. normalize the exact profile through `gen_sprite.py import` and retain its checked
   fallback;
2. rebuild the `.pck` and enter the real Character consumer;
3. assert the rendered node uses the exact custom resource and expected size;
4. capture a settled headed screenshot that visibly excludes the fallback;
5. keep the Foundation/resource/buffer structured Tier-2 marker and no fresh error.

Wayfinder satisfies this contract for selection portrait/background, top-panel icon,
static combat/rest/merchant bodies, full energy, and the compact resource icon/counter.
Test locked selection, map marker, and Ancient/Architect separately before promoting them.

## Unsupported extensions

- custom Character Spine animation, attacks, hurt/cast/death states, trails, and
  animated transitions;
- custom transition/card-trail materials, shaders, and material lifecycle;
- remote-player/multiplayer hands, identity, ownership, and Character UI;
- custom Character audio registration, dialogue/attack/energy cues, and fallback/mix
  behavior;
- shaders/scripts and editor-compiled scene resources outside the raw static wrappers;
- arbitrary top-bar or retained-card-zone UI;
- custom Ancient layouts/backgrounds or an unproven native Architect presentation claim.

Animation, materials, multiplayer presentation, and audio are four explicit tracks in the
later Character presentation expansion. None is implied by the current static profiles.
