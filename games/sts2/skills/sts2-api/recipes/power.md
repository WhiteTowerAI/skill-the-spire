# Recipe: Power

> A copy-adaptable, **known-good** pattern for a single STS2 power (a buff/debuff:
> Strength, Poison, Vulnerable…). Every signature here was confirmed against
> decompiled `sts2.dll` + BaseLib — not guessed. Reads the shared `reference/mechanics.md`
> for DynamicVars, SmartFormat descriptions, and enums; **read that first.**
>
> Vanilla powers to imitate: `StrengthPower` (passive damage modifier), `PoisonPower`
> (turn-triggered damage + decay), `VulnerablePower` (duration debuff that ticks down).

## When to use

A **power** is a **persistent buff/debuff on a creature** — it has a stack count and
its own trigger hooks that fire repeatedly while it's present. Phrasings: "gain X
Strength", "enemies take N poison", "at the start of each turn, …" applied *as a
lasting status*, "whenever you're attacked, …".

**Powers are almost never the top-level request** — the player doesn't "get a power",
they play a **card** or own a **relic** that *applies* one. So a power is usually a
**dependency of a card/relic recipe**: if the requested card does something vanilla
powers don't cover ("at end of turn, deal 3 damage to all enemies"), you author a
custom power here, then apply it from the card via `PowerCmd.Apply<T>` (below).

**Prefer a vanilla power** when one fits (Strength, Dexterity, Weak, Vulnerable,
Poison, Thorns…) — just `PowerCmd.Apply<StrengthPower>(...)`, no new class. Author a
custom power only for behavior no vanilla power provides.

## Registration — the good news: NO `[Pool]`, NO manual registration

Unlike relics/potions/cards, a custom power is **auto-discovered by `ModelDb`
reflection** (it's a `PowerModel` subtype in your mod assembly). `CustomPowerModel`
has no `AddModel` call, so:

- **Do NOT add `[Pool(...)]`** — powers don't go in a drop pool. (Adding one is
  harmless-ish but wrong; leave it off.)
- No registration boilerplate. Subclass + localization + (optional) icon is all.

This makes powers the **least-boilerplate element type**. Confirmed:
`CustomPowerModel` has no constructor; BaseLib's `[Pool]` enforcement
(`CustomContentDictionary.AddModel`) is only called for Card/Relic/Potion.

## The skeleton (fill only the marked spots)

Create `<ModName>Code/Powers/` if the template didn't (it scaffolds `Cards/`,
`Powers/`, `Relics/` — `Powers/` usually exists). Add ONE file
`<ModName>Code/Powers/<PowerName>.cs`:

```csharp
using System.Collections.Generic;
using System.Threading.Tasks;
using BaseLib.Abstracts;                              // CustomPowerModel
using MegaCrit.Sts2.Core.Combat;                      // CombatSide, ICombatState
using MegaCrit.Sts2.Core.Commands;                    // CreatureCmd, PowerCmd
using MegaCrit.Sts2.Core.Entities.Creatures;          // Creature
using MegaCrit.Sts2.Core.Entities.Powers;             // PowerType, PowerStackType
using MegaCrit.Sts2.Core.Localization.DynamicVars;    // DynamicVar (only if you scale)
using MegaCrit.Sts2.Core.ValueProps;                  // ValueProp

namespace <ModName>.<ModName>Code.Powers;

public sealed class <PowerName> : CustomPowerModel        // NO [Pool] attribute
{
    public override PowerType Type => PowerType.Buff;      // or Debuff  (REQUIRED)
    public override PowerStackType StackType => PowerStackType.Counter;  // REQUIRED

    // Optional: only for Strength/Dexterity-style powers that can go negative
    // (removed at exactly 0 instead of below 0):
    // public override bool AllowNegative => true;

    // ─────────── TRIGGER — override the ONE hook matching the effect ───────────
    // (See "Trigger hooks" below. `base.Amount` is the current stack count.)
    // ────────────────────────────────────────────────────────────────────────────
}
```

## Required overrides (both abstract on `PowerModel`)

| Property | Type | Pick by |
|---|---|---|
| `Type` | `PowerType` = `Buff`, `Debuff` | good = `Buff`, bad = `Debuff` (only affects the label color / classification) |
| `StackType` | `PowerStackType` = `None, Counter, Single` | **`Counter`** = visible numeric stacks (Strength, Poison). **`Single`** = hidden flag, amount always 1 (a boolean "you have this" power). |

