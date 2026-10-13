# art-contract.md — where a custom sprite must land, and at what size

> **The art source of truth.** When a mod ships a custom sprite (a card portrait, a
> relic icon, …) the image only shows up in-game if it lands at the **exact path** the
> template's base class resolves AND is the **exact pixel size** the game expects.
>
> The exact values live in code: `gen_sprite.py`'s `SPECS` and `character_art.py`'s
> `CHARACTER_ART_BUNDLE`. They are projected into
> `reference/catalogs/art-contract-sts2-0.107.1.json` by
> `python ${GAME_TOOLS_DIR}/gen_sprite.py export-contract`, so you can read every path,
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

## Character art profiles and combat cues

Character assets are separate contracts because `CharacterAssetProfile` maps distinct
game hosts. The active profiles are re-grounded against STS2 `0.107.1` and RitsuLib
`0.6.7`; archived framework inventories are style/consumer research only.
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
runtime specs. Every grid below is **columns x rows**, matching the sheet you actually
request: cells are read left-to-right, then top-to-bottom, and each cell is 512x512.

| source spec | sheet grid (cols x rows) | source size | runtime output | timing |
|---|---:|---:|---|---:|
| `character_cue_idle` | 2x2 | 1024x1024 | `cues/idle/00.png` .. `03.png` | 180 ms, loop |
| `character_cue_attack` | 2x2 | 1024x1024 | `cues/attack/00.png` .. `03.png` | 90 ms, one shot |
| `character_cue_hit` | 2x2 | 1024x1024 | `cues/hit/00.png` .. `03.png` | 80 ms, one shot |
| `character_cue_dead` | 2x3 | 1024x1536 | `cues/dead/00.png` .. `05.png` | 140 ms, terminal |

Locked selection and map marker are not in the supported list: resource existence is not
visual proof for those consumers. They are in no art tier and are generated only when the
user names them.

The bundle's `tiers` set the spend the user picks at interview; `export-contract` publishes
each tier's slots, cue choice, and call count as `character_art_tiers` in the catalog.
`minimal` acquires the selection portrait and the body sheet, `standard` every required
static slot, and `full` adds the four cue sheets. A slot outside the chosen tier keeps its
checked fallback: author no wrapper scene or profile path for it.

### Character art sheets

Several same-role slots come from one paid grid image, split by the tool
(`character_art_sheets` in the catalog). One image keeps the cells in one style and, for
bodies, one identity; a real trial kept the same individual across all three bodies.

| sheet | 2x2 cells, reading order | references |
|---|---|---|
| `body_sheet` | combat body, rest body, merchant body, empty | portrait source as identity + `character_combat` style |
| `icon_sheet` | top-panel icon, large Energy icon, text Energy icon, empty | `character_icon` style; no portrait |

```powershell
python ${GAME_TOOLS_DIR}/gen_sprite.py generate-sheet --sheet body_sheet `
  --prompt "<sheet prompt>" --out <ModName>/images --backend <name> `
  --reference ${STS2API_SKILL_DIR}/reference/art-samples `
  --identity-reference <project>/art-sources/generated/character_select/select.png
python ${GAME_TOOLS_DIR}/gen_sprite.py import-sheet --sheet icon_sheet `
  --input <sheet.png> --out <ModName>/images
```

