# M6 Native Presentation Items 1-6

Dates: 2026-07-20 and 2026-07-21

Environment: STS2 0.107.1, BaseLib 3.3.5, Windows headed run. The disposable
`baselines/.presentation-canary` project used the existing `CombatPlayer` and `MapNode`
hosts and was retired after evidence capture.

## Presentation 1: cross-content bounded rich text

The real Card body rendered authored `gold`/`purple` spans and its auto-positioned keyword.
The upgraded typed Card preview rendered SmartFormat's green difference. Typed relic,
potion, and power Hover Tips rendered their per-surface allowlists. The existing Block
behavior remained `0 -> 7`.

Structured proof:

```text
CanaryPresentation state proof: presentation1 card=True tips=card,relic,potion,power keyword=True block=0->7
selftest done
PASS Tier-2
Fresh-run errors: none
```

Screenshot: `C:\Users\YY\AppData\Roaming\SlayTheSpire2\canary_presentation_rich_text.png`

## Presentation 2: Event option presentation

Enabled typed Card/relic/potion/power tips reached the native `NHoverTipSet`. Locked options
retained tip data but `NEventOptionButton.OnFocus` suppressed display. Normal `RelicOption<T>`
rendered title/description/metadata and deliberately had no relic image because that button
consumer is Ancient-only. The enabled option changed Gold by 25.

Structured proof:

```text
CanaryPresentation state proof: presentation2 unlockedTips=True lockedTipsVisible=False normalRelicIcon=False gold=25
selftest done
PASS Tier-2
Fresh-run errors: none
```

Screenshot: `C:\Users\YY\AppData\Roaming\SlayTheSpire2\canary_presentation_event_tips.png`

The normal-layout relic image and locked-option tooltip remain explicit presentation gaps;
no Ancient layout or custom tooltip workaround was added.

## Presentation 3: native lethal-choice warnings

The exact Cmd costs were attached through `ThatDoesDamage` and `ThatDecreasesMaxHp`. Native
warnings used inclusive boundaries: `CurrentHp <= damage` and `MaxHp <= maxHpLoss`. Safe
choices had RedFlash alpha 0.00 and exact-lethal choices had alpha 0.50; the actual option
Cmd still owned the cost.

Structured proofs:

```text
CanaryPresentation state proof: presentation3 hpSafe=False hpLethal=True maxSafe=False maxLethal=True glow=0.00/0.50/0.00/0.50
selftest done
PASS Tier-2
Fresh-run errors: none
```

Screenshots:

- `C:\Users\YY\AppData\Roaming\SlayTheSpire2\canary_presentation_lethal_choices.png`
- `C:\Users\YY\AppData\Roaming\SlayTheSpire2\canary_presentation_lethal_max_hp.png`

## Presentation 4-6: acquisition, screen shake, and built-in Event VFX

The disposable `CanaryNativePresentation` project reused the `MapNode` host and combined
the three remaining contracts into one final 35.1-second headed run. It used the real
Card-pile add result for the native Card preview, exactly one native Relic obtain, one
preference-respecting `weak_short` shake, and the pinned `trial_noble` scene at Trial's
actual portrait host and placement. Three settled screenshots covered the initial VFX,
the Card preview plus acquired top-bar relic, and the clean result page.

Structured proof:

```text
native presentation complete
expected=cardPreview+relicPreview+screenShake+builtinEventVfx+cleanup
observed=all
cardDelta=1 relicDelta=1
shakePreference=2 shakeMoved=True
vfxPath=res://scenes/vfx/events/trial_noble_vfx.tscn
selftest done
PASS Tier-2
Fresh-run errors: none
```

Screenshots:

- `C:\Users\YY\AppData\Roaming\SlayTheSpire2\m6_native_presentation_456_initial.png`
- `C:\Users\YY\AppData\Roaming\SlayTheSpire2\m6_native_presentation_456_acquisition.png`
- `C:\Users\YY\AppData\Roaming\SlayTheSpire2\m6_native_presentation_456_settled.png`

The proof observed exact Card/Relic deltas `1/1`, shake movement and return at native
preference index 2, exact VFX position `(292,68)` with inherited process mode, and complete
preview/VFX cleanup. The preliminary `VfxContainer` hypothesis was superseded by vanilla
Trial's `NEventLayout.AddVfxAnchoredToPortrait` contract.

## Promotion boundary

Items 1-6 are promoted through the interview, SPEC, author, API references, recipes, active
verification docs, and generated payloads. Built-in VFX support is limited to the exact
`trial_noble` contract; screen shake is limited to `weak_short`; acquisition must preserve
single-grant semantics. Character static assets and richer character-mechanic UI are next.
