# Recipe: Relic

Everything one new Relic needs: the SPEC fields, the class, its text, and its proof. The skill
fills only the effect logic; `ModRelicTemplate`, content-pack registration, localization keys,
and `RelicAssetProfile` follow the fixed shapes below. Read `reference/vanilla-text-style.md`
for every string. Vanilla Relics to imitate: `Lantern` (combat-start Energy), `FurCoat` (seeded
RNG).

Also read, only when SPEC selects it:

- progress it remembers ("every N", "once per combat", "last turn", limited uses):
  `reference/stateful-mechanics.md` before choosing a field or hook; the state lifetime is part
  of the SPEC;
- a Rest Site action: `reference/rest-site-options.md` (never adapt the combat skeleton into an
  option by guessing UI methods);
- supplemental corner values: `reference/extra-corner-labels.md`;
- extra colored words beyond the default style: `reference/content-text-effects.md`;
- a raw hook rule: `reference/model-hook-participation.md`.

Changing an existing vanilla Relic's availability or pool membership resolves the target
through `reference/vanilla-overrides.md`, then `reference/vanilla-availability-overrides.md`;
never replace the vanilla model or register it again.

## When to use

The request is a **Relic** when it is a passive or triggered item the player owns, not a Card
they play or a one-shot Potion. Triggers are combat or run lifecycle events: "at the start of
combat…", "whenever you play a card…", "the first time each turn…", "at the start of each
floor…".

## SPEC fields

```markdown
# SPEC — <Mod Name>

- **mod id**: <stable mod identity>
- **author**: <author>
- **content**:
  - name: <shown name>
  - surface: relic
  - logical id: <stable local stem, e.g. gamblers_coin>
  - rarity: Common | Uncommon | Rare | Shop | Event | Ancient | Starter
- **registration**:
  - availability: shared | character:<name>
  - ownership: player
  - placement: <plain-language drop/pool rule>
- **localization**:
  - languages: [eng, zhs]
  - fields: title=<shown name>; description=<hover text>; flavor=<flavor line>
  - formatting: vanilla text style (`reference/vanilla-text-style.md`); dynamic value placeholders
  - extra emphasis: none | <description phrase -> color the default style would not apply>
  - displayed values: none | <value name -> declared scaling name; literal or placeholder>
- **effects**:
  - trigger: <plain-language event and boundary, e.g. start of combat>
  - cadence: once per combat | once per turn | every trigger | once per run
  - target: owner
  - sequence: <ordered game-term effect with exact values>
  - scaling: <named values and bounds, or none>
- **hook participation**: none | one or more; see § Hook participation below
- **state**: none | see `reference/stateful-mechanics.md`
- **presentation**:
  - assets: relic icon; placeholder | generate
  - art source: host-tool | backend:<name> | local-image (generate only)
  - native presentation: standard relic display
  - hover tips: none | <each keyword, Power, Card, or Orb named in the description>
  - extra badges: none | one to three
    - meaning: <player-facing auxiliary value, e.g. charges remaining>
      value: <state value or bounded display rule>
      corner: top-left | top-right | bottom-left (one label per corner)
      format: plain | bounded color rich text; at most 4 visible characters
      refresh: <state change that updates it>
      remove: <condition that hides/removes it>
- **fallback**:
  - missing asset: checked template relic icon
  - unavailable seam: preserve behavior or stop with an explicit unsupported boundary
- **proof**:
  - scenario: CombatPlayer
  - driver: <real trigger, e.g. enter combat>
  - invariants: <exact expected/observed state plus visible trigger>
  - cadence case: <the observation that separates the declared cadence from every-trigger;
    required whenever cadence is not "every trigger">
  - boundary cases: <owner guard/reset/save cases, or none>
- **adapter output** (written to MEMORY after acceptance): resolved content id,
  localization keys, asset profile, and framework diagnostic record
```

`cadence` and its cadence case are mandatory: the trigger hook a Relic overrides usually fires
more often than the design wants, so the guard is the Relic's identity (§ Proof matrix).

A Relic that contributes a Rest Site action adds this block (the shared route also serves
standalone, exactly-one Card, and selected Modifier owners through their own recipes):

