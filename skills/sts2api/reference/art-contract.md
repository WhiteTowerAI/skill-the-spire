# art-contract.md — where a custom sprite must land, and at what size

> **The art source of truth.** When a mod ships a custom sprite (a card portrait, a
> relic icon, …) the image only shows up in-game if it lands at the **exact path** the
> template's base class resolves AND is the **exact pixel size** the game expects.
>
> The exact values live in code: `gen_sprite.py`'s `SPECS` and `character_art.py`'s
> `CHARACTER_ART_BUNDLE`. They are projected into
> `reference/catalogs/art-contract-sts2-0.107.1.json` by
> `python ../modmaker/scripts/gen_sprite.py export-contract`, so you can read every path,
> size, fit, chroma, and fallback as data instead of executing anything. Query that catalog
> when you need a value the tables below do not spell out.
>
> The tables on this page are a readable view of that same contract, not a second
> definition. `test_art_contract_catalog.py` asserts every size here equals the catalog's
> and that every spec in the catalog has a row, so the two cannot drift apart. Do not
> hand-edit the catalog, and do not re-derive a size by eye.
>
> **How the placeholder mechanism works (read this first).** A RitsuLib content template
> shows custom art only through its explicit asset profile: `CardAssetProfile`,
> `RelicAssetProfile`, `PotionAssetProfile`, `PowerAssetProfile`, and so on. RitsuLib checks
> each profile path and keeps the template or base-game fallback when the file is absent or
> the profile field is empty. So "use a placeholder" = *omit the profile override*. "Generate/
> import a custom sprite" = write the correctly-named PNG at the path below, **and** point the
> model's profile at that same `res://<ModName>/…` path (the surface recipe shows the
> override), then rebuild the `.pck`. A PNG that no profile names never reaches the game.
> Normal events and enchantments have no scaffolded base helper. A concrete event must
> check its mod path and return the verified vanilla portrait when absent. A concrete
> enchantment must check its mod path and return `null` when absent so the original getter
> reaches `MissingIconPath`. Never return a missing custom path directly.
> A concrete orb must check its custom icon and return a matched vanilla icon when absent;
> it must also declare a vanilla Spine scene and channel-SFX fallback. The raster tool owns
> only the orb icon, never its combat scene.
> A concrete monster must check its static PNG in `TryCreateCreatureVisuals()` and pass its
> texture to RitsuLib's `RitsuGodotNodeFactories`; `MonsterAssetProfile` retains the explicit
> built-in fallback scene. Never put the PNG in the profile's scene path.
> A new Ancient must set every `EventAssetProfile` and `AncientEventPresentationAssetProfile`
> field explicitly: empty fields derive missing paths from its own id. The checked placeholder
> borrows Darv's background scene and map/run-history icons (`recipes/ancient.md`
> § Required explicit fallback). No `gen_sprite.py` spec produces Ancient art.
> A concrete Rest Site option must resolve an absent custom icon to
> `res://images/ui/rest_site/option_heal.png` before constructing
> `RestSiteOptionAssetProfile`. The vanilla path derived from a custom `OptionId` is not a
> usable fallback.
> A generated Character explicitly selects the base-game Ironclad placeholder profile. Its
> missing Energy resources resolve to `ironclad_energy_counter.tscn`,
> `EnergyIconHelper.GetPath("ironclad")` (`energy_ironclad.tres`), and
> `res://images/packed/sprite_fonts/ironclad_energy_icon.png`; they are never derived from a
> theme palette name such as `red`.
>
> **Acquisition is source-independent.** When the current agent runtime exposes a
> callable raster image tool of its own (`host-tool`), it may create the source PNG without a separate
> user API key (Codex calls the tool `image_gen`). Do not infer that capability from a
> text-model name or an installed skill file: the tool itself must be callable and must
> yield a local image file. Its output, a user-configured backend's output, and user/local
> files all enter the same normalization path. A host without that tool keeps the placeholder unless
> the user explicitly selects another acquisition route.
>
> **Sizes derived from MegaCrit content** (via the decompile / existing snapshots) unless
> explicitly labeled an skill-the-spire profile — © Mega Crit. Only the *contract* (path + size)
> is distilled here; no game asset ships.

Custom keywords do not belong in the image contract below. Their presentation is localized
card text plus a RitsuLib/native hover tooltip whose icon is intentionally null. The headed
keyword proof covers both text consumers; do not add a keyword image, asset path, or
`gen_sprite.py` spec.

## Path root

Every path resolves under the mod's own resource root:

```
res://<ModName>/images/<sub-path>/<slug>.png
```

- `<ModName>` — the Mod name; `build.py` packs `<project>/<ModName>/` under exactly this
  `res://<ModName>/` prefix.
- `<slug>` — the element's lowercase snake-case logical id from SPEC, for example
  `quick_jab` for the Card class `QuickJab` → `quick_jab.png`. RitsuLib does not derive it:
  write the same literal path in the PNG location and in the model's asset profile.
- The image only reaches the game **through the `.pck`**, so any art change needs a
  `.pck` rebuild (PckPacker / `build.py`) — a plain `dotnet build` of code alone won't
  pick it up. (Same rule as localization; see `../modmaker/build.md`.)

