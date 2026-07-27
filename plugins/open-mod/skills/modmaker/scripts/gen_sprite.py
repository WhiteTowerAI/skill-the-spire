#!/usr/bin/env python3
"""Produce a custom STS2 sprite at the exact path + size the game expects.

Two sources, one normalizer (PROJECT.md §7.1 — placeholder-vs-generate is decided
upstream; this tool only runs when the user chose a custom sprite):

  generate  — BYO backend. Reads a provider-agnostic config ({base_url, api_key, model,
              mode}). Two transport shapes chosen by `mode`: "images" (OpenAI Images API,
              /images/generations + /images/edits) or "chat" (OpenAI Chat Completions,
              image returned in the reply — Poe / Gemini-native / OpenRouter). POSTs the
              prompt (+ few-shot references), gets an image back.
  import    — local file. The user already has an image; skip the network.

Both then NORMALIZE + PLACE identically: optional magenta (#FF00FF) chroma-key →
fit/center to the exact contract size (reference/art-contract.md) → write <slug>.png at
the exact sub-path under the mod's images/ dir. Dropping that file in and rebuilding the
  .pck (build.py) is the whole "install a custom sprite" operation — the selected
  framework asset profile resolves it; a missing file falls back to the template default
  (= the placeholder).

We do NOT bundle or default to any provider (§7.1: bring-your-own-backend). No key is
committed. A missing/invalid config makes `generate` fail with a clear message and a
non-zero exit so the caller can fall back to the placeholder.

Cross-platform (Windows/macOS/Linux). Depends on Pillow; HTTP uses stdlib urllib (no
`requests` dep). Quiet output: detail to a .gen_sprite.log next to the output, one
summary line to stdout, and the final image path as the LAST stdout line (callers parse
it — same convention as build.py).

Usage:
  python gen_sprite.py generate --spec card --slug firebolt \
      --prompt "<filled prompt>" --out <mod>/<ModName>/images --config art-backend.json
  python gen_sprite.py import --spec card --slug firebolt \
      --input ./my-art.png --out <mod>/<ModName>/images
  python gen_sprite.py list-specs
"""
from __future__ import annotations

import argparse
import base64
import json
import random
import sys
import urllib.request
import urllib.error
from pathlib import Path

from character_art import CHARACTER_ART_BUNDLE, CharacterArtValidationError

try:
    from PIL import Image, ImageFilter, ImageOps
except ImportError:
    print("[gen_sprite] Pillow is required for the art pipeline. Install it with:\n"
          "  python -m pip install Pillow\n"
          "(It is the only extra dependency beyond the stdlib.)", file=sys.stderr)
    sys.exit(2)

