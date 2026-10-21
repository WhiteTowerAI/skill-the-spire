# Recipe: Character Foundation

Everything one new playable Character needs: one selectable Character shell plus its starter
ecosystem, with `RunStart` + `CombatPlayer` proof. This recipe covers exactly-once registration,
typed pools, starters, localization, run entry, one hosted starter mechanic, the nine promoted
static presentation profiles, the bounded non-Spine Idle/Attack/Hit/Dead combat cues, and the
Character-wide theme (RitsuLib's public pool-material helper only). Load
`design/character-foundation.md` before creative questions.

Also read, only when SPEC selects it:

- static art: `reference/character-presentation.md` and `reference/art-contract.md`;
- combat cues: `reference/character-combat-cues.md`;
- a secondary resource: `reference/character-resource.md`; an ordered semantic buffer:
  `reference/ordered-card-buffer.md`;
- Character dialogue on vanilla Ancients or richer Architect dialogue:
  `reference/ancient-dialogue.md`.

Ancient models, Spine, Cast, trails, arbitrary custom materials, multiplayer presentation, and
audio are not promoted here. A pinned existing vanilla Character's fresh unlock gate goes through
`reference/vanilla-overrides.md` and `reference/vanilla-availability-overrides.md` (singleplayer
pinned epoch only; no permanent disable, pool replacement, or registration as a Mod Character).

## SPEC fields

```markdown
# SPEC — <Mod Name>

- **mod id**: <stable mod identity>
- **author**: <author>
- **content**:
  - name: <shown character name>
  - surface: character
  - logical id: <stable character stem>
  - starting HP: <positive int; native 66–80 is an analogy, see `design/character-foundation.md`>
  - starting Gold: <nonnegative int; native 99 is the default analogy>
  - max energy: <positive int; native 3 is the default analogy>
  - base Orb slots: <nonnegative int; native values are analogies>
  - description: <short identity/theme>
  - pronouns: <subject/object/possessive adjective/possessive pronoun>
- **registration**:
  - availability: character-scoped card/relic/potion pools
  - ownership: player
  - placement: character select screen
- **localization**:
  - languages: [eng, zhs]
  - fields: character name, description, and pronouns (in `characters.json`); all pool Card
    and Power titles/descriptions; all Ancient dialogue lines
  - table intent: `characters.json` plus element-specific tables
  - formatting: vanilla text style (`reference/vanilla-text-style.md`); description is two
    short lines joined by `\n`; Cards and Powers follow their own rows
- **effects**:
  - trigger: run start
  - target: player
  - starter deck: <exact Basic-card multiset, base effects, upgrades, and total count>
  - starter deck rationale: <how its first-run decisions teach the core mechanic>
  - starter relic: <exact Starter relic>
  - starter potions: <exact potion multiset, including empty>
  - Orobas upgrades: none | <Archaic Tooth: starter Card -> Ancient Card>; <Touch of Orobas:
    starter Relic -> refined Starter Relic> (§ Registration; without them Archaic Tooth is
    never offered and Touch of Orobas gives Circlet)
  - hosted mechanic: <one starter card/relic grounded public mechanic with exact numbers>
  - pool cards: <every non-Basic pool card, each with its exact effect and numbers; each one
    with a non-trivial mechanic also needs its own `recipes/card.md` envelope>
  - scaling: <named values for each pool card or hosted mechanic, or none>
- **state**:
  - lifetime: run
  - owner: player
  - advance/check: pools and starter state initialized at RunStart
  - reset: run end
  - persistence: ordinary
  - visible state: character select button/background, HP, energy display
- **presentation**:
  - assets: placeholder | generate (Character static profiles and optional combat cues;
    list each consumer and acquisition count)
  - art source: host-tool | backend:<name> | local-image (generate only)
  - character art tier: minimal | standard | full (generate only; see the interview's art step)
  - native presentation: character select screen + combat UI
  - character art bundle: one `CharacterArtBundle` row per selected slot; record
    required/optional, output path, dimensions, alpha policy, fallback, and real consumer
  - character identity route: selection portrait is the sole identity bootstrap;
    combat/rest/merchant use identity + type-matched style; the combat cue sheet uses the
    approved combat body as its anchor + combat style;
    background/icon/Energy use palette/motif brief + type-matched style only
  - palette/motif brief: concise colors, motif, material, and silhouette derived from
    the user's description and reviewed selection portrait; never a second canonical image
  - character theme contract:
    - name color: `<RRGGBB>`
    - energy-label outline: `<RRGGBB>` (outline of the combat "3/3"; never a free pick:
      use the color `character_art.py` reports for the counter)
    - deck-entry color: `<RRGGBB>`
    - energy outline: `<RRGGBB>` (outline of the card cost and the counter's edge ring;
      derived from the large Energy icon with `--energy-colors <frame>,auto`)
    - card-frame target RGB: `<0..1, 0..1, 0..1>`
    - card-frame brightness: `<0..2>`
    - energy-icon palette: `<primary/accent/outline colors plus motif/material>`
    - full Energy counter: rendered from the card-frame target RGB and energy outline
      (`character_art.py --energy-colors`); no generation call
    - energy resource prefix: `<stable Mod-owned lookup key; never a palette name>`
    - placeholder Energy fallback: Ironclad counter, large Card icon, and rich-text icon
  - character art profiles: none | selection | locked selection | top-panel icon |
    map marker | select background | combat body | rest body | merchant body | energy |
    large energy icon | text energy icon (never infer one profile from another; mark
    unsupported consumers as explicit gaps per `reference/character-presentation.md`)
  - character combat cues: none | fixed bounded bundle
    - actions: Idle `4 x 250ms, loop` (the anchor breathing); Attack `9 x 60ms, one-shot ->
      Idle`; Hit `6 x 70ms, one-shot -> Idle`; Dead `5 x 170ms, terminal final frame`
    - acquisition: one 2048x2048 sheet (shared anchor + 6 Attack + 4 Hit + 5 Dead poses),
      one call, after the body sheet; the normalized `charui/combat.png` as anchor reference;
      a route that cannot return 2K keeps the static body (1K frames were rejected as too
      blurry)
    - poses: <signature item, attack wind-up and strike, in the SPEC's words>
    - continuity lock: same identity, costume, proportions, equipment, handedness, facing,
      camera, apparent scale, and baseline in every cell
    - frame motion: one concrete, distinct pose per cell; Attack/Hit start on the shared
      anchor, Hit recovers through Attack's recovery, holds repeat a cell; Dead lowers the
      full-size body to the ground
    - attack timing: `AttackAnimDelay` `0.30f` (strike at frame 5 x 60ms), so damage lands
      on the strike
    - geometry: shared 512x512 content box/baseline/style and Bounds/Intent/Center/Orb/Talk anchors
    - fallback: one missing or invalid frame disables all cues and uses static combat body
    - explicit gaps: Cast, Spine, trails, audio, animated merchant/rest bodies
- **fallback**:
  - missing asset: Foundation-only template; selected profiles fill only their matched fields;
    Energy uses `ironclad_energy_counter.tscn`, `EnergyIconHelper.GetPath("ironclad")`
    (`energy_ironclad.tres`), and
    `res://images/packed/sprite_fonts/ironclad_energy_icon.png`, never a theme-derived path
  - unavailable seam: preserve Foundation behavior or stop with an explicit unsupported boundary
- **proof**:
  - scenario: RunStart + CombatPlayer
  - driver: locate the real custom character-select button, click it, then assert runtime state
  - invariants:
    - the character is registered exactly once and appears in character selection
    - real character-select button present and clicked
    - runtime identity, HP, three pool types/members, exact deck/relic multisets
    - combat `MaxEnergy` and base Orb slots equal current SPEC plus the hosted mechanic's
      independent state delta
    - every pool card whose mechanic SPEC describes behaviorally is played and asserted
  - boundary cases: Shop-pool card slot fill; art consumer assertions when profiles are selected
- **advanced mechanic**: none | <maintained route or Mod-local route>
- **Ancient dialogue**: none | one block per cataloged vanilla target
  - target: <natural-language Ancient name; adapter resolves the pinned entry>
  - groups:
    - visit rule: first | visit <one-based N> | repeat from visit <one-based N>
      - lines: ordered `speaker: Character|Ancient`, `text`, and a transition prompt on
        every non-terminal line
      - Architect only: start attackers and end attackers, each
        `None|Player|Architect|Both`
  - native priority: preserve the global first-visit-ever introduction before Character
    exact-visit and repeating dialogue
  - explicit gaps: custom Ancient/model/background/layout/options/rewards/audio/multiplayer
- **native design basis**:
  - grammar profile: `design/character-foundation.md @ STS2 0.107.1`
  - pinned facts used: <exact native identities/values used in the proposal>
  - observed convention: <native shape used as the recommendation>
  - creative decision: <exact selected deck shape and teaching intent>
- **deliberate native departure**: none | <departure plus onboarding, compatibility, and
  balance consequences accepted by the user>
- **adapter output** (written to MEMORY after acceptance): character logical id, every
  starter content logical id and localization fields, flat Ancient dialogue keys and
  zero-based visit metadata from the semantic groups, and framework diagnostic record
```

The maintained routes for an `advanced mechanic` are `reference/character-resource.md` and
`reference/ordered-card-buffer.md` (their SPEC blocks are in § Advanced mechanic blocks). If
neither expresses the mechanic, implement it as a Mod-local route under `grounding.md`
§ Mod-local Routes. Never add a manual registration line or invent a nonstandard Energy override.

## Pool cards are content, not filler

A Foundation needs enough unlocked non-Basic Cards to fill the merchant's colored slots, so the
natural failure is to treat them as inventory that only has to *exist*. Pool membership is what
the Foundation proof asserts, and a Card whose behavior is entirely broken satisfies it. Declare
every pool Card's effect in `pool cards`; any pool Card with a real mechanic (anything beyond a
plain damage or Block number) also gets its own `recipes/card.md` envelope and owes that proof. A
Foundation whose signature mechanic lives in a pool Card is unverified until that Card is played.

## Registration

Use the pinned skill-the-spire scaffold. Never invoke an Alchyr/BaseLib Character template, add
pool attributes, instantiate the model, or call `AddCharacter`. Register the Character, starters,
every pool member, and every supporting Power once through one content pack:

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

Starter Cards are `CardRarity.Basic` and starter Relics `RelicRarity.Starter`. Use the same
Character entry for every SPEC starter multiset: `.AddStartingCard<T>(count, order)`,
`.AddStartingRelic<T>(count, order)`, `.AddStartingPotion<T>(count, order)`. Zero entries means an
empty multiset; never register a placeholder model to fill one. Every starter is also registered
in its typed content graph.

When the design includes Darv dialogue, the same pack registers a semantically authored Ancient
Card for Darv's unchanged Dusty Tome option. `<AncientCard>` reports `CardRarity.Ancient`; never
remove Dusty Tome, map a Basic starter, or continue without an approved Ancient Card:

```csharp
    .Card<<CardPool>, <AncientCard>>()
    .DustyTomeCard<<CharacterName>, <AncientCard>>()
```

Orobas offers two starter upgrades that vanilla maps only for vanilla Characters. When the design
includes either, register it on the same pack:

```csharp
    .Card<<CardPool>, <TranscendedCard>>()
    .ArchaicToothTranscendence<<StarterCard>, <TranscendedCard>>()
    .Relic<<RelicPool>, <RefinedStarterRelic>>()
    .TouchOfOrobasRefinement<<StarterRelic>, <RefinedStarterRelic>>()
```

- Archaic Tooth transforms the first deck Card with a mapping, keeping its upgrade and
  enchantment. `<TranscendedCard>` reports `CardRarity.Ancient` (RitsuLib ignores the mapping
  otherwise) and differs from the Dusty Tome Card, which excludes transcendence Cards.
- Touch of Orobas replaces the starter Relic. Give `<RefinedStarterRelic>`
  `RelicRarity.Starter`, as vanilla does with Black Blood, so it never enters an ordinary pool.
- A second mapping for the same starter replaces the first with a warning; map each once.

## Model shell

Extend the typed template and fill every public abstract member explicitly; never infer getter
names from other templates:

```csharp
using Godot;
using MegaCrit.Sts2.Core.Entities.Characters;
using STS2RitsuLib.Scaffolding.Characters;

public sealed class <CharacterName>
    : ModCharacterTemplate<<CardPool>, <RelicPool>, <PotionPool>>
{
    public const int InitialHp = <HP>;

    // Mod-owned resource paths used by the presentation profile, theme, and SelfTest.
    public static string CharacterUi(string fileName) =>
        "res://<ModName>/images/charui/" + fileName;

    public static string CharacterScene(string fileName) =>
        "res://<ModName>/scenes/charui/" + fileName;

    public override CharacterGender Gender => CharacterGender.Neutral;
    public override int StartingHp => InitialHp;
    public override int StartingGold => <gold>;
    public override int MaxEnergy => <max-energy>;
    public override int BaseOrbSlotCount => <base-orb-slots>;
    public override string? PlaceholderCharacterId => "ironclad";
    public override Color NameColor => <CharacterName>Theme.NameColor;
    public override Color EnergyLabelOutlineColor => <CharacterName>Theme.EnergyLabelOutlineColor;
    public override float AttackAnimDelay => 0.15f;   // 0.30f when combat cues are selected
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

`StartingHp`, `StartingGold`, `MaxEnergy`, and `BaseOrbSlotCount` come from SPEC; native 99 Gold,
3 Energy, and 0 Orb slots are analogies, not requirements. Foundation may prove a separate starter
mechanic, such as one turn-1 Energy gain, but never replaces native Energy or invents an
alternative-Energy hook.

## Typed pools and starter ecosystem

Use RitsuLib's public pool models:

```csharp
using Godot;
using STS2RitsuLib.Scaffolding.Content;

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

Use the same stable Mod-owned prefix for all three pools. It is a lookup key, not a display color:
never lower a palette name such as `red` into `EnergyColorName`, because missing custom art would
make the engine request an ungrounded `energy_red` resource.

Before a native Shop, the unlocked non-Basic pool needs at least two eligible Attacks, two Skills,
and one Power. The merchant excludes the first same-type result while filling the second slot, so
a `1/1/1` pool throws before the Shop UI exists. Author real effect Cards for all five slots, each
through `recipes/card.md`; the RitsuLib Shop profile needs no static-merchant patch.

## Character-wide theme

Keep all runtime theme values in one Character-local contract, taken from SPEC; never choose a
second palette while authoring. RitsuLib's public pool-material surface applies one cached
deterministic hue replacement to the vanilla card-frame texture, so no generated frame image,
custom shader, or `.tres` file is needed:

```csharp
using Godot;
using STS2RitsuLib.Utils;

internal static class <CharacterName>Theme
{
    public static Color NameColor => new("<RRGGBB>");
    // The two Energy-number outlines come from character_art.py's number-contrast review.
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

    // Literal vanilla paths. Never call EnergyIconHelper.GetPath from a pool getter.
    public const string PlaceholderLargeEnergyIconPath =
        "res://images/atlases/ui_atlas.sprites/card/energy_ironclad.tres";
    public const string PlaceholderTextEnergyIconPath =
        "res://images/packed/sprite_fonts/ironclad_energy_icon.png";

    public static string? ExistingLargeEnergyIconPath =>
        ResourceLoader.Exists(LargeEnergyIconPath)
            ? LargeEnergyIconPath
            : PlaceholderLargeEnergyIconPath;
    public static string? ExistingTextEnergyIconPath =>
        ResourceLoader.Exists(TextEnergyIconPath)
            ? TextEnergyIconPath
            : PlaceholderTextEnergyIconPath;
}
```

The large icon is a transparent 256x256 `character_energy_large` output consumed through
`EnergyIconHelper.GetPath` by a real `NCard.%EnergyIcon`; the text icon is a separate transparent
24x24 `character_energy_text` output consumed by `EnergyIconsFormatter` in rich-text descriptions.
Both share the SPEC palette/motif brief but are composed for their own size, and each missing file
falls back independently to Ironclad (`energy_ironclad.tres`, `ironclad_energy_icon.png`). Keep
both fallbacks literal: RitsuLib patches `EnergyIconHelper.GetPath` and builds its icon cache by
reading every pool's `BigEnergyIconPath`, so calling the helper from that getter recurses until
the game dies with a stack overflow at run start. The full combat counter follows
`PlaceholderCharacterId = "ironclad"` and resolves `ironclad_energy_counter.tscn`. Never derive a
fallback path from the theme color.

## Optional Character capability and state routes

Read a route only when SPEC selects it and append only its SPEC block:

- a separable Character-owned state/display bundle: `reference/model-capabilities.md` with a
  `CharacterCapability`, which can own typed state, DynamicVars, tips, and supported display
  contributions. A Character is not a run/combat hook listener, so never claim owner-hook
  dispatch;
- Character-owned player/run/profile state, lifecycle, persistence, or deterministic RNG:
  `reference/lifecycle-state-rng.md`.

Keep Card/Relic/Power effects on those models, preserve exact player/run identity, cleanup, and
persistence, and prove the real Character consumer plus any selected save/profile host. These
routes never create a Settings, Progression, Multiplayer, or process-wide effect surface.

A resource SPEC registers one `SecondaryResourceDefinition`, uses `SecondaryResourceCmd` for the
amount and all-or-nothing payment, and mounts the fixed control through public `RegisterCombatUi`.
An ordered-buffer SPEC uses `AttachedState<PlayerCombatState,TState>`, native source-Card result
piles, visible state text, and one configured output Card; never emit a retained-Card
`CustomPile`. A Foundation-only SPEC emits no patch infrastructure. Keep proof-only observers and
assertions out of generated gameplay.

## Localization

RitsuLib uses the normalized entry `<MOD>_CHARACTER_<TYPE>`. Ship the 14 flat `characters.json`
keys:

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

Write them in the vanilla style of `reference/vanilla-text-style.md`:

- `title`/`titleObject`: the plain display name (`The Silent` / `静默猎手`);
- `description`: two short plain sentences joined by `\n`, identity then fighting style
  (`A huntress from outside the Spire.\nReady to stab and poison anything in her way.`);
- pronoun keys: the bare word (`she`, `her`, `hers` / `她`, `她的`);
- `cardsModifierTitle`: `<Name> Cards`; `cardsModifierDescription`:
  `<Name> cards will now appear in rewards and shops.`;
- spoken lines (`goldMonologue`, `eventDeathPrevention`, `aromaPrinciple`, banter): short, in
  character, trailing `...` in English and `……` in Chinese; vanilla wraps murmurs in `[sine]`
  and may tint `aromaPrinciple`, but plain is always valid.

Also ship this complete repeating `ancients.json` group. It covers Architect win index zero and
all later wins even when no optional Ancient dialogue was requested:

```text
THE_ARCHITECT.talk.<CHAR_ID>.0-0r.char
THE_ARCHITECT.talk.<CHAR_ID>.0-0r.next
THE_ARCHITECT.talk.<CHAR_ID>.0-1r.ancient
THE_ARCHITECT.talk.<CHAR_ID>.0-visit
THE_ARCHITECT.talk.<CHAR_ID>.0-startattack
THE_ARCHITECT.talk.<CHAR_ID>.0-endattack
```

Use visit `0`, start attackers `None`, and end attackers `Architect` unless SPEC says otherwise.
Selected dialogue for other cataloged vanilla Ancients or richer Architect groups is lowered
through `reference/ancient-dialogue.md`. Dialogue text may use the engine's `{character}` and
pronoun tokens; prefer them over a hardcoded name so non-English dialogue keeps grammatical
agreement.

### Native Ancient dialogue boundary

RitsuLib's registered population patch reads the generated flat table and appends only this
Character's dialogue to native sets; the generated Mod emits no Harmony or reflection injection.
`reference/ancient-dialogue.md` owns catalog, visit, repeat, prompt, attacker, validation, and
hosted-proof rules. Custom Ancient models, backgrounds/layouts, options/rewards, line audio, and
multiplayer stay unsupported.

## Static presentation

Put the promoted paths in one `CharacterAssetProfile`, keeping its partial fallback semantics:
selected profiles fill only their matching fields after headed proof.

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

Locked selection and map marker paths may keep checked assets, but the Character proof does not
reach those consumers; report them as unverified. RitsuLib's resolved profile keeps the selected
Ironclad placeholder for missing fields. Never add a static-merchant prefix patch: the scene
profile renders a real `NMerchantCharacter` directly.

Leave `Scenes.VisualsPath` unset for the generated combat body so the profile keeps its checked
missing-file fallback. When `images/charui/combat.png` exists, load it as `Texture2D` and call
`RitsuGodotNodeFactories.CreateFromResource<NCreatureVisuals>(texture, style)` from the protected
override, with `VisualNodeStyle.Empty.WithScale(0.80f)` followed by
`.WithPosition(new Vector2(0f, -184f))`; return `null` when the PNG is absent. The texture-only
`Scenes.VisualsPath` shortcut cannot carry that reviewed footprint transform.

## Bounded combat cues

The optional cue bundle is exactly Idle 4x250ms loop (the anchor breathing), Attack 9x60ms
one-shot then Idle, Hit 6x70ms one-shot then Idle, and Dead 5x170ms terminal final pose, all from
one generated sheet anchored on the static combat body, with Attack and Hit starting on the shared
anchor cell. All twenty-four transparent 512x512 frames share the static body's content box,
baseline, style, and the fixed Bounds/Intent/Center/Orb/Talk geometry from
`reference/character-combat-cues.md`. Set `AttackAnimDelay` to `0.30f` (five Attack frame times)
so damage lands on the strike frame.

Require every expected path and size before building one private `VisualCueSet`. Use `Idle/00` to
create the anchored combat visuals and pass that set directly to `ModAnimStateMachines.StandardCue`
from `SetupCustomCombatAnimationStateMachine`. Never set `CharacterAssetProfile.VisualCues`:
RitsuLib also uses that global fallback in merchant/rest playback. One missing or invalid frame
disables all cues, creates no playback node, and selects the static `combat.png`; if that is also
absent, return `null` for the resolved profile fallback.

## Checklist

- [ ] `ModCharacterTemplate<TCardPool,TRelicPool,TPotionPool>` with every abstract member; one
      content pack owns the Character, starters, every pool member, and supporting Powers; no
      BaseLib dependency, pool attribute, or manual registration.
- [ ] The non-Basic pool has at least `2 Attack / 2 Skill / 1 Power` before Shop, each a real Card.
- [ ] All 14 Character keys and the complete Architect dialogue use the normalized entry; selected
      Ancient groups pass `ancient_dialogue.py` and mount from a `has_pck=true` resource tree.
- [ ] Darv dialogue registers a Mod-local `CardRarity.Ancient` Dusty Tome candidate.
- [ ] One theme contract owns four colors, frame parameters, and distinct 256x256/24x24 Energy
      paths with literal Ironclad fallbacks.
- [ ] One 3% white-alpha rule derives the top icon and every generated Relic outline with no
      acquisition call.
- [ ] Selected combat cues use the fixed private four-action set with all-or-nothing fallback;
      `CharacterAssetProfile.VisualCues` stays unset.
- [ ] Locked/map/custom-Ancient/Cast/Spine/trail/arbitrary-material/multiplayer/audio boundaries
      stay explicit.

## Self-test driver body

Use the **`RunStart` + `CombatPlayer`** host (`reference/selftest-harness.md` § The `RunStart` +
`CombatPlayer` scenario). Set `plan.Character<CharacterName>()`: the kit locates the real
character-select button by model type, unlocks it only for proof setup, selects that exact model,
and waits for the run UI and local Player. Never match the `%Icon` texture path (placeholder art
keeps the fallback portrait) and never choose the first unlocked Character.

1. The roll call requires exactly one registered custom Character and logs its canonical HP, Gold,
   Energy, pools, and starters.
2. When custom selection art is selected, prove the 132x195 portrait and 1920x1200 background in
   the visible select UI. In every case assert the button lies inside the 1920x1080 viewport,
   capture a settled screenshot, and click Confirm.
3. In a `plan.RunStart` scenario (it runs before any combat), assert identity, exact HP/Max HP,
   Gold, all three exact typed pool types and member sets, every supporting Power, and exact
   starter deck/relic/potion multisets (`t.DeckCounts()`, `t.RelicNames()`). A non-starter pool
   Card never leaks into the starter deck. Give the starter Cards face checks.
4. Orobas mappings: grant the vanilla `ArchaicTooth` or `TouchOfOrobas` Relic in `RunStart` and
   assert the exact deck Card or Relic replacement, including a preserved upgrade. Headed review
   opens Orobas with `ancient OROBAS <TOUCH_OF_OROBAS|ARCHAIC_TOOTH>` and confirms the offer and
   its text name the Mod Card or Relic.
5. In a `plan.Combat(..., freshCombat: true)` scenario, assert native `MaxEnergy`, base Orb slots,
   and the hosted starter mechanic's independent state delta. When those profiles are selected,
   also assert all four theme colors, the frame shader target/brightness, the non-Spine 512x512
   body, normal and outlined 88x88 top-panel icons under one real `NTopBarPortrait`, one
   `NEnergyCounter` with all five 256x256 layers, a 256x256 large icon in a real hand
   `NCard.%EnergyIcon`, the distinct 24x24 path in a real formatted description, and every
   generated Relic's exact 256x256 main/outline pair under one real `NRelic`. For the body also
   assert alpha bounds within `(26,26)-(486,486)`, baseline `486`, scale `0.80`, position
   `(0,-184)`, screen bounds inside the viewport, and no overlap with top/bottom UI, the enemy
   lane, or the turn banner.
6. When combat cues are selected, prove Idle loops, Attack/Hit each return to Idle, shared
   geometry stays fixed, the first combat's playback node is freed, and a fresh combat's Dead
   sequence reaches and holds its last frame. Run the one-missing-frame fallback separately and
   require static combat with no playback node or frame flash.
7. When those profiles are selected, finish combat, enter RestSite and Shop, and assert the real
   `NRestSiteCharacter` / `NMerchantCharacter`, exact 512x512 resources, and settled screenshots.
8. Emit the final `character foundation/static-presentation ... observed=all` marker only after
   every assertion passes, followed by `selftest done` and a strict no-fresh-error check.

## Proof matrix

- Derive every expected identity, count, value, and terminal summary from the current `SPEC.md`;
  never reuse a retired proof Mod's constants or marker.
- The unlocked Card pool fills Shop's native colored Attack, Skill, and Power slots without falling
  back to another Character's pool.
- Assert the hosted mechanic's independent state delta.
- **Play every behavioral pool Card.** Pool assertions prove membership, not `OnPlay`. For each
  pool Card with its own `recipes/card.md` envelope, drive it and assert its concrete state delta
  in the same run.
- Secondary resources: derive only the selected definitions, uses, policies, and UI consumers;
  require bounded gain/payment, authoritative committed payoff, rejected nondestructive cases,
  live values, public UI attachment, and non-overlapping stable geometry for every visible
  consumer. Exercise a second combat or run-save boundary only when the selected persistence or
  turn-start policy requires it.
- Ordered semantic buffer: exact source/compile-Card result piles, visible order, capacity and
  overflow behavior, one generated-history entry, exact configured output/effect, `AttachedState`
  ownership, and a distinct empty state/UI in combat 2. Reject retained-Card, hidden-zone, and
  `skipVisuals` substitutions.
- The Character-wide theme asserts all four colors, shader parameters, distinct paths, exact
  256x256/24x24 textures, and both real consumers before emitting the theme marker. The visible
  appearance of Energy icons, theme, and cues remains a headed review.

## Manual fallback (only when the harness cannot reach its scenario)

Grant it: select the custom Character on the real character screen and click Confirm; no console
shortcut proves character-select presence. Trigger it: confirm SPEC HP, Gold, Energy, Orb slots,
and starter deck/relic/potions after run start; enter combat and observe the starter mechanic's
exact state delta. With combat cues, watch one full Idle loop, play an Attack, take one Hit, and
reach Dead; the first two return to Idle, Dead holds its last pose, and no anchor jumps.

## Advanced mechanic blocks

When `advanced mechanic` is not `none`, also record the matching block. Author it only when the
named capability has its own shipped reference; these fields never imply non-public access or a
patch target.

### Capability module

```markdown
- **capability module**: <family/name>
- **semantic host**: <real owner/event>
- **lifetime/reset/save**: <turn|combat|run; exact reset and persistence>
- **public surface**: <semantic context/listener used by domain code>
- **adapter route**: public-api | owned-adapter
- **adapter constraints**: <exact supported version and implementation-only limits>
- **multiplayer ordering**: <owner/local guard and deterministic order>
- **UI host/fallback**: <host, visibility, refresh, generic fallback>
- **conflict/failure**: <composition policy and fallback>
- **scenario/invariant**: <real host plus exact expected/observed state>
```

### Secondary resources

The selected fields lower to one or more framework-owned bounded resources, exact combat/run and
turn-start policies, declared payment planner/commit uses, and selected built-in or explicit UI
consumers (`reference/character-resource.md`). Implementation records belong in `MEMORY.md`.

```markdown
- **resources**: <stable id, min/default/max, combat|run persistence, turn-start policy>
- **uses**: <stable use id, Card, resource, required|optional|repeatable-extra,
  fixed|X amount, shortfall, replacement resource when selected, post-commit payoff>
- **UI consumers**: <resource, combat counter row|Card payment line, route, stable geometry>
- **owner**: local Player; native Energy remains separate
- **adapter route**: public registry/commands/payment planner selected after SPEC
- **observe**: only selected definitions, uses, rejection/commit, bounds, lifecycle, and UI
```

### Ordered semantic buffer

The block lowers to combat-attached semantic state (`reference/ordered-card-buffer.md`).
Implementation records belong in `MEMORY.md`.

```markdown
- **buffer**: <name>; owner local PlayerCombatState; lifetime combat
- **recorded value/order**: <semantic value from accepted cards>; append order <matters|not>
- **capacity/overflow**: <positive N>; reject without mutating current contents
- **source destination**: normal STS2 result pile, default Discard
- **visibility**: <compact player-readable state through a grounded UI host>
- **compile**: <trigger>; snapshot <ordered fields>; formula <deterministic expression>
- **output**: <real card + configured scaling values + exact effect>
- **observe**: exact source/compile-card destinations, order/capacity/overflow/UI,
  one CardGeneratedEntry, output state/effect, and distinct empty state in combat 2
```