## The contract — the ONE card portrait (read this carefully — the folder name lies)

**A card has exactly one portrait the game actually loads, and it is 1000×760.**
Source-verified against the decompile after a live in-game run (do not re-derive):

- RitsuLib's `CardAssetProfile.PortraitPath` resolves the card texture path.
  `images/card_portraits/<slug>.png`; omit the profile to retain the checked placeholder
  fallback. A normal card's portrait is
  **1000×760 landscape**. The 606×852 "full art" size is **Ancient-rarity only** (a
  different card layout / UI slot — `NCard.cs` switches on `Rarity == CardRarity.Ancient`).
  **We only make normal cards, so we only ever produce 1000×760.** Putting a 606×852
  (portrait-shaped) image there feeds a vertical picture into a landscape slot → it looks
  distorted in-game.

| spec | file(s) written (under `images/`) | size | notes |
|------|-----------------------------------|------|-------|
| `card` | `card_portraits/<slug>.png` | **1000×760 landscape** (profile contract) | **the only card portrait to make** — normal-rarity cards |
| `relic` | `relics/<slug>.png` **+** `relics/<slug>_outline.png` **+** `relics/big/<slug>.png` | **256×256** | cut-out main/big icons plus deterministic outline; all three paths verified live |
| `power` | `powers/<slug>.png` **+** `powers/big/<slug>.png` | **256×256** (verified live) | cut-out icon; **two files** — see below. No outline file |
| `potion` | `potions/<slug>.png` | **256×256** (verified live) | cut-out icon; **ONE file** — bar/hover/use all reuse the same texture, no `big/`. Tilt ~45° right (see below) |
| `enchantment` | `enchantments/<slug>.png` | **64×64** (verified live) | cut-out icon; **ONE file** — card tab/amount and hover tooltip reuse it |
| `orb` | `orbs/<slug>.png` | **100×100** (verified live) | cut-out icon; **ONE file** — smart tooltip and trigger flash reuse it. Combat body is a separate Spine scene |
| `monster` | `monsters/<slug>.png` | **360×360** (verified live profile) | transparent static body; **ONE file** — combat and bestiary reuse it. No animation/phobia variant |
| `event` | `events/<slot-slug>.png` | **3440×1613 wide landscape** (verified live) | opaque full-bleed portrait; one file per initial/page slot. Normal/default-layout events only |
| `rest_site_option` | `rest_site_options/<slug>.png` | **256x169** (verified live) | opaque native-button image; one file; checked custom framing and native Heal fallback |

**A relic and a power each need TWO files; every other invocation writes ONE
(`gen_sprite.py` handles the count automatically). An event may invoke the same spec once
per selected portrait slot.**
Relic/power read the icon from two separate loose-PNG getters — writing only the first
leaves the other on the placeholder:
- **relic**: `relics/<slug>.png` = the relic-bar icon; `relics/big/<slug>.png` = the
  **detail/inspect popup** (click a relic you own). Both are selected by the
  `RelicAssetProfile` paths.
- **power**: `powers/<slug>.png` = the combat **status icon**; `powers/big/<slug>.png` = the
  big **apply/expire notification** that jumps out for a few seconds. Patched to
  `PowerAssetProfile` paths.
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
  `NBestiaryLayoutDefault` both call the same `MonsterModel.CreateVisuals()` path. RitsuLib
  builds a non-Spine `NCreatureVisuals` around the texture, including bounds and intent
  anchors; there is no second bestiary file.
- **event portrait**: `events/<slot-slug>.png` **only** for each selected slot. The initial
  slot is resolved by `EventAssetProfile.InitialPortraitPath`; authored page slots are loaded and
  passed to `NEventRoom.SetPortrait` by the event option method.
- **Rest Site option**: `rest_site_options/<slug>.png` **only**. Two local
  pinned-version product consumers independently use an opaque 256x169 canvas. RitsuLib's
  `RestSiteOptionAssetProfile.IconPath` feeds the real native button. The focused
  hosted headed run confirmed the custom framing and missing-art Heal fallback.
`gen_sprite.py` writes the same normalized image to every path a spec needs, so you don't
manage them by hand. The RitsuLib Card profile uses the single
`card_portraits/<slug>.png` path.

**Why these icon specs take a loose `.png` (no `.tres` authoring).** Vanilla STS2 loads every icon
family from Godot `.tres` sprite-atlases (`atlases/relic_atlas.sprites/…`, `power_atlas`,
`potion_atlas`, `relic_outline_atlas` — see `RelicModel`/`PowerModel`/`PotionModel` in the
decompile). But the icon getters accept a plain `Texture2D` path, so a loose PNG works too:
for **relic/power/potion**, RitsuLib's asset profiles accept explicit loose PNG paths with
an existence-checked fallback. Either way a mod just drops a 256×256 PNG in — no atlas.
A potion needs no `.tres` emitter. The only reason vanilla potions *appear* to require an atlas is
that the default (un-overridden) getter points at the atlas path, which a mod doesn't ship.
Enchantment and Orb profiles likewise accept a loose PNG directly; omit the profile to keep
the checked fallback.