# ---------------------------------------------------------------------------
# The contract. MUST match reference/art-contract.md. sub_path is under images/.
# size = exact (w, h) the game expects. A size of None means we have no measurement at
# all → generate/import refuses without an explicit --size (grounding doctrine: don't
# guess a size as if measured). "verified" = the size + all icon paths have been confirmed
# correct IN-GAME (a live run), not merely source-known. card/relic/power are live-verified:
# card 1000×760 (2026-07-08); relic + power 256×256 (2026-07-08, canary-relic "Bauble" +
# canary-power "Smolder" — bar/status icon, big detail-popup, and power's apply/expire
# notification all render correctly). potion 256×256 also live-verified (2026-07-08,
# canary-potion "Fizz") — RitsuLib's PotionAssetProfile accepts a loose PNG (no
# .tres atlas needed); potion has ONE image texture (no big/), drawn tilted ~45° right.
# Every normal-event portrait slot is a 3440x1613 loose PNG. The initial slot reaches
# EventModel.CreateInitialPortrait through CustomEventModel.CustomInitialPortraitPath;
# authored later-page slots reach the same TextureRect through NEventRoom.SetPortrait.
# The initial contract was live-verified on 2026-07-17, and the reused MapNode run verified
# a second page slot plus missing-phobia fallback and portrait-child cleanup on 2026-07-20.
# enchantment is one 64x64 loose icon. The 2026-07-17 CanaryEnchantment headed run
# observed the same custom resource in both the real NCard enchantment tab and the card's
# hover tooltip, then preserved the attached enchantment's Block behavior.
# orb art has two independent contracts. This spec owns only the loose 100x100 icon used
# by the hover tooltip and NOrb flash particles. CanaryOrb live-verified both consumers on
# 2026-07-17. The persistent combat body is a separate Spine scene and is never emitted by
# this raster normalizer.
# monster is a static-body profile, not an animation contract. RitsuLib renders the loose
# texture one-to-one through RitsuGodotNodeFactories, so the normalized pixel dimensions
# also define the combat/bestiary footprint. RitsuMonsterProof live-verified the 360x360
# texture in both consumers with generated bounds/intent nodes on 2026-07-22.
# fit: "cover"   = fill the whole rect, crop overflow (a full-bleed illustration the
#                  game frames itself, e.g. a card portrait). Opaque.
#      "contain" = fit inside with transparent padding (a cut-out object on a keyed
#                  background, e.g. a relic/power icon on the relic bar).
# chroma: default #FF00FF chroma-key on generate. TRUE for cut-out icons (they need
#         transparency); FALSE for full-bleed illustrations (a card portrait is a full
#         scene filling the frame window, not an object on transparency). Overridable
#         per call with --chroma / --no-chroma.
# ---------------------------------------------------------------------------
# NOTE: RitsuLib's `CardAssetProfile.PortraitPath` resolves
# card_portraits/<slug>.png. A normal card is 1000×760 landscape; 606×852 "full art" is
# Ancient-rarity only
# and we don't make Ancient cards (see reference/art-contract.md).
#
# relic/power/potion: RitsuLib's asset profiles accept loose PNGs and retain checked
# fallbacks. Relic and power use small + big icons; potion uses one 256×256 icon. A relic also
# gets a deterministic `<slug>_outline.png`; a missing outline retains the template fallback.
# Power has NO outline; PotionAssetProfile.OutlinePath stays null with its own fallback.
#
# extra_sub_paths: relic AND power each use TWO loose-PNG profile paths:
#   relic → relics/<slug>.png (relic-bar icon)  +  relics/big/<slug>.png (detail/inspect popup)
#   power → powers/<slug>.png (combat status icon) + powers/big/<slug>.png (the big
#           apply/expire NOTIFICATION popup that jumps out for a few seconds)
# They're separate files (the template ships both <x>.png and big/<x>.png), so writing only
# the small icon leaves the big popup on the placeholder. We write the same normalized image
# to both. `card` writes only its single RitsuLib portrait path.
# potion has only ONE image profile path; the detail/inspect view scales
# that same texture up — there is no separate big/ file — so potion's extra_sub_paths is [].
# enchantment likewise has ONE icon getter. NCard contexts and the hover tooltip reuse the
# same EnchantmentModel.Icon texture, so there is no big/ variant.
# orb likewise has ONE icon getter, but its combat body remains a separate scene contract.
# Character assets stay independent because their RitsuLib profiles feed different consumers. Background,
# rest, and merchant add raw text-scene wrappers after import; full energy uses five layers.
# Static-profile verification is not a claim that a PNG can replace Spine animation.
# Relic and Character top-panel outlines are deterministic opaque-white silhouettes expanded
# from the final normalized main icon alpha. They spend no additional acquisition call.
# Missing files retain RitsuLib's checked fallback. Power has no outline; beta paths stay null.
SPECS: dict[str, dict] = {
    "card":       {"sub_path": "card_portraits",       "extra_sub_paths": [],             "size": (1000, 760), "verified": True,  "fit": "cover",   "chroma": False},
    "relic":      {"sub_path": "relics",               "extra_sub_paths": ["relics/big"], "size": (256, 256),  "verified": True,  "fit": "contain", "chroma": True},
    "power":      {"sub_path": "powers",               "extra_sub_paths": ["powers/big"], "size": (256, 256),  "verified": True,  "fit": "contain", "chroma": True},
    "potion":     {"sub_path": "potions",              "extra_sub_paths": [],             "size": (256, 256),  "verified": True,  "fit": "contain", "chroma": True},
    "event":      {"sub_path": "events",               "extra_sub_paths": [],             "size": (3440, 1613), "verified": True,  "fit": "cover",   "chroma": False},
    "enchantment": {"sub_path": "enchantments",         "extra_sub_paths": [],             "size": (64, 64),    "verified": True,  "fit": "contain", "chroma": True},
    "orb":        {"sub_path": "orbs",                 "extra_sub_paths": [],             "size": (100, 100),  "verified": True,  "fit": "contain", "chroma": True},
    "monster":    {"sub_path": "monsters",             "extra_sub_paths": [],             "size": (360, 360),  "verified": True,  "fit": "contain", "chroma": True},
}
SPECS.update(CHARACTER_ART_BUNDLE.sprite_specs())
FRAGMENT_CLEANUP_SPECS = {"enchantment", "orb", "monster"}
REFERENCE_FAMILIES = CHARACTER_ART_BUNDLE.reference_families()
DERIVED_OUTLINE_SPECS = {"character_icon", "relic"}
OUTLINE_EXPANSION_RATIO = 0.03
OUTLINE_COLOR = (255, 255, 255)


def resolve_size(spec: str, override: tuple[int, int] | None) -> tuple[int, int]:
    info = SPECS[spec]
    if override:
        return override
    if info["size"] is None:
        raise SystemExit(
            f"[gen_sprite] spec '{spec}' has no source-verified size in art-contract.md; "
            f"pass --size WxH explicitly (and confirm it in-game). Refusing to guess.")
    return info["size"]


