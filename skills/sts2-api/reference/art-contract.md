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
> A concrete monster must check its static PNG in `TryCreateCreatureVisuals()` and pass its
> texture to RitsuLib's `RitsuGodotNodeFactories`; `MonsterAssetProfile` retains the explicit
> built-in fallback scene. Never put the PNG in the profile's scene path.
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
card text plus a RitsuLib/native hover tooltip whose icon is intentionally null. The headed
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

- RitsuLib's `CardAssetProfile.PortraitPath` resolves the card texture path.
  `images/card_portraits/<slug>.png`; omit the profile to retain the checked placeholder
  fallback. A normal card's portrait is
  **1000×760 landscape**. The 606×852 "full art" size is **Ancient-rarity only** (a
  different card layout / UI slot — `NCard.cs` switches on `Rarity == CardRarity.Ancient`).
  **We only make normal cards, so we only ever produce 1000×760.** Putting a 606×852
  (portrait-shaped) image there feeds a vertical picture into a landscape slot → it looks
  distorted in-game (the M5.5 "违和" bug, fixed 2026-07-08).

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

**A relic and a power each need TWO files; every other invocation writes ONE
(`gen_sprite.py` handles the count automatically). An event may invoke the same spec once
per selected portrait slot.** Relic/power/potion were confirmed live
by Bauble, Smolder, and Fizz on 2026-07-08; enchantment by Guarded and the orb icon by
Shelter on 2026-07-17; the monster combat/bestiary body by Canary Sentinel on 2026-07-17.
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
`gen_sprite.py` writes the same normalized image to every path a spec needs, so you don't
manage them by hand. The RitsuLib Card profile uses the single
`card_portraits/<slug>.png` path.

**Why these icon specs take a loose `.png` (no `.tres` authoring).** Vanilla STS2 loads every icon
family from Godot `.tres` sprite-atlases (`atlases/relic_atlas.sprites/…`, `power_atlas`,
`potion_atlas`, `relic_outline_atlas` — see `RelicModel`/`PowerModel`/`PotionModel` in the
decompile). But the icon getters accept a plain `Texture2D` path, so a loose PNG works too:
for **relic/power/potion**, RitsuLib's asset profiles accept explicit loose PNG paths with
an existence-checked fallback. Either way a mod just drops a 256×256 PNG in — no atlas.
**This overturned an earlier belief that potion needed a `.tres` emitter** — it does not
(live-verified 2026-07-08). The only reason vanilla potions *appear* to require an atlas is
that the default (un-overridden) getter points at the atlas path, which a mod doesn't ship.
Enchantment and Orb profiles likewise accept a loose PNG directly; omit the profile to keep
the checked fallback.

**Sizes.** All 324 vanilla relic + 271 power + 63 potion icons extracted from the game are a
uniform **256×256**; live canary runs confirmed that size + all icon paths render correctly,
so relic/power/potion are all `verified: True`. `card` is 1000×760, also live-verified
(2026-07-08). Normal enchantment icons are 64×64 and live-verified in both consumers
(2026-07-17). Normal orb icons are 100×100 and live-verified in the smart tooltip and
trigger flash (2026-07-17); this does not verify a custom combat scene. Static monsters use
an open-mod **360×360 profile**: unlike the atlas-backed icons, this is a chosen consistent
render footprint rather than an engine-mandated source size. RitsuLib renders it one-to-one;
the headed combat and bestiary proof verified the resulting 396×396 bounds.

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
retains the template outline fallback when it is absent. `power` has no outline. This
M6.5 route passed exact path/texture assertions under a real `NRelic` and the maintainer's
headed review in the 2026-07-27 Meridian proof.

Ancient-rarity full art (606×852) is intentionally **out of scope** — we don't make
Ancient cards.

## Character art profiles and combat cues

Character assets are separate contracts because `CharacterAssetProfile` maps distinct
game hosts. The active profiles are re-grounded against STS2 `0.107.1` and RitsuLib
`0.4.62`; archived framework inventories are style/consumer research only.
Each profile is promoted independently only after a real headed Character run shows the
packed resource instead of the resolved fallback.