**Sizes.** All 324 vanilla relic + 271 power + 63 potion icons extracted from the game are a
uniform **256×256**. A normal card portrait is 1000×760, a normal enchantment icon 64×64, and
a normal orb icon 100×100; the orb size does not cover a custom combat scene. Static monsters
use a skill-the-spire **360×360 profile**: unlike the atlas-backed icons, this is a chosen
consistent render footprint rather than an engine-mandated source size. RitsuLib renders it
one-to-one into 396×396 bounds.

**A power subclass must extend `ModPowerTemplate` directly.** Its `PowerAssetProfile`
controls the loose-PNG paths. A direct game-model subclass bypasses the adapter and leaves
the checked fallback in place. (Same holds for relic: extend `ModRelicTemplate`.) See
`recipes/power.md`.

**The relic outline (`<slug>_outline.png`).** A relic has a third file through
`RelicAssetProfile.IconOutlinePath`. `gen_sprite.py` thresholds every nonzero final-main
alpha pixel to opaque, expands that mask with an 8-pixel square max filter
(`round(256 * 0.03)`), and writes a filled white RGBA silhouette. Relic normalization
reserves the same 8-pixel inset on the fitted dimension before deriving the outline, so
the expansion stays inside the unchanged 256x256 canvas. The main and big files remain
identical to each other and no acquisition call is made. RitsuLib checks the custom path and
retains the template outline fallback when it is absent. `power` has no outline.

Ancient-rarity full art (606×852) is intentionally **out of scope** — we don't make
Ancient cards.

## Character art

A playable Character's slots, tiers, sheets, identity routing, and prompt templates are in
`reference/art-character.md`; read it only for Character art.

## The enchantment icon contract

A generated enchantment owns one transparent `images/enchantments/<slug>.png`, normalized
to **64×64** with `contain` fit and chroma-key on. Its concrete class uses an
`EnchantmentAssetProfile` when custom art is selected:

```csharp
public override EnchantmentAssetProfile AssetProfile => new(
    IconPath: $"res://<ModName>/images/enchantments/<slug>.png");
```

Use forward slashes in every `res://` URI. Omit the profile override in placeholder mode so
the template keeps the checked game fallback. Do not return a missing mod path directly.

This is one shared texture, not two outputs. `NCard.UpdateEnchantmentVisuals` assigns
`EnchantmentModel.Icon` to `%Enchantment/Icon` for hand, grid, reward, and inspect-style
card nodes; `CardModel.HoverTips` adds `EnchantmentModel.HoverTips`, whose `HoverTip` uses
the same `Icon`. Nonstandard special-case 160×150 vanilla icons do not change this
normal generated profile.

## The orb icon contract

A generated orb owns one transparent `images/orbs/<slug>.png`, normalized to **100×100**
with `contain` fit and chroma-key on. This spec is icon-only. Use a checked custom path plus
explicit matched vanilla fallbacks:

```csharp
public override OrbAssetProfile AssetProfile =>
    ContentAssetProfiles.Orb("frost_orb");

protected override string ChannelSfx =>
    "event:/sfx/characters/defect/defect_frost_channel";
```

`OrbModel.Icon` feeds both the smart `HoverTip(orb, ...)` and the `CpuParticles2D` at
`NOrb/%Flash`.

The combat body remains explicitly separate. `gen_sprite.py --spec orb` emits no scene,
atlas, skeleton, animation, or audio. Proof covers the Frost scene fallback and
channel event, not a custom icon becoming the body. Keep both fallbacks; a custom Spine
body belongs to the later animation expansion and does not block current static support.

## The static monster-body contract

A generated monster owns one transparent `images/monsters/<slug>.png`, normalized to
**360×360** with `contain` fit and chroma-key on. Draw one full creature in a neutral
combat-ready pose, feet on a clear shared baseline, with the silhouette filling roughly
85-90% of the frame. Do not add ground, cast shadow, scenery, text, particles, or effects
that imply a one-time attack; the same still image remains visible for every move.

`MonsterAssetProfile.VisualsScenePath` is a scene seam, not the loose-PNG seam. Wire the
static body through the public RitsuLib resource factory and retain an explicit checked
fallback:

```csharp
using Godot;
using MegaCrit.Sts2.Core.Nodes.Combat;
using STS2RitsuLib.Scaffolding.Content;
using STS2RitsuLib.Scaffolding.Godot;

public static string FallbackVisualPath =>
    SceneHelper.GetScenePath("creature_visuals/fallback");
public static string ModVisualPath =>
    "res://<ModName>/images/monsters/<slug>.png";

public override MonsterAssetProfile AssetProfile => new(FallbackVisualPath);
public override bool HasDeathSfx => false;

protected override NCreatureVisuals? TryCreateCreatureVisuals()
    => ResourceLoader.Exists(ModVisualPath)
        ? RitsuGodotNodeFactories.CreateFromResource<NCreatureVisuals>(
            ResourceLoader.Load<Texture2D>(ModVisualPath))
        : null;
```

