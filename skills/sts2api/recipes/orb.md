# Recipe: Custom Orb

An Orb is real content with its own identity and slot lifecycle, but no trigger of its own:
every behavior runs through a host Card, Relic, or Power that channels it. A useful Orb has four
invariants: registration, channel presence, passive behavior, and evoke behavior with removal.
Read `reference/vanilla-text-style.md` for every string.

## SPEC fields

The host is named in `registration.placement`, and the three behaviors are separate `effects`
entries rather than one sequence.

```markdown
- **content**:
  - name: <shown name>
  - surface: orb
  - logical id: <stable local stem>
  - relations: <the Card/relic/Power that channels it>
- **registration**:
  - availability: shared | character:<name>
  - ownership: player
  - placement: channelled by <the Card/relic/Power that channels it, and when>
- **localization**:
  - languages: [eng, zhs]
  - fields: title=<shown name>; description=<plain fallback text, read when no
    smartDescription resolves>
  - smartDescription: <text using {Passive} and {Evoke}; required for live values>
  - formatting: vanilla text style (`reference/vanilla-text-style.md`); dynamic value placeholders
  - extra emphasis: none | <description phrase -> color the default style would not apply>
- **effects**:
  - trigger: channel | per-turn passive | evoke (three independent behaviors)
  - target: <per behavior>
  - channel: <what happens when the host channels it>
  - passive: <what it does per turn, with numbers>
  - evoke: <what it does when evoked, with numbers>
  - scaling: passive value <declared scaling name and value>; evoke value <declared
    scaling name and value>
- **hook participation**: none | one or more; see § Hook participation below
- **state**:
  - lifetime: combat
  - owner: the player's orb queue
  - advance/check: slots <how the design expects capacity to be obtained, and its bounds>
  - reset: combat end
  - persistence: none
  - eviction: engine default (oldest evoked first when channeling into full slots) |
    <the declared design if it intentionally differs>
  - visible state: native orb queue display
- **presentation**:
  - assets: orb icon; placeholder | generate (one 100x100 icon; the persistent combat body
    stays the checked Frost Spine fallback)
  - art source: host-tool | backend:<name> | local-image (generate only)
  - native presentation: smart tooltip plus trigger flash
- **fallback**:
  - missing asset: checked Frost orb icon; the Frost Spine body and, unless the user supplied
    one (`reference/audio.md`), the Frost channel SFX remain
  - unavailable seam: preserve behavior or stop with an explicit unsupported boundary
- **proof**:
  - scenario: CombatPlayer
  - driver: channel through the real host, advance a turn, then evoke
  - invariants: <exact expected/observed state for channel, passive, and evoke>
  - boundary cases: <full-slot eviction, empty-queue evoke, or none>
- **adapter output** (written to MEMORY after acceptance): resolved content id,
  localization keys (`title`, `description`, `smartDescription`), orb icon asset role, and
  framework diagnostic record
```

## Registration

Register once with `ModOrbTemplate`; never add `[Pool]` or rely on constructor discovery.
RitsuLib derives `MOD_ORB_TYPENAME`: `ShelterOrb` in `ExampleMod` becomes
`EXAMPLE_MOD_ORB_SHELTER_ORB`.

```csharp
RitsuLibFramework.CreateContentPack(ModId)
    .Orb<<Name>Orb>()
    .Apply();
```

## Skeleton

Add `<ModName>Code/Orbs/<Name>Orb.cs`:

```csharp
using System.Collections.Generic;
using System.Threading.Tasks;
using Godot;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.ValueProps;
using STS2RitsuLib.Scaffolding.Content;

namespace <ModName>.Orbs;

public sealed class <Name>Orb : ModOrbTemplate
{
    protected override string ChannelSfx =>
        "event:/sfx/characters/defect/defect_frost_channel";

    public override Color DarkenedColor => new("7860a7");
    public override decimal PassiveVal => ModifyOrbValue(2m);
    public override decimal EvokeVal => ModifyOrbValue(5m);
    public override ModOrbValueDisplayMode ValueDisplayMode =>
        ModOrbValueDisplayMode.Contextual;

    public override OrbAssetProfile AssetProfile =>
        ContentAssetProfiles.Orb("frost_orb");

    public override Task BeforeTurnEndOrbTrigger(PlayerChoiceContext choiceContext) =>
        Passive(choiceContext, null);

    public override async Task Passive(
        PlayerChoiceContext choiceContext, Creature? target)
    {
        if (target is not null)
            throw new InvalidOperationException("This Orb does not target creatures");
        Trigger();
        await CreatureCmd.GainBlock(
            Owner.Creature, PassiveVal, ValueProp.Unpowered, null);
    }

    public override async Task<IEnumerable<Creature>> Evoke(
        PlayerChoiceContext choiceContext)
    {
        await CreatureCmd.GainBlock(
            Owner.Creature, EvokeVal, ValueProp.Unpowered, null);
        return new[] { Owner.Creature };
    }
}
```

`ContentAssetProfiles.Orb("frost_orb")` is the checked placeholder: Frost icon plus Frost Spine
combat scene. A generated 100x100 icon (shared by the smart tooltip and trigger flash) may
replace only `IconPath`; it never promotes a custom combat body. Keep the explicit native
`ChannelSfx`: channeling always plays one, and an empty custom value probes a missing
debug-audio file. The user's own channel, passive, or evoke sound replaces it per
`reference/audio.md`.

## The three behaviors