| spec | output under `images/charui/` | size | presentation |
|---|---|---:|---|
| `character_select` | `<slug>.png` | 132x195 | opaque selection portrait/button |
| `character_select_locked` | `<slug>.png` | 132x195 | opaque locked selection portrait; optional, template fallback is valid |
| `character_icon` | `<slug>.png` + `<slug>_outline.png` | 88x88 each | transparent main icon plus deterministic white outline; raw icon scene layers both in the top panel |
| `character_map_marker` | `<slug>.png` | 49x64 | transparent map marker |
| `character_background` | `<slug>.png` | 1920x1200 | opaque select background consumed by a minimal raw-scene wrapper |
| `character_combat` | `<slug>.png` | 512x512 | transparent static body consumed by an existence-checked public resource factory |
| `character_rest` | `<slug>.png` | 512x512 | transparent static rest-site body consumed by an `NRestSiteCharacter` wrapper |
| `character_merchant` | `<slug>.png` | 512x512 | transparent static merchant body consumed by an `NMerchantCharacter` wrapper |
| `character_energy` | `orb_layer_<1..5>.png` | 256x256 each | five transparent layers referenced by one raw energy-counter `.tscn` |
| `character_energy_large` | `<slug>.png` | 256x256 | transparent large card Energy icon |
| `character_energy_text` | `<slug>.png` | 24x24 | transparent rich-text Energy icon |

The bounded combat-cue sources are four action sheets rather than ordinary single-file
runtime specs:

| source spec | sheet grid | runtime output | timing |
|---|---:|---|---:|
| `character_cue_idle` | 2x2 | `cues/idle/00.png` .. `03.png` | 180 ms, loop |
| `character_cue_attack` | 2x2 | `cues/attack/00.png` .. `03.png` | 90 ms, one shot |
| `character_cue_hit` | 2x2 | `cues/hit/00.png` .. `03.png` | 80 ms, one shot |
| `character_cue_dead` | 2x3 | `cues/dead/00.png` .. `05.png` | 140 ms, terminal |

The 2026-07-23 RitsuLib-only Wayfinder run re-proved `character_select`, `character_background`,
`character_icon`, `character_combat`, `character_rest`, `character_merchant`,
`character_energy`, and `character_energy_text`. Real selection, CombatPlayer, RestSite,
and Shop hosts rendered the exact PNGs; one native energy counter exposed five 256x256
layers and the real hand Card rendered the separate 24x24 icon. Strict Tier 2 and
no-fresh-error checks passed. Locked selection and map marker remain unpromoted because
resource existence is not visual proof for those consumers.

The 2026-07-27 M6.5 Meridian proof separately established the split consumers: a real
hand `NCard` rendered the 256x256 large icon, and a formatted Card description rendered
the distinct 24x24 text icon. The maintainer's headed review passed both consumers.

`character_select` uses safe `contain` composition with chroma off; its full opaque source
is preserved inside `(6,8)-(126,187)` on the unchanged 132x195 canvas.
`character_background` remains exact 16:10 `cover` with chroma off. The icon,
marker, static body, and energy profiles use `contain` with chroma on and a flat pure
`#FF00FF` source background. The normalizer writes only loose PNGs; author code creates
the tiny raw `.tscn` wrappers for icon/background/rest/merchant/energy, and `build.py` packs them
without Godot/MegaDot. Full energy references all five layers from that one energy scene.
The optional non-Spine cue contract is limited to the four tabled sequences. Cast, Spine,
phobia, trails, audio, animated merchant/rest bodies, and multiplayer views remain outside
the contract. Read `reference/character-combat-cues.md` for runtime ownership and fallback.

### CharacterArtBundle and reference routing

`games/sts2/tools/character_art.py` owns one structured `CharacterArtBundle` for every
Character static slot and the four-action cue contract. Each static row records
required/optional status, normalized output path,
exact dimensions, alpha policy, checked fallback, real consumer, style-reference family,
fit mode, verification status, and any host-specific visible content box/baseline/public
visual style. `gen_sprite.py` and `acquire_sprite.py` read this
bundle instead of maintaining a second Character spec table. The optional locked
selection and map-marker rows remain native/shared fallback rows; their presence in the
inventory does not promote those consumers. The cue contract separately owns action order,
sheet layout, frame count/timing, loop/terminal flags, generation-call count, output
directories, shared geometry, style, anchors, and static fallback slot.

The generated Character profile uses these stable bundle output names: `select.png`,
`background.png`, `icon.png`, `icon_outline.png`, `combat.png`, `rest.png`, `merchant.png`,
`orb_layer_1.png` through `orb_layer_5.png`, `energy_large.png`, and `energy_text.png`, all under
`images/charui/`. Keep these role names when invoking the normalizer so the review tool
and the generated `CharacterAssetProfile` resolve the same files.

