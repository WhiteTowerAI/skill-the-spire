# Recipe: Potion

> A copy-adaptable, **known-good** pattern for a single STS2 potion. Every signature
> here was confirmed against decompiled `sts2.dll` + BaseLib — not guessed. Content
> facts (which effects exist, realistic numbers, vanilla analogs) come from
> `reference/potions-snapshot.md` (sourced from spire-codex). The skill fills only
> the **effect logic**; everything else (class skeleton, pool attribute,
> localization, base class) is templated.
>
> Vanilla potions to imitate: `BlockPotion` (self-buff), `FirePotion` (single-target
> damage), `StrengthPotion` (apply a Power). Pairs with `recipes/relic.md` — read the
> relic recipe's ID/loc-key rule; potions derive keys the same way.

## When to use

The request maps to a **potion** when it's a **one-shot consumable the player drinks/
uses**, not a passive item they own (relic) or a card they play. Phrasings: "a potion
that…", "when you drink it…", "a one-time…". Potions are **actively used** (there's a
Use action), so the effect fires in `OnUse` — there is **no combat-lifecycle hook**
like a relic's `AfterSideTurnStart`.

## Scaffold difference from relics (do this first)

The Alchyr content template scaffolds `Cards/`, `Powers/`, `Relics/` folders and a
mod base class for each — **but NOT `Potions/`**. So before authoring:

1. Create the folder `<ModName>Code/Potions/`.
2. Add a mod potion **base class** (mirrors the generated `<ModName>Relic` base — it
   resolves the packed image path). Potion art is a **`.tres` sprite atlas**, not a
   loose `.png` like relics, so during early milestones just let it fall back to the
   default icon (override `CustomPackedImagePath` only when you have real art — M4+):

```csharp
using BaseLib.Abstracts;      // CustomPotionModel

namespace <ModName>.<ModName>Code.Potions;

/// Base class for this mod's potions. Custom art (a .tres atlas) is an M4 concern;
/// leaving CustomPackedImagePath null falls back to the default potion icon.
public abstract class <ModName>Potion : CustomPotionModel
{
}
```

## The skeleton (fill only the marked spot)

Add ONE file under `<ModName>Code/Potions/<PotionName>.cs`:

```csharp
using System.Threading.Tasks;
using BaseLib.Utils;                                  // [Pool]
using MegaCrit.Sts2.Core.Commands;                    // CreatureCmd, PlayerCmd, PowerCmd
using MegaCrit.Sts2.Core.Entities.Cards;              // TargetType (potions share the card enum)
using MegaCrit.Sts2.Core.Entities.Creatures;          // Creature
using MegaCrit.Sts2.Core.Entities.Potions;            // PotionRarity, PotionUsage
using MegaCrit.Sts2.Core.GameActions.Multiplayer;     // PlayerChoiceContext
using MegaCrit.Sts2.Core.Models.PotionPools;          // SharedPotionPool + character pools
using MegaCrit.Sts2.Core.ValueProps;                  // ValueProp

namespace <ModName>.<ModName>Code.Potions;

[Pool(typeof(SharedPotionPool))]                      // REQUIRED — omitting it throws at registration
public sealed class <PotionName> : <ModName>Potion    // the mod base above (image path)
{
    public override PotionRarity Rarity => PotionRarity.Common;
    public override PotionUsage Usage  => PotionUsage.CombatOnly;   // or AnyTime / Automatic
    public override TargetType TargetType => TargetType.AnyPlayer;  // self-buff; AnyEnemy for damage

    protected override async Task OnUse(PlayerChoiceContext choiceContext, Creature? target)
    {
        AssertValidForTargetedPotion(target);         // guards null target for a targeted potion

        // ─────────── EFFECT LOGIC — the ONLY part the skill writes ───────────
        // (See "Effect building blocks". Pick the block matching SPEC's effect.)
        // ─────────────────────────────────────────────────────────────────────

        MainFile.Logger.Info("[T2MOD-SELFTEST] <PotionName> used: <what happened>");
    }
}
```

## The three abstract properties (all REQUIRED)

| Property | Type | Pick by |
|---|---|---|
| `Rarity` | `PotionRarity` = `None, Common, Uncommon, Rare, Event, Token` | SPEC; default `Common` |
| `Usage` | `PotionUsage` = `None, CombatOnly, AnyTime, Automatic` | `CombatOnly` for damage/block/most buffs; `AnyTime` for heal/max-HP/card gen; `Automatic` fires without manual use |
| `TargetType` | `TargetType` (shared with cards) | self-buff → **`AnyPlayer`** (potions target a player creature, NOT `Self`); one enemy → `AnyEnemy`; whole room → `AllEnemies` |

