# Event Option Presentation

Normal-layout custom Events may use the public `EventOption` presentation seams below.
The Event room owns the buttons and cleanup; generated code supplies typed option data and
does not create a button, tooltip scene, shader, or red-glow node.

## Typed option Hover Tips

`ModEventTemplate` uses the public `EventOption` model. Supply typed `IHoverTip` values
from the grounded factories:

```csharp
new EventOption(this, Inspect, InitialOptionKey("INSPECT"), new IHoverTip[]
{
    HoverTipFactory.FromCard<MyPreview>(upgrade: true),
    HoverTipFactory.FromRelic<MyRelic>().First(),
    HoverTipFactory.FromPotion<MyPotion>(),
    HoverTipFactory.FromPower<MyPower>(2),
});
```

For an enabled option, the real `NEventOptionButton.OnFocus` passes `Option.HoverTips` to
`NHoverTipSet`; Card previews and text descriptions then use their normal native consumers.
`OnUnfocus` removes the set. A null-callback (locked) option retains the supplied data in
its model, but
the vanilla button deliberately skips focus and never creates a Hover Tip. Do not claim
locked-option tooltip presentation or add a custom workaround.

## Relic-backed options and the image blocker

`ModEventTemplate.CreateModRelicOption<T>` is the RitsuLib helper for a custom Event. It
sets the option's `Relic`, owner, title, description, and normal relic metadata. In a
normal Event, the real button displays the relic title/description and its typed text
consumer, but `NEventOptionButton` only creates `%RelicIcon` when
`Event is AncientEventModel`. A normal `ModEventTemplate` therefore has no supported
relic-image button consumer.

Pipeline boundary:

- supported: normal Event `CreateModRelicOption<T>` title/description and semantic acquisition
  through a separate public `RelicCmd.Obtain<T>` consequence;
- deferred: relic image inside a normal Event option;
- deferred: generating an Ancient Event/layout solely to obtain that image, because custom
  Ancient layouts and their dedicated presentation are a later Character-phase seam.

If a user explicitly asks for a normal Event relic image, preserve it as a presentation
gap and keep the normal relic-backed option fallback visible.

## Native lethal-choice warnings

Attach the exact cost to the option before the Event room renders it:

```csharp
new EventOption(this, PayHp, ModOptionKey("PAGE", "PAY_HP"))
    .ThatDoesDamage(damage);
new EventOption(this, PayMaxHp, ModOptionKey("PAGE", "PAY_MAX_HP"))
    .ThatDecreasesMaxHp(maxHpLoss);
```

These helpers only describe the warning; the option's Cmd still owns the actual cost. The
native predicates are inclusive: `CurrentHp <= damage` and `MaxHp <= maxHpLoss` are lethal.
The normal button sets its built-in `RedFlash` to persistent alpha `0.5` for lethal choices
and leaves safe choices at alpha `0`; focusing a lethal choice pulses that same native
glow. Use the exact decimal cost represented by the later Cmd, including DynamicVar values
resolved when options are generated. In solo runs, the player may still choose the
lethal option after seeing the warning; multiplayer death-prevention interaction is outside
this local presentation contract.

## Verification

Reuse `MapNode` in one headed run:

1. focus an enabled option with Card/relic/potion/power tips and prove the real
   `NHoverTipSet` consumers plus cleanup;
2. assert a locked option retains tips but does not show them, and assert a normal
   `CreateModRelicOption<T>` has metadata/title/description but no visible relic image;
3. show safe and exact-lethal HP options together, then a second settled page with safe and
   exact-lethal Max HP options; inspect `RedFlash` alpha and capture both states;
4. drive a real enabled option to its Gold/page consequence and require the strict
   `state proof:` marker, `selftest done`, and no fresh error block.

The 2026-07-23 RitsuLib-only `MapNode` proof repeated the established presentation
contract in the same run as Event core/outcomes: enabled typed tips rendered Card preview,
Relic, Potion, and Power descriptions; locked tips remained hidden; normal relic-backed
metadata rendered without a normal-layout image; and HP/Max HP independently produced
safe/exact-lethal native warning states. The full suite reached `selftest done` with no
fresh error.
