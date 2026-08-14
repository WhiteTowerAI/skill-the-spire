# Character combat cues

> Implemented on STS2 `0.107.1` / RitsuLib `0.4.67` by the 2026-07-27
> Meridian focused proof. This is a bounded non-Spine frame-sequence contract, not a
> general Character animation pipeline.

Use this page with `recipes/character.md`, `reference/character-presentation.md`, and
`reference/art-contract.md` when a Character SPEC selects combat cues.

## Cue contract

Source sheets are **columns x rows** of 512x512 cells, read left-to-right then
top-to-bottom. The same values are queryable under `character_cues` in
`reference/catalogs/art-contract-sts2-0.107.1.json`, which names `columns`, `rows`, and
`sheet_px` separately so the grid order cannot be misread.

| cue | source sheet (cols x rows) | runtime frames | frame time | behavior |
|---|---|---:|---:|---|
| `Idle` | 2x2 | 4 | 180 ms | loops |
| `Attack` | 2x2 | 4 | 90 ms | one shot, then returns to `Idle` |
| `Hit` | 2x2 | 4 | 80 ms | one shot, then returns to `Idle` |
| `Dead` | 2x3 | 6 | 140 ms | one shot, then holds its final frame |

There is no `Cast` cue. Do not infer extra states, variable frame counts, per-frame timing,
Spine data, transition materials, trails, audio, or merchant/rest animation from this
contract.

Each runtime frame is a transparent 512x512 PNG under
`images/charui/cues/<idle|attack|hit|dead>/<00..>.png`. All eighteen frames share:

- alpha bounds contained by `(26,26)-(486,486)` with exclusive baseline `486`;
- public `VisualNodeStyle` scale `0.80` and position `(0,-184)`;
- bounds position `(-160,-368)` and size `(320,368)`;
- intent `(0,-410)`, center `(0,-184)`, orb `(-178,-230)`, and talk `(0,-420)` anchors.

Do not tune individual frames or actions. The shared geometry is what prevents a cue from
moving the Character, intent, targeting center, orb, or dialogue UI.

## Acquisition and normalization

The four supported source specs are `character_cue_idle`, `character_cue_attack`,
`character_cue_hit`, and `character_cue_dead`. Each is one action-sheet acquisition, so a
complete generated set has an explicit budget of four calls. Every request uses the
normalized selection portrait as `--identity-reference` plus the `character_combat`
style-reference family. The normal art consent rule applies separately to each paid call.

Before the first call, derive one concise neutral combat-anchor sentence from the reviewed
selection portrait and Character description and record it in SPEC. Use the fixed combat
cue prompt in `reference/art-contract.md`, repeating its identity, costume, camera, scale,
pivot, baseline, and neutral-anchor wording verbatim in all four requests. Only the action
sentence, grid, and fixed beats differ. Because these short sequences play quickly, every
adjacent cell is a closely spaced in-between pose with substantial silhouette overlap,
never a jump between distant key poses. Attack and Hit begin near the neutral anchor and
finish already recovering toward Idle; Dead distributes its fall across all six frames.

Import each sheet with the matching lowercase action slug:

```powershell
python ../modmaker/scripts/gen_sprite.py import --spec character_cue_idle --slug idle `
  --input <idle-sheet.png> --out <ModName>/images `
  --identity-reference <ModName>/images/charui/select.png
```

Repeat for `attack`, `hit`, and `dead`. Imports stage the original sheets under
`<project>/art-sources/character-cues/`. The first three sheets do not modify runtime cue
files. Once all four are present, `character_cues.py` processes the bundle and replaces
`images/charui/cues/` only after every action passes.

The deterministic processor owns magenta cleanup, grid splitting, largest connected-body
selection, edge-touch rejection, shared cross-action scaling, baseline alignment, and
Attack/Hit body-height drift rejection against Idle (`0.85..1.15`). It writes per-action
transparent GIFs, cleaned sheets, one contact sheet, and `pipeline-meta.json` under
`<project>/art-review/character-cues/`. A failed import leaves the existing runtime cue
directory unchanged. These processing techniques are adapted from agent-sprite-forge
under its MIT license; no runtime dependency or shipped external asset is introduced.
The contact-sheet review must reject identity/costume drift, apparent-size or camera
changes, baseline/pivot movement, and large adjacent-frame pose jumps; deterministic
geometry checks do not substitute for that visual continuity review.

## Runtime wiring

Treat the four cues as one private combat-only set. Before constructing it, require every
expected resource to exist, load as `Texture2D`, and report exactly 512x512. One missing,
unreadable, or wrongly sized expected frame disables the entire set.

**Never assign the generated set to `CharacterAssetProfile.VisualCues`.** RitsuLib also
consults that profile-level fallback for merchant/rest playback, so a global assignment can
replace the checked world-host texture with combat frames. Keep `AssetProfile.VisualCues`
unset and pass the private set directly from the combat override:

```csharp
protected override ModAnimStateMachine? SetupCustomCombatAnimationStateMachine(
    Node visualsRoot,
    CharacterModel character)
{
    VisualCueSet? cues = <CharacterName>CombatCues.TryBuild();
    return cues is null
        ? null
        : ModAnimStateMachines.StandardCue(
            visualsRoot,
            character,
            idleName: "Idle",
            deadName: "Dead",
            hitName: "Hit",
            attackName: "Attack",
            cueSet: cues);
}
```

When the set is complete, `TryCreateCreatureVisuals()` uses `Idle/00.png` as the initial
texture and creates the shared anchored `NCreatureVisuals`. When it is incomplete, return
the existing static 512x512 `combat.png` factory result. If that static file is also absent,
return `null` so RitsuLib resumes the resolved Character profile fallback. The incomplete
route must create no cue playback node and must never play the surviving action frames.

## Hosted proof

The `RunStart` + `CombatPlayer` harness must prove all of these in real combat:

1. every expected frame path exists at 512x512;
2. Idle advances and loops while the footprint and all five geometry/anchor values stay fixed;
3. an Attack trigger enters Attack and returns to Idle;
4. real damage enters Hit and returns to Idle;
5. leaving the first combat frees its cue playback node;
6. in a fresh combat, death reaches the sixth Dead frame after the contracted duration and
   holds that terminal frame;
7. omitting one expected frame selects the static combat body, creates no playback node,
   and never flashes a remaining cue frame.

Emit `character combat cues complete expected=Idle/Attack/Hit/Dead/cleanup observed=all`
only after the complete route passes. The fallback proof uses
`combat cue fallback expected=one-missing-disables-all/static-combat512/no-playback observed=all`.
Both still require the exact load marker, `selftest done`, no fresh error block, and human
headed confirmation of visible motion or static fallback.

## Unsupported extensions

- `Cast` or any cue beyond Idle/Attack/Hit/Dead;
- Spine skeleton/atlas authoring;
- animated merchant/rest-site bodies;
- Character card trails, custom shaders/material transitions, audio, or remote-player UI;
- using profile-global cues as a shortcut around the combat-only ownership rule.
