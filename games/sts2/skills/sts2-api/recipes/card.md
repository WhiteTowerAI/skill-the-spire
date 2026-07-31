# Recipe: Card

> A copy-adaptable, **known-good** RitsuLib pattern for a single STS2 card. Every signature
> here was confirmed against STS2 `0.107.1`, RitsuLib `0.4.67`, and the hosted
> `RitsuCardProof` run, not guessed. Cards
> lean harder on `reference/mechanics.md` than relics/potions do (scaling numbers,
> upgrades, SmartFormat descriptions) — **read that first.** The skill fills only the
> **effect logic**; `ModCardTemplate`, content-pack registration, localization, and
> `CardAssetProfile` are adapter-owned.
> When SPEC declares calculated values, Energy/Star icon counts, typed computed Power
> amounts, or variable tooltips, also read `reference/card-computed-values.md`.
> When SPEC declares a filtered live-creature target, also read
> `reference/advanced-targeting.md`; it owns registration, one/many execution,
> zero-target cancellation, and headed selection proof.
> When SPEC declares hand emphasis, also read `reference/card-hand-emphasis.md`; it owns
> ordered-rule lowering, priority/ties, refresh boundaries, and headed hand proof.
>
> Vanilla cards to imitate: `StrikeIronclad` (single-target attack), `DefendIronclad`
> (self block), `Inflame` (gain a Power), `Bash` (attack + apply a debuff).
>
> **Scope: making a NEW card.** *Editing* an existing vanilla card is a different,
> harder path (version-sensitive patching) and is deferred;
> see the note near the end.

## When to use

The request maps to a **card** when it's something the player **plays from hand for an
energy cost** during combat — not a passive item they own (relic) or a one-shot
consumable (potion). Phrasings: "a card that…", "an attack that…", "a skill that
gives…", "a power that…", "costs 1 energy and…". Cards fire their effect in `OnPlay`
when the player plays them, and their numbers can **scale** (Strength, upgrades) — so
they use `DynamicVar`s + SmartFormat, not the literal amounts relics/potions get away with.

The bounded forced-follow-up Quest token is the one exception to this normal play-from-
hand classification. It is an unplayable dependency of an Event composition; route it to
`reference/forced-followup-event.md` instead of giving it `OnPlay` behavior.

## Card types (pick from SPEC — sets the frame + where it slots)

`CardType` (`Entities.Cards`, see `mechanics.md` §3): **`Attack`** (deals damage),
**`Skill`** (block / utility / non-attack effect), **`Power`** (a permanent buff played
once, consumed into a power). `Status`/`Curse`/`Quest` are special — not for a normal
custom card. The only current Quest exception is the bounded unplayable token in
`reference/forced-followup-event.md`. Most requests are `Attack` or `Skill`.

## Scaffold and registration

The open-mod scaffold exposes one `MainFile.RegisterContent()` partial hook. Add the
Card to that hook exactly once; the pool generic is the availability contract:

```csharp
RitsuLibFramework.CreateContentPack(ModId)
    .Card<ColorlessCardPool, Cards.<CardName>>()
    .Apply();
```

Do not add a pool attribute or a second registration path. The model extends RitsuLib's
public `ModCardTemplate`. Custom art uses an explicit profile:

```csharp
public override CardAssetProfile AssetProfile => new()
{
    PortraitPath = "res://<ModName>/images/card_portraits/<slug>.png",
};
```

Omit the override for placeholder art. Empty profile fields retain the template/base-game
fallback. Custom art is optional and never blocks the pipeline. The established normal
portrait import remains `1000×760`; Ancient-only full art remains out of scope. See
`reference/art-contract.md`.

### Optional hand emphasis

Do not put visual-node code in the Card. For one non-competing gold/red rule, override the
matching native `ShouldGlowGoldInternal` or `ShouldGlowRedInternal` property. For multiple
rules or any custom color, append exactly one typed `.CardHandOutline<TCard>(...)` step to
the same builder and emit every `ModCardHandOutlineSwitchRule<TCard>.Fixed(...)` in SPEC
order. The highest active integer priority wins; a tie uses the later listed rule.

Use the reference's exact `visibleWhenUnplayable` mapping and keep fixed rules at
`RefreshEveryFrame: false`. Never mix the native and custom-outline routes on one generated
Card, register after `.Apply()`, retain a Card instance, or poll UI state.

