#!/usr/bin/env python3
"""Normalize one combined Character cue sheet into an all-or-nothing cue bundle.

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
# Drawn cell-border lines: pixels darker than this (max channel) on a row or column near a
# cell boundary, covering at least this share of the sheet's length.
GRID_LINE_DARK = 90
GRID_LINE_COVERAGE = 0.5
# Pixels this close to a detected line and tinted toward the key by more than this are the
# line's antialiased fringe.
GRID_LINE_FRINGE = 2
GRID_LINE_FRINGE_SPILL = 40
# Background flood from the sheet edge: always clear pixels this close to the measured
# background; farther ones (up to the edge threshold) only when at least this bright
# relative to it.
FLOOD_NEAR_BACKGROUND = 60
# Edge-reachable pixels this close to the pure key flood whatever the background is.
FLOOD_NEAR_KEY = 90
FLOOD_MIN_RELATIVE_LUMINANCE = 0.8
SHEET_COLUMNS = CUE_CONTRACT.sheet_columns
SHEET_ROWS = CUE_CONTRACT.sheet_rows
ACTION_CONTRACT = {
    action.name: {
        "state_name": action.state_name,
        "play_cells": list(action.play_cells),
        "frame_count": action.frame_count,
        "duration_ms": action.frame_duration_ms,
        "loop": action.loop,
        "terminal": action.terminal,
        "output_dir": action.output_dir,
        "breathing": action.breathing,
    }
    for action in CUE_CONTRACT.actions
}


class CharacterCueError(ValueError):
    """Raised when a cue sheet cannot satisfy the cue bundle contract."""


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


def despill_edges(image: Image.Image, key: str = "magenta", band: int | None = 2) -> Image.Image:
    """Neutralize key-colored spill on the visible pixels within `band` px of transparency,
    or on every visible pixel when `band` is None.
    Antialiased edges blend the subject (often a dark ink line) with the key; distance keying
    cannot remove those without eating real dark pixels, and left alone they draw a magenta
    (or green) rim around the cut-out on dark game UI."""
    image = image.convert("RGBA")
    alpha = image.getchannel("A").point(lambda a: 255 if a else 0)
    eroded = (Image.new("L", image.size, 0) if band is None
              else alpha.filter(ImageFilter.MinFilter(2 * band + 1)))
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


def erase_grid_lines(image: Image.Image, rows: int, cols: int, key: str) -> Image.Image:
    """Repaint drawn cell-border lines in the key color so keying can flood past them.

    Only a row or column near a cell boundary that is dark along at least half the sheet
    counts as a line, so a subject that merely crosses a boundary keeps its pixels.
    """
    image = image.copy()
    pixels = image.load()
    width, height = image.size
    cell_width, cell_height = width / cols, height / rows
    band = max(3, round(min(cell_width, cell_height) * 0.02))
    key_pixel = (*KEY_COLORS[key], 255)

    def dark(pixel: tuple[int, int, int, int]) -> bool:
        return max(pixel[:3]) < GRID_LINE_DARK

    def key_tinted(pixel: tuple[int, int, int, int]) -> bool:
        r, g, b = pixel[:3]
        if key == "green":
            return g - max(r, b) > GRID_LINE_FRINGE_SPILL
        return min(r, b) - g > GRID_LINE_FRINGE_SPILL

    line_columns = [
        x
        for boundary in range(cols + 1)
        for x in range(max(0, round(boundary * cell_width) - band),
                       min(width, round(boundary * cell_width) + band + 1))
        if sum(dark(pixels[x, y]) for y in range(height)) >= GRID_LINE_COVERAGE * height
    ]
    line_rows = [
        y
        for boundary in range(rows + 1)
        for y in range(max(0, round(boundary * cell_height) - band),
                       min(height, round(boundary * cell_height) + band + 1))
        if sum(dark(pixels[x, y]) for x in range(width)) >= GRID_LINE_COVERAGE * width
    ]
    for x in line_columns:
        for y in range(height):
            if dark(pixels[x, y]):
                pixels[x, y] = key_pixel
    for y in line_rows:
        for x in range(width):
            if dark(pixels[x, y]):
                pixels[x, y] = key_pixel
    # A line's antialiased fringe is a dark blend with the key, e.g. (104, 0, 104): too
    # light to count as line and too far from the key to flood, it bridged a real 1K
    # sheet's rows into one component. Neutral subject pixels such as boots stay.
    fringe = GRID_LINE_FRINGE
    for x in {c for line in line_columns
              for c in range(max(0, line - fringe), min(width, line + fringe + 1))}:
        for y in range(height):
            if key_tinted(pixels[x, y]):
                pixels[x, y] = key_pixel
    for y in {r for line in line_rows
              for r in range(max(0, line - fringe), min(height, line + fringe + 1))}:
        for x in range(width):
            if key_tinted(pixels[x, y]):
                pixels[x, y] = key_pixel
    return image


def _measured_background(image: Image.Image) -> tuple[int, int, int]:
    """The median color of the sheet border; backends rarely return the exact key."""
    rgb = image.convert("RGB")
    pixels = rgb.load()
    width, height = rgb.size
    border = [pixels[x, y] for x in range(0, width, 3) for y in (0, height - 1)]
    border += [pixels[x, y] for y in range(0, height, 3) for x in (0, width - 1)]
    return tuple(int(statistics.median(channel)) for channel in zip(*border))


def _clear_near(
    image: Image.Image, colors: tuple[tuple[int, int, int], ...], distance: int
) -> Image.Image:
    image = image.convert("RGBA")
    pixels = image.load()
    limit = distance * distance
    for y in range(image.height):
        for x in range(image.width):
            r, g, b, a = pixels[x, y]
            if a and any((r - cr) ** 2 + (g - cg) ** 2 + (b - cb) ** 2 < limit
                         for cr, cg, cb in colors):
                pixels[x, y] = (0, 0, 0, 0)
    return image


def _luminance(color: tuple[int, int, int]) -> float:
    return 0.2126 * color[0] + 0.7152 * color[1] + 0.0722 * color[2]


def _flood_background(
    image: Image.Image,
    background: tuple[int, int, int],
    edge_threshold: int,
    key: tuple[int, int, int],
) -> Image.Image:
    """Clear background reachable from the sheet edge.

    A pixel floods when it is near the measured background or near the pure key, or within
    `edge_threshold` of the background and at least about as bright (a light glow haze).
    Darker blends are subject: see-through glass painted as darkened key, or an ink rim;
    despill neutralizes their tint. Flooding those too punched lantern glass out of a real
    1K sheet. Near-key pixels always flood: a real sheet on pale pink drew its cell borders
    in saturated key, and their blends, darker than that background, became a frame.
    """
    image = image.convert("RGBA")
    pixels = image.load()
    width, height = image.size
    near = FLOOD_NEAR_BACKGROUND ** 2
    near_key = FLOOD_NEAR_KEY ** 2
    edge = edge_threshold ** 2
    bright_enough = FLOOD_MIN_RELATIVE_LUMINANCE * _luminance(background)
    visited = bytearray(width * height)
    queue: deque[tuple[int, int]] = deque()
    queue.extend((x, y) for x in range(width) for y in (0, height - 1))
    queue.extend((x, y) for y in range(height) for x in (0, width - 1))
    while queue:
        x, y = queue.popleft()
        if not (0 <= x < width and 0 <= y < height) or visited[y * width + x]:
            continue
        visited[y * width + x] = 1
        r, g, b, a = pixels[x, y]
        distance = ((r - background[0]) ** 2 + (g - background[1]) ** 2
                    + (b - background[2]) ** 2)
        to_key = (r - key[0]) ** 2 + (g - key[1]) ** 2 + (b - key[2]) ** 2
        if not (a == 0 or distance < near or to_key < near_key
                or (distance < edge and _luminance((r, g, b)) >= bright_enough)):
            continue
        pixels[x, y] = (0, 0, 0, 0)
        queue.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
    return image


def _center(component: Component) -> tuple[float, float]:
    left, top, right, bottom = component.bbox
    return (left + right) / 2, (top + bottom) / 2


def segment_sheet(
    raw: Image.Image,
    rows: int,
    cols: int,
    threshold: int = 40,
    edge_threshold: int = 200,
    required: Iterable[int] | None = None,
) -> tuple[Image.Image, list[tuple[Image.Image, tuple[int, int, int, int], Component, int] | None]]:
    """Key the whole sheet and give every cell its body plus detached companions.

    Only the `required` cells (default: all) must hold a subject; any other empty cell is
    returned as None.

    Models do not draw on an exact pixel grid: in a real 2K sheet 12 of 16 bodies crossed
    their cell's bottom edge by 2-7 px, and fixed-grid cropping cut their feet. So each cell
    takes the largest component centered in it, wherever its pixels reach, plus companions
    (a held item that separated from the body: at least 1% of the body's area, centered
    within the body's bounds padded by 25%; a lantern otherwise blinked out of 7 of 32
    frames). Despill matches static Character bodies: without it, 56-80% of the visible
    rim of real frames stayed magenta-tinted ink.

    Returns the cleaned sheet and, per cell in reading order, (subject image, cell box,
    selected component in sheet coordinates, components centered in the cell).
    """
    key = detect_key_color(raw)
    erased = erase_grid_lines(raw, rows, cols, key)
    background = _measured_background(erased)
    # Enclosed background (between an arm and the body) is cleared only when it is close
    # to the sheet's measured background, not anything within 100 of the pure key: a real
    # 1K sheet painted lantern glass as see-through key, (133, 30, 99), and the wide pass
    # punched it out. Background reachable from the sheet edge is flooded as before.
    cleaned = _clear_near(erased, (background, KEY_COLORS[key]), threshold)
    cleaned = _flood_background(cleaned, background, edge_threshold, KEY_COLORS[key])
    # A subject on the key color holds no key hue by contract (pink or purple subjects use
    # the other key), so any tint left anywhere is background seen through the subject.
    cleaned = despill_edges(cleaned, key, band=None)
    width, height = cleaned.size
    cell_width, cell_height = width // cols, height // rows

    def cell_of(component: Component) -> int:
        x, y = _center(component)
        return (min(rows - 1, int(y // cell_height)) * cols
                + min(cols - 1, int(x // cell_width)))

    components = connected_components(cleaned)
    bodies: dict[int, Component] = {}
    counts = [0] * (rows * cols)
    for component in components:
        counts[cell_of(component)] += 1
        bodies.setdefault(cell_of(component), component)
    expected = range(rows * cols) if required is None else required
    missing = [index for index in expected if index not in bodies]
    if missing:
        raise CharacterCueError(
            f"cells {[index + 1 for index in missing]} are empty after key-color cleanup"
        )

    kept: dict[int, list[Component]] = {index: [body] for index, body in bodies.items()}
    body_ids = {id(body) for body in bodies.values()}
    for component in components:
        if id(component) in body_ids:
            continue
        x, y = _center(component)
        owners = []
        for index, body in bodies.items():
            left, top, right, bottom = body.bbox
            padding = max(2, round(max(right - left, bottom - top) * 0.25))
            if (
                component.area >= max(3, round(body.area * 0.01))
                and left - padding <= x <= right + padding
                and top - padding <= y <= bottom + padding
            ):
                bx, by = _center(body)
                owners.append(((x - bx) ** 2 + (y - by) ** 2, index))
        if owners:
            kept[min(owners)[1]].append(component)

    cells = []
    for index in range(rows * cols):
        if index not in kept:
            cells.append(None)
            continue
        members = kept[index]
        bbox = (
            min(member.bbox[0] for member in members),
            min(member.bbox[1] for member in members),
            max(member.bbox[2] for member in members),
            max(member.bbox[3] for member in members),
        )
        selected = Component(
            area=sum(member.area for member in members),
            bbox=bbox,
            pixels=tuple(pixel for member in members for pixel in member.pixels),
        )
        mask = Image.new("L", (bbox[2] - bbox[0], bbox[3] - bbox[1]), 0)
        mask_pixels = mask.load()
        for flat_index in selected.pixels:
            mask_pixels[flat_index % width - bbox[0], flat_index // width - bbox[1]] = 255
        subject = Image.new("RGBA", mask.size, (0, 0, 0, 0))
        subject.paste(cleaned.crop(bbox), (0, 0), mask)
        row, column = divmod(index, cols)
        cell_box = (column * cell_width, row * cell_height,
                    (column + 1) * cell_width, (row + 1) * cell_height)
        cells.append((subject, cell_box, selected, counts[index]))
    return cleaned, cells


def extract_sheet(
    source_path: Path,
    threshold: int = 40,
    edge_threshold: int = 200,
) -> tuple[Image.Image, dict[str, list[ExtractedFrame]]]:
    """Cut the combined sheet into each cue's frames; a breathing cue keeps one cell."""
    try:
        with Image.open(source_path) as source:
            source.verify()
        with Image.open(source_path) as source:
            raw = source.convert("RGBA")
    except (OSError, ValueError, SyntaxError) as exc:
        raise CharacterCueError(f"cue sheet is not a readable image: {source_path} ({exc})") from exc

    rows, cols = SHEET_ROWS, SHEET_COLUMNS
    expected = CUE_CONTRACT.sheet_size
    if (raw.width % cols or raw.height % rows) and abs(
        (raw.width / raw.height) / (expected[0] / expected[1]) - 1
    ) <= SHEET_ASPECT_TOLERANCE:
        # Backends round canvases to their own sizes (Gemini returns 2:3 as 848x1264), so a
        # right-shaped sheet does not always divide into whole cells as delivered.
        raw = raw.resize(expected, Image.Resampling.LANCZOS)
    if raw.width % cols or raw.height % rows:
        # Name the axes. A bare "NxM" grid reads as WxH to anyone who just produced the
        # sheet, which is the opposite order, and that ambiguity is how a wrong-shaped
        # sheet gets requested in the first place.
        raise CharacterCueError(
            f"cue sheet size {raw.width}x{raw.height} is not divisible by its "
            f"{cols} cols x {rows} rows grid (expected {expected[0]}x{expected[1]})"
        )
    played = {cell for contract in ACTION_CONTRACT.values() for cell in contract["play_cells"]}
    cleaned, cells = segment_sheet(raw, rows, cols, threshold, edge_threshold, required=played)
    # Each played cell is extracted once, under the first cue that plays it; unplayed cells
    # (the spare Hit pose) take no part in scaling.
    frames: dict[str, list[ExtractedFrame]] = {action: [] for action in ACTION_CONTRACT}
    seen: set[int] = set()
    for action, contract in ACTION_CONTRACT.items():
        for index in dict.fromkeys(contract["play_cells"]):
            if index in seen:
                continue
            seen.add(index)
            subject, cell_box, selected, component_count = cells[index]
            left, top, right, bottom = selected.bbox
            if left <= 0 or top <= 0 or right >= raw.width or bottom >= raw.height:
                raise CharacterCueError(
                    f"{action} cell {index + 1} touches the {raw.width}x{raw.height} sheet "
                    f"edge: {selected.bbox}"
                )
            frames[action].append(ExtractedFrame(
                action=action,
                index=index,
                image=subject,
                source_box=cell_box,
                # Relative to the cell's own origin; may run past the cell when the model
                # drew across the boundary.
                source_bbox=(left - cell_box[0], top - cell_box[1],
                             right - cell_box[0], bottom - cell_box[1]),
                selected_area=selected.area,
                component_count=component_count,
            ))
    return cleaned, frames


