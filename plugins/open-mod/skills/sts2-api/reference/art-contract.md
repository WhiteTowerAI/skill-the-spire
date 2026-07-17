# art-contract.md — where a custom sprite must land, and at what size

> **The art source of truth.** When a mod ships a custom sprite (a card portrait, a
> relic icon, …) the image only shows up in-game if it lands at the **exact path** the
> template's base class resolves AND is the **exact pixel size** the game expects. This
> page is the single place that records both. `tools/gen_sprite.py` reads the same
> contract; keep them in sync.
>
> **How the placeholder mechanism works (read this first).** The scaffolded card/relic/
> power bases resolve each sprite path with a `ResourceLoader.Exists(path)` check and, if
> the file is absent, **fall back to a template default** (`card.png`, `relic.png`, …).
> So "use a placeholder" = *do nothing* — the fallback fires and the mod loads on the
> default art. "Generate/import a custom sprite" = drop the correctly-named PNG at the
> path below and rebuild the `.pck`. That is the entire operation; there is no
> registration step. Verified against a scaffolded mod's
> `<ModName>Code/Extensions/StringExtensions.cs`.
> Normal events and enchantments have no scaffolded base helper. A concrete event must
> check its mod path and return the verified vanilla portrait when absent. A concrete
> enchantment must check its mod path and return `null` when absent so the original getter
> reaches `MissingIconPath`. Never return a missing custom path directly.
> A concrete orb must check its custom icon and return a matched vanilla icon when absent;
> it must also declare a vanilla Spine scene and channel-SFX fallback. The raster tool owns
> only the orb icon, never its combat scene.
> A concrete monster must check its static PNG in `CreateCustomVisuals()` and pass it to
> BaseLib's `NodeFactory<NCreatureVisuals>`; `CustomVisualPath` remains the explicit built-in
> fallback scene. Never return the PNG as a scene path.
>
> **Acquisition is source-independent.** When the current agent runtime exposes a
> callable host-native raster image tool, it may create the source PNG without a separate
> user API key (Codex calls the tool `image_gen`). Do not infer that capability from a
> text-model name or an installed skill file: the tool itself must be callable and must
> yield a local image file. Its output, Vofy output, and user/local files all enter the
> same `gen_sprite.py import` path. A host without that tool keeps the placeholder unless
> the user explicitly selects another acquisition route.
>
> **Sizes derived from MegaCrit content** (via the decompile / existing snapshots) unless
> explicitly labeled an open-mod profile — © Mega Crit. Only the *contract* (path + size)
> is distilled here; no game asset ships.

Custom keywords do not belong in the image contract below. Their presentation is localized
card text plus a BaseLib rich hover tooltip whose icon is intentionally null. The headed
`CanaryKeyword` proof covers both text consumers; do not add a keyword image, asset path, or
`gen_sprite.py` spec.

## Path root

Every path resolves under the mod's own resource root:

```
res://<ModName>/images/<sub-path>/<slug>.png
```