When present, `RitsuGodotNodeFactories` creates a foot-aligned `Sprite2D`, expands the
360×360 texture to 396×396 bounds, and generates `%CenterPos` plus `IntentPos` at
`(0,-466)`. `NCreature` sees no `SpineBody`, skips animator creation, and keeps its normal
hitbox/intent/fade lifecycle. When absent, `TryCreateCreatureVisuals()` returns `null`; the
original scene loader resumes at `FallbackVisualPath` without first logging a missing
custom-id scene. `HasDeathSfx => false` avoids the default nonexistent custom-id death
audio event while the non-Spine death fade remains available.

Combat and bestiary are independent visible consumers of the same getter. Headed review
checks floor/health-bar alignment and an unobscured intent in combat, and the title, move
list, and uncropped body in the bestiary.

This does not support attack/hurt/death/cast animation, Spine skeleton/atlas data, animated
bestiary move previews, or a separate phobia body. Those are later animation/variant
extensions. In the supported profile animation triggers safely no-op, death fades the still
body, and phobia mode retains the same texture.

## The normal-event portrait contract

An implemented normal event has an initial portrait at
`images/events/<event-slug>.png` and may have additional page portraits at
`images/events/<event-slug>_<page-key-lower>.png`. Every slot is independently normalized
with `--spec event` to **3440×1613**, opaque `cover` fit, and chroma-key off. Eleven current
normal/phobia portrait samples in the pinned game pack use that logical size.

Use an explicit checked `EventAssetProfile` fallback in every generated Event. Also remove
the convention-derived missing path from preloading when the profile uses a different name:

```csharp
public const string FallbackPortraitPath = "res://images/events/this_or_that.png";

public static string ModPortraitPath =>
    "res://<ModName>/images/events/<slug>.png";

private string DefaultInitialPortraitPath =>
    $"res://images/events/{Id.Entry.ToLowerInvariant()}.png";

public override EventAssetProfile AssetProfile => new(
    InitialPortraitPath: ResourceLoader.Exists(ModPortraitPath)
        ? ModPortraitPath
        : FallbackPortraitPath);

public override IEnumerable<string> GetAssetPaths(IRunState runState) =>
    base.GetAssetPaths(runState)
        .Where(path => path != DefaultInitialPortraitPath);
```

For a page portrait, check the mod path before loading it. When it is absent, do not call
`SetPortrait`; the current portrait is the verified fallback. `NEventRoom.SetPortrait`
accepts the loose `Texture2D` directly. If the old portrait owns attached nodes, call
`NEventLayout.RemoveNodesOnPortrait()` before switching, as vanilla `Trial` does. Generated
owned VFX is stricter: `RemoveNodesOnPortrait()` only detaches it, so first locate every
named owned root and call `QueueFreeSafely()` as required by `reference/event-vfx.md`.

The remaining boundaries are explicit:

- phobia uses a private engine path and has no promoted RitsuLib consumer proof; keep the
  normal portrait/fallback and do not generate a phobia claim;
- `EventLayoutType.Custom` resolves a fixed global scene path and requires a complete
  `ICustomEventNode`, including focus, input, options, lifecycle, and cleanup. There is no
  checked standard-layout fallback;
- `NAncientEventLayout` casts the model to `AncientEventModel` and instantiates its
  background scene. A normal `ModEventTemplate` is not an Ancient presentation proof;
- raster portrait generation does not create VFX. The separate code-native
  `portrait_halo` profile is implemented through `reference/event-vfx.md`; arbitrary
  VFX remains later work.

The promoted bounded VFX proof used only public/native pieces: `EventModel.OnRoomEnter`,
`NEventLayout.AddVfxAnchoredToPortrait`, native `Node2D`/`Line2D`/`Polygon2D`, a looping
`Tween`, Fast Mode handling, and explicit `QueueFreeSafely` cleanup. The real headed run
observed rotation advance plus visible initial/page/resumed states, then proved cleanup on
combat entry. RitsuLib exposes broader custom Event VFX/layout routes, but they remain
unlisted. `portrait_halo` is the only generated VFX profile; the
separate exact built-in `trial_noble` profile is documented in
`reference/event-native-presentation.md`. Arbitrary scenes, shaders, audio, or other
generated motion remain outside the static-art contract.

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

Bold 2D game illustration: big simplified shapes, hard-edged cel shading with about
two flat tones per surface, thick clean dark outlines on the focal subject, high
contrast. One dramatic moment frozen mid-motion, shown close up: the focal subject is
large and dominates the frame. The subject carries rich hand-painted material detail
(chipped metal, wood grain, wrapped leather, painted highlight shapes) while the
background stays simple. Build the whole image from two or three dominant hues:
one for the background, one or two for the subject and its effect, taken from the
subject's own element (fire is orange and yellow, poison green, frost cyan, shadow
purple). A thin bright rim line in the subject's accent color traces part of its
silhouette. The background is a few broad, low-detail flat shapes (drifting smoke, rock
slabs, swirls, or one soft glow behind the subject), darker or less saturated than the
subject. No rainbow palette, no busy particle field, no detailed scenery. The
composition must read clearly even at small card-art size.

