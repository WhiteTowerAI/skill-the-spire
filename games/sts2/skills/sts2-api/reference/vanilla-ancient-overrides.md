# Existing vanilla Ancient overrides

Use this reference after `vanilla-overrides.md` resolves an exact `EVENT.*` target with
`content_kind: ancient`. These routes are pinned to STS2 `0.107.1` and RitsuLib `0.5.11`. They
supports both public initial-option append and one reviewed, fingerprinted initial-option
replacement Adapter while preserving the vanilla model, room, dialogue, save identity,
and Ancient choice-history lifecycle.

## Promoted routes

| Route id | Class | Mode | What it owns |
|---|---|---|---|
| `ancient.initial-options.append` | public | `compose` | One `ModAncientOptionRule` that returns zero or more initial options, with condition, priority, and duplicate-text handling |
| `ancient.initial-options.replace` | adapter | `replace` | The complete initial option list for one exact Ancient type; later public option rules from other Mods may still append |

Both routes use surface `ancient.initial_options`, require `multiplayer: singleplayer`, and
accept ordered custom pages and consequences. The catalog Package is
`m6.7.3-existing-ancient-overrides`.

The exact pinned Ancient targets are `Darv`, `DeprecatedAncientEvent`, `Neow`, `Nonupeipe`,
`Orobas`, `Pael`, `Tanx`, `Tezcatara`, and `Vakuu`. `TheArchitect` is an ordinary
`EventModel` in `0.107.1`, despite the current upstream tutorial example, so the manifest
must reject it as an Ancient target.

## Supported semantic vocabulary

Every option has a stable Mod-local id and localization prefix, two conditions, one fixed
cost, typed presentation, ordered effects, and one next step.

- operation and option visibility conditions: `always`, nested `all`/`any`/`not`, exact
  Character, owner Gold/HP/Max HP/deck/relic/potion counts, and possession of a known
  Card/Relic/Potion;
- cost: none, fixed Gold, fixed HP, or fixed Max HP, with explicit lethal policy;
- option state: visible, hidden, enabled, or native locked;
- presentation: Card/Relic/Potion/Power Hover Tips, optional relic-backed metadata and
  Ancient relic image, and exact native HP/Max HP lethal warning;
- immediate effects: damage, heal, gain/lose Gold, gain/lose Max HP, add one known Card,
  obtain one known Relic, and try to procure one known Potion;
- blocking effects: select deck Cards to upgrade, remove, transform, or enchant; offer a
  fixed custom Gold/Card/Relic/Potion reward list;
- adjacent presentation: the bounded `weak_short` screen shake from
  `event-native-presentation.md`;
- progression: stay on the current page, move to an ordered custom page, or finish through
  the native Ancient `Done()` lifecycle.

Effects execute once in manifest order after successful cost payment. A page transition
waits for every blocking selector/reward. `visible_when` omits an option;
`enabled_when` or an unaffordable nonlethal cost supplies a null callback and therefore a
native locked option. Conditions are recomputed from the mutable Ancient owner whenever
that page is built.

Generated Mod-local options always use `disable_on_chosen: true` and `is_proceed: false`.
The public full-localization `EventOption` constructor does not expose those setters.
Native `Done()` creates the Proceed state, updates Ancient choice history, and finishes the
room. Do not use `StartPreFinished()` as a shortcut: it omits that choice-history update.

## Manifest shape

Model references are typed objects. Use `source: vanilla` only for an exact catalog model;
use `source: mod` for a model registered by the generated Mod.

