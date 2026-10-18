#!/usr/bin/env python3
"""Normalize four Character action sheets into one all-or-nothing cue bundle.

Frame extraction, magenta cleanup, connected-component selection, shared scaling,
bottom alignment, edge-touch QC, and GIF preview techniques are adapted from
agent-sprite-forge's ``generate2dsprite.py``.

MIT License

Copyright (c) 2026 0x0funky

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from __future__ import annotations

import argparse
from collections import deque
from dataclasses import dataclass
import json
from pathlib import Path
import shutil
import statistics
import tempfile
from typing import Iterable

from PIL import Image, ImageDraw, ImageFilter, ImageFont
from character_art import CHARACTER_ART_BUNDLE


CUE_CONTRACT = CHARACTER_ART_BUNDLE.combat_cues
if CUE_CONTRACT is None:
    raise RuntimeError("CharacterArtBundle has no combat cue contract")

FRAME_SIZE = CUE_CONTRACT.frame_size
CONTENT_BOX = CUE_CONTRACT.content_box
BASELINE_Y = CUE_CONTRACT.baseline_y
# A delivered sheet that does not divide into whole cells but is within this relative aspect
# error of its grid is resampled to the exact grid size; anything further off is the wrong
# shape and fails.
SHEET_ASPECT_TOLERANCE = 0.02
# Fraction of each cell trimmed from every edge before keying, to drop drawn grid lines
# (the same inset gen_sprite uses for Character art sheets).
CELL_INSET = 0.016
ACTION_CONTRACT = {
    action.name: {
        "state_name": action.state_name,
        "source_spec": action.source_spec,
        "rows": action.rows,
        "cols": action.columns,
        "duration_ms": action.frame_duration_ms,
        "loop": action.loop,
        "terminal": action.terminal,
        "output_dir": action.output_dir,
        "generation_calls": action.generation_calls,
    }
    for action in CUE_CONTRACT.actions
}


class CharacterCueError(ValueError):
    """Raised when an action sheet cannot satisfy the cue bundle contract."""


@dataclass(frozen=True)
class Component:
    area: int
    bbox: tuple[int, int, int, int]
    pixels: tuple[int, ...]


@dataclass(frozen=True)
class ExtractedFrame:
    action: str
    index: int
    image: Image.Image
    source_box: tuple[int, int, int, int]
    source_bbox: tuple[int, int, int, int]
    selected_area: int
    component_count: int


# Cut-out sources sit on flat magenta by default. A subject that itself uses magenta,
# pink, or purple is drawn on flat green instead, or keying eats the subject.
KEY_COLORS = {"magenta": (255, 0, 255), "green": (0, 255, 0)}


def _key_distance_sq(pixel: tuple[int, int, int], key: tuple[int, int, int]) -> int:
    return sum((channel - target) ** 2 for channel, target in zip(pixel, key))


def detect_key_color(image: Image.Image, threshold: int = 100) -> str:
    """Name the key color the source background uses, read from its border pixels."""
    rgb = image.convert("RGB")
    pixels = rgb.load()
    width, height = rgb.size
    border = [pixels[x, y] for x in range(width) for y in (0, height - 1)]
    border += [pixels[x, y] for y in range(height) for x in (0, width - 1)]
    threshold_sq = threshold * threshold
    green = sum(_key_distance_sq(p, KEY_COLORS["green"]) < threshold_sq for p in border)
    magenta = sum(_key_distance_sq(p, KEY_COLORS["magenta"]) < threshold_sq for p in border)
    return "green" if green > magenta else "magenta"


def remove_key_color(
    image: Image.Image,
    threshold: int = 100,
    edge_threshold: int = 200,
    key: str = "magenta",
) -> Image.Image:
    """Remove the solid key color, then flood the softer key color inward from edges."""
    image = image.convert("RGBA")
    pixels = image.load()
    width, height = image.size
    threshold_sq = threshold * threshold
    edge_threshold_sq = edge_threshold * edge_threshold
    key_rgb = KEY_COLORS[key]

    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            if a and _key_distance_sq((r, g, b), key_rgb) < threshold_sq:
                pixels[x, y] = (0, 0, 0, 0)

    queue: deque[tuple[int, int]] = deque()
    for x in range(width):
        queue.append((x, 0))
        queue.append((x, height - 1))
    for y in range(height):
        queue.append((0, y))
        queue.append((width - 1, y))

    visited = bytearray(width * height)
    while queue:
        x, y = queue.popleft()
        if not (0 <= x < width and 0 <= y < height):
            continue
        flat_index = y * width + x
        if visited[flat_index]:
            continue
        visited[flat_index] = 1

        r, g, b, a = pixels[x, y]
        removable = a == 0 or _key_distance_sq((r, g, b), key_rgb) < edge_threshold_sq
        if not removable:
            continue
        if a:
            pixels[x, y] = (0, 0, 0, 0)
        queue.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
    return image


def despill_edges(image: Image.Image, key: str = "magenta", band: int = 2) -> Image.Image:
    """Neutralize key-colored spill on the visible pixels within `band` px of transparency.
    Antialiased edges blend the subject (often a dark ink line) with the key; distance keying
    cannot remove those without eating real dark pixels, and left alone they draw a magenta
    (or green) rim around the cut-out on dark game UI."""
    image = image.convert("RGBA")
    alpha = image.getchannel("A").point(lambda a: 255 if a else 0)
    eroded = alpha.filter(ImageFilter.MinFilter(2 * band + 1))
    pixels = image.load()
    alpha_pixels, eroded_pixels = alpha.load(), eroded.load()
    for y in range(image.height):
        for x in range(image.width):
            if not alpha_pixels[x, y] or eroded_pixels[x, y]:
                continue
            r, g, b, a = pixels[x, y]
            if key == "green":
                spill = g - max(r, b)
                if spill > 0:
                    pixels[x, y] = (r, g - spill, b, a)
            else:
                spill = min(r, b) - g
                if spill > 0:
                    pixels[x, y] = (r - spill, g, b - spill, a)
    return image


def key_cell(
    cell: Image.Image,
    key: str = "magenta",
    threshold: int = 100,
    edge_threshold: int = 200,
) -> Image.Image:
    """Key one grid cell on its own. Models draw dark grid lines between cells; keying the
    whole sheet lets those lines wall off the edge flood, so a cell's noisy off-key
    background survived as one cell-sized component in a real 2K sheet. Despill matches
    static Character bodies: without it, 56-80% of the visible rim of real frames stayed
    magenta-tinted ink."""
    return despill_edges(remove_key_color(cell, threshold, edge_threshold, key), key)


def connected_components(image: Image.Image, alpha_threshold: int = 8) -> list[Component]:
    alpha = image.getchannel("A")
    pixels = alpha.load()
    width, height = image.size
    visited = bytearray(width * height)
    components: list[Component] = []

    for y in range(height):
        for x in range(width):
            start = y * width + x
            if visited[start] or pixels[x, y] <= alpha_threshold:
                visited[start] = 1
                continue

            visited[start] = 1
            queue = deque([start])
            members: list[int] = []
            min_x = max_x = x
            min_y = max_y = y
            while queue:
                current = queue.popleft()
                cx, cy = current % width, current // width
                members.append(current)
                min_x, max_x = min(min_x, cx), max(max_x, cx)
                min_y, max_y = min(min_y, cy), max(max_y, cy)
                for ny in range(max(0, cy - 1), min(height, cy + 2)):
                    for nx in range(max(0, cx - 1), min(width, cx + 2)):
                        neighbor = ny * width + nx
                        if visited[neighbor]:
                            continue
                        visited[neighbor] = 1
                        if pixels[nx, ny] > alpha_threshold:
                            queue.append(neighbor)

            components.append(Component(
                area=len(members),
                bbox=(min_x, min_y, max_x + 1, max_y + 1),
                pixels=tuple(members),
            ))

    return sorted(components, key=lambda component: component.area, reverse=True)


def _largest_component_image(image: Image.Image) -> tuple[Image.Image, Component, int]:
    """The body plus its detached companions (same rule as static Character cut-outs).

    A held item often separates from the body after keying (a thin handle, a dropped
    lantern); keeping only the largest component made a real lantern blink out of 7 of 32
    frames. Companions are components of at least 1% of the body's area whose center lies
    within the body's bounds padded by 25%; smaller or farther ones are debris.
    """
    components = connected_components(image)
    if not components:
        raise CharacterCueError("frame is empty after key-color cleanup")
    body = components[0]
    left, top, right, bottom = body.bbox
    padding = max(2, round(max(right - left, bottom - top) * 0.25))
    min_area = max(3, round(body.area * 0.01))
    kept = [body] + [
        component for component in components[1:]
        if component.area >= min_area
        and left - padding <= (component.bbox[0] + component.bbox[2]) / 2 <= right + padding
        and top - padding <= (component.bbox[1] + component.bbox[3]) / 2 <= bottom + padding
    ]
    selected = Component(
        area=sum(component.area for component in kept),
        bbox=(
            min(component.bbox[0] for component in kept),
            min(component.bbox[1] for component in kept),
            max(component.bbox[2] for component in kept),
            max(component.bbox[3] for component in kept),
        ),
        pixels=tuple(pixel for component in kept for pixel in component.pixels),
    )
    mask = Image.new("L", image.size, 0)
    mask_pixels = mask.load()
    for flat_index in selected.pixels:
        mask_pixels[flat_index % image.width, flat_index // image.width] = 255
    isolated = Image.new("RGBA", image.size, (0, 0, 0, 0))
    isolated.paste(image, (0, 0), mask)
    return isolated.crop(selected.bbox), selected, len(components)


def extract_action(
    action: str,
    source_path: Path,
    threshold: int = 100,
    edge_threshold: int = 200,
) -> tuple[Image.Image, list[ExtractedFrame]]:
    contract = ACTION_CONTRACT[action]
    try:
        with Image.open(source_path) as source:
            source.verify()
        with Image.open(source_path) as source:
            raw = source.convert("RGBA")
    except (OSError, ValueError, SyntaxError) as exc:
        raise CharacterCueError(f"{action} sheet is not a readable image: {source_path} ({exc})") from exc

    rows, cols = contract["rows"], contract["cols"]
    expected = (cols * FRAME_SIZE[0], rows * FRAME_SIZE[1])
    if (raw.width % cols or raw.height % rows) and abs(
        (raw.width / raw.height) / (expected[0] / expected[1]) - 1
    ) <= SHEET_ASPECT_TOLERANCE:
        # Backends round non-square canvases to their own sizes (Gemini returns 2:3 as
        # 848x1264), so a right-shaped sheet rarely divides into whole cells as delivered.
        raw = raw.resize(expected, Image.Resampling.LANCZOS)
    if raw.width % cols or raw.height % rows:
        # Name the axes. A bare "NxM" grid reads as WxH to anyone who just produced the
        # sheet, which is the opposite order, and that ambiguity is how a wrong-shaped
        # sheet gets requested in the first place.
        raise CharacterCueError(
            f"{action} sheet size {raw.width}x{raw.height} is not divisible by its "
            f"{cols} cols x {rows} rows grid "
            f"(expected {cols * 512}x{rows * 512})"
        )
    key = detect_key_color(raw)
    cleaned = Image.new("RGBA", raw.size, (0, 0, 0, 0))
    cell_width, cell_height = raw.width // cols, raw.height // rows
    inset = max(4, round(min(cell_width, cell_height) * CELL_INSET))
    cell_width, cell_height = cell_width - 2 * inset, cell_height - 2 * inset
    frames: list[ExtractedFrame] = []
    for index in range(rows * cols):
        row, column = divmod(index, cols)
        source_box = (
            column * (cell_width + 2 * inset) + inset,
            row * (cell_height + 2 * inset) + inset,
            (column + 1) * (cell_width + 2 * inset) - inset,
            (row + 1) * (cell_height + 2 * inset) - inset,
        )
        cell = key_cell(raw.crop(source_box), key, threshold, edge_threshold)
        cleaned.paste(cell, source_box[:2])
        subject, selected, component_count = _largest_component_image(cell)
        left, top, right, bottom = selected.bbox
        if left <= 0 or top <= 0 or right >= cell_width or bottom >= cell_height:
            raise CharacterCueError(
                f"{action} frame {index:02d} touches its {cell_width}x{cell_height} cell edge: "
                f"{selected.bbox}"
            )
        frames.append(ExtractedFrame(
            action=action,
            index=index,
            image=subject,
            source_box=source_box,
            source_bbox=selected.bbox,
            selected_area=selected.area,
            component_count=component_count,
        ))
    return cleaned, frames


def _validate_body_scale(frames_by_action: dict[str, list[ExtractedFrame]]) -> dict[str, float]:
    idle_height = statistics.median(frame.image.height for frame in frames_by_action["idle"])
    if idle_height <= 0:
        raise CharacterCueError("idle frames have no measurable body height")

    ratios: dict[str, float] = {}
    for action, frames in frames_by_action.items():
        action_height = statistics.median(frame.image.height for frame in frames)
        ratios[action] = action_height / idle_height

    for action in ("attack", "hit"):
        if not 0.85 <= ratios[action] <= 1.15:
            raise CharacterCueError(
                f"{action} median body height is {ratios[action]:.3f}x Idle; expected 0.85..1.15"
            )
    return ratios


def normalize_frames(
    frames_by_action: dict[str, list[ExtractedFrame]],
) -> tuple[dict[str, list[Image.Image]], dict[str, list[dict]], float, dict[str, float]]:
    ratios = _validate_body_scale(frames_by_action)
    all_frames = [frame for frames in frames_by_action.values() for frame in frames]
    # Keep each frame's horizontal place in its cell (one shared transform) instead of
    # centering every frame on its own bounds: re-centering slid real Attack/Hit frames up
    # to ~30 px against each other whenever a limb or the weapon reached out.
    union_left = min(frame.source_bbox[0] for frame in all_frames)
    union_right = max(frame.source_bbox[2] for frame in all_frames)
    max_height = max(frame.image.height for frame in all_frames)
    box_width = CONTENT_BOX[2] - CONTENT_BOX[0]
    box_height = CONTENT_BOX[3] - CONTENT_BOX[1]
    global_scale = min(box_width / (union_right - union_left), box_height / max_height)
    offset_x = (
        CONTENT_BOX[0]
        + (box_width - (union_right - union_left) * global_scale) / 2
        - union_left * global_scale
    )

    normalized: dict[str, list[Image.Image]] = {}
    metadata: dict[str, list[dict]] = {}
    for action, frames in frames_by_action.items():
        normalized[action] = []
        metadata[action] = []
        for frame in frames:
            new_width = max(1, round(frame.image.width * global_scale))
            new_height = max(1, round(frame.image.height * global_scale))
            resized = frame.image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            paste_x = min(
                max(CONTENT_BOX[0], round(offset_x + frame.source_bbox[0] * global_scale)),
                CONTENT_BOX[2] - new_width,
            )
            paste_y = BASELINE_Y - new_height
            canvas = Image.new("RGBA", FRAME_SIZE, (0, 0, 0, 0))
            canvas.paste(resized, (paste_x, paste_y), resized)
            alpha_bbox = canvas.getchannel("A").getbbox()
            if alpha_bbox is None:
                raise CharacterCueError(f"{action} frame {frame.index:02d} became empty")
            if (
                alpha_bbox[0] < CONTENT_BOX[0]
                or alpha_bbox[1] < CONTENT_BOX[1]
                or alpha_bbox[2] > CONTENT_BOX[2]
                or alpha_bbox[3] != BASELINE_Y
            ):
                raise CharacterCueError(
                    f"{action} frame {frame.index:02d} normalized outside the shared footprint: {alpha_bbox}"
                )
            normalized[action].append(canvas)
            metadata[action].append({
                "index": frame.index,
                "source_box": list(frame.source_box),
                "selected_component_bbox": list(frame.source_bbox),
                "selected_component_area": frame.selected_area,
                "component_count": frame.component_count,
                "output_size": [new_width, new_height],
                "paste_position": [paste_x, paste_y],
                "alpha_bbox": list(alpha_bbox),
                "output_path": f"{ACTION_CONTRACT[action]['output_dir']}/{frame.index:02d}.png",
            })
    return normalized, metadata, global_scale, ratios


def save_transparent_gif(frames: list[Image.Image], path: Path, duration_ms: int) -> None:
    key = (255, 0, 254)
    width, height = frames[0].size
    stacked = Image.new("RGB", (width, height * len(frames)), key)
    for index, frame in enumerate(frames):
        rgb = frame.convert("RGB")
        mask = frame.getchannel("A").point(lambda value: 255 if value >= 128 else 0)
        stacked.paste(rgb, (0, index * height), mask)

    paletted = stacked.convert("P", palette=Image.Palette.ADAPTIVE, colors=256,
                               dither=Image.Dither.NONE)
    palette = list(paletted.getpalette() or [])
    palette.extend([0] * (768 - len(palette)))
    key_index = min(
        range(256),
        key=lambda index: sum(
            (palette[index * 3 + channel] - key[channel]) ** 2 for channel in range(3)
        ),
    )
    if key_index != 0:
        lookup = list(range(256))
        lookup[0], lookup[key_index] = key_index, 0
        paletted = paletted.point(lookup)
        for channel in range(3):
            zero = channel
            keyed = key_index * 3 + channel
            palette[zero], palette[keyed] = palette[keyed], palette[zero]
        paletted.putpalette(palette)

    gif_frames = [
        paletted.crop((0, index * height, width, (index + 1) * height))
        for index in range(len(frames))
    ]
    gif_frames[0].save(
        path,
        "GIF",
        save_all=True,
        append_images=gif_frames[1:],
        duration=duration_ms,
        loop=0,
        disposal=2,
        transparency=0,
        background=0,
    )


def _checkerboard(size: tuple[int, int], tile: int = 16) -> Image.Image:
    image = Image.new("RGBA", size, "#d5d8dc")
    draw = ImageDraw.Draw(image)
    for y in range(0, size[1], tile):
        for x in range(0, size[0], tile):
            if (x // tile + y // tile) % 2:
                draw.rectangle((x, y, x + tile - 1, y + tile - 1), fill="#aeb4bb")
    return image


def render_contact_sheet(frames_by_action: dict[str, list[Image.Image]]) -> Image.Image:
    cell = 180
    label_height = 24
    columns = max(len(frames) for frames in frames_by_action.values())
    sheet = Image.new("RGB", (columns * cell, len(ACTION_CONTRACT) * (cell + label_height)), "#20252b")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for row, (action, frames) in enumerate(frames_by_action.items()):
        y = row * (cell + label_height)
        for column, frame in enumerate(frames):
            preview = frame.resize((cell, cell), Image.Resampling.LANCZOS)
            tile = _checkerboard((cell, cell))
            tile.alpha_composite(preview)
            sheet.paste(tile.convert("RGB"), (column * cell, y + label_height))
            draw.text((column * cell + 6, y + 6), f"{action} {column:02d}", fill="white", font=font)
    return sheet


def _replace_directory(source: Path, destination: Path) -> None:
    backup = destination.with_name(f".{destination.name}.backup")
    if backup.exists():
        raise CharacterCueError(f"stale cue backup blocks install: {backup}")
    if destination.exists():
        destination.rename(backup)
    try:
        source.rename(destination)
    except Exception:
        if backup.exists() and not destination.exists():
            backup.rename(destination)
        raise
    else:
        if backup.exists():
            shutil.rmtree(backup)


def process_bundle(
    sources: dict[str, Path],
    images_root: Path,
    review_dir: Path,
    threshold: int = 100,
    edge_threshold: int = 200,
) -> dict:
    missing = [action for action in ACTION_CONTRACT if action not in sources]
    if missing:
        raise CharacterCueError(f"missing action sheet(s): {', '.join(missing)}")

    cleaned_sheets: dict[str, Image.Image] = {}
    extracted: dict[str, list[ExtractedFrame]] = {}
    for action in ACTION_CONTRACT:
        cleaned, frames = extract_action(
            action,
            Path(sources[action]),
            threshold=threshold,
            edge_threshold=edge_threshold,
        )
        cleaned_sheets[action] = cleaned
        extracted[action] = frames

    normalized, frame_metadata, global_scale, ratios = normalize_frames(extracted)
    metadata = {
        "contract": "skill-the-spire-character-cues/v1",
        "processor_source": "agent-sprite-forge techniques, adapted under MIT",
        "frame_size": list(FRAME_SIZE),
        "content_box": list(CONTENT_BOX),
        "baseline_y": BASELINE_Y,
        "global_scale": global_scale,
        "body_height_ratio_to_idle": ratios,
        "generation_calls": CUE_CONTRACT.generation_calls,
        "fallback_slot": CUE_CONTRACT.fallback_slot,
        "consumer": CUE_CONTRACT.consumer,
        "visual_style": {
            "scale": CUE_CONTRACT.visual_scale,
            "position": list(CUE_CONTRACT.visual_position),
        },
        "anchors": {
            "bounds_position": list(CUE_CONTRACT.bounds_position),
            "bounds_size": list(CUE_CONTRACT.bounds_size),
            "intent_position": list(CUE_CONTRACT.intent_position),
            "center_position": list(CUE_CONTRACT.center_position),
            "orb_position": list(CUE_CONTRACT.orb_position),
            "talk_position": list(CUE_CONTRACT.talk_position),
        },
        "actions": {},
    }
    for action, contract in ACTION_CONTRACT.items():
        metadata["actions"][action] = {
            **contract,
            "source": str(Path(sources[action]).resolve()),
            "frame_order": list(range(len(normalized[action]))),
            "frames": frame_metadata[action],
        }

    images_root = images_root.resolve()
    review_dir = review_dir.resolve()
    charui_root = images_root / "charui"
    charui_root.mkdir(parents=True, exist_ok=True)
    review_dir.parent.mkdir(parents=True, exist_ok=True)
    stage_root = Path(tempfile.mkdtemp(prefix="skill-the-spire-cues-", dir=charui_root))
    stage_review = Path(tempfile.mkdtemp(prefix="skill-the-spire-cue-review-", dir=review_dir.parent))
    try:
        for action, frames in normalized.items():
            action_dir = stage_root / action
            action_dir.mkdir(parents=True)
            for index, frame in enumerate(frames):
                frame.save(action_dir / f"{index:02d}.png", "PNG", optimize=True)

            action_review = stage_review / action
            action_review.mkdir(parents=True)
            cleaned_sheets[action].save(action_review / "raw-sheet-clean.png", "PNG", optimize=True)
            save_transparent_gif(
                frames,
                action_review / "animation.gif",
                ACTION_CONTRACT[action]["duration_ms"],
            )

        render_contact_sheet(normalized).save(
            stage_review / "character-cues-contact-sheet.png", "PNG", optimize=True
        )
        (stage_review / "pipeline-meta.json").write_text(
            json.dumps(metadata, indent=2), encoding="utf-8"
        )
        _replace_directory(stage_root, charui_root / "cues")
        _replace_directory(stage_review, review_dir)
    finally:
        if stage_root.exists():
            shutil.rmtree(stage_root)
        if stage_review.exists():
            shutil.rmtree(stage_review)
    return metadata


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Normalize Idle/Attack/Hit/Dead action sheets into Character cue frames."
    )
    parser.add_argument("--idle", type=Path, required=True, help="2x2 Idle sheet")
    parser.add_argument("--attack", type=Path, required=True, help="2x2 Attack sheet")
    parser.add_argument("--hit", type=Path, required=True, help="2x2 Hit sheet")
    parser.add_argument("--dead", type=Path, required=True, help="2x3 Dead sheet")
    parser.add_argument("--images-root", type=Path, required=True)
    parser.add_argument("--review-dir", type=Path, required=True)
    parser.add_argument("--threshold", type=int, default=100)
    parser.add_argument("--edge-threshold", type=int, default=200)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        metadata = process_bundle(
            {action: getattr(args, action) for action in ACTION_CONTRACT},
            args.images_root,
            args.review_dir,
            threshold=args.threshold,
            edge_threshold=args.edge_threshold,
        )
    except CharacterCueError as exc:
        print(f"[character_cues] FAILED: {exc}")
        return 2
    frame_count = sum(len(action["frames"]) for action in metadata["actions"].values())
    print(f"[character_cues] OK: {frame_count} frames -> {args.images_root / 'charui' / 'cues'}")
    print(f"[character_cues] review -> {args.review_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