## The skeleton (fill only the marked spots)

Add ONE file under `<ModName>Code/Cards/<CardName>.cs`:

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
        // (See "Effect building blocks". Pick the block(s) matching SPEC's effect.)
        // ─────────────────────────────────────────────────────────────────────

        MainFile.Logger.Info("[T2MOD-SELFTEST] <CardName> played: <what happened>");
    }

    protected override void OnUpgrade()
    {
        base.DynamicVars.Damage.UpgradeValueBy(3m);   // bump the var(s) the upgrade improves
    }
}
```

## The constructor arguments (all REQUIRED — passed to `base(...)`)

| Arg | Type | Pick by |
|---|---|---|
| `cost` | `int` | energy cost from SPEC (0/1/2/3…). |
| `type` | `CardType` = `Attack, Skill, Power, …` | deals damage → `Attack`; block/utility → `Skill`; permanent buff → `Power`. |
| `rarity` | `CardRarity` = `Basic, Common, Uncommon, Rare, …` | droppable default `Common`; `Basic` is for starter cards. |
| `target` | `TargetType` (shared with potions) | one enemy → **`AnyEnemy`**; all enemies → `AllEnemies`; a self/no-selection effect (block, gain Strength) → **`Self`**. |

An advanced target does not lower to a vanilla enum. Use the stable registered value from
`reference/advanced-targeting.md`. A single-target Card keeps `cardPlay.Target`; a
multi-target Card overrides `IsPlayable` for the empty group and calls `GetTargets()`
inside `OnPlay`. Never cache the target list from selection time.

> ⚠️ Card `Self` vs potion `AnyPlayer`: a **card** that targets the player uses
> `TargetType.Self` (no target selection) — `DefendIronclad`/`Inflame` do. Potions use
> `AnyPlayer` instead. Don't copy a potion's target type onto a card.

## Trigger

Override **`protected override async Task OnPlay(PlayerChoiceContext choiceContext,
CardPlay cardPlay)`** — runs when the card is played. `cardPlay.Target` is the chosen
enemy (for a targeted card; **null-check it** with `ArgumentNullException.ThrowIfNull`).
`base.Owner` is the `Player`, `base.Owner.Creature` their body. There's no hook to pick
like a relic — all the card's effect goes in `OnPlay`. (Rare extras exist:
`OnTurnEndInHand` for "if this is in your hand at end of turn…", `IsPlayable` to gate
playability — reach for them only if SPEC demands.)

## Effect building blocks (confirmed APIs — pick the block(s) matching SPEC)

All `Cmd`s are `static async Task` — `await` every one. Read static scaling numbers from
their normal `DynamicVars`; read calculated values through the matching `Compute*Value`
extension. Never execute a calculated effect from `BaseValue` or display-only
`PreviewValue`.

### Attack — deal damage (`CardType.Attack`, `TargetType.AnyEnemy`)

`DamageCmd.Attack(...)` returns a **fluent builder** (`AttackCommand`) — chain the
attacker, target, and fx, then `.Execute(choiceContext)`:

```csharp
ArgumentNullException.ThrowIfNull(cardPlay.Target, "cardPlay.Target");
await DamageCmd.Attack(base.DynamicVars.Damage.BaseValue)
    .FromCard(this)                        // attacker = this card's owner; enables Strength etc.
    .Targeting(cardPlay.Target)            // the single chosen enemy
    .WithHitFx("vfx/vfx_attack_slash")     // hit vfx (+ optional sfx args); slash is the generic one
    .Execute(choiceContext);
```

Builder methods you may need (all return the builder, keep chaining):
- `.TargetingAllOpponents(combatState)` — hit every enemy (`TargetType.AllEnemies`).
  Get `combatState` from `base.Owner.PlayerCombatState!`.
- `.TargetingRandomOpponents(combatState)` — random target(s).
- `.WithHitCount(n)` — multi-hit (Twin Strike = 2). `n` can be a `DynamicVar` value.
- `.Unpowered()` — do NOT scale with Strength (rare; for fixed-damage attacks).

### Block — gain block (`CardType.Skill`, `TargetType.Self`)

Set `GainsBlock => true` (the engine uses it for previews/tags) and use the
**`cardPlay` overload** of `GainBlock` (different from the potion's 3-arg overload):

```csharp
public override bool GainsBlock => true;
// ...in OnPlay:
await CreatureCmd.GainBlock(base.Owner.Creature, base.DynamicVars.Block, cardPlay);
```

### Power — apply a buff/debuff (`CardType.Power` for self-buffs, or on any card)

Use a vanilla power if one fits (`StrengthPower`, `DexterityPower`, `VulnerablePower`,
`WeakPower`, `PoisonPower`…). `cardSource` is `this`:

```csharp
// self-buff (Inflame — gain Strength; TargetType.Self):
await PowerCmd.Apply<StrengthPower>(choiceContext, base.Owner.Creature,
    base.DynamicVars["StrengthPower"].BaseValue, base.Owner.Creature, this);

