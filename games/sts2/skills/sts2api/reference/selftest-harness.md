# Reference: the Tier 2 self-test kit

> Tier 2 runs inside the real game with nobody at the keyboard: the Mod drives itself from
> the main menu into the hosted scenario, fires its own content, and asserts the exact
> post-state. Every API here is public.
>
> **Two files.** `scaffold.py` generates `<ModName>Code/SelfTestKit.cs` and the arming line in
> `MainFile.Initialize()`. The kit is fixed code: Build rejects a hand-edited copy, and
> `scaffold.py --refresh-selftest-kit` rewrites it. You write only
> `<ModName>Code/SelfTestScenarios.cs`, which lists this Mod's checks.
>
> **Ship-safety.** The kit stays dormant unless the game starts with `--t2selftest`; a normal
> player launch never navigates, enters a room, or changes state.
>
> **Both modes.** The same scenarios run in singleplayer (`launch.py --self-test`) and in a
> two-instance multiplayer run (`--self-test --multiplayer`, § Multiplayer Tier 2).

## What the kit does on every run

1. **Roll call**, at the main menu. Every Card, Relic, Potion, Power, Character, Monster,
   Encounter, Event, Ancient, Act, Orb, Enchantment, and Affliction class in the Mod's assembly
   must be registered by its content pack: the game also discovers an unregistered class, but
   gives it a vanilla-style id without the Mod's stem, so its text never resolves. For every
   registered model the player-facing text must exist and resolve in both `eng` and `zhs`
   through the real model consumer (the Compendium's `GetDescriptionForPile(PileType.None)` for
   a Card), with no raw key, empty value, or unresolved `{placeholder}`: titles, descriptions,
   flavor, selection prompts, Power smart descriptions, all fourteen `characters.json` keys,
   Monster names, Encounter titles and loss lines, Event and Ancient titles and initial pages,
   Ancient epithets, and Act titles. Every Mod Ancient must keep a valid dialogue for every
   Character on a first visit and after many visits (the native room throws when none is
   left). It restores the player's language and logs one `roll call:` line per model (a Card's
   id, pool, cost, type, rarity, target, and base numbers; a Character's HP, Gold, Energy,
   pools, starter deck, and Relics; a Monster's HP range; an Encounter's room and roster; an
   Act's index and pool sizes), with both titles. Compare those lines with SPEC.
2. **Navigation** (singleplayer; multiplayer joins a local lobby, § Multiplayer Tier 2): abandons an open run, starts a singleplayer run as the selected Character
   (`plan.Character<T>()`, matched by model type) or the first unlocked one, and waits for the
   run UI, the local Player, and the run's first room (a room entered before that races the
   game's own startup).
3. **Scenarios in order**, except that `RunStart` scenarios run first and `Act` scenarios last. Each has its own budget. A failed assertion, an exception, or a
   timeout ends only that scenario: the kit logs its event trail and runs the next one.
4. **One shared combat.** Combat scenarios share a `CorpseSlugsWeak` fight with 999 Plating on
   the player. Before each one the kit removes the Cards it created from the Hand, returns the
   deck's Hand Cards to the Draw Pile, removes the player's Powers except Plating, clears
   Block, restores HP and Energy, and sets every enemy to 999/999 HP with no Powers or Block.
   When the combat ended, and right after a scenario of another host, the kit starts a new
   combat and applies the same reset, so every scenario starts alike whatever ran before it. A scenario
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
   never owned, Power never seen, Character never played, Monster never met, or Encounter,
   Event, Ancient, or Act never entered; a `selftest summary:` line lists every scenario with its result and seconds. Only when all pass does it log
   `state proof: kit summary passed=N/N skipped=K scope=all` and `selftest done`. A `SKIP`
   scenario did not run in this mode and is never counted as a pass.
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
| Every content model class (registered), its text, and every Ancient's dialogue coverage | roll call, automatic |
| A **simple Card**: its SPEC Implementation cites only its recipe and `reference/effect-primitives.md`, its numbers are fixed (no calculated value, X cost, or condition), and its effects are damage, Block, Energy, Stars, Gold, healing, HP loss, Max HP, draw, or a stack of an existing Power | `plan.FaceCheck<TCard>()`: one line, no assertions to write |
| Everything else: a custom Power, Keyword, Enchantment, or Orb; a raw hook or a `Mod-local:` route; a condition, counter, or state across turns or combats; a Card choice; an interaction between elements; a Relic or Potion trigger | a named `plan.Combat(...)` scenario |
| A Monster and its Encounter | a named `plan.Encounter<TEncounter>(...)` scenario (`recipes/monster.md` § Self-test driver body) |
| A Character's starting state | `plan.Character<T>()` and a named `plan.RunStart(...)` scenario (`recipes/character.md` § Self-test driver body) |
| An Event | a named `plan.Event<TEvent>(...)` scenario (`recipes/event.md` § Self-test driver body) |
| An Ancient | a named `plan.Ancient<TAncient>(...)` scenario (`recipes/ancient.md` § Self-test driver body) |
| A Rest Site option | named `plan.RestSite(...)` scenarios (`recipes/rest-site.md` § Proof matrix) |
| An Act | a named `plan.Act<TAct>(..., slotIndex)` scenario (`recipes/act.md` § Proof matrix) |
| Anything no host covers (a forced follow-up Event through a real Unknown map point) | a named `plan.Custom(...)` scenario (§ Other hosts) |
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
- `Event<TEvent>(name, body, budgetSeconds = 60)`: enters the Event as an Unknown map point and
  waits for its options.
