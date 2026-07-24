# mechanics.md — cross-element foundations (numbers, descriptions, enums)

> The shared substrate the per-element recipes (`card`, `power`, `monster`) all build
> on. Relics and potions mostly dodge this by using **literal amounts** (`20m`) and
> **plain-text descriptions** — fine for a fixed one-shot effect. Cards and powers
> can't: their numbers scale (Strength, upgrades, enchantments) and their descriptions
> must show the *current* number. This file grounds the three mechanisms that make
> that work, so each recipe can reference it instead of re-deriving it.
>
> Every signature below was confirmed against the pinned STS2/RitsuLib API surface by the
> maintainer, not guessed. When a recipe needs a number/description/enum concept, it
> points here.

## 1. DynamicVars — the numbers that scale

A `DynamicVar` is a **named, mutable numeric value** attached to a model (card, power,
monster move). Use it instead of a C# literal whenever the number can change at
runtime — because of an upgrade, a power (Strength), an enchantment, or a preview.
Literals are correct only for a value that is truly constant.

**Declare** by overriding `CanonicalVars` (same on cards and powers):

```csharp
protected override IEnumerable<DynamicVar> CanonicalVars => new[]
{
    new DynamicVar("DamageIncrease", 1.5m),   // DynamicVar(string name, decimal baseValue)
};
```

**Read** the value for game logic (always the *base*, never the preview):

```csharp
decimal v = base.DynamicVars["DamageIncrease"].BaseValue;   // .IntValue for int
```

**Typed helpers on cards** — cards use `DynamicVar` subclasses with strongly-typed
accessors instead of string keys:

```csharp
// Strike (vanilla): a DamageVar in CanonicalVars, read via a named property.
protected override IEnumerable<DynamicVar> CanonicalVars =>
    new[] { new DamageVar(6m, ValueProp.Move) };
// ...
await DamageCmd.Attack(base.DynamicVars.Damage.BaseValue) /* ... */;
```

**Upgrade** a card's value in `OnUpgrade()`:

```csharp
protected override void OnUpgrade() => base.DynamicVars.Damage.UpgradeValueBy(3m);
```

`DynamicVar` also carries `EnchantedValue` and `PreviewValue` (display-only, reflect
enchantments / power hooks). **Never use `PreviewValue` for logic** — it's for the
number shown on the card. Use `BaseValue`.

## 2. SmartFormat descriptions — showing the current number

STS2 descriptions are **SmartFormat templates**, not plain strings. A placeholder
`{Name}` is replaced at display time with the model's DynamicVar (or an auto-injected
variable), so the hover text always shows the *current* value — after upgrades,
Strength, etc. This is why you write `"Deal {Damage} damage."`, not `"Deal 6 damage."`.

**Auto-injected variables** (available in every description without declaring them):
- `{Amount}` — a power's current stack count (powers only; `PowerModel` adds it).
- `{energyPrefix}` / energy icons, `{singleStarIcon}` — UI glyphs.
- Any name you put in `CanonicalVars` (e.g. `{Damage}`, `{DamageIncrease}`).

**Formatters** — the `:func()` suffix transforms a value. These formatter classes
exist in `Core/Localization/Formatters/` (confirmed); the exact call token in loc
text is the SmartFormat name shown below — **grep a vanilla loc entry to confirm the
precise token/args before relying on one you haven't seen used:**

| Syntax | Formatter | Effect |
|---|---|---|
| `{Damage:diff()}` | HighlightDifferences | Colors the number green/red vs. its base (upgrade/buff preview). The common one for card values. |
| `{X:diffInverse()}` | HighlightDifferencesInverse | Same, flipped (green when lower is better). |
| `{Cost:energyIcons()}` | EnergyIcons | Renders energy-cost glyphs. |
| `{X:stars()}` | StarIcons | Star glyphs. |
| `{X:percentMore()}` / `:percentLess()` | PercentMore/Less | "X% more/less" phrasing. |
| `{X:showIfUpgraded()}` | ShowIfUpgraded | Emits text only on the upgraded card. |
| `{X:abs()}` | AbsoluteValue | Absolute value (for powers that store a signed amount). |

