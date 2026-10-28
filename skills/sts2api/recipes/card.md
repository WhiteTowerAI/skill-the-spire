# Recipe: Card

Everything one new Card needs: the SPEC fields, the class, its text, and its proof. Read
`reference/mechanics.md` first (DynamicVars, SmartFormat, enums) and
`reference/vanilla-text-style.md` for every string. The skill fills only the effect logic;
`ModCardTemplate`, content-pack registration, localization keys, and `CardAssetProfile` follow
the fixed shapes below.

Also read, only when SPEC selects it:

- calculated values, Energy/Star icon counts, typed computed Power amounts, or variable
  tooltips: `reference/card-computed-values.md`;
- a filtered live-creature target: `reference/advanced-targeting.md`;
- hand emphasis: `reference/card-hand-emphasis.md`;
- extra colored words beyond the default style: `reference/content-text-effects.md`;
- a raw hook rule: `reference/model-hook-participation.md`; bounded state:
  `reference/stateful-mechanics.md`;
- rarity `Ancient`: `reference/ancient-card.md` (acquisition, pool, full-card art).

Vanilla Cards to imitate: `StrikeIronclad` (single-target attack), `DefendIronclad` (self
Block), `Inflame` (gain a Power), `Bash` (attack plus a debuff).

**Scope: a new Card.** Editing an existing vanilla Card starts at
`reference/vanilla-overrides.md` and `reference/vanilla-card-overrides.md`; fresh unlock gates
or pool membership use `reference/vanilla-availability-overrides.md`. Reuse this recipe there
only for the effect commands a promoted override route selects.

## When to use

The request is a **Card** when the player **plays it from hand for an Energy cost** during
combat, not a passive item they own (Relic) or a one-shot consumable (Potion): "a card
that…", "an attack that…", "a skill that gives…", "a power that…", "costs 1 energy and…". Its
effect runs in `OnPlay`, and its numbers scale (Strength, upgrades), so it uses `DynamicVar`s
and SmartFormat rather than literal amounts. Energy and Stars are independent native
payments: fixed or X Energy, and no, fixed, or X Stars, except that Energy-X with Star-X is
blocked.

The bounded forced-follow-up Quest token is the one exception: an unplayable dependency of an
Event composition. Route it to `reference/forced-followup-event.md`; it gets no `OnPlay`.

## SPEC fields

