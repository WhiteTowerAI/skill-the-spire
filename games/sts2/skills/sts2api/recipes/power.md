# Recipe: Power

Everything one custom Power needs: the SPEC fields, the class, its text, and its proof. A
Power is a persistent buff or debuff on one Creature; prefer a vanilla Power when its semantics
match. Read `reference/mechanics.md` (amount domains in §4) and `reference/vanilla-text-style.md`
first. Also read `reference/extra-corner-labels.md` for a supplemental corner value,
`reference/content-text-effects.md` for extra colored words, and
`reference/model-hook-participation.md` for a raw hook rule.

## SPEC fields

Include one block for every authored custom Power. A Power is usually a dependency of a Card,
Relic, or Potion, so the block sits beside its host's `content:` section; `mod id` and `author`
are declared once by the host.

```markdown
- **content**:
  - name: <shown name>
  - surface: power
  - logical id: <stable local stem>
  - type: Buff | Debuff
  - stack type: Counter | Single
  - amount domain: `[0, unbounded]` (default for Counter) | `[<min>, <max>]`
  - signed amounts: no (default) | yes - <what negative stacks mean>
- **registration**:
  - availability: shared
  - ownership: <the creature that carries it: player | enemy>
  - placement: applied by <the host element that applies it>
- **localization**:
  - languages: [eng, zhs]
  - fields: title=<shown name>; description=<the general rule, without {Amount}: Card and
    Relic tooltips show it before any stack exists>
  - smartDescription: <the live rule with [blue]{Amount}[/blue]; required>
  - formatting: vanilla text style (`reference/vanilla-text-style.md`); dynamic value placeholders
  - extra emphasis: none | <description phrase -> color the default style would not apply>
  - hover tips: none | <each other Power, keyword, or Card the text names>
- **effects**:
  - trigger: <the exact hook or passive boundary the behavior runs on>
  - target: owner | the creature the owner affects
  - sequence: <precise hook/passive behavior with exact numbers>
  - scaling: <named values and bounds, or none>
- **hook participation**: none | one or more; see § Hook participation below
- **state**:
  - lifetime: permanent | decays <amount> at <boundary> | removed when <condition>
  - owner: the creature holding the Power
  - reset: <exact boundary, or none for permanent>
  - visible state: native Amount display
- **presentation**:
  - assets: power icon; placeholder | generate
  - art source: host-tool | backend:<name> | local-image (generate only)
  - native presentation: standard Power icon plus composed title/description Hover Tip
  - extra badges: none | one
    - meaning: <player-facing auxiliary value distinct from Amount>
      value: <state value or bounded display rule>
      corner: top-left
      format: plain | bounded color rich text; at most 6 visible characters
      refresh: <state change that updates it>
      remove: <condition that hides/removes it>
- **fallback**:
  - missing asset: checked template power icon
  - unavailable seam: preserve behavior or stop with an explicit unsupported boundary
- **proof**:
  - scenario: driven through its real host (see § Self-test driver body)
  - driver: <the host interaction that applies it>
  - invariants: <exact expected/observed amount and the dependent effect it causes>
  - lifetime case: <the observation that proves the declared lifetime; required whenever
    lifetime is not "permanent">
- **adapter output** (written to MEMORY after acceptance): resolved content id,
  localization keys (`title`, `description`, `smartDescription`), power icon asset role,
  and framework diagnostic record
```

`amount domain` is mandatory for every custom `Counter`. Keep the nonnegative default unless the
design defines negative stacks; `AllowNegative` is an implementation property, not a substitute
for that decision. Write finite bounds as numbers. `Single` is a flag-like Power with hidden
amount 1 and needs no domain. A signed domain flips the displayed polarity color when the amount
crosses zero; keep the nonnegative default if that is not intended.

`lifetime` is mandatory: a Power that never decays and one that does look identical in a
single-turn proof (§ Proof matrix).

Hand emphasis and extra badges are product semantics. Record why the player needs the signal and
the game-state rule that owns it, never RitsuLib interfaces, predicates, colors, raw markup,
rectangles, or event names. A Power uses at most one top-left label (preset bands overlap in
crowded rows), and every badge supplements the native Amount. Intent badges have no authoring
recipe; an accepted one is a Mod-local route.

## Registration

Register once in `MainFile.Content.cs`; never add `[Pool]` or rely on reflection discovery:

```csharp
RitsuLibFramework.CreateContentPack(ModId)
    .Power<<PowerName>>()
    .Apply();
```