`icon_outline.png` is a required derived bundle row with zero generation calls. It uses
the same opaque-white 3% max-filter rule as Relics, which resolves to a 3-pixel expansion
on the 88x88 canvas; main normalization reserves the same 3-pixel inset. `Ui.IconOutlineTexturePath` points to it, while `Ui.IconPath` points
to the raw icon scene that layers the outline behind the main texture in the supported
top-panel host. The Meridian proof passed the exact model/resource/node assertions and the
maintainer's headed review for this outline route.

M6.5 splits `energy_large.png` into a 256x256 pool Energy icon while retaining
`energy_text.png` as the 24x24 rich-text icon. They are separate required bundle rows,
paths, normalization specs, and real consumers; neither path may stand in for the other.

The source directory `reference/energy_template/` contains the four lead-supplied,
transparent `256x256` PNGs `layer_2.png` through `layer_5.png`. They are fixed assets,
not generation targets: `character_energy` layer 1 has one Character-specific generation
call, while layers 2-5 have zero generation calls and are copied byte-for-byte to
`orb_layer_2.png` through `orb_layer_5.png`. The bundle validates dimensions, alpha, exact
slot mapping, and source presence before installation; it never resizes or invents a
template.

The required `selection_portrait` is the sole identity bootstrap. It is normalized first
to `charui/select.png` and is the only approved identity image; open-mod does not create a
separate Character sheet or canonical identity asset. Identity-sensitive
`character_combat`, `character_rest`, `character_merchant`, and all four
`character_cue_*` acquisitions pass that
normalized portrait as `--identity-reference` in addition to up to three type-matched STS2
style references. Background, top-panel icon, full-energy layers, and large/text Energy-icon
acquisition use a palette/motif brief derived from the user's description and reviewed
selection portrait, but deliberately do not receive the portrait as an image reference.

Cue imports stage sheets under `<project>/art-sources/character-cues/`. Runtime cue files
are replaced only when all four sheets pass magenta cleanup, grid/component extraction,
edge/body-scale QC, shared cross-action scaling, and baseline alignment. Review GIFs,
cleaned sheets, a contact sheet, and QC metadata land under
`<project>/art-review/character-cues/`; failed processing leaves prior runtime cues intact.
The processing techniques are adapted from agent-sprite-forge under MIT, with no runtime
dependency or external asset reuse.

Run the bundle review after the selected required outputs are normalized:

```powershell
python ../modmaker/scripts/character_art.py \
  --images-root <work dir>/<ModName>/images \
  --install-energy-templates \
  --out-dir <work dir>/art-review
```

The command validates exact dimensions, alpha policy, readable PNGs, required outputs,
and the selection identity bootstrap, then writes a labeled contact sheet plus a
deterministic five-layer Energy composite outside the runtime asset directory. These are
human review artifacts; no brittle image-similarity score is used as runtime acceptance.

Downfall's `char_select_locked.png` is a shared lock treatment, so generated mods may keep
the template locked asset when no custom locked portrait is requested. `mp_*` hand
textures, card trails, transition materials, and animated rest/merchant/energy scenes are
separate later contracts; do not silently infer them from these PNGs.

For static combat, leave `CharacterAssetProfile.Scenes.VisualsPath` unset and override the
existence-checked `TryCreateCreatureVisuals()` route. Load the checked PNG only when it
exists, then pass its `Texture2D` plus
`VisualNodeStyle.Empty.WithScale(0.80f).WithPosition(new Vector2(0f, -184f))` to the public
`RitsuGodotNodeFactories.CreateFromResource<NCreatureVisuals>` factory. Return `null` when
the PNG is absent so RitsuLib resumes the resolved profile fallback. Normalize visible
alpha inside `(26,26)-(486,486)` with exclusive baseline `486`; empty alpha, canvas-edge
contact, overflow, an undersized subject, or a different baseline fails validation. The
2026-07-27 Meridian host proof observed exact alpha `(64,26)-(447,486)`, screen bounds
`(326.4,372)-(632.8,740)` in a `1920x1080` viewport, and no overlap with top/bottom UI,
enemy lane, or turn banner. Static
rest-site and merchant wrappers are each one `Sprite2D` root. The R4 real
`NMerchantCharacter` rendered the merchant wrapper without a versioned prefix. Every
wrapper keeps a checked profile fallback
when its PNG or raw scene is missing. `pack_pck.py` still rejects `.gdshader`, `.gdscript`,
and `.gdextension`.

### Character prompt templates

Selection portrait:

