# Recipe: Character Foundation

> Live-proven on STS2 stable `0.107.1` with RitsuLib `0.4.67` by focused Character
> Foundation and presentation proofs. This recipe covers exactly-once registration,
> typed pools, starters, localization, run entry, one hosted starter mechanic,
> the nine promoted static presentation profiles, and the bounded non-Spine
> Idle/Attack/Hit/Dead combat cues. Selected resource/buffer/UI
> capability details live in `reference/character-resource.md` and
> `reference/ordered-card-buffer.md`; this Foundation recipe does not duplicate them or
> promote Ancient, Spine, Cast, trails, arbitrary custom materials, multiplayer
> presentation, or audio. Its bounded theme uses only RitsuLib's public
> pool-material helper.

Read `reference/ritsulib-adapter.md` first. When static art is selected, also
read `reference/character-presentation.md` and `reference/art-contract.md`.
When combat cues are selected, additionally read `reference/character-combat-cues.md`.

This recipe creates a new Mod-owned Character. For a pinned existing vanilla Character's
fresh unlock gate, resolve it through `reference/vanilla-overrides.md` and then use
`reference/vanilla-availability-overrides.md`, which permits a singleplayer pinned-epoch
requirement only; it does not permit permanent disable, pool replacement, or registration
as a generated-Mod Character.

## Registration and model shell

Use the pinned skill-the-spire scaffold. Do not invoke an Alchyr/BaseLib character
template, add pool attributes, instantiate the model, or call `AddCharacter`.
Register the character, starters, and every pool member once through one content
pack:

```csharp
RitsuLibFramework.CreateContentPack(ModId)
    .Character<<CharacterName>>(character => character
        .AddStartingCard<<Strike>>(5, order: 10)
        .AddStartingCard<<Guard>>(5, order: 20)
        .AddStartingRelic<<StarterRelic>>(1, order: 0))
    .Card<<CardPool>, <Strike>>()
    .Card<<CardPool>, <Guard>>()
    .Card<<CardPool>, <CommonAttackA>>()
    .Card<<CardPool>, <CommonAttackB>>()
    .Card<<CardPool>, <CommonSkillA>>()
    .Card<<CardPool>, <CommonSkillB>>()
    .Card<<CardPool>, <CommonPower>>()
    .Relic<<RelicPool>, <StarterRelic>>()
    .Potion<<PotionPool>, <Potion>>()
    .Power<<Power>>()
    .Apply();
```

When the selected design includes Darv dialogue, the same content pack must register a semantically
authored Ancient Card for Darv's unchanged Dusty Tome option:

```csharp
    .Card<<CardPool>, <AncientCard>>()
    .DustyTomeCard<<CharacterName>, <AncientCard>>()
```

`<AncientCard>` must report `CardRarity.Ancient`. Do not remove Dusty Tome, map a Basic
starter, or continue when the Character design has no approved Ancient Card.

The character extends the typed RitsuLib template. Fill every public abstract
member explicitly; do not infer historical getter names:

```csharp
using Godot;
using MegaCrit.Sts2.Core.Entities.Characters;
using STS2RitsuLib.Scaffolding.Characters;

public sealed class <CharacterName>
    : ModCharacterTemplate<<CardPool>, <RelicPool>, <PotionPool>>
{
    public const int InitialHp = <HP>;

    public override CharacterGender Gender => CharacterGender.Neutral;
    public override int StartingHp => InitialHp;
    public override int StartingGold => <gold>;
    public override int MaxEnergy => <max-energy>;
    public override int BaseOrbSlotCount => <base-orb-slots>;
    public override string? PlaceholderCharacterId => "ironclad";
    public override Color NameColor => <CharacterName>Theme.NameColor;
    public override Color EnergyLabelOutlineColor => <CharacterName>Theme.EnergyLabelOutlineColor;
    public override float AttackAnimDelay => 0.15f;
    public override float CastAnimDelay => 0.25f;
    public override bool RequiresEpochAndTimeline => false;

    public override List<string> GetArchitectAttackVfx() =>
    [
        "vfx/vfx_attack_blunt",
        "vfx/vfx_heavy_blunt",
        "vfx/vfx_attack_slash",
        "vfx/vfx_bloody_impact",
        "vfx/vfx_rock_shatter",
    ];
}
```