```json
{
  "order": 0,
  "operation_id": "darv.replace-paths",
  "target_model_id": "EVENT.DARV",
  "mode": "replace",
  "surface": "ancient.initial_options",
  "route": {
    "class": "adapter",
    "id": "ancient.initial-options.replace",
    "fingerprint": "7645a9eea1118c340449e339ede4ce15169c72bed29a196990d8824bbdf12ca5",
    "dependencies": [
      {
        "id": "ancient.flow.finish",
        "fingerprint": "04fef98282aa7e01fbab7934c6f15ca5969b3029c32d4e83ae0ad3636dfcd060"
      },
      {
        "id": "ancient.flow.set-state",
        "fingerprint": "3a93f71ad25d06ad1470da740b5a4bc9095f8dbdb1c6f9d48fed397c0ce1c7b6"
      }
    ]
  },
  "expected_baseline": {
    "category": "EVENT",
    "type": "MegaCrit.Sts2.Core.Models.Events.Darv",
    "content_kind": "ancient"
  },
  "semantics": {
    "condition": {"kind": "always", "parameters": {}},
    "multiplayer": "singleplayer",
    "priority": 0,
    "skip_duplicate_text_keys": false,
    "options": [
      {
        "id": "enter-workshop",
        "localization_key": "EXAMPLEMOD_ANCIENT_ENTER_WORKSHOP",
        "visible_when": {"kind": "always", "parameters": {}},
        "enabled_when": {
          "kind": "owner_value",
          "parameters": {"field": "gold", "comparison": "gte", "value": 25}
        },
        "cost": {"kind": "gold", "amount": 25, "allow_lethal": false},
        "disable_on_chosen": true,
        "is_proceed": false,
        "hover_tips": [
          {
            "kind": "card",
            "model": {"source": "vanilla", "model_id": "CARD.STRIKE_IRONCLAD"},
            "upgraded": true
          }
        ],
        "relic": null,
        "effects": [{"kind": "gain_max_hp", "amount": 3}],
        "next": {"kind": "page", "page": "WORKSHOP"}
      }
    ],
    "pages": [
      {
        "id": "WORKSHOP",
        "description_key": "EXAMPLEMOD_ANCIENT_WORKSHOP_DESCRIPTION",
        "options": [
          {
            "id": "leave-workshop",
            "localization_key": "EXAMPLEMOD_ANCIENT_LEAVE_WORKSHOP",
            "visible_when": {"kind": "always", "parameters": {}},
            "enabled_when": {"kind": "always", "parameters": {}},
            "cost": {"kind": "none", "amount": 0, "allow_lethal": false},
            "disable_on_chosen": true,
            "is_proceed": false,
            "hover_tips": [],
            "relic": null,
            "effects": [],
            "next": {"kind": "finish"}
          }
        ]
      }
    ]
  }
}
```

Dependencies are semantic, not an escape hatch. Include exactly the sorted Adapter ids
required by the selected next steps: `page` requires `ancient.flow.set-state`; `finish`
requires `ancient.flow.finish`. Replacement additionally owns the route fingerprint.
Omit `dependencies` only when every option stays on its current page. Do not add method
names, patch bodies, reflection, or arbitrary IL to the manifest.

Append uses the same semantics with public class, null route fingerprint, `mode: compose`,
and public rule priority/dedup values. Replacement must use priority `0` and
`skip_duplicate_text_keys: false`, because those fields belong to RitsuLib's append
registry. Multiple append rules compose. One replacement conflicts with every append or
replacement for the same exact target in the generated Mod.

## Public append lowering

Register all append rules before ModelDb freezes. A multi-option factory is the normal
route; use `Single(...)` only when the accepted operation can return at most one option.

```csharp
RitsuLibFramework.CreateContentPack(MainFile.ModId)
    .AncientOption<Darv>(new ModAncientOptionRule(ancient =>
        AncientOverrides.BuildDarvInitialOptions(ancient))
    {
        Condition = ancient => AncientOverrides.MatchesRule(ancient),
        Priority = 25,
        SkipDuplicateTextKeys = true,
    })
    .Apply();
```

`BuildDarvInitialOptions` returns options in manifest order after applying each
`visible_when`. Never instantiate or register a second `Darv`, mutate ModelDb, or subclass
the vanilla model.

## Reviewed replacement Adapter

