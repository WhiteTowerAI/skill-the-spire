# Character resource - RitsuLib combat state, payment, and live counter

Use this capability when Cards or other character-owned effects gain and spend one or more
named nonnegative resources. It is a selected Character capability, not a new content type
and not a replacement for native Energy or Stars.


## Semantic contract

For each resource, SPEC records a stable local id, `min/default/max`, persistence, turn-start
policy, localization/icons, and every Card or combat UI consumer. For each Card payment use,
record a globally unique use id, Card id, resource id, required/optional/repeatable-extra role,
fixed or X cost, shortfall policy, and the exact post-commit payoff.

| Field | Required value |
|---|---|
| owner | the local `Player`; RitsuLib stores live amounts on its current `PlayerCombatState` |
| lifetime | `combat` snapshot or `run` save persistence, selected per resource |
| amount domain | bounded nonnegative integer; no implicit debt |
| gain | positive amount and exact source event |
| affordability | `amount >= cost`, checked explicitly |
| spend | the RitsuLib play plan/commit ledger is authoritative; rejection is nondestructive |
| reset/save | exact `Combat` or `Run` persistence and exact built-in turn-start policy |
| UI | selected built-in counter row, Card payment line, or a checked explicit attachment |
| layout | every selected consumer has stable dimensions and a non-overlap rule |
| proof | derive only the selected resources, payments, lifecycle, and consumers from SPEC |

Do not reinterpret this contract as alternative Energy payment. Patching card resource
cost hooks is unsupported. The proven payoff pattern spends inside generated domain/card
behavior and applies the consequence only when RitsuLib reports successful payment.

## Registration and commands

Register every resource once from Mod initialization, before the content pack is used in
combat. Translate the SPEC policy names exactly: `none`, `reset_to_max`,
`add_max_to_current`, and `clear` map to the four `SecondaryResourceTurnStartPolicy`
members; `combat` and `run` map to the matching `SecondaryResourcePersistencePolicy`
members. Do not infer either policy from the resource's name.

```csharp
using STS2RitsuLib;
using STS2RitsuLib.Combat.SecondaryResources;
using STS2RitsuLib.Scaffolding.Godot.NodeAttachments;

private static readonly ModSecondaryResourceRegistry Resources =
    RitsuLibFramework.GetSecondaryResourceRegistry(MainFile.ModId);
private static readonly ModNodeAttachmentRegistry Attachments =
    RitsuLibFramework.GetNodeAttachmentRegistry(MainFile.ModId);

public static SecondaryResourceDefinition Definition { get; private set; } = null!;
public static string Id => Definition.Id;

public static void Register()
{
    Definition = Resources.Register("resource", new SecondaryResourceDefinition(
        defaultAmount: 0,
        minAmount: 0,
        turnStartPolicy: SecondaryResourceTurnStartPolicy.None,
        persistencePolicy: SecondaryResourcePersistencePolicy.Combat,
        smallIconPath: IconPath,
        largeIconPath: IconPath));
    Resources.AlwaysShowInCombatUi("resource");
    Resources.RegisterCombatUi(
        "resource-counter",
        _ => CharacterResourceCounter.Create(),
        UpdateCounter,
        new NodeAttachmentOptions
        {
            Name = "<ModName>ResourceCounter",
            AttachParentSelector = node =>
                ((NCombatUi)node).EnergyCounterContainer,
        });
}
```

Use `SecondaryResourceCmd` as the only amount store and mutation route:

```csharp
public static int Get(Player player) =>
    SecondaryResourceCmd.Get(player, Id);

public static bool CanAfford(Player player, int cost)
{
    ArgumentOutOfRangeException.ThrowIfNegative(cost);
    return Get(player) >= cost;
}

public static Task<int> Gain(
    Player player, int amount, AbstractModel? source = null)
{
    ArgumentOutOfRangeException.ThrowIfNegativeOrZero(amount);
    return SecondaryResourceCmd.Gain(player, Id, amount, source);
}

public static Task<bool> TrySpend(
    Player player,
    int cost,
    CardModel? card = null,
    AbstractModel? source = null)
{
    ArgumentOutOfRangeException.ThrowIfNegative(cost);
    return SecondaryResourceCmd.Spend(player, Id, cost, card, source);
}
```

Do not add a duplicate `int`, `ScopedState`, save property, or combat-start reset hook.
RitsuLib owns the amount, combat snapshots, and run-save persistence. Direct
`SecondaryResourceCmd.Spend` remains the route for an effect that explicitly pays inside
its own behavior; a Card cost or named Card use must use the play-use planner below.

The spender applies its payoff only after payment:

```csharp
bool paid = await CharacterResource.TrySpend(Owner, cost, this, this);
if (paid)
    await CreatureCmd.GainBlock(Owner.Creature, DynamicVars.Block, cardPlay);
```

## Card payment uses

