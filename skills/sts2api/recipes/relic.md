# Recipe: Relic

> A copy-adaptable RitsuLib pattern for a single STS2 relic. The skill fills
> only the effect logic; `ModRelicTemplate`, content-pack registration, localization, and
> `RelicAssetProfile` are adapter-owned.
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

If the Relic owns a custom Rest Site action, also read
`../reference/rest-site-options.md`. That reference owns the first singleplayer-only
free/fixed-Gold slice, final selection-time checks, repeatability, native stay/leave
lifecycle, and icon fallback. Do not adapt the ordinary combat-trigger skeleton below into
a Rest Site option by guessing UI methods.

If the Relic declares supplemental corner values, also read
`../reference/extra-corner-labels.md`. That reference owns the specs provider, safe-corner
and text bounds, refresh/removal, cleanup, and headed consumer proof.

If the request changes an existing vanilla Relic's fresh availability or pool membership,
resolve the target through `../reference/vanilla-overrides.md` and then read
`../reference/vanilla-availability-overrides.md`. That reference owns the promoted
singleplayer epoch-gate, pool-add, and pool-membership routes; do not replace the vanilla
model or add a second content registration.

## The skeleton (fill only the marked spot)

Add ONE file under `<ModName>Code/Relics/<RelicName>.cs`:

```csharp
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Combat;                  // CombatSide, ICombatState
using MegaCrit.Sts2.Core.Commands;                // PlayerCmd, RelicCmd, DamageCmd, PowerCmd...
using MegaCrit.Sts2.Core.Entities.Creatures;      // Creature
using MegaCrit.Sts2.Core.Entities.Relics;         // RelicRarity
using MegaCrit.Sts2.Core.Random;                  // Rng
using STS2RitsuLib.Scaffolding.Content;            // ModRelicTemplate, RelicAssetProfile

namespace <ModName>.Relics;

public sealed class <RelicName> : ModRelicTemplate
{
    public override RelicRarity Rarity => RelicRarity.Common;

    private static string RelicImage(string fileName) =>
        "res://<ModName>/images/relics/" + fileName;

    public override RelicAssetProfile AssetProfile => new(
        RelicImage("<slug>.png"),
        RelicImage("<slug>_outline.png"),
        RelicImage("big/<slug>.png"));

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

Add the same entries to `<ModName>/localization/<lang>/relics.json` for both `eng` and
`zhs`. Keys are flat and use the exact RitsuLib public entry:

```json
{
  "<MOD>_RELIC_<TYPE>.title": "Display Name",
  "<MOD>_RELIC_<TYPE>.description": "At the start of each combat, gain [blue]{Block}[/blue] [gold]Block[/gold].",
  "<MOD>_RELIC_<TYPE>.flavor": "It has weathered every storm."
}
```

```json
{
  "<MOD>_RELIC_<TYPE>.title": "显示名称",
  "<MOD>_RELIC_<TYPE>.description": "每场战斗开始时，获得[blue]{Block}[/blue]点[gold]格挡[/gold]。",
  "<MOD>_RELIC_<TYPE>.flavor": "它经受住了每一场风暴。"
}
```

Write the description in the Relic row of `reference/vanilla-text-style.md`: displayed numbers
in `[blue]` (declared in `CanonicalVars`, see the surface page § Displayed values), heals in
`[green]`, glossary terms in `[gold]`, Curses in `[red]`, Enchantment names in `[purple]`.
Title and flavor stay plain. Declare a tip in `AdditionalHoverTips` for every Power, keyword,
Card, or Orb the description names.

Register it exactly once in `MainFile.Content.cs`; the pool generic is its availability
contract:

```csharp
RitsuLibFramework.CreateContentPack(ModId)
    .Relic<SharedRelicPool, Relics.<RelicName>>()
    .Apply();
