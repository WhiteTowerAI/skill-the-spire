# Reference: the Tier 2 self-test kit

> Tier 2 runs inside the real game with nobody at the keyboard: the Mod drives itself from
> the main menu into the hosted scenario, fires its own content, and asserts the exact
> post-state. Every API here is public and pinned to STS2 `0.107.1` / RitsuLib `0.6.7`.
>
> **Two files.** `scaffold.py` generates `<ModName>Code/SelfTestKit.cs` and the arming line in
> `MainFile.Initialize()`. The kit is fixed code: Build rejects a hand-edited copy, and
> `scaffold.py --refresh-selftest-kit` rewrites it. You write only
> `<ModName>Code/SelfTestScenarios.cs`, which lists this Mod's checks.
>
> **Ship-safety.** The kit stays dormant unless the game starts with `--t2selftest`; a normal
> player launch never navigates, enters a room, or changes state.

## What the kit does on every run

1. **Roll call**, at the main menu. Every concrete model class in the Mod's assembly must be
   registered. For every Card, Relic, Potion, Power, Character, Monster, and Encounter, the
   player-facing text must exist and resolve in both `eng` and `zhs` through the real model
   consumer (the Compendium's `GetDescriptionForPile(PileType.None)` for a Card), with no raw
   key, empty value, or unresolved `{placeholder}`: titles, descriptions, flavor, selection
   prompts, Power smart descriptions, all fourteen `characters.json` keys, Monster names, and
   Encounter titles and loss lines. It restores the player's language and logs one `roll call:`
   line per model (a Card's id, pool, cost, type, rarity, target, and base numbers; a
   Character's HP, Gold, Energy, pools, starter deck, and Relics; a Monster's HP range; an
   Encounter's room and roster), with both titles. Compare those lines with SPEC.
2. **Navigation**: abandons an open run, starts a singleplayer run as the selected Character
   (`plan.Character<T>()`, matched by model type) or the first unlocked one, and waits for the
   run UI and the local Player.
3. **Scenarios in order**, except that `RunStart` scenarios run first. Each has its own budget. A failed assertion, an exception, or a
   timeout ends only that scenario: the kit logs its event trail and runs the next one.
4. **One shared combat.** Combat scenarios share a `CorpseSlugsWeak` fight with 999 Plating on
   the player. Before each one the kit removes the Cards it created from the Hand, returns the
   deck's Hand Cards to the Draw Pile, removes the player's Powers except Plating, clears
   Block, restores HP and Energy, and sets every enemy to 999/999 HP with no Powers or Block.
   When the combat ended, and right after an `Encounter` or `Custom` scenario, the kit starts a
   new combat and applies the same reset, so every scenario starts alike whatever ran before it. A scenario
   that asks for `freshCombat` or `beforeCombat` instead gets the new combat exactly as the
   host started it (opening Hand, combat-start Energy and Powers), with only the enemies set
   to 999 HP.
5. **Real plays.** `Play` uses `CardModel.TryManualPlay`, the same validation, Energy and Star
   payment, and play lifecycle as a player's click. Never use `CardCmd.AutoPlay` to prove a
   played Card: it pays nothing and runs the auto-play hooks instead.
6. **Settling, not sleeping.** After every action the kit waits until the action queue is
   empty and idle for two frames (`Settle()`), so no scenario needs a `Task.Delay`.
7. **Passive enemies.** `EndTurn()` stuns every enemy for that turn, so their moves (the
   slugs' Frail, attacks) cannot change what you measure. Pass `enemiesAct: true` when the
   scenario needs the enemy turn.
8. **Event trail.** RitsuLib lifecycle events record every Card played, drawn, discarded, and
   exhausted, Energy spent and gained, Relics obtained, and Potions procured during the
   scenario (`t.Trail`). A failed scenario prints its trail.
9. **Report.** A `selftest coverage:` line names any Mod Card never played, Relic or Potion
   never owned, Power never seen, Character never played, Monster never met, or Encounter never
   entered; a `selftest summary:` line lists every scenario with its result and seconds. Only when all pass does it log
   `state proof: kit summary passed=N/N scope=all` and `selftest done`.
10. **Watchdog.** A step stuck past its scenario budget ends the run with
    `selftest FAILED: timeout: scenario <name> stuck at '<step>'`.

`launch.py --self-test --only a,b` passes `--t2selftest=a,b`: only the named scenarios run (a
trailing `*` matches a prefix, `face.*` selects every face check), after the roll call. The
summary then says `scope=partial` and `grep_log.py` reports a partial pass, which is never the
final Tier 2.

## Which content gets which check

Tier 2 does not need a hand-written scenario per Card. Split the SPEC's content like this:

| Content | Check |
|---|---|
| Every model class (registered), and every Card, Relic, Potion, Power, Character, Monster, and Encounter (text) | roll call, automatic |
| A **simple Card**: its SPEC Implementation cites only its recipe and `reference/effect-primitives.md`, its numbers are fixed (no calculated value, X cost, or condition), and its effects are damage, Block, Energy, Stars, Gold, healing, HP loss, Max HP, draw, or a stack of an existing Power | `plan.FaceCheck<TCard>()`: one line, no assertions to write |
| Everything else: a custom Power, Keyword, Enchantment, or Orb; a `Hook:` or `Mod-local:` line; a condition, counter, or state across turns or combats; a Card choice; an interaction between elements; a Relic or Potion trigger | a named `plan.Combat(...)` scenario |
| A Monster and its Encounter | a named `plan.Encounter<TEncounter>(...)` scenario (§ The `CombatEnemy` scenario) |
| A Character's starting state | `plan.Character<T>()` and a named `plan.RunStart(...)` scenario (§ The `RunStart` + `CombatPlayer` scenario) |
| Events, Ancients, Rest Site options, Acts | a named `plan.Custom(...)` scenario (§ Other hosts) |
| Images, layout, animation, mouse/controller, wording, feel | headed review, never Tier 2 |

A face check plays the Card once and, when it can upgrade, once upgraded, then compares every
number on its face with what happened: `DamageVar` with the target's HP loss (each enemy for
`AllEnemies`, the total for `RandomEnemy`, times a `RepeatVar`), `BlockVar` with Block,
`EnergyVar` with Energy after payment, `CardsVar` with the Cards drawn, a Power variable
(`PowerVar<T>`, keyed by the Power's class name) with that Power's stacks on the target
(yourself for a `Self` Card), and `HealVar`, `HpLossVar`, `MaxHpVar`, `GoldVar`, `StarsVar`
with the player's matching value. It also requires the played Card in the Discard Pile, or
the Exhaust Pile when it has Exhaust. A variable it cannot read is listed as `not checked`;
give that Card a scenario. A face check reads the expected numbers from the Card itself, so
compare the roll call line with SPEC to catch a wrong base number.

## Writing `SelfTestScenarios.cs`

```csharp
using System.Linq;
using System.Threading.Tasks;
using <ModName>.Cards;
using <ModName>.Potions;
using <ModName>.Powers;
using <ModName>.Relics;
using MegaCrit.Sts2.Core.Entities.Cards;

namespace <ModName>;   // the same namespace as MainFile.cs

internal static partial class SelfTestScenarios
{
    static partial void Define(SelfTestPlan plan)
    {
        plan.FaceCheck<EmberStrike>()
            .FaceCheck<EmberGuard>();

        plan.Combat("kindling_burns_all_enemies_next_turn", async t =>
        {
            await t.Play<Kindling>();
            t.Proof(t.PowerAmount<KindlingPower>(t.Me) == 3,
                $"kindling stacks expected=3 observed={t.PowerAmount<KindlingPower>(t.Me)}");
            var before = t.Enemies.ToDictionary(enemy => enemy, enemy => enemy.CurrentHp);
            await t.EndTurn();
            var lost = before.Select(pair => pair.Value - pair.Key.CurrentHp).ToList();
            t.Proof(lost.All(hp => hp == 3), $"turn-start damage expected=3 each observed={string.Join(",", lost)}");
        });
    }
}
```

Name each scenario after the SPEC behavior in `snake_case`; names must be unique, and
`--only` uses them. Put every expected value from SPEC, never from an observed run. Each
`t.Proof(condition, observation)` logs `state proof: <scenario>: <observation>` when it holds
and fails the scenario when it does not, so write the observation with both the expected and
the observed value.

### `SelfTestPlan`

- `FaceCheck<TCard>()`: the face check above, scenario `face.<TCard>`.
- `Combat(name, body, budgetSeconds = 30, freshCombat = false, beforeCombat = null)`: a
  player-combat scenario. `beforeCombat` runs out of combat, before a fresh combat starts;
  giving it implies `freshCombat`.
- `RunStart(name, body, budgetSeconds = 30)`: runs before any combat and sees the run as it
  started.
- `Encounter<TEncounter>(name, body, budgetSeconds = 60, keepPlayerHp = false)`: enters the Mod's
  Encounter with its real roster; no Plating; the player at 999/999 HP unless `keepPlayerHp`.
- `Custom(name, body, budgetSeconds = 60)`: a scenario that enters its own room (§ Other hosts);
  the kit first finishes any combat in progress.
- `Character<TCharacter>()`: start the run as this Character.

### `SelfTestRun t`

- State: `t.Player`, `t.Me` (the player Creature), `t.Combat` (`PlayerCombatState`), `t.State`
  (the combat state), `t.Enemies`, `t.Enemy` (the first hittable enemy), `t.Token`, `t.Trail`,
  `t.PowerAmount<TPower>(creature)`.
- `t.Proof(condition, observation)`.
- `await t.AddToHand<TCard>(upgraded: false)` creates a live copy in the Hand;
  `await t.Play(card, target)` plays a Hand Card; `await t.Play<TCard>(target, upgraded)` does
  both. An `AnyEnemy` Card without a target uses `t.Enemy`. Play tops Energy up to the cost
  when it is short, so assert Energy from `t.Trail.EnergySpent`, not from a raw before/after.
- `await t.ObtainRelic<TRelic>()` and `await t.UsePotion<TPotion>(target)`; the kit removes a
  scenario's Relics and leftover Potions when it ends.
- `using var choices = t.ScriptChoices(offered => ...)` answers every Card choice until disposed;
  `choices.OfferedCounts` and `choices.Picked` record what the host asked.
- `await t.EndTurn(enemiesAct: false)` ends the turn and waits for the next player Play phase.
- `await t.StartNewCombat()` finishes this combat and starts another, so turn 1 and
  combat-start triggers fire again inside one scenario.
- `await t.Settle()` and `await t.ClearDebuffs(creature)`.
- Enemies: `t.Monster<TMonster>()` (the live Creature; the scenario fails when it is absent),
  `t.NextMove(monster)` (its next `MoveState`, with `Intents`), and
  `await t.EnemyTurn(monster, "MOVE_ID")` (§ The `CombatEnemy` scenario).
- Run start: `t.DeckCounts()` (Card class name to count), `t.RelicNames()`, and
  `t.Describe(counts)` (`AxN,BxM` in name order).

Any other public STS2 or RitsuLib API works inside a body: snapshot state, drive the real
source, `await t.Settle()`, then assert.

## Combat scenario recipes

### relic — a combat-start trigger

A combat-start hook (`AfterSideTurnStart` with `TurnNumber <= 1`, `AfterPlayerTurnStart`,
`AfterRoomEntered`) fires only when the Relic is owned before combat starts, so obtain it in
`beforeCombat`. When that hook asks for a Card choice, open `t.ScriptChoices` in
`beforeCombat` and keep it until the body ends.

```csharp
plan.Combat("lantern_combat_start_energy", t =>
{
    t.Proof(t.Combat.Energy == t.Combat.MaxEnergy + 1,
        $"combat-start energy expected={t.Combat.MaxEnergy + 1} observed={t.Combat.Energy}");
    return Task.CompletedTask;
}, beforeCombat: async t => await t.ObtainRelic<Lantern>());
```

A Relic that reacts during combat (on Card played, on damage taken) is obtained inside the body
instead, then driven by the real source.

### potion

```csharp
plan.Combat("tonic_damage", async t =>
{
    var enemy = t.Enemy;
    int hp = enemy.CurrentHp;
    await t.UsePotion<Tonic>(enemy);
    t.Proof(hp - enemy.CurrentHp == 10, $"potion damage expected=10 observed={hp - enemy.CurrentHp}");
});
```

### card that asks the player to choose — script the selection

`CardSelectCmd.FromHand`, `FromCombatPile`, `FromSimpleGrid`, `FromChooseACardScreen`, and
deck selections ask the selector the kit installs, so no screen waits for a click. The Hand
starts empty (except in a `freshCombat` scenario): add every Card the choice needs. `FromHand` returns the whole filtered Hand
without asking when it holds no more Cards than the minimum, so give a one-of choice at least
two candidates and assert what was offered.

```csharp
plan.Combat("sift_exhausts_the_chosen_card", async t =>
{
    var chosen = await t.AddToHand<Defend>();
    var other = await t.AddToHand<Strike>();
    var sift = await t.AddToHand<Sift>();
    using var choices = t.ScriptChoices(offered => offered.Where(card => card == chosen));
    await t.Play(sift);
    t.Proof(choices.OfferedCounts.SequenceEqual(new[] { 2 }) && chosen.Pile?.Type == PileType.Exhaust
            && other.Pile?.Type == PileType.Hand,
        $"offered={string.Join(",", choices.OfferedCounts)} chosen={chosen.Pile?.Type} other={other.Pile?.Type}");
});
```

The selector skips the screen, so the prompt text and screen layout stay headed-review items.

### custom Power and multi-element interactions

There is no `combo` model. Drive the real source exactly as a player would, then walk SPEC's
`interactions` in dependency order and assert each dependent state with its own `t.Proof`,
so a broken edge is localized. A Power whose hook is `AfterSideTurnStart` for its owner's side
fires at the start of the owner's next turn: play the source, `await t.EndTurn()`, then assert.
When the dependent fires on the enemy's turn (an enemy-side debuff, a reaction to the enemy's
attack), use `await t.EndTurn(enemiesAct: true)` so that turn runs as the host plays it.

### stateful relic cadence — prove the lifetime, not only one trigger

Use the live Relic instance from `ObtainRelic` and advance real turns and combats; never set the
counter from the harness. A run-persistent counter (Happy Flower shape, `N = 3`): obtain the
Relic in `beforeCombat`, assert progress after turn 1, `await t.EndTurn()` and assert the
below-threshold state with no effect, round-trip the saved state into a fresh mutable copy
(`SavedProperties.From(live)` then `saved.Fill(restored)`, `using MegaCrit.Sts2.Core.Saves.Runs;`),
then `await t.StartNewCombat()` and assert the threshold effect at turn 1 of the new combat.
A combat-local turn counter (Stone Calendar shape): assert no effect at turn 1, `EndTurn` to the
specified turn and assert the exact delta, then `StartNewCombat` and assert `TurnNumber == 1`
with no second activation. One `t.Proof` per invariant keeps a wrong lifetime distinguishable
from a wrong effect.

### State-consuming Counter interactions — test the amount domain

A `consumes` edge for a nonnegative Counter runs three cases in one scenario, driving the real
consumer each time: zero stacks (no instance is created), fewer than N (the amount is consumed
and the Power removed at zero), and at least N (exactly N consumed, the remainder kept). Remove
any existing instance first, `PowerCmd.Apply<TPower>(new ThrowingPlayerChoiceContext(), t.Me, 2m, t.Me, null)`
to set up a case, `await t.Play<TConsumer>()`, and assert after every case that no negative
amount exists. When N is 1, zero is also the only fewer-than-N case.

### calculated-value Card — preview, raw request, final state, and headed text

Read `reference/card-computed-values.md` and keep all cases in one scenario. For each case set
deterministic combat state, call `card.UpdateDynamicVarPreview(CardPreviewMode.Normal, target,
card.DynamicVars)`, record the matching `PreviewValue`, then `await t.Play(card, target)` and
assert the exact HP, Block, Energy, Stars, or Power delta. Also inspect the raw execution request
through the matching `Compute*Value` extension, which tells a wrong formula from a hook applied
zero or two times. Cover zero, positive, and changing inputs and an upgraded Card. Apply
Strength/Vulnerable for Damage and Dexterity/Frail for Block, one modifier family at a time, and
require the final preview to equal the observed result. For Power, obtain `SneckoSkull`, use raw
Poison 2, and separately prove raw `ComputedPower<PoisonPower>` 2, amount-given preview 3, and
final target Poison 3. A calculated Card never takes a face check.

The structured proof does not establish presentation. In the same headed combat the reviewer
inspects the real hand Card at zero, positive, changed, and upgraded states; confirms Energy 0 is
`0` plus one Energy icon while Stars 0 is empty; and checks multiple icons, maximum-count reflow,
clipping, the localized variable tooltip, and the omitted-icon fallback.

### advanced Card/Potion targeting — prove each lifecycle separately

Read `advanced-targeting.md` and keep its three-consumer matrix in one scenario: source-aware
single Card, single Potion, and player-aware multi Card. Do not add a multi Potion or infer its
lifecycle from another consumer. Use at least two live enemies and establish zero/one/multiple
candidate states through public combat Cmds. For each consumer assert the registered target kind,
the resolved creature combat ids, before/after values, and the diagnostic target id. Snapshot
Energy, Stars, Potion belt membership, and the source Card pile before boundary cases: a normal
cancel and a target that turns invalid while queued leave payment and Potion state unchanged, and
a successful Card reaches its result pile. Mouse and controller selection, invalid-target
rejection, and multi reticles stay headed checks.

### Gameplay readability, custom Card Piles, and other capabilities

Hand emphasis (`reference/card-hand-emphasis.md`): place the real Card in the Hand, change the
actual condition state, and assert no-active, single-active, conflict winner, playability, and
Hand entry/exit; the outline color itself is a headed or live-node observation. Relic/Power
corner labels (`reference/extra-corner-labels.md`): assert the exact zero/one/bounded label
sequence, visible text, safe corners, refresh source, removal, and the unchanged main amount.
Custom Card Piles (`reference/card-piles.md`): assert each selected pile's identity, owner, exact
Card instances and order, entry/exit outcomes, rejections, reset/save behavior, and any
deterministic open/view/callback state; for manual ExtraHand play also assert payment, cancel
restoration, the result pile, callback counts, and that the next Card can enter the same native
play flow. Each capability reference names its own proof matrix; derive only the cases SPEC
selected.

When the user reserves headed review, build and deploy the focused proof, give them the exact
console setup and observation matrix, and record their reported result separately.

## The `CombatEnemy` scenario (`plan.Encounter`)

Enemy-side content (a Monster and the Encounter that spawns it) is proven through the enemy:
enter the Mod's own Encounter, confirm its Monster spawned, let the enemy act, and observe the
state it changed.

`plan.Encounter<TEncounter>(name, body)` finishes any combat in progress, enters a fresh mutable
copy of the Encounter with its real roster and HP, and waits for the player's Play phase. It
applies no Plating, so the enemy's hits land, and raises the player to 999/999 HP so a long cycle
cannot end the run; pass `keepPlayerHp: true` when a move reads the player's HP. The next `Combat`
scenario starts a fresh kit combat. The roll call already lists every Mod Monster (`hp=min-max`)
and every Encounter an Act or a scenario names, with its roster.

`await t.EnemyTurn(monster, "MOVE_ID")` drives one real enemy turn: it asserts the Monster's
`NextMove.Id`, ends the player turn with enemies acting, waits for the next player Play phase,
asserts from combat history (`MonsterPerformedMoveEntry`) that the Monster performed exactly that
move, and returns `SelfTestEnemyTurn(MoveId, PlayerHpLost, Hits, UnblockedDamage)`. `Hits` counts
the new `CreatureAttackedEntry.DamageResults`, so a multi-hit move is proven by its hit count,
not by an HP total. Never call move bodies, `PerformMove`, `SetMoveImmediate`, or
`ForceCurrentState` to prove a move; those bypass normal enemy turn selection.

```csharp
plan.Encounter<EmberHoundEncounter>("ember_hound_bites_for_6", async t =>
{
    var hound = t.Monster<EmberHound>();          // fails the scenario when it did not spawn
    var bite = await t.EnemyTurn(hound, "BITE");
    t.Proof(bite.PlayerHpLost == 6 && bite.Hits == 1,
        $"bite expected hp=6 hits=1 observed={bite.PlayerHpLost}/{bite.Hits}");
});
```

The monster's own move body may log `attacked:` for diagnosis; it is never proof.

### Multi-turn move vocabulary

For a multi-move SPEC, drive the real enemy turn repeatedly and read each move's intents from
`t.NextMove(monster).Intents` before its turn. For the representative cycle in
`recipes/monster.md` (`MUSTER -> PRESSURE -> FLURRY -> HEALTH_BRANCH -> GUARD|RECOVER -> MUSTER`):

```csharp
plan.Encounter<<Name>Encounter>("<name>_cycle_and_branches", async t =>
{
    var mob = t.Monster<<Name>>();
    t.Proof(t.NextMove(mob).Intents.OfType<BuffIntent>().Count() == 1, "MUSTER intent expected=buff observed=match");
    await t.EnemyTurn(mob, "MUSTER");
    t.Proof(t.PowerAmount<<CustomBuff>>(mob) == 2,
        $"self power expected=2 observed={t.PowerAmount<<CustomBuff>>(mob)}");

    var pressureIntents = t.NextMove(mob).Intents;
    t.Proof(pressureIntents.OfType<SingleAttackIntent>().Count() == 1 &&
            pressureIntents.OfType<DebuffIntent>().Count() == 1,
        "PRESSURE intents expected=attack+debuff observed=match");
    var pressure = await t.EnemyTurn(mob, "PRESSURE");
    t.Proof(pressure.PlayerHpLost == 5 && t.PowerAmount<WeakPower>(t.Me) == 2,
        $"attack+debuff expected=5/2 observed={pressure.PlayerHpLost}/{t.PowerAmount<WeakPower>(t.Me)}");

    var multi = t.NextMove(mob).Intents.OfType<MultiAttackIntent>().SingleOrDefault();
    t.Proof(multi?.Repeats == 2, $"FLURRY repeats expected=2 observed={multi?.Repeats}");
    var flurry = await t.EnemyTurn(mob, "FLURRY");
    t.Proof(flurry.Hits == 2 && flurry.PlayerHpLost == 8,
        $"multi-attack expected=2/8 observed={flurry.Hits}/{flurry.PlayerHpLost}");

    // At full health the branch must choose GUARD.
    int blockBefore = mob.Block;
    await t.EnemyTurn(mob, "GUARD");
    t.Proof(mob.Block - blockBefore == 5, $"healthy branch block expected=+5 observed={mob.Block - blockBefore}");

    // Change the branch's real input through a public Cmd, without forcing a move state.
    int woundedHp = Math.Max(1, mob.MaxHp / 2 - 1);
    await CreatureCmd.Damage(new ThrowingPlayerChoiceContext(), mob, mob.CurrentHp - woundedHp,
        ValueProp.Unblockable | ValueProp.Unpowered, t.Me, null);
    t.Proof(mob.CurrentHp == woundedHp, $"branch setup hp expected={woundedHp} observed={mob.CurrentHp}");

    // Traverse the cycle again. The stacked buff must change later attack damage.
    await t.EnemyTurn(mob, "MUSTER");
    t.Proof(t.PowerAmount<<CustomBuff>>(mob) == 4,
        $"stacked self power expected=4 observed={t.PowerAmount<<CustomBuff>>(mob)}");
    pressure = await t.EnemyTurn(mob, "PRESSURE");
    t.Proof(pressure.PlayerHpLost == 7 && t.PowerAmount<WeakPower>(t.Me) == 2,
        $"buffed attack+debuff expected=7/2 observed={pressure.PlayerHpLost}/{t.PowerAmount<WeakPower>(t.Me)}");
    flurry = await t.EnemyTurn(mob, "FLURRY");
    t.Proof(flurry.Hits == 2 && flurry.PlayerHpLost == 12,
        $"buffed multi-attack expected=2/12 observed={flurry.Hits}/{flurry.PlayerHpLost}");

    int hpBeforeRecover = mob.CurrentHp;
    blockBefore = mob.Block;
    await t.EnemyTurn(mob, "RECOVER");
    t.Proof(mob.CurrentHp - hpBeforeRecover == 3 && mob.Block - blockBefore == 4,
        $"wounded branch heal+block expected=3/4 observed={mob.CurrentHp - hpBeforeRecover}/{mob.Block - blockBefore}");
}, budgetSeconds: 120);
```

The scenario needs `MegaCrit.Sts2.Core.MonsterMoves.Intents`, `MegaCrit.Sts2.Core.Models.Powers`,
`MegaCrit.Sts2.Core.GameActions.Multiplayer`, and `MegaCrit.Sts2.Core.ValueProps`.

Adapt move ids, numbers, Power types, and branch setup to SPEC. The important invariants are:

- inspect `NextMove` intents before the turn and the matching
  `MonsterPerformedMoveEntry` afterward;
- prove self Power attachment **and** a later changed result;
- assert target debuff amount immediately after the composite move;
- wound through a public Cmd, then assert exact heal/Block deltas;
- prove multi-hit with `CreatureAttackedEntry.DamageResults.Count` (HP total alone is not a
  repeat count);
- drive every advertised branch through its real predicate and traverse enough turns to
  demonstrate the explicit cycle.

> The `PlayerCmd.EndTurn` gate matches `CombatRoomHandler`'s AutoSlay loop: after the enemy
> turn, control returns to the player at `Phase == Play`. The monster's attack must use
> `DamageCmd.Attack(n).FromMonster(this).Execute(null)`; the card `.Targeting(target)` chain
> hangs the enemy turn and the second gate times out (`selftest FAILED: player play phase not
> resumed after enemy turn`). Needs `using MegaCrit.Sts2.Core.Map;` for `MapPointType`.

## The `RunStart` + `CombatPlayer` scenario (Character Foundation)

A character is not proven by `ModelDb` registration alone. The harness must select its
real UI button, start a run as it, assert the starter ecosystem, then enter combat and
prove one hosted mechanic. `plan.Character<<CharacterName>>()` makes the kit select the real
button by model type (placeholder art keeps the fallback `%Icon` texture, so a path match finds
nothing) and confirm it; the setup fails when that button is missing or locked. The roll call
already resolves all fourteen `characters.json` keys in both languages and logs one
`roll call: character` line with the canonical HP, Gold, Energy, pools with their sizes, starter
deck, and starter Relics; compare it with SPEC.

`plan.RunStart(name, body)` scenarios run first, whatever their position in the plan, and see the
live run exactly as it started. Assert concrete runtime state rather than only the canonical
declarations:

```csharp
plan.Character<<CharacterName>>();
plan.RunStart("<character>_run_start", t =>
{
    var player = t.Player;
    t.Proof(player.Character is <CharacterName> && t.Me.CurrentHp == <HP> && t.Me.MaxHp == <HP> &&
            player.Gold == <GOLD>,
        $"run start expected=<CharacterName> hp=<HP>/<HP> gold=<GOLD> observed=" +
        $"{player.Character.GetType().Name} hp={t.Me.CurrentHp}/{t.Me.MaxHp} gold={player.Gold}");
    var deck = t.Describe(t.DeckCounts());      // "ClassNamexCount" in name order
    t.Proof(deck == "<StarterDefend>x4,<StarterStrike>x4,<Signature>x1",
        $"starter deck expected=<StarterDefend>x4,<StarterStrike>x4,<Signature>x1 observed={deck}");
    t.Proof(t.RelicNames().SequenceEqual(new[] { "<StarterRelic>" }) && !player.Potions.Any(),
        $"starter relics expected=<StarterRelic> potions=0 observed={string.Join(",", t.RelicNames())}");
    // Also assert the concrete CardPool/RelicPool/PotionPool types and their membership.
    return Task.CompletedTask;
});
```

Then a `plan.Combat(..., freshCombat: true)` scenario (a new kit combat in its Play phase,
with the turn-1 starter effects intact) asserts both designed energy and the independent
starter behavior, here a turn-1 starter Relic:

```csharp
plan.Combat("<character>_combat_energy", t =>
{
    t.Proof(t.Combat.MaxEnergy == 3 && t.Combat.Energy == 4,
        $"combat energy expected max/current=3/4 observed={t.Combat.MaxEnergy}/{t.Combat.Energy}");
    return Task.CompletedTask;
}, freshCombat: true);
```

The Character's starter Cards are simple Cards like any other: give them face checks. A starter
Relic that acts when a combat ends uses `t.StartNewCombat()`, which finishes the combat first.

When static presentation is selected, do not stop at model properties. In the same run,
assert the visible 132x195 selection portrait and 1920x1200 background; 512x512 non-Spine
combat body; normal and outlined 88x88 top-panel textures under the same real
`NTopBarPortrait`; one native counter with five 256x256 energy layers; and the 24x24 compact
icon in a real hand card. Also assert each generated Relic's exact 256x256 main/outline
textures under the same real `NRelic`, plus its explicit big-icon path. Compare the
CharacterModel main/outline texture properties to the same top-icon paths so a decorative
proof-only node cannot hide broken RitsuLib wiring. Then finish combat and enter RestSite and Shop
to assert the real `NRestSiteCharacter` and `NMerchantCharacter` with their 512x512 bodies.
Capture settled selection, combat/top-panel/energy, RestSite, and Shop screenshots. Structured
state cannot see placement, so these are what the maintainer and the user review; a real run
whose node assertions all passed still showed a spinning Energy ring, an oversized health bar,
and a sunken merchant body. Save each after a short settle delay:

```csharp
private static void Capture(string name)
{
    var directory = OS.GetUserDataDir() + "/<modname>_selftest";
    DirAccess.MakeDirRecursiveAbsolute(directory);
    var path = $"{directory}/{name}.png";
    ((SceneTree)Engine.GetMainLoop()).Root.GetViewport().GetTexture().GetImage().SavePng(path);
    MainFile.Logger.Info($"[T2MOD-SELFTEST] <ModName> screenshot: {path}");
}
```

Also assert the combat body's `%Bounds` width equals its opaque width times 0.80 within 2 px
(`reference/character-presentation.md`); the health bar takes that width.

For the Card/UI theme, replace the shared compact-icon assertion with two
independent consumers. Assert the Character/card-pool properties equal all four theme
colors; `PoolFrameMaterial` is the cached theme `ShaderMaterial` with exact
`target_color`/`brightness`; `BigEnergyIconPath` and `TextEnergyIconPath` are distinct,
existing, and load as 256x256/24x24 textures; a visible real `NCard.%EnergyIcon` uses the
large path; and a real formatted card description embeds the text path. Emit
`character theme expected=colors/frame/large-icon/text-icon observed=all` only after every
assertion succeeds. Automatic node/property proof is required even when the maintainer
chooses to perform the focused visual review manually.

For bounded Character combat cues, read `reference/character-combat-cues.md` and keep the
proof independent from the static/theme marker. Assert all twenty-four exact 512x512 paths,
shared style plus Bounds/Intent/Center/Orb/Talk geometry,
Idle advance/loop, Attack trigger and return to Idle, damage-triggered Hit and return to
Idle, first-combat playback-node cleanup, and Dead's contracted duration/final-frame hold
in a fresh combat. Emit
`character combat cues complete expected=Idle/Attack/Hit/Dead/cleanup observed=all` only
after every assertion succeeds.

Run one separate missing-frame variant. Omit exactly one expected frame and assert that the
entire private cue set is unavailable, the exact static 512x512 `combat.png` is mounted,
no cue playback node exists, and no surviving action frame appears. Its marker is
`combat cue fallback expected=one-missing-disables-all/static-combat512/no-playback observed=all`.
The user performs both headed observations; do not infer motion or fallback from model-only
state. `CharacterAssetProfile.VisualCues` must remain unset so merchant/rest retain their
static textures.

For every generated Character, load the expected identity, HP, Gold, pools, starters,
supporting models, relics, Energy behavior, and selected presentation profiles from the
current `SPEC.md`. Do not embed an example Mod's values or terminal marker in the
generated harness. Emit the Foundation/static marker only after the SPEC-derived automatic
assertions and selected headed observations pass.

## Advanced `CombatPlayer` capabilities

Write these as `plan.Combat` scenarios; in the snippets below `StateProof` is `t.Proof` and
`player` is `t.Player`.

The Character Foundation checks still run for a generated character, but they do not
replace each selected capability's own invariant. Read the capability page and add its
driver after combat reaches `PlayerTurnPhase.Play`.

### Resource/UI

Use `reference/character-resource.md`. Resolve the public RitsuLib attachment, drive the
real gain and spender cards, then enter a second combat. Before the terminal marker assert
all of:

1. `RegisterCombatUi` mounted the control and `SecondaryResourceCmd.Get` starts at zero;
2. the checked icon path/24x24 size or text-only fallback, 220x32 root, 188x32 Label,
   `(160,0)` offset, and non-intersection with native Energy are exact;
3. gain changes state and counter;
4. one affordable and one unaffordable check return the expected values;
5. successful spend changes amount and payoff exactly once;
6. rejected spend changes neither amount nor payoff and never creates debt;
7. combat 2 has a distinct `PlayerCombatState`, amount zero, and reset counter.

Finish with:

```csharp
StateProof(true, "resource UI complete expected=all observed=all");
```

Derive the resource name, amounts, payment, payoff, and reset expectations from the current
`SPEC.md`; the UI dimensions and non-intersection contract remain fixed. Do not reuse an
example Mod's state sequence.

### Ordered semantic buffer/dynamic output

Use `reference/ordered-card-buffer.md`. Drive real source cards through normal visual/result
pile behavior, compile through the generated domain method, play the produced card, and
enter a second combat. Assert all of:

1. the `AttachedState<PlayerCombatState,TState>` buffer and player-visible state start empty;
2. accepted semantic values preserve exact order and every source reaches its normal
   result pile;
3. capacity overflow leaves the buffer/resource unchanged while its source still resolves;
4. the compile card resolves normally, clears state, and refreshes visible text;
5. the output stores the ordered snapshot and exact deterministic `DynamicVars`;
6. exactly one matching `CardGeneratedEntry` exists and the output effect fires;
7. rejected output payment leaves amount and payoff unchanged;
8. combat 2 owns a distinct attached state, empty route, reset resource, and reset UI.

Finish with:

```csharp
StateProof(true, "ordered buffer complete expected=all observed=all");
```

Derive source/output identities, ordered values, capacity, generated-history count, formula,
payment, payoff, reset state, and the composed terminal summary from the current `SPEC.md`.
Retained-card custom piles are not covered by this supported path.

## Other hosts through `plan.Custom`

Events, Ancients, Rest Site options, and Acts have no kit host yet. Write each as
`plan.Custom(name, async t => { ... })` with the host body from the sections below. The dev
console's string commands are not reachable from a Mod (`NDevConsole`'s inner console is
private); call the public commands they wrap instead: `fight` is
`RunManager.Instance.EnterRoomDebug(RoomType.Monster, MapPointType.Unassigned,
encounter.ToMutable())`, `event` is `EnterRoomDebug(RoomType.Event, MapPointType.Unknown,
ModelDb.Event<T>())`, `relic add` is `RelicCmd.Obtain`, `card` is `ICombatState.CreateCard` plus
`CardPileCmd.Add`, and `potion` is `PotionCmd.TryToProcure`. Those bodies predate the kit, so read them with these
substitutions:

- the kit owns the arm gate, budget, navigation, run-UI gate, terminal markers, and failure
  classification: never copy them; a section's "replace the scaffold's room entry / `InCombat`"
  means "put this code in the `Custom` body";
- `StateProof(condition, observation)` is `t.Proof(condition, observation)`, `player` is
  `t.Player`, `ct` is `t.Token`, and a `Task.Delay` after an action is `await t.Settle()`;
- the next `Combat` scenario after a `Custom` one starts a fresh kit combat.

The kit's player combat stays the right host for anything a Card, Relic, Potion, or Power does,
`plan.Encounter` for a Monster, and `plan.RunStart` for a Character's starting state.

## The `MapNode` scenario (event / World Node)

An event is not proven by registration alone. The harness must enter its real `EventRoom`,
wait for the nested event UI, click an actual `NEventOptionButton`, and observe the option's
run-state consequence. Reuse the fixed menu-to-run navigation and `NRun.GlobalUi` timing
gate. Before debug-entering an Event, wait until the normal startup has generated its map
and created its first room; this prevents terminal Event/combat paths from opening a half-
initialized `NMapScreen`:

```csharp
await WaitHelper.Until(
    () => RunManager.Instance.DebugOnlyGetState()?.Map is not NullActMap &&
          (NRun.Instance?.EventRoom?.Layout != null || NRun.Instance?.MapRoom != null),
    ct, TimeSpan.FromSeconds(30), "initial map and room did not finish loading");

var canonical = ModelDb.Event<<Name>>();
await RunManager.Instance.EnterRoomDebug(RoomType.Event, MapPointType.Unknown, canonical);

EventRoom? room = null;
await WaitHelper.Until(() =>
{
    room = RunManager.Instance.DebugOnlyGetState()?.CurrentRoom as EventRoom;
    return room?.LocalMutableEvent is <Name> && NEventRoom.Instance?.Layout != null;
}, ct, TimeSpan.FromSeconds(30), "custom event room not entered");

var mutableEvent = (<Name>)room!.LocalMutableEvent;
NEventOptionButton? choice = null;
await WaitHelper.Until(() =>
{
    var eventRoomNode = NEventRoom.Instance;
    if (eventRoomNode == null) return false;
    choice = UiHelper.FindAll<NEventOptionButton>(eventRoomNode)
        .SingleOrDefault(button =>
            !button.Option.IsLocked
            && button.Option.Title.GetFormattedText() == "<Option title>");
    return choice is { IsEnabled: true, Visible: true };
}, ct, TimeSpan.FromSeconds(30), "event option not available");

// ENTER/LOC: prove title + nested option localization before driving the choice.
var title = mutableEvent.Title.GetFormattedText();
var optionTitle = choice!.Option.Title.GetFormattedText();
var optionDescription = choice.Option.Description.GetFormattedText();
if (title != "<Title>" || optionTitle != "<Option title>" || optionDescription.Length == 0)
    throw new InvalidOperationException(
        $"Nested event localization mismatch: title='{title}', option='{optionTitle}', description='{optionDescription}'");
MainFile.Logger.Info($"[T2MOD-SELFTEST] <ModName> event entered: title='{title}' option='{optionTitle}'");

// DRIVE/OBSERVE: click the game's real option UI and assert the SPEC consequence.
var player = LocalContext.GetMe(RunManager.Instance.DebugOnlyGetState()!)
    ?? throw new InvalidOperationException("local player not found");
var before = player.Gold;
await UiHelper.Click(choice);
await WaitHelper.Until(
    () => player.Gold == before + <amount> && mutableEvent.IsFinished,
    ct, TimeSpan.FromSeconds(30), "event option consequence not observed");

var resultDescription = mutableEvent.Description?.GetFormattedText() ?? string.Empty;
if (resultDescription.Length == 0)
    throw new InvalidOperationException("result page localization missing");
StateProof(player.Gold - before == <amount> && mutableEvent.IsFinished,
    $"event gold expected=<amount> observed={player.Gold - before}; " +
    $"gold {before} -> {player.Gold}; resultLoc={resultDescription.Length > 0}");
```

Required namespaces beyond the fixed scaffold: the event type; `MegaCrit.Sts2.Core.Map`;
`MegaCrit.Sts2.Core.Nodes.Events`; `MegaCrit.Sts2.Core.Nodes.Rooms`; and
`MegaCrit.Sts2.Core.Rooms`. `System.Linq` is already used by the navigation code.

Select the button by the SPEC option's formatted title, not merely "the only unlocked
option". The fast path drives one specified consequence; the extended path below drives
each independent outcome family declared by SPEC.
The event option method logs its own `option chosen:` marker **after** the Cmd changes run
state. The harness independently asserts the same state and emits `state proof:`. Verify
with a pattern such as `"event gold.*observed=25"`; the verifier still requires the exact
load marker and `selftest done`.

### Extended outcomes, special combat, VFX, and rich text

When SPEC uses the full Event vocabulary, read `reference/event-outcomes.md` and drive one
real UI path per independent semantic invariant. Do not create one harness project per
outcome. The supported combined shape is:

1. immediate Cmd and `SetEventState`;
2. a blocking `CardSelectCmd` overlay, then its exact deck mutation;
3. a resumable special combat, then the named `Resume` page;
4. a blocking `RewardsCmd.OfferCustom` overlay, then its exact reward state;
5. click the standard proceed option and confirm the real map opens;
6. enter a fresh mutable Event instance for a terminal special-combat branch;
7. finish combat and confirm the map opens without `Resume`.

Each mutable Event instance starts at most one special combat. This is a runtime boundary,
not just a test simplification.

Wait for the standard Event completion option by semantics, never localized English text:

```csharp
NEventOptionButton? proceed = null;
await WaitHelper.Until(() =>
{
    var eventRoom = NEventRoom.Instance;
    if (eventRoom == null)
        return false;
    proceed = UiHelper.FindAll<NEventOptionButton>(eventRoom)
        .SingleOrDefault(button => button.Option.IsProceed);
    return proceed is { IsEnabled: true, Visible: true };
}, ct, TimeSpan.FromSeconds(30), "event proceed option not available");
await UiHelper.Click(proceed!);
```

For a resumable combat, retain the first mutable Event reference as its concrete custom type
(`mutableEvent`) and require all of the following. `ResumeCount` is the counter its `Resume`
override increments (`reference/event-outcomes.md` § Resume the Event after combat):

```csharp
await WaitHelper.Until(
    () => RunManager.Instance.DebugOnlyGetState()?.CurrentRoom is EventRoom &&
          NEventRoom.Instance?.Layout != null &&
          mutableEvent.ResumeCount == 1,
    ct, TimeSpan.FromSeconds(30), "event did not resume after special combat");
```

For a terminal branch, require an open map, zero resumes on the fresh Event instance, and
no live `NEventRoom`. Identify every combat through its mutable custom encounter type; a
generic `CombatRoom` is not proof of the requested fight.

If SPEC selects `portrait_halo`, follow `reference/event-vfx.md`. Assert the named root is
visible and animating (or intentionally static in Instant mode), then prove it is freed on
page/combat transitions. Delay screenshots until the option UI and room fade are visibly
settled; a node path or near-black transition frame is not visual evidence.

If SPEC selects Event `extra atmosphere`, follow `reference/event-text-effects.md` in this
same `MapNode` run. Resolve `%EventDescription` as a BBCode-enabled `MegaRichTextLabel`,
assert every required allowed host effect type is installed and the exact balanced tags reached its raw text,
then switch to a second authored page and prove the same label contains the new tags but
none of the prior page's tagged span. Capture both settled player-visible states; do not
create a text-only Event project or re-run the other outcome families separately.

If SPEC selects native Card/relic acquisition, `weak_short`, or built-in `trial_noble`,
follow `reference/event-native-presentation.md` in this same `MapNode` run. Wait for the
initial Event description to reach full `VisibleRatio` and opacity, assert the exact
built-in scene parent/position/inherited process mode, then click the real option. Observe
the matching `NCard` in the native preview container and the matching
`NRelicInventoryHolder`; assert exact deck/relic deltas and no duplicates. Sample the
public shake target until it moves and returns when the preference is nonzero, or remains
still at preference index zero. Finish only after the Card preview and owned VFX are gone
and the result page is readable. One marker may cover all selected profiles.

### Bounded forced follow-up Event variant

When SPEC selects `reference/forced-followup-event.md`, replace direct canonical Event
entry with one compact real-map proof. Reuse the same run/map startup gate above, then:

1. call `Hook.ModifyUnknownMapPointRoomTypes` and `Hook.ModifyNextEvent` without the Quest
   token and require unchanged inputs;
2. add one run-created token to `PileType.Deck` with `skipVisuals: true` as proof setup;
3. require unchanged inputs in the wrong act;
4. enter the specified act and require `{ RoomType.Event }` plus the target canonical
   Event from the two hooks;
5. call `EnterMapPointInternal(..., MapPointType.Unknown, ..., saveGame: false)`, wait for
   the target mutable Event and real option button, then capture one settled screenshot;
6. click the completion option, require the token count to become zero, and require both
   hooks to return their ordinary inputs again.

Do not debug-enter the target Event: that skips both invariants this variant exists to
prove. Keep all guards, the real room, UI click, consumption, and restoration in one headed
run and one structured marker. Required additional namespaces are
`MegaCrit.Sts2.Core.Hooks`, `MegaCrit.Sts2.Core.Models.Events`, and the Quest Card/target
Event types.

## The Ancient `MapNode` scenario (new Mod-owned Ancient)

A new `ModAncientEventTemplate` Ancient is not an ordinary Event: its room uses
`NAncientEventLayout`, plays a dialogue, and is recorded as an Ancient map point. Reuse the
fixed menu-to-run navigation, the `NRun.GlobalUi` gate, and the map-ready gate from the
`MapNode` scenario above, then replace the Event driver with this one. It enters the room the
same way the game's own `event <ID>` console command does for an Ancient, and advances
dialogue the way the game's AutoSlay `EventRoomHandler` does.

This driver passed Tier 2 on the pinned host for a Shared Ancient with a Gold option, and a
headed run confirmed its dialogue displays.

```csharp
// REGISTRATION: exactly one identity, in the set SPEC selected (Shared or the Act's set).
var shared = ModelDb.AllSharedAncients.OfType<<Name>>().ToList();
var all = ModelDb.AllAncients.OfType<<Name>>().ToList();
StateProof(shared.Count == 1 && all.Count == 1,
    $"ancient registration expected=shared:1/all:1 observed=shared:{shared.Count}/all:{all.Count}");
var canonical = shared[0];

// DIALOGUE DATA: the real localization consumer parsed every SPEC group.
var dialogues = canonical.DialogueSet;
int firstLines = dialogues.FirstVisitEverDialogue?.Lines.Count ?? 0;
int anyCount = dialogues.AgnosticDialogues.Count;
StateProof(firstLines == <first-visit line count> && anyCount == <ANY dialogue count>,
    $"ancient dialogue expected=firstVisitEver:<n>/ANY:<m> observed=firstVisitEver:{firstLines}/ANY:{anyCount}");

// ENTER as an Ancient map point (not MapPointType.Unknown).
await RunManager.Instance.EnterRoomDebug(RoomType.Event, MapPointType.Ancient, canonical);
EventRoom? room = null;
await WaitHelper.Until(() =>
{
    room = RunManager.Instance.DebugOnlyGetState()?.CurrentRoom as EventRoom;
    return room?.LocalMutableEvent is <Name> && NEventRoom.Instance?.Layout != null;
}, ct, TimeSpan.FromSeconds(30), "custom ancient room not entered");
var mutableEvent = (<Name>)room!.LocalMutableEvent;
var layout = UiHelper.FindFirst<NAncientEventLayout>(NEventRoom.Instance!)
    ?? throw new InvalidOperationException("room did not use NAncientEventLayout");

// DIALOGUE UI: click the real dialogue hitbox until the options are enabled.
int clicks = 0;
while (clicks < 20)
{
    ct.ThrowIfCancellationRequested();
    if (UiHelper.FindAll<NEventOptionButton>(layout).Any(b => b.IsEnabled && !b.Option.IsLocked))
        break;
    var hitbox = layout.GetNodeOrNull<NButton>("%DialogueHitbox");
    if (hitbox == null || !hitbox.Visible || !hitbox.IsEnabled)
    {
        await Task.Delay(100, ct);
        continue;
    }
    hitbox.EmitSignal(NClickableControl.SignalName.Released, hitbox);
    clicks++;
    await Task.Delay(500, ct);
}
await WaitHelper.Until(
    () => UiHelper.FindAll<NEventOptionButton>(layout).Count(b => b.IsEnabled && !b.Option.IsLocked)
          == <initial option count>,
    ct, TimeSpan.FromSeconds(15), "ancient options did not appear after dialogue");
```

The options can be enabled while the dialogue is still on screen, so a passing run may
advance with zero clicks. The click count therefore proves nothing about dialogue display:
the `DialogueSet` assertion proves the data and headed review proves the display.

Then resolve every SPEC string in both languages through the real consumers and restore the
original language (`LocManager.Instance.SetLanguage`, restored in `finally`, as the roll call
does): `mutableEvent.Title`,
`mutableEvent.Epithet`, and each button's `Option.Title`/`Option.Description`. Select a
button by its stable `Option.TextKey` suffix (for example `.EndsWith(".BLESSING")`), not by
English text, click it through `UiHelper.Click`, wait for the SPEC consequence plus
`mutableEvent.IsFinished` (or the next page), and finish with `StateProof`, for example
`ancient blessing gold expected=25 observed={player.Gold - before}; finished={mutableEvent.IsFinished}`.

Required namespaces beyond the fixed scaffold: the Ancient type; `MegaCrit.Sts2.Core.Localization`;
`MegaCrit.Sts2.Core.Map`; `MegaCrit.Sts2.Core.Nodes.Events`;
`MegaCrit.Sts2.Core.Nodes.GodotExtensions`; `MegaCrit.Sts2.Core.Nodes.Rooms`; and
`MegaCrit.Sts2.Core.Rooms`.

Headed review still owns: name/epithet banner, whether the dialogue displays and in which
order, background, speech color, option layout and text colors, map and run-history icons,
mouse/controller progression, and the return to the map. To reach the room by hand, start a
run and enter `event <ENTRY>` in the dev console.

## Relic-owned Rest Site option focused host

Use `reference/rest-site-options.md` for the supported contract. This proof is not a
`CombatPlayer` substitute: it must enter the real Rest Site through
`RunManager.Instance.EnterRoomDebug(RoomType.RestSite, MapPointType.RestSite)` or the
equivalent `room RESTSITE` dev-console command.

The focused proof Mod should expose diagnostic snapshots, but the reviewer drives the
native buttons. Before each selection, record Gold, Current HP, Max HP, the owner's saved
use flag, current option IDs, and current map-history Rest Site choices. After selection,
emit one structured line only when all expected deltas match:

```text
[T2MOD-SELFTEST] <ModName> state proof: framework=RitsuLib frameworkVersion=0.6.7 host=0.107.1 compat=0.107.1 expected=rest-site gold=-30 maxHp=+5 history=1 repeat=hidden observed=rest-site gold=-30 maxHp=+5 history=1 repeat=hidden
```

The required matrix is:

1. no owner produces no custom option;
2. owner plus insufficient Gold produces one disabled option;
3. an enabled button whose Gold becomes insufficient after rendering calls `OnSelect`,
   returns false, and preserves Gold, Max HP, saved use, history, and every option ID;
4. success produces exact fixed-Gold and deterministic-outcome deltas, one history entry,
   and no second custom option in the rebuilt same-visit list;
5. native options either clear normally or remain according to SPEC, with the selected
   custom option removed in both cases;
6. a second visit matches once-per-site or once-per-run semantics;
7. explicit non-singleplayer generation produces no custom option;
8. the custom-icon and missing-icon builds both preload without a fresh error.

Button color, localization, image framing, hover, and controller focus are headed
observations. A model-generated list cannot prove them. When the user reserves this
headed run, do not launch the game automatically; provide the exact console route and keep
an unrun strict `selftest done` as an explicit verification exception.

## Signals for verify and repair

Every kit line starts `[T2MOD-SELFTEST] <ModName>`:

- `selftest budget: <N>s` and `selftest scope: all scenarios=<n>` or
  `selftest scope: only=<names> selected=<k> of <n>`, logged when the kit arms;
- `stage: <name> t=<seconds>s` for the main menu, roll call, run start, and each new combat;
- `roll call: <kind> <Type> id=... ...` per model (`card`, `relic`, `potion`, `power`,
  `character`, `monster`, `encounter`);
- `scenario start: <name>`, then `scenario PASS: <name> (<s>s)` or
  `scenario FAILED: <name>: FAIL|ERROR|TIMEOUT: <detail> (<s>s)` followed by its
  `scenario trail:` lines;
- `state proof: <name>: <observation>` for each assertion that held;
- `selftest coverage:` and `selftest summary:`;
- the terminal line: `state proof: kit summary passed=<n>/<n> scope=all|partial` then
  `selftest done`, or `selftest FAILED: <class>: ...`. The class is `state proof` when any
  scenario failed an assertion or threw (a behavior bug, or a scenario that encoded SPEC
  wrongly), `timeout` when only budgets ran out or a step stayed stuck, and `setup` when the
  kit could not reach its first scenario (navigation, an unknown `--only` name, or a
  definition error).

`verify.md` checks the run with `grep_log.py --tier2-pattern "kit summary passed=.* scope=all"`.
A scenario's own `played/fired/used` diagnostic log is never proof.

## Checklist

- [ ] `SelfTestKit.cs` is the scaffold's copy (Build checks it) and `MainFile.Initialize()`
      arms it after the load marker; no older `SelfTest.cs` is armed beside it.
- [ ] `SelfTestScenarios.cs` is in the `<ModName>` namespace and implements
      `static partial void Define(SelfTestPlan plan)`.
- [ ] Every simple Card from SPEC has a `FaceCheck`; every other behavior SPEC selected has a
      named scenario; no scenario repeats what the roll call or a face check already proves.
- [ ] Each scenario drives the real source, settles, and asserts SPEC's exact post-state with
      expected and observed values; nothing is asserted from a preview, a log, or a model-only
      mutation.
- [ ] A combat-start Relic is obtained in `beforeCombat`; a Card choice runs inside
      `ScriptChoices` with at least two candidates and asserts what was offered.
- [ ] A Character sets `plan.Character<T>()` and asserts its live starting state in a `RunStart`
      scenario; its energy and starter behavior in a `freshCombat` scenario.
- [ ] Every Monster move SPEC selects is driven by `t.EnemyTurn` in a `plan.Encounter` scenario,
      with its intents read first; a multi-hit move asserts `Hits`; every advertised branch is
      reached through its real input, and the cycle is traversed far enough to show its order.
- [ ] A Counter `consumes` edge runs zero/fewer-than-N/at-least-N and asserts no negative
      instance after each.
- [ ] A long scenario raises its own `budgetSeconds`.
- [ ] The final run is unfiltered (`scope=all`); a `selftest FAILED` line is never reported as
      Tier 2.