> ⚠️ Self-buff potions use **`AnyPlayer`**, not `Self`. Potion targeting differs from
> card targeting (see `PotionModel.IsValidTarget` in the decompile): a self potion
> still passes the owner's creature as `target`. Copy `BlockPotion` (`AnyPlayer`), not
> a card, for a self effect.

## Trigger

Override **`protected override async Task OnUse(PlayerChoiceContext choiceContext,
Creature? target)`** — this runs when the player uses the potion. There is no hook to
pick like relics; all potion effects go here. `target` is the chosen creature
(guaranteed non-null for a targeted potion after `AssertValidForTargetedPotion`);
`base.Owner` is the `Player` who drank it, `base.Owner.Creature` their body.

## Effect building blocks (confirmed APIs — literal-amount overloads)

Use the `decimal`+`ValueProp` overloads so you write plain numbers, not `DynamicVar`s.
**`ValueProp.Unpowered`** is the damage type for relics/potions/powers.

```csharp
// DAMAGE to the target enemy (TargetType.AnyEnemy):
await CreatureCmd.Damage(choiceContext, target, 20m, ValueProp.Unpowered, base.Owner.Creature, null);

// DAMAGE to all enemies (TargetType.AllEnemies) — pass the enemy list:
var enemies = target.CombatState.GetCreaturesOnSide(CombatSide.Enemy);   // needs ...Core.Combat
await CreatureCmd.Damage(choiceContext, enemies, 10m, ValueProp.Unpowered, base.Owner.Creature, null);

// BLOCK on the target player (TargetType.AnyPlayer):
await CreatureCmd.GainBlock(target, 12m, ValueProp.Unpowered, null);

// HEAL:
await CreatureCmd.Heal(target, 10m);

// APPLY A POWER (Strength/Dexterity/Weak/Vulnerable/Poison...):
await PowerCmd.Apply<StrengthPower>(choiceContext, target, 2m, base.Owner.Creature, null);
//   ^ power classes live in MegaCrit.Sts2.Core.Models.Powers; confirm the exact
//     class name via grounding.md (content: potions-snapshot; code: the decompile).

// ENERGY / DRAW (player-level; good for AnyTime utility potions):
await PlayerCmd.GainEnergy(2m, base.Owner);
await PlayerCmd.Draw(3, base.Owner);   // Draw's signature: maintainer to confirm + fold in (not yet canary-verified)
```

For an effect not listed, follow `grounding.md`: match the closest vanilla row in
`reference/potions-snapshot.md` for realistic numbers and check the rest of the pack
(`reference/mechanics.md`, `errors.md`) for the Cmd. If it's genuinely not in the
pack, report a pack gap — **do not guess a Cmd name** (the maintainer grounds new
Cmds offline).

## Localization (ships in the .pck)

Table is **`potions`** (not `relics`). Add to `<ModName>/localization/eng/potions.json`.
Keys are **FLAT and prefixed**, same derivation as relics, plus one potion-only key:

```json
{
  "<PREFIX>-<SLUG>.title":                 "Display Name",
  "<PREFIX>-<SLUG>.description":            "What the potion does, shown on hover.",
  "<PREFIX>-<SLUG>.selectionScreenPrompt":  "Prompt shown if the potion asks the player to choose."
}
```

`selectionScreenPrompt` is only needed if the effect prompts a choice (card select,
etc.); harmless to include a short one otherwise.

## ID / loc-key derivation (same rule as relics — MEMORIZE)

`Id.Entry = "<PREFIX>-<SLUG>"` where `SLUG = Slugify(ClassName)` (CamelCase split +
UPPER_SNAKE) and `PREFIX = <first namespace segment>.ToUpperInvariant()`. Class
`SwiftBrew` in namespace `SwiftBrew.*` → `SWIFTBREW-SWIFT_BREW`, so keys are
`SWIFTBREW-SWIFT_BREW.title` etc. — **flat string keys, not nested JSON.** The
`potions` LocTable is a flat `Dictionary<string,string>`. Override with
`[CustomID("EXACT-ID")]` if needed. (Full rationale in `recipes/relic.md`.)

## Rarity & pool