NOT photorealistic, NOT a 3D render, NOT pixel art. No text, letters, numbers, logos,
border, card frame, UI, or watermark.
```

**Layer 2 — few-shot reference images (when the acquisition route supports them, much
stronger).**
Pass `--reference <sts2api>/reference/art-samples` to `gen_sprite.py generate` — always the
**root** samples dir, not a subdir. It contains `card/` (18 portraits), `relic/` (6 icons),
`power/` (6 icons), `potion/` (6 icons), `enchantment/` (20 normal 64x64 icons), `orb/`
(5 non-empty icons), `monster/` (the Axebot, Ceremonial Beast, and Crossbow Ruby Raider
renders), `event/` (six reviewed wiki.gg previews), `rest_site_option/` (Rest, Smith, and
Lift button tiles), and the three-image Character pools:
`character_select/`, `character_background/`, `character_icon/`, `character_combat/`, and
`character_rest/`.
The tool **auto-selects the matching visual family** and randomly samples three distinct
images when the pool is larger. A file named on its own in `--reference` is never sampled
away: it is sent after the sampled style images. Character aliases are explicit: locked uses select,
marker/energy use icon, merchant and the combat cue sheet use combat, and rest uses rest;
background uses its own
wide selection-scene pool. A missing
same-name directory never falls back to another content family's images.
Monster's fixed three are always all supplied.
Never mix families merely to fill the reference list; their visual languages differ.

The Images transport sends the selected files as multipart `image[]` inputs to
`/images/edits`; Chat transports inline them as image data URLs; a command backend receives its
`reference_args` once per file. This needs a model that accepts image inputs. For a host tool,
randomly choose up to three files from the matching spec directory, make them visible
through the runtime's normal local-image mechanism, and label each one STYLE REFERENCE
ONLY. If the route cannot consume local references, use the type-specific text prompt
alone. (All © Mega Crit, reference-only — see `art-samples/ATTRIBUTION.md`.)

If any reference set is removed, the corresponding detailed text template remains the
fallback.

## The card portrait prompt template — three segments

The final prompt is **three segments concatenated**. Only the middle one is written per
card; the outer two are fixed guardrails, so style stays consistent and `gen_sprite.py`
can always fit/place the result:

```
[① fixed style prefix]   ← the Layer-1 STS2 style descriptor above (verbatim)
[② generated subject]    ← the ONE thing that differs per card (see below)
[③ fixed structural/negative constraints]:
   A single {subject}, large and close up, dynamic diagonal composition. Keep its key
   part (head, blade, point of impact) well inside the frame; the rest may run off an
   edge. Landscape ~4:3.
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
list. Name the focal subject and how it fills the frame (large, close up), the one
action it's frozen mid-motion in, and its two or three colors (the element hue, the rim
line, the dark background). Keep it concrete and heroic; one clear subject beats a busy
scene. Example shape (subject only — ①③ wrap it):

> *A blazing arrow of living fire, seen close up, streaks diagonally toward the upper
> right, frozen mid-flight. A ribbon of orange-and-yellow flame streams behind it, and a
> thin yellow rim line traces the arrowhead against a deep navy background of slow
> smoke shapes. Stylized and heroic.*  ← for a card named **"Firebolt"**

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
- **Key color follows the subject.** When the subject's own colors include magenta, pink,
  or purple, replace every `#FF00FF` magenta background instruction in that asset's prompt
  (including Character sheets) with solid flat pure `#00FF00` green, and "no magenta in the
  subject" with "no green in the subject". Import reads the key from the source border, so
  the command and flags stay the same. Otherwise keep magenta.
- **Key part inside the frame.** A landscape source near 4:3 loses only a sliver in the
  `cover` crop to 1000x760, so the subject can be large as long as its key part stays
  clear of the edges. A square source loses about a quarter of its height; keep the key
  part nearer the middle then.
- **One image per call.** `gen_sprite.py` requests `n=1` and keeps that single result —
  there is no batch-and-pick. If it's not right, *regenerate*: tweak segment ② and re-run
  (the regenerate loop below). One at a time, judged by eye.

**Cut-out subject shape (relic / power / potion / enchantment / orb / monster).** These are a single isolated subject,
not a scene. Name one object, center it, put it on flat magenta. Spec-specific art
direction, distilled from the vanilla references:

- **Scale — make the object BIG.** Unlike a card portrait (a full-bleed scene the `cover`
  crop trims), an icon should nearly fill its frame. `gen_sprite.py` crops
  to the subject's bounding box and scales it up (`fit: contain`, `fill=1.0`), so the *only*
  thing that makes a relic look small in-game is the model drawing it small on a big empty
  background (that empty space either survives as padding, or a soft/gradient background
  defeats the chroma-key and gets counted into the bbox). Fight this in the prompt: say the
  object is **large and fills ~90% of the frame, tightly framed, matching the scale and
  framing of the reference images** (the references define proportion, not just style), and
  demand a **solid flat pure #FF00FF magenta background — no gradient, no shadow, no vignette**
  so the cut-out is clean. If a generated icon still reads small, this scale/tight-framing
  line in segment ② is the first thing to strengthen (then regenerate).
- **No semi-transparent effects.** Smoke, steam, mist, glow haze, and soft auras blend
  with the key color, and the cut-out keeps them as a pink smear. Every cut-out prompt's
  segment ③ forbids them; do not describe them in segment ② either. Paint glow as solid
  shapes inside the subject (glowing cracks, a lit core) instead.
