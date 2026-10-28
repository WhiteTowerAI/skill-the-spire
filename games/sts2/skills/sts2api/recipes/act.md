# Recipe: Custom Act

Use `ModActTemplate` for a complete playable chapter. An Act is not just a background: it owns
one run slot, map generation, weak/regular/elite/Boss Encounter pools, Event and Ancient pools,
treasure and Rest Site presentation, music and ambience, map colors, and an explicit route by
which a singleplayer run enters it.

Registration and reachability are separate. `.Act<T>()` adds the model to `ModelDb` but never
makes a run enter it (the template defaults `AllowInRandomActList` to `false`), so every Act also
selects exactly one supported entry policy. Lifecycle and supplied-RNG rules are in
`reference/lifecycle-state-rng.md`; never use `System.Random`, process-local randomness, or a
Progression route.

## DESIGN and SPEC vocabulary

Settle and write:

- slot/index: first, second, or third chapter (`0`, `1`, or `2`);
- entry policy: force (one Act or a weighted candidate set), uniform pool with the existing
  chapter, or weighted pool with the existing chapter;
- eligibility, force priority, and tie behavior; for weighted entry, every candidate weight
  relative to the existing chapter's fixed weight 1;
- map length and exact Unknown/Rest counts, or deterministic formulas over the supplied map RNG;
- nonempty weak, regular, elite, and Boss Encounter sets, Boss discovery order, ordinary Events,
  and Shared/Act-scoped Ancient relations;
- unlock policy: available under the selected singleplayer entry rule; new
  Progression/epoch/unlock integration is deferred;
- title in English and Simplified Chinese (plain Title Case per
  `reference/vanilla-text-style.md`; its Encounters, Events, and Ancients follow their own rows),
  map colors, music/banks/ambience, chest resource/skins/sound, background, combat layers, Rest
  Site scene, and three map textures; and
- a real Act-transition SelfTest that reaches map, weak/regular/elite/Boss combat, Event,
  Ancient, chest, and Rest Site consumers.

An entry rule needs no mode gate: every peer resolves the same deterministic rule from the same
run state, and RitsuLib re-syncs the map selection after it replaces an Act, so a forced, uniform,
or weighted Act works in singleplayer and multiplayer alike. Use `ctx.IsMultiplayer` only when
SPEC makes the Act mode-specific. Keep `AllowInRandomActList == false`: the organic vanilla
random-list opt-in is a separate placement this route does not prove.

## Registration and entry

Choose exactly one entry mode for the selected slot:

```csharp
ModContentPackBuilder.For(MainFile.ModId)
    .Act<<ActName>>()
    .ActEnterForce<<ActName>>(
        slotIndex: <0|1|2>,
        priority: <integer>,
        eligibility: static ctx => <plain condition>)
    .Apply();
```

Uniform selection includes the existing chapter automatically:

```csharp
.ActEnterUniformPool(<slot>)
.ActEnterUniformPoolCandidate<<ActName>>(
    <slot>, static ctx => <condition>)
```

Weighted selection also includes the existing chapter at fixed weight 1; only candidate weights
are configurable, so "the existing chapter is twice as likely" is candidate weight `0.5`. Declare
the pool first, then its candidates; non-finite or nonpositive weights are ignored:

```csharp
.ActEnterWeightedPool(<slot>)
.ActEnterWeightedPoolCandidate<<ActName>>(
    <slot>,
    static ctx => <condition>,
    static ctx => <positive double>)
```

A Mod declares one mode per slot; another Mod's uniform and weighted contributions to the same
slot coexist with it. To replace the slot with one of several Acts and never keep the existing
chapter, force a weighted candidate set:

```csharp
.ActEnterForcePool(
    slotIndex: <slot>,
    priority: <integer>,
    eligibility: static ctx => <condition>,
    (typeof(<ActA>), <positive double>),
    (typeof(<ActB>), <positive double>))
```

Higher force priority wins; equal priority uses earlier registration. The resolver supplies
`ActEnterResolveContext` with `RunState`, `UnlockState`, `EnteringActIndex`, `IsMultiplayer`, and
the run's `Rng.Niche`, which uniform/weighted selection consumes. Never roll with
`System.Random` or consume RNG in a preview or eligibility check.

## Required model contract

The template wires assets but does not implement `ActModel` gameplay. Override every required
member:

- identity/selection: `Index` (`0..2`), `IsDefault => false`, and
  `IsUnlocked(UnlockState) => true` while Progression integration is deferred;
- room shape: positive `BaseNumberOfRooms`, optional `NumberOfWeakEncounters`, and
  `GetMapPointTypes(Rng mapRng)` using only `mapRng`;
- content: `GenerateAllEncounters()`, `BossDiscoveryOrder`, `AllEvents`, `AllAncients`, and
  `GetUnlockedAncients(UnlockState)`;
- discovery: `ApplyActDiscoveryOrderModifications(UnlockState)`, empty unless SPEC defines a
  non-Progression ordering rule;
