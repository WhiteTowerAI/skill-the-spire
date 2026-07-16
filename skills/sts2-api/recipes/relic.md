# Recipe: Relic

> A copy-adaptable, **known-good** pattern for a single STS2 relic, distilled from
> the live-verified hand-built "Gambler's Coin" substrate proof. Every signature here
> was confirmed against decompiled `sts2.dll` + BaseLib 3.3.2 — not guessed. The
> goal: the skill fills only the **effect logic**; everything else (class skeleton,
> pool attribute, localization, image paths) is templated.
>
> Vanilla relics to imitate: `Lantern` (combat-start energy), `FurCoat` (seeded RNG).

## When to use

The user's request maps to a **relic** when it's a passive/triggered item the
player *owns* (not a card they play, not a one-shot potion). Triggers are combat-
or run-lifecycle events: "at the start of combat…", "whenever you play a card…",
"the first time each turn…", "at the start of each floor…".

If the relic remembers progress ("every N", "once per combat", "last turn", limited
uses), read `../reference/stateful-mechanics.md` before choosing a field or hook. The
state lifetime is part of the SPEC; it is not an implementation detail.

## The skeleton (fill only the marked spot)

Assume a mod scaffolded with `dotnet new alchyrsts2contentmod -n <ModName> -M <Author>`.
Add ONE file under `<ModName>Code/Relics/<RelicName>.cs`:

```csharp
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Utils;                              // [Pool]
using MegaCrit.Sts2.Core.Combat;                  // CombatSide, ICombatState
using MegaCrit.Sts2.Core.Commands;                // PlayerCmd, RelicCmd, DamageCmd, PowerCmd...
using MegaCrit.Sts2.Core.Entities.Creatures;      // Creature
using MegaCrit.Sts2.Core.Entities.Relics;         // RelicRarity
using MegaCrit.Sts2.Core.Models.RelicPools;       // SharedRelicPool + character pools
using MegaCrit.Sts2.Core.Random;                  // Rng

namespace <ModName>.<ModName>Code.Relics;

[Pool(typeof(SharedRelicPool))]                   // REQUIRED — omitting it throws at registration
public sealed class <RelicName> : <ModName>Relic  // <ModName>Relic is the template base (sets image paths)
{
    public override RelicRarity Rarity => RelicRarity.Common;

    // Pick the hook that matches the trigger (see "Trigger hooks" below).
    public override async Task AfterSideTurnStart(CombatSide side,
        IReadOnlyList<Creature> participants, ICombatState combatState)
    {
        // Standard combat-start guard: my owner is in this turn, and it's turn 1.
        var combat = Owner.PlayerCombatState!;     // non-null inside a combat hook
        if (!participants.Contains(Owner.Creature) || combat.TurnNumber > 1)
            return;

        Flash();                                   // visual: relic pulses on trigger

        // ─────────── EFFECT LOGIC — the ONLY part the skill writes ───────────
        // (Everything above/below is boilerplate. See "Effect building blocks".)
        // ─────────────────────────────────────────────────────────────────────
    }
}
```

## Localization (ships in the .pck)

Add entries to `<ModName>/localization/eng/relics.json`. **Keys are FLAT and
prefixed** — this is the #1 silent-failure footgun (see the ID rule below):

```json
{
  "<PREFIX>-<SLUG>.title":       "Display Name",
  "<PREFIX>-<SLUG>.description":  "What the relic does, shown on hover.",
  "<PREFIX>-<SLUG>.flavor":       "Flavor text."
}
```

## The ID / loc-key derivation rule (MEMORIZE — silent failure if wrong)

The final `Id.Entry` a relic gets, and therefore its loc keys and icon name:

1. **Base entry** = `ModelDb.GetEntry` = `StringHelper.Slugify(ClassName)` =
   split CamelCase on boundaries + UPPERCASE. `GamblersCoin` → `GAMBLERS_COIN`.
2. **Prefix** = BaseLib prepends `<first namespace segment>.ToUpperInvariant() + "-"`.
   Namespace `GamblersCoin.GamblersCoinCode.Relics` → first segment `GamblersCoin`
   → `GAMBLERSCOIN-`.
3. **Final** `Id.Entry` = `GAMBLERSCOIN-GAMBLERS_COIN`. So loc keys are
   `GAMBLERSCOIN-GAMBLERS_COIN.title` etc. — **flat string keys, not nested JSON.**
