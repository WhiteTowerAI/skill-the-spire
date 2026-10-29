# Character art acquisition

Read this page for a playable Character's art step, with `reference/art-contract.md` for the
shared rules: the placeholder mechanism, consent and the regenerate loop, import, and cut-out
cleanup. Every Character slot's spec, output file, size, RitsuLib surface, and real consumer is
in `reference/character-presentation.md` § Profile and consumer matrix; the combat-cue sheet's
grid, play order, timing, and processing are in `reference/character-combat-cues.md`.

Character assets are separate contracts because `CharacterAssetProfile` maps distinct game
hosts. Each profile is promoted independently only after a real headed Character run shows the
packed resource instead of the resolved fallback.

Locked selection and map marker are not in the supported list: resource existence is not
visual proof for those consumers. They are in no art tier and are generated only when the
user names them.

The bundle's `tiers` set the spend the user picks at interview; `export-contract` publishes
each tier's slots, cue choice, and call count as `character_art_tiers` in the catalog.
`minimal` acquires the selection portrait and the body sheet, `standard` every required
static slot, and `full` adds the one cue sheet. A slot outside the chosen tier keeps its
checked fallback: author no wrapper scene or profile path for it.

## Character art sheets

Several same-role slots come from one paid grid image, split by the tool
(`character_art_sheets` in the catalog). One image keeps the cells in one style and, for
bodies, one identity; a real trial kept the same individual across all three bodies.

| sheet | 2x2 cells, reading order | references |
|---|---|---|
| `body_sheet` | combat body, rest body, merchant body, empty | portrait source as identity + two `character_combat` and two `character_rest` style samples |
| `icon_sheet` | top-panel icon, large Energy icon, text Energy icon, empty | `character_icon` style; no portrait |

```powershell
python ../modmaker/scripts/gen_sprite.py generate-sheet --sheet body_sheet `
  --prompt "<sheet prompt>" --out <ModName>/images --backend <name> `
  --reference ../sts2api/reference/art-samples `
  --identity-reference <project>/art-sources/generated/character_select/select.png
python ../modmaker/scripts/gen_sprite.py import-sheet --sheet icon_sheet `
  --input <sheet.png> --out <ModName>/images
```

`generate-sheet` spends one call, splits `--max-refs` (default 4) evenly across the
reference families of the sheet's cells, so the rest cell always sees seated rest
examples, keeps the raw sheet under
`<project>/art-sources/generated/sheets/`, finds each cell's subject over the whole sheet
(drawn grid lines erased; a subject may run past its cell edge, as real bodies' feet do,
and a fixed-grid crop once cut them), crops it with a key-colored margin, and normalizes
it exactly as `import` does for its slot. `import-sheet` does the same
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
bodies use the combat, rest, and merchant cell lines of the body template; the icon is
readable at 88x88; the large Energy icon is readable at 256x256; the text Energy icon is
the same core simplified for 24x24. Models often fill the empty fourth cell anyway; the
split ignores it.

`character_select` uses full-bleed `cover` with chroma off, like the vanilla buttons: the
opaque source fills the whole 132x195 canvas and its edges may crop.
`character_background` remains exact 16:10 `cover` with chroma off. The icon,
marker, static body, and energy profiles use `contain` with chroma on and a flat pure
`#FF00FF` source background (`#00FF00` for a magenta/pink/purple subject; see the key-color
rule under "The card portrait prompt template"). The normalizer writes only loose PNGs; author code creates
the tiny raw `.tscn` wrappers for icon/background/rest/merchant/energy, and `build.py` packs them
without Godot/MegaDot. Full energy references all five layers from that one energy scene.
The optional non-Spine cue contract is limited to the four tabled cues. Cast, Spine,
phobia, trails, animated merchant/rest bodies, and multiplayer views remain outside the art
contract; the Character's sounds follow `reference/audio.md`. Read `reference/character-combat-cues.md` for runtime ownership and fallback.

## CharacterArtBundle and reference routing