```text
Original opaque character-select portrait for a deck-building combat game. Match the
provided STS2 selection references as STYLE ONLY. Show one original character in a clear,
full-body or waist-up pose with a readable silhouette, restrained painterly 2D shading,
and a calm neutral presentation suitable for a 132x195 button. Keep the intended head,
body, and held-object composition visible with breathing room on all sides; deterministic
normalization preserves the complete source inside the reviewed safe box. No text, logo, UI, frame,
watermark, or borrowed character design.
```

Top-panel icon/map marker:

```text
Original compact character emblem for a deck-building combat game. Match the provided
references as STYLE ONLY. Use one bold readable silhouette or emblem with broad painterly
forms, transparent cut-out edges, and no fine detail that disappears at 88x88 (or 49x64).
Place it on a perfectly flat solid #FF00FF background. No text, border, badge, watermark,
detached particles, or borrowed character design.
```

Static combat/rest/merchant body:

```text
Original full-body character render for a deck-building combat game. Match the provided
references as STYLE ONLY: softly hand-painted 2D volume, readable broad value groups,
controlled brush texture, and a neutral grounded pose. Show the entire original body on
one baseline, centered and filling about 85-90% of a square. Use a perfectly flat solid
#FF00FF background with no floor, shadow, attack effect, text, UI, watermark, or animation
streak. This still is the static fallback body, not a Spine animation frame.
```

Combat cue action sheets:

```text
Original non-Spine combat action sheet for a deck-building combat game. The normalized
selection portrait is CHARACTER IDENTITY ONLY; the provided STS2 combat images are STYLE
ONLY. Across every cell in this sheet and across all Idle, Attack, Hit, and Dead sheets,
depict exactly the same original individual, never a redesign, variant, costume change,
or reinterpretation. Keep the face, head shape, hairstyle, body proportions, outfit
construction and layers, accessories, colors, weapon shape and size, handedness, and
facing direction unchanged.

Reuse this exact neutral combat anchor from the Character SPEC: <one concise pose sentence>.
Use the same locked camera, viewing angle, apparent body scale, torso and head size, ground
baseline, and visual pivot in every cell and every action. Motion comes only from pose
changes; never zoom, crop, resize, or move the camera. Attack and Hit may extend limbs or
the weapon, while preserving body scale. Dead rotates and lowers the same-sized body
rather than shrinking, stretching, or changing its proportions.

These frames play quickly. Treat adjacent cells as closely spaced in-between frames, not
widely separated key poses. Advance the pose by one small readable step per cell; adjacent
silhouettes must substantially overlap, with no sudden jump in limb position, weapon
position, body angle, center of mass, or facing direction. Keep the complete silhouette
inside every cell with consistent padding. Read frames left-to-right, then top-to-bottom.
Use equal cells with no panel borders, labels, numbers, or gutters.

<action-specific sentence and fixed beat list from the cue contract>

Use one perfectly flat solid #FF00FF background across the sheet, with no gradient,
floor, shadow, text, UI, border, logo, or watermark. Do not borrow a reference character's
design. NOT photorealistic, NOT a 3D render, NOT pixel art.
```

The continuity and geometry paragraphs plus the SPEC's neutral anchor are repeated
verbatim in all four paid requests. Only the action-specific sentence, grid, and beat list
may change:

- `Idle` 2x2: four subtle breathing/cloth/weapon-settle steps; frame 4 stays close enough
  to frame 1 for a quiet loop.
- `Attack` 2x2: begin close to the neutral anchor, move through four restrained adjacent
  attack steps, and end already recovering toward Idle. Do not compress distant wind-up,
  peak, and recovery key poses into abrupt jumps.
- `Hit` 2x2: begin close to the neutral anchor, show a compact recoil through four small
  adjacent steps, and end already recovering toward Idle.
- `Dead` 2x3: begin from the same anchor and distribute the fall across six small adjacent
  steps before the final terminal pose; do not jump directly from standing to the ground.

Reject and regenerate a sheet when the contact-sheet review shows identity, costume,
scale, camera, pivot, or baseline drift, or when any adjacent pair has a large pose jump.
Do not replace this review with a brittle image-similarity score.

Select background:

```text
Original wide character-select background for a deck-building combat game. Match the
provided references as STYLE ONLY. Create a broad environment that supports a live
character-select information panel. Use a grounded vanilla-like close composition WITH THE FOCAL
CHARACTER ON THE RIGHT HALF, without cropping the head or identity-defining held
object. Keep the left-center region calm and low-detail for the name, HP, description, and
relic panel; keep the bottom strip and lower-right confirm-button region readable. Opaque
16:10 landscape, no text, logo, UI, border, watermark, or borrowed character design.
```