The replacement Adapter is one fixed postfix on
`AncientEventModel.GenerateInitialOptionsWrapper()`. It lets the original method allocate
and retain its native `_generatedOptions` list, then clears and fills that same list. This
is required because `Done()` later reads that list to record Ancient choice history.

Consolidate all selected replacement targets into one patch class and exact-type dispatch.
Run this postfix before RitsuLib's public append postfix so other Mods' registered options
can still append to the replacement result.

```csharp
using HarmonyLib;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Events;
using STS2RitsuLib.Patching.Core;
using STS2RitsuLib.Patching.Models;

internal sealed class AncientInitialOptionsReplacementPatch : IPatchMethod
{
    public static string PatchId => "openmod_m673_ancient_initial_options";
    public static string Description => "Replace selected vanilla Ancient initial options";
    public static ModPatchTarget[] GetTargets() =>
        [new(typeof(AncientEventModel), "GenerateInitialOptionsWrapper", Type.EmptyTypes)];

    [HarmonyBefore("com.ritsukage.sts2-RitsuLib.framework-core")]
    public static void Postfix(
        AncientEventModel __instance,
        ref IReadOnlyList<EventOption> __result)
    {
        if (__result.Count == 1 && __result[0].IsProceed)
            return; // Preserve the game's ShouldAllowAncient blocked state.
        if (__instance.GetType() != typeof(Darv) ||
            !AncientOverrides.MatchesReplacement(__instance))
            return;
        if (__result is not List<EventOption> retained)
            throw new InvalidOperationException(
                "Pinned Ancient generated-options list shape drifted.");

        retained.Clear();
        retained.AddRange(AncientOverrides.BuildDarvInitialOptions(__instance));
        __result = retained;
    }
}
```

Install it once from normal Mod initialization and treat a critical application failure as
a load failure:

```csharp
using STS2RitsuLib;
using STS2RitsuLib.Patching.Core;

var patcher = RitsuLibFramework.CreatePatcher(
    MainFile.ModId, "ancient-overrides", "Ancient option overrides");
patcher.RegisterPatch<AncientInitialOptionsReplacementPatch>();
if (!patcher.PatchAll())
    throw new InvalidOperationException("Ancient override Adapter failed to apply.");
```

This is the only generated Harmony route in the Package. Do not derive another patch from
prompt text. The manifest/catalog validator owns exact target, signature, IL fingerprint,
operation name, and conflict checks before authoring.

## Options, costs, and pages

Use the full public constructor so text remains in the generated Mod's `events` table:

```csharp
var option = new EventOption(
    ancient,
    enabled ? () => RunOption(ancient) : null,
    new LocString("events", $"{key}.title"),
    new LocString("events", $"{key}.description"),
    key,
    hoverTips);
```

For relic-backed presentation, create one mutable relic, assign its owner, and call
`option.WithRelic(relic)`. This supplies the native Ancient relic image/category metadata;
the actual acquisition remains one separate awaited `RelicCmd.Obtain` effect. Attach
`.ThatDoesDamage(amount)` or `.ThatDecreasesMaxHp(amount)` for the exact HP/Max HP cost.

Cost affordability is part of `enabled`, in addition to `enabled_when`. Pay it first with
the checked forms from `event-outcomes.md`: `PlayerCmd.LoseGold(..., GoldLossType.Spent)`,
`CreatureCmd.Damage(...)`, or `CreatureCmd.LoseMaxHp(...)`. Never mutate owner fields or
collections directly. For nonlethal HP and Max HP payment require the post-payment value to
remain positive. Gold cannot use `allow_lethal: true`.

The `.cs` file that lowers a Gold cost must include
`using MegaCrit.Sts2.Core.Entities.Gold;` for `GoldLossType`; imports from another generated
file do not apply.

After cost and ordered effects, lower the next step through only these fixed helpers:

