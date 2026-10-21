#!/usr/bin/env python3
"""Pack STS2 assets, including raw Godot text scenes, without Godot/MegaDot.

The Godot 4.5 PCK layout, CTEX wrapper, and PNG import-remap behavior are adapted from
BSchneppe/StS2PckPacker 0.1.1 (MIT). That package deliberately blocks `.tscn`; STS2
0.107.1 has separately been verified to load a raw text scene from the same PCK format.
Shaders and scripts remain blocked because this tool does not implement their import or
compilation contracts.

Copyright (c) BSchneppe

Permission is hereby granted, free of charge, to any person obtaining a copy of this
software and associated documentation files (the "Software"), to deal in the Software
without restriction, including without limitation the rights to use, copy, modify,
merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import os
import struct
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print(
        "[pack_pck] Pillow is required. Install it with `python -m pip install Pillow`.",
        file=sys.stderr,
    )
    raise SystemExit(2)


IMAGE_SUFFIX = ".png"
UNSUPPORTED_SUFFIXES = {".gdextension", ".gdscript", ".gdshader"}
# Tool logs hold local absolute paths; a stale one in the resource tree never ships.
EXCLUDED_NAMES = {".gen_sprite.log"}
PCK_MAGIC = b"GDPC"
PCK_FORMAT_VERSION = 3
ENGINE_VERSION = (4, 5, 1)
PACK_FLAGS = 2
HEADER_SIZE = 112
DATA_ALIGNMENT = 32


class PackError(Exception):
    """A bounded packing failure with an actionable message."""


@dataclass(frozen=True)
class PckEntry:
    path: str
    data: bytes


def _align_padding(position: int, boundary: int) -> int:
    remainder = position % boundary
    return 0 if remainder == 0 else boundary - remainder


def _texture_import_text(source_path: str, ctex_path: str) -> str:
    return (
        '[remap]\n\nimporter="texture"\ntype="CompressedTexture2D"\n'
        f'path="{ctex_path}"\nmetadata={{\n"vram_texture": false\n}}\n\n'
        f'[deps]\n\nsource_file="{source_path}"\n'
        f'dest_files=["{ctex_path}"]\n\n[params]\n\ncompress/mode=0\n'
        "compress/high_quality=false\ncompress/lossy_quality=1.0\n"
        "mipmaps/generate=false"
    )


def _png_to_ctex(png_data: bytes) -> bytes:
    with Image.open(io.BytesIO(png_data)) as source:
        image = source.convert("RGBA")
        width, height = image.size
        encoded = io.BytesIO()
        image.save(encoded, format="WEBP", lossless=True, quality=100, method=6)
    payload = encoded.getvalue()
    header = b"".join(
        [
            b"GST2",
            struct.pack("<I", 1),
            struct.pack("<I", width),
            struct.pack("<I", height),
            struct.pack("<I", 218103808),
            struct.pack("<i", -1),
            bytes(12),
            struct.pack("<I", 2),
            struct.pack("<I", (height << 16) | width),
            struct.pack("<I", 0),
            struct.pack("<I", 5),
            struct.pack("<I", len(payload)),
        ]
    )
    return header + payload


def collect_entries(source_dir: Path, res_prefix: str) -> list[PckEntry]:
    source_dir = source_dir.resolve()
    if not source_dir.is_dir():
        raise PackError(f"asset directory not found: {source_dir}")
    prefix = res_prefix.strip("/\\")
    if not prefix:
        raise PackError("res prefix must not be empty")

    files = sorted(
        path for path in source_dir.rglob("*")
        if path.is_file() and path.name not in EXCLUDED_NAMES
    )
    unsupported = [
        path.relative_to(source_dir).as_posix()
        for path in files
        if path.suffix.lower() in UNSUPPORTED_SUFFIXES
    ]
    if unsupported:
        raise PackError(
            "assets require Godot compilation and remain unsupported: "
            + ", ".join(unsupported)
        )

    entries: dict[str, bytes] = {}
    for path in files:
        relative = path.relative_to(source_dir).as_posix()
        suffix = path.suffix.lower()
        if suffix == IMAGE_SUFFIX:
            resource_path = f"res://{prefix}/{relative}"
            digest = hashlib.md5(resource_path.encode("utf-8")).hexdigest()
            ctex_name = f"{path.name}-{digest}.ctex"
            ctex_entry = f".godot/imported/{ctex_name}"
            import_entry = f"{prefix}/{relative}.import"
            ctex_path = f"res://{ctex_entry}"
            entries[ctex_entry] = _png_to_ctex(path.read_bytes())
            entries[import_entry] = _texture_import_text(
                resource_path, ctex_path
            ).encode("utf-8")
            continue

        entry_path = f"{prefix}/{relative}"
        entries[entry_path] = path.read_bytes()

    return [PckEntry(path, entries[path]) for path in sorted(entries)]


def write_pck(output, entries: list[PckEntry]) -> None:
    indexed: list[tuple[PckEntry, int, bytes]] = []
    data_size = 0
    for entry in entries:
        padding = _align_padding(HEADER_SIZE + data_size, DATA_ALIGNMENT)
        data_size += padding
        indexed.append((entry, data_size, hashlib.md5(entry.data).digest()))
        data_size += len(entry.data)

    directory_offset = HEADER_SIZE + data_size
    output.write(PCK_MAGIC)
    output.write(struct.pack("<I", PCK_FORMAT_VERSION))
    output.write(struct.pack("<III", *ENGINE_VERSION))
    output.write(struct.pack("<I", PACK_FLAGS))
    output.write(struct.pack("<q", HEADER_SIZE))
    output.write(struct.pack("<q", directory_offset))
    output.write(bytes(64))
    output.write(bytes(8))

    for entry, relative_offset, _digest in indexed:
        absolute_position = HEADER_SIZE + relative_offset
        padding = absolute_position - output.tell()
        if padding < 0:
            raise PackError("internal PCK offset calculation moved backwards")
        output.write(bytes(padding))
        output.write(entry.data)

    output.write(struct.pack("<I", len(indexed)))
    for entry, relative_offset, digest in indexed:
        path_bytes = entry.path.encode("utf-8")
        path_padding = _align_padding(len(path_bytes), 4)
        output.write(struct.pack("<I", len(path_bytes) + path_padding))
        output.write(path_bytes)
        output.write(bytes(path_padding))
        output.write(struct.pack("<q", relative_offset))
        output.write(struct.pack("<q", len(entry.data)))
        output.write(digest)
        output.write(struct.pack("<I", 0))


def pack_assets(source_dir: Path, res_prefix: str, output_path: Path) -> Path:
    entries = collect_entries(source_dir, res_prefix)
    output_path = output_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=output_path.parent, suffix=".pck.tmp", delete=False
        ) as handle:
            temporary = Path(handle.name)
            write_pck(handle, entries)
        os.replace(temporary, output_path)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return output_path


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Pack STS2 PNG/JSON/TRES/TSCN assets without Godot"
    )
    parser.add_argument("--source-dir", required=True)
    parser.add_argument("--res-prefix", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    try:
        output = pack_assets(
            Path(args.source_dir), args.res_prefix, Path(args.output)
        )
    except (OSError, PackError, Image.UnidentifiedImageError) as exc:
        print(f"[pack_pck] FAILED: {exc}", file=sys.stderr)
        return 1
    print(f"[pack_pck] packed raw text scenes -> {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