```

Only when SPEC selects `extra emphasis` beyond the default style, read
`reference/content-text-effects.md`. Relic descriptions may author balanced `blue`, `gold`,
`green`, `purple`, and `red` spans; the standard relic Hover Tip renders that same
description. Keep title and flavor plain.

## The ID / loc-key derivation rule

RitsuLib derives `Id.Entry` as `MOD_CATEGORY_TYPENAME`, normalizing every segment to
uppercase snake case. Mod id `GamblersCoin`, Relic class `GamblersCoin` becomes
`GAMBLERS_COIN_RELIC_GAMBLERS_COIN`; use that exact stem in `relics.json`. If a published
entry must survive a type rename, pass `ModelPublicEntryOptions.FromStem(...)` to the
content-pack registration. Do not add another id mechanism.

For custom icons, override `RelicAssetProfile` with the exact main, outline, and big paths
shown above. `gen_sprite.py` derives the 256x256 filled-white outline from final main alpha
using the shared 3% rule (8 pixels) without another acquisition call. RitsuLib checks each
path and retains its template/base-game fallback when a file is absent; leave the whole
profile empty in placeholder mode.

## Optional extra badges

Implement `IRelicExtraIconAmountLabelSpecsProvider` on the same Relic class. Return zero to
three `ExtraIconAmountLabelSpec.Plain(...)` or bounded `RichText(...)` entries in SPEC
order, using each of `TopLeft`, `TopRight`, and `BottomLeft` at most once. Preserve the
native bottom-right counter and the four-visible-character limit.

If badge text follows the Relic's displayed state, mutate that state and call
`InvokeDisplayAmountChanged()`. For a separate field with no host display refresh,
implement `IRelicExtraIconAmountLabelsChangeSource`, declare
`event Action? RelicExtraIconAmountLabelsInvalidated`, and invoke it once after the state
mutation. Returning no spec after the removal condition makes RitsuLib remove the label.
Do not poll or generate custom rectangles.

## Optional hidden inventory presence

For an owned Relic that must keep working while absent from the player's view (a dormant
form, a hidden curse), implement `STS2RitsuLib.Relics.Visibility.IModRelicVisibility` on the
same Relic class. Hiding removes only the UI presence: the inventory holder, its
flash animation, its hover tips, and the basic holder that reward, choose-a-relic, run
history, and unlock screens build. Hooks, state, and saves keep running.

Because the same check runs on offered and history copies, derive `IsRelicVisible` only from
Mod-owned state that the owned Relic sets, and keep it `true` by default:

```csharp
using STS2RitsuLib.Relics.Visibility;

public bool IsRelicVisible => !IsMutable || !_dormant;