`character_art.py` owns one structured `CharacterArtBundle` for every
Character static slot and the one-sheet cue contract. Each static row records
required/optional status, normalized output path,
exact dimensions, alpha policy, checked fallback, real consumer, style-reference family,
fit mode, verification status, and any host-specific visible content box/baseline/public
visual style. `gen_sprite.py` reads this
bundle instead of maintaining a second Character spec table. The optional locked
selection and map-marker rows remain native/shared fallback rows; their presence in the
inventory does not promote those consumers. The cue contract separately owns action order,
sheet rows and grid, frame count/timing, loop/terminal flags, the Idle breath, the
one-call budget, output directories, shared geometry, style, anchors, and static fallback
slot.

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
`character_combat`, `character_rest`, and `character_merchant` acquisitions pass that
portrait's full-resolution source as `--identity-reference`: the kept generated source
`<project>/art-sources/generated/character_select/<slug>.png`, or the user's original file
for an imported portrait. The 132x195 normalized copy is too small to carry the face and
costume. It goes in addition to the type-matched STS2 style references (three for a single
asset, two combat plus two rest for `body_sheet`). Background, top-panel icon, full-energy layers, and large/text Energy-icon
acquisition use a palette/motif brief derived from the user's description and reviewed
selection portrait, but deliberately do not receive the portrait as an image reference.
The `character_cues` sheet is the exception to portrait identity: its anchor is the
approved full-body combat body, `<ModName>/images/charui/combat.png`, passed as
`--identity-reference` and sent first, since every cue must start from that exact figure.

Cue imports stage the sheet at `<project>/art-sources/character-cues/sheet.png`. Runtime cue
files are replaced only when the whole sheet passes key cleanup, grid/component extraction,
edge/body-scale QC, shared scaling, and baseline alignment (`character-combat-cues.md` §
Acquisition and normalization). Review GIFs, the cleaned sheet, a contact sheet, and QC
metadata land under `<project>/art-review/character-cues/`; failed processing leaves prior
runtime cues intact.
The processing techniques are adapted from agent-sprite-forge under MIT, with no runtime
dependency or external asset reuse.

Run the bundle review after the selected required outputs are normalized:

```powershell
python ../modmaker/scripts/character_art.py \
  --images-root <work dir>/<ModName>/images \
  (--tier <minimal|standard|full> | --present-only) \
  [--energy-colors <frame RRGGBB>,<energy outline RRGGBB | auto>] \
  [--number-outlines <EnergyOutlineColor>,<EnergyLabelOutlineColor>] \
  --out-dir <work dir>/art-review
```

Energy numbers are drawn by the game in a fixed cream fill (`#FFF6E2`) with a
Mod-owned outline: the card-pool `EnergyOutlineColor` around the cost on the large card
Energy icon, and the Character `EnergyLabelOutlineColor` around "3/3" on the combat
counter. The rich-text icon never carries a number. Vanilla icon centers are mostly light,
so the outline carries readability; it must reach 6.5:1 against the cream fill and 2.8:1
against the icon center, unless the icon center is dark enough (4.5:1) for the fill alone.
The review measures each icon's center (vanilla Ironclad's for a consumer on its fallback)
and then either checks the two colors given with `--number-outlines` or prints the shade of
the icon's own hue to use. `--energy-colors <frame>,auto` derives `EnergyOutlineColor`
from `energy_large.png`. Copy the reported or derived colors into the Character theme;
never pick these two outlines by eye.

Use `--tier` for generated art (`host-tool` or `backend:<name>`). Use `--present-only` for
`local-image` art that covers only part of the bundle, or for an Energy-only recolor: it
requires every slot of each group already on disk (the icon with its derived outline, all
five Energy layers) and leaves every other slot on its fallback. Pass `--energy-colors`
only when full Energy is selected. The command
validates exact dimensions, alpha policy, readable PNGs, the selected required outputs,
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

## Character prompt templates

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