# --- normalize primitives (magenta chroma-key adapted from agent-sprite-forge,
#     reference/baselines; M6 cut-outs also remove disconnected model debris) ---

def chroma_key_magenta(img: "Image.Image", threshold: int = 100) -> "Image.Image":
    """Make near-#FF00FF pixels transparent. Single pass over RGBA data."""
    img = img.convert("RGBA")
    thr_sq = threshold * threshold
    out = []
    for r, g, b, a in img.getdata():
        # squared distance to pure magenta (255, 0, 255)
        if a != 0 and ((r - 255) ** 2 + g * g + (b - 255) ** 2) < thr_sq:
            out.append((0, 0, 0, 0))
        else:
            out.append((r, g, b, a))
    img.putdata(out)
    return img


def remove_cutout_fragments(img: "Image.Image", alpha_threshold: int = 8) -> "Image.Image":
    """Keep the central subject cluster while dropping disconnected background debris."""
    img = img.convert("RGBA")
    width, height = img.size
    alpha = img.getchannel("A")
    alpha_pixels = alpha.load()
    visited = bytearray(width * height)
    components: list[list[int]] = []

    for y in range(height):
        for x in range(width):
            start = y * width + x
            if visited[start]:
                continue
            visited[start] = 1
            if alpha_pixels[x, y] <= alpha_threshold:
                continue

            component = [start]
            stack = [start]
            while stack:
                index = stack.pop()
                px, py = index % width, index // width
                for ny in range(max(0, py - 1), min(height, py + 2)):
                    for nx in range(max(0, px - 1), min(width, px + 2)):
                        neighbor = ny * width + nx
                        if visited[neighbor]:
                            continue
                        visited[neighbor] = 1
                        if alpha_pixels[nx, ny] > alpha_threshold:
                            component.append(neighbor)
                            stack.append(neighbor)
            components.append(component)

    if len(components) <= 1:
        return img

    canvas_center_x = (width - 1) / 2
    canvas_center_y = (height - 1) / 2
    primary = min(
        components,
        key=lambda component: min(
            ((index % width) - canvas_center_x) ** 2
            + ((index // width) - canvas_center_y) ** 2
            for index in component
        ),
    )
    primary_x = [index % width for index in primary]
    primary_y = [index // width for index in primary]
    left, right = min(primary_x), max(primary_x)
    top, bottom = min(primary_y), max(primary_y)
    padding = max(2, round(max(right - left + 1, bottom - top + 1) * 0.25))
    min_area = max(3, round(len(primary) * 0.01))

    keep = bytearray(width * height)
    for component in components:
        component_x = [index % width for index in component]
        component_y = [index // width for index in component]
        center_x = (min(component_x) + max(component_x)) / 2
        center_y = (min(component_y) + max(component_y)) / 2
        near_subject = (
            left - padding <= center_x <= right + padding
            and top - padding <= center_y <= bottom + padding
        )
        companion = min_area <= len(component) <= len(primary) and near_subject
        if component is primary or companion:
            for index in component:
                keep[index] = 1

    pixels = list(img.getdata())
    img.putdata([
        pixel if keep[index] else (0, 0, 0, 0)
        for index, pixel in enumerate(pixels)
    ])
    return img


def fit_into_rect(img: "Image.Image", size: tuple[int, int], fit: str,
                  fill: float = 1.0, crop_to_content: bool = True) -> "Image.Image":
    """Scale img to the exact contract rect. 'cover' fills and center-crops;
    'contain' fits inside (× fill) on a transparent canvas. Crops to the
    non-transparent bbox first so keyed art centers on the subject."""
    img = img.convert("RGBA")
    if crop_to_content:
        bbox = img.getbbox()
        if bbox:
            img = img.crop(bbox)
    tw, th = size
    sw, sh = img.size
    if sw == 0 or sh == 0:
        return Image.new("RGBA", size, (0, 0, 0, 0))
    if fit == "cover":
        scale = max(tw / sw, th / sh)
    else:  # contain
        scale = min(tw / sw, th / sh) * fill
    nw, nh = max(1, round(sw * scale)), max(1, round(sh * scale))
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    canvas.paste(img, ((tw - nw) // 2, (th - nh) // 2), img)
    return canvas


def fit_into_footprint(img: "Image.Image", size: tuple[int, int], footprint,
                       opaque_canvas: bool) -> "Image.Image":
    """Preserve a source composition inside a host-safe box or bottom-align a cut-out."""
    img = img.convert("RGBA")
    left, top, right, bottom = footprint.content_box
    box_width, box_height = right - left, bottom - top
    if footprint.alpha_content:
        bbox = img.getchannel("A").getbbox()
        if bbox is None:
            raise SystemExit("[gen_sprite] Character combat footprint is empty")
        img = img.crop(bbox)
    if img.width == 0 or img.height == 0:
        raise SystemExit("[gen_sprite] Character visible footprint has no image content")

    if opaque_canvas:
        backdrop = ImageOps.fit(
            img.convert("RGB"), size, Image.Resampling.LANCZOS
        ).filter(ImageFilter.GaussianBlur(radius=max(1, round(min(size) * 0.03))))
        canvas = backdrop.convert("RGBA")
    else:
        canvas = Image.new("RGBA", size, (0, 0, 0, 0))

    scale = min(box_width / img.width, box_height / img.height)
    normalized_size = (
        max(1, round(img.width * scale)),
        max(1, round(img.height * scale)),
    )
    normalized = img.resize(normalized_size, Image.Resampling.LANCZOS)
    x = left + (box_width - normalized.width) // 2
    if footprint.baseline_y is None:
        y = top + (box_height - normalized.height) // 2
    else:
        y = footprint.baseline_y - normalized.height
    canvas.alpha_composite(normalized, (x, y))
    return canvas


def outline_expansion_radius(size: tuple[int, int]) -> int:
    """Use one proportional, integer dilation radius for every supported outline."""
    return max(1, round(min(size) * OUTLINE_EXPANSION_RATIO))


def outline_safe_fill(size: tuple[int, int]) -> float:
    """Reserve one dilation radius on the fitted dimension so the outline is not clipped."""
    minimum = min(size)
    return (minimum - 2 * outline_expansion_radius(size)) / minimum


def derive_alpha_outline(img: "Image.Image") -> "Image.Image":
    """Return a filled white silhouette expanded from every nonzero final-alpha pixel."""
    rgba = img.convert("RGBA")
    source_alpha = rgba.getchannel("A")
    if source_alpha.getbbox() is None:
        raise SystemExit("[gen_sprite] cannot derive an outline from empty final alpha")
    alpha = source_alpha.point(lambda value: 255 if value else 0)
    radius = outline_expansion_radius(rgba.size)
    expanded = alpha.filter(ImageFilter.MaxFilter(radius * 2 + 1))
    outline = Image.new("RGBA", rgba.size, (*OUTLINE_COLOR, 0))
    outline.putalpha(expanded)
    return outline


def normalize_and_place(src: "Image.Image", spec: str, slug: str, out_dir: Path,
                        size: tuple[int, int], do_chroma: bool, fit: str,
                        log) -> Path:
    """The load-bearing step shared by generate + import: key → fit → place."""
    log(f"source size {src.size}, target {size}, chroma={do_chroma}, fit={fit}")
    info = SPECS[spec]
    footprint = info.get("visible_footprint")
    img = src
    if do_chroma:
        threshold = 180 if spec in FRAGMENT_CLEANUP_SPECS else 100
        img = chroma_key_magenta(img, threshold=threshold)
        log("applied magenta chroma-key")
    if footprint is not None:
        img = fit_into_footprint(
            img,
            size,
            footprint,
            opaque_canvas=not footprint.alpha_content,
        )
        log(
            f"applied {footprint.host} content box {footprint.content_box}"
            + (
                f" and baseline {footprint.baseline_y}"
                if footprint.baseline_y is not None
                else ""
            )
        )
    else:
        img = fit_into_rect(
            img,
            size,
            fit,
            fill=outline_safe_fill(size) if spec in DERIVED_OUTLINE_SPECS else 1.0,
            crop_to_content=spec != "character_energy",
        )
    if do_chroma and spec in FRAGMENT_CLEANUP_SPECS:
        img = remove_cutout_fragments(img)
        img = fit_into_rect(img, size, fit)
        log("removed disconnected cut-out background fragments")
    if footprint is not None:
        try:
            alpha_bounds = CHARACTER_ART_BUNDLE.validate_visible_footprint(spec, img)
        except CharacterArtValidationError as exc:
            raise SystemExit(f"[gen_sprite] {exc}") from exc
        if alpha_bounds is not None:
            log(f"validated normalized alpha bounds {alpha_bounds}")
    # write the primary path + any extra paths the game reads for this spec (e.g. a relic's
    # big/ detail-popup icon). The first is returned as the canonical dest.
    dest = None
    for sub in [info["sub_path"], *info.get("extra_sub_paths", [])]:
        dest_dir = out_dir / sub
        dest_dir.mkdir(parents=True, exist_ok=True)
        p = dest_dir / f"{slug}.png"
        img.save(p, "PNG")
        log(f"wrote {p} ({p.stat().st_size:,} bytes) at {img.size}")
        if dest is None:
            dest = p
    if spec in DERIVED_OUTLINE_SPECS:
        outline = derive_alpha_outline(img)
        outline_path = out_dir / info["sub_path"] / f"{slug}_outline.png"
        outline.save(outline_path, "PNG")
        log(
            f"wrote {outline_path} ({outline_path.stat().st_size:,} bytes) at "
            f"{outline.size} with {outline_expansion_radius(outline.size)}px white expansion"
        )
    return dest

# --- BYO backend (OpenAI-images-compatible HTTP) ---------------------------

def load_config(config_path: Path | None) -> dict:
    """Provider-agnostic config: {base_url, api_key, model}. From --config, else
    the GEN_SPRITE_CONFIG env var. NEVER hardcode a provider or a key."""
    import os
    path = config_path or (Path(os.environ["GEN_SPRITE_CONFIG"])
                           if os.environ.get("GEN_SPRITE_CONFIG") else None)
    if not path:
        raise SystemExit(
            "[gen_sprite] no backend config. Pass --config <art-backend.json> or set "
            "GEN_SPRITE_CONFIG. It is provider-agnostic (OpenAI-images-compatible):\n"
            '  {"base_url": "https://api.example.com/v1", "api_key": "...", "model": "..."}\n'
            "We bundle no provider (BYO backend). Falling back to a placeholder is fine.")
    if not path.is_file():
        raise SystemExit(f"[gen_sprite] config not found: {path}")
    cfg = json.loads(path.read_text(encoding="utf-8"))
    missing = [k for k in ("base_url", "api_key", "model") if not cfg.get(k)]
    if missing:
        raise SystemExit(f"[gen_sprite] config missing keys: {', '.join(missing)}")
    # HTTP headers are latin-1; a non-ASCII api_key/base_url is almost always a
    # placeholder left in (e.g. "<your key>", "你的key") or a smart-quote paste.
    for k in ("api_key", "base_url", "model"):
        v = cfg[k]
        if not isinstance(v, str) or not v.isascii():
            raise SystemExit(
                f"[gen_sprite] config '{k}' has non-ASCII characters — this is almost "
                f"always an unfilled placeholder. Put your real backend {k} in {path} "
                f"(ASCII only, no angle brackets).")
    return cfg


def _parse_image_response(payload: dict, cfg: dict, log) -> "Image.Image":
    import io
    try:
        item = payload["data"][0]
    except (KeyError, IndexError, TypeError):
        raise SystemExit(f"[gen_sprite] unexpected backend response shape: {str(payload)[:300]}")
    if item.get("b64_json"):
        raw = base64.b64decode(item["b64_json"])
        log(f"received b64 image ({len(raw):,} bytes)")
        return Image.open(io.BytesIO(raw))
    if item.get("url"):
        log(f"fetching image url {item['url']}")
        return _fetch_image_url(item["url"], cfg)
    raise SystemExit("[gen_sprite] response had neither b64_json nor url")


def call_backend(cfg: dict, prompt: str, size: tuple[int, int], log,
                 references: list[Path] | None = None) -> "Image.Image":
    """Ask the user's BYO backend for an image. Two transport shapes, chosen by the
    config's `mode` (BYO = the config describes the backend; we hardcode no provider):

      mode "images" (default) — the OpenAI *Images* API: POST /images/generations
        (text-to-image) or, with references, multipart /images/edits (few-shot). Used by
        OpenAI gpt-image-1, and gateways that expose that endpoint.
      mode "chat" — the OpenAI *Chat Completions* API returning an image in the reply.
        Used by Poe (api.poe.com), Gemini-native, OpenRouter and most "one key, many
        models" gateways, whose image models live under /chat/completions, NOT /images.

    Raises SystemExit on any failure so the caller can fall back to a placeholder."""
    mode = str(cfg.get("mode", "images")).lower()
    if mode == "chat":
        return _call_backend_chat(cfg, prompt, size, log, references)
    if mode == "images":
        return _call_backend_images(cfg, prompt, size, log, references)
    raise SystemExit(f"[gen_sprite] unknown config mode {mode!r} (use \"images\" or \"chat\")")


def _call_backend_images(cfg: dict, prompt: str, size: tuple[int, int], log,
                         references: list[Path] | None = None) -> "Image.Image":
    """OpenAI Images transport: /images/generations, or /images/edits with references."""
    base = cfg["base_url"].rstrip("/")
    req_size = cfg.get("request_size", "1024x1024")
    if references:
        url = cfg.get("edit_url") or (base + "/images/edits")
        data, ct = _multipart([
            ("model", cfg["model"]), ("prompt", prompt), ("n", "1"), ("size", req_size),
        ], [(f"image[]", p) for p in references])
        headers = {"Content-Type": ct, "Authorization": f"Bearer {cfg['api_key']}"}
        log(f"POST {url} model={cfg['model']} with {len(references)} reference image(s)")
        req = urllib.request.Request(url, data=data, method="POST", headers=headers)
    else:
        url = base + "/images/generations"
        body = json.dumps({"model": cfg["model"], "prompt": prompt, "n": 1,
                           "size": req_size}).encode("utf-8")
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {cfg['api_key']}"}
        log(f"POST {url} model={cfg['model']} (text-to-image)")
        req = urllib.request.Request(url, data=body, method="POST", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=cfg.get("timeout", 180)) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:500]
        raise SystemExit(f"[gen_sprite] backend HTTP {e.code}: {detail}")
    except urllib.error.URLError as e:
        raise SystemExit(f"[gen_sprite] backend unreachable: {e.reason}")
    return _parse_image_response(payload, cfg, log)


def _fetch_image_url(u: str, cfg: dict) -> "Image.Image":
    """Download an image URL into a PIL image. Sends a browser User-Agent — image CDNs
    (Poe's poecdn.net, many others) reject the default `Python-urllib/x.y` UA with 403."""
    import io
    req = urllib.request.Request(u, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
        "Accept": "image/*,*/*;q=0.8",
    })
    with urllib.request.urlopen(req, timeout=cfg.get("timeout", 120)) as r:
        return Image.open(io.BytesIO(r.read()))


def _data_url(path: Path) -> str:
    """Read an image file into a base64 data: URL (for chat image_url content)."""
    import mimetypes
    mime = mimetypes.guess_type(str(path))[0] or "image/png"
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def _extract_image_from_chat(payload: dict, cfg: dict, log) -> "Image.Image":
    """Pull an image out of a /chat/completions reply. Backends return the generated
    image in several shapes — try them in order:
      1. an OpenAI-Images-style `images`/`data` array on the message (b64_json or url),
      2. a base64 data: URL anywhere in the text content,
      3. a plain http(s) image URL / markdown image link in the text content."""
    import io, re
    try:
        msg = payload["choices"][0]["message"]
    except (KeyError, IndexError, TypeError):
        raise SystemExit(f"[gen_sprite] unexpected chat response shape: {str(payload)[:300]}")

    # (1) some gateways attach images as a structured array on the message
    for key in ("images", "data"):
        arr = msg.get(key)
        if isinstance(arr, list) and arr:
            item = arr[0]
            if isinstance(item, dict):
                b64 = item.get("b64_json") or (item.get("image_url", {}) or {}).get("url", "")
                if b64 and b64.startswith("data:"):
                    b64 = b64.split(",", 1)[1]
                if item.get("b64_json"):
                    raw = base64.b64decode(item["b64_json"])
                    log(f"chat: got structured b64 image ({len(raw):,} bytes)")
                    return Image.open(io.BytesIO(raw))
                u = item.get("url") or (item.get("image_url", {}) or {}).get("url")
                if u and not u.startswith("data:"):
                    log(f"chat: fetching structured image url {u}")
                    return _fetch_image_url(u, cfg)

    # content may be a string or a list of content parts
    content = msg.get("content", "")
    if isinstance(content, list):
        content = " ".join(
            (c.get("text", "") if isinstance(c, dict) else str(c)) for c in content)

    # (2) inline base64 data URL
    m = re.search(r"data:image/[^;]+;base64,([A-Za-z0-9+/=\s]+)", content)
    if m:
        raw = base64.b64decode(re.sub(r"\s+", "", m.group(1)))
        log(f"chat: decoded inline base64 image ({len(raw):,} bytes)")
        return Image.open(io.BytesIO(raw))

    # (3) an image URL (bare or markdown ![...](url))
    m = re.search(r"https?://[^\s)\"']+?\.(?:png|jpg|jpeg|webp)", content, re.IGNORECASE)
    if not m:
        m = re.search(r"https?://\S+", content)  # last resort: first URL, let PIL judge
    if m:
        u = m.group(0)
        log(f"chat: fetching image url {u}")
        return _fetch_image_url(u, cfg)

    raise SystemExit(
        "[gen_sprite] chat reply contained no image (no data-URL, image array, or image "
        f"link). First 300 chars: {content[:300]!r}")


def _call_backend_chat(cfg: dict, prompt: str, size: tuple[int, int], log,
                       references: list[Path] | None = None) -> "Image.Image":
    """Chat-Completions transport (Poe, Gemini-native, OpenRouter, …). The prompt is the
    user text; references (few-shot style images) are inlined as image_url data URLs in
    the same user message so the model matches the STS2 look."""
    base = cfg["base_url"].rstrip("/")
    url = cfg.get("chat_url") or (base + "/chat/completions")
    parts: list[dict] = [{"type": "text", "text": prompt}]
    if references:
        for p in references:
            parts.append({"type": "image_url", "image_url": {"url": _data_url(p)}})
    body_obj = {"model": cfg["model"],
                "messages": [{"role": "user", "content": parts}]}
    if cfg.get("chat_extra"):  # backend-specific knobs (e.g. modalities), stays BYO
        body_obj.update(cfg["chat_extra"])
    body = json.dumps(body_obj).encode("utf-8")
    headers = {"Content-Type": "application/json",
               "Authorization": f"Bearer {cfg['api_key']}"}
    nref = len(references) if references else 0
    log(f"POST {url} model={cfg['model']} (chat-completions, {nref} reference image(s))")
    req = urllib.request.Request(url, data=body, method="POST", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=cfg.get("timeout", 180)) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:500]
        raise SystemExit(f"[gen_sprite] backend HTTP {e.code}: {detail}")
    except urllib.error.URLError as e:
        raise SystemExit(f"[gen_sprite] backend unreachable: {e.reason}")
    return _extract_image_from_chat(payload, cfg, log)


def _multipart(fields: list[tuple[str, str]], files: list[tuple[str, Path]]):
    """Minimal multipart/form-data encoder (stdlib only)."""
    import uuid, mimetypes
    boundary = "----gensprite" + uuid.uuid4().hex
    out = bytearray()
    for name, val in fields:
        out += f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n'.encode()
        out += f"{val}\r\n".encode()
    for name, path in files:
        mime = mimetypes.guess_type(str(path))[0] or "image/png"
        out += f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"; filename="{path.name}"\r\n'.encode()
        out += f"Content-Type: {mime}\r\n\r\n".encode()
        out += path.read_bytes() + b"\r\n"
    out += f"--{boundary}--\r\n".encode()
    return bytes(out), f"multipart/form-data; boundary={boundary}"


# --- quiet logging (mirror build.py) ---------------------------------------

def make_logger(out_dir: Path):
    lines: list[str] = []
    def log(msg: str):
        lines.append(str(msg))
    def flush():
        try:
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / ".gen_sprite.log").write_text("\n".join(lines) + "\n", encoding="utf-8")
        except OSError:
            pass
    return log, flush


# --- few-shot reference images ---------------------------------------------

def resolve_references(
    ref_arg: str | None,
    max_refs: int,
    log,
    spec: str | None = None,
    identity_reference: str | None = None,
) -> list[Path] | None:
    """Turn --reference (a dir of style samples, or a comma-separated file list) into a
    randomly capped list of image Paths for the few-shot edit call. Returns None if nothing
    usable is found (caller falls back to plain text-to-image, never blocks).

    Spec-aware subdir selection: different families look nothing alike, so the shipped
    art-samples/ dir is split into per-spec subdirs. When a --reference
    token is a directory that CONTAINS a subdir named after the current --spec, we descend
    into it. A root with no matching subdir contributes only its own direct image files,
    never another family's subdir. A custom flat dir keeps the old behavior."""
    IMG_EXT = (".png", ".jpg", ".jpeg", ".webp")
    def images_in(d: Path) -> list[Path]:
        return [f for f in sorted(d.iterdir()) if f.suffix.lower() in IMG_EXT]

    try:
        identity = CHARACTER_ART_BUNDLE.validate_identity_reference(
            spec or "", Path(identity_reference) if identity_reference else None
        )
    except CharacterArtValidationError as exc:
        raise SystemExit(f"[gen_sprite] {exc}") from exc

    paths: list[Path] = []
    for token in str(ref_arg or "").split(","):
        token = token.strip()
        if not token:
            continue
        p = Path(token)
        if p.is_dir():
            reference_family = REFERENCE_FAMILIES.get(spec, spec) if spec else None
            spec_subdir = (p / reference_family) if reference_family else None
            if spec_subdir and spec_subdir.is_dir():
                imgs = images_in(spec_subdir)
                log(
                    f"reference: using spec subdir {spec_subdir.name}/ "
                    f"for {spec} ({len(imgs)} images)"
                )
                paths.extend(imgs)
            else:
                paths.extend(images_in(p))
        elif p.is_file():
            paths.append(p)
        else:
            log(f"reference not found (skipped): {token}")
    if max_refs and len(paths) > max_refs:
        paths = random.SystemRandom().sample(paths, max_refs)
    paths = list(dict.fromkeys(paths))
    if identity is not None:
        paths.append(identity)
        log(f"identity reference: {identity.name}")
    if not paths:
        log("no usable reference images — falling back to text-to-image")
        return None
    log(f"using {len(paths)} reference image(s): {[p.name for p in paths]}")
    return paths


# --- command handlers -------------------------------------------------------

def cmd_generate(args: argparse.Namespace) -> int:
    out_dir = Path(args.out)
    log, flush = make_logger(out_dir)
    info = SPECS[args.spec]
    size = resolve_size(args.spec, args.size)
    try:
        cfg = load_config(Path(args.config) if args.config else None)
        refs = resolve_references(
            args.reference,
            args.max_refs,
            log,
            spec=args.spec,
            identity_reference=args.identity_reference,
        )
        src = call_backend(cfg, args.prompt, size, log, references=refs)
        # default follows the spec (cut-out icon → key; full-bleed illustration → don't);
        # explicit --chroma / --no-chroma override it.
        do_chroma = info["chroma"]
        if args.chroma:
            do_chroma = True
        if args.no_chroma:
            do_chroma = False
        dest = normalize_and_place(src, args.spec, args.slug, out_dir, size,
                                   do_chroma, info["fit"], log)
    finally:
        flush()
    print(f"[gen_sprite] generated {args.spec} '{args.slug}' -> {dest.name} at {size[0]}x{size[1]}")
    print(str(dest))
    return 0


def cmd_import(args: argparse.Namespace) -> int:
    out_dir = Path(args.out)
    log, flush = make_logger(out_dir)
    info = SPECS[args.spec]
    size = resolve_size(args.spec, args.size)
    src_path = Path(args.input)
    if not src_path.is_file():
        print(f"[gen_sprite] input file not found: {src_path}", file=sys.stderr)
        return 2
    try:
        src = Image.open(src_path)
        # import defaults to NO chroma-key (user's image is assumed already cut),
        # unless they explicitly ask for it with --chroma.
        do_chroma = bool(args.chroma)
        dest = normalize_and_place(src, args.spec, args.slug, out_dir, size,
                                   do_chroma, info["fit"], log)
    finally:
        flush()
    print(f"[gen_sprite] imported {args.spec} '{args.slug}' -> {dest.name} at {size[0]}x{size[1]}")
    print(str(dest))
    return 0


def cmd_list_specs(_args: argparse.Namespace) -> int:
    print("spec        sub-path (under images/)      size         fit      chroma")
    print("----        -------------------------      ----         ---      ------")
    for name, info in SPECS.items():
        size = f'{info["size"][0]}x{info["size"][1]}' if info["size"] else "(unverified)"
        chroma = "on" if info["chroma"] else "off"
        star = "" if info["verified"] else "  *not live-verified"
        print(f'{name:<11} {info["sub_path"]:<30} {size:<12} {info["fit"]:<8} {chroma}{star}')
    if any(not info["verified"] for info in SPECS.values()):
        print("\n* contract is source-grounded but still requires headed in-game proof.")
    return 0


def parse_size(text: str) -> tuple[int, int]:
    try:
        w, h = text.lower().split("x")
        return (int(w), int(h))
    except ValueError:
        raise argparse.ArgumentTypeError(f"size must be WxH, e.g. 1000x760 (got {text!r})")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Produce an STS2 custom sprite at the exact contract path+size.")
    sub = parser.add_subparsers(dest="command", required=True)

    g = sub.add_parser("generate", help="Generate via a BYO OpenAI-compatible backend.")
    g.add_argument("--spec", required=True, choices=sorted(SPECS))
    g.add_argument("--slug", required=True, help="lowercased prefix-stripped id, e.g. firebolt")
    g.add_argument("--prompt", required=True)
    g.add_argument("--out", required=True, help="the mod's <ModName>/images dir")
    g.add_argument("--config", help="art-backend.json (else $GEN_SPRITE_CONFIG)")
    g.add_argument("--size", type=parse_size, help="override WxH (required for unverified specs)")
    g.add_argument("--reference", help="few-shot STS2 style references: a dir (e.g. the "
                   "sts2-api art-samples/) or comma-separated image files. Sent to the "
                   "backend's /images/edits endpoint so output matches the game style. "
                   "Requires a backend that accepts reference images (e.g. gpt-image "
                   "edits or Gemini/nano-banana). Omit → plain text-to-image.")
    g.add_argument("--max-refs", type=int, default=3,
                   help="randomly sample at most three style references; identity is added separately")
    g.add_argument(
        "--identity-reference",
        help="normalized Character selection portrait; required for identity-sensitive body/cue assets",
    )
    g.add_argument("--chroma", action="store_true", help="force the #FF00FF chroma-key on (default: per-spec)")
    g.add_argument("--no-chroma", action="store_true", help="force the #FF00FF chroma-key off (default: per-spec)")
    g.set_defaults(func=cmd_generate)

    i = sub.add_parser("import", help="Normalize + place a local image (no HTTP).")
    i.add_argument("--spec", required=True, choices=sorted(SPECS))
    i.add_argument("--slug", required=True)
    i.add_argument("--input", required=True, help="path to the source image")
    i.add_argument("--out", required=True, help="the mod's <ModName>/images dir")
    i.add_argument("--size", type=parse_size, help="override WxH (required for unverified specs)")
    i.add_argument("--chroma", action="store_true", help="apply the #FF00FF chroma-key (default off for import)")
    i.set_defaults(func=cmd_import)

    ls = sub.add_parser("list-specs", help="Print the sprite contract (path+size per spec).")
    ls.set_defaults(func=cmd_list_specs)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()