- **potion** — use the potion template below: the bottle **tilted ~45° leaning to the
  right**, glass painted opaque. That is how STS2 displays potions; only some big
  square-ish potions stand upright. We tilt *all* generated potions right for consistency
  (a deliberate, accepted simplification — no upright/tilt branching). Pick the bottle
  silhouette + liquid colour from the potion's name/effect (a red fizzing flask for a
  damage potion, a blue calm vial for block, …).
- **relic** — use the relic template below: a painted physical object.
- **power** — use the power template below: a flat graphic glyph. Powers look nothing
  like relics; never reuse the relic wording for them.
- **enchantment** — use the dedicated micro-emblem template below. It is much flatter and
  simpler than a relic/power icon because it must survive at 64x64.
- **orb icon** — use the dedicated elemental-core template below. It owns painted material
  and contained glow, not a generic flat glyph and not the combat body.
- **monster** - one complete creature in a neutral combat-ready pose, in a 3/4 view
  **facing left**, toward the player on the left of the screen. Keep both feet on one
  baseline and the entire silhouette inside the frame; fill about 85-90%. No floor, cast
  shadow, background prop, attack streak, spell burst, or other animation-like moment.
  This one still serves combat and bestiary.

## The relic prompt template

A relic is a painted physical object on the relic bar, reused for the inspect popup. The
references are chunky, slightly exaggerated objects with soft painterly shading and a
thick dark outline band; they read as real materials, not as flat symbols.

```
[① fixed relic style]:
   Original relic icon for a deck-building game. Match the reference images'
   hand-painted icon language as STYLE ONLY: one chunky, slightly exaggerated physical
   object with simplified shapes, soft painterly shading in two or three value steps, a
   few crisp highlight strokes, and a thick, even dark charcoal outline band around the
   whole silhouette. Medium saturation with one clear local color and an honest material
   (metal, wood, cloth, bone, stone, glass). No glossy 3D render, photoreal texture, flat
   vector style, or app-icon gradient. Do not copy the reference objects.
[② generated object]:
   One or two concrete sentences translating the relic name into one object, naming its
   main color and its single accent.
[③ fixed relic composition/negative constraints]:
   One object, upright or gently tilted, centered, large and filling about 90% of a
   square, readable at 64x64. Perfectly flat solid #FF00FF background with no gradient,
   texture, or shadow. No smoke, glow haze, sparkles, or any other semi-transparent or
   detached effect. No text, letters, numbers, UI, frame, badge, backing plate, or
   watermark. Do not use magenta inside the object.
```

## The power prompt template

A power is a status icon over a creature and in the apply/expire popup. The references are
flat graphic glyphs (a crosshair, a gear, a hazard barrier, a red coil) with almost no
shading, closer to stickers or road signs than to painted objects.

```
[① fixed power style]:
   Original status-effect icon for a deck-building combat game. Match the reference
   images' flat graphic glyph language as STYLE ONLY: one bold, simple symbol built from
   two or three flat colors, almost no shading (at most one darker tone per color), clean
   geometric or brush-stroke shapes, and a thick, even dark charcoal outline band around
   the whole silhouette. It reads like a sticker or a road sign, not a painted object. Do
   not copy the reference symbols.
[② generated symbol]:
   One or two concrete sentences translating the power name into one symbol, naming its
   two or three flat colors.
[③ fixed power composition/negative constraints]:
   One symbol, centered, filling about 90% of a square, instantly readable at 32x32.
   Perfectly flat solid #FF00FF background with no gradient, texture, or shadow. No
   smoke, glow haze, sparkles, or any other semi-transparent or detached effect. No text,
   letters, numbers, UI, frame, badge, backing plate, or watermark. Do not use magenta
   inside the symbol.
```

## The potion prompt template

A potion is one glass bottle shown in the potion bar, tooltip, and use effect. Real
transparency is impossible on a keyed cut-out: a model that paints see-through glass lets
the magenta background tint the bottle, so the template asks for opaque painted glass.

```
[① fixed potion style]:
   Original potion icon for a deck-building game. Match the reference images as STYLE
   ONLY: one glass flask with a cork or stopper, tilted about 45 degrees to the right.
   Paint the glass as an opaque pale grey-blue rim with one bright highlight streak, never
   as real transparency: the background must not show through the glass. The liquid is one
   saturated color with a few bubbles or one simple symbol shape inside. Soft painterly
   shading and a thick, even dark charcoal outline band around the whole silhouette. Do
   not copy the reference bottles.
[② generated potion]:
   One sentence naming the bottle shape, the liquid color, and the one symbol or bubble
   pattern inside, taken from the potion's name/effect.
[③ fixed potion composition/negative constraints]:
   One bottle, large, filling about 90% of a square, readable at 64x64. Perfectly flat
   solid #FF00FF background with no gradient, texture, or shadow. No smoke, fumes, glow
   haze, sparkles, or any other semi-transparent or detached effect. No text, letters,
   numbers, UI, frame, label, or watermark. Do not use magenta inside the bottle.
```

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
   watermark, detached particles, semi-transparent glow outside the core, or energy
   extending to the canvas edge. Do not use magenta inside the orb.
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
   One complete creature in a neutral combat-ready pose, 3/4 view facing left.
   Both feet on one shared baseline; full silhouette visible; fill 85-90% of a square.
   Perfectly flat solid #FF00FF background with no gradient, texture, or shadow.
   No floor, scenery, text, UI, watermark, attack streak, spell burst, or particles.
   No cropped limbs, cast shadow, contact shadow, reflection, or magenta in the creature.
   No smoke, steam, mist, glow haze, or any other semi-transparent effect: everything in
   the image is either solid creature or flat background.
