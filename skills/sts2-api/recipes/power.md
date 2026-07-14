# Recipe: Power

> A copy-adaptable, **known-good** pattern for a single STS2 power (a buff/debuff:
> Strength, Poison, Vulnerable…). Every signature here was confirmed against
> decompiled `sts2.dll` + BaseLib — not guessed. Reads the shared `reference/mechanics.md`
> for DynamicVars, SmartFormat descriptions, enums, and Counter amount domains;
> **read that first.**
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
using MegaCrit.Sts2.Core.Combat;                      // CombatSide, ICombatState
using MegaCrit.Sts2.Core.Commands;                    // CreatureCmd, PowerCmd
using MegaCrit.Sts2.Core.Entities.Creatures;          // Creature
using MegaCrit.Sts2.Core.Entities.Powers;             // PowerType, PowerStackType
using MegaCrit.Sts2.Core.Localization.DynamicVars;    // DynamicVar (only if you scale)
using MegaCrit.Sts2.Core.ValueProps;                  // ValueProp

namespace <ModName>.<ModName>Code.Powers;

// Extend the TEMPLATE base <ModName>Power, NOT CustomPowerModel directly. The template
// base overrides CustomPackedIconPath / CustomBigIconPath to the mod's loose-PNG icon
// paths; a direct CustomPowerModel subclass leaves them null, so a custom icon silently
// shows the default (verified live, 2026-07-08). No [Pool] attribute either way.
public sealed class <PowerName> : <ModName>Power
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
power auto-removed at exactly 0). Default `false` removes an existing power at 0 or
below after an amount change, but does **not** reject a negative first application.

## Amount domain (required for every custom Counter)

Copy the `amount domain` from `SPEC.md` before writing any mutation. Default to
nonnegative (`[0, unbounded]`). A signed domain is valid only when SPEC explains what
negative stacks do; implement that intent with `AllowNegative => true`. Record and
enforce finite lower/upper bounds in every gain or consumption path.

`PowerVar<T>` does not have min/max metadata, and `AllowNegative` is removal/display
behavior rather than input validation. The authored Cmd sequence must preserve the SPEC
domain; neither type can do it automatically.

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

`Decrement(this)` and `TickDownDuration(this)` operate on the already-present Power
instance, so they cannot create a missing negative instance. For variable or multi-stack
consumption initiated by another element, use the guarded pattern below instead.

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

### Consuming a nonnegative Counter (find, clamp, then modify)

`PowerCmd.Apply<T>` is for gaining/applying. **Never consume a nonnegative Counter with
`PowerCmd.Apply<T>(..., -N, ...)`.** When no instance exists, that call creates a new
Power at `-N`; `AllowNegative => false` does not block the first application.

For "consume up to N", find the mutable instance, clamp the actual spend to its current
amount, and modify that instance. This card-side example also records the real spend for
the effect marker (`using System;` supplies `Math`):

```csharp
int requested = Math.Max(0, base.DynamicVars["PowerSpent"].IntValue);
int spent = 0;
var power = base.Owner.Creature.GetPower<<PowerName>>();
if (power is { Amount: > 0 })
{
    spent = Math.Min(power.Amount, requested);
    await PowerCmd.ModifyAmount(choiceContext, power, -spent,
        base.Owner.Creature, this);
}

MainFile.Logger.Info(
    $"[T2MOD-SELFTEST] <CardName> played: spent {spent} <PowerName>");
```

At zero stacks, `GetPower<T>()` returns `null` and the code spends zero. With fewer than
N, it spends the available amount and `ModifyAmount` removes the Power at 0. With at least
N, it subtracts exactly N. A relic/potion uses the same sequence with its real owner and
`cardSource: null` where appropriate.

If SPEC declares a finite upper bound, clamp positive gains to the available headroom
before `Apply<T>` too: `headroom = Math.Max(0, max - current)` and
`gained = Math.Min(Math.Max(0, requested), headroom)`, then skip the Cmd when
`gained == 0`. Apply the same current-state clamp to either side of any finite signed
domain.

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
`recipes/relic.md`). ⚠️ **Powers need THREE keys, not two** — the Alchyr
`ModAnalyzers` package hard-fails the build (`STS001 ... .smartDescription not
found`) unless a power ships `.title` **and** `.description` **and**
`.smartDescription`. (Cards/potions need only `.title/.description`; relics add
`.flavor`.) At runtime `SmartDescription` falls back to `Description`, but the
build-time analyzer does not — so include it. Simplest: make `.smartDescription`
identical to `.description`:

```json
{
  "<PREFIX>-<SLUG>.title":            "Display Name",
  "<PREFIX>-<SLUG>.description":      "At the start of your turn, lose {Amount} HP. Decrease by 1 each turn.",
  "<PREFIX>-<SLUG>.smartDescription": "At the start of your turn, lose {Amount} HP. Decrease by 1 each turn."
}
```

Icon: the template base wires the power icon to a loose PNG under `images/powers/`
(`Exists()` + fallback to `missing_power.png`), so with no custom art it loads on the
default — not a failure. To ship art, drop a 256×256 PNG at `powers/<slug>.png` **and**
`powers/big/<slug>.png` (status icon + apply/expire notification) via
`gen_sprite.py --spec power`; see `reference/art-contract.md`.

## Pre-flight checklist (catches the common silent failures)

- [ ] Class is `public sealed`, extends the template base **`<ModName>Power`** (NOT
      `CustomPowerModel` directly — that breaks the custom icon; see the skeleton note).
- [ ] **NO `[Pool]` attribute** (powers aren't pooled — auto-discovered).
- [ ] Both abstract props overridden: `Type`, `StackType`.
- [ ] Every `Counter` has its SPEC amount domain implemented; signed behavior is explicit,
      and every finite bound is enforced.
- [ ] Correct hook overridden; turn hooks guard `participants.Contains(base.Owner)`.
- [ ] Modify-* hooks **return** a value and guard `props.IsPoweredAttack()` + owner/target.
- [ ] Turn hooks `await` all Cmds and consume a stack (`Decrement`/`TickDownDuration`)
      if the effect is per-stack / duration.
- [ ] `powers.json` has `<PREFIX>-<SLUG>.{title,description,smartDescription}` — **all
      THREE** (the analyzer `STS001`-fails without `.smartDescription`), **flat,
      prefixed keys**, table `powers`; `{Amount}` in the text if it scales.
- [ ] The card/relic that applies it uses `PowerCmd.Apply<<PowerName>>(...)`.
- [ ] Nonnegative Counter consumption finds an existing instance, clamps the spend, and
      uses `PowerCmd.ModifyAmount`; no negative `PowerCmd.Apply<T>`.
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

public sealed class Smolder : EmberModPower        // extends the template base; id EMBERMOD-SMOLDER
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

`powers.json` (**all THREE keys** — `.smartDescription` is what the STS001 analyzer
requires; omitting it fails the build even though it runs fine):
```json
{
  "EMBERMOD-SMOLDER.title": "Smolder",
  "EMBERMOD-SMOLDER.description": "At the start of its turn, this creature loses {Amount} HP, then Smolder is reduced by 1.",
  "EMBERMOD-SMOLDER.smartDescription": "At the start of its turn, this creature loses {Amount} HP, then Smolder is reduced by 1."
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
