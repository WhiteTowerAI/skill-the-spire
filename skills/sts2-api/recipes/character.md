# Recipe: Character Foundation

> Live-proven on STS2 v0.107.1, BaseLib v3.3.5, and
> `Alchyr.Sts2.Templates` v2.5.0 by `CanaryCharacter` (2026-07-15).
> This recipe covers the M6 6b Foundation boundary only: a selectable character,
> valid pools and starters, run entry, HP/energy, and one public/BaseLib mechanic.
> It does not add a patch kernel, custom resource UI, custom zones, or dynamic content.

## Scaffold: use the character template

Run the character template, not the content template:

```bash
dotnet new alchyrsts2charmod -n <ModName> -M <Author>
```

It creates the character shell, `CustomCardPoolModel`, `CustomRelicPoolModel`,
`CustomPotionPoolModel`, character-scoped card/relic/potion bases, placeholder UI
images, and `characters.json`/`ancients.json`. Enable PckPacker in the csproj as
usual. Keep the outer work-directory name different from `<ModName>`.

## Registration: constructor-owned, exactly once

In BaseLib 3.3.5, `CustomCharacterModel()` calls:

```csharp
CustomContentDictionary.AddCharacter(this);
```

`PlaceholderCharacterModel` inherits that constructor. Therefore the generated
character class must not call `AddCharacter`, instantiate itself, or carry a manual
registration initializer. Model discovery constructs it and BaseLib adds it to
`ModelDb.AllCharacters`. Tier 2 requires exactly one instance of the generated type.

## Character shell

Keep the template's `PlaceholderCharacterModel` base until custom character art is
separately grounded. Fill identity, HP, starters, and all three pool references:

```csharp
using BaseLib.Abstracts;
using MegaCrit.Sts2.Core.Entities.Characters;
using MegaCrit.Sts2.Core.Models;

public sealed class <CharacterName> : PlaceholderCharacterModel
{
    public const string CharacterId = "<CharacterName>";

    public override CharacterGender Gender => CharacterGender.Neutral;
    public override int StartingHp => <HP>;

    public override IEnumerable<CardModel> StartingDeck =>
    [
        ModelDb.Card<<StarterCardA>>(),
        // Repeat the exact SPEC multiset.
        ModelDb.Card<<StarterCardB>>()
    ];

    public override IReadOnlyList<RelicModel> StartingRelics =>
    [
        ModelDb.Relic<<StarterRelic>>()
    ];

    public override CardPoolModel CardPool => ModelDb.CardPool<<ModName>CardPool>();
    public override RelicPoolModel RelicPool => ModelDb.RelicPool<<ModName>RelicPool>();
    public override PotionPoolModel PotionPool => ModelDb.PotionPool<<ModName>PotionPool>();
}
```

The template's inherited energy is the standard 3 per turn. Foundation supports that
standard value and proves it from the live `PlayerCombatState.MaxEnergy`; do not invent
an override name for a different energy design. A future exact nonstandard-energy
contract must be grounded before the pipeline advertises it.

## Pools and starter ecosystem

The character template already wires these bases:

- `<ModName>CardPool : CustomCardPoolModel`
- `<ModName>RelicPool : CustomRelicPoolModel`
- `<ModName>PotionPool : CustomPotionPoolModel`
- `[Pool(typeof(<ModName>CardPool))]` on the mod card base
- `[Pool(typeof(<ModName>RelicPool))]` on the mod relic base
- `[Pool(typeof(<ModName>PotionPool))]` on the mod potion base

Author concrete starter cards/relics with the existing `card.md` and `relic.md`
effect patterns, but keep the character template's pool attributes instead of changing
them to shared pools. A minimal Foundation slice also authors one concrete potion so
Tier 2 can prove that the potion pool resolves a real member. Requirements:

- starter cards use `CardRarity.Basic` and the deck contains the exact SPEC counts;
- the starter relic uses `RelicRarity.Starter` and is returned by `StartingRelics`;
- every `ModelDb.Card/Relic/Pool<T>()` reference resolves during run start;
- `CardPool.AllCards`, `RelicPool.AllRelics`, and `PotionPool.AllPotions` each contain
  the expected generated type(s);
- at least one starter card or starter relic has a real public/BaseLib behavior that
  `CombatPlayer` can drive and observe independently.