`[Pool(typeof(...))]` (from `BaseLib.Utils`) is **required** — omitting it throws the
same registration exception relics do (errors.md). Pools
(`MegaCrit.Sts2.Core.Models.PotionPools`):
- **`SharedPotionPool`** — colorless, any character. **Default choice** (46 of 63
  vanilla potions are here).
- `IroncladPotionPool`, `SilentPotionPool`, `DefectPotionPool`, `RegentPotionPool`,
  `NecrobinderPotionPool` — character-specific.

## Pre-flight checklist (catches the common silent failures)

- [ ] Created `<ModName>Code/Potions/` and the `<ModName>Potion` base class (template omits them).
- [ ] Class is `public sealed`, extends the mod potion base.
- [ ] `[Pool(typeof(SharedPotionPool))]` present (else BaseLib throws at registration).
- [ ] All three abstract props overridden: `Rarity`, `Usage`, `TargetType`.
- [ ] `TargetType` matches the effect (self-buff = `AnyPlayer`, not `Self`).
- [ ] `AssertValidForTargetedPotion(target)` first if the potion targets.
- [ ] Effect in `OnUse`; all `Cmd`s `await`ed; `ValueProp.Unpowered` for damage/block.
- [ ] `potions.json` has `<PREFIX>-<SLUG>.{title,description}` — **flat, prefixed keys**, table `potions`.
- [ ] `[T2MOD-SELFTEST]` marker logged in `OnUse` (for tier-2 verify) + the load marker in MainFile (tier-1).

## Full worked examples (verified vanilla, copy-adapt)

**Self-buff / block — `BlockPotion` (Common, AnyPlayer):**
```csharp
[Pool(typeof(SharedPotionPool))]
public sealed class BlockBrew : <ModName>Potion
{
    public override PotionRarity Rarity => PotionRarity.Common;
    public override PotionUsage Usage  => PotionUsage.CombatOnly;
    public override TargetType TargetType => TargetType.AnyPlayer;

    protected override async Task OnUse(PlayerChoiceContext choiceContext, Creature? target)
    {
        AssertValidForTargetedPotion(target);
        await CreatureCmd.GainBlock(target, 12m, ValueProp.Unpowered, null);
        MainFile.Logger.Info("[T2MOD-SELFTEST] BlockBrew used: +12 block");
    }
}
```

**Single-target damage — `FirePotion` (Common, AnyEnemy):**
```csharp
[Pool(typeof(SharedPotionPool))]
public sealed class Firebomb : <ModName>Potion
{
    public override PotionRarity Rarity => PotionRarity.Common;
    public override PotionUsage Usage  => PotionUsage.CombatOnly;
    public override TargetType TargetType => TargetType.AnyEnemy;

    protected override async Task OnUse(PlayerChoiceContext choiceContext, Creature? target)
    {
        AssertValidForTargetedPotion(target);
        await CreatureCmd.Damage(choiceContext, target, 20m, ValueProp.Unpowered, base.Owner.Creature, null);
        MainFile.Logger.Info("[T2MOD-SELFTEST] Firebomb used: 20 dmg to target");
    }
}
```
`potions.json`:
```json
{
  "FIREBOMB-FIREBOMB.title": "Firebomb",
  "FIREBOMB-FIREBOMB.description": "Deal 20 damage to target enemy."
}
```

## Verify (tier-1 + tier-2)

1. Build: PckPacker uncommented, `dotnet build -c Release` → `.dll`+`.pck` into
   `mods/<ModName>/`. (Details: `build.md`.) **Note:** potion art is a `.tres` atlas;
   without custom art the potion loads with the default icon — expected in M4, not a
   failure. If load *errors* on a missing atlas, that's a repair signal (`repair.md`).
2. Launch, grep `godot.log` for the load marker (tier-1).
3. Tier-2: dev console (backtick, auto-enabled when modded) → **`potion <PREFIX>-<SLUG>`**
   → in a combat, use the potion (target if needed) → confirm the effect and grep the
   `used:` marker.

> ⚠️ The potion console command is **`potion <id>`** — there is **no `add`/`remove`
> subcommand** (unlike `relic [add|remove] <id>`). It also matches the id **exactly**
> (uppercased), NOT by substring, so you must pass the full `<PREFIX>-<SLUG>` — e.g.
> `potion FIREBOMB-FIREBOMB`, not just `FIREBOMB`. A run must be in progress. Confirmed
> against `PotionConsoleCmd.cs` in the decompile.