```

Do not include a transient move effect. The same still image is used for idle, every move,
combat damage, death fade, and the bestiary entry until the later animation expansion.

## The Rest Site option prompt template

A Rest Site option is a compact opaque button tile, not a transparent relic icon and not a
detailed scene. The references (Rest, Smith, Lift) each use one saturated background hue
that sets the action's mood, a few simple swirl, burst, or lightning shapes in lighter and
darker tones of that hue, and one large central object with a thick dark outline:

```
[① fixed Rest Site style]:
   Original Rest Site action tile for a deck-building game. Match the reference images
   as STYLE ONLY: one saturated dominant background hue that sets the action's mood,
   with a few simple swirl, burst, or streak shapes in lighter and darker tones of that
   same hue; one central object with a thick dark outline, simple painted shading, and a
   few crisp highlights. Bold and readable like a button, not a detailed scene. Do not
   copy the reference objects.
[② generated action]:
   One or two sentences naming the one object or tool that shows the action, its
   material, and the background hue.
[③ fixed Rest Site composition/negative constraints]:
   The object large and centered, filling about 70% of the tile height, 3:2 landscape.
   Full-bleed opaque background to every edge. No text, letters, numbers, logo, border,
   frame, torn-paper edge, UI, photorealism, 3D render, or pixel art.
```

`--reference` selects the `rest_site_option/` pool. `gen_sprite.py` normalizes the result
to 256x169 with `cover`; each generated asset still receives normal headed framing review.

## The event portrait prompt template

An event portrait is a very wide room illustration behind live UI, not a centered card
portrait. Derive its subject from the event's title and opening situation, not from the
numeric option rewards. Use the general flat 2D/cel-shaded style language above, but
replace the card composition paragraph with this fixed event structure:

```
[① fixed event style]:
   Original wide environment illustration for a deck-building game's event room.
   Match the reference images' graphic 2D environment painting: large angular silhouettes,
   simplified polygonal forms, hard-edged two-to-four-step shading, selective clean dark
   outlines, deep cool atmospheric shadows, and one restrained saturated or emissive
   accent. Use sparse detail and broad negative space outside the focal situation. Do not
   reuse the card prompt's radial burst, centered hero pose, or warm rim-light formula.
[② generated situation]:
   Two-to-four sentences showing the event title/opening as one concrete moment.
[③ fixed event composition/negative constraints]:
   Very wide ~2.13:1 landscape. Place the focal subject in the left third.
   Keep the center-right and lower-right dark, low-detail, and low-contrast so the
   game's title, description, and option buttons remain readable. Full-bleed opaque scene.
   No text, letters, numbers, logos, border, UI, card frame, or watermark.
   NOT photorealistic, NOT a 3D render, NOT pixel art.
```

Do not reuse the card prompt's "subject centered" constraint for events. Request the
widest supported landscape ratio from the selected backend after checking its live model
guide; `gen_sprite.py` owns the final 3440×1613 crop and placement.

## Consent and the regenerate loop

For a host tool, the mod-level `generate` choice authorizes the initial one-image-
per-asset run without a separate API key. Follow any approval or usage warning presented by
the host and do not claim that host usage is free. For a `backend:<name>` route,
**get one approval for the whole initial run before the first paid call.** Show it in one
message: the model/backend, the credit-spending action, the shared segments ①③ once, then
one line per asset or Character sheet (a sheet line names its cells) with its segment ②
subject and its call count (one, or the spec's fixed
budget such as one Character sheet), the total number of calls, and the worst case if
every asset used both regenerations below. One yes covers
exactly that list; an asset added later needs its own yes. A Character lists only its
chosen tier's slots and its cue sheet. A Character run is two batches:
the selection portrait alone first, because every later Character asset uses it as the
identity reference, then the rest after the user has seen the portrait. Within the second
batch the cue sheet runs after the body sheet, since its anchor is the normalized combat
body. Do not silently
spend or treat an earlier custom-art preference as approval for an external route. Every
regeneration, including a native-tool regeneration, needs a new confirmation after the user
sees the current result. This is also where the "regenerate/tweak this sprite" loop
lives:

```
derive subjects (②) → show the batch list → one yes → generate all → user looks at results
   → happy: keep it, continue to build
   → not happy: fix it in import if it can be, else regenerate (at most twice), look again