def breathing_frames(anchor: Image.Image) -> list[Image.Image]:
    """Idle from one painted frame: a small vertical stretch about the baseline per frame.

    Redrawn idle cells jitter (adjacent silhouettes differed 14-26% in a real sheet while
    looking identical); stretching one frame moves only the breath.
    """
    frames = []
    for amount in CUE_CONTRACT.breath:
        stretch = 1 + amount
        frame = anchor.transform(
            anchor.size, Image.Transform.AFFINE,
            (1, 0, 0, 0, 1 / stretch, BASELINE_Y * (1 - 1 / stretch)),
            resample=Image.Resampling.BICUBIC,
        )
        # Bicubic rings one row past the feet; the contract baseline is exclusive.
        frame.paste((0, 0, 0, 0), (0, BASELINE_Y, frame.width, frame.height))
        frames.append(frame)
    return frames


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
    # Leave headroom for the breathing stretch, so a body that fills the box stays inside it.
    headroom = 1 + max(CUE_CONTRACT.breath, default=0.0)
    global_scale = min(box_width / (union_right - union_left),
                       box_height / (max_height * headroom))
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
                "cell": frame.index,
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


def process_sheet(
    source: Path,
    images_root: Path,
    review_dir: Path,
    threshold: int = 40,
    edge_threshold: int = 200,
) -> dict:
    cleaned_sheet, extracted = extract_sheet(
        Path(source), threshold=threshold, edge_threshold=edge_threshold
    )
    normalized_poses, pose_metadata, global_scale, ratios = normalize_frames(extracted)
    by_cell = {
        frame.index: image
        for action in extracted
        for frame, image in zip(extracted[action], normalized_poses[action])
    }
    normalized: dict[str, list[Image.Image]] = {}
    for action, contract in ACTION_CONTRACT.items():
        if contract["breathing"]:
            normalized[action] = breathing_frames(by_cell[contract["play_cells"][0]])
        else:
            normalized[action] = [by_cell[cell] for cell in contract["play_cells"]]
    metadata = {
        "contract": "skill-the-spire-character-cues/v3",
        "processor_source": "agent-sprite-forge techniques, adapted under MIT",
        "source": str(Path(source).resolve()),
        "sheet": {"columns": SHEET_COLUMNS, "rows": SHEET_ROWS,
                  "sheet_px": list(CUE_CONTRACT.sheet_size)},
        "frame_size": list(FRAME_SIZE),
        "content_box": list(CONTENT_BOX),
        "baseline_y": BASELINE_Y,
        "global_scale": global_scale,
        "body_height_ratio_to_idle": ratios,
        "breath": list(CUE_CONTRACT.breath),
        "anchor_cell": CUE_CONTRACT.anchor_cell,
        "attack_strike_frame": CUE_CONTRACT.attack_strike_frame,
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
            "frame_order": list(range(len(normalized[action]))),
            "poses": pose_metadata[action],
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
            save_transparent_gif(
                frames,
                action_review / "animation.gif",
                ACTION_CONTRACT[action]["duration_ms"],
            )
        cleaned_sheet.save(stage_review / "raw-sheet-clean.png", "PNG", optimize=True)
        render_contact_sheet({
            action: [by_cell[frame.index] for frame in extracted[action]]
            for action in extracted
            if extracted[action]
        }).save(
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
        description="Normalize one combined Idle/Attack/Hit/Dead sheet into Character cue frames."
    )
    parser.add_argument("--sheet", type=Path, required=True,
                        help=f"{SHEET_COLUMNS} cols x {SHEET_ROWS} rows cue sheet, one row per cue")
    parser.add_argument("--images-root", type=Path, required=True)
    parser.add_argument("--review-dir", type=Path, required=True)
    parser.add_argument("--threshold", type=int, default=40)
    parser.add_argument("--edge-threshold", type=int, default=200)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        metadata = process_sheet(
            args.sheet,
            args.images_root,
            args.review_dir,
            threshold=args.threshold,
            edge_threshold=args.edge_threshold,
        )
    except CharacterCueError as exc:
        print(f"[character_cues] FAILED: {exc}")
        return 2
    frame_count = sum(len(action["frame_order"]) for action in metadata["actions"].values())
    print(f"[character_cues] OK: {frame_count} frames -> {args.images_root / 'charui' / 'cues'}")
    print(f"[character_cues] review -> {args.review_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
