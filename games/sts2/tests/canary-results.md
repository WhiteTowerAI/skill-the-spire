# Canary matrix — run record (M4.5 ②)

> Companion to `canary.md`. Records the first full run (2026-07-03, STS2 v0.107.1,
> .NET 9.0.300, BaseLib active) and the exact minimal element bodies used, so the
> suite is reproducible. All projects live **outside the repo** at
> `D:\26summer_intern\canary-<x>\` (regenerate-on-demand, not committed).

## Result: ALL FIVE PASS (build 0/0 + tier-1 load-verified)

| Cell | Build | `.pck` | Tier-1 (load marker + no mod errors) |
|------|-------|--------|--------------------------------------|
| CanaryRelic | 0 warn / 0 err | ✓ | PASS |
| CanaryPotion | 0 warn / 0 err | ✓ | PASS |
| CanaryCard | 0 warn / 0 err | ✓ | PASS |
| CanaryPower | 0 warn / 0 err | ✓ | PASS |
| CanaryCombo | 0 warn / 0 err | ✓ | PASS |

One launch loaded all five (`RUNNING MODDED = YES`); each load marker
`[T2MOD-SELFTEST] Canary<X> loaded ok` found, zero errors/exceptions naming any mod.

## Findings this suite surfaced (its whole point)

1. **`power.md` worked-example `powers.json` was missing `.smartDescription`** — the
   exact STS001 bug the milestone is about, sitting in the recipe's own copy-paste
   example (the prose above it said "three keys", the example showed two). Fixed the
   example to include `.smartDescription`. This is the "recipe written from grounding
   but never built" class — power was the only recipe with no prior green build.
2. **`card.md` skeleton omits the null-guard the prose requires** → a minimal follow
   builds with **CS8604** (possible null on `.Targeting(cardPlay.Target)`). The prose
   and the "Attack" block *do* show `ArgumentNullException.ThrowIfNull(cardPlay.Target)`,
   but the top-level skeleton (lines ~91) does not, so the most literal reading warns.
   The canary adds the guard and builds clean. (Left as a note — the guard is already
   documented; a future card.md tidy could hoist it into the skeleton.)

Both are real recipe-quality wins caught with **zero user involvement** — the
argument for keeping this suite.

## Exact minimal bodies used (copy-paste reproducible)

Each mod = scaffold + PckPacker uncommented + the file(s) below + the
`Logger.Info("[T2MOD-SELFTEST] Canary<X> loaded ok")` line in `MainFile.Initialize()`.
IDs follow the derivation rule (namespace first segment upper + `-` + slugified class).

### relic — `CanaryRelicCode/Relics/Bauble.cs` + `relics.json` (3 keys)
```csharp
[Pool(typeof(SharedRelicPool))]
public sealed class Bauble : CanaryRelicRelic {
    public override RelicRarity Rarity => RelicRarity.Common;
    public override async Task AfterSideTurnStart(CombatSide side,
        IReadOnlyList<Creature> participants, ICombatState combatState) {
        var combat = Owner.PlayerCombatState!;
        if (!participants.Contains(Owner.Creature) || combat.TurnNumber > 1) return;
        Flash();
        await PlayerCmd.GainEnergy(1, Owner);
        MainFile.Logger.Info("[T2MOD-SELFTEST] CanaryRelic Bauble fired: +1 energy");
    }
}
```
`relics.json`: `CANARYRELIC-BAUBLE.{title,description,flavor}`.

### potion — hand-made `Potions/CanaryPotionPotion.cs` (base) + `Potions/Fizz.cs` + `potions.json` (2 keys)
```csharp
public abstract class CanaryPotionPotion : CustomPotionModel { }