- `Ancient<TAncient>(name, body, budgetSeconds = 60)`: enters the Ancient as an Ancient map point
  and advances its dialogue through the real hitbox until its options are enabled.
- `RestSite(name, body, budgetSeconds = 60, beforeEnter = null)`: enters a Rest Site after
  `beforeEnter` (the host generates the options on entry, so obtain their owner or change Gold
  there).
- `Act<TAct>(name, body, slotIndex, budgetSeconds = 120)`: enters slot `slotIndex` (0-2) through
  `RunManager.EnterAct`, the transition the Mod's entry rule resolves in; runs last.
- `Custom(name, body, budgetSeconds = 60)`: a scenario that enters its own room (§ Other hosts).
  Every host except `Combat` and `RunStart` first finishes any combat in progress.
- `Coop(name, body, budgetSeconds = 45, freshCombat = false)`: a two-player combat scenario that
  runs only in a multiplayer run (singleplayer reports `SKIP`); § Multiplayer Tier 2.
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
  `await t.EnemyTurn(monster, "MOVE_ID")` (`recipes/monster.md` § Self-test driver body).
- Run start: `t.DeckCounts()` (Card class name to count), `t.RelicNames()`, and
  `t.Describe(counts)` (`AxN,BxM` in name order).
- World: `t.Run` (the `RunState`), `t.Act`, `t.MapPointCounts()`, `t.Event` (the room's mutable
  Event), `t.EventOptions()` (shown options, locked included), `await t.ChooseEventOption(key)`
  (a text key or its last segment, `"proceed"` for Proceed; waits until the host took it),
  `t.RestSiteOptions()` (shown options, disabled included), `await t.ChooseRestSiteOption(id)`,
  and the room entries `EnterEvent<T>()`, `EnterAncient<T>()`, `EnterRestSite()`,
  `EnterTreasure()`, `Fight(encounter)`, `WinCombat()`, and `EnterAct(slot)` for use inside a body.
- `await t.WaitUntil(condition, what, seconds = 15)` waits for any host consequence (a page, a
  finished Event, a reward) inside the scenario budget.
- `await t.Do(owner => <command>, "label")` runs a state change (a Cmd, a debug room entry)
  as a step every multiplayer peer executes in order; singleplayer runs it at once.
  `t.Relic<TRelic>()` reads the live Relic. `t.Multiplayer`, `t.Ally`, and `await t.Sync()` serve
  multiplayer scenarios.

Any other public STS2 or RitsuLib API works inside a body: snapshot state, drive the real
source, `await t.Settle()`, then assert. A body that **changes** state does it through the
kit helpers or `t.Do`, never with a direct call (§ Multiplayer Tier 2).

## Multiplayer Tier 2

```bash
python ${GAME_TOOLS_DIR}/launch.py --self-test --multiplayer --mod-name <ModName>
```

The launcher starts two game instances on this machine with the game's own local-multiplayer
flags: the host opens an ENet lobby (`--fastmp=host_standard`), the client joins `127.0.0.1`
(`--fastmp=join --clientId=1001`), each with its own log (`godot-t2-host.log`,
`godot-t2-client.log` beside `godot.log`). Both pick the plan's Character, ready up, and start
one two-player run. No Steam lobby, second machine, or second account is needed.