`Passive(PlayerChoiceContext choiceContext, Creature? target)` and
`Evoke(PlayerChoiceContext choiceContext)` supply the real choice context, `Owner` (a `Player`),
`Owner.Creature`, no Card source, and only the target explicitly passed to the passive. Lower each
behavior through `reference/effect-primitives.md` (which also owns channel, evoke, and slot
signatures) and return the exact Creatures `Evoke` affected. The host Card/Relic/Power owns the
`OrbCmd.Channel<T>` call and its own bindings; never channel from the Orb itself. A direct
`OrbCmd.Passive` call is diagnostic only, never a substitute for the native turn callback.

## Hook participation

Channel, passive, and evoke are the Orb acting. A SPEC `hook participation` block is the engine
asking the queued Orb for a number or decision while resolving something else, a fourth,
independent behavior (`reference/model-hook-participation.md`). An Orb receives combat-scope
hooks only (45 of 68); run-scope hooks never reach it, and Build rejects them. `Owner` is a
`Player`, so a subject guard goes through `Owner.Creature`. Participation holds only while the Orb
is queued and stops when it is evoked out; state that in SPEC if the design depends on it.

## Optional routes

Keep channel/passive/evoke in their native methods. Read a route only when SPEC selects it,
append only its SPEC block for an independent rule, and preserve phase/order, neutral behavior,
combat cleanup, display refresh, and real queue-host assertions. The Orb or its typed capability
is reachable only while queued. Never use a process-wide listener.

- a separable Orb-owned behavior/state bundle: `reference/model-capabilities.md`;
- lifecycle/persistence/RNG: `reference/lifecycle-state-rng.md`;
- reachable per-hit attack, healing, Energy/Stars-gain response, or maximum hand size:
  `reference/shared-effect-hooks.md`;
- a right-click on the Orb: `reference/model-right-click.md`.

## Localization: `smartDescription` is what makes the numbers live

`OrbModel` substitutes `{Passive}`, `{Evoke}`, and `{energyPrefix}` only when a
`.smartDescription` key exists. Without it the engine falls back to a dumb tip that shows
`.description` verbatim, so any runtime-modified value, Focus included, stays invisible while the
tooltip states the base number. Ship all three keys in matching `localization/eng/orbs.json` and
`localization/zhs/orbs.json`:

```json
{
  "<MOD>_ORB_<TYPE>.title": "Display Name",
  "<MOD>_ORB_<TYPE>.description": "Orb: Gains [gold]Block[/gold].",
  "<MOD>_ORB_<TYPE>.smartDescription": "[gold]Passive:[/gold] At the end of turn, gain [blue]{Passive}[/blue] [gold]Block[/gold].\n[gold]Evoke:[/gold] Gain [blue]{Evoke}[/blue] [gold]Block[/gold]."
}
```

```json
{
  "<MOD>_ORB_<TYPE>.title": "显示名称",
  "<MOD>_ORB_<TYPE>.description": "充能球：获得[gold]格挡[/gold]。",
  "<MOD>_ORB_<TYPE>.smartDescription": "[gold]被动：[/gold]在回合结束时，获得[blue]{Passive}[/blue]点[gold]格挡[/gold]。\n[gold]激发：[/gold]获得[blue]{Evoke}[/blue]点[gold]格挡[/gold]。"
}
```

This is the vanilla `FROST_ORB` shape (Orb row of `reference/vanilla-text-style.md`): a short
general `.description` and a two-line `.smartDescription` with `[blue]` values. The `Passive:` and
`Evoke:` labels are author-written, not engine-composed; only the values are substituted.

## Self-test driver body

An Orb gets a named `plan.Combat` scenario driven entirely through the real host: channel via the
host, `await t.EndTurn()` so the passive fires on its own, then evoke. `OrbCmd.Channel<T>`,
`OrbCmd.Passive`, and `OrbCmd.EvokeNext` are host commands; calling `OrbCmd.Passive` directly is
a diagnostic, not the passive proof.

## Proof matrix

- Assert queue capacity and presence after channel, with the title resolving to shipped
  localization.
- Assert the passive and evoke post-states with exact expected/observed values, and removal
  from the queue after evoke.
- **Prove all three behaviors, not one.** An Orb that channels and evokes correctly but whose
  passive never fires is a different design.
- **Fire the passive through the real per-turn path.** The engine triggers passives from the
  turn-end queue walk, which consults a public trigger-count hook; a direct `OrbCmd.Passive`
  bypasses it, so a passive the game would never trigger still passes. Advance a real turn and
  assert the resulting state.
- Assert the declared slot bounds and the full-slot case: channeling into full slots evokes the
  oldest Orb first. Under `engine default`, assert that observed order rather than assuming it.
- **Hook participation: assert the neutral case outside the guard.** The three behavior
  assertions observe none of it. Drive one event the guard ignores and assert the host's value is
  unchanged; assert participation after evoke only if the design says it holds. For a collection
  edit, assert an unrelated entry survives.
- Assert `{Passive}`/`{Evoke}` resolve in the real smart tooltip; a dumb-tip fallback shows
  plausible text and hides a missing `smartDescription` from every state assertion. Visible icon
  support also needs the real smart tooltip and trigger flash in a headed run; the persistent
  body stays labeled as the Frost fallback until a custom Spine scene is separately proven.

## Manual fallback (only when the harness cannot reach its scenario)

No dev-console command grants an Orb. Grant its **channel host** through that host's recipe,
then play or trigger the host to channel, end a turn for the passive, and evoke. An Orb reached
any other way is not evidence that its declared host channels it.