```markdown
- **owned Rest Site option**:
  - owner: relic
  - owner multiplicity: exactly one
  - state handle: host visit removal | saved owner bool
  - title: <localized button title>
  - description: <localized hover description>
  - eligibility: <when the owned relic contributes the option>
  - repeatability: once per Rest Site | once per run
  - enabled rule: always | can pay fixed Gold cost
  - cost: free | <nonnegative integer> Gold
  - outcome: <ordered deterministic game-term operations and exact values>
  - after success: leave | keep remaining options available
  - icon: checked native fallback | generate
  - multiplayer: both
  - proof: absent owner; present disabled/enabled; stale-render failed payment with no
    mutation; exact successful cost/outcome/history; no duplicate; stay/leave; second visit;
    custom icon and missing-icon fallback
```

Absence and disabled are separate: `eligibility` controls contribution, `enabled rule` the
native gray/clickable state. A fixed-Gold outcome must be completely preflightable before its
first mutation; stop for a post-payment selection, random branch, or anything that would need
rollback.

## Registration and asset profile

Register exactly once in `MainFile.Content.cs`; the pool generic is the availability contract:

```csharp
RitsuLibFramework.CreateContentPack(ModId)
    .Relic<SharedRelicPool, Relics.<RelicName>>()
    .Apply();
```

Custom icons set the three exact paths in the skeleton's `RelicAssetProfile`. `gen_sprite.py`
derives the 256x256 filled-white outline from the final main alpha (shared 3% rule, 8 pixels)
without another acquisition call. RitsuLib checks each path and keeps its fallback when a file
is absent; leave the whole profile out in placeholder mode.

## The skeleton (fill only the marked spot)