Energy icons:

```text
Original energy-core icon for a deck-building combat game. Match the provided references
as STYLE ONLY and follow the Character theme's exact palette/motif brief. Use a single
layered material core with clear value separation, centered for the requested consumer,
and no numbers or UI. For `character_energy_large`, keep bold internal structure readable
at 256x256. For `character_energy_text`, simplify the same motif to a broad silhouette and
two or three value groups that survive at 24x24. Put it on a perfectly flat solid #FF00FF
background. No frame, text, watermark, detached particles, or borrowed design.
```

For the full counter, invoke `character_energy` exactly once with slug `orb_layer_1`.
Install the committed `energy_template/layer_2.png` through `layer_5.png` files as
`orb_layer_2.png` through `orb_layer_5.png`; these four transparent 256x256 layers are
fixed byte-for-byte and never generation targets. The 256x256 `character_energy_large`
and 24x24 `character_energy_text` outputs are independently acquired and normalized from
the same theme brief. Show the user that full energy is five image assets, with only layer
1 eligible for generation, and that the two pool icons are separate assets before a paid
acquisition route runs.

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
public override OrbAssetProfile AssetProfile =>
    ContentAssetProfiles.Orb("frost_orb");

protected override string ChannelSfx =>
    "event:/sfx/characters/defect/defect_frost_channel";
```

`OrbModel.Icon` feeds both the smart `HoverTip(orb, ...)` and the `CpuParticles2D` at
`NOrb/%Flash`. The 2026-07-17 `CanaryOrb` headed run observed the same custom resource path
and 100×100 size in both nodes, triggered the particle, captured the real orb and tooltip
together, preserved passive/evoke Block `0 -> 2 -> 7`, and passed strict Tier 2 with no
fresh error block.

The combat body remains explicitly separate. `gen_sprite.py --spec orb` emits no scene,
atlas, skeleton, animation, or audio. The R3 proof verifies the Frost scene fallback and
channel event, not that a custom icon becomes the body. Keep both fallbacks; a custom Spine
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
    $"{MainFile.ResPath}/images/monsters/<slug>.png";

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

Combat and bestiary are independent visible consumers of the same getter. The 2026-07-22
RitsuLib-only `RitsuMonsterProof` headed run asserted the same custom resource path, 360×360 size,
non-Spine body, 396×396 bounds, and intent position in the real combat `NCreature` and a
real `NBestiary` default layout; it captured both and passed strict Tier 2 with no fresh
error block. The combat screenshot showed correct floor/health-bar alignment and an
unobscured intent; the bestiary screenshot showed the title, move list, and uncropped body.

This does not support attack/hurt/death/cast animation, Spine skeleton/atlas data, animated
bestiary move previews, or a separate phobia body. Those are later animation/variant
extensions. In the supported profile animation triggers safely no-op, death fades the still
body, and phobia mode retains the same texture.

## The normal-event portrait contract

A pipeline-supported normal event has an initial portrait at
`images/events/<event-slug>.png` and may have additional page portraits at
`images/events/<event-slug>_<page-key-lower>.png`. Every slot is independently normalized
with `--spec event` to **3440×1613**, opaque `cover` fit, and chroma-key off. Eleven current
normal/phobia portrait samples in the pinned game pack use that logical size. The
2026-07-17 `CanaryEvent` headed run proved the initial mod path in the real `MapNode` host.
The 2026-07-20 extension reused the same room and option click to switch to a second mod
portrait after the consequence: both textures reported 3440×1613, the result screenshot
showed the replacement, Gold changed by 25, and strict Tier 2 passed with no fresh error.
The 2026-07-23 RitsuLib-only combined Event run re-proved both portrait consumers, every
selected Event family, `selftest done`, and no fresh error.

Use an explicit checked `EventAssetProfile` fallback in every generated Event. Also remove
the convention-derived missing path from preloading when the profile uses a different name:

```csharp
public const string FallbackPortraitPath = "res://images/events/this_or_that.png";

public static string ModPortraitPath =>
    $"{MainFile.ResPath}/images/events/<slug>.png";

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
  `portrait_halo` profile is pipeline-supported through `reference/event-vfx.md`; arbitrary
  VFX remains later work.