- map: `MapTraveledColor`, `MapUntraveledColor`, and `MapBgColor`;
- audio: `BgMusicOptions`, `MusicBankPaths`, `AmbientSfx`, and `ChestOpenSfx`; and
- chest: `ChestSpineSkinNameNormal` and `ChestSpineSkinNameStroke`, plus the profile's exact
  `ChestSpineResourcePath`.

`GenerateAllEncounters()` must leave the derived weak, regular, elite, and Boss groups nonempty;
list every canonical referenced model with `ModelDb.*<T>()`. RitsuLib appends `.ActEncounter`,
`.ActEvent`, and `.ActAncient` registrations dynamically, but the final runtime pools still owe
that invariant: an Act with an empty group compiles and fails during room creation.

Register related nodes exactly once, using `recipes/monster.md`, `recipes/event.md`, and
`recipes/ancient.md` for their contracts:

```csharp
.Monster<<Monster>>()
.ActEncounter<<ActName>, <Encounter>>()
.ActEvent<<ActName>, <Event>>()
.ActAncient<<ActName>, <Ancient>>()
```

## Assets and localization

Ship identical-key `localization/eng/acts.json` and `localization/zhs/acts.json`:

```json
{
  "<MOD>_ACT_<ACT>.title": "<plain Title Case name>"
}
```

`ActAssetProfile` owns the background scene, Rest Site scene, top/middle/bottom map textures,
chest Spine resource, and optional combat-background layer directory. Prefer explicit Mod-local
`res://` paths. `ContentAssetProfiles.FromVanillaActId("hive")` derives paths from a vanilla
folder name, not a model id, so validate every derived resource. Base-game chest resources use
numbered paths (`act_1`, `act_2`, `act_3`), so never assume a folder-derived chest path exists;
override that field with the exact vanilla or Mod-local resource and matching skin names and SFX.

Missing or invalid Act scenes, layers, map textures, chest Spine/skins, music banks, or events are
Build- or runtime-visible failures, not implicit fallbacks. Reusing an exact checked vanilla
profile is the placeholder route; custom presentation needs headed proof.

## Proof matrix

Use a fresh singleplayer run and the real transition into the selected slot: a
`plan.Act<TAct>(name, body, slotIndex)` scenario enters it through
`RunManager.Instance.EnterAct(slotIndex)`, the transition the entry rule resolves in (the dev
console's `act <n>` takes the same path), waits for the new map and room, and runs after every
other scenario. The world helpers enter its rooms:

```csharp
plan.Act<EmberWilds>("ember_wilds_takes_slot_two", async t =>
{
    t.Proof(t.Act is EmberWilds && t.Run.CurrentActIndex == 1,
        $"slot 2 act expected=EmberWilds observed={t.Act.GetType().Name} index={t.Run.CurrentActIndex}");
    var act = t.Act;
    var map = t.MapPointCounts();
    t.Proof(act.AllWeakEncounters.Any() && act.AllRegularEncounters.Any() && act.AllEliteEncounters.Any() &&
            act.AllBossEncounters.Any() && act.AllEvents.Any() && act.AllAncients.Any(),
        $"pools weak={act.AllWeakEncounters.Count()} boss={act.AllBossEncounters.Count()} " +
        $"map={string.Join(",", map.Select(pair => $"{pair.Key}:{pair.Value}"))}");
    await t.Fight(act.AllWeakEncounters.First());
    await t.WinCombat();
    await t.Fight(act.BossEncounter ?? act.AllBossEncounters.First());
    await t.WinCombat();
    await t.EnterTreasure();
    await t.EnterRestSite();
}, slotIndex: 1, budgetSeconds: 180);
```

`GetMapPointTypes` counts are generation targets: the generated map also holds the fixed rows (a
probe declaring five Rest Sites showed seven), so assert SPEC's counts against the map the kit
reports. A maintainer probe Act gates its entry rule on `CommandLineHelper.HasArg("t2selftest")` so it never replaces a slot in a player's
real runs. Prove:

1. assert the canonical Act is registered once and the mutable run Act occupies only its selected
   slot after the declared force/pool rule resolves;
2. drive eligible and ineligible contexts and, for force rules, priority/tie behavior; for
   uniform or weighted pools, inject deterministic supplied RNG and assert the selected candidate
   without claiming a statistical distribution;
3. assert the generated map has the declared floor and point counts (the map also holds fixed
   rows beyond `GetMapPointTypes`) and every runtime-required Encounter/Ancient pool is nonempty;
4. enter representative weak, regular, elite, Boss, ordinary Event, Ancient, chest, and Rest Site
   nodes and assert their exact registered identities and post-state;
5. save/load in the Act and assert the same mutable Act identity, room state, and no duplicate
   registration or re-roll; and
6. headed review checks map/background layering, path colors, chest, Rest Site, music/ambience,
   and mouse/controller navigation.

Compile, model lookup, calling an entry predicate, or inspecting a generated list establishes
neither Act entry nor usable rooms and assets.