`StartingHp`, `StartingGold`, `MaxEnergy`, and `BaseOrbSlotCount` come from current SPEC.
Native values such as 99 Gold, 3 Energy, and 0 base Orb slots are design analogies/defaults,
not hard requirements. Foundation may prove a separate starter mechanic such as one turn-1
Energy gain, but must not replace native Energy or invent an alternative-energy hook.

## Optional Character capability and state routes

For a separable Character-owned state/display bundle, read `reference/model-capabilities.md` and
use `CharacterCapability`; do not claim normal owner-hook dispatch. For Character-owned
player/run/profile state, lifecycle, persistence, or deterministic RNG, read
`reference/lifecycle-state-rng.md`. Keep gameplay effects on the actual Card/Relic/Power owner,
and prove Character identity plus the selected save/profile lifecycle. These routes do not create
Settings, Progression, Multiplayer, or process-wide effects.

## Typed pools and starter ecosystem

Use RitsuLib's public pool models:

```csharp
public sealed class <CardPool> : TypeListCardPoolModel
{
    public override string Title => "<Character> Cards";
    public override string EnergyColorName => "<stable custom energy prefix>";
    public override Color DeckEntryCardColor => <CharacterName>Theme.DeckEntryCardColor;
    public override Color EnergyOutlineColor => <CharacterName>Theme.EnergyOutlineColor;
    public override Material? PoolFrameMaterial => <CharacterName>Theme.CardFrameMaterial;
    public override string? BigEnergyIconPath => <CharacterName>Theme.ExistingLargeEnergyIconPath;
    public override string? TextEnergyIconPath => <CharacterName>Theme.ExistingTextEnergyIconPath;
    public override bool IsColorless => false;
}

public sealed class <RelicPool> : TypeListRelicPoolModel
{
    public override string EnergyColorName => "<stable custom energy prefix>";
}

public sealed class <PotionPool> : TypeListPotionPoolModel
{
    public override string EnergyColorName => "<stable custom energy prefix>";
}
```

Use the same stable, Mod-owned prefix for all three pools. It is a lookup key, not a display
color: never lower a palette name such as `red` into `EnergyColorName`, because missing
custom art would make the engine request an ungrounded `energy_red` resource.

Register every concrete member with its pool generic. Starter cards are
`CardRarity.Basic`; starter relics are `RelicRarity.Starter`. Use the same Character
registration entry for all current-SPEC starter multisets: `.AddStartingCard<T>(count, order)`,
`.AddStartingRelic<T>(count, order)`, and `.AddStartingPotion<T>(count, order)`. Zero entries
means an empty starter multiset; never register a placeholder model merely to fill one. Every
starter must also be registered in its typed content graph.

Before entering a
native Shop, the unlocked non-Basic pool must contain at least two eligible
Attacks, two eligible Skills, and one eligible Power. The merchant excludes the
first same-type result while filling the second slot, so a `1/1/1` pool throws
before the Shop UI exists. Author real effect cards for all five slots. Verification derives
HP, Gold, Energy, Orb slots, and all three exact starter multisets from current SPEC.

## Character-wide theme

Keep all runtime theme values in one Character-local contract. Values come from the
accepted SPEC; do not choose a second palette while authoring. RitsuLib's public
pool-material surface applies one cached deterministic hue replacement to the vanilla
card-frame texture, so no generated frame image, custom shader, or `.tres` file is needed:

```csharp
using Godot;
using MegaCrit.Sts2.Core.Helpers;
using STS2RitsuLib.Utils;

internal static class <CharacterName>Theme
{
    public static Color NameColor => new("<RRGGBB>");
    public static Color EnergyLabelOutlineColor => new("<RRGGBB>");
    public static Color DeckEntryCardColor => new("<RRGGBB>");
    public static Color EnergyOutlineColor => new("<RRGGBB>");

    public const float FrameRed = <0..1>f;
    public const float FrameGreen = <0..1>f;
    public const float FrameBlue = <0..1>f;
    public const float FrameBrightness = <0..2>f;

    private static ShaderMaterial? _cardFrameMaterial;
    public static Material CardFrameMaterial => _cardFrameMaterial ??=
        MaterialUtils.CreateReplaceHueShaderMaterial(
            FrameRed, FrameGreen, FrameBlue, FrameBrightness);

    public static string LargeEnergyIconPath =>
        <CharacterName>.CharacterUi("energy_large.png");
    public static string TextEnergyIconPath =>
        <CharacterName>.CharacterUi("energy_text.png");

    public const string PlaceholderEnergyColorName = "ironclad";
    public const string PlaceholderTextEnergyIconPath =
        "res://images/packed/sprite_fonts/ironclad_energy_icon.png";

    public static string? ExistingLargeEnergyIconPath =>
        ResourceLoader.Exists(LargeEnergyIconPath)
            ? LargeEnergyIconPath
            : EnergyIconHelper.GetPath(PlaceholderEnergyColorName);
    public static string? ExistingTextEnergyIconPath =>
        ResourceLoader.Exists(TextEnergyIconPath)
            ? TextEnergyIconPath
            : PlaceholderTextEnergyIconPath;
}
```

The large icon is a transparent 256x256 `character_energy_large` output consumed through
`EnergyIconHelper.GetPath` by a real `NCard.%EnergyIcon`. The text icon is a separate
transparent 24x24 `character_energy_text` output consumed by `EnergyIconsFormatter` in
rich-text card descriptions. Both use the SPEC's shared palette/motif brief, but each is
composed and normalized for its own size. Missing files fall back independently to the
base-game Ironclad resources: `energy_ironclad.tres` for the large Card icon and
`ironclad_energy_icon.png` for rich text. The full combat counter follows the explicit
`PlaceholderCharacterId = "ironclad"` profile and resolves
`ironclad_energy_counter.tscn`. Do not derive any fallback path from the theme color.

Tier 2 asserts the exact pool sets, not only their counts, and separately asserts
the exact starter deck/relic multisets. A non-starter pool card must never leak
into the starter deck.

## Localization

RitsuLib uses the normalized public entry
`<MOD>_CHARACTER_<TYPE>`. Ship the 14 flat `characters.json` keys:

```text
<CHAR_ID>.title
<CHAR_ID>.titleObject
<CHAR_ID>.description
<CHAR_ID>.pronounObject
<CHAR_ID>.possessiveAdjective
<CHAR_ID>.pronounPossessive
<CHAR_ID>.pronounSubject
<CHAR_ID>.goldMonologue
<CHAR_ID>.eventDeathPrevention
<CHAR_ID>.aromaPrinciple
<CHAR_ID>.cardsModifierTitle
<CHAR_ID>.cardsModifierDescription
<CHAR_ID>.banter.alive.endTurnPing
<CHAR_ID>.banter.dead.endTurnPing
```

Also ship this complete repeating `ancients.json` group. It covers Architect win index
zero and all later wins even when no optional Ancient dialogue was requested:

```text
THE_ARCHITECT.talk.<CHAR_ID>.0-0r.char
THE_ARCHITECT.talk.<CHAR_ID>.0-0r.next
THE_ARCHITECT.talk.<CHAR_ID>.0-1r.ancient
THE_ARCHITECT.talk.<CHAR_ID>.0-visit
THE_ARCHITECT.talk.<CHAR_ID>.0-startattack
THE_ARCHITECT.talk.<CHAR_ID>.0-endattack
```

Use visit `0`, start attackers `None`, and end attackers `Architect` unless SPEC says
otherwise. When SPEC selects Character-specific dialogue for a cataloged vanilla Ancient
or richer Architect dialogue, read `reference/ancient-dialogue.md` and lower every
semantic group through that contract. Do not generate an Ancient injection patch.