- **Both peers run every scenario; the host acts.** `t.Player` is the host's player on both
  peers. The host plays the Cards and uses the Potions; the client waits for each interaction
  and checks the same `t.Proof` against its own simulation. So every assertion is checked twice,
  and the host's content is also exercised as a *remote* player's content on the client.
- **Every state change is a step.** The kit helpers (`AddToHand`, `Play`'s Energy top-up,
  `ObtainRelic`, `UsePotion`, `EndTurn`'s stun, combat entry, reset, cleanup) are already steps:
  the host requests each through a RitsuLib managed net action, and every peer runs its own copy
  of that code line in queue order. A direct `await PowerCmd.Apply(...)` in a body would run on
  one peer only and desync the run; wrap it as `await t.Do(owner => PowerCmd.Apply(...))`.
- **References after a room entry.** Entering any room rebuilds the remote players' Relics,
  Potions, and Deck from synchronized state, so a model reference taken before a room entry is
  stale on the client. Read it again after the entry (`t.Relic<TRelic>()`, `t.Player.Deck`).
- **Monsters hit every player.** Vanilla monster attacks target the whole party, so
  `t.EnemyTurn` reports only the HP and hits that reached the acting player: the same numbers as
  singleplayer.
- **`plan.Coop` scenarios** are for behavior that needs two players: ally targeting
  (`TargetType.AnyAlly`/`AllAllies`), a multiplayer-only Card, or a team effect. Both peers run
  the body *for their own player*: `t.Player` is the local player and `t.Ally` the other one.
  Helpers act for the local player, and a `t.Do` body must reach models only through its
  `owner` argument (the other peer runs it for its own player). `await t.Sync()` waits until
  both players' interactions so far have resolved on this peer.

  ```csharp
  plan.Coop("shield_blocks_ally", async t =>
  {
      var card = await t.AddToHand<CoopShield>();
      await t.Play(card, t.Ally.Creature);   // each player shields the other
      t.Proof(t.Me.Block == 7 && t.Ally.Creature.Block == 7,
          $"Block expected=7/7 observed me={t.Me.Block} ally={t.Ally.Creature.Block}");
  });
  ```
- **Hosts without a multiplayer driver yet** (`Event`, `Ancient`, `RestSite`, `Act`, `Custom`)
  report `SKIP` in a multiplayer run, naming the host; their singleplayer run stays the proof.
- **Verdict.** The launcher passes only when both peers log `selftest done`, every scenario's
  `selftest digest:` line (run and combat state at the same queue position) is equal on both
  peers, and neither log contains the game's `State divergence` error. It prints each mismatch.
  Then run `grep_log.py --log-path <each log>` as usual.

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

### Selected capabilities

Each capability page owns its proof section; add a `plan.Combat` scenario from it and derive only
the cases SPEC selected: computed Card values (`card-computed-values.md` § Focused proof
contract; a calculated Card never takes a face check), advanced targeting (`advanced-targeting.md`
§ Verification contract), hand emphasis, corner labels, Custom Card Piles, secondary resources
(`character-resource.md`), and an ordered buffer (`ordered-card-buffer.md`). A generated
Character's Foundation checks do not replace a capability's own invariant.

When the user reserves headed review, build and deploy the focused proof, give them the exact
console setup and observation matrix, and record their reported result separately.

## Other hosts through `plan.Custom`

Use `plan.Custom(name, async t => { ... })` for a room no kit host enters the right way: the
bounded forced follow-up Event, which must arrive through a real Unknown map point
(`forced-followup-event.md` § Verification contract), or a Shop. The dev
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

Every other content kind has its own host: the kit's player combat for anything a Card, Relic,
Potion, or Power does, `plan.Encounter` for a Monster, `plan.RunStart` for a Character's starting
state, `plan.Event`, `plan.Ancient`, `plan.RestSite`, and `plan.Act`.

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
- [ ] A Counter `consumes` edge runs zero/fewer-than-N/at-least-N and asserts no negative
      instance after each.
- [ ] A Monster, Character, Event, Ancient, Rest Site option, or Act follows its recipe's driver
      body: real enemy turns, the live run start, real option clicks, and real room entry.
- [ ] A long scenario raises its own `budgetSeconds`.
- [ ] The final run is unfiltered (`scope=all`); a `selftest FAILED` line is never reported as
      Tier 2.