4. **Icon file** = prefix stripped + lowercased → `gamblers_coin.png` (the template
   base class resolves this; falls back to placeholder `relic.png` if missing).

Worked example → `GamblersCoin` class in namespace `GamblersCoin.*`:
- Id.Entry: `GAMBLERSCOIN-GAMBLERS_COIN`
- loc keys: `GAMBLERSCOIN-GAMBLERS_COIN.{title,description,flavor}`
- icon: `<ModName>/images/relics/gamblers_coin.png` (+ `_outline`, + `big/`)

To override the derived id, put `[CustomID("EXACT-ID")]` on the class.

## Trigger hooks (override the one matching the request)

All are `public virtual async Task` on `AbstractModel` (relics receive them because
`RelicModel.ShouldReceiveCombatHooks => true` — no interface, no manual subscribe).
There is NO `ICombatHook` to implement; just override the method.

| Request phrasing | Hook to override | Notes |
|---|---|---|
| "at the start of combat" | `AfterSideTurnStart(CombatSide, IReadOnlyList<Creature>, ICombatState)` | Guard `TurnNumber <= 1`. **This is the combat-start hook** — same one Lantern uses. Fires every turn otherwise. |
| "at the start of each turn" | `AfterSideTurnStart(...)` | Same hook, no TurnNumber guard (still guard `participants.Contains(Owner.Creature)`). |
| "every N turns" across combats | `AfterSideTurnStart(...)` | `[SavedProperty]` modulo progress; never clear it at combat end. See `stateful-mechanics.md`. |
| "on turn N" / "every N turns this combat" | start: `AfterSideTurnStart(...)`; end: `BeforeSideTurnEnd(...)` | Read `Owner.PlayerCombatState.TurnNumber` (`== N` or `% N == 0`); no saved counter. |
| "every N cards this turn" | `AfterCardPlayed(...)` + `BeforeSideTurnStart(...)` reset | Owner-card guard; ordinary turn-local field. |
| "once per combat" | the real trigger + `AfterRoomEntered(CombatRoom)` reset | Ordinary bool; reset only on combat entry. |
| pre-combat setup (no energy) | `BeforeCombatStart()` | Fires once before turn 1. **Do NOT grant energy here** — the turn-1 energy reset wipes it. |

> ⚠️ Do not use `BeforeCombatStart()` for energy. Confirmed: `PlayerCombatState`
> resets energy to max at turn start, so any energy added earlier is lost. Use
> `AfterSideTurnStart` + `TurnNumber <= 1`.

The `participants.Contains(Owner.Creature)` check is mandatory in multiplayer —
the hook fires for every side; act only when your owner's side is the one starting.

## Effect building blocks (confirmed APIs)

Namespaces: commands in `MegaCrit.Sts2.Core.Commands`, RNG in `...Core.Random`.

**Energy** (`PlayerCmd`, all `static async Task`, amount is `decimal`):
```csharp
int current = Owner.PlayerCombatState!.Energy;           // read current energy (int)
await PlayerCmd.GainEnergy(current, Owner);              // +current  => doubles it
await PlayerCmd.SetEnergy(0m, Owner);                    // set to exactly 0
await PlayerCmd.LoseEnergy(2m, Owner);                   // -2 (clamped at 0)
```

**Seeded RNG** (NEVER `System.Random` — breaks determinism/seed sharing):
```csharp
Rng rng = new(Owner, base.Id);      // deterministic per (run seed, relic id)
bool heads = rng.NextBool();        // 50/50
int roll   = rng.NextInt(3);        // 0,1,2
// add a mixin if the relic may roll repeatedly and you want distinct results:
Rng perTurn = new(Owner, base.Id, (uint)Owner.PlayerCombatState!.TurnNumber);
```

**Reaching the player / creature** from inside a relic hook:
```csharp
Player me       = Owner;                       // RelicModel.Owner (non-null in combat)
Creature myBody = Owner.Creature;
var combatState = Owner.PlayerCombatState!;     // Energy, MaxEnergy, TurnNumber
```

For other effects (damage, block, powers), query the rest of the pack rather than an
invented catalog: use `reference/mechanics.md` for shared Cmd/value foundations,
`reference/build-constraints.md` for enforced model rules, and `errors.md` for known
failure signatures. If the exact symbol is still absent, follow `grounding.md` and report
a pack gap — never guess a Cmd name.