Optional: `AllowNegative => true` (Strength/Dexterity — negative stacks debuff you;
power auto-removed at exactly 0). Default `false` (removed when it drops below 0).

## Trigger hooks (override the ONE matching the request)

Powers receive the **same hook family as relics** (`ShouldReceiveCombatHooks => true`
— no interface, no subscribe; just override the `virtual Task`/value method). Reach
your owner via **`base.Owner`** (the `Creature` the power is on) and the stack count
via **`base.Amount`**. `Flash()` for the on-trigger pulse.

| Request phrasing | Hook to override | Vanilla example |
|---|---|---|
| "at the start of your turn, …" (poison-like) | `AfterSideTurnStart(CombatSide side, IReadOnlyList<Creature> participants, ICombatState combatState)` — guard `participants.Contains(base.Owner)` | `PoisonPower` |
| "at end of turn, …" | `AfterSideTurnEnd(PlayerChoiceContext, CombatSide, IEnumerable<Creature>)` or `BeforeSideTurnEndEarly(...)` | `PlatingPower` (gains block at turn end) |
| "duration debuff that wears off" (Weak/Vulnerable) | `AfterSideTurnEnd(...)` → `await PowerCmd.TickDownDuration(this)` | `VulnerablePower` |
| "increases damage you deal" (passive) | `ModifyDamageAdditive(Creature? target, decimal amount, ValueProp props, Creature? dealer, CardModel? cardSource)` → **return** the flat bonus | `StrengthPower` (returns `base.Amount`) |
| "increases damage taken" (passive) | `ModifyDamageMultiplicative(...)` → **return** a multiplier (e.g. `1.5m`) | `VulnerablePower` |
| "when applied / removed" | `AfterApplied(Creature? applier, CardModel? cardSource)` / `AfterRemoved(Creature oldOwner)` / `BeforeApplied(...)` | — |