Use `SecondaryCosts()` or `SecondaryResourceUses()` so `CanPlay`, `SpendResources`,
auto-play bookkeeping, Card UI, and the post-commit ledger agree. Required entries reserve
their amounts before repeatable-extra and optional entries. Use ids are unique across all
three contribution routes on that Card.

- required fixed/X: `.Require(...)`; default shortfall blocks play;
- optional fixed/X: `.SpendIfAvailable(...)`; it never blocks play and its payoff checks
  `cardPlay.SecondaryResources().Activated(useId)`;
- repeatable extra: `.SpendExtra(...)` with a positive per-stack amount and optional positive
  max stacks; it cannot use X, and payoff reads `ExtraStacksByUse(useId)`;
- allowed shortfall: `.RequireAllowingShortfall(...)`, with `spendAvailable` matching the
  declaration; any remaining-shortfall effect runs only during commit;
- replacement: a side-effect-free resolver reads one different declared resource during
  planning and returns a bounded `Cover(...)` callback that spends it only at commit.

No planner mutates state. No Card payoff guesses affordability or reruns payment. It reads
the committed `SecondaryResourcePlayLedger`; this preserves preview, rejection, auto-play,
and execution as one transaction.

## Public combat UI attachment

Prefer RitsuLib's built-in `NSecondaryResourceCounterRow` for one or more visible combat
counters and `NSecondaryResourceCardCostUi.Create(...)` / `CreateForUse(...)` for each
declared Card payment line. Register them through `RegisterCombatUi` / `RegisterCardUi` and
bind only the declared definitions or use ids. Use a custom combat attachment only when the
SPEC selects additional bounded mechanic text that the built-in row cannot render. Do not
emit a Harmony `NCombatUi.Activate` postfix or a separate patch module.

The update callback must use the context's local player and `VisibleDefinitions`, keep the
control hidden when this resource is not visible, and render the current resource plus any
bounded mechanic state:

```csharp
private static void UpdateCounter(
    SecondaryResourceCombatUiContext<NCombatUi, CharacterResourceCounter> context)
{
    var visible = context.Player != null &&
        context.VisibleDefinitions.Any(definition => definition.Id == Id);
    context.Node.Visible = visible;
    if (!visible) return;

    context.Node.ValueLabel.Text =
        $"{DisplayName}: {Get(context.Player!)}" +
        MechanicStateText.GetOptionalSuffix(context.Player!);
}

public static bool TryGetMounted(
    NCombatUi ui, out CharacterResourceCounter counter) =>
    Attachments.TryGetAttached(ui, "resource-counter", out counter);

public static void Refresh(Player player)
{
    if (NCombatRoom.Instance?.Ui is { } ui)
        SecondaryResourceUiRuntime.UpdateCombatUi(ui, player);
}
```

The fixed control is an `HBoxContainer` with:

- `CustomMinimumSize = new Vector2(220, 32)`;
- `Position = new Vector2(160, 0)` so it does not overlap the 128x128 native Character
  energy counter;
- an optional existence-checked 24x24 `TextureRect`;
- a minimum 188x32 live `Label`;
- resource/lifetime metadata for diagnostics;
- identical live text when the icon is missing.

RitsuLib owns attachment and combat-UI lifecycle. Call `Refresh(player)` after a state
change that does not itself mutate the secondary resource, such as clearing a composed
ordered buffer. Resource gain/spend already travels through `SecondaryResourceCmd`.

## Verification owed by a generated Mod

Verify only the resources and variants selected by the current SPEC. At minimum, drive the
real Card play/payment lifecycle and the declared persistence boundary; add a second combat
or save round trip only when that selected policy needs it. Assert:

1. every selected resource starts at its declared default and remains inside its bounds;
2. gain changes amount, affordability, and visible text;
3. one successful spend changes amount and payoff exactly once;
4. one rejected spend leaves amount/payoff unchanged and never goes negative;
5. each selected counter/payment line is bound to the right definition/use and does not
   overlap native Energy/Stars or another declared consumer;
6. turn-start and combat/run persistence match SPEC, including save/resume only when claimed.

The maintained harness derives the resource name, gain/spend amounts, payoff, and expected
counter states from the current `SPEC.md`. It reaches `selftest done` only after the exact
configured values, rejected-payment invariants, disjoint UI, and distinct combat-2 reset
state pass.

## Unsupported extensions

- partial, hybrid, or alternative-Energy engine payment;
- prompt-authored arbitrary payment delegates or replacement sources outside the declared
  bounded secondary-resource plan;
- arbitrary UI hosting, animated UI, or custom-zone presentation;
- remote-player or multiplayer resource UI;
- a private patch fallback when the public attachment is unavailable.

These are outside this route; do not stretch it to approximate them. A request for one follows
`grounding.md` § Mod-local Routes, and the private patch fallback stays unsupported.