```markdown
# SPEC — <Mod Name>

- **mod id**: <stable mod identity>
- **author**: <author>
- **content**:
  - name: <shown name>
  - surface: card
  - logical id: <stable local stem, e.g. blade_dance>
  - kind: Attack | Skill | Power
  - rarity: Basic | Common | Uncommon | Rare | Ancient
  - relations: <none | custom power/keyword/enchantment/orb dependencies>
  - keywords: none | <keyword name> — <the shared rule its tooltip states>
    native or mod: native | mod
    behavior owner: <the element that implements the rule>
  - enchantment: none | <name> — <what it adds to this card>
    amount: <value and bounds>
    host restriction: <which cards may legally carry it>
    stacking: replaces an existing enchantment | not stackable
- **registration**:
  - availability: shared | character:<name>
  - ownership: player
  - placement: <plain-language card-pool rule>
- **localization**:
  - languages: [eng, zhs]
  - fields: title=<shown name>; description=<hover text>; optional selection prompt
  - formatting: vanilla text style (`reference/vanilla-text-style.md`); dynamic value placeholders
  - extra emphasis: none | <description phrase -> color the default style would not apply>
  - hover tips: none | <each Power, keyword, Orb, or Card the description names>
  - variable tooltips: none | <value name -> localized title; description; optional icon>
  - engine-composed text: none | <each native keyword, mod keyword, or enchantment
    `extraCardText` the engine appends to this card's rendered description>
- **multiplayer**: both | multiplayer only | singleplayer only (§ Multiplayer; default both)
- **effects**:
  - trigger: play
  - target: one enemy | all enemies | self | another player | every player
  - advanced target: none | see `reference/advanced-targeting.md`
  - native costs:
    - energy: fixed <nonnegative integer> | X
      upgrade: same | fixed delta <integer>
    - stars: none | fixed <nonnegative integer> | X
      upgrade: same | fixed delta <integer>
    - payment/UI: native
  - sequence: <ordered game-term effect with exact values>
  - scaling: <named base values, e.g. damage 6; block 5; strength 2>
  - upgrade: <named value deltas, e.g. damage +3>
  - calculated values: none | one or more
    - <name>: role <plain | damage | block | Energy icons | Star icons | raw typed Power |
      applied typed Power>; formula <one deterministic expression>; inputs <complete list>;
      domain <integer [min,max]>; upgrade <same | exact change>; evaluation <before play |
      after normal payment and move>
- **hook participation**: none | one or more; see § Hook participation below
- **state**: none | see `reference/stateful-mechanics.md`
- **owned Rest Site option**: none | one
  - owner: card
  - owner multiplicity: exactly one in the owner's deck
  - title: <localized button title>
  - description: <localized hover description>
  - eligibility: <when this exact Card contributes the option>
  - repeatability: once per Rest Site | once per run
  - state handle: host visit removal | saved owner bool
  - enabled rule: always | can pay fixed Gold cost
  - cost: free | <nonnegative integer> Gold
  - outcome: <ordered deterministic preflightable operations>
  - after success: leave | keep remaining options available
  - icon: checked native fallback | generate
  - multiplayer: both
- **presentation**:
  - assets: card portrait; placeholder | generate
  - art source: host-tool | backend:<name> | local-image (generate only)
  - native presentation: standard card body/preview
  - hand emphasis: none | one or more ordered rules
    - rule: <stable local rule name; repeat in precedence order>
      meaning: <actionable bonus, warning, or other player-facing state>
      condition: <plain-language active rule>
      color: gold | red | custom <plain color>
      priority: <integer; highest active rule wins>
      while unplayable: show | hide
- **fallback**:
  - missing asset: checked template card portrait
  - unavailable seam: preserve behavior or stop with an explicit unsupported boundary
- **proof**:
  - scenario: CombatPlayer
  - driver: play the real card against its declared target
  - invariants: <exact expected/observed state, result pile, and dependent effects>
  - boundary cases: <upgrade/state/relationship cases; for calculated values include
    zero/positive/changing input, domain bounds, base/upgrade, normal modifiers, final
    preview vs effect result, icon reflow, and variable tooltip; or none>
- **adapter output** (written to MEMORY after acceptance): resolved content id,
  localization keys, asset profile, and framework diagnostic record
```

## Card types

`CardType` (`Entities.Cards`, `mechanics.md` §3): **`Attack`** deals damage, **`Skill`** is
Block or another non-attack effect, **`Power`** is a permanent buff played once.
`Status`/`Curse`/`Quest` are not for a normal custom Card; the only Quest exception is the
token in `reference/forced-followup-event.md`.

## Registration and asset profile

Add the Card exactly once to the scaffold's `MainFile.RegisterContent()` partial hook in
`MainFile.Content.cs`. The pool generic is the availability contract; never add a pool
attribute or a second registration path:

```csharp
RitsuLibFramework.CreateContentPack(ModId)
    .Card<ColorlessCardPool, Cards.<CardName>>()
    .Apply();
```

Custom art uses an explicit profile; omit the override for the placeholder. Empty fields keep
the template/base-game fallback, and custom art never blocks the pipeline. The normal portrait
import is `1000×760` (`reference/art-contract.md`); an Ancient-rarity Card imports `606×852`
full-card art with `--spec card_ancient`.

```csharp
public override CardAssetProfile AssetProfile => new()
{
    PortraitPath = "res://<ModName>/images/card_portraits/<slug>.png",
};
```

## The skeleton (fill only the marked spots)

Add one file `<ModName>Code/Cards/<CardName>.cs`:

