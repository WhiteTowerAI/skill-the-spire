# Normal Event Portrait VFX

This is one bounded, pipeline-supported VFX profile for a normal/default-layout Event:
a code-native portrait halo made from Godot `Node2D`, `Line2D`, and `Polygon2D` nodes. It
was re-verified on RitsuLib `0.4.62` on 2026-07-23 across the initial page, a later
portrait page, Event-to-combat cleanup, and the resumed post-combat page.

This page does not authorize arbitrary VFX scenes, shader generation, custom/Ancient
layouts, phobia assets, combat VFX paths, or animation on other content families.

## Why this route

- `EventModel.OnRoomEnter()` is public.
- `NEventLayout.AddVfxAnchoredToPortrait(Node)` is public and used by vanilla Events.
- The normal layout exposes its `%Portrait` node for owned-child lookup and cleanup.
- RitsuLib exposes optional custom Event VFX/layout routes, but those broader routes are
  not promoted by this proof. The supported profile attaches only through this public
  portrait host.

The VFX is authored as code, not raster art. It has no `gen_sprite.py` spec and does not
require an image backend.

## Supported profile

SPEC may select `portrait_halo` for any authored normal Event page. Each page supplies:

- one unique node name;
- one portrait-local anchor (`Vector2`);
- primary and secondary colors;
- `none` or `portrait_halo` for pages that should have no VFX.

The profile contains two counter-moving arcs, nine diamond motes, and a restrained alpha
pulse. Keep card text and option UI unobscured; anchors belong on the portrait side.

## Helper

Emit one `<ModName>Code/Events/EventVfx.cs` when an Event SPEC selects this profile:

```csharp
using Godot;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.Nodes.Rooms;
using MegaCrit.Sts2.Core.Saves;
using MegaCrit.Sts2.Core.Settings;

namespace <ModName>.<ModName>Code.Events;

internal static class EventVfx
{
    public static Node2D? AttachPortraitHalo(
        string nodeName,
        Vector2 anchor,
        Color primary,
        Color secondary)
    {
        var layout = NEventRoom.Instance?.Layout;
        var portrait = layout?.GetNodeOrNull<TextureRect>("%Portrait");
        if (layout == null || portrait == null)
            return null;

        if (portrait.GetNodeOrNull<Node2D>(nodeName) is { } existing)
            return existing;

        var root = new Node2D
        {
            Name = nodeName,
            Position = anchor,
            Modulate = new Color(1f, 1f, 1f, 0.78f),
        };
        var outer = new Node2D { Name = "OuterOrbit" };
        var inner = new Node2D { Name = "InnerOrbit" };
        root.AddChild(outer);
        root.AddChild(inner);

        outer.AddChild(new Line2D
        {
            Points = ArcPoints(82f, -2.65f, 2.2f, 34),
            Width = 3.5f,
            DefaultColor = primary,
        });
        inner.AddChild(new Line2D
        {
            Points = ArcPoints(58f, -0.65f, 4.15f, 30),
            Width = 2f,
            DefaultColor = secondary,
        });

        for (var i = 0; i < 9; i++)
        {
            var angle = i * MathF.Tau / 9f;
            outer.AddChild(new Polygon2D
            {
                Name = $"Mote{i}",
                Polygon = new[]
                {
                    new Vector2(0f, -6f),
                    new Vector2(4f, 0f),
                    new Vector2(0f, 6f),
                    new Vector2(-4f, 0f),
                },
                Position = Vector2.FromAngle(angle) * (94f + i % 3 * 6f),
                Rotation = angle,
                Color = i % 2 == 0 ? primary : secondary,
            });
        }

        layout.AddVfxAnchoredToPortrait(root);
        if (SaveManager.Instance.PrefsSave.FastMode == FastModeType.Instant)
            return root;

        var duration = SaveManager.Instance.PrefsSave.FastMode == FastModeType.Fast
            ? 1.1
            : 2.2;

        var orbitTween = root.CreateTween().SetLoops();
        orbitTween.TweenProperty(outer, "rotation", 0.1f, duration)
            .SetEase(Tween.EaseType.InOut)
            .SetTrans(Tween.TransitionType.Sine);
        orbitTween.TweenProperty(outer, "rotation", -0.08f, duration)
            .SetEase(Tween.EaseType.InOut)
            .SetTrans(Tween.TransitionType.Sine);

        var counterTween = root.CreateTween().SetLoops();
        counterTween.TweenProperty(inner, "rotation", -0.14f, duration * 0.8)
            .SetEase(Tween.EaseType.InOut)
            .SetTrans(Tween.TransitionType.Sine);
        counterTween.TweenProperty(inner, "rotation", 0.12f, duration * 0.8)
            .SetEase(Tween.EaseType.InOut)
            .SetTrans(Tween.TransitionType.Sine);

        var pulseTween = root.CreateTween().SetLoops();
        pulseTween.TweenProperty(root, "modulate:a", 0.52f, duration * 0.55)
            .SetEase(Tween.EaseType.InOut)
            .SetTrans(Tween.TransitionType.Sine);
        pulseTween.TweenProperty(root, "modulate:a", 0.78f, duration * 0.55)
            .SetEase(Tween.EaseType.InOut)
            .SetTrans(Tween.TransitionType.Sine);
        return root;
    }

    public static void FreePortraitVfx(params string[] nodeNames)
    {
        var portrait = NEventRoom.Instance?.Layout?.GetNodeOrNull<TextureRect>("%Portrait");
        if (portrait == null)
            return;

        foreach (var nodeName in nodeNames)
            portrait.GetNodeOrNull<Node>(nodeName)?.QueueFreeSafely();
    }

    private static Vector2[] ArcPoints(float radius, float start, float end, int segments)
    {
        var points = new Vector2[segments + 1];
        for (var i = 0; i <= segments; i++)
            points[i] = Vector2.FromAngle(
                Mathf.Lerp(start, end, i / (float)segments)) * radius;
        return points;
    }
}
```