// debuff on the target enemy (needs TargetType.AnyEnemy + a null-check):
await PowerCmd.Apply<VulnerablePower>(choiceContext, cardPlay.Target,
    base.DynamicVars["VulnerablePower"].BaseValue, base.Owner.Creature, this);
```

If no vanilla power matches the request ("at end of turn deal 3 to all"), author a
**custom power** first (`recipes/power.md`), then `PowerCmd.Apply<YourPower>(...)` here.

`Apply<T>` is the gain/application path. If the card **consumes** a custom nonnegative
Counter ("lose/consume up to N stacks"), do not pass a negative amount to `Apply<T>`.
Use `recipes/power.md`'s amount-domain pattern: `GetPower<T>()`, clamp the spend to the
existing amount, then `PowerCmd.ModifyAmount` that instance.

### Scry - inspect top X, discard any number (`CardType.Skill`, `TargetType.Self`)

Read `reference/scry-helper.md` and emit its generated-Mod-local `OpenModScry` helper.
Declare `new DynamicVar("Scry", X)` and await it from `OnPlay`:

```csharp
Result = await OpenModScry.Execute(
    choiceContext, Owner, DynamicVars["Scry"].IntValue);
```

Do not inline a second selector/pile implementation, add BaseLib, or dispatch a global
Scry hook. The current contract is singleplayer-only and returns requested/seen/discarded
Cards for local composition. Its focused proof covers zero/empty/short/full Draw, visible
UI and await behavior, stable order, normal source result pile, and exact discard
history/hooks.

### Combine — attack THEN debuff (Bash pattern)

Declare both vars, run the attack, then apply the power on the same target:

```csharp
ArgumentNullException.ThrowIfNull(cardPlay.Target, "cardPlay.Target");
await DamageCmd.Attack(base.DynamicVars.Damage.BaseValue).FromCard(this)
    .Targeting(cardPlay.Target).WithHitFx("vfx/vfx_attack_blunt").Execute(choiceContext);
await PowerCmd.Apply<VulnerablePower>(choiceContext, cardPlay.Target,
    base.DynamicVars["VulnerablePower"].BaseValue, base.Owner.Creature, this);