RitsuLib derives `MOD_POWER_TYPENAME`, keeping the CLR suffix: `ChargePower` in `ExampleMod`
becomes `EXAMPLE_MOD_POWER_CHARGE_POWER`.

## Skeleton

Add `<ModName>Code/Powers/<PowerName>.cs`:

```csharp
using MegaCrit.Sts2.Core.Entities.Powers;
using STS2RitsuLib.Scaffolding.Content;

namespace <ModName>.Powers;

public sealed class <PowerName> : ModPowerTemplate
{
    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    public override PowerAssetProfile AssetProfile => new(
        IconPath: "res://<ModName>/images/powers/<slug>.png",
        BigIconPath: "res://<ModName>/images/powers/big/<slug>.png");
}
```

Omit `AssetProfile` in placeholder mode. Generated Power art is two checked 256x256 PNGs: the
status icon and the `big/` apply/expire icon.

## Hooks and the effect sequence

Override only the hook SPEC selects. `Owner` is the attached mutable Creature; derive its Player
only when `Owner.Player` is non-null. The Power is the source identity but not a Card source, and
many hooks supply no `PlayerChoiceContext` or target. Lower `effects.sequence` through
`reference/effect-primitives.md`, authoring only commands whose required inputs the hook has: a
guarded turn hook can affect `Owner`, while draw, targeted Power application, Orb queue actions,
or Max HP loss need the exact Player/context/target callback. A synchronous value hook modifies
its return value and cannot run an awaited sequence.

- turn start: `AfterSideTurnStart(...)` guarded by `participants.Contains(Owner)`; when the
  effect draws, selects, or needs a `PlayerChoiceContext`, `AfterPlayerTurnStart(choiceContext,
  player)` guarded by `player == Owner.Player`;
- turn end and duration: `AfterSideTurnEnd(...)` plus `PowerCmd.TickDownDuration(this)`;
- flat outgoing damage: `ModifyDamageAdditive(...)`, guarded by owner/props;
- application and removal: `AfterApplied(...)` / `AfterRemoved(...)`.

Use `Amount` for current stacks, `Flash()` for a real trigger, and await every command.
Implement a non-permanent SPEC `lifetime` explicitly by ticking it from the declared boundary
hook with `PowerCmd.TickDownDuration(this)`; a Power that only ever gains amount is permanent
regardless of intent.

## Amount domain

Every `Counter` has an explicit SPEC domain, nonnegative by default. Use
`AllowNegative => true` only when SPEC defines signed behavior. Clamp every caller-owned gain or
spend before invoking a Cmd, then re-read the retained live instance, because hooks may rewrite
the requested offset.

Apply or gain:

```csharp
await PowerCmd.Apply<<PowerName>>(
    choiceContext, target, amount, applier, cardSource);
```

Consume an existing nonnegative Counter:

```csharp
var power = target.GetPower<<PowerName>>();
if (power is { Amount: > 0 })
{
    var spend = Math.Min(power.Amount, Math.Max(0, requested));
    await PowerCmd.ModifyAmount(choiceContext, power, -spend, null, null);
}
```

Never consume with a negative `PowerCmd.Apply<T>`: with no existing instance it can create
invalid negative state.

## Hook participation: modify a value the host is computing

A SPEC `hook participation` block has the engine ask the Power for a number or decision while
resolving someone else's event. Follow `reference/model-hook-participation.md`. A Power receives
**combat-scope hooks only** (45 of 68); a run-scope hook overridden on a Power compiles and never
fires, and Build rejects it. `Owner` is the attached `Creature` directly.

The shape is a guard, then the value, with the hook's neutral default on every other path:

```csharp
public override decimal ModifyDamageMultiplicative(
    Creature? target, decimal amount, ValueProp props, Creature? dealer, CardModel? cardSource)
{
    if (target != Owner) return 1m;               // SPEC `subject`: incoming, not outgoing
    if (!props.IsPoweredAttack()) return 1m;      // SPEC `condition`: attack damage only
    return DynamicVars["DamageIncrease"].BaseValue;
}
```

That is vanilla `VulnerablePower`. Keep three things straight:

- **`target` versus `dealer`** is the difference between "damage I take" and "damage I deal":
  `VulnerablePower` guards `target`, `WeakPower` guards `dealer`. SPEC's `subject` says which.
- **Return the neutral default outside the guard**, never a stored modifier; the engine also uses
  it to decide whether to list this Power as a modifier of that number in the UI.
- **Read the number from `DynamicVars`** and declare it in `CanonicalVars`, so the rules text and
  the body use one value.