Static combat/rest/merchant body. The lead and the closing paragraph are shared; a single
`generate --spec` request uses the one pose line for its spec, and the `body_sheet`
request puts the three pose lines into its cell lines after the consistency sentence:

```text
Original full-body character render for a deck-building combat game. The provided STS2
body renders are STYLE ONLY: paint exactly like them, in soft hand-painted 2D with subtle
angular faceted planes, muted slightly desaturated colors, broad value groups, warm key
light from the upper left and cool shadows. Paint with no black ink outlines: every edge
is a soft change of value or color, as in those renders. Use their sturdy stylized
proportions: a strong readable silhouette, with hands, feet, and the signature item
slightly oversized, never spindly. The last provided image, the selection portrait, is
CHARACTER IDENTITY ONLY: copy its face, head covering, hair, costume, colors, and
signature item, but repaint them in the body-render style above, never in the portrait's
inked comic style or close-up framing. Character: <one-sentence identity brief>.

The body is turned toward the right in a 3/4 view and never faces the viewer; the
signature item stays in the character's right hand, the hand nearer the viewer, whenever
it is held.

Combat: combat idle, ready for battle like the STS2 combat references: feet planted wide
apart, knees bent, weight low, chest and face turned toward the right edge so the torso is
seen at a 3/4 angle rather than from the front, the signature item raised and brandished
toward the enemies on the right, the other arm ready; a held pose, not mid-attack.

Rest: resting at the rest site like the STS2 rest references, facing right where the game
scene places its campfire; draw only the character, never the fire, firewood, or ground:
seated low on the ground, knees drawn up with one knee higher than the other, forearms on
the knees, shoulders slumped and head lowered toward the fire, the signature item set down
touching the body; an asymmetric, compact pose about as wide as it is tall, seen from a
slightly raised camera that looks down onto the head and shoulders.

Merchant: visiting a shop: standing relaxed with weight on one leg, the signature item
lowered at the side, head turned slightly right as if browsing wares; calm, not a combat
stance.

Each standing body sits on one baseline and fills about 85-90% of its square's height.
The STS2 renders' soft floor shadows are not part of the style: paint no shadow, contact
shadow, or dark patch under the feet, seat, or body. Use a perfectly flat solid #FF00FF
background with no floor, attack effect, text, UI, watermark, or animation streak. Light
from a held object stays inside the object and on the body: the background right next to
a light source is the same flat #FF00FF, with no glow, bloom, halo, or haze outside the
silhouette. This still is the static fallback body, not a Spine animation frame. Not
photorealistic, not a 3D render, not pixel art, not a comic illustration.
```

The `body_sheet` consistency sentence, placed after the grid paragraph:

```text
All three bodies are the same individual at the same scale, with the head covering, mask,
hair, and costume unchanged in every cell, turned toward the right in a 3/4 view and
never facing the viewer, and the signature item stays in the character's right hand, the
hand nearer the viewer, in every cell where it is held.
```

Each rule answers a failure seen in real trials against the shipped references: the
portrait's ink outlines and flat cel shading leak into the bodies unless the prompt says
to repaint them; "neutral" yields a passive, front-facing stance instead of vanilla's
braced one; a rest pose without the seated rest samples sits on air or sprawls wide; the
word "campfire" alone makes the model paint one; and the vanilla samples' gray floor
shadows come back as a dark key-colored patch that survives the cut-out.

Combat cue sheet (`character_cues`, one call). Fill the `<...>` slots from the Character
SPEC; keep everything else verbatim. Never number the cells in the prompt: a model told the
cells are "numbered" writes the numbers, and they leak into frames.