```

> For any effect not covered here (draw, energy, card generation), follow
> `grounding.md`: check the rest of the pack (`reference/mechanics.md`, snapshots,
> `errors.md`) for the Cmd. If it's genuinely not in the pack, report a pack gap —
> **do not guess a Cmd name** (the maintainer grounds new Cmds offline).

### Calculated values, icon counts, and variable tooltips

Read `reference/card-computed-values.md` and preserve its complete contract. In short:

- generate one pure bounded calculation shared by base/upgrade preview and execution;
- select `ComputedDamage`/`ComputedBlock` when normal combat modifiers apply, plain
  `Computed` only when they intentionally do not, and the typed Energy/Stars/Power helper
  for those roles;
- execute through `ComputeDynamicValue`, `ComputeEnergyValue`, `ComputeStarsValue`, or
  `ComputePowerValue<T>`, then pass the raw result to the normal Cmd exactly once;
- use `{EnergyGain:energyIcons()}` and `{StarGain:starIcons()}`; and
- attach `.WithSharedTooltip(...)` only when SPEC supplies the corresponding
  `static_hover_tips` title/description.

If Card payment or normal Hand-to-Play movement changes a formula input, the shared helper
must make preview and live execution observe the SPEC's declared evaluation point. Stop
authoring when that cannot be done deterministically.

## DynamicVars, upgrade & description (see `reference/mechanics.md` §1–2)

Cards declare their static numbers in `CanonicalVars` and read them via typed accessors:

- `new DamageVar(6m, ValueProp.Move)` → `base.DynamicVars.Damage.BaseValue`
- `new BlockVar(5m, ValueProp.Move)` → `base.DynamicVars.Block.BaseValue`
- `new PowerVar<StrengthPower>(2m)` → `base.DynamicVars["StrengthPower"].BaseValue`
  (power vars use the string key = the power's class name)

**Upgrade** bumps the var(s) in `OnUpgrade()`:

```csharp
protected override void OnUpgrade()
{
    base.DynamicVars.Damage.UpgradeValueBy(3m);
    // base.DynamicVars["VulnerablePower"].UpgradeValueBy(1m);   // bump each var the upgrade changes
}
```

**There is NO separate "upgraded description" loc key.** The upgraded name is
auto-generated (`title` + `+N`); the upgraded *description* is the SAME description
string, re-rendered through SmartFormat — so you write the number as a placeholder with
`:diff()` and it shows the new value in green after upgrade:

```
"Deal {Damage:diff()} damage. Apply {VulnerablePower:diff()} Vulnerable."
```

Use `{X:showIfUpgraded()}` for text that should appear only on the upgraded card. See
`mechanics.md` §2 for the full formatter table.

## Localization (ships in the .pck)

Table is **`cards`**. Add to `<ModName>/localization/eng/cards.json`. Keys are flat and
use the exact RitsuLib public entry (`MOD_CARD_TYPENAME`):

```json
{
  "<MOD>_CARD_<TYPE>.title": "Display Name",
  "<MOD>_CARD_<TYPE>.description": "Deal {Damage:diff()} damage.",
  "<MOD>_CARD_<TYPE>.selectionScreenPrompt": "Prompt — only if the card asks the player to choose; else omit."
}
```

`{Damage}`/`{Block}` resolve from the matching `DynamicVar`; a power var resolves by its
class-name key (`{StrengthPower}`, `{VulnerablePower}`). **Flat string keys, not nested
JSON.** No `.flavor` for cards (relics only).

Calculated icon variables use the pinned `{EnergyGain:energyIcons()}` and
`{StarGain:starIcons()}` tokens. A declared variable tooltip adds flat `.title` and
`.description` entries to `localization/eng/static_hover_tips.json`; see
`reference/card-computed-values.md` for the deterministic entry stem and null-icon
fallback.

### Bounded rich text

If SPEC selects vanilla text effects, read `reference/content-text-effects.md`. Card
descriptions may author only balanced `gold` and `purple` spans. Preserve SmartFormat
placeholders; `:diff()` owns its automatic green/red preview highlighting. The same
description renders in the real Card body and typed Card Hover Tip preview.

## ID / loc-key derivation

RitsuLib derives `Id.Entry` as `MOD_CATEGORY_TYPENAME`; each segment is normalized to
uppercase snake case. Mod id `BladeDance`, Card class `BladeDance` becomes
`BLADE_DANCE_CARD_BLADE_DANCE`. Use that exact stem for `cards.json`. If a published
identity must survive a type rename, pass `ModelPublicEntryOptions.FromStem(...)` to the
content-pack Card registration. Do not create a second id rule.

## Rarity & pool

`CardRarity` (`mechanics.md` §3): `Basic` (starters), `Common` (default droppable),
`Uncommon`, `Rare`. The pool is required once as the first generic argument to
`.Card<TPool,TCard>()`. Pools (`MegaCrit.Sts2.Core.Models.CardPools`):
- **`ColorlessCardPool`** — any character can find it. **Default choice** (mirrors
  `SharedRelicPool`). Note: the pool's `Title` feeds the card frame color / atlas
  subdir, so a colorless card gets the grey colorless frame.
- `IroncladCardPool`, `SilentCardPool`, `DefectCardPool`, `RegentCardPool`,
  `NecrobinderCardPool` — a specific character's pool (card only appears for them).

## Pre-flight checklist (catches the common silent failures)

- [ ] Class is `public sealed` and extends `ModCardTemplate`.
- [ ] Exactly one `.Card<TPool,TCard>()` registration exists in `MainFile.Content.cs`.
- [ ] Constructor passes `cost, CardType, CardRarity, TargetType` to `base(...)`.
- [ ] `TargetType` matches the effect: `AnyEnemy` (targeted attack), `Self` (block /
      self-buff — NOT `AnyPlayer`, that's potions), `AllEnemies` (room).
- [ ] An advanced target follows `reference/advanced-targeting.md`: one stable
      registration, source context only for single-target rules, live `GetTargets()` for
      many, zero-target gate before payment, normal result pile, and headed mouse/controller
      proof.
- [ ] Targeted card null-checks `cardPlay.Target` (`ArgumentNullException.ThrowIfNull`).
- [ ] Static numbers come from `CanonicalVars` + `DynamicVars.*`, not literals;
      `OnUpgrade` bumps each static var the upgrade changes.
- [ ] Calculated values have one bounded deterministic helper, explicit inputs/upgrade/
      evaluation point, the matching computed factory and `Compute*Value` execution read;
      neither `BaseValue` nor `PreviewValue` executes the effect.
- [ ] Energy/Star descriptions use `energyIcons()`/`starIcons()` and any variable tooltip
      has flat `static_hover_tips` title/description keys plus an intentional icon fallback.
- [ ] Block card sets `GainsBlock => true` and uses the `cardPlay` overload of `GainBlock`.
- [ ] `cards.json` has `<MOD>_CARD_<TYPE>.{title,description}` — flat public-entry keys,
      table `cards`; description uses `{Damage:diff()}` etc. so upgrades render.
- [ ] All `Cmd`s `await`ed.
- [ ] Scry, when selected, uses the one attributed `OpenModScry` helper; preserves Draw
      order/history/hooks; and keeps its explicit singleplayer boundary.
- [ ] `[T2MOD-SELFTEST]` diagnostic marker logged in `OnPlay`; load marker in MainFile;
      `SelfTest` independently asserts post-state.
- [ ] A Quest Card is emitted only for the bounded forced-follow-up contract: cost `-1`,
      Quest rarity/type, unplayable, no upgrades, one act/target, and unchanged hook inputs
      outside that act.

## Full worked examples (verified vanilla, copy-adapt)

> Each example extends the public RitsuLib template directly. Register the chosen class
> once through `.Card<TPool,TCard>()` in the shared content pack.

**Single-target attack — `StrikeIronclad` shape (Attack, AnyEnemy):**
```csharp
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

