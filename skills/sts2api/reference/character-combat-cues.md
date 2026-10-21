# Character combat cues

> A bounded non-Spine frame-sequence contract, not a general Character
> animation pipeline.

Use this page with `recipes/character.md`, `reference/character-presentation.md`, and
`reference/art-contract.md` when a Character SPEC selects combat cues.

## Cue contract

All four cues come from **one** generated sheet of **4x4** cells (columns x rows), each cell
512x512, so the sheet is **2048x2048**. One image keeps one style, light, and body scale
across every action; four separate action sheets did not, and switching cues then read as a
different person in headed review. The same values are queryable under `character_cues` in
`reference/catalogs/art-contract-sts2-0.107.1.json`.

Cells are numbered 1-16 in reading order (the catalog's `play_cells` count from 0):

| cells | content |
|---|---|
| 1 | the anchor: the approved combat body's pose, redrawn once and shared |
| 2-7 | Attack: crouch, wind-up, mid-swing, strike, follow-through, recovery |
| 8-11 | Hit: flinch, recoil, deepest recoil, steadying (a spare: drawn, not played) |
| 12-16 | Dead: sag, kneel, topple, fall, lying still |

Each cue plays sheet cells in a fixed order. A repeated cell is a hold, and a cell may serve
two cues:

| cue | play order (cells) | runtime frames | frame time | behavior |
|---|---|---:|---:|---|
| `Idle` | 1, breathing | 4 | 250 ms | loops |
| `Attack` | 1, 2, 3, 3, 4, 5, 5, 6, 7 | 9 | 60 ms | one shot, then returns to `Idle` |
| `Hit` | 1, 8, 9, 10, 10, 7 | 6 | 70 ms | one shot, then returns to `Idle` |
| `Dead` | 12, 13, 14, 15, 16 | 5 | 170 ms | one shot, then holds its final frame |

Why this shape, from headed review of a real Character:

- **Shared anchor.** Attack and Hit start on cell 1 itself, the same image Idle breathes,
  so starting a cue never redraws the body. Hit also ends on Attack's recovery (cell 7),
  which keeps the held item; the steadying cell lost it in a real sheet.
- **Breathing Idle.** Idle's four frames are cell 1 stretched vertically about the
  baseline by 0%, 0.4%, 0.8%, and 0.4%: a breath that moves the head a few pixels. Redrawn
  idle cells jitter (adjacent silhouettes differed 14-26% in a real sheet while looking
  identical), and a single stretched frame cannot.
- **Distinct poses, holds by repetition.** Every cell is a clearly different body
  position. Cells described as "starting to" or "almost back to" another came back as
  copies of it, and an 8-frame-per-cue sheet played as jitter. Anticipation (the wind-up)
  and impact (the strike, the deepest recoil) are held by repeating a cell, at no extra
  cost.

The Attack strike (cell 5) starts at frame 5, so set the Character's `AttackAnimDelay` to
5 x 60 ms (`0.30f`) and damage lands on the strike pose.

There is no `Cast` cue. Do not infer extra states, per-frame timing, Spine data,
transition materials, trails, audio, or merchant/rest animation from this contract.

Each runtime frame is a transparent 512x512 PNG under
`images/charui/cues/<idle|attack|hit|dead>/<00..>.png`, written in play order, so a hold or
a shared cell is the same image saved again. All twenty-four frames share:

- alpha bounds contained by `(26,26)-(486,486)` with exclusive baseline `486`;
- public `VisualNodeStyle` scale `0.80` and position `(0,-184)`;
- bounds position `(-160,-368)` and size `(320,368)`;
- intent `(0,-410)`, center `(0,-184)`, orb `(-178,-230)`, and talk `(0,-420)` anchors.

Do not tune individual frames or actions. The shared geometry is what prevents a cue from
moving the Character, intent, targeting center, orb, or dialogue UI.

## Acquisition and normalization

The source spec is `character_cues`: one paid call. It belongs to the Character's second art
batch under the normal art consent rule, after the static combat body is approved, because
that body is the anchor: pass the normalized `<ModName>/images/charui/combat.png` as
`--identity-reference`. The tool sends it as the first reference image, ahead of the
`character_combat` style samples.

The sheet must come back at 2048x2048. A real 1024x1024 sheet needed its 256 px cells
upscaled about 1.9x, measured about 0.6x the interior detail of a 2K sheet, and was rejected
in headed review as too blurry. So `generate` refuses a cue sheet under 1536 px (it keeps
the paid source for a later import), and `import` processes a small file but prints a
warning. Offer combat cues only with a route that returns 2K:

- `host-tool` in Codex: the built-in `image_gen` tool, confirmed by the maintainer to take
  the combat body as its anchor reference and return the 2048x2048 sheet. Give it
  `<ModName>/images/charui/combat.png` as the first reference image and the
  `character_combat` style samples after it, ask for a 2048x2048 square, then run
  `gen_sprite.py import --spec character_cues` on the file it reports;
- an OpenAI Images backend on `gpt-image-2` with `"exact_size": true` in its config entry;
- a Gemini 3 image model with `image_size: true`;
- a command backend whose `{resolution}` reaches the model (a real `vofy` route on
  `gemini-3.1-flash-image-preview` returned 2048x2048).

A 1K-only route (the built-in defaults `gpt-image-1.5` and `gemini-2.5-flash-image`, or a
chat gateway that sends no size) keeps the static combat body.

```powershell
python ../modmaker/scripts/gen_sprite.py generate --spec character_cues --slug cues `
  --prompt "<filled cue prompt>" --out <ModName>/images --backend <name> `
  --reference ../sts2api/reference/art-samples `
  --identity-reference <ModName>/images/charui/combat.png
python ../modmaker/scripts/gen_sprite.py import --spec character_cues --slug cues `
  --input <sheet.png> --out <ModName>/images
```

Use the fixed cue prompt in `reference/art-contract.md`. `import` takes an existing sheet (a
host-tool output, the user's file, or a kept source) without a call and no identity
reference. Either command stages the sheet at `<project>/art-sources/character-cues/sheet.png`
and replaces `images/charui/cues/` only after the whole sheet passes.

The deterministic processor owns:

- **resampling**: a sheet within 2% of the grid's aspect that does not divide into whole
  cells (Gemini returns 2:3 as 848x1264) is resampled to the exact grid size;
- **grid lines**: drawn cell-border lines and their antialiased key-tinted fringe are erased;
- **keying**: background reachable from the sheet edge is cleared when near the measured
  sheet background, near the pure key (a real sheet on pale pink drew its cell borders in
  saturated key), or a light blend of the background. Darker blends are subject: see-through
  glass painted as darkened key, or an ink rim. Enclosed background is cleared only when close to
  the measured background. Every remaining key tint is then neutralized;
- **cells**: each cell takes the largest component centered in it, wherever its pixels reach
  (models draw off the exact grid; 12 of 16 bodies in a real sheet crossed the cell bottom),
  plus detached companions such as a held item;
- **QC**: a played cell touching the sheet edge fails, and Attack/Hit body height must stay
  within `0.85..1.15` of Idle; unplayed cells take no part in QC or scaling;
- **placement**: one shared scale and horizontal offset for every frame, so frames keep
  their source positions and do not slide, with headroom for the breath; each frame's feet
  sit on the baseline.

It writes per-cue transparent GIFs, the cleaned sheet, one contact sheet, and
`pipeline-meta.json` under `<project>/art-review/character-cues/`. A failed import leaves the
existing runtime cue directory unchanged. These processing techniques are adapted from
agent-sprite-forge under its MIT license; no runtime dependency or shipped external asset is
introduced. The contact-sheet review must reject identity/costume drift, apparent-size or
camera changes, a held item that switches hands or vanishes between cells, a cell that
copies its neighbor instead of a new pose, and drawn numbers or labels (a model that writes
cell numbers leaks them into frames as companions); deterministic geometry checks do not
substitute for that visual review.

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

`TryBuild()` adds one `VisualFrameSequenceBuilder` per cue, with `Loop(true)` only for Idle
and each frame file, in order, at its cue's frame time. When the set is complete, `TryCreateCreatureVisuals()`
uses `Idle/00.png` as the initial texture and creates the shared anchored `NCreatureVisuals`.
When it is incomplete, return the existing static 512x512 `combat.png` factory result. If that
static file is also absent, return `null` so RitsuLib resumes the resolved Character profile
fallback. The incomplete route must create no cue playback node and must never play the
surviving action frames.

## Hosted proof

The `RunStart` + `CombatPlayer` harness must prove all of these in real combat:

1. every expected frame path exists at 512x512;
2. Idle advances and loops while the footprint and all five geometry/anchor values stay fixed;
3. an Attack trigger enters Attack and returns to Idle;
4. real damage enters Hit and returns to Idle;
5. leaving the first combat frees its cue playback node;
6. in a fresh combat, death reaches the last Dead frame after the contracted duration and
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