> Rule of thumb: a **card damage/block number → `{Damage:diff()}`** so upgrades show
> green. A **power stack count → `{Amount}`** (plain; it's already the live value).
> When unsure which formatter a vanilla element uses, grep its loc entry (content) via
> `grounding.md`, or read its class for the `CanonicalVars` name.

## 3. Shared enums (one grounded list — recipes reference this)

These enums are shared across element types; each recipe picks from them rather than
redefining. Namespaces in `MegaCrit.Sts2.Core.Entities.*`. Values below are the full
sets read from the decompile (STS2 v0.107.1 — a game update could add members):

- **`TargetType`** (`Entities.Cards`, shared by cards AND potions): `None, Self,
  AnyEnemy, AllEnemies, RandomEnemy, AnyPlayer, AnyAlly, AllAllies, TargetedNoCreature,
  Osty`. ⚠️ **potions self-target with `AnyPlayer`, not `Self`** (see
  `recipes/potion.md`); cards may use `Self` (no target selection). `AnyEnemy` =
  single enemy w/ selection; `AllEnemies` = all, no selection. `TargetType.IsSingleTarget()`
  is a helper.
- **`CardType`** (`Entities.Cards`): `None, Attack, Skill, Power, Status, Curse, Quest`.
- **`CardRarity`** (`Entities.Cards`): `None, Basic, Common, Uncommon, Rare, Ancient,
  Event, Token, Status, Curse, Quest`. (Starter cards like Strike use `Basic`;
  droppable = `Common`.)
- **`PowerType`** (`Entities.Powers`): `Buff`, `Debuff`.
- **`PowerStackType`** (`Entities.Powers`): `None`, `Counter` (amount visible, manually
  inc/decremented — Strength, Poison), `Single` (amount hidden, always 1 — flag-like
  powers).
- **`PotionRarity`** (`Entities.Potions`): `None, Common, Uncommon, Rare, Event, Token`.
- **`PotionUsage`** (`Entities.Potions`): `None, CombatOnly, AnyTime, Automatic`.
- **`RelicRarity`** (`Entities.Relics`): `None, Starter, Common, Uncommon, Rare, Shop,
  Event, Ancient`.
- **`ValueProp`** (`Core.ValueProps`): damage/effect flags. `Unpowered` = the type for
  relic/potion/power flat effects; `Move` = a monster/card move's damage;
  `Unblockable`, `Unpowered | Unblockable` combine (Poison uses the latter).
  `props.IsPoweredAttack()` gates Strength/Vulnerable modifiers.

## 4. Counter Power amount domains

Every custom `PowerStackType.Counter` needs an explicit **amount domain** in `SPEC.md`.
The default is nonnegative (`[0, unbounded]`). Use a signed domain only when negative
stacks have intentional gameplay semantics (Strength/Dexterity-style), and record every
finite lower or upper bound.

The runtime types do **not** supply this contract for you:

- `PowerVar<T>` is a card `DynamicVar` for the amount an effect requests. It has no
  minimum/maximum API and does not constrain the mutable Power instance.
- `AllowNegative => false` controls when an existing Power is removed after an amount
  change. It does not reject a negative amount when `PowerCmd.Apply<T>` creates the first
  instance.
- `PowerCmd.Apply<T>` is therefore for gaining/applying a Power. For a nonnegative
  Counter, never pass a negative amount to it to consume stacks.

To consume a nonnegative Counter, get the existing instance with
`Creature.GetPower<T>()`, clamp the actual spend to `0..power.Amount`, and call
`PowerCmd.ModifyAmount` on that instance. If there is no instance, spend zero and do
nothing. Internal consumption passes `null, null` for applier/card source, matching vanilla
`VigorPower`/`Decrement`. Amount hooks can rewrite an offset, so the SPEC domain constrains
the final observable amount as well as the request: capture `ModifyAmount`'s returned raw
new amount, re-read the retained instance, and assert/log those post-hook values.
`recipes/power.md` has the copyable Cmd sequence and finite-bound rule.

## 5. Stateful timing and counters

DynamicVars and Power amounts are not a general lifecycle contract. When an effect
remembers turns/cards/uses, route to `stateful-mechanics.md` and specify the advancing
event, threshold phase, `turn|combat|run` lifetime, reset, persistence, and boundary
proof. In particular, a run-persistent relic counter uses RitsuLib
`SavedAttachedState<SpecificRelic, int/bool>`, while a combat-local turn trigger reads
`PlayerCombatState.TurnNumber`.

## Where each recipe leans on this file

- **`recipes/power.md`** — DynamicVars (§1) for the stack/scaling number, `{Amount}` +
  formatters (§2) for the description, `PowerType`/`PowerStackType` (§3), and the
  required Counter amount-domain contract (§4).
- **`recipes/card.md`** — `DamageVar`/`BlockVar` in `CanonicalVars` (§1), `OnUpgrade`,
  `{Damage:diff()}` (§2), `CardType`/`CardRarity`/`TargetType` in the constructor (§3).
- **relics/potions** — mostly literal amounts + plain descriptions; they only need §3
  (enums). They reach here only for a scaling effect. A stateful relic additionally
  routes to `stateful-mechanics.md` (§5); potion saved state is not pipeline-supported.

When this file lacks a specific value or formatter, follow `grounding.md`: at runtime
that means the rest of the pack (recipes, `build-constraints.md`, snapshots,
`errors.md`); if it's genuinely not in the pack, report a pack gap rather than
guessing. Never a third guess.
