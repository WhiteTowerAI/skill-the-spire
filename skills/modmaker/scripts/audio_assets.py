#!/usr/bin/env python3
"""Check user-supplied sound files before they ship inside a generated Mod's `.pck`.

A Mod plays its own sound by registering a RitsuLib virtual event that names a raw file under
`res://<ModName>/audio/` (`sts2api/reference/audio.md`). `pack_pck.py` packs that file unchanged
and RitsuLib reads its bytes at playback, so a wrong container, an unsupported codec, or a typo
in a source path compiles and packs fine and only goes silent in game. This check runs before
MSBuild:

- every file in `<ModName>/audio/` has a lowercase snake_case name and a `.wav`, `.ogg`, or
  `.mp3` suffix, at most 256 MiB (RitsuLib's per-file cap);
- the bytes match the suffix: PCM or float WAV, Ogg Vorbis (not Opus), or MP3; and
- every `res://.../audio/...` literal in the Mod's sources names this Mod and an existing file.

Whether a sound plays, and how it sounds, stays with Tier 2 and headed review.
"""
from __future__ import annotations

import re
import struct
from pathlib import Path

from source_scan import mod_sources

AUDIO_DIR = "audio"
SUPPORTED_SUFFIXES = (".wav", ".ogg", ".mp3")
MAX_BYTES = 256 * 1024 * 1024
NAME_RE = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*\.(?:wav|ogg|mp3)$")
RES_AUDIO_RE = re.compile(r'"res://(?P<root>[^"/]+)/audio/(?P<relative>[^"]*)"')
# WAVE_FORMAT_PCM, WAVE_FORMAT_IEEE_FLOAT, WAVE_FORMAT_EXTENSIBLE.
WAV_FORMAT_TAGS = {1, 3, 0xFFFE}
CONVERT_HINT = "re-export it as 16-bit PCM .wav, Ogg Vorbis .ogg, or .mp3 (for example in Audacity)"


class AudioAssetError(Exception):
    """A sound file or reference the game would not play."""


def _wav_problem(data: bytes) -> str | None:
    if len(data) < 12 or data[:4] != b"RIFF" or data[8:12] != b"WAVE":
        return "is not a RIFF/WAVE file"
    position = 12
    while position + 8 <= len(data):
        chunk_id = data[position:position + 4]
        (size,) = struct.unpack_from("<I", data, position + 4)
        if chunk_id == b"fmt ":
            if size < 2 or position + 10 > len(data):
                return "has a truncated fmt chunk"
            (tag,) = struct.unpack_from("<H", data, position + 8)
            if tag not in WAV_FORMAT_TAGS:
                return f"uses compressed WAV format 0x{tag:04x}"
            return None
        position += 8 + size + (size & 1)
    return "has no fmt chunk"


def _ogg_problem(data: bytes) -> str | None:
    if data[:4] != b"OggS":
        return "is not an Ogg file"
    head = data[:128]
    if b"OpusHead" in head:
        return "is Ogg Opus, which the game's audio engine does not decode"
    if b"\x01vorbis" not in head:
        return "is not Ogg Vorbis"
    return None


def _mp3_problem(data: bytes) -> str | None:
    if data[:3] == b"ID3" or (len(data) >= 2 and data[0] == 0xFF and data[1] & 0xE0 == 0xE0):
        return None
    return "has neither an ID3 tag nor an MPEG frame header"


CONTENT_CHECKS = {".wav": _wav_problem, ".ogg": _ogg_problem, ".mp3": _mp3_problem}


def check_file(path: Path) -> str | None:
    """Return why the game would not play this file, or None."""
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_SUFFIXES:
        return f"unsupported audio format {suffix or '(none)'}; {CONVERT_HINT}"
    if not NAME_RE.fullmatch(path.name):
        return "rename it to lowercase snake_case such as hit_heavy.ogg"
    size = path.stat().st_size
    if size == 0:
        return "is empty"
    if size > MAX_BYTES:
        return f"is {size:,} bytes; RitsuLib plays at most {MAX_BYTES:,}"
    problem = CONTENT_CHECKS[suffix](path.read_bytes())
    return f"{problem}; {CONVERT_HINT}" if problem else None


def scan(project_dir: Path, mod_name: str) -> tuple[int, int, list[str]]:
    """(file count, reference count, problems) for the Mod's audio files and source paths."""
    problems: list[str] = []
    audio_dir = project_dir / mod_name / AUDIO_DIR
    files = sorted(path for path in audio_dir.rglob("*") if path.is_file()) if audio_dir.is_dir() else []
    for path in files:
        relative = path.relative_to(audio_dir).as_posix()
        if path.parent != audio_dir:
            problems.append(f"{AUDIO_DIR}/{relative}: keep sound files directly in {AUDIO_DIR}/")
            continue
        problem = check_file(path)
        if problem:
            problems.append(f"{AUDIO_DIR}/{relative} {problem}")

    references = 0
    for source in mod_sources(project_dir, mod_name):
        text = source.read_text(encoding="utf-8")
        for match in RES_AUDIO_RE.finditer(text):
            references += 1
            line = text.count("\n", 0, match.start()) + 1
            label = f"{source.relative_to(project_dir).as_posix()}:{line}"
            if match.group("root") != mod_name:
                problems.append(f"{label}: audio path must start with res://{mod_name}/audio/")
            elif not (audio_dir / match.group("relative")).is_file():
                problems.append(
                    f"{label}: res://{mod_name}/audio/{match.group('relative')} does not exist"
                )
    return len(files), references, problems


def validate_project_audio(project_dir: Path, mod_name: str) -> str:
    files, references, problems = scan(project_dir, mod_name)
    if problems:
        raise AudioAssetError("; ".join(problems))
    return f"files={files} references={references}" if files or references else "no audio"