- before entering the native Shop, the unlocked non-Basic card pool must contain at least
  two eligible Attacks, two eligible Skills, and one eligible Power. The merchant owns
  exactly those five colored slots and excludes the first result before filling the second
  same-type slot; an undersized Character pool throws before the room UI appears. Author
  real Character cards for these slots rather than shipping no-op proof cards.

The live canary uses a starter relic with the already-grounded combat-start energy
pattern: `AfterSideTurnStart`, owner participant + turn-1 guards, then
`PlayerCmd.GainEnergy(1m, Owner)`. Its live proof is `MaxEnergy/Energy = 3/4`.

## Character localization: two tables

Use BaseLib's `CharacterLoc` for the 14 `characters` suffixes:

```csharp
public override List<(string, string)>? Localization => new CharacterLoc(
    "<title>",
    "<title object>",
    "<description>",
    "<object pronoun>",
    "<subject pronoun>",
    "<possessive pronoun>",
    "<possessive adjective>",
    "<aroma principle>",
    "<alive end-turn line>",
    "<dead end-turn line>",
    "<death-prevention line>",
    "<gold monologue>",
    "<cards modifier title>",
    "<cards modifier description>");
```

`CharacterLoc` emits `.title`, `.titleObject`, `.description`, the four pronoun/
possessive fields, `.aromaPrinciple`, both banter keys, `.eventDeathPrevention`,
`.goldMonologue`, `.cardsModifierTitle`, and `.cardsModifierDescription`.

The analyzer also requires these four flat keys in `ancients.json`, where
`<CHAR_ID>` is the character's final `Id.Entry`:

```json
{
  "THE_ARCHITECT.talk.<CHAR_ID>.0-0r.char": "<character line>",
  "THE_ARCHITECT.talk.<CHAR_ID>.0-0r.next": "<transition line>",
  "THE_ARCHITECT.talk.<CHAR_ID>.0-1r.ancient": "<Architect reply>",
  "THE_ARCHITECT.talk.<CHAR_ID>.0-attack": "<attack line>"
}
```

Missing any one is `STS001`. The canary's first build exposed this exact four-key set.

## Placeholder visual contract

Keep the character template's UI images and inherit `PlaceholderCharacterModel`.
It supplies built-in Ironclad creature, trail, energy counter, rest-site, merchant,
transition, audio, and hand assets. The template's `CustomIcon` and character-select/
map icon overrides provide distinguishable mod-owned placeholder PNGs. Do not block
Foundation on custom art or animation, and do not claim those built-in assets are custom.

## Static presentation expansion (M6)

Static Character art is an opt-in layer over the Foundation shell. Each getter has its
own consumer and its own checked fallback. The source-independent asset pipeline writes
these loose PNGs under `images/charui/`:

Read `reference/character-presentation.md` for the current promotion matrix. As of
2026-07-21, selection portrait/background, top-panel icon, static non-Spine combat/rest/
merchant bodies, five-layer full energy, and compact resource icon are live-proven.
Locked selection, map marker, and Ancient/Architect remain explicit gaps.

| getter/consumer | spec | size | fallback |
|---|---|---:|---|
| selection portrait | `CustomCharacterSelectIconPath` | 132x195 | inherited portrait |
| locked selection portrait | `CustomCharacterSelectLockedIconPath` | 132x195 | inherited locked portrait |
| top-panel icon | `CustomIconTexturePath` | 88x88 | inherited top-panel icon |
| map marker | `CustomMapMarkerPath` | 49x64 | inherited map marker |
| select background | `CustomCharacterSelectBg` | 1920x1200 | inherited select scene |
| static combat body | `CreateCustomVisuals()` | 512x512 | inherited creature scene |
| static rest-site body | `CustomRestSiteAnimPath` | 512x512 | inherited rest-site scene |
| static merchant body | `CustomMerchantAnimPath` | 512x512 | inherited merchant scene |
| energy counter layers | `CustomEnergyCounter` | five 256x256 PNGs | inherited energy scene |
| compact energy icon | card-pool `TextEnergyIconPath` | 24x24 | template icon |

Selection/background files are opaque and use `fit: cover`; icon, marker, static-body,
and energy files use `fit: contain` with the explicit magenta chroma-key import. A static
body is not a Spine contract: leave `SetupCustomAnimationStates` null and retain the
fallback for attack, hurt, cast, death, phobia, multiplayer, and animated transitions.

