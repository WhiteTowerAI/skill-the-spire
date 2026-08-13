# Relic and Power extra corner labels

Use this reference when a Relic or custom Power SPEC selects supplemental player-readable
values. The labels supplement the native main amount; they never replace it. This route is
pinned to STS2 `0.107.1` and RitsuLib `0.5.11` and uses the public Extra Badges Package.

## Generated bounds

- Relics may generate at most three labels, using each of `TopLeft`, `TopRight`, and
  `BottomLeft` at most once.
- Powers may generate at most one supplemental label and must use `TopLeft`. This preserves
  the documented dual-number use case while avoiding overlapping preset bands in crowded
  Power rows.
- Never generate `BottomRight`; the native main count commonly owns it.
- The public Package supports `Custom`, but normal natural-language authoring does not
  accept arbitrary rectangles. A custom slot requires a separately checked host-specific
  layout and is not lowered by this recipe.
- Relic: at most 4 visible characters per label.
- Power: at most 6 visible characters per label.
- Count visible text after formatting and after removing rich-text tags. Empty text means
  the label is absent. Stop authoring rather than silently truncating a semantic value.
- Plain text is the default. Bounded rich text allows exactly one balanced, non-nested
  `[color=blue|gold|green|purple|red]...[/color]` span and no other BBCode. The interview
  records color intent, never raw markup.

Labels may use a bounded integer formatter with one fixed prefix or suffix such as `+2`,
`x3`, `4%`, or `2/3`, provided the worst-case visible text stays within the host limit.
No arbitrary strings, user-controlled markup, icons, polling, animation, or remote-player
state belong in this slice.

## Provider route

Implement exactly the specs provider for the host:

```csharp
using STS2RitsuLib.Combat.Ui.ExtraCornerAmountLabels;

public sealed class <PowerName> : ModPowerTemplate,
    IPowerExtraIconAmountLabelSpecsProvider
{
    public IReadOnlyList<ExtraIconAmountLabelSpec> GetPowerExtraIconAmountLabelSpecs()
    {
        return <show badge>
            ? [ExtraIconAmountLabelSpec.Plain(
                ExtraIconAmountLabelCorner.TopLeft, <bounded text>)]
            : [];
    }
}
```

For a Relic, use `IRelicExtraIconAmountLabelSpecsProvider` and
`GetRelicExtraIconAmountLabelSpecs()`. Emit `ExtraIconAmountLabelSpec.RichText(...)` only
after lowering the bounded color intent. Keep SPEC order in the returned list. Duplicate
preset corners are invalid even though the runtime skips later duplicates with a warning.

The pinned Power presets are not clipped to one compact Power icon: `TopLeft` and
`BottomLeft` each use a 100-pixel-wide band, while `TopRight` extends from x=-56 to x=44.
Do not combine those presets or generate a custom rectangle to compensate. A new
host-specific layout would need separate geometry design and headed proof.

## Refresh and removal

When the badge follows the host's normal main amount, update that state through the normal
model path and call the protected `InvokeDisplayAmountChanged()` when the model owns the
mutation. RitsuLib rereads the specs after the host refreshes its amount.

When a separate field controls the badge and no normal display event fires, implement the
matching change source and raise it immediately after the successful mutation:

```csharp
public event Action? PowerExtraIconAmountLabelsInvalidated;

private void InvalidateExtraBadges()
{
    PowerExtraIconAmountLabelsInvalidated?.Invoke();
}
```

Relics use `IRelicExtraIconAmountLabelsChangeSource` and
`RelicExtraIconAmountLabelsInvalidated`. Powers use
`IPowerExtraIconAmountLabelsChangeSource` and
`PowerExtraIconAmountLabelsInvalidated`. Do not raise both the host display event and an
extra-label event for the same mutation. Do not poll every frame.

Removal is data-driven: after the declared removal condition becomes true, return no spec
for that label and raise the same refresh path. RitsuLib owns label-node removal,
unsubscription on host destruction, and combat-transition cleanup.

## Verification

Use the matching real Relic/Power combat consumer. Structured checks must prove the model
state and returned spec sequence for zero/one Power labels and zero/one/bounded-multiple
Relic labels; exact plain/rich text; state-driven refresh; removal; the selected safe
corners; and preservation of the native main amount. A provider return value alone does
not prove presentation.

Headed observation must inspect a crowded Relic row and crowded Power row at common aspect
ratios, then confirm that labels remain readable and do not overlap the native icon, main
counter, tooltip, or adjacent labels. It must also confirm removal and cleanup after host
destruction or combat transition.

Intent belongs to the supported public Extra Badges Package, but no Intent authoring recipe
exists yet. Do not adapt this Relic/Power recipe to Intent, and do not describe that missing
recipe as an unsupported capability.