Add one file `<ModName>Code/Relics/<RelicName>.cs`:

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

    // Pick the hook that matches the trigger (§ Trigger hooks).
    public override async Task AfterSideTurnStart(CombatSide side,
        IReadOnlyList<Creature> participants, ICombatState combatState)
    {
        // Standard combat-start guard: my owner is in this turn, and it's turn 1.
        var combat = Owner.PlayerCombatState!;     // non-null inside a combat hook
        if (!participants.Contains(Owner.Creature) || combat.TurnNumber > 1)
            return;

        Flash();                                   // visual: relic pulses on trigger

        // ─────────── EFFECT LOGIC — the ONLY part the skill writes ───────────
        // (Lower SPEC's effects.sequence through reference/effect-primitives.md.)
        // ─────────────────────────────────────────────────────────────────────
    }
}
```

## Trigger hooks (override the one matching the request)

All are `public virtual async Task` on `AbstractModel`. Relics receive combat hooks because
`RelicModel.ShouldReceiveCombatHooks => true`; there is no `ICombatHook` interface and no manual
subscription, just the override.

| Request phrasing | Hook to override | Notes |
|---|---|---|
| "at the start of combat": Block, damage, Energy | `AfterSideTurnStart(CombatSide, IReadOnlyList<Creature>, ICombatState)` | Guard `participants.Contains(Owner.Creature)` and `TurnNumber <= 1`, as Lantern does. It has **no `PlayerChoiceContext`**, so nothing that draws, selects, or asks the player belongs here. |
| "at the start of combat": apply a Power | `AfterRoomEntered(AbstractRoom room)` | Guard `room is CombatRoom`; the Power is on before turn 1, as Bronze Scales does. Pass `new ThrowingPlayerChoiceContext()` to `PowerCmd.Apply`. |
| "at the start of combat": more cards in the opening hand | `ModifyHandDraw(Player, decimal)` | Hook participation, guard `player == Owner` and `TurnNumber <= 1`, as Bag of Preparation does. |
| "at the start of combat/turn": draw after the opening hand, choose/discard/exhaust a Card, or anything else that needs a `PlayerChoiceContext` | `AfterPlayerTurnStart(PlayerChoiceContext choiceContext, Player player)` | Guard `player == Owner` and, for combat start, `Owner.PlayerCombatState!.TurnNumber <= 1`, as Gambling Chip does. Runs after the Energy reset and the hand draw, before `AfterSideTurnStart`. |
| "at the start of each turn" | `AfterSideTurnStart(...)`, or `AfterPlayerTurnStart(...)` when it needs a `PlayerChoiceContext` | Same hooks, no TurnNumber guard (still guard the owner). |
| "every N turns" across combats | `AfterSideTurnStart(...)` | `SavedAttachedState<SpecificRelic, int>` modulo progress; never clear it at combat end (`stateful-mechanics.md`). |
| "on turn N" / "every N turns this combat" | start: `AfterSideTurnStart(...)`; end: `BeforeSideTurnEnd(...)` | Read `Owner.PlayerCombatState.TurnNumber` (`== N` or `% N == 0`); no saved counter. |
| "every N cards this turn" | `AfterCardPlayed(...)` + `BeforeSideTurnStart(...)` reset | Owner-card guard; ordinary turn-local field. |
| "once per combat" | the real trigger + `AfterRoomEntered(CombatRoom)` reset | Ordinary bool; reset only on combat entry. |
| pre-combat setup (no Energy) | `BeforeCombatStart()` | Fires once before turn 1. **Never grant Energy here**: the turn-1 Energy reset wipes it. |

The `TurnNumber <= 1` guard **is** the declared once-per-combat cadence; without it the hook
fires every turn. The `participants.Contains(Owner.Creature)` check is mandatory in
multiplayer because the hook fires for every side.

## The effect sequence

The hook parameters provide the live combat state, participant/subject, Card, or other trigger
context; the mutable Relic supplies `Owner` (a `Player`) and `Owner.Creature`, but no Card
source and no general `PlayerChoiceContext`. Lower `effects.sequence` through
`reference/effect-primitives.md`, using only primitives whose inputs the chosen hook truly has.
Resource gain, self Block/heal, and known combat-Card creation can bind to `Owner` in a live
combat hook; a target-dependent Power, draw/discard, Orb action, or Max HP loss needs a hook
that supplies its context and target. Never manufacture a `PlayerChoiceContext` because the
Relic is in combat, and never use an absolute setter for a normal effect. `await` every Cmd.

**Seeded RNG** (never `System.Random`, which breaks determinism and seed sharing):

```csharp
Rng rng = new(Owner, base.Id);      // deterministic per (run seed, relic id)
bool heads = rng.NextBool();        // 50/50
int roll   = rng.NextInt(3);        // 0,1,2
// add a mixin if the relic may roll repeatedly and you want distinct results:
Rng perTurn = new(Owner, base.Id, (uint)Owner.PlayerCombatState!.TurnNumber);
```

**Reaching the player and creature** inside a Relic hook:

```csharp
Player me       = Owner;                       // RelicModel.Owner (non-null in combat)
Creature myBody = Owner.Creature;
var combatState = Owner.PlayerCombatState!;     // Energy, MaxEnergy, TurnNumber
```

**Always** call `Flash()` when the Relic visibly triggers, and log a diagnostic marker; the
harness uses it to localize the trigger, but only asserted state is Tier 2 proof:

```csharp
MainFile.Logger.Info($"[T2MOD-SELFTEST] <RelicName> fired: {outcome} energy {before} -> {after}");
```

For selected bounded state, follow `reference/stateful-mechanics.md`: a run-save profile may use
`SavedAttachedState<SpecificRelic, bool/int/string>` with a Mod-qualified name; combat-local
turn timing reads `PlayerCombatState.TurnNumber`. Emit only declared transitions and consumers,
and route every visible mutation through one refresh path. For an effect family outside the
shared reference, query the rest of the pack; if no route exists, follow `grounding.md`
§ Mod-local Routes.

## Displayed values the engine keeps current

`RelicModel` runs SmartFormat/DynamicVar substitution over the description and its Hover Tip,
so a value declared in `CanonicalVars` renders live in native `[blue]`. Vanilla `WingedBoots`
declares `new DynamicVar("Rooms", 3m)` and its description reads `… [blue]{Rooms}[/blue] times.`

A literal number in the text is acceptable **only** when the value can never change and
appears in exactly one place. Declare a scaling name and use a `{Placeholder}` whenever:

- the value changes at runtime, by upgrade, save state, or another element;
- the same number also appears in the effect code, where the two can silently diverge; or
- the design intends vanilla's native colored presentation.

Record the choice in `localization.displayed values`.

## Keyword tips are not automatic here

Unlike a Card, a Relic gets no keyword tooltip from naming a keyword. `ModRelicTemplate` shows
tips only through its declared `RegisteredKeywordIds` and `AdditionalHoverTips`. Declare every
keyword the description names in `presentation.hover tips` and register it, and add an
`AdditionalHoverTips` entry for every Power, Card, or Orb it names.

## Localization (ships in the .pck)

Add the same entries to `<ModName>/localization/<lang>/relics.json` for `eng` and `zhs`. Keys
are flat and use the exact RitsuLib public entry:

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
in `[blue]`, heals in `[green]`, glossary terms in `[gold]`, Curses in `[red]`, Enchantment
names in `[purple]`; title and flavor stay plain. Only when SPEC selects `extra emphasis`, read
`reference/content-text-effects.md`: Relic descriptions may add balanced `blue`, `gold`,
`green`, `purple`, and `red` spans, and the Hover Tip renders the same description.

RitsuLib derives `Id.Entry` as `MOD_CATEGORY_TYPENAME` in uppercase snake case: Mod id
`GamblersCoin` with Relic class `GamblersCoin` becomes `GAMBLERS_COIN_RELIC_GAMBLERS_COIN`. To keep
a published entry across a type rename, pass `ModelPublicEntryOptions.FromStem(...)` to the
registration; never add another id mechanism.

## Hook participation: modify a value rather than act on a trigger

The hooks above are the Relic *doing* something. A SPEC `hook participation` block has the
engine ask the Relic for a number or decision while resolving someone else's event; nothing
fires. Follow `reference/model-hook-participation.md`. A Relic reaches both the run-scope and
combat-scope sets (66 of 68 hooks), the widest of any surface.

**`Owner` is a `Player`, not a `Creature`**, so a subject guard goes through `Owner.Creature`
and through `Owner.Osty` wherever the Osty can be the subject. Vanilla `PenNib` checks both:

```csharp
public override decimal ModifyDamageMultiplicative(
    Creature? target, decimal amount, ValueProp props, Creature? dealer, CardModel? cardSource)
{
    if (!props.IsPoweredAttack()) return 1m;                        // SPEC `condition`
    if (dealer != Owner.Creature && dealer != Owner.Osty) return 1m; // SPEC `subject`
    return 2m;
}
```

A guard that checks only `Owner.Creature` silently stops applying when the Osty acts.

For a **collection** participation (`try_modify_rewards` and relatives), the bool reports only
that you touched the list: add or remove entries and return `true`, or return `false`
untouched. Preserve every entry you did not come for; vanilla `Midas` doubles gold rewards by
rebuilding the list with `Clear()` plus `AddRange()` of everything. Never contribute a Rest Site
option through the raw hook; use § Optional owned Rest Site action.

## Optional routes

Keep native trigger effects in their override. Read a route only when SPEC selects it, append
only its independent SPEC block, and preserve cadence, phase/order, subject guard, neutral case,
persistence/reset, display refresh, removal cleanup, and exact real-host assertions. Never
register a Relic-owned rule process-wide.

- a separable Relic-owned behavior/state bundle: `reference/model-capabilities.md`;
- lifecycle/persistence/RNG across callbacks, run/save/profile boundaries:
  `reference/lifecycle-state-rng.md`;
- reachable per-hit attack, healing, Energy/Stars-gain response, or maximum hand size:
  `reference/shared-effect-hooks.md`;
- a right-click action: `reference/model-right-click.md`.

### Optional extra badges

Implement `IRelicExtraIconAmountLabelSpecsProvider` on the Relic. Return zero to three
`ExtraIconAmountLabelSpec.Plain(...)` or bounded `RichText(...)` entries in SPEC order, using
each of `TopLeft`, `TopRight`, and `BottomLeft` at most once. Preserve the native bottom-right
counter and the four-visible-character limit. When badge text follows the Relic's displayed
state, mutate it and call `InvokeDisplayAmountChanged()`. For a separate field with no host
refresh, implement `IRelicExtraIconAmountLabelsChangeSource`, declare
`event Action? RelicExtraIconAmountLabelsInvalidated`, and invoke it once after the mutation.
Returning no spec after the removal condition removes the label. Never poll or draw custom
rectangles.

### Optional hidden inventory presence

For an owned Relic that keeps working while absent from the player's view (a dormant form, a
hidden curse), implement `STS2RitsuLib.Relics.Visibility.IModRelicVisibility` on the Relic.
Hiding removes only the UI presence: the inventory holder, its flash, its hover tips, and the
basic holder that reward, choose-a-relic, run-history, and unlock screens build. Hooks, state,
and saves keep running. Because the same check runs on offered and history copies, derive
`IsRelicVisible` only from Mod-owned state the owned Relic sets, `true` by default:

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
active inventory and returns whether a holder was removed, added, or moved (`false` when
nothing changed or no run inventory exists). Never read `Owner` in the getter: a canonical Relic
has none. Hiding another Mod's or a vanilla Relic through the global
`RegisterRelicVisibilityRule` is not part of this route.

### Optional owned Rest Site action

Keep the Relic registered once. Add one separate `ModRestSiteOptionTemplate` class (not
content-pack registered) and contribute it from the Relic's `TryModifyRestSiteOptions`. Use the
reference's `ShouldOffer`/`CanPay` split: `TryModifyRestSiteOptions` owns absence and rejects a
duplicate `OptionId`; `IsEnabled` owns the native gray state; `OnSelect` repeats the final
eligibility/payment check before any command. A false result mutates nothing and leaves the
list intact. A true result awaits fixed Gold payment and the deterministic outcome, marks
once-per-run state only after success, and lets the native host remove the option.

Put the option title/description beside the Relic's keys in `relics.json`. A generated icon is
one verified `rest_site_option` 256x169 image at `images/rest_site_options/<slug>.png`; resolve
absence to the native Heal icon before building `RestSiteOptionAssetProfile`, never a missing
custom path.

## Multiplayer

A Relic belongs to one player and every peer simulates it. Combat and run hooks fire for every
player's models, so the owner guard in § Trigger hooks is what keeps a Relic from also firing for
a teammate. Team effects are explicit:

- **every player** iterates `combatState.GetTeammatesOf(Owner.Creature).Where(c => c.IsAlive &&
  c.IsPlayer)` in combat, or `Owner.RunState.Players` outside it;
- **when a teammate does something**, the hook's subject is another player
  (`cardPlay.Card.Owner != Owner`, `player != Owner`); the effect still acts for the stated
  receiver;
- **multiplayer only** overrides `public override bool IsAllowed(IRunState runState) =>
  runState.Players.Count > 1` (vanilla `MassiveScroll`; `== 1` for singleplayer only), which
  keeps it out of the other mode's rewards, shops, and Neow; text names the receiver ("all
  players", `所有玩家`).

```csharp
public override async Task AfterSideTurnStart(CombatSide side,
    IReadOnlyList<Creature> participants, ICombatState combatState)
{
    if (!participants.Contains(Owner.Creature) || Owner.PlayerCombatState!.TurnNumber > 1)
        return;
    Flash();
    foreach (var ally in combatState.GetTeammatesOf(Owner.Creature).Where(c => c.IsAlive && c.IsPlayer).ToList())
        await CreatureCmd.GainBlock(ally, DynamicVars.Block.BaseValue, ValueProp.Unpowered, null);
}
```

Its scenario asserts the value on every player (`t.State.Players`), so the same scenario passes
with one player and with two.

## Rarity and pool

`RelicRarity` (`MegaCrit.Sts2.Core.Entities.Relics`): `None, Starter, Common, Uncommon, Rare,
Shop, Event, Ancient`. Use **`Common`** for a normal droppable Relic unless the request implies
otherwise. The pool is the first generic argument of `.Relic<TPool,TRelic>()`
(`MegaCrit.Sts2.Core.Models.RelicPools`): `SharedRelicPool` (any Character, the default), or
`IroncladRelicPool`, `SilentRelicPool`, `DefectRelicPool`, `RegentRelicPool`,
`NecrobinderRelicPool`.

## Pre-flight checklist

- [ ] `public sealed` class extending `ModRelicTemplate`, `Rarity` overridden, registered
      exactly once with `.Relic<TPool,TRelic>()`.
- [ ] The hook matches the trigger; combat start uses `AfterSideTurnStart` with the
      `participants.Contains(Owner.Creature)` and `TurnNumber <= 1` guards.
- [ ] Stateful: event/threshold/phase/lifetime/reset/persistence match SPEC; run state uses a
      Mod-qualified `SavedAttachedState<SpecificRelic, int/bool>`; combat turns use
      `PlayerCombatState.TurnNumber`.
- [ ] A Rest Site action has the owner guard, stable namespaced id, duplicate check,
      shared offer/payment predicate, click-time recheck, success-only repeatability,
      declared stay/leave, and native Heal icon fallback (`reference/rest-site-options.md`).
- [ ] Every `Cmd`/RNG call is awaited; `Flash()` and the diagnostic marker fire on trigger.
- [ ] `relics.json` has flat `<MOD>_RELIC_<TYPE>.{title,description,flavor}` keys.
- [ ] Main/outline/big files exist at their exact paths with the three-field
      `RelicAssetProfile`, or the placeholder profile is left out.
- [ ] Extra badges: at most three unique safe corners, bounded text, one refresh path per
      mutation, removal, native main counter preserved.

## Self-test driver body

A Relic gets a named `plan.Combat` scenario (`reference/selftest-harness.md` § relic). A
combat-start trigger obtains the Relic in `beforeCombat` so its hook fires as combat starts,
and the body asserts SPEC state; a trigger during combat obtains it in the body and drives the
real source. A Relic whose cadence crosses combats uses that reference's stateful-cadence
recipe; other bounded-state profiles derive only their selected transition/reset/persistence
checks.

## Proof matrix

- Assert the declared effect's exact expected/observed state plus its visible trigger.
- **Assert the cadence.** A combat-start assertion runs inside turn 1, so it cannot tell
  "once per combat" from "every turn": deleting the `TurnNumber <= 1` guard still passes it.
  Whenever `cadence` is not `every trigger`, advance past the boundary and assert the value did
  **not** change again: one more turn (`t.EndTurn()`) for a per-combat Relic, a second combat
  (`t.StartNewCombat()`) for a per-run Relic.
- **Assert each declared keyword tip resolves**: the registered id is present and its
  title/description resolve to shipped localization, not a raw key.
- **Assert each declared displayed value renders live**: the rendered description contains
  the current value, not the placeholder token or a stale literal.
- **Hook participation: assert the neutral case outside the guard.** Drive one event the guard
  should ignore and assert the host's value is unchanged; add the Osty case when the design
  counts it. For a collection edit, assert that an entry placed beforehand survives.
- Bounded state owes only its selected transition/reset/persistence boundary; a run-save
  profile also owes its real save/fill round trip (`N-1`, threshold, reset/carry-over, and a
  `SavedProperties.From`/`Fill` round trip).
- Hidden inventory presence: assert `RitsuLibFramework.IsRelicVisible(relic)` before and after
  each change, that `RefreshRelicVisibility()` reports a changed inventory, and that the effect
  still resolves while hidden. Headed review confirms the holder leaves and returns with no
  empty slot, stale tooltip, or flash.
- A Rest Site option follows `reference/rest-site-options.md` in the real native room:
  absent/disabled/enabled states, click-time payment rejection with no deltas, exact
  Gold/outcome/history deltas, no duplicate after rebuild, declared stay/leave and second-visit
  repeatability, custom icon, and missing-icon fallback, in both modes.
  Model-generated option lists are diagnostics, not hosted proof.

## Manual fallback (only when the harness cannot reach its scenario)

Grant it: `relic add <PREFIX>-<SLUG>` (matching is substring `Contains`, uppercased, so a
unique substring works). Trigger it: enter a combat. For a cadence other than `every trigger`,
end the turn and confirm the effect did not fire again.

## Full golden example (Gambler's Coin)

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
            await PlayerCmd.LoseEnergy(before, Owner);    // bust

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