## Static presentation

Put the promoted paths in one `CharacterAssetProfile`:

| consumer | profile field | exact asset |
|---|---|---|
| selection portrait | `Ui.CharacterSelectIconPath` | 132x195 PNG |
| selection background | `Ui.CharacterSelectBgPath` | raw `.tscn` wrapping 1920x1200 PNG |
| top-panel identity | `Ui.IconTexturePath`, `Ui.IconOutlineTexturePath`, and `Ui.IconPath` | 88x88 main/derived-outline PNGs plus raw wrapper scene |
| combat body | existence-checked `TryCreateCreatureVisuals()` | 512x512 PNG; public resource factory + reviewed `VisualNodeStyle` |
| RestSite body | `Scenes.RestSiteAnimPath` | raw `.tscn` wrapping 512x512 PNG |
| Shop body | `Scenes.MerchantAnimPath` | raw `.tscn` wrapping 512x512 PNG |
| full energy | `Scenes.EnergyCounterPath` | raw `.tscn` using five 256x256 PNGs |
| large card energy | card-pool `BigEnergyIconPath` | checked 256x256 PNG |
| text card energy | card-pool `TextEnergyIconPath` | checked 24x24 PNG |

Locked selection and map marker paths may retain checked assets, but they are not
pipeline-promoted until their real consumers are visibly proved. RitsuLib's resolved
profile keeps the explicitly selected Ironclad placeholder/native fallback for missing
fields. Do not
add the historical static-merchant prefix: the Shop proof rendered a real
`NMerchantCharacter` directly from the RitsuLib scene profile.

Leave `Scenes.VisualsPath` unset for the generated combat body so the resolved profile
retains its checked missing-file fallback. When `images/charui/combat.png` exists, load it
as `Texture2D` and call
`RitsuGodotNodeFactories.CreateFromResource<NCreatureVisuals>(texture, style)` from the
protected override. The settled style is `VisualNodeStyle.Empty.WithScale(0.80f)` followed
by `.WithPosition(new Vector2(0f, -184f))`; return `null` when the PNG is absent. Do not use
the texture-only `Scenes.VisualsPath` shortcut because it cannot carry this reviewed
visible-footprint transform.

## Bounded combat cues

The optional combat-cue bundle is exactly Idle 4x180ms loop, Attack 4x90ms one-shot then
Idle, Hit 4x80ms one-shot then Idle, and Dead 6x140ms terminal final pose. All eighteen
transparent 512x512 frames share the static combat content box, baseline, public style,
and the fixed Bounds/Intent/Center/Orb/Talk geometry from
`reference/character-combat-cues.md`.

Require every expected path and size before building one private `VisualCueSet`. Use
`Idle/00` to create the anchored combat visuals and pass that set directly to
`ModAnimStateMachines.StandardCue` from `SetupCustomCombatAnimationStateMachine`.
Never set `CharacterAssetProfile.VisualCues`: RitsuLib also uses that global fallback in
merchant/rest playback. One missing or invalid frame disables all cues, creates no playback
node, and selects the checked static `combat.png`; if that file is also absent, return
`null` for the resolved profile fallback.

## Native Ancient dialogue boundary

The public Character abstract members include `NameColor`, animation delays, and
`GetArchitectAttackVfx()`. RitsuLib's registered population patch reads the generated flat
table and appends only this Character's dialogue to native sets. The generated Mod emits no
Harmony/reflection injection. Follow `reference/ancient-dialogue.md` for catalog, visit,
repeat, prompt, attacker, validation, and hosted-proof rules. Custom Ancient models,
backgrounds/layouts, options/rewards, line audio, and multiplayer remain unsupported.

## Tier 2: selection + RunStart + CombatPlayer + world consumers

1. Require exactly one registered custom Character.
2. On the real character-select screen, locate its button by normalized `%Icon`
   texture path, unlock only for proof setup, and select that exact model. Never
   choose the first unlocked character.
