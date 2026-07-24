# Recipe: Character Foundation

> Live-proven on STS2 stable `0.107.1` with RitsuLib `0.4.62` by the
> 2026-07-23 Wayfinder R4 proof. This recipe covers exactly-once registration,
> typed pools, starters, localization, run entry, one hosted starter mechanic,
> and the eight promoted static presentation profiles. Selected R5 resource/buffer/UI
> capability details live in `reference/character-resource.md` and
> `reference/ordered-card-buffer.md`; this Foundation recipe does not duplicate them or
> promote Ancient, animation, materials, multiplayer presentation, or audio.

Read `reference/ritsulib-adapter.md` first. When static art is selected, also
read `reference/character-presentation.md` and `reference/art-contract.md`.

## Registration and model shell

Use the pinned open-mod scaffold. Do not invoke an Alchyr/BaseLib character
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
    public override Color NameColor => new("<hex>");
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

The inherited combat energy is the normal `3`. Foundation may prove a separate
starter mechanic such as one turn-1 Energy gain, but must not replace native
Energy or invent an alternative-energy hook.

## Typed pools and starter ecosystem

Use RitsuLib's public pool models:

```csharp
public sealed class <CardPool> : TypeListCardPoolModel
{
    public override string Title => "<Character> Cards";
    public override string EnergyColorName => "<color>";
    public override Color DeckEntryCardColor => new("<hex>");
    public override bool IsColorless => false;
}

public sealed class <RelicPool> : TypeListRelicPoolModel
{
    public override string EnergyColorName => "<color>";
}

public sealed class <PotionPool> : TypeListPotionPoolModel
{
    public override string EnergyColorName => "<color>";
}
```

Register every concrete member with its pool generic. Starter cards are
`CardRarity.Basic`; the starter relic is `RelicRarity.Starter`. Before entering a
native Shop, the unlocked non-Basic pool must contain at least two eligible
Attacks, two eligible Skills, and one eligible Power. The merchant excludes the
first same-type result while filling the second slot, so a `1/1/1` pool throws
before the Shop UI exists. Author real effect cards for all five slots.

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

Also ship these four `ancients.json` keys even though native custom-Character
Ancient presentation remains unverified:

```text
THE_ARCHITECT.talk.<CHAR_ID>.0-0r.char
THE_ARCHITECT.talk.<CHAR_ID>.0-0r.next
THE_ARCHITECT.talk.<CHAR_ID>.0-1r.ancient
THE_ARCHITECT.talk.<CHAR_ID>.0-attack
```

## Static presentation

Put the promoted paths in one `CharacterAssetProfile`:

| consumer | profile field | exact asset |
|---|---|---|
| selection portrait | `Ui.CharacterSelectIconPath` | 132x195 PNG |
| selection background | `Ui.CharacterSelectBgPath` | raw `.tscn` wrapping 1920x1200 PNG |
| top-panel identity | both `Ui.IconTexturePath` and `Ui.IconPath` | 88x88 PNG |
| combat body | `Scenes.VisualsPath` | 512x512 PNG; RitsuLib builds `NCreatureVisuals` |
| RestSite body | `Scenes.RestSiteAnimPath` | raw `.tscn` wrapping 512x512 PNG |
| Shop body | `Scenes.MerchantAnimPath` | raw `.tscn` wrapping 512x512 PNG |
| full energy | `Scenes.EnergyCounterPath` | raw `.tscn` using five 256x256 PNGs |
| compact card energy | card-pool `BigEnergyIconPath` and `TextEnergyIconPath` | checked 24x24 PNG |

Locked selection and map marker paths may retain checked assets, but they are not
pipeline-promoted until their real consumers are visibly proved. RitsuLib's
resolved profile keeps the placeholder/native fallback for missing fields. Do not
add the historical static-merchant prefix: the R4 Shop proof rendered a real
`NMerchantCharacter` directly from the RitsuLib scene profile.

## Ancient boundary

The public Character abstract members include `NameColor`, animation delays, and
`GetArchitectAttackVfx()`. Supplying them and the four localization keys is a
compile/localization requirement, not an Ancient presentation proof. Do not drive
the initial Ancient merely to make the Foundation map load; the R4 harness used the
public test API to initialize act 0 and left `NAncientNameBanner`, Architect
dialogue, speech color, and custom Ancient layouts unclaimed.

## Tier 2: selection + RunStart + CombatPlayer + world consumers

1. Require exactly one registered custom Character.
2. On the real character-select screen, locate its button by normalized `%Icon`
   texture path, unlock only for proof setup, and select that exact model. Never
   choose the first unlocked character.
3. Prove the 132x195 portrait and 1920x1200 background in the visible select UI,
   capture a settled screenshot, and click Confirm.
4. After `NRun.GlobalUi` is ready, assert selected identity, exact HP/Max HP,
   starting Gold, all three exact typed pool types/member sets, every independently
   registered supporting Power, and exact starter deck/relic multisets.
5. Enter a real combat, wait for `PlayerTurnPhase.Play`, and assert native
   `MaxEnergy`, the hosted starter mechanic, the non-Spine 512x512 body, 88x88
   top-panel icon, one `NEnergyCounter`, all five 256x256 layers, and a visible
   24x24 icon in a real hand `NCard`.
6. Finish combat, enter RestSite and Shop, and assert the real
   `NRestSiteCharacter` / `NMerchantCharacter`, exact 512x512 resources, and
   settled screenshots.
7. Emit the final `character foundation/static-presentation ... observed=all`
   marker only after every assertion passes, followed by `selftest done` and a
   strict no-fresh-error check.

The 2026-07-23 RitsuLib-only Wayfinder proof observed exactly one selected model,
HP `72/72`, Gold `99`, exact pools `cards7/relic1/potion1/power1`, starter deck
`5 Strike + 5 Guard`, one Compass, Energy `3/4`, and every promoted static
consumer above. It built with zero warnings/errors against the pinned profile and
passed strict Tier 2 with no fresh error.

## Checklist

- [ ] `ModCharacterTemplate<TCardPool,TRelicPool,TPotionPool>` and all abstract members compile
- [ ] one content pack owns Character, starters, every pool member, and supporting Power
- [ ] no BaseLib namespace/package/manifest dependency, pool attribute, or manual registration
- [ ] exact HP/Gold/pool member sets/starter multisets are asserted
- [ ] non-Basic pool has at least `2 Attack / 2 Skill / 1 Power` before Shop
- [ ] all 14 Character keys and four Architect keys use the normalized Character entry
- [ ] every selected static asset renders in its real consumer with a screenshot and state proof
- [ ] locked/map/Ancient/animation/material/multiplayer/audio boundaries remain explicit
- [ ] strict Tier 1/Tier 2, `selftest done`, and no fresh error pass on the pinned profile