`NCreatureVisualsFactory` accepts the checked combat PNG directly when
`CreateCustomVisuals()` returns it. Background, rest-site, and merchant use the minimal raw
`.tscn` wrappers from `reference/character-presentation.md`; `build.py` packs them without
Godot/MegaDot. Merchant additionally selects the exact version-gated
`NMerchantCharacter._Ready()` prefix and gates its getter on successful installation.
Full energy overrides `CustomEnergyCounter` with five checked loose PNGs and does not use a
scene. Every missing asset or failed patch retains the inherited template consumer.

### Ancient opening and Architect boundary

Character localization must include the four `THE_ARCHITECT.talk.<CHAR_ID>` keys listed
above. The opening banner is not a normal Event label: the game creates a fixed vanilla
`NAncientNameBanner` and its `RichTextAncientBanner` from `AncientEventModel.Title` and
`AncientEventModel.Epithet`. Architect speech uses the character's
`SpeechBubbleColor`; player attack presentation consumes `GetArchitectAttackVfx()`.
This phase may research and prove those native consumers, but it does not authorize a
custom Ancient layout or arbitrary Architect scene. A headed proof must identify the
banner/dialogue and keep the static character fallback honest. The M6 research inventory
is complete; native custom-Character support remains unverified until that headed proof.

## Static Character checklist

- [ ] each requested getter has a matching `character_*` spec and explicit fallback
- [ ] generated PNGs pass `gen_sprite.py import` at the exact profile size
- [ ] scene wrappers contain only grounded BaseLib nodes and are registered by the matching getter
- [ ] selection/background, combat, rest, merchant, and energy consumers render the custom resource in a headed run
- [ ] unlocked non-Basic pool has at least 2 Attack, 2 Skill, and 1 Power before Shop proof
- [ ] static merchant prefix resolves exact version/MVID/target and its getter falls back on failure
- [ ] Ancient banner/Architect dialogue is tested through the real Ancient host, not a normal Event surrogate
- [ ] no Spine, transition material, trail, phobia, remote-hand, or arbitrary Ancient-layout claim is made

## Tier 2: `RunStart` + `CombatPlayer`

Start from `reference/selftest-harness.md`, then use its Character Foundation variant.
The proof is one ordered vertical slice:

1. On the real character-select screen, assert one canonical custom character exists.
2. Find its real `NCharacterSelectButton` by `%Icon` texture resource path, normalizing
   both `\\` and `/`; never pick the first unlocked character.
3. Select it and click the real Confirm button.
4. Wait for `IsInProgress`, then `NRun.Instance?.GlobalUi != null` before calling
   `LocalContext.GetMe`; the run-state flag becomes true before the local player/UI bind.
5. Assert runtime character identity, current/max HP, all three pool types and member
   models, exact deck multiset, and exact starter relic multiset.
6. Enter a minimal combat and wait for `PlayerTurnPhase.Play`.
7. Assert the designed `MaxEnergy` and the independent hosted mechanic state delta.
8. If static rest/merchant presentation is selected, finish combat and enter real RestSite
   and Shop rooms; assert the exact textures and the static-merchant patch status.
9. Emit a final structured proof only after every assertion passes, for example:
   `character foundation complete expected=all observed=all`.

The trigger log (`TrailMarker fired`, card played, and so on) is diagnostic only.
`grep_log.py` accepts the structured post-state proof plus the exact load and terminal
markers.

## Checklist

- [ ] scaffolded with `alchyrsts2charmod`; PckPacker enabled
- [ ] extends `PlaceholderCharacterModel`
- [ ] no manual `AddCharacter`, no self-instantiation
- [ ] exact HP and standard 3 energy recorded in SPEC
- [ ] custom card/relic/potion pools resolve and contain expected types
- [ ] starter deck/relic use exact SPEC counts and rarities
- [ ] card pool can fill the native Shop's 2 Attack / 2 Skill / 1 Power colored slots
- [ ] all 14 `CharacterLoc` values plus four Architect keys supplied
- [ ] real character-select button located and clicked
- [ ] RunStart asserts identity/HP/pools/starters
- [ ] CombatPlayer asserts `MaxEnergy` and one public/BaseLib mechanic delta
- [ ] build 0 warnings / 0 errors, Tier 1 PASS, Tier 2 PASS