[Pool(typeof(SharedPotionPool))]
public sealed class Fizz : CanaryPotionPotion {
    public override PotionRarity Rarity => PotionRarity.Common;
    public override PotionUsage Usage => PotionUsage.CombatOnly;
    public override TargetType TargetType => TargetType.AnyEnemy;
    protected override async Task OnUse(PlayerChoiceContext choiceContext, Creature? target) {
        AssertValidForTargetedPotion(target);
        await CreatureCmd.Damage(choiceContext, target!, 10m, ValueProp.Unpowered, base.Owner.Creature, null);
        MainFile.Logger.Info("[T2MOD-SELFTEST] CanaryPotion Fizz used: 10 dmg");
    }
}
```
`potions.json`: `CANARYPOTION-FIZZ.{title,description}`.

### card — `Cards/Jolt.cs` + `cards.json` (2 keys)
```csharp
[Pool(typeof(ColorlessCardPool))]
public sealed class Jolt : CanaryCardCard {
    protected override IEnumerable<DynamicVar> CanonicalVars => new DynamicVar[] { new DamageVar(6m, ValueProp.Move) };
    public Jolt() : base(1, CardType.Attack, CardRarity.Common, TargetType.AnyEnemy) { }
    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay) {
        System.ArgumentNullException.ThrowIfNull(cardPlay.Target);   // <- without this: CS8604
        await DamageCmd.Attack(DynamicVars.Damage.BaseValue).FromCard(this)
            .Targeting(cardPlay.Target).WithHitFx("vfx/vfx_attack_slash").Execute(choiceContext);
        MainFile.Logger.Info($"[T2MOD-SELFTEST] CanaryCard Jolt played: {DynamicVars.Damage.BaseValue} dmg to target");
    }
    protected override void OnUpgrade() => DynamicVars.Damage.UpgradeValueBy(3m);
}
```
`cards.json`: `CANARYCARD-JOLT.{title,description}` (description uses `{Damage}`).

### power — `Powers/Smolder.cs` + `powers.json` (**3 keys incl. smartDescription**)
```csharp
public sealed class Smolder : CustomPowerModel {           // NO [Pool]
    public override PowerType Type => PowerType.Debuff;
    public override PowerStackType StackType => PowerStackType.Counter;
    public override async Task AfterSideTurnStart(CombatSide side,
        IReadOnlyList<Creature> participants, ICombatState combatState) {
        if (!participants.Contains(base.Owner)) return;
        Flash();
        int dealt = base.Amount;
        await CreatureCmd.Damage(new ThrowingPlayerChoiceContext(), base.Owner, dealt,
            ValueProp.Unblockable | ValueProp.Unpowered, null, null);
        if (base.Owner.IsAlive) await PowerCmd.Decrement(this);
        MainFile.Logger.Info($"[T2MOD-SELFTEST] CanaryPower Smolder fired: {dealt} dmg to {base.Owner}");
    }
}
```
`powers.json`: `CANARYPOWER-SMOLDER.{title,description,smartDescription}`.

### combo — `Powers/Signal.cs` (as power above) + `Cards/Charge.cs` + both loc tables
```csharp
[Pool(typeof(ColorlessCardPool))]
public sealed class Charge : CanaryComboCard {
    protected override IEnumerable<DynamicVar> CanonicalVars => new DynamicVar[] { new PowerVar<Signal>(3m) };
    public Charge() : base(1, CardType.Skill, CardRarity.Common, TargetType.AnyEnemy) { }
    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay) {
        System.ArgumentNullException.ThrowIfNull(cardPlay.Target);
        await PowerCmd.Apply<Signal>(choiceContext, cardPlay.Target,
            base.DynamicVars["Signal"].BaseValue, base.Owner.Creature, this);
        MainFile.Logger.Info("[T2MOD-SELFTEST] CanaryCombo Charge played: applied Signal");
    }
}
```
`cards.json`: `CANARYCOMBO-CHARGE.{title,description}` (uses `{Signal}`);
`powers.json`: `CANARYCOMBO-SIGNAL.{title,description,smartDescription}`.