```

Each asset gets **at most two regenerations**, so the cost stays predictable:

- First fix what needs no call: re-run `gen_sprite.py import` on the kept raw source under
  `<project>/art-sources/generated/<spec>/` (import re-crops, re-fits, and re-keys it;
  `--chroma` or `--no-chroma` toggles keying) for framing, scale, or background problems.
- Style drift or a bad sample is usually sampling variance: re-run the same prompt once
  before editing it. Edit segment ② only when the content itself is wrong.
- After the second regeneration, keep the best result or the checked fallback, and say
  which. Another paid call needs the user to ask for it explicitly, with its cost stated.

Only segment ② changes on a regenerate; ①③ and the few-shot references stay fixed.
Adjusting a prompt is far cheaper than editing code, so this loop is the natural place to
iterate. For a multi-card mod, segments ①③ + the references are shared across all cards,
so cross-card style stays consistent even though each card's ② differs.

## Cut-out cleanup

An image model may texture the requested magenta background with dark fragments. Color
keying alone keeps those fragments and shrinks the subject. The cut-out cleanup in
`gen_sprite.py import` retains the centered subject cluster, removes disconnected debris, and
then performs the final `contain` fit, so such a source can pass without a paid
regeneration.

Antialiased edges blend the subject with the key color. Every keyed import neutralizes
that spill on the visible pixels within 2 px of transparency, so a dark outline does not
carry a thin magenta (or green) line onto the game's dark UI.

## Using the tool

```
# host-tool: image generation is an agent tool call, not a shell command. Use it only
# when the current runtime actually exposes it. Codex: built-in image_gen mode, one call
# per asset, no OPENAI_API_KEY. Then normalize the host-reported local source file:
python ../modmaker/scripts/gen_sprite.py import \
  --spec card --slug firebolt --input "<native-output.png>" \
  --out "<mod>/<ModName>/images"

# import keys each spec by its contract default: cut-out specs (relic/power/potion/
# enchantment/orb/monster and transparent Character profiles) are keyed, card/event/
# Rest Site/selection/background stay opaque. --chroma / --no-chroma override it.
# Keep the raw source on a perfectly flat #FF00FF background until this import step.
# For each selected normal-event slot use --spec event; it writes events/<slot-slug>.png.

# backend:<name> — after the batch approval that lists this asset (or a regeneration's
# own yes). Sends the prompt (+ the spec's few-shot references when the backend takes
# images), then fits, resizes, and places the result like import:
python ../modmaker/scripts/gen_sprite.py generate \
  --spec card --slug firebolt --prompt "<the filled template above>" \
  --out <mod>/<ModName>/images --backend <name> \
  --reference ../sts2api/reference/art-samples

# local-image — the user's own file, same normalize + place:
python ../modmaker/scripts/gen_sprite.py import \
  --spec card --slug firebolt --input ./my-art.png --out <mod>/<ModName>/images

# local-image inside a larger picture (a whole card with frame and text, a sheet):
# 1. write a source-pixel grid preview, read the box off it, and redraw to confirm;
python ../modmaker/scripts/gen_sprite.py grid \
  --input ./whole-card.png --out <work dir>/art-review/whole-card-grid.png \
  [--box 40,90,520,381]
# 2. import only that box (X,Y,W,H in source pixels, exactly as the grid labels them):
python ../modmaker/scripts/gen_sprite.py import \
  --spec card --slug firebolt --input ./whole-card.png --crop 40,90,520,381 \
  --out <mod>/<ModName>/images

# list the contract (script's view — should match the table above):
python ../modmaker/scripts/gen_sprite.py list-specs
```

The host-tool route must follow the runtime's installed image-generation instructions.
For Codex, use the built-in `image_gen` tool rather than the image skill's CLI/API fallback;
that fallback requires `OPENAI_API_KEY` and belongs under an explicit backend. Inspect
the native output before importing it. Use the actual local path returned by the host
(Codex normally stores built-in output under `$CODEX_HOME/generated_images/`); if the host
returns no local file, the route is unavailable and the placeholder remains. Do not run a
second background-removal helper for cut-out sources: `gen_sprite.py import` owns the
keying, fit, resize, and final STS2 placement. When the host tool takes a size or
orientation, request the one matching the spec: landscape for card, event, Rest Site, and
Character background; portrait for Character selection; square otherwise, at 2048x2048
for the `character_cues` sheet when the tool takes a size. `gen_sprite.py generate` picks
the same orientation for a backend unless its config sets `request_size`.

After a cut-out import, a stdout line starting `[gen_sprite] warning:` names one of two
failures. `only N% ... became transparent` means the background was not a flat key color
and will show as a box in game; regenerate with a flatter background instead of shipping
it. `subject touches the <edge> edge` means the subject reached the source border (for a
sheet, its cell border), so part of it, such as a hem or a weapon tip, was probably cut
off; look at the result and regenerate with margin on every side when it is. Before showing
any imported result to the user, look at the normalized PNG yourself and regenerate an
obvious framing or background failure first; the user still judges style.

`generate` keeps each raw backend source at `<project>/art-sources/generated/<spec>/<slug>.png`,
outside the packed Mod folder. A failed or redone normalization re-imports that file
instead of paying for a second generation. A failed, timed-out, or ambiguous generation
exits nonzero; never resubmit it automatically, because the backend may already have
charged. Offer another route, local import, or placeholder instead.

A `backend:<name>` route is configured per `reference/art-backends.md`.