```csharp
using System.Runtime.CompilerServices;

[UnsafeAccessor(UnsafeAccessorKind.Method, Name = "Done")]
private static extern void FinishAncient(AncientEventModel ancient);

[UnsafeAccessor(UnsafeAccessorKind.Method, Name = "SetEventState")]
private static extern void SetAncientState(
    EventModel ancient,
    LocString description,
    IEnumerable<EventOption> options);
```

- `stay`: return after effects; the clicked option is natively disabled;
- `page`: call `SetAncientState(ancient, new LocString("events", descriptionKey),
  BuildPageOptions(ancient))`;
- `finish`: call `FinishAncient(ancient)` exactly once.

These UnsafeAccessor calls are the two fingerprinted flow dependencies. They are fixed,
source-generated access to protected members, not reflection, Publicizer, retained method
names from a prompt, or arbitrary IL.

## Effects and presentation

Reuse the exact public Cmd shapes in `event-outcomes.md` and
`event-native-presentation.md`. In particular:

- create a known Card through `owner.RunState.CreateCard<T>(owner)`, await its real Deck
  add, and preview that same successful result only when `preview: true`;
- obtain a Relic exactly once with `RelicCmd.Obtain`; use
  `PotionCmd.TryToProcure` honestly when a full belt can reject procurement;
- await each `CardSelectCmd.FromDeckForUpgrade/Removal/Transformation/Enchantment` result,
  cap the selected count to the manifest count, then use the matching Card/CardPile Cmd;
- build fixed `GoldReward`, `SpecialCardReward`, `RelicReward`, or `PotionReward` objects
  for `RewardsCmd.OfferCustom`, and await the overlay before progressing;
- call `NGame.Instance?.ScreenShake(ShakeStrength.Weak, ShakeDuration.Short)` at most once
  after successful effects and before page/finish.

Typed Hover Tips use only the matching `HoverTipFactory.FromCard`, `FromRelic`,
`FromPotion`, or `FromPower` overload. A locked option retains its typed data but the
native button does not display Hover Tips; keep that existing presentation boundary.

## Localization and visual composition

Every option prefix must start with `<MOD_ID>_ANCIENT_`. For every shipped localization
directory, including required `eng` and `zhs`,
`<ModId>/localization/<lang>/events.json` contains:

```json
{
  "EXAMPLEMOD_ANCIENT_ENTER_WORKSHOP.title": "Enter the workshop",
  "EXAMPLEMOD_ANCIENT_ENTER_WORKSHOP.description": "Pay 25 Gold. Gain 3 Max HP.",
  "EXAMPLEMOD_ANCIENT_WORKSHOP_DESCRIPTION": "The work is complete."
}
```

Option keys are prefixes and require `.title` plus `.description`; page description keys
are complete table entries. Build preflight rejects missing files, keys, and empty values.
Do not put these non-dialogue keys in `ancients.json`; that table remains owned by native
Ancient dialogue and the existing custom-Character dialogue Package.

`vanilla-visual-overrides.md` composes with these routes for exact existing Ancient visuals: Event background,
layout, initial portrait, VFX, Ancient map icons, and run-history icons. Each requested
visual is still its own checked operation/resource. A visual override changes a scene
resource, not Ancient behavior; do not attach generated scripts or hide gameplay in a
scene.

## Boundaries and checks

Supported replacement means complete initial options plus Mod-owned subsequent pages. It
does not replace the canonical Ancient class, Id, initial native description/dialogue,
room type, save record, map generation, healing/allowance gate, ambient audio, or arbitrary
private state. New Ancient models, global native dialogue replacement, line audio,
randomized outcomes/RNG rewrites, special combat, direct merchant/rest/treasure
transitions, and multiplayer remain outside this Package.

A focused manifest/localization test, a static signature/fingerprint check, and a
representative compile establish the manifest and the build, nothing more. Real Ancient room
behavior, choice history, locked/tip/relic presentation, page selectors, reward overlays, and
visual composition are proved only by observing them in a real Ancient room. An accepted
manifest or a successful compilation is not real-host proof.
