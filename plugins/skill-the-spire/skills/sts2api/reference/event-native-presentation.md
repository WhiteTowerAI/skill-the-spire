# Native Event Acquisition, Screen Shake, and Built-in VFX

Normal/default-layout Events may use three bounded native presentation contracts. They
reuse the game's public commands and existing visual hosts; generated mods do not create
replacement acquisition UI, a screen-shake node, or a custom VFX scene.

## Supported profiles

| Contract | Supported shape | Native consumer |
|---|---|---|
| Card acquisition | each declared known Card added to `PileType.Deck` once, previewed from that successful `CardPileCmd.Add` result | `NRun.GlobalUi.CardPreviewContainer` plus the native card-fly VFX |
| Relic acquisition | each declared known Relic obtained through exactly one awaited `RelicCmd.Obtain` | `NRelicInventory` newly-acquired animation, sound, seen-state, and `AfterObtained` |
| screen shake | one optional allowlisted profile: `weak_short` or `strong_normal`, after the named successful consequence and before its page transition | the game's current `NScreenShake` target and player-configured multiplier |
| built-in Event VFX | `trial_noble`: the pinned Trial scene at its vanilla portrait-local position | normal `NEventLayout` portrait host; scene-owned animation and inherited pause mode |

These profiles may be composed in one option. Acquisitions are an ordered bounded list, each
semantic acquisition happens exactly once, and each presentation consumes the result of that
same successful grant. Do not create a second grant or a custom holder.

## Card acquisition preview

Create the Card through the run, await the real deck addition, and pass that exact result
to the preview:

```csharp
var card = owner.RunState.CreateCard<MyCard>(owner);
var result = await CardPileCmd.Add(card, PileType.Deck);
CardCmd.PreviewCardPileAdd(result, 2f);
```

The `2f` linger matches vanilla normal Events such as `Bugslayer` and `ByrdonisNest`.
`PreviewCardPileAdd` already checks success, local ownership, test mode, and the current
pile. It is intentionally non-blocking; vanilla Events may transition their page
immediately after starting the preview.

Do not add the Card again, manually create `NCard`, or call `CardCmd.Preview` as a second
acquisition animation. `CardCmd.Preview` is for an existing Card whose mutation should be
shown, such as an enchantment or upgrade; it does not replace the add-result contract.

## Relic acquisition preview

The obtain command owns both semantics and presentation:

```csharp
await RelicCmd.Obtain<MyRelic>(owner);
```

`RelicCmd.Obtain` adds the mutable Relic once, updates grab bags/history, asks
`NRelicInventory` to run its native newly-acquired animation and sound for the local
player, marks it seen, then awaits `AfterObtained`. Do not call `AnimateRelic`, add a
second mutable Relic, or create a custom holder.

`CreateModRelicOption<T>` remains option text/metadata only. When the option actually grants that
Relic, pair it with one awaited `RelicCmd.Obtain<T>` call. Normal-layout option images are
still Ancient-only and remain unsupported.

## One-shot screen shake

The generated allowlist is:

```csharp
NGame.Instance?.ScreenShake(ShakeStrength.Weak, ShakeDuration.Short);
// or, when SPEC selects strong_normal:
NGame.Instance?.ScreenShake(ShakeStrength.Strong, ShakeDuration.Normal);
```

Call the selected profile at most once from one named successful normal-Event option, after any blocking
selection/reward operation finishes and before `SetEventState` or `SetEventFinished`.
`strong_normal` is pinned to The Architect's final-hit native call; it is not permission to
mix arbitrary strengths/durations. Do not generate `Medium`, `TooMuch`, `Long`, `Forever`,
rumble, hit stop, repeated calls, or a custom target.

The game initializes `NScreenShake` from `PrefsSave.ScreenShakeOptionIndex` through
`NScreenshakePaginator.GetShakeMultiplier`: none/some/normal/lots map to the native
multipliers, including zero when disabled. Generated code must not read, override, or
restore that setting. Calling the public API is what respects the preference.