> The modify-* hooks **return a value and do no action** — guard them with
> `props.IsPoweredAttack()` and an owner/target check (Strength only buffs *its
> owner's* attacks; Vulnerable only when *its owner* is the target). The turn hooks
> **do actions** (`await` Cmds), then usually `PowerCmd.Decrement(this)` or
> `TickDownDuration(this)` to consume a stack.

## Effect building blocks (confirmed APIs)

Inside a turn-triggered hook (`base.Owner` is the afflicted creature, `base.Amount`
the stacks). All `Cmd`s are `static async Task` — `await` them.

```csharp
// Deal poison-style damage to the owner, then consume a stack:
await CreatureCmd.Damage(new ThrowingPlayerChoiceContext(), base.Owner, base.Amount,
    ValueProp.Unblockable | ValueProp.Unpowered, null, null);
await PowerCmd.Decrement(this);                 // -1 stack

// Gain block for the owner at turn end (Plating-style):
await CreatureCmd.GainBlock(base.Owner, base.Amount, ValueProp.Unpowered, null);

// Duration debuff wearing off (Vulnerable/Weak-style), in AfterSideTurnEnd:
await PowerCmd.TickDownDuration(this);
```

**Applying THIS power from a card/relic** (the caller side — usually in the card's
`OnPlay` or the relic's hook). Single target:

```csharp
// PowerCmd.Apply<T>(PlayerChoiceContext, Creature target, decimal amount,
//                   Creature? applier, CardModel? cardSource, bool silent = false)
await PowerCmd.Apply<<PowerName>>(choiceContext, target, 3m, base.Owner.Creature, this);
```

`applier` = the creature causing it (usually `Owner.Creature`). `cardSource` = the
card if applied from a card's `OnPlay` (pass `this`), else `null` (e.g. from a relic
hook). See the worked example below for both.

(There's also an `IEnumerable<Creature>` overload for all-target application.)

## DynamicVars & description (see `reference/mechanics.md` §1–2)

If the power has a tunable number beyond the plain stack `Amount` (e.g. Vulnerable's
1.5× multiplier), declare it:

```csharp
protected override IEnumerable<DynamicVar> CanonicalVars =>
    new[] { new DynamicVar("DamageIncrease", 1.5m) };
// read it: base.DynamicVars["DamageIncrease"].BaseValue
```

`{Amount}` (the stack count) is **auto-injected** into the description — so
`"At the start of your turn, lose {Amount} HP..."` resolves to the live number. Add
custom vars by their `CanonicalVars` name (`{DamageIncrease}`). Formatters like
`{Amount:diff()}` per `mechanics.md`.

## Localization (ships in the .pck)

Table is **`powers`**. Add to `<ModName>/localization/eng/powers.json`. **Flat,
prefixed keys**, same ID derivation as relic/potion (`<PREFIX>-<SLUG>`, see
`recipes/relic.md`):

```json
{
  "<PREFIX>-<SLUG>.title":       "Display Name",
  "<PREFIX>-<SLUG>.description":  "At the start of your turn, lose {Amount} HP. Decrease by 1 each turn."
}
```

Icon: power atlas is a `.tres` (like potions); with no custom art it falls back to
`missing_power.png` — expected in M4, not a load failure (same finding as the potion
atlas). Override `CustomPackedIconPath` only when you have real art.

## Pre-flight checklist (catches the common silent failures)

- [ ] Class is `public sealed`, extends `CustomPowerModel` (or a vanilla power +
      `ICustomPower`).
- [ ] **NO `[Pool]` attribute** (powers aren't pooled — auto-discovered).
- [ ] Both abstract props overridden: `Type`, `StackType`.
- [ ] Correct hook overridden; turn hooks guard `participants.Contains(base.Owner)`.
- [ ] Modify-* hooks **return** a value and guard `props.IsPoweredAttack()` + owner/target.
- [ ] Turn hooks `await` all Cmds and consume a stack (`Decrement`/`TickDownDuration`)
      if the effect is per-stack / duration.
- [ ] `powers.json` has `<PREFIX>-<SLUG>.{title,description}` — **flat, prefixed keys**,
      table `powers`; `{Amount}` in the text if it scales.
- [ ] The card/relic that applies it uses `PowerCmd.Apply<<PowerName>>(...)`.
- [ ] `[T2MOD-SELFTEST]` marker logged on trigger (for tier-2 verify).

## Full worked example — a turn-start damage debuff (Poison-like)

```csharp
using System.Collections.Generic;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.ValueProps;

namespace EmberMod.EmberModCode.Powers;

public sealed class Smolder : CustomPowerModel        // id EMBERMOD-SMOLDER
{
    public override PowerType Type => PowerType.Debuff;
    public override PowerStackType StackType => PowerStackType.Counter;

    // "At the start of its turn, the creature loses Amount HP, then Smolder -1."
    public override async Task AfterSideTurnStart(CombatSide side,
        IReadOnlyList<Creature> participants, ICombatState combatState)
    {
        if (!participants.Contains(base.Owner))
            return;

        Flash();
        int dealt = base.Amount;                       // capture before Decrement changes it
        await CreatureCmd.Damage(new ThrowingPlayerChoiceContext(), base.Owner,
            dealt, ValueProp.Unblockable | ValueProp.Unpowered, null, null);
        if (base.Owner.IsAlive)
            await PowerCmd.Decrement(this);

        MainFile.Logger.Info($"[T2MOD-SELFTEST] Smolder fired: {dealt} dmg to {base.Owner}");
    }
}
```

`powers.json`:
```json
{
  "EMBERMOD-SMOLDER.title": "Smolder",
  "EMBERMOD-SMOLDER.description": "At the start of its turn, this creature loses {Amount} HP, then Smolder is reduced by 1."
}
```

Applied from a card's `OnPlay` (the card is the `cardSource` → pass `this`):
```csharp
await PowerCmd.Apply<Smolder>(choiceContext, cardPlay.Target, 5m, base.Owner.Creature, this);
```
From a **relic** hook instead, the source isn't a card — pass `null` for `cardSource`:
```csharp
await PowerCmd.Apply<Smolder>(choiceContext, target, 5m, Owner.Creature, null);
```

## Verify (tier-1 + tier-2)

1. Build (PckPacker uncommented) → tier-1 launch + grep the load marker
   (`verify.md`). A no-art power should load with the fallback icon — if load
   *errors*, that's a repair signal.
2. Tier-2 (user-guided, `verify.md`): a power can't be granted directly by console —
   grant the **card/relic that applies it** (`card add …` / `relic add …`), or use a
   vanilla applier, then enter combat, trigger it, and confirm the stacks appear on
   the creature + the effect fires. Re-grep for the `fired:` marker. (Automating this
   is M5.)