```csharp
using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Commands;                    // DamageCmd, CreatureCmd, PowerCmd
using MegaCrit.Sts2.Core.Entities.Cards;              // CardType, CardRarity, TargetType, CardTag
using MegaCrit.Sts2.Core.GameActions.Multiplayer;     // PlayerChoiceContext
using MegaCrit.Sts2.Core.Localization.DynamicVars;    // DamageVar, BlockVar, PowerVar
using MegaCrit.Sts2.Core.ValueProps;                  // ValueProp
using STS2RitsuLib.Scaffolding.Content;                // ModCardTemplate, CardAssetProfile

namespace <ModName>.Cards;

public sealed class <CardName> : ModCardTemplate
{
    // Optional native Star payment selected by SPEC:
    // public override int CanonicalStarCost => 2;
    // public override bool HasStarCostX => true; // use instead of CanonicalStarCost for Star-X

    // Numbers that scale (upgrades/Strength). Pick the vars the effect needs:
    protected override IEnumerable<DynamicVar> CanonicalVars => new DynamicVar[]
    {
        new DamageVar(6m, ValueProp.Move),            // attack damage  → DynamicVars.Damage
        // new BlockVar(5m, ValueProp.Move),          // block          → DynamicVars.Block
        // new PowerVar<StrengthPower>(2m),           // a power amount → DynamicVars["StrengthPower"]
    };

    // Optional: category tags (e.g. CardTag.Strike so "for each Strike" cards count it):
    // protected override HashSet<CardTag> CanonicalTags => new() { CardTag.Strike };

    public <CardName>()
        : base(1, CardType.Attack, CardRarity.Common, TargetType.AnyEnemy)   // cost, type, rarity, target
    {
    }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        // ─────────── EFFECT LOGIC — the ONLY part the skill writes ───────────
        // (Lower SPEC's effects.sequence through reference/effect-primitives.md.)
        // ─────────────────────────────────────────────────────────────────────

        MainFile.Logger.Info("[T2MOD-SELFTEST] <CardName> played: <what happened>");
    }

    protected override void OnUpgrade()
    {
        base.DynamicVars.Damage.UpgradeValueBy(3m);   // bump the var(s) the upgrade improves
    }
}
```

## The constructor arguments (all required, passed to `base(...)`)

| Arg | Type | Pick by |
|---|---|---|
| `cost` | `int` | Energy cost from SPEC (0/1/2/3…); `-1` for Energy-X. |
| `type` | `CardType` | deals damage → `Attack`; Block/utility → `Skill`; permanent buff → `Power`. |
| `rarity` | `CardRarity` | droppable default `Common`; `Basic` for starter Cards; `Ancient` only through `reference/ancient-card.md`. |
| `target` | `TargetType` | one enemy → **`AnyEnemy`**; all enemies → `AllEnemies`; self or no selection (Block, gain Strength) → **`Self`**; another player → `AnyAlly`; every player, you included → `AllAllies` (§ Multiplayer). |

A Card that targets the player uses `TargetType.Self`, never `AnyPlayer`: that one is for
Potions (`DefendIronclad` and `Inflame` use `Self`).

## Native Energy and Star costs

The first constructor argument is the native Energy cost: a nonnegative integer, or `-1` for
Energy-X together with `protected override bool HasEnergyCostX => true`. Never encode X as a
large integer or a DynamicVar. Star cost is independent:

```csharp
public override int CanonicalStarCost => 2;       // fixed Stars; omit for none
// OR:
public override bool HasStarCostX => true;        // Star-X; do not also set a fixed Star cost

protected override void OnUpgrade()
{
    UpgradeStarCostBy(-1);                        // fixed Star cost only
}
```

Use `UpgradeStarCostBy` only for a fixed Star cost; the host throws on Star-X. Energy upgrades
use `EnergyCost.UpgradeBy(...)`. Keep both on the native `CardModel` lifecycle so
playability, cost UI, payment, auto-play, cloning, and replay see the same declarations.
Never create a parallel Star store or spend Stars inside `OnPlay`.

Reject simultaneous Energy-X and Star-X; every other Energy/Star combination is authorable.
Payment rejection must leave both resources, Card state, and effect state unchanged.

## OnPlay and the effect sequence

`OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)` runs when the Card is played
and holds the whole effect. It supplies `choiceContext`, the owner Player `base.Owner`, its
Creature `base.Owner.Creature`, the Card source `this`, and `cardPlay`. A targeted Card
null-checks `cardPlay.Target` with `ArgumentNullException.ThrowIfNull`; a multi-target Card
uses only the resolved list from `reference/advanced-targeting.md` (it gates zero candidates
through `IsPlayable`, executes once with `null`, and calls `GetTargets()` inside `OnPlay`;
never cache the selection-time list). Never substitute another Player/Creature or turn a
missing target into an all-enemy effect. `OnTurnEndInHand` ("if this is in your hand at end
of turn") and `IsPlayable` exist for SPECs that demand them.

Lower every ordinary command in `effects.sequence` through `reference/effect-primitives.md`
and await each in SPEC order, preserving `this`/`cardPlay` provenance. Read static numbers
from their `DynamicVars`. Keep `GainsBlock => true` for a Card that gains Block and pass
`cardPlay` to `GainBlock`; use `WithHitCount(n)` rather than a loop for a multi-hit attack.
When no vanilla Power fits, author the custom one first through `recipes/power.md` and
register it once with `.Power<T>()`.

### Calculated values, icon counts, and variable tooltips

Follow `reference/card-computed-values.md` completely. In short:

- for each declared value, one pure bounded calculation shared by base/upgrade preview and
  execution, with a unique name on that Card;
- `ComputedDamage`/`ComputedBlock` when normal combat modifiers apply, plain `Computed` only
  when they intentionally do not, and the typed Energy/Stars/Power helper for those roles;
- execute through `ComputeDynamicValue`, `ComputeEnergyValue`, `ComputeStarsValue`, or
  `ComputePowerValue<T>`, then pass the raw result to the normal Cmd exactly once. Never
  execute from `BaseValue` or the display-only `PreviewValue`;
- `{EnergyGain:energyIcons()}` and `{StarGain:starIcons()}` in text; and
- `.WithSharedTooltip(...)` only when SPEC supplies the `static_hover_tips` title/description.

If payment or the normal Hand-to-Play move changes a formula input, the helper must make
preview and execution observe SPEC's declared evaluation point. Stop authoring when that cannot
be done deterministically.

## DynamicVars, upgrade, and description (`reference/mechanics.md` §1–2)

Cards declare static numbers in `CanonicalVars` and read them through typed accessors:

- `new DamageVar(6m, ValueProp.Move)` → `base.DynamicVars.Damage.BaseValue`
- `new BlockVar(5m, ValueProp.Move)` → `base.DynamicVars.Block.BaseValue`
- `new PowerVar<StrengthPower>(2m)` → `base.DynamicVars["StrengthPower"].BaseValue`
  (a power var's key is the Power's class name)

The upgrade bumps vars in `OnUpgrade()`:

```csharp
protected override void OnUpgrade()
{
    base.DynamicVars.Damage.UpgradeValueBy(3m);
    // base.EnergyCost.UpgradeBy(-1);  // when SPEC lowers a fixed Energy-cost upgrade
    // UpgradeStarCostBy(-1);         // when SPEC lowers a fixed Star-cost upgrade
    // base.DynamicVars["VulnerablePower"].UpgradeValueBy(1m);   // each var the upgrade changes
}
```

**There is no separate upgraded-description key.** The upgraded name is generated (`title` +
`+N`), and the same description re-renders through SmartFormat, so write each number as a
`:diff()` placeholder and it turns green after upgrade:
`"Deal {Damage:diff()} damage.\nApply {VulnerablePower:diff()} [gold]Vulnerable[/gold]."`.
Use `{X:showIfUpgraded()}` for upgraded-only text (`mechanics.md` §2).

## Hook participation: a rule that holds without being played

A SPEC `hook participation` block is a rule the Card contributes while merely present: the
engine asks it for a number or decision while resolving something else. Follow
`reference/model-hook-participation.md`. A Card reaches the widest set (66 of 68), but
`CardModel` receives combat hooks only while it sits in a combat pile:

```csharp
public override bool ShouldReceiveCombatHooks => Pile?.IsCombatPile ?? false;   // pinned engine
```

A deck Card always receives run-scope hooks, so a "while this is in your deck" rule works from
the deck, but a combat-scope declaration on a Card outside the piles never fires. Put a rule
that must hold all combat long on a Relic or a Power. `Owner` is a `Player`; guard against
`Owner.Creature`, and `Owner.Osty` where an Osty can act. An Enchantment on this Card inherits
the same pile-dependent reachability and uses its five `Enchant*` replacements
(`recipes/enchantment.md`).

## Optional routes

Keep an ordinary play effect in `effects.sequence`. Read a route only when SPEC selects it,
append only that reference's SPEC block, and for each one name the owner, phase/order, guard and neutral case, state lifetime, cleanup, and
exact SelfTest post-state:

- a separable behavior/state bundle: `reference/model-capabilities.md`;
- state across a turn/combat/run/save boundary, or gameplay randomness:
  `reference/lifecycle-state-rng.md`;
- per-hit attack, healing, Energy/Stars-gain response, or maximum hand size:
  `reference/shared-effect-hooks.md`;
- before/after `OnPlay`, suppression, free-play duration, transforms, carry-over, or type
  text: `reference/card-play-lifecycle.md` (do not copy it into `OnPlay` or refund a free play
  manually);
- a right-click action: `reference/model-right-click.md`;
- a Card-owned Rest Site action: `reference/rest-site-options.md`. Require exactly one
  matching concrete Card in the owner's deck, keep that instance as option/state owner,
  contribute through `TryModifyRestSiteOptions`, and use `SavedAttachedState<SpecificCard,bool>`
  only for once-per-run state. Never use canonical Cards, duplicate ids, or raw hook
  participation to bypass the transaction.

A process-wide registration belongs only to an explicit Global Effect.

### Hand emphasis

Never put visual-node code in the Card. For one non-competing gold/red rule, override the
native `ShouldGlowGoldInternal` or `ShouldGlowRedInternal`. For several rules or any custom
color, append exactly one typed `.CardHandOutline<TCard>(...)` step to the same builder and emit
every `ModCardHandOutlineSwitchRule<TCard>.Fixed(...)` in SPEC order; the highest active
priority wins and a tie uses the later rule. Use the reference's `visibleWhenUnplayable`
mapping and keep `RefreshEveryFrame: false`. Never mix the native and custom-outline routes,
register after `.Apply()`, retain a Card instance, or poll UI state. Stop if the condition can
change without a normal combat-state refresh.

## Localization (ships in the .pck)

Table **`cards`**, with the same keys in `<ModName>/localization/eng/cards.json` and
`zhs/cards.json`. Keys are flat and use the exact RitsuLib public entry `MOD_CARD_TYPENAME`:

```json
{
  "<MOD>_CARD_<TYPE>.title": "Display Name",
  "<MOD>_CARD_<TYPE>.description": "Deal {Damage:diff()} damage.\nApply {VulnerablePower:diff()} [gold]Vulnerable[/gold].",
  "<MOD>_CARD_<TYPE>.selectionScreenPrompt": "Choose a card to put into your [gold]Hand[/gold]."
}
```

```json
{
  "<MOD>_CARD_<TYPE>.title": "显示名称",
  "<MOD>_CARD_<TYPE>.description": "造成{Damage:diff()}点伤害。\n给予{VulnerablePower:diff()}层[gold]易伤[/gold]。",
  "<MOD>_CARD_<TYPE>.selectionScreenPrompt": "选择一张牌加入你的[gold]手牌[/gold]。"
}
```

Emit `selectionScreenPrompt` only when the Card asks the player to choose; Cards have no
`.flavor`. `{Damage}`/`{Block}` resolve from the matching `DynamicVar`, a power var from its
class name (`{StrengthPower}`). Write every value in the vanilla style: glossary terms with
their exact `eng`/`zhs` names in `[gold]`, one effect per line, uncolored `:diff()` numbers,
Energy as `{Energy:energyIcons()}`, and Chinese full-width punctuation with the vanilla
measure word (点/层/张) and no spaces. A declared variable tooltip adds flat `.title` and
`.description` entries to both languages' `static_hover_tips.json`
(`reference/card-computed-values.md`).

Only when SPEC selects `extra emphasis`, read `reference/content-text-effects.md`: Card
descriptions may add balanced `gold`, `purple`, and `blue` spans; `:diff()` keeps its own
green/red highlight.

### Hover tips for named terms

When the description names a Power, keyword, Orb, or Card that is not one of this Card's own
keywords, declare its tip as vanilla does (`Bash` shows Vulnerable, `Blade Dance` shows Shiv);
`reference/vanilla-text-style.md` § Hover tips for named terms lists each factory:

```csharp
using MegaCrit.Sts2.Core.HoverTips;

protected override IEnumerable<IHoverTip> AdditionalHoverTips =>
    [HoverTipFactory.FromPower<VulnerablePower>()];
```

## ID / loc-key derivation

RitsuLib derives `Id.Entry` as `MOD_CATEGORY_TYPENAME`, each segment in uppercase snake case:
Mod id `BladeDance` with Card class `BladeDance` becomes `BLADE_DANCE_CARD_BLADE_DANCE`. Use
that exact stem in `cards.json`. To keep a published identity across a type rename, pass
`ModelPublicEntryOptions.FromStem(...)` to the Card registration; never add a second id rule.

## Custom Card tags

A tag is a mechanical category with no text or icon, like vanilla `CardTag.Strike`, that other
effects count ("for each Echo card in your hand"). Use a Keyword instead when the player must
read it on the Card. Register each Mod tag once on the same content pack before `.Apply()`
(registration freezes at `ModelDb.Init`):

```csharp
using STS2RitsuLib.CardTags;

    .CardTagOwned("echo")
```

The qualified id is `MOD_CARDTAG_STEM`, e.g. `EXAMPLE_MOD_CARDTAG_ECHO`. Resolve it with
`GetModCardTag()` in the canonical set of every Mod Card that carries it:

```csharp
public const string EchoTagId = "<MOD>_CARDTAG_<STEM>";

protected override HashSet<CardTag> CanonicalTags => new() { EchoTagId.GetModCardTag() };
```

Test membership with `card.Tags.Contains(EchoTagId.GetModCardTag())`. To tag a vanilla Card,
use the `card.property.tags` append route in `reference/vanilla-card-overrides.md`. Never call
`AddModCardTag`/`RemoveModCardTag` on a live Card: the set is shared with clones, unsaved, and
read-only once a capability contributes tags. A tag that changes during a run is Mod-owned
state read by the effect that tests it. Tier 2 asserts that the registered tag resolves, that
the canonical Card and a new mutable copy both contain it, and that the counting effect
produces the expected amount in `CombatPlayer`.

## Rarity and pool

`CardRarity` (`mechanics.md` §3): `Basic` (starters), `Common` (default), `Uncommon`, `Rare`.
The pool is the first generic argument of `.Card<TPool,TCard>()`
(`MegaCrit.Sts2.Core.Models.CardPools`):

- **`ColorlessCardPool`**: any Character can find it, the default (like `SharedRelicPool`). The
  pool's `Title` feeds the frame color, so a colorless Card gets the grey frame.
- `IroncladCardPool`, `SilentCardPool`, `DefectCardPool`, `RegentCardPool`,
  `NecrobinderCardPool`: one Character's pool.

## Pre-flight checklist

- [ ] `public sealed` class extending `ModCardTemplate`, registered exactly once with
      `.Card<TPool,TCard>()` in `MainFile.Content.cs`.
- [ ] Constructor passes `cost, CardType, CardRarity, TargetType`; `TargetType` matches the
      effect (`AnyEnemy`, `Self` not `AnyPlayer`, `AllEnemies`, `AnyAlly`, `AllAllies`).
- [ ] An `AnyAlly` Card, or one whose effect needs a teammate, overrides
      `MultiplayerConstraint => CardMultiplayerConstraint.MultiplayerOnly`; effects reach
      players through `cardPlay.Target` or `CombatState.GetTeammatesOf(Owner.Creature)`, never
      `LocalContext`.
- [ ] Energy/Star cost kinds match SPEC (`CanonicalStarCost` or `HasStarCostX`, never both
      X kinds); cost upgrades use `EnergyCost.UpgradeBy` / `UpgradeStarCostBy`.
- [ ] An advanced target follows `reference/advanced-targeting.md`: one stable registration,
      live `GetTargets()` for many, zero-target gate before payment, headed selection proof.
- [ ] Targeted Card null-checks `cardPlay.Target`; every `Cmd` is awaited.
- [ ] Static numbers come from `CanonicalVars` and `DynamicVars`, never literals; `OnUpgrade`
      bumps each var the upgrade changes.
- [ ] Calculated values use one bounded helper and `Compute*Value` execution, never
      `BaseValue` or `PreviewValue`.
- [ ] A Block Card sets `GainsBlock => true` and passes `cardPlay` to `GainBlock`.
- [ ] `cards.json` has flat `<MOD>_CARD_<TYPE>.{title,description}` keys using `:diff()`
      placeholders, in the vanilla style, with no hand-written keyword line; Build lists no
      `.text-style.log` entry.
- [ ] Every named Power/keyword/Orb/Card that is not the Card's own keyword has an
      `AdditionalHoverTips` entry.
- [ ] The `[T2MOD-SELFTEST]` diagnostic marker is logged in `OnPlay`.
- [ ] A Quest Card exists only for the bounded forced-follow-up contract: cost `-1`, Quest
      rarity/type, unplayable, no upgrades, one finite prioritized mapping, exact terminal
      consumption.

## Multiplayer

Every Card plays in a multiplayer run unchanged: the owner is `base.Owner`, each player's
copy runs on every peer through the game's action queue, and an `AnyEnemy`/`AllEnemies`/`Self`
Card needs nothing more. Monster HP and Block scale with the party on their own.

Help for teammates uses the vanilla targets:

| SPEC | Shape (vanilla analog) | Code |
|---|---|---|
| another player | `TargetType.AnyAlly` (`DemonicShield`, `Intercept`) | `ArgumentNullException.ThrowIfNull(cardPlay.Target)`, then act on `cardPlay.Target` (its player: `cardPlay.Target.Player!`) |
| every player, you included | `TargetType.AllAllies` (`EnergySurge`, `HuddleUp`) | `foreach (var c in base.CombatState.GetTeammatesOf(base.Owner.Creature).Where(c => c.IsAlive && c.IsPlayer))` |

`multiplayer only` overrides `MultiplayerConstraint => CardMultiplayerConstraint.MultiplayerOnly`
(`singleplayer only` uses `SingleplayerOnly`): the host's Card factory then leaves the Card out
of rewards, shops, and pools of the other mode. An `AnyAlly` Card is always `multiplayer only`,
because with no teammate it has no legal target. Text names the receiver: "Another player
gains...", "All players gain..." (`另一名玩家`, `所有玩家`).

```csharp
public sealed class ShareGuard : ModCardTemplate
{
    public override CardMultiplayerConstraint MultiplayerConstraint => CardMultiplayerConstraint.MultiplayerOnly;
    public override bool GainsBlock => true;
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new DynamicVar[] { new BlockVar(7m, ValueProp.Move) };

    public ShareGuard() : base(1, CardType.Skill, CardRarity.Uncommon, TargetType.AnyAlly) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        ArgumentNullException.ThrowIfNull(cardPlay.Target, "cardPlay.Target");
        await CreatureCmd.GainBlock(cardPlay.Target, base.DynamicVars.Block, cardPlay);
    }

    protected override void OnUpgrade() => base.DynamicVars.Block.UpgradeValueBy(3m);
}
```

A face check reads `AnyAlly` numbers on the targeted teammate and `AllAllies` numbers on every
player; a `multiplayer only` Card's face check reports `SKIP` in singleplayer and runs in
`launch.py --self-test --multiplayer`. Behavior that needs each player to act (both play, or one
reacts to the other) takes a `plan.Coop` scenario.

## Self-test driver body

A simple Card (SPEC cites only this recipe and `reference/effect-primitives.md`, fixed numbers,
no condition) takes `plan.FaceCheck<TCard>()` and no scenario. Any other Card gets a named
`plan.Combat` scenario that plays it with `t.Play`, the real manual-play lifecycle
(`reference/selftest-harness.md`).

A calculated-value Card uses the focused matrix in `reference/card-computed-values.md`:
Damage/Block modifiers, zero and changing Energy/Star icon counts, raw versus amount-given
typed Power, base/upgrade display, and the real hand-Card tooltip. Structured post-state
proves behavior; headed review separately proves text, icon reflow, and tooltip presentation.

## Proof matrix

- **Play effect: assert the result pile.** Drive the real Card through its normal play
  lifecycle and verify it reaches the SPEC-selected result pile after its awaited effects.
- **Native Star cost: use the native play lifecycle.** Assert the rendered Energy/Star costs,
  a successful payment and effect exactly once, and an unaffordable rejection with Energy,
  Stars, Card state, and payoff unchanged. For X, include the selected captured-X/replay
  boundary.
- **Card-owned Rest Site option: assert owner identity and multiplicity.** The option is
  absent with zero or duplicate matching Cards and present for exactly one, then follows the
  shared native-room matrix: disabled/enabled, stale click rejection, deterministic success,
  repeatability, stay/leave, and icon fallback.
- **Hook participation: assert the neutral case outside the guard.** Play assertions observe
  none of it. Assert the modified value through the real path, drive one event the guard should
  ignore and assert it unchanged, and assert a combat-scope declaration from a combat pile, not
  the deck. For a collection edit, also assert an unrelated entry survives.

### Gameplay-readability headed acceptance

For hand emphasis, put the real Card in hand and drive no-active, activation, deactivation,
conflict winner, unplayable show/hide, hover/drag, and hand enter/leave states. Confirm that
cost, art, rules text, rarity, selection, and native playable feedback stay readable.

## Manual fallback (only when the harness cannot reach its scenario)

Grant it: **`card <MOD>_CARD_<TYPE>`** spawns it into the **hand** (run in progress, hand not
full). There is **no `add`** subcommand (unlike `relic add <id>`), and the id matches
**exactly** (uppercased snake case), not by substring, e.g. `card QUICK_JAB_CARD_QUICK_JAB`.
A non-attack Card can also target a pile: `card <id> Draw`.

Trigger it: play it (target an enemy for an attack; run `energy 3` first for headroom) and
confirm the expected state change. The `played:` marker is diagnostic, not proof.

## Full worked examples (verified vanilla shapes, copy-adapt)

Each extends `ModCardTemplate` and registers once through `.Card<TPool,TCard>()`.

**Single-target attack, `StrikeIronclad` shape (Attack, AnyEnemy):**
```csharp
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.ValueProps;
using STS2RitsuLib.Scaffolding.Content;

public sealed class QuickJab : ModCardTemplate
{
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new DynamicVar[] { new DamageVar(6m, ValueProp.Move) };

    public QuickJab() : base(1, CardType.Attack, CardRarity.Common, TargetType.AnyEnemy) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        ArgumentNullException.ThrowIfNull(cardPlay.Target, "cardPlay.Target");
        await DamageCmd.Attack(base.DynamicVars.Damage.BaseValue).FromCard(this)
            .Targeting(cardPlay.Target).WithHitFx("vfx/vfx_attack_slash").Execute(choiceContext);
        MainFile.Logger.Info($"[T2MOD-SELFTEST] QuickJab played: {base.DynamicVars.Damage.BaseValue} dmg");
    }

    protected override void OnUpgrade() => base.DynamicVars.Damage.UpgradeValueBy(3m);
}
```
`cards.json`: `{ "QUICK_JAB_CARD_QUICK_JAB.title": "Quick Jab", "QUICK_JAB_CARD_QUICK_JAB.description": "Deal {Damage:diff()} damage." }`
(`zhs`: `"造成{Damage:diff()}点伤害。"`)

**Self Block, `DefendIronclad` shape (Skill, Self):**
```csharp
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.ValueProps;
using STS2RitsuLib.Scaffolding.Content;

public sealed class Brace : ModCardTemplate
{
    public override bool GainsBlock => true;
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new DynamicVar[] { new BlockVar(5m, ValueProp.Move) };

    public Brace() : base(1, CardType.Skill, CardRarity.Common, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await CreatureCmd.GainBlock(base.Owner.Creature, base.DynamicVars.Block, cardPlay);
        MainFile.Logger.Info($"[T2MOD-SELFTEST] Brace played: +{base.DynamicVars.Block.BaseValue} block");
    }

    protected override void OnUpgrade() => base.DynamicVars.Block.UpgradeValueBy(3m);
}
```

**Gain a Power, `Inflame` shape (Power, Self):**
```csharp
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models.Powers;
using STS2RitsuLib.Scaffolding.Content;

public sealed class Bulk : ModCardTemplate
{
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new DynamicVar[] { new PowerVar<StrengthPower>(2m) };

    public Bulk() : base(1, CardType.Power, CardRarity.Uncommon, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await PowerCmd.Apply<StrengthPower>(choiceContext, base.Owner.Creature,
            base.DynamicVars["StrengthPower"].BaseValue, base.Owner.Creature, this);
        MainFile.Logger.Info($"[T2MOD-SELFTEST] Bulk played: +{base.DynamicVars["StrengthPower"].BaseValue} Strength");
    }

    protected override void OnUpgrade() => base.DynamicVars["StrengthPower"].UpgradeValueBy(1m);
}
```
`cards.json`: `{ ...".description": "Gain {StrengthPower:diff()} [gold]Strength[/gold]." }`
(`zhs`: `"获得{StrengthPower:diff()}点[gold]力量[/gold]。"`), plus
`AdditionalHoverTips => [HoverTipFactory.FromPower<StrengthPower>()]`.

**Attack plus debuff, `Bash` shape (Attack, AnyEnemy):** declare `DamageVar` and
`PowerVar<VulnerablePower>`, run the `QuickJab` attack, then
`await PowerCmd.Apply<VulnerablePower>(choiceContext, cardPlay.Target,
base.DynamicVars["VulnerablePower"].BaseValue, base.Owner.Creature, this)`; the upgrade bumps
both vars. Text: `"Deal {Damage:diff()} damage.\nApply {VulnerablePower:diff()} [gold]Vulnerable[/gold]."`
/ `"造成{Damage:diff()}点伤害。\n给予{VulnerablePower:diff()}层[gold]易伤[/gold]。"`, plus
`HoverTipFactory.FromPower<VulnerablePower>()`.