3. Prove the 132x195 portrait and 1920x1200 background in the visible select UI,
   assert the button is inside the 1920x1080 viewport, capture a settled screenshot, and
   click Confirm.
4. After `NRun.GlobalUi` is ready, assert selected identity, exact HP/Max HP,
   starting Gold, all three exact typed pool types/member sets, every independently
   registered supporting Power, and exact starter deck/relic multisets.
5. Enter a real combat, wait for `PlayerTurnPhase.Play`, and assert native
   `MaxEnergy`, the hosted starter mechanic, all four exact theme colors, frame shader
   target/brightness, the non-Spine 512x512 body, normal and outlined 88x88 top-panel
   icon textures under the same real `NTopBarPortrait`, one
   `NEnergyCounter`, all five 256x256 layers, a 256x256 large icon in a real hand
   `NCard.%EnergyIcon`, the distinct 24x24 path in a real formatted card description, and
   every generated Relic's exact 256x256 main/outline pair under one real `NRelic`.
   For the body also assert alpha bounds within
   `(26,26)-(486,486)`, baseline `486`, scale `0.80`, position `(0,-184)`, resulting screen
   bounds inside the viewport, and no overlap with top/bottom UI, enemy lane, or turn banner.
6. When combat cues are selected, prove Idle loops, Attack/Hit each return to Idle, all
   shared geometry remains fixed, the first combat's playback node is freed, and a fresh
   combat's Dead sequence reaches and holds its sixth frame. Run the one-missing-frame
   fallback proof separately and require static combat with no playback node/frame flash.
7. Finish combat, enter RestSite and Shop, and assert the real
   `NRestSiteCharacter` / `NMerchantCharacter`, exact 512x512 resources, and
   settled screenshots.
8. Emit the final `character foundation/static-presentation ... observed=all`
   marker only after every assertion passes, followed by `selftest done` and a
   strict no-fresh-error check.

For every generated Character, derive the selected model identity, HP, Gold, pool members,
starter deck/relic multiset, supporting models, MaxEnergy, and terminal state summary from
the current `SPEC.md`. Do not copy exact values or log markers from a historical acceptance
Mod. The 2026-07-27 Meridian proof added the split large/text Energy
consumers and bounded card/UI theme; the maintainer's headed review passed all seven
visible checks, while generated Mods retain the automatic node/property assertions.
The 2026-07-27 Meridian cue proof separately passed the complete four-action route,
playback cleanup, strict Tier 2, and the one-missing-disables-all static fallback; the human
lead accepted both headed checkpoints.

## Checklist

- [ ] `ModCharacterTemplate<TCardPool,TRelicPool,TPotionPool>` and all abstract members compile
- [ ] one content pack owns Character, starters, every pool member, and supporting Power
- [ ] no BaseLib namespace/package/manifest dependency, pool attribute, or manual registration
- [ ] exact HP/Gold/pool member sets/starter multisets are asserted
- [ ] non-Basic pool has at least `2 Attack / 2 Skill / 1 Power` before Shop
- [ ] all 14 Character keys and complete Architect dialogue use the normalized Character entry
- [ ] selected Ancient groups pass `ancient_dialogue.py`, mount from a `has_pck=true` resource tree, and preserve native scenes/options
- [ ] Darv dialogue registers a Mod-local `CardRarity.Ancient` Dusty Tome candidate
- [ ] every selected static asset renders in its real consumer with a screenshot and state proof
- [ ] one theme contract owns four colors, frame parameters, and distinct 256x256/24x24 Energy paths
- [ ] one 3% white-alpha rule derives the top icon and every generated Relic outline with no acquisition call
- [ ] selected combat cues use the fixed private four-action set, shared geometry, cleanup, and all-or-nothing fallback
- [ ] `CharacterAssetProfile.VisualCues` remains unset; merchant/rest keep their static textures
- [ ] locked/map/custom-Ancient/Cast/Spine/trail/arbitrary-material/multiplayer/audio boundaries remain explicit
- [ ] strict Tier 1/Tier 2, `selftest done`, and no fresh error pass on the pinned profile
