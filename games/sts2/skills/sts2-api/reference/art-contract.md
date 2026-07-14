# art-contract.md — where a custom sprite must land, and at what size

> **The art source of truth.** When a mod ships a custom sprite (a card portrait, a
> relic icon, …) the image only shows up in-game if it lands at the **exact path** the
> template's base class resolves AND is the **exact pixel size** the game expects. This
> page is the single place that records both. `tools/gen_sprite.py` reads the same
> contract; keep them in sync.
>
> **How the placeholder mechanism works (read this first).** The scaffolded base
> classes resolve each sprite path with a `ResourceLoader.Exists(path)` check and, if
> the file is absent, **fall back to a template default** (`card.png`, `relic.png`, …).
> So "use a placeholder" = *do nothing* — the fallback fires and the mod loads on the
> default art. "Generate/import a custom sprite" = drop the correctly-named PNG at the
> path below and rebuild the `.pck`. That is the entire operation; there is no
> registration step. Verified against a scaffolded mod's
> `<ModName>Code/Extensions/StringExtensions.cs`.
>
> **Sizes derived from MegaCrit content** (via the decompile / existing snapshots) —
> © Mega Crit. Only the *contract* (path + size) is distilled here; no game asset ships.

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

**A relic and a power each need TWO files; a potion needs ONE (`gen_sprite.py` handles the
count automatically).** Confirmed live (canary-relic "Bauble" + canary-power "Smolder" +
canary-potion "Fizz", 2026-07-08). relic/power read the icon from two separate loose-PNG
getters — writing only the first leaves the other on the placeholder:
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
`gen_sprite.py` writes the same normalized image to every path a spec needs, so you don't
manage them by hand. (`card`'s outer `card_portraits/<slug>.png` is dead code under BaseLib —
only `big/` is written.)

**Why all three take a loose `.png` (no `.tres` authoring).** Vanilla STS2 loads every icon
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

**Sizes.** All 324 vanilla relic + 271 power + 63 potion icons extracted from the game are a
uniform **256×256**; live canary runs confirmed that size + all icon paths render correctly,
so relic/power/potion are all `verified: True`. `card` is 1000×760, also live-verified
(2026-07-08).

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

**Layer 2 — few-shot reference images (when the backend supports them, much stronger).**
Pass `--reference <sts2-api>/reference/art-samples` to `gen_sprite.py generate` — always
the **root** samples dir, not a subdir. That dir is split into `card/` (18 portraits),
`relic/` (6 icons), `power/` (6 icons), and `potion/` (6 icons), and the tool
**auto-selects the subdir matching `--spec`** so a relic run never gets card portraits
(they look nothing alike — mixing them poisons the style). It sends up to `--max-refs` (default 3, even stride to
span styles) to the backend's `/images/edits` endpoint so the model imitates the game's
look directly. This needs a backend that accepts reference images (e.g. gpt-image-1 edits,
Gemini / nano-banana, ComfyUI IPAdapter). Plain text-to-image backends ignore references —
Layer 1 carries them. (All © Mega Crit, reference-only — see `art-samples/ATTRIBUTION.md`.
If they're removed, Layer 1 still works.)

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
  magenta trick is for the cut-out specs (`relic` / `power` / `potion`, `fit: contain`,
  chroma ON) that sit transparent on the relic/potion bar — for those, add "solid flat
  magenta (#FF00FF) background, no gradient" to the prompt. Force keying on a card with
  `--chroma` only if you deliberately want to cut a magenta-backed portrait out.
- **Subject centered, generous margin**, so the `cover` crop keeps the subject in frame.
- **One image per call.** `gen_sprite.py` requests `n=1` and keeps that single result —
  there is no batch-and-pick. If it's not right, *regenerate*: tweak segment ② and re-run
  (the regenerate loop below). One at a time, judged by eye.

**Icon-spec subject shape (relic / power / potion).** These are a single cut-out object,
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

## Confirm the prompt before spending, and the regenerate loop

Generating calls the user's paid API or managed-credit CLI. So **before every paid
generation, disclose the model/backend, output count (one), and credit-spending action.
Use the
assembled prompt** (segments ①②③ concatenated) and the subject you derived, and get a
quick yes — one line, e.g. *"I'll generate the portrait with this prompt: … — go ahead?"*
Don't silently spend or treat an earlier custom-art preference as approval. Every
regeneration needs a new confirmation. This is also where the §7.1
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

## Using the tool

```
# managed credits — Vofy is acquisition only. The user installs/logs in themselves;
# preflight prints no account/credit details. Inspect live model capabilities separately:
python ${GAME_TOOLS_DIR}/acquire_sprite.py preflight --model <chosen-model>
vofy models <chosen-model>

# after explicit approval for this prompt/model/one-image spend. Add --reference only
# when the live model guide supports image inputs; repeat it at most three times:
python ${GAME_TOOLS_DIR}/acquire_sprite.py create \
  --spec card --slug firebolt --prompt "<the filled template above>" \
  --out <mod>/<ModName>/images --model <chosen-model> \
  --aspect-ratio <confirmed-ratio> [--reference <sample.png> ...] --yes

# generate (BYO backend) — POSTs the prompt (+ few-shot STS2 style references when the
# backend supports them), then fits + resizes to the contract size + places it:
python ${GAME_TOOLS_DIR}/gen_sprite.py generate \
  --spec card --slug firebolt --prompt "<the filled template above>" \
  --out <mod>/<ModName>/images --config <path to art-backend.json> \
  --reference ${STS2_API_SKILL_DIR}/reference/art-samples

# import (local file) — same normalize + place, no HTTP:
python ${GAME_TOOLS_DIR}/gen_sprite.py import \
  --spec card --slug firebolt --input ./my-art.png --out <mod>/<ModName>/images

# list the contract (script's view — should match the table above):
python ${GAME_TOOLS_DIR}/gen_sprite.py list-specs
```

`acquire_sprite.py` never installs Vofy, runs `vofy login`, reads credentials, records
status/credit output, or parses Vofy's normal stdout for a result filename. It runs one
synchronous `vofy image create --yes --n 1` into a unique empty temporary directory,
requires exactly one downloaded image, and invokes `gen_sprite.py import` for the real
crop/fit/chroma/path contract. For relic/power/potion it supplies import's `--chroma`
automatically. Before crossing a Windows/npm `.cmd` shim it folds all prompt whitespace
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