The promoted bounded VFX proof used only public/native pieces: `EventModel.OnRoomEnter`,
`NEventLayout.AddVfxAnchoredToPortrait`, native `Node2D`/`Line2D`/`Polygon2D`, a looping
`Tween`, Fast Mode handling, and explicit `QueueFreeSafely` cleanup. The real headed run
observed rotation advance plus visible initial/page/resumed states, then proved cleanup on
combat entry. RitsuLib exposes broader custom Event VFX/layout routes, but they remain
unpromoted. `portrait_halo` is the only generated VFX profile; the
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
(5 non-empty icons), `monster/` (the Axebot, Ceremonial Beast, and Crossbow Ruby Raider
renders), `event/` (six reviewed wiki.gg previews), and four three-image Character pools:
`character_select/`, `character_background/`, `character_icon/`, `character_combat/`, and
`character_rest/`.
The tool **auto-selects the matching visual family** and randomly samples three distinct
images when the pool is larger. Character aliases are explicit: locked uses select,
marker/energy use icon, merchant and all combat cues use combat, and rest uses rest;
background uses its own
wide selection-scene pool. A missing
same-name directory never falls back to another content family's images.
Monster's fixed three are always all supplied.
Never mix families merely to fill the reference list; their visual languages differ.

The Images transport sends the selected files as multipart `image[]` inputs to
`/images/edits`; Chat transports inline them as image data URLs; Vofy receives repeated
`--image` arguments. This needs a model that accepts image inputs. For a host-native tool,
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

On 2026-07-20, one separately approved `seedream-5.0-lite` Event request used the curated
Event pool and randomly selected `this_or_that.png`, `drowning_beacon.png`, and
`doors_of_light_and_dark.png`. The `21:9`/`2K` source preserved the requested left-third
focal subject and dark center-right UI area without text or borrowed reference objects.
It normalized to the exact opaque 3440×1613 profile, packed into `CanaryEvent.pck`, and
rendered behind the real Event option UI. The same headed run changed Gold by 25, switched
to the later-page portrait, removed the initial portrait VFX, and passed strict Tier 2 with
no fresh error. This closes reference-prompt acquisition for the normal Event portrait
profile; it does not promote custom layouts, phobia art, Ancient backgrounds, or general
VFX generation. The later Event outcome/VFX acceptance separately promoted the bounded
code-native halo without adding a raster asset type.

## Using the tool

```
# host-native image generation is an agent tool call, not a shell command. Use it only
# when the current runtime actually exposes it. Codex: built-in image_gen mode, one call
# per asset, no OPENAI_API_KEY. Then normalize the host-reported local source file:
python ../modmaker/scripts/gen_sprite.py import \
  --spec card --slug firebolt --input "<native-output.png>" \
  --out "<mod>/<ModName>/images"

# For relic/power/potion/enchantment/orb/monster native sources, use the same import command with --chroma.
# Keep the raw source on a perfectly flat #FF00FF background until this import step.
# For each selected normal-event slot use --spec event with no --chroma; it writes
# events/<slot-slug>.png.

# managed credits — Vofy is acquisition only. The user installs/logs in themselves;
# preflight prints no account/credit details. Inspect live model capabilities separately:
python ../modmaker/scripts/acquire_sprite.py preflight --model <chosen-model>
vofy models <chosen-model>

# after explicit approval for this prompt/model/one-image spend. Add the root --reference
# once when the live model guide supports image inputs; the tool selects the spec and 3 files:
python ../modmaker/scripts/acquire_sprite.py create \
  --spec card --slug firebolt --prompt "<the filled template above>" \
  --out <mod>/<ModName>/images --model <chosen-model> \
  --aspect-ratio <confirmed-ratio> \
  [--reference ../sts2-api/reference/art-samples] --yes

# generate (BYO backend) — POSTs the prompt (+ few-shot STS2 style references when the
# backend supports them), then fits + resizes to the contract size + places it:
python ../modmaker/scripts/gen_sprite.py generate \
  --spec card --slug firebolt --prompt "<the filled template above>" \
  --out <mod>/<ModName>/images --config <path to art-backend.json> \
  --reference ../sts2-api/reference/art-samples

# import (local file) — same normalize + place, no HTTP:
python ../modmaker/scripts/gen_sprite.py import \
  --spec card --slug firebolt --input ./my-art.png --out <mod>/<ModName>/images

# list the contract (script's view — should match the table above):
python ../modmaker/scripts/gen_sprite.py list-specs
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
crop/fit/chroma/path contract. For relic/power/potion/enchantment/orb/monster and Character
icon/marker/combat/rest/merchant/energy/cue profiles it supplies import's `--chroma`
automatically; event and Character selection/background remain opaque. It prints the selected reference filenames
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