- `<ModName>` — the mod name (== `MainFile.ResPath`'s tail).
- `<slug>` — `Id.Entry.RemovePrefix().ToLowerInvariant()` (the same lowercased,
  prefix-stripped id used for the loc keys). A card with id `FIREBOLT-FIREBOLT` →
  slug `firebolt` → `firebolt.png`.
- The image only reaches the game **through the `.pck`**, so any art change needs a
  `.pck` rebuild (PckPacker / `build.py`) — a plain `dotnet build` of code alone won't
  pick it up. (Same rule as localization; see `build-constraints.md`.)

## The contract — the ONE card portrait (read this carefully — the folder name lies)

**A card has exactly one portrait the game actually loads, and it is 1000×760.**
Source-verified against the decompile after a live in-game run (do not re-derive):

- BaseLib Harmony-patches the game's card-texture getter to use
  `CustomCardModel.CustomPortraitPath` and nothing else. The Alchyr template maps that to
  `images/card_portraits/**big/**<slug>.png`. So **`big/<slug>.png` is the only file that
  reaches the card** — the outer `card_portraits/<slug>.png` (`PortraitPath`) is **dead
  code** under Alchyr+BaseLib; don't generate it.
- **`big/` is Alchyr's folder name, NOT a size cue.** A normal card's portrait is
  **1000×760 landscape**. The 606×852 "full art" size is **Ancient-rarity only** (a
  different card layout / UI slot — `NCard.cs` switches on `Rarity == CardRarity.Ancient`).
  **We only make normal cards, so we only ever produce 1000×760.** Putting a 606×852
  (portrait-shaped) image there feeds a vertical picture into a landscape slot → it looks
  distorted in-game (the M5.5 "违和" bug, fixed 2026-07-08).

| spec | file(s) written (under `images/`) | size | notes |
|------|-----------------------------------|------|-------|
| `card` | `card_portraits/big/<slug>.png` | **1000×760 landscape** (verified live) | **the only card portrait to make** — normal-rarity cards |
| `relic` | `relics/<slug>.png` **+** `relics/big/<slug>.png` | **256×256** (verified live) | cut-out icon; **two files** — see below. Also has `<slug>_outline.png` (optional, we skip it) |
| `power` | `powers/<slug>.png` **+** `powers/big/<slug>.png` | **256×256** (verified live) | cut-out icon; **two files** — see below. No outline file |
| `potion` | `potions/<slug>.png` | **256×256** (verified live) | cut-out icon; **ONE file** — bar/hover/use all reuse the same texture, no `big/`. Tilt ~45° right (see below) |
| `enchantment` | `enchantments/<slug>.png` | **64×64** (verified live) | cut-out icon; **ONE file** — card tab/amount and hover tooltip reuse it |
| `orb` | `orbs/<slug>.png` | **100×100** (verified live) | cut-out icon; **ONE file** — smart tooltip and trigger flash reuse it. Combat body is a separate Spine scene |
| `monster` | `monsters/<slug>.png` | **360×360** (verified live profile) | transparent static body; **ONE file** — combat and bestiary reuse it. No animation/phobia variant |
| `event` | `events/<slug>.png` | **3440×1613 wide landscape** (verified live) | opaque full-bleed initial portrait; **ONE file**. Normal/default-layout events only |

**A relic and a power each need TWO files; every other live spec needs ONE
(`gen_sprite.py` handles the count automatically).** Relic/power/potion were confirmed live
by Bauble, Smolder, and Fizz on 2026-07-08; enchantment by Guarded and the orb icon by
Shelter on 2026-07-17; the monster combat/bestiary body by Canary Sentinel on 2026-07-17.
Relic/power read the icon from two separate loose-PNG getters — writing only the first
leaves the other on the placeholder:
- **relic**: `relics/<slug>.png` = the relic-bar icon; `relics/big/<slug>.png` = the
  **detail/inspect popup** (click a relic you own). Both patched by BaseLib to the template's
  `PackedIconPath` / `BigIconPath`.
- **power**: `powers/<slug>.png` = the combat **status icon**; `powers/big/<slug>.png` = the
  big **apply/expire notification** that jumps out for a few seconds. Patched to
  `CustomPackedIconPath` / `CustomBigIconPath`.
- **potion**: `potions/<slug>.png` **only**. `PotionModel` exposes a single image texture
  (`Image` ← `PackedImagePath`); the potion bar, the hover tooltip, and the throw/use VFX all
  reuse that one texture — there is **no separate `big/` file**. (Confirmed by enumerating
  `PotionModel.cs`: its only other image getter is the outline, which self-guards with
  `Exists()` and we leave to the vanilla fallback.)
- **enchantment**: `enchantments/<slug>.png` **only**. `NCard` tabs and the card hover
  tooltip both reuse `EnchantmentModel.Icon`; there is no separate large texture.
- **orb icon**: `orbs/<slug>.png` **only**. The smart hover tooltip and `NOrb/%Flash`
  particle reuse `OrbModel.Icon`. The persistent combat body is not a second PNG; it is a
  separate Spine `PackedScene` and remains on the explicit vanilla fallback.
- **monster**: `monsters/<slug>.png` **only**. Combat `NCreature` and
  `NBestiaryLayoutDefault` both call the same `MonsterModel.CreateVisuals()` path. BaseLib
  builds a non-Spine `NCreatureVisuals` around the texture, including bounds and intent
  anchors; there is no second bestiary file.
`gen_sprite.py` writes the same normalized image to every path a spec needs, so you don't
manage them by hand. (`card`'s outer `card_portraits/<slug>.png` is dead code under BaseLib —
only `big/` is written.)

**Why these icon specs take a loose `.png` (no `.tres` authoring).** Vanilla STS2 loads every icon
family from Godot `.tres` sprite-atlases (`atlases/relic_atlas.sprites/…`, `power_atlas`,
`potion_atlas`, `relic_outline_atlas` — see `RelicModel`/`PowerModel`/`PotionModel` in the
decompile). But the icon getters accept a plain `Texture2D` path, so a loose PNG works too:
for **relic/power** the Alchyr template overrides the getters to `images/relics|powers/`
(`Exists()`-check + fallback); for **potion**, BaseLib's `CustomPotionModel` itself patches
`PotionModel.ImagePath` to `CustomPackedImagePath` (docstring: *"You may pass the path to a
png"*), so we hand-add a `PotionImagePath` helper + override that getter in the mod's potion
base (see `recipes/potion.md`). Either way a mod just drops a 256×256 PNG in — no atlas.
**This overturned an earlier belief that potion needed a `.tres` emitter** — it does not
(live-verified 2026-07-08). The only reason vanilla potions *appear* to require an atlas is
that the default (un-overridden) getter points at the atlas path, which a mod doesn't ship.
Enchantment and orb BaseLib `CustomIconPath` patches likewise accept a loose PNG directly;
their concrete classes own the existence check because the scaffold has no helper for them.

**Sizes.** All 324 vanilla relic + 271 power + 63 potion icons extracted from the game are a
uniform **256×256**; live canary runs confirmed that size + all icon paths render correctly,
so relic/power/potion are all `verified: True`. `card` is 1000×760, also live-verified
(2026-07-08). Normal enchantment icons are 64×64 and live-verified in both consumers
(2026-07-17). Normal orb icons are 100×100 and live-verified in the smart tooltip and
trigger flash (2026-07-17); this does not verify a custom combat scene. Static monsters use
an open-mod **360×360 profile**: unlike the atlas-backed icons, this is a chosen consistent
render footprint rather than an engine-mandated source size. BaseLib renders it one-to-one;
the headed combat and bestiary proof verified the resulting 396×396 bounds.

**A power subclass must extend the template base class (not `CustomPowerModel` directly).**
The template's `<ModName>Power` base is what overrides `CustomPackedIconPath` /
`CustomBigIconPath` to the loose-PNG paths. A power that inherits `CustomPowerModel`
directly leaves those null → the icon silently falls back to the default even though the
PNG exists. (Same holds for relic: extend the template `<ModName>Relic`.) See `recipes/power.md`.

**The relic outline (`<slug>_outline.png`).** A relic has a third file — the white
selection/hover outline — via its own `PackedIconOutlinePath` getter. It has a template
fallback (`relic_outline.png`), so **a missing outline does not break load and looks fine
in-game** (confirmed live — the generic default outline around a custom icon is not
jarring). `gen_sprite.py` deliberately does **not** emit it; if a mod ever wants a matching
outline it can be added later (e.g. derived from the icon's alpha). `power` has no outline.

Ancient-rarity full art (606×852) is intentionally **out of scope** — we don't make
Ancient cards.

## The enchantment icon contract

A generated enchantment owns one transparent `images/enchantments/<slug>.png`, normalized
to **64×64** with `contain` fit and chroma-key on. Its concrete class must use an
existence-checked protected `CustomIconPath`:

```csharp
public static string ModIconPath =>
    $"{MainFile.ResPath}/images/enchantments/<slug>.png";

protected override string? CustomIconPath =>
    ResourceLoader.Exists(ModIconPath) ? ModIconPath : null;
```

Use forward slashes in every `res://` URI. Returning `null` is the placeholder route:
BaseLib resumes the original `EnchantmentModel.IconPath` getter, which ultimately uses
`MissingIconPath`. Returning a missing mod path directly bypasses that fallback.

This is one shared texture, not two outputs. `NCard.UpdateEnchantmentVisuals` assigns
`EnchantmentModel.Icon` to `%Enchantment/Icon` for hand, grid, reward, and inspect-style
card nodes; `CardModel.HoverTips` adds `EnchantmentModel.HoverTips`, whose `HoverTip` uses
the same `Icon`. The 2026-07-17 `CanaryEnchantment` headed run observed the custom resource
path and 64×64 size in the real hand-card tab and hover tooltip, captured both together,
preserved the attached `Guarded` behavior (Block `0 -> 5`), and passed strict Tier 2 with
no fresh error block. Nonstandard special-case 160×150 vanilla icons do not change this
normal generated profile.

## The orb icon contract

A generated orb owns one transparent `images/orbs/<slug>.png`, normalized to **100×100**
with `contain` fit and chroma-key on. This spec is icon-only. Use a checked custom path plus
explicit matched vanilla fallbacks:

```csharp
public const string FallbackIconPath = "res://images/orbs/frost_orb.png";
public static string ModIconPath =>
    $"{MainFile.ResPath}/images/orbs/<slug>.png";
public static string FallbackSpritePath =>
    SceneHelper.GetScenePath("orbs/orb_visuals/frost_orb");

public override string? CustomIconPath =>
    ResourceLoader.Exists(ModIconPath) ? ModIconPath : FallbackIconPath;
public override string? CustomSpritePath => FallbackSpritePath;
public override string? CustomChannelSfx =>
    "event:/sfx/characters/defect/defect_frost_channel";
```

`OrbModel.Icon` feeds both the smart `HoverTip(orb, ...)` and the `CpuParticles2D` at
`NOrb/%Flash`. The 2026-07-17 `CanaryOrb` headed run observed the same custom resource path
and 100×100 size in both nodes, triggered the particle, captured the real orb and tooltip
together, preserved passive/evoke Block `0 -> 2 -> 7`, and passed strict Tier 2 with no
fresh error block.

The combat body remains explicitly separate. `NOrb` calls `CreateSprite()`, gets child
`SpineSkeleton`, and starts `idle_loop`. `gen_sprite.py --spec orb` does not emit a scene,
atlas, skeleton, animation, or audio. The canary proved the Frost scene fallback was present
and valid, not that the custom icon became the body. Leaving `CustomSpritePath` null probes
a missing custom-id scene; leaving `CustomChannelSfx` empty probes a missing
`debug_audio/<custom-id>_channel.mp3`. Keep both fallbacks; a custom Spine body belongs to
the later animation expansion and does not block M6 or M7.

## The static monster-body contract

A generated monster owns one transparent `images/monsters/<slug>.png`, normalized to
**360×360** with `contain` fit and chroma-key on. Draw one full creature in a neutral
combat-ready pose, feet on a clear shared baseline, with the silhouette filling roughly
85-90% of the frame. Do not add ground, cast shadow, scenery, text, particles, or effects
that imply a one-time attack; the same still image remains visible for every move.

`CustomVisualPath` is a scene seam, not the loose-PNG seam. Wire the static body through
the public BaseLib resource factory and retain an explicit checked fallback:

```csharp
using BaseLib.Utils.NodeFactories;
using Godot;
using MegaCrit.Sts2.Core.Nodes.Combat;

public static string FallbackVisualPath =>
    SceneHelper.GetScenePath("creature_visuals/fallback");
public static string ModVisualPath =>
    $"{MainFile.ResPath}/images/monsters/<slug>.png";

public override string CustomVisualPath => FallbackVisualPath;
public override bool HasDeathSfx => false;

public override NCreatureVisuals? CreateCustomVisuals()
    => ResourceLoader.Exists(ModVisualPath)
        ? NodeFactory<NCreatureVisuals>.CreateFromResource(ModVisualPath)
        : null;
```

When present, `NCreatureVisualsFactory` creates a foot-aligned `Sprite2D`, expands the
360×360 texture to 396×396 bounds, and generates `%CenterPos` plus `IntentPos` at
`(0,-466)`. `NCreature` sees no `SpineBody`, skips animator creation, and keeps its normal
hitbox/intent/fade lifecycle. When absent, `CreateCustomVisuals()` returns `null`; the
original scene loader resumes at `FallbackVisualPath` without first logging a missing
custom-id scene. `HasDeathSfx => false` avoids the default nonexistent custom-id death
audio event while the non-Spine death fade remains available.

Combat and bestiary are independent visible consumers of the same getter. The 2026-07-17
`CanaryMonsterVocabulary` headed run asserted the same custom resource path, 360×360 size,
non-Spine body, 396×396 bounds, and intent position in the real combat `NCreature` and a
real `NBestiary` default layout; it captured both and passed strict Tier 2 with no fresh
error block. The combat screenshot showed correct floor/health-bar alignment and an
unobscured intent; the bestiary screenshot showed the title, move list, and uncropped body.

This does not support attack/hurt/death/cast animation, Spine skeleton/atlas data, animated
bestiary move previews, or a separate phobia body. Those are later animation/variant
extensions. In the supported profile animation triggers safely no-op, death fades the still
body, and phobia mode retains the same texture.

## The normal-event portrait contract

A pipeline-supported normal event has exactly one generated art asset: its initial
portrait at `images/events/<slug>.png`, normalized to **3440×1613** with opaque `cover`
fit and chroma-key off. Eleven current normal/phobia portrait samples in the pinned game
pack use that logical size. The 2026-07-17 `CanaryEvent` headed run then proved the mod
path in the real `MapNode` host: `%Portrait.Texture.ResourcePath` was
`res://CanaryEvent/images/events/gilded_signpost.png`, its logical size was 3440×1613,
the option UI rendered over the custom image, the option changed Gold by 25, and strict
Tier 2 passed with no fresh error block.

Unlike card/relic template bases, `CustomEventModel.CustomInitialPortraitPath` does not
check whether the returned path exists. Use an explicit fallback in every generated event:

```csharp
public const string FallbackPortraitPath = "res://images/events/this_or_that.png";

public static string ModPortraitPath =>
    $"{MainFile.ResPath}/images/events/<slug>.png";

public override string? CustomInitialPortraitPath =>
    ResourceLoader.Exists(ModPortraitPath) ? ModPortraitPath : FallbackPortraitPath;
```

The one-file claim is deliberately narrow:

- the optional phobia portrait is a separate inferred `<full-id>_phobia_mode.png` path;
- a later page may replace the portrait through `NEventRoom.SetPortrait`;
- portrait-anchored VFX use a separate scene;
- custom-layout and Ancient events own scene/background contracts.

Those consumers remain deferred. Do not generate extra files for them or describe the
normal initial-portrait proof as event scene/VFX support.

## Making a generated portrait actually match STS2 (read before writing the prompt)

A general image model does **not** know Slay the Spire 2 — the words "Slay the Spire 2
style" are near-noise to it (it's a niche game). Getting a usable, non-jarring portrait
needs the style supplied explicitly. Two layers, use both when possible:

**Layer 1 — the style descriptor (always, text-only, zero dependencies).** Prepend this
fixed descriptor to every card-portrait prompt. It encodes STS2's actual card art
language (distilled from the game's own portraits):

```
Original splash art for a deck-building card game. If reference images are provided,
treat them as STYLE REFERENCE ONLY — match their art style, rendering technique,
palette logic, and energy precisely, but do NOT reuse their objects, characters, or
layout; invent a new subject.

Flat 2D vector game illustration: bold simplified shapes, hard-edged cel shading with
about two flat tones per surface, thin clean dark outlines on key objects, high color
saturation, high contrast. One dramatic action moment frozen mid-motion, the focal
subject centered in the frame. A bright warm glowing rim light hugs the subject's
silhouette; energy glow flares orange-to-yellow. Background is a radial burst of color
radiating out from the point of action, over a darker cool backdrop with large soft
paint-splatter silhouettes. Palette by role: cool desaturated background (teal / deep
purple / dark red), a warmer, more saturated subject that pops. The composition must
read clearly even at small card-art size.

NOT photorealistic, NOT a 3D render, NOT pixel art. No text, letters, numbers, logos,
border, card frame, UI, or watermark.
```

**Layer 2 — few-shot reference images (when the acquisition route supports them, much
stronger).**
Pass `--reference <sts2-api>/reference/art-samples` to either acquisition tool — always the
**root** samples dir, not a subdir. It contains `card/` (18 portraits), `relic/` (6 icons),
`power/` (6 icons), `potion/` (6 icons), `enchantment/` (20 normal 64x64 icons), `orb/`
(5 non-empty icons), and `monster/` (the Axebot, Ceremonial Beast, and Crossbow Ruby Raider
renders). The tool **auto-selects the subdir matching `--spec`** and randomly samples three
distinct images when the pool is larger. Monster's fixed three are always all supplied.
Never mix families merely to fill the reference list; their visual languages differ.

The Images transport sends the selected files as multipart `image[]` inputs to
`/images/edits`; Chat transports inline them as image data URLs; Vofy receives repeated
`--image` arguments. This needs a model that accepts image inputs. For a host-native tool,
randomly choose up to three files from the matching spec directory, make them visible
through the runtime's normal local-image mechanism, and label each one STYLE REFERENCE
ONLY. If the route cannot consume local references, use the type-specific text prompt
alone. (All © Mega Crit, reference-only — see `art-samples/ATTRIBUTION.md`.)

Only `event` lacks a bundled reference-image set in the current static pipeline. It remains
text-template-only until a type-matched pool is grounded. If any reference set is removed,
the corresponding detailed text template remains the fallback.

## The card portrait prompt template — three segments

The final prompt is **three segments concatenated**. Only the middle one is written per
card; the outer two are fixed guardrails, so style stays consistent and `gen_sprite.py`
can always fit/place the result:

```
[① fixed style prefix]   ← the Layer-1 STS2 style descriptor above (verbatim)
[② generated subject]    ← the ONE thing that differs per card (see below)
[③ fixed structural/negative constraints]:
   A single {subject}, centered in frame, full subject visible with generous margin,
   dynamic 3/4 composition, landscape ~4:3.
   No text, no border, no card frame, no UI, no watermark.
   NOT photorealistic, NOT 3D render, NOT pixel art.
```

**Segment ② is a TRANSLATION of the NAME, not a rephrase of the mechanics.** A card's
SPEC is mechanical ("deal 8 damage, gain 2 block") — that has *no picture*, and painting
the numbers (two drops of blood for "lose 2 HP") makes the art literal and awkward. Do
NOT put damage numbers or keyword mechanics into the prompt. Anchor the picture on the
card's **name** (its flavor is a secondary seed): decide *what one thing the name shows*,
then describe that one thing vividly.

Write ② as **two-to-four sentences describing a single dramatic moment**, not a keyword
list. Name the focal subject and where it sits (centered, dominating the frame), the one
action it's frozen mid-motion in, and the light on it (a warm rim light hugging its
silhouette, an energy glow). Keep it concrete and heroic; one clear subject beats a busy
scene. Example shape (subject only — ①③ wrap it):

> *A blazing arrow of living fire dominates the center of the frame, loosed and
> streaking diagonally toward the upper right, frozen mid-flight. Trailing embers and a
> ribbon of flame stream behind it; a bright orange-to-yellow rim light traces its
> edge against the dark. Stylized and heroic.*  ← for a card named **"Firebolt"**

Quick seeds (each is *what the name depicts*, mechanics ignored):

- "Firebolt" → *a blazing arrow of fire streaking forward, mid-flight*
- "Gambler's Coin" → *a golden coin spinning in mid-air, motion trail*
- "Blood Temper" → *an armored fist clenched, a warm power-flare rising from it* — the
  name's theme (pain → strength), NOT "two drops of blood" for "lose 2 HP".

If a card's name is too abstract to picture, pick the closest concrete object or action
its theme implies.

Rules that make the output usable (they mirror the fit logic in `gen_sprite.py`):

- **No text / border / UI** — the game draws the card frame; the portrait is art only.
- **Full-bleed illustration, not a cut-out object.** A card portrait *fills* the frame
  window (`fit: cover`, opaque) — a scene, not an object on transparency. So `card`
  defaults to **chroma-key OFF** (no magenta background needed). The `#FF00FF`
  magenta trick is for the cut-out specs (`relic` / `power` / `potion` / `enchantment` / `orb` / `monster`,
  `fit: contain`, chroma ON) that sit transparent on game UI — for those, add "solid flat
  magenta (#FF00FF) background, no gradient" to the prompt. Force keying on a card with
  `--chroma` only if you deliberately want to cut a magenta-backed portrait out.
- **Subject centered, generous margin**, so the `cover` crop keeps the subject in frame.
- **One image per call.** `gen_sprite.py` requests `n=1` and keeps that single result —
  there is no batch-and-pick. If it's not right, *regenerate*: tweak segment ② and re-run
  (the regenerate loop below). One at a time, judged by eye.

**Cut-out subject shape (relic / power / potion / enchantment / orb / monster).** These are a single isolated subject,
not a scene. Name one object, center it, put it on flat magenta. Spec-specific art
direction, distilled from the vanilla references:

- **Scale — make the object BIG.** Unlike a card portrait (which wants a generous margin so
  the `cover` crop stays safe), an icon should nearly fill its frame. `gen_sprite.py` crops
  to the subject's bounding box and scales it up (`fit: contain`, `fill=1.0`), so the *only*
  thing that makes a relic look small in-game is the model drawing it small on a big empty
  background (that empty space either survives as padding, or a soft/gradient background
  defeats the chroma-key and gets counted into the bbox). Fight this in the prompt: say the
  object is **large and fills ~90% of the frame, tightly framed, matching the scale and
  framing of the reference images** (the references define proportion, not just style), and
  demand a **solid flat pure #FF00FF magenta background — no gradient, no shadow, no vignette**
  so the cut-out is clean. If a generated icon still reads small, this scale/tight-framing
  line in segment ② is the first thing to strengthen (then regenerate).
- **potion** — draw the bottle **tilted ~45° leaning to the right** (shown diagonally).
  That is how STS2 displays potions; only some big square-ish potions stand upright. We
  tilt *all* generated potions right for consistency (a deliberate, accepted simplification —
  no upright/tilt branching). Pick the bottle silhouette + liquid colour from the potion's
  name/effect (a red fizzing flask for a damage potion, a blue calm vial for block, …).
- **relic / power** — a single emblem/object centered upright; match the material and
  symbol language of the `relic/` / `power/` references.
- **enchantment** — use the dedicated micro-emblem template below. It is much flatter and
  simpler than a relic/power icon because it must survive at 64x64.
- **orb icon** — use the dedicated elemental-core template below. It owns painted material
  and contained glow, not a generic flat glyph and not the combat body.
- **monster** - one complete creature in a neutral combat-ready pose, seen from a readable
  front or 3/4 angle. Keep both feet on one baseline and the entire silhouette inside the
  frame; fill about 85-90%. No floor, cast shadow, background prop, attack streak, spell
  burst, or other animation-like moment. This one still serves combat and bestiary.

## The enchantment prompt template

An enchantment is a tiny symbolic tab icon, not a miniature card illustration and not a
relic object. The normal references use bold, slightly irregular silhouettes, broad matte
color fills, and extremely sparse interior marks. They range from an abstract cyan flame
glyph to a peach organic blob, but remain readable at 64x64 because they avoid fine linework.

```
[① fixed enchantment style]:
   Original micro-emblem for a deck-building card game's enchantment tab. Match the
   reference images' hand-painted flat icon language: one bold asymmetric silhouette,
   broad opaque color shapes, one dominant hue with only one or two lighter/darker tones,
   subtly organic edges, and at most a few chunky interior cutouts or highlights. No
   glossy 3D volume, dense texture, thin filigree, generic app-icon polish, badge, ring,
   frame, or backing plate.
[② generated emblem]:
   One or two concrete sentences translating the enchantment name/effect into one symbol.
[③ fixed enchantment composition/negative constraints]:
   One compact upright emblem, centered, filling about 85-90% of a square and recognizable
   at 64x64. Perfectly flat solid #FF00FF background with no gradient, texture, or shadow.
   No scene, character, text, letters, numbers, UI, border, watermark, particles, or aura
   extending beyond the emblem. Do not use magenta inside the emblem.
```

## The orb-icon prompt template

An orb icon is a compact elemental core. The original Dark Orb uses concentric painted
shells, deep internal occlusion, violet reflections, and tiny highlights; Frost is an
irregular cluster of broad cyan ice facets with sharp white glints. The shared language is
a large near-circular elemental mass, layered material shapes, and contained light — not a
flat logo, generic glass marble, UI badge, or the persistent combat scene.

```
[① fixed orb-icon style]:
   Original elemental-orb icon for a deck-building combat game. Match the reference
   images' compact hand-painted material rendering: chunky layered forms, an irregular
   near-circular silhouette, saturated element-specific colors, three-to-five broad value
   groups, dark internal occlusion, selective crisp highlights, and a small amount of
   contained inner glow or speck detail. Preserve readable material identity such as ice
   facets, plasma bands, lightning arcs, or a dark reflective shell. No photoreal glass,
   smooth 3D sphere render, generic vector logo, UI badge, or ornamental backing frame.
[② generated elemental core]:
   Two-to-four concrete sentences translating the orb name/passive/evoke theme into one
   material or energy core; do not depict gameplay numbers.
[③ fixed orb-icon composition/negative constraints]:
   One compact elemental core, centered, filling about 88-94% of a square, readable at
   100x100 and as a small trigger flash. Perfectly flat solid #FF00FF background with no
   gradient, texture, floor, or shadow. No environment, character, text, UI, border,
   watermark, detached particles, or energy extending to the canvas edge. Do not use
   magenta inside the orb.
```

## The static monster prompt template

A static monster is a full-body cut-out, not the card template's frozen action moment and
not an environment. The three fixed references show the actual normal-monster rendering
range: softly modeled digital paint, simplified stylized anatomy, material-specific brush
texture, restrained base colors with focused bright accents, and selective edges rather
than uniform black linework. Do not reuse the card prompt's hard cel-shading, warm rim-light,
or radial-burst language.

```
[① fixed monster style]:
   Original full-body enemy render for a deck-building combat game. Match the reference
   images' softly hand-painted 2D character art: broad readable value groups, gently
   modeled volume, visible but controlled digital brush texture, simplified stylized
   anatomy and proportions, material-specific shading, and soft-to-hard edge variation.
   Use little or no uniform outline; define the silhouette through value and color. Favor
   a restrained, slightly muted base palette with one or two focused saturated accents or
   emissive details. It may feel dimensional, but must remain painterly — not a glossy 3D,
   PBR, photoreal, anime, vector, or hard cel-shaded render. Reference images are STYLE
   ONLY: do not copy their axes, antlers, crossbow, clothing, anatomy, or silhouette.
[② generated creature]:
   Two-to-four concrete sentences translating the monster's name/concept into one original
   creature, including its dominant shape language, materials, palette, and focal accent.
[③ fixed monster composition/negative constraints]:
   One complete creature in a neutral combat-ready pose, front or 3/4 view.
   Both feet on one shared baseline; full silhouette visible; fill 85-90% of a square.
   Perfectly flat solid #FF00FF background with no gradient, texture, or shadow.
   No floor, scenery, text, UI, watermark, attack streak, spell burst, or particles.
   No cropped limbs, cast shadow, contact shadow, reflection, or magenta in the creature.
```

Do not include a transient move effect. The same still image is used for idle, every move,
combat damage, death fade, and the bestiary entry until the later animation expansion.

## The event portrait prompt template

An event portrait is a very wide room illustration behind live UI, not a centered card
portrait. Derive its subject from the event's title and opening situation, not from the
numeric option rewards. Use the general flat 2D/cel-shaded style language above, but
replace the card composition paragraph with this fixed event structure:

```
[① fixed event style]:
   Original wide environment illustration for a deck-building game's event room.
   Flat 2D shapes, hard-edged cel shading, clean dark outlines, cool atmospheric
   background, and one clearly readable focal situation.
[② generated situation]:
   Two-to-four sentences showing the event title/opening as one concrete moment.
[③ fixed event composition/negative constraints]:
   Very wide ~2.13:1 landscape. Place the focal subject in the left third.
   Keep the center-right and lower-right darker, lower-detail, and low-contrast so the
   game's title, description, and option buttons remain readable. Full-bleed opaque scene.
   No text, letters, numbers, logos, border, UI, card frame, or watermark.
   NOT photorealistic, NOT a 3D render, NOT pixel art.
```

Do not reuse the card prompt's "subject centered" constraint for events. Request the
widest supported landscape ratio from the selected backend after checking its live model
guide; `gen_sprite.py` owns the final 3440×1613 crop and placement.

## Consent and the regenerate loop

For a host-native tool, the mod-level `generate` choice authorizes the initial one-image-
per-asset run without a separate API key. Follow any approval or usage warning presented by
the host and do not claim that host usage is free. For a paid API or managed-credit CLI,
**before every paid generation, disclose the model/backend, output count (one), and credit-
spending action. Use the assembled prompt** (segments ①②③ concatenated) and the subject
you derived, and get a quick yes — one line, e.g. *"I'll generate the portrait with this
prompt: … — go ahead?"* Do not silently spend or treat an earlier custom-art preference as
approval for an external route. Every regeneration, including a native-tool regeneration,
needs a new confirmation after the user sees the current result. This is also where the §7.1
"regenerate/tweak this sprite" loop
lives:

```
derive subject (②) → assemble ①②③ → show user → generate → user looks at result
   → happy: keep it, continue to build
   → not happy: adjust ② (or the subject), re-run gen_sprite.py, look again
```

Only segment ② changes on a regenerate; ①③ and the few-shot references stay fixed.
Adjusting a prompt is far cheaper than editing code, so this loop is the natural place to
iterate. For a multi-card mod, segments ①③ + the references are shared across all cards,
so cross-card style stays consistent even though each card's ② differs.

## Reference-driven generation acceptance

On 2026-07-17, `seedream-5.0-lite` generated one approved `1:1`/`2K` preview for each new
reference-backed family: Emberbound enchantment, Verdant Pulse orb, and Cinder Pilgrim
monster. Each request used three type-matched real-game images. Headed visual inspection
confirmed the dedicated styles remained distinct: a compact flat enchantment emblem, a
layered painted orb core, and a softly modeled full-body monster with no borrowed reference
objects. All normalized outputs had the exact target size, RGBA mode, and transparent
corners.

The orb source also provided a useful negative case: the model textured its requested
magenta background with dark fragments. Color keying alone kept those fragments and shrank
the orb. The bounded M6 cut-out cleanup now retains the centered subject cluster, removes
disconnected debris, and performs the final `contain` fit; the already-paid source then
passed locally without regeneration. This acceptance proves reference delivery, prompt
shaping, and deterministic normalization. It does not replace the existing headed
combat/tooltip/bestiary consumer proofs.

## Using the tool

```
# host-native image generation is an agent tool call, not a shell command. Use it only
# when the current runtime actually exposes it. Codex: built-in image_gen mode, one call
# per asset, no OPENAI_API_KEY. Then normalize the host-reported local source file:
python ${CLAUDE_PLUGIN_ROOT}/tools/gen_sprite.py import \
  --spec card --slug firebolt --input "<native-output.png>" \
  --out "<mod>/<ModName>/images"

# For relic/power/potion/enchantment/orb/monster native sources, use the same import command with --chroma.
# Keep the raw source on a perfectly flat #FF00FF background until this import step.
# For a normal event use --spec event with no --chroma; it writes events/<slug>.png.

# managed credits — Vofy is acquisition only. The user installs/logs in themselves;
# preflight prints no account/credit details. Inspect live model capabilities separately:
python ${CLAUDE_PLUGIN_ROOT}/tools/acquire_sprite.py preflight --model <chosen-model>
vofy models <chosen-model>

# after explicit approval for this prompt/model/one-image spend. Add the root --reference
# once when the live model guide supports image inputs; the tool selects the spec and 3 files:
python ${CLAUDE_PLUGIN_ROOT}/tools/acquire_sprite.py create \
  --spec card --slug firebolt --prompt "<the filled template above>" \
  --out <mod>/<ModName>/images --model <chosen-model> \
  --aspect-ratio <confirmed-ratio> \
  [--reference ${CLAUDE_PLUGIN_ROOT}/skills/sts2-api/reference/art-samples] --yes

# generate (BYO backend) — POSTs the prompt (+ few-shot STS2 style references when the
# backend supports them), then fits + resizes to the contract size + places it:
python ${CLAUDE_PLUGIN_ROOT}/tools/gen_sprite.py generate \
  --spec card --slug firebolt --prompt "<the filled template above>" \
  --out <mod>/<ModName>/images --config <path to art-backend.json> \
  --reference ${CLAUDE_PLUGIN_ROOT}/skills/sts2-api/reference/art-samples

# import (local file) — same normalize + place, no HTTP:
python ${CLAUDE_PLUGIN_ROOT}/tools/gen_sprite.py import \
  --spec card --slug firebolt --input ./my-art.png --out <mod>/<ModName>/images

# list the contract (script's view — should match the table above):
python ${CLAUDE_PLUGIN_ROOT}/tools/gen_sprite.py list-specs
```

The host-native route must follow the runtime's installed image-generation instructions.
For Codex, use the built-in `image_gen` tool rather than the image skill's CLI/API fallback;
that fallback requires `OPENAI_API_KEY` and belongs under the explicit BYO route. Inspect
the native output before importing it. Use the actual local path returned by the host
(Codex normally stores built-in output under `$CODEX_HOME/generated_images/`); if the host
returns no local file, the route is unavailable and the placeholder remains. Do not run a
  second background-removal helper for cut-out sources: `gen_sprite.py import --chroma` owns the
keying, fit, resize, and final STS2 placement.

`acquire_sprite.py` never installs Vofy, runs `vofy login`, reads credentials, records
status/credit output, or parses Vofy's normal stdout for a result filename. It runs one
synchronous `vofy image create --yes --n 1` into a unique empty temporary directory,
requires exactly one downloaded image, and invokes `gen_sprite.py import` for the real
crop/fit/chroma/path contract. For relic/power/potion/enchantment/orb/monster it supplies import's
`--chroma` automatically; event remains opaque. It prints the selected reference filenames
so the random few-shot choice is auditable without exposing account data. For enchantment,
orb, and monster, normalization also keeps the centered subject cluster and removes
disconnected dark/chroma debris before the final `contain` fit; this is bounded to the new
profiles and does not alter the earlier M5.5 specs. Before crossing a Windows/npm `.cmd` shim it folds all prompt whitespace
to one line, preserving every sentence; an empty/whitespace-only prompt stops before any
CLI call. A missing CLI/auth/account, model lookup failure, task failure/timeout, or
zero/multiple downloads exits nonzero. Do not automatically resubmit after a timeout or
ambiguous result; inspect `vofy tasks --plain` first because the task may already be paid.
Offer BYO HTTP, local import, or placeholder instead, with no silent second paid route.

Backend config (`art-backend.json`, **never committed — holds a key**) is
provider-agnostic. There are **two transport shapes**, chosen by `mode` — because image
models split into two API families and BYO means the config, not the code, says which:

```json
// mode "images" (default) — OpenAI *Images* API: /images/generations (+ /images/edits
// for references). Used by OpenAI gpt-image-1 and gateways exposing that endpoint.
{ "base_url": "https://api.example.com/v1", "api_key": "sk-...", "model": "gpt-image-1" }
```

```json
// mode "chat" — OpenAI *Chat Completions* API returning an image in the reply. Used by
// Poe, Gemini-native, OpenRouter, and most "one key, many models" gateways.
{ "mode": "chat",
  "base_url": "https://api.poe.com/v1", "api_key": "...", "model": "GPT-Image-1.5" }
```

In `chat` mode, references (few-shot style images) are inlined into the user message as
`image_url` data URLs, and the tool parses the generated image back out of the reply
(structured image array, inline base64 data URL, or an image link — in that order).
Optional keys: `chat_url` (override the endpoint), `chat_extra` (merge extra JSON into
the request body, e.g. a provider's `modalities` knob), `request_size`, `timeout`.

We bundle or default to **no** provider — the user points this at whatever endpoint
(cloud or local) they want (PROJECT.md §7.1: BYO backend). A missing/invalid config makes
`generate` fail with a clear message and a non-zero exit, and the caller falls back to the
placeholder.