```text
Original non-Spine combat animation sheet for a deck-building combat game. The FIRST
provided image is the approved full-body combat render of this character and is the ANCHOR
POSE: reproduce exactly this individual, <head covering, clothing, signature item>, colors,
lighting, painted rendering, body proportions, apparent size, and facing in every cell, never
a redesign, variant, costume change, or restyle. The other provided images are STS2 combat
renders and are STYLE ONLY: soft hand-painted 2D with subtle angular faceted planes, muted
colors, warm key light from the upper left and cool shadows, and no black ink outlines;
every edge is a soft change of value or color.

One square image divided into an exact 4x4 grid of sixteen equal square cells, read
left-to-right then top-to-bottom. The cells are empty background apart from the character:
no borders, lines, gutters, labels, letters, numbers, or marks of any kind. Every cell holds
one full-body frame of the same character, fully inside its own cell with clear empty margin
on all sides, at the same size and standing on the same ground line as in every other cell.
The camera is locked: never zoom, crop, pan, or change the viewing angle. Light comes from
the same direction in every cell. Every cell shows a clearly different body position from
its neighbors; only the first cell shows the anchor pose. The <signature item> stays in the
same hand as in the anchor image in every cell.

Row 1, first cell: the exact anchor pose, unchanged.

ATTACK, one continuous <attack with the signature item> at an enemy on the right, in the
next six cells (row 1 cells two to four, then row 2 cells one to three):
- Crouch: knees bent deeper than the anchor, the body lowered, the <signature item> pulled in
  tight against the chest.
- Wind-up: the torso twisted away to the left, the <signature item> swung far back behind the
  hip, the free arm thrown forward for balance.
- Mid-swing: the <signature item> passing in front of the belly at waist height, halfway
  between the wind-up and the strike, the torso turning back toward the right.
- Strike: the <signature item> arm fully extended toward the right at shoulder height, the
  torso leaning into it, the weight on the front foot.
- Follow-through: the arm carried past the strike and upward, the <signature item> raised
  above shoulder height, the body still leaning forward.
- Recovery: the <signature item> arm halfway back toward the chest, the weight returning to
  the center, the knees softening.

HIT, a blow arriving from the right, in the next four cells (row 2 cell four, then row 3
cells one to three):
- Flinch: the head snapped back, the mouth open, the shoulders jerked up.
- Recoil: the torso thrown back and away to the left, the clothing flaring, the back foot
  lifted off the ground.
- Deepest recoil: hunched low with the back foot slid far back, the head turned away, the
  <signature item> held close.
- Steadying: half upright again, the free arm out for balance, the <signature item> still
  held.

DEAD, one collapse in the last five cells (row 3 cell four, then all of row 4); the body
keeps its full size and is only lowered and rotated, and the <signature item> is visible in
every one of these cells:
- Sag: the knees buckling, the head dropping, the <signature item> arm hanging limp.
- Kneel: down on one knee, the torso slumped forward, the <signature item> touching the
  ground.
- Topple: both knees down and tipping forward, the <signature item> slipping out of the hand
  onto the ground beside the body.
- Fall: falling onto one side, the clothing spreading, the <signature item> on the ground
  beside the body.
- Lying still on the ground on one side, the <signature item> on the ground beside the body.

<Any glowing or glass part> is solid and opaque in its own warm color: the background never
shows through it or through any gap in it, and it is never pink, purple, or magenta. Use one
perfectly flat solid pure magenta #FF00FF background (RGB 255,0,255, fully saturated, not
pink or lilac) across the whole sheet: no gradient, floor, ground shadow, glow halo, light
spill, motion streak, attack effect, text, UI, border, logo, or watermark. Do not borrow a
reference character's design. Not photorealistic, not a 3D render, not pixel art, not a
comic illustration.
```

The anchor is the static body, not the selection portrait: the portrait is a head close-up
in an inked style, and real sheets made from it changed stance, line weight, and light
between actions. Each cell names one concrete body position, because a cell described as
"starting to" or "almost back to" another came back as a copy of it. The Hit steadying cell
is a spare that the contract does not play; Hit recovers through Attack's recovery cell.

Reject and regenerate the sheet when the contact-sheet review shows identity, costume,
scale, camera, or baseline drift, drawn numbers or labels, a held item switching hands or
vanishing between cells, or a cell that copies its neighbor. Do not replace this review
with a brittle image-similarity score.

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