private void SetDormant(bool dormant)
{
    _dormant = dormant;   // Mod-owned state; persist it per reference/stateful-mechanics.md
    RitsuLibFramework.RefreshRelicVisibility();
}
```

Call `RitsuLibFramework.RefreshRelicVisibility()` after every state change; it rebuilds the
active inventory and returns whether a holder was removed, added, or moved (`false` when nothing
changed or no run inventory exists). Never read `Owner` in the
getter: a canonical Relic has none. Hiding another Mod's or a vanilla Relic through the
global `RegisterRelicVisibilityRule` is not part of this route. Tier 2 asserts
`RitsuLibFramework.IsRelicVisible(relic)` before and after
each change, that `RefreshRelicVisibility()` reports a changed inventory, and that the
Relic's effect still resolves while hidden. Headed review confirms that the holder leaves
and returns with no empty slot, stale tooltip, or flash.

## Optional owned Rest Site action

Keep the Relic registered exactly once through the normal content pack. Add one separate
`ModRestSiteOptionTemplate` class and contribute it from the Relic's
`TryModifyRestSiteOptions`; the option itself is not content-pack registered.

Use the reference page's `ShouldOffer` / `CanPay` split. `TryModifyRestSiteOptions` owns
absence and duplicate prevention; `IsEnabled` owns native gray state; `OnSelect` repeats
the final eligibility/payment check before any command. A false result mutates nothing and
leaves the current Rest Site list intact. A true result awaits fixed Gold payment and the
deterministic outcome, marks once-per-run state only after success, and lets the native
host remove the selected option.

Put option title/description beside the Relic's keys in `relics.json`. A generated option
icon is one verified `rest_site_option` 256x169 image at
`images/rest_site_options/<slug>.png`. Resolve absence to the native Heal icon before
building `RestSiteOptionAssetProfile`; do not return a missing custom path.

## Optional shared capability routes

Keep ordinary Relic triggers in their matching override below. For a separable Relic-owned
behavior/state bundle, read `reference/model-capabilities.md`; for lifecycle/persistence/RNG, read
`reference/lifecycle-state-rng.md`; and for reachable per-hit attack, healing, Energy/Stars-gain
response, or maximum hand size, read `reference/shared-effect-hooks.md`. Implement on the Relic or
typed capability and preserve cadence, owner guard, phase/order, neutral behavior, reset/save, and
removal cleanup. Do not register a Relic-owned rule process-wide.

## Trigger hooks (override the one matching the request)

All are `public virtual async Task` on `AbstractModel` (relics receive them because
`RelicModel.ShouldReceiveCombatHooks => true` — no interface, no manual subscribe).
There is NO `ICombatHook` to implement; just override the method.

| Request phrasing | Hook to override | Notes |
|---|---|---|
| "at the start of combat": Block, damage, Energy | `AfterSideTurnStart(CombatSide, IReadOnlyList<Creature>, ICombatState)` | Guard `participants.Contains(Owner.Creature)` and `TurnNumber <= 1`, as Lantern does. It has **no `PlayerChoiceContext`**, so nothing that draws, selects, or asks the player belongs here. |
| "at the start of combat": apply a Power | `AfterRoomEntered(AbstractRoom room)` | Guard `room is CombatRoom`; the Power is on before turn 1, as Bronze Scales does. Pass `new ThrowingPlayerChoiceContext()` to `PowerCmd.Apply`. |
| "at the start of combat": more cards in the opening hand | `ModifyHandDraw(Player, decimal)` | Hook participation, guard `player == Owner` and `TurnNumber <= 1`, as Bag of Preparation does. |
| "at the start of combat/turn": draw after the opening hand, choose/discard/exhaust a Card, or anything else that needs a `PlayerChoiceContext` | `AfterPlayerTurnStart(PlayerChoiceContext choiceContext, Player player)` | Guard `player == Owner` (for a Power, `player == Owner.Player`) and, for combat start, `Owner.PlayerCombatState!.TurnNumber <= 1`, as Gambling Chip does. Runs after the Energy reset and the hand draw, before `AfterSideTurnStart`. |
| "at the start of each turn" | `AfterSideTurnStart(...)`, or `AfterPlayerTurnStart(...)` when it needs a `PlayerChoiceContext` | Same hooks, no TurnNumber guard (still guard the owner). |
| "every N turns" across combats | `AfterSideTurnStart(...)` | `SavedAttachedState<SpecificRelic, int>` modulo progress; never clear it at combat end. See `stateful-mechanics.md`. |
| "on turn N" / "every N turns this combat" | start: `AfterSideTurnStart(...)`; end: `BeforeSideTurnEnd(...)` | Read `Owner.PlayerCombatState.TurnNumber` (`== N` or `% N == 0`); no saved counter. |
| "every N cards this turn" | `AfterCardPlayed(...)` + `BeforeSideTurnStart(...)` reset | Owner-card guard; ordinary turn-local field. |
| "once per combat" | the real trigger + `AfterRoomEntered(CombatRoom)` reset | Ordinary bool; reset only on combat entry. |
| pre-combat setup (no energy) | `BeforeCombatStart()` | Fires once before turn 1. **Do NOT grant energy here** — the turn-1 energy reset wipes it. |

> ⚠️ Do not use `BeforeCombatStart()` for energy. Confirmed: `PlayerCombatState`
> resets energy to max at turn start, so any energy added earlier is lost. Use
> `AfterSideTurnStart` + `TurnNumber <= 1` (or `AfterPlayerTurnStart`, which also runs
> after the reset).

The `participants.Contains(Owner.Creature)` check is mandatory in multiplayer —
the hook fires for every side; act only when your owner's side is the one starting.

## SPEC `hook participation`: modify a value rather than act on a trigger

The hooks above are the relic *doing* something. A SPEC `hook participation` block is different:
the engine asks the relic for a number or a decision while resolving someone else's event, and
nothing fires. Read `reference/model-hook-participation.md` for the contract. A Relic reaches
both the run-scope and combat-scope sets — the widest reach of any surface here.

The one shape difference from a Power: **`Owner` is a `Player`, not a `Creature`.** So a subject
guard goes through `Owner.Creature`, and through `Owner.Osty` wherever the Osty can be the
subject. Vanilla `PenNib` checks both:

```csharp
public override decimal ModifyDamageMultiplicative(
    Creature? target, decimal amount, ValueProp props, Creature? dealer, CardModel? cardSource)
{
    if (!props.IsPoweredAttack()) return 1m;                        // SPEC `condition`
    if (dealer != Owner.Creature && dealer != Owner.Osty) return 1m; // SPEC `subject`
    return 2m;
}
```

A guard that checks only `Owner.Creature` silently stops applying the moment the player's Osty
is the one acting, which no single-value assertion catches.

For a **collection** participation (`try_modify_rewards` and its relatives), the bool reports only
that you touched the list — add or remove entries and return `true`, or return `false` untouched.
Preserve every entry you did not come for: vanilla `Midas` doubles gold rewards by rebuilding the
list with `Clear()` plus `AddRange()` of *everything*, transformed and untransformed alike. And do
not contribute a Rest Site option through the raw hook; use § Optional owned Rest Site action
above, which carries boundaries the bare hook does not.

## Effect building blocks (confirmed APIs)

Namespaces: commands in `MegaCrit.Sts2.Core.Commands`, RNG in `...Core.Random`.

Ordinary command signatures, return/rejection behavior, and lifecycle bounds live in
`reference/effect-primitives.md`. Select the exact async Relic hook first and bind only the inputs
its callback plus `Owner` truthfully supply. Absolute setters are setup/lifecycle control and are
not an ordinary Relic effect.

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

For an effect family outside the shared reference, query the rest of the pack rather than an
invented catalog. If the exact route is still absent, follow `grounding.md` § Mod-local Routes.

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

The pool is required once as the first generic argument to `.Relic<TPool,TRelic>()`.
Pools (`MegaCrit.Sts2.Core.Models.RelicPools`):
- `SharedRelicPool` — colorless, drops for **any** character. **Default choice.**
- `IroncladRelicPool`, `SilentRelicPool`, `DefectRelicPool`, `RegentRelicPool`,
  `NecrobinderRelicPool` — character-specific.

## Pre-flight checklist (catches the common silent failures)

- [ ] Class is `public sealed` and extends `ModRelicTemplate`.
- [ ] Exactly one `.Relic<TPool,TRelic>()` registration exists in `MainFile.Content.cs`.
- [ ] `Rarity` overridden.
- [ ] Correct hook overridden; combat-start uses `AfterSideTurnStart` + `TurnNumber <= 1`.
- [ ] If stateful: event/threshold/phase/lifetime/reset/persistence match SPEC; run state
      uses `SavedAttachedState<SpecificRelic, int/bool>` with a Mod-qualified name;
      combat turns use `PlayerCombatState.TurnNumber`.
- [ ] If it owns a Rest Site action: singleplayer guard, stable namespaced option ID,
      duplicate check, shared offer/payment predicate, final click-time recheck,
      success-only repeatability mutation, declared stay/leave behavior, and native Heal
      icon fallback all match `reference/rest-site-options.md`.
- [ ] `participants.Contains(Owner.Creature)` guard present.
- [ ] All `Cmd`/RNG calls `await`ed.
- [ ] `relics.json` has `<MOD>_RELIC_<TYPE>.{title,description,flavor}` flat keys.
- [ ] Main/derived-outline/big files exist at their exact paths and the three-field
      `RelicAssetProfile` is wired, or the placeholder profile is left empty.
- [ ] `[T2MOD-SELFTEST]` diagnostic marker logged on trigger; `SelfTest` asserts post-state.
- [ ] If it has extra badges: at most three unique safe corners, bounded visible text,
      exactly one refresh path per mutation, removal, and the native main counter preserved.
- [ ] Stateful SelfTest proves `N-1`, threshold, reset/carry-over, and a
      `SavedProperties.From`/`Fill` round trip for run-persistent state.

## Full golden example (Gambler's Coin — verified firing in-game)

```csharp
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Relics;
using MegaCrit.Sts2.Core.Random;
using STS2RitsuLib.Scaffolding.Content;

public sealed class GamblersCoin : ModRelicTemplate
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
  "GAMBLERS_COIN_RELIC_GAMBLERS_COIN.title": "Gambler's Coin",
  "GAMBLERS_COIN_RELIC_GAMBLERS_COIN.description": "At the start of each combat, flip a coin. Heads: double your [gold]Energy[/gold]. Tails: lose all your [gold]Energy[/gold].",
  "GAMBLERS_COIN_RELIC_GAMBLERS_COIN.flavor": "Heads I win. Tails you lose."
}
```
`zhs` description: `"每场战斗开始时，抛一枚硬币。正面：你的[gold]能量[/gold]翻倍。反面：失去所有[gold]能量[/gold]。"`

## Verify (tier-1 + tier-2)

1. Build with `tools/build.py`; it validates the pinned compat/runtime, packs resources,
   and deploys only the Mod's own artifacts.
2. Run `verify.md` Tier 1 and confirm the exact RitsuLib profile marker.
3. Run the `CombatPlayer` self-test. Obtain the Relic before combat, let the real
   `AfterSideTurnStart` hook fire, assert the concrete state delta, and grep the structured
   `state proof:` line. A `fired:` diagnostic alone is not Tier 2.