An **Enchantment** never uses `ModifyDamageMultiplicative` or the other four redirected hooks;
see `recipes/enchantment.md`.

## Optional routes

Read a route only when SPEC selects it, append only its SPEC block, and preserve amount/duration
semantics, phase/order, owner/subject guard, neutral behavior, display refresh, and cleanup when
the Power or capability is removed. The capability inherits the Power's combat-scope lifetime.
SelfTest asserts both the dependent effect and no second firing after removal. A process-wide
listener is never a Power route.

- a separable Power-owned behavior/state bundle: `reference/model-capabilities.md`;
- lifecycle/persistence/RNG: `reference/lifecycle-state-rng.md`;
- reachable per-hit attack, healing, Energy/Stars-gain response, or maximum hand size:
  `reference/shared-effect-hooks.md`;
- a right-click on the Power icon: `reference/model-right-click.md`.

### Optional extra badges

Implement `IPowerExtraIconAmountLabelSpecsProvider` on the Power. Return zero or one
`ExtraIconAmountLabelSpec.Plain(...)` or bounded `RichText(...)` entry at `TopLeft`, preserving
the native bottom-right `Amount` and the six-visible-character limit. Never combine Power
presets: their bands are not clipped and intrude into adjacent Powers. When badge text follows
`Amount`, use the normal amount mutation and `InvokeDisplayAmountChanged()`. For a separate field
with no host refresh, implement `IPowerExtraIconAmountLabelsChangeSource`, declare
`event Action? PowerExtraIconAmountLabelsInvalidated`, and invoke it once after the mutation.
Returning no spec after the removal condition removes the label. Never poll or draw rectangles.

## Localization

Ship matching `localization/eng/powers.json` and `localization/zhs/powers.json` with the exact
public entry, always all three keys:

```json
{
  "<MOD>_POWER_<TYPE>.title": "Display Name",
  "<MOD>_POWER_<TYPE>.description": "At the start of your turn, gain [gold]Block[/gold].",
  "<MOD>_POWER_<TYPE>.smartDescription": "At the start of your turn, gain [blue]{Amount}[/blue] [gold]Block[/gold]."
}
```

```json
{
  "<MOD>_POWER_<TYPE>.title": "显示名称",
  "<MOD>_POWER_<TYPE>.description": "在你的回合开始时，获得[gold]格挡[/gold]。",
  "<MOD>_POWER_<TYPE>.smartDescription": "在你的回合开始时，获得[blue]{Amount}[/blue]点[gold]格挡[/gold]。"
}
```

The two descriptions have different jobs. `PowerModel.HoverTips` uses `.smartDescription` for a
live Power, with `{Amount}` bound to its stacks. A Card, Relic, or Potion tooltip built from
`HoverTipFactory.FromPower<T>()` shows the canonical model's `.description`, whose `{Amount}` is
usually 0. So `.description` states the general rule without `{Amount}` (a fixed number may
appear as `[blue]2[/blue]`), and `.smartDescription` states the live rule with
`[blue]{Amount}[/blue]`, as vanilla `DEMON_FORM_POWER` does. Never write a literal stack count or
a second copy of the tip text; the engine composes the Hover Tip from `title` plus the
description. Both follow the Power row of `reference/vanilla-text-style.md`.

## Self-test driver body

A custom Power has no scenario of its own: drive it through its real host and add the Power
assertions below to that scenario. A Card host plays it with `t.Play` (`recipes/card.md`), and a
Card that applies a custom Power never takes a face check alone.

## Proof matrix

- Assert the applied amount with exact expected/observed values, and the dependent effect the
  amount causes, so the Power is proved to *do* something.
- **Assert the declared lifetime.** Applied amount plus one effect delta observe the same turn,
  so a decaying Power passes them even when it never ticks. Whenever `lifetime` is not
  `permanent`, advance past the boundary, assert the reduced amount, then assert removal at zero.
- Assert `Type` when the design depends on Buff versus Debuff; it drives visible polarity.
- **Assert the amount domain at its bounds.** For every finite bound, drive past it and assert
  the amount stopped there; for the nonnegative default, consume more than the current amount and
  assert no negative instance appears. For a signed domain, assert the declared negative meaning.
- **Hook participation: assert the neutral case outside the guard.** Drive one event the guard
  ignores and assert the host's value is unchanged; for a collection edit, assert that an entry
  placed beforehand survives.
- Extra badges: assert zero/one provider output, the exact `TopLeft` corner and text, the
  selected invalidation path, removal, and unchanged native `Amount`. The real `NPower` label
  layout is a headed observation.