**Self block — `DefendIronclad` shape (Skill, Self):**
```csharp
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

**Gain a power — `Inflame` shape (Power, Self):**
```csharp
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
`cards.json`: `{ ...".description": "Gain {StrengthPower:diff()} Strength." }` (needs `using MegaCrit.Sts2.Core.Models.Powers;` for `StrengthPower`.)

**Attack + debuff — `Bash` shape (Attack, AnyEnemy):** declare `DamageVar` + `PowerVar<VulnerablePower>`, run the attack then apply — see "Combine" above; upgrade bumps both vars.

## Verify (tier-1 + tier-2)

1. Build with `tools/build.py`; it packs the generated resource tree and deploys the
   Mod's own `.dll`, `.json`, and `.pck`. A no-art card loads with a placeholder
   portrait — expected in M4, not a failure. If load *errors*, that's a repair signal.
2. Run `verify.md`: Tier 1 checks the load marker; automated Tier 2 spawns/plays the card,
   asserts its concrete state delta, and greps the structured `state proof:` line.
   A calculated-value Card uses the focused behavior/presentation matrix in
   `reference/card-computed-values.md`.
   A Scry Card instead uses the single focused visible-selector matrix in
   `reference/scry-helper.md` and its `R6 scry helper complete ... observed=all` marker.
3. Manual fallback only: dev console (backtick) → **`card <MOD>_CARD_<TYPE>`** → play it in
   combat and directly confirm the expected state change. The `played:` marker is diagnostic,
   not sufficient proof.

> ⚠️ The card console command is **`card <id> [pile]`** — spawns into your **hand by
> default**, there is **no `add`/`remove` subcommand** (unlike `relic add <id>`). It
> matches the id **exactly** (uppercased, screaming-snake), NOT by substring — pass the
> full public entry, e.g. `card QUICK_JAB_CARD_QUICK_JAB`. Confirmed against
> `CardConsoleCmd.cs`. (For a non-attack card you can also target a pile: `card <id> Draw`.)

## Editing an EXISTING vanilla card — deferred (not this recipe)

This recipe makes **new** cards. *Changing* a shipped card (e.g. "make Strike deal 9")
is a different mechanism requiring a version-sensitive patch against vanilla code. It is
outside the supported boundary; do not initialize a patcher for a normal new Card. If a
request is really "edit an existing card", report that gap and offer the closest new Card.