## Event integration

Attach the current room's profile from `OnRoomEnter`. Stateful return pages can branch on a
saved/mutable Event field set by `Resume`:

```csharp
public override void OnRoomEnter()
{
    base.OnRoomEnter();
    EventVfx.AttachPortraitHalo(
        InitialVfxNodeName,
        new Vector2(700f, 315f),
        new Color(1f, 0.77f, 0.2f, 0.86f),
        new Color(1f, 0.94f, 0.62f, 0.72f));
}
```

For a later page, free the old named node, switch an optional portrait, attach that page's
profile, then call `SetEventState`. Before entering combat or finishing onto a page without
VFX, free the active named node.

## Cleanup rule

`NEventLayout.RemoveNodesOnPortrait()` detaches portrait children but does not free them.
For every generated VFX node, call `QueueFreeSafely()` through `FreePortraitVfx` before:

1. switching to another page profile;
2. replacing the portrait;
3. entering special combat;
4. finishing the Event when the result page has no profile.

Use unique names and make `AttachPortraitHalo` idempotent so repeated room callbacks never
stack copies. Godot frees the owned tweens with their root node.

## Accessibility and timing

- `FastModeType.Instant`: render the static halo and create no looping tweens.
- `FastModeType.Fast`: use the shorter duration in the helper.
- normal mode: use the standard duration.
- Keep alpha restrained and never flash the whole viewport.
- Do not add sound to this profile.

## Verification

The headed `MapNode` proof must inspect player-visible state, not only model/node presence:

1. capture the initial page with title, description, options, portrait, and halo visible;
2. observe an orbit rotation change unless Fast Mode is Instant;
3. transition to a later page and prove the prior named node is freed;
4. enter special combat and prove no Event portrait VFX remains in-tree;
5. if combat resumes the Event, capture the return page and its configured profile;
6. require the structured Event outcome proof, `selftest done`, and no fresh error block.

This reference supports only the generated `portrait_halo` profile on the normal Event
layout. The separately grounded built-in `trial_noble` profile is documented in
`event-native-presentation.md`; neither contract generalizes arbitrary Event VFX.