`generate-sheet` spends one call, keeps the raw sheet under
`<project>/art-sources/generated/sheets/`, trims a drawn grid line from every cell edge,
and normalizes each cell exactly as `import` does for its slot. `import-sheet` does the same
for an existing image (a host-tool output, the user's file, or a kept sheet) without a
call. A failed cell leaves the others placed; fix it by re-importing or by regenerating that
one slot with `generate --spec` (one call, counted against that asset's regenerations).
Regenerate the whole sheet only when most cells are wrong.

Sheet prompt: start with the sheet's per-asset template lead and its STYLE ONLY / IDENTITY
ONLY sentence, then this grid paragraph, then one line per cell, then the template's
background and exclusion sentences:

```text
One square image divided into an exact 2x2 grid of four equal square cells, read
left-to-right then top-to-bottom, with no borders, labels, numbers, or gutters. Every cell
holds exactly one centered subject, fully inside its own cell with clear empty margin on
all sides; nothing touches or crosses a cell edge. Cell 1 (top-left): <...>. Cell 2
(top-right): <...>. Cell 3 (bottom-left): <...>. Cell 4 (bottom-right): <... or "empty,
only background">.
```

Each cell line carries its slot's own constraint from the templates below: the three
bodies are the same individual in a 3/4 view facing right (combat stance, sitting at rest,
standing at ease); the icon is readable at 88x88; the large Energy icon is readable at 256x256; the text Energy icon is the
same core simplified for 24x24.

`character_select` uses full-bleed `cover` with chroma off, like the vanilla buttons: the
opaque source fills the whole 132x195 canvas and its edges may crop.
`character_background` remains exact 16:10 `cover` with chroma off. The icon,
marker, static body, and energy profiles use `contain` with chroma on and a flat pure
`#FF00FF` source background (`#00FF00` for a magenta/pink/purple subject; see the key-color
rule under "The card portrait prompt template"). The normalizer writes only loose PNGs; author code creates
the tiny raw `.tscn` wrappers for icon/background/rest/merchant/energy, and `build.py` packs them
without Godot/MegaDot. Full energy references all five layers from that one energy scene.
The optional non-Spine cue contract is limited to the four tabled sequences. Cast, Spine,
phobia, trails, audio, animated merchant/rest bodies, and multiplayer views remain outside
the contract. Read `reference/character-combat-cues.md` for runtime ownership and fallback.

### CharacterArtBundle and reference routing

`character_art.py` owns one structured `CharacterArtBundle` for every
Character static slot and the four-action cue contract. Each static row records
required/optional status, normalized output path,
exact dimensions, alpha policy, checked fallback, real consumer, style-reference family,
fit mode, verification status, and any host-specific visible content box/baseline/public
visual style. `gen_sprite.py` reads this
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
top-panel host.

The contract splits `energy_large.png` into a 256x256 pool Energy icon while retaining
`energy_text.png` as the 24x24 rich-text icon. They are separate required bundle rows,
paths, normalization specs, and real consumers; neither path may stand in for the other.

Full Energy is rendered, never generated. The source directory `reference/energy_template/`
contains four bundled, transparent `256x256` PNGs `layer_2.png` through `layer_5.png` that
fix the counter's shape: a translucent swirl (2) and an opaque pale core (3), which rotate,
and the fixed octagonal ring (4) and edge (5) above them (`character-presentation.md` §
Raw scene contract). Layer 1 sits under all of them, so only its tint around the core shows. `character_art.py --energy-colors` writes all five layers from the Character
theme contract: layer 1 is a radial disc in the card-frame color, layers 2-4 are the
templates recolored along the card-frame color, and layer 5 along the Energy outline color.
Geometry and alpha are kept exactly. Pass the card-frame target RGB as hex (each 0..1
channel times 255) and the `EnergyOutlineColor`, so the counter matches the card frames.
The bundle validates every template's dimensions, alpha, slot mapping, and presence before
writing; it never resizes or invents a template.

The required `selection_portrait` is the sole identity bootstrap. It is normalized first
to `charui/select.png` and is the only approved identity image; skill-the-spire does not create a
separate Character sheet or canonical identity asset. Identity-sensitive
`character_combat`, `character_rest`, `character_merchant`, and all four
`character_cue_*` acquisitions pass that portrait's full-resolution source as
`--identity-reference`: the kept generated source
`<project>/art-sources/generated/character_select/<slug>.png`, or the user's original file
for an imported portrait. The 132x195 normalized copy is too small to carry the face and
costume. It goes in addition to up to three type-matched STS2 style references. Background, top-panel icon, full-energy layers, and large/text Energy-icon
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
python ${GAME_TOOLS_DIR}/character_art.py \
  --images-root <work dir>/<ModName>/images \
  --tier <minimal|standard|full> \
  [--energy-colors <frame RRGGBB>,<energy outline RRGGBB>] \
  --out-dir <work dir>/art-review
```

Pass `--energy-colors` only when the tier includes full Energy. The command
validates exact dimensions, alpha policy, readable PNGs, the tier's required outputs,
and the selection identity bootstrap, then writes a labeled contact sheet plus, when the
tier includes it, a deterministic five-layer Energy composite outside the runtime asset
directory. These are
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
contact, overflow, an undersized subject, or a different baseline fails validation. Static
rest-site and merchant wrappers are each one `Sprite2D` root. The real
`NMerchantCharacter` rendered the merchant wrapper without a versioned prefix. Every
wrapper keeps a checked profile fallback
when its PNG or raw scene is missing. `pack_pck.py` still rejects `.gdshader`, `.gdscript`,
and `.gdextension`.

### Character prompt templates

Selection portrait:

```text
Original character-select portrait for a deck-building combat game. Match the provided
STS2 selection references as STYLE ONLY, including their framing: a tight close-up of the
character's head and shoulders, slightly tilted, filling the whole tall frame and running
off its edges, with bold flat cel shading, thick dark outlines, high contrast, and simple
graphic shapes, on one flat saturated background in the Character theme color. Tall 2:3
portrait. No text, logo, UI, frame, watermark, or borrowed character design.
```

Vanilla select buttons are full-bleed head close-ups on a flat theme-color field; a
waist-up figure with margins reads as a small, foreign button next to them. When a
portrait is regenerated for an existing Character, add its earlier portrait as one more
`--reference` file and say in the prompt that it fixes the identity, so the bodies made
from it still match.

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
controlled brush texture, and a neutral grounded pose in a 3/4 view facing right, toward
the enemies. Show the entire original body on
one baseline, centered and filling about 85-90% of a square. Use a perfectly flat solid
#FF00FF background with no floor, shadow, attack effect, text, UI, watermark, or animation
streak. Light from a held object stays on the object and the body: no glow halo, light
spill, or cast shadow on the background. This still is the static fallback body, not a
Spine animation frame.
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
floor, shadow, light spill, text, UI, border, logo, or watermark. Do not borrow a reference character's
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

Full Energy needs no prompt: it is rendered from the theme (see § CharacterArtBundle and
reference routing).

Pool Energy icons (`character_energy_large`, `character_energy_text`):

```text
Original energy-core icon for a deck-building combat game. Match the provided references
as STYLE ONLY and follow the Character theme's exact palette/motif brief. Use a single
layered material core with clear value separation, centered for the requested consumer,
and no numbers or UI. For `character_energy_large`, keep bold internal structure readable
at 256x256. For `character_energy_text`, simplify the same motif to a broad silhouette and
two or three value groups that survive at 24x24. Put it on a perfectly flat solid #FF00FF
background. No frame, text, watermark, detached particles, or borrowed design.
```

Both pool Energy icons and the top-panel icon come from one `icon_sheet` call; a single
regeneration uses the pool icon's own spec. The 256x256 `character_energy_large` and 24x24
`character_energy_text` outputs are separate cells normalized from the same theme brief.
Show the user that full energy is five layers rendered in the theme colors at no cost, and
that the two pool icons are separate generated assets, before a paid acquisition route runs.

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

A Rest Site option is a compact opaque scene tile, not a transparent relic icon. Translate
the action title into one immediately readable object or moment and keep the composition
simple enough for the 256x169 button:

```text
Original compact Rest Site action illustration for a deck-building game. Use graphic 2D
painting, broad shapes, clear light-dark separation, and one restrained focal accent.
Show one centered action or object with generous edge clearance in a 3:2 landscape tile.
Use a complete opaque background. No text, numbers, logo, border, UI, card frame,
photorealism, 3D render, pixel art, or transparent cut-out.
```

The role has no shipped style-reference pool yet. `gen_sprite.py` normalizes the result to
256x169 with `cover`; each generated asset still receives normal headed framing review.

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
budget such as four Character cue sheets), the total number of calls, and the worst case if
every asset used both regenerations below. One yes covers
exactly that list; an asset added later needs its own yes. A Character lists only its
chosen tier's slots and cue sheets. A Character run is two batches:
the selection portrait alone first, because every later Character asset uses it as the
identity reference, then the rest after the user has seen the portrait. Do not silently
spend or treat an earlier custom-art preference as approval for an external route. Every
regeneration, including a native-tool regeneration, needs a new confirmation after the user
sees the current result. This is also where the §7.1
"regenerate/tweak this sprite" loop
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
python ${GAME_TOOLS_DIR}/gen_sprite.py import \
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
python ${GAME_TOOLS_DIR}/gen_sprite.py generate \
  --spec card --slug firebolt --prompt "<the filled template above>" \
  --out <mod>/<ModName>/images --backend <name> \
  --reference ${STS2API_SKILL_DIR}/reference/art-samples

# local-image — the user's own file, same normalize + place:
python ${GAME_TOOLS_DIR}/gen_sprite.py import \
  --spec card --slug firebolt --input ./my-art.png --out <mod>/<ModName>/images

# list the contract (script's view — should match the table above):
python ${GAME_TOOLS_DIR}/gen_sprite.py list-specs
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
Character background; portrait for Character selection and the 2x3 Dead cue sheet; square
otherwise. `gen_sprite.py generate` picks the same orientation for a backend unless its
config sets `request_size`.

After a cut-out import, a stdout line starting `[gen_sprite] warning:` means almost none of
the source became transparent: the background was not a flat key color and will show as a
box in game. Regenerate with a flatter background instead of shipping it. Before showing
any imported result to the user, look at the normalized PNG yourself and regenerate an
obvious framing or background failure first; the user still judges style.

`generate` keeps each raw backend source at `<project>/art-sources/generated/<spec>/<slug>.png`,
outside the packed Mod folder. A failed or redone normalization re-imports that file
instead of paying for a second generation. A failed, timed-out, or ambiguous generation
exits nonzero; never resubmit it automatically, because the backend may already have
charged. Offer another route, local import, or placeholder instead.

## Backend config

No backend runs unless the user chose it in the interview. Three built-in names need only
a key the user sets in their own environment, never in the conversation:

| `--backend` | key variable | transport | default model |
|---|---|---|---|
| `openai` | `OPENAI_API_KEY` | `images` at `https://api.openai.com/v1` | `gpt-image-1.5` |
| `gemini` | `GEMINI_API_KEY` | `gemini` at the Gemini API | `gemini-2.5-flash-image` |
| `openrouter` | `OPENROUTER_API_KEY` | `chat` at `https://openrouter.ai/api/v1` | `google/gemini-2.5-flash-image` |

`--model` overrides the model for one call; offer it when the user names a newer model their
account has. A variable the user sets after the agent session started is not visible to it;
the user restarts the session or writes a config entry instead.

Anything else is a named entry in `~/.skill-the-spire/art-backends.json` (or a file named
by `--config` / `$GEN_SPRITE_CONFIG`). The user owns that file. It lives outside every Mod
project and is **never committed — it may hold a key**. Prefer `api_key_env` (the name of a
variable holding the key) over `api_key`, so the file itself holds no secret. An entry
named like a built-in overrides it, and a file with one backend needs no `--backend`:

```json
{ "backends": {
    "my-gateway": { "mode": "images", "base_url": "https://api.example.com/v1",
                    "api_key_env": "MY_GATEWAY_KEY", "model": "<model id>" },
    "local":      { "mode": "command",
                    "command": ["my-image-cli", "--prompt", "{prompt}",
                                "--ratio", "{aspect_ratio}", "--out", "{out_dir}"],
                    "reference_args": ["--image", "{image}"] } } }
```

Before the first paid call, run `gen_sprite.py check --backend <name>` once. It checks the
config shape, that the key is present, and a command backend's executable and `preflight`.
It requests no image, so it costs nothing and does not prove the model will accept the
prompt.

- `images` — the OpenAI *Images* API: `/images/generations`, or multipart `/images/edits`
  with references. OpenAI's gpt-image models and any platform exposing that endpoint.
  The request size follows the spec's orientation. Optional: `edit_url`, `request_size`,
  `timeout`.
- `chat` — the OpenAI *Chat Completions* API returning an image in the reply. Poe,
  OpenRouter, and most "one key, many models" gateways. References are inlined as
  `image_url` data URLs, and the tool parses the image back out of the reply (structured
  image array, inline base64 data URL, or an image link — in that order). Optional:
  `chat_url`, `chat_extra` (merged into the request body, e.g. OpenRouter's
  `modalities`), `timeout`. This transport sends no size; the prompt states the
  orientation.
- `gemini` — the Gemini API's native `generateContent` with image output. References are
  inline image parts, and `imageConfig.aspectRatio` is the closest of `aspect_ratios`.
  Optional: `base_url`, `aspect_ratios`, `timeout`, and `image_size: true` for a model
  that accepts `imageConfig.imageSize` (Gemini 3 image models); it then asks for `2K` on
  event and Character background specs and `1K` otherwise.
- `command` — the user's own CLI, script, or local workflow (for example ComfyUI). The tool
  runs `command` with stdin closed and its output hidden, into a fresh empty `{out_dir}`,
  and requires exactly one image there. Tokens: `{prompt}` (folded to one line for Windows
  `.cmd` shims), `{out_dir}`, `{model}`, `{request_size}`, `{aspect_ratio}` (the
  closest of `aspect_ratios`, default `1:1 2:3 3:2 3:4 4:3 9:16 16:9 21:9`), and
  `{resolution}` (`2K` when the contract's long edge exceeds 1600 px, such as an event
  portrait, else `1K`). Each reference
  appends `reference_args` with `{image}`; without `reference_args`, references are
  skipped. Optional: `model`, `preflight` (commands that must exit 0 first, such as an
  auth check), `timeout` (default 600 seconds).

A missing key, missing or invalid config, or unknown backend name makes `generate` and
`check` fail with a clear message and a non-zero exit, and the caller falls back to the
placeholder.