## Curated built-in Event VFX

The only promoted built-in profile is `trial_noble`, grounded from vanilla `Trial`:

```text
scene: res://scenes/vfx/events/trial_noble_vfx.tscn
host: normal NEventLayout portrait child
position: Vector2(292, 68)
process mode: Inherit
```

The earlier research candidate named the Event `VfxContainer`, but the production Trial
implementation uses `NEventLayout.AddVfxAnchoredToPortrait`. Follow the observed host.
No normal vanilla Event model provided a safer reusable `VfxContainer` scene contract.

Add the scene path to the Event's preload inventory, attach one uniquely named instance,
and free only that owned node:

```csharp
private static readonly string TrialNobleVfxPath =
    SceneHelper.GetScenePath("vfx/events/trial_noble_vfx");
private const string TrialNobleVfxName = "<ModName>TrialNobleVfx";

public override IEnumerable<string> GetAssetPaths(IRunState runState)
    => base.GetAssetPaths(runState).Append(TrialNobleVfxPath);

private static Node2D? AttachTrialNobleVfx()
{
    var layout = NEventRoom.Instance?.Layout;
    var portrait = layout?.GetNodeOrNull<TextureRect>("%Portrait");
    if (layout == null || portrait == null)
        return null;
    if (portrait.GetNodeOrNull<Node2D>(TrialNobleVfxName) is { } existing)
        return existing;

    var root = PreloadManager.Cache.GetScene(TrialNobleVfxPath)
        .Instantiate<Node2D>(PackedScene.GenEditState.Disabled);
    root.Name = TrialNobleVfxName;
    root.Position = new Vector2(292f, 68f);
    layout.AddVfxAnchoredToPortrait(root);
    return root;
}

private static void FreeTrialNobleVfx()
{
    var portrait = NEventRoom.Instance?.Layout?
        .GetNodeOrNull<TextureRect>("%Portrait");
    portrait?.GetNodeOrNull<Node>(TrialNobleVfxName)?.QueueFreeSafely();
}
```

Attach it only on explicitly named normal Event pages. Keep `ProcessMode` inherited so the
scene follows the Event/tree pause lifecycle. Free it before switching page or portrait,
entering combat, or finishing onto a page without the profile. `RemoveNodesOnPortrait`
only detaches children and is not sufficient cleanup.

Do not promote the other Trial scenes, arbitrary built-in scenes, custom transforms,
audio, shaders, or arbitrary custom-VFX routes from this one proof. The existing code-native
`portrait_halo` remains a separate supported profile in `event-vfx.md`.

## Verification

Reuse one headed `MapNode` run for every selected contract:

1. enter the real normal Event, wait for description reveal/fade to settle, and capture
   the `trial_noble` profile with readable title, body, and options;
2. click the real enabled option and observe the matching native Card preview; assert the
   exact Card identity, successful deck result, and eventual preview/fly cleanup;
3. assert the Relic inventory gained exactly one matching model and its native holder/icon
   became visibly settled;
4. sample the public screen-shake target: when the preference multiplier is nonzero it
   must move and return to its original position; index zero must produce no movement;
5. assert exact deck/relic deltas, a readable result page, and no owned built-in VFX node;
6. emit one structured marker, `selftest done`, and no fresh error block.

A 2026-07-21 hosted run completed this combined proof in 35 seconds.
It observed Card/Relic deltas `1/1`, shake preference index `2` with movement and return,
the exact Trial scene/path/position/inherited process mode, settled initial/acquisition/
result screenshots, preview/VFX cleanup, strict Tier 2, and no fresh error.

The 2026-07-23 RitsuLib-only Event run repeated these native consumers inside the
combined `MapNode` suite and again reached strict Tier 2, `selftest done`, and no fresh
error. The earlier run remains regression history rather than the active framework proof.