**Always** call `Flash()` when the relic visibly triggers, and log a diagnostic marker.
The automated harness uses it to localize the trigger, but independently asserted state is
the Tier-2 proof:
```csharp
MainFile.Logger.Info($"[T2MOD-SELFTEST] <RelicName> fired: {outcome} energy {before} -> {after}");
```

## Rarity & pool

`RelicRarity` (`MegaCrit.Sts2.Core.Entities.Relics`): `None, Starter, Common,
Uncommon, Rare, Shop, Event, Ancient`. Use **`Common`** for a normal droppable
relic unless the request implies otherwise.

`[Pool(typeof(...))]` (from `BaseLib.Utils`) is **required**. Pools
(`MegaCrit.Sts2.Core.Models.RelicPools`):
- `SharedRelicPool` — colorless, drops for **any** character. **Default choice.**
- `IroncladRelicPool`, `SilentRelicPool`, `DefectRelicPool`, `RegentRelicPool`,
  `NecrobinderRelicPool` — character-specific.

## Pre-flight checklist (catches the common silent failures)

- [ ] Class is `public sealed`, extends the template `<ModName>Relic` base.
- [ ] `[Pool(typeof(SharedRelicPool))]` present (else BaseLib throws).
- [ ] `Rarity` overridden.
- [ ] Correct hook overridden; combat-start uses `AfterSideTurnStart` + `TurnNumber <= 1`.
- [ ] If stateful: event/threshold/phase/lifetime/reset/persistence match SPEC; run state
      uses `[SavedProperty]`, combat turns use `PlayerCombatState.TurnNumber`.
- [ ] `participants.Contains(Owner.Creature)` guard present.
- [ ] All `Cmd`/RNG calls `await`ed.
- [ ] `relics.json` has `<PREFIX>-<SLUG>.{title,description,flavor}` — **flat, prefixed keys**.
- [ ] Icon at `images/relics/<slug>.png` (+ `_outline`, + `big/`) or placeholder left in place.
- [ ] `[T2MOD-SELFTEST]` diagnostic marker logged on trigger; `SelfTest` asserts post-state.
- [ ] Stateful SelfTest proves `N-1`, threshold, reset/carry-over, and a
      `SavedProperties.From`/`Fill` round trip for run-persistent state.

## Full golden example (Gambler's Coin — verified firing in-game)

```csharp
[Pool(typeof(SharedRelicPool))]
public sealed class GamblersCoin : GamblersCoinRelic
{
    public override RelicRarity Rarity => RelicRarity.Common;

    public override async Task AfterSideTurnStart(CombatSide side,
        IReadOnlyList<Creature> participants, ICombatState combatState)
    {
        var combat = Owner.PlayerCombatState!;
        if (!participants.Contains(Owner.Creature) || combat.TurnNumber > 1)
            return;

        Flash();
        Rng rng = new(Owner, base.Id);
        bool heads = rng.NextBool();

        int before = combat.Energy;
        if (heads)
            await PlayerCmd.GainEnergy(before, Owner);   // double
        else
            await PlayerCmd.SetEnergy(0m, Owner);         // bust

        int after = combat.Energy;
        MainFile.Logger.Info($"[T2MOD-SELFTEST] GamblersCoin fired: {(heads ? "HEADS (double)" : "TAILS (bust)")} energy {before} -> {after}");
    }
}
```
`relics.json`:
```json
{
  "GAMBLERSCOIN-GAMBLERS_COIN.title": "Gambler's Coin",
  "GAMBLERSCOIN-GAMBLERS_COIN.description": "At the start of each combat, flip a coin. Heads: double your Energy. Tails: lose all your Energy.",
  "GAMBLERSCOIN-GAMBLERS_COIN.flavor": "Heads I win. Tails you lose."
}
```

## Verify (tier-1 + tier-2)

1. Build: uncomment `BSchneppe.StS2.PckPacker` in the csproj, `dotnet build -c Release`
   → `.dll`+`.pck` land in the game `mods/<ModName>/`. (Details: `build.md`.)
2. Launch `SlayTheSpire2.exe` (needs `steam_appid.txt`=`2868840` in game dir),
   grep `%APPDATA%\SlayTheSpire2\logs\godot.log` for `... loaded ok` (tier-1).
3. Tier-2: open the dev console with **`` ` ``** (auto-enabled when modded), run
   `relic add <PREFIX>-<SLUG>` in an active run, enter combat, grep the log for the
   `fired:` marker. (Details: `behavior-test.md`.)

