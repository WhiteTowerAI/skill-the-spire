from __future__ import annotations

import struct
import sys
import tempfile
import unittest
from pathlib import Path


TOOLS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_DIR))
import audio_assets  # noqa: E402
from audio_assets import AudioAssetError, validate_project_audio  # noqa: E402

MOD = "SoundMod"


def wav(format_tag: int = 1) -> bytes:
    fmt = struct.pack("<HHIIHH", format_tag, 1, 44100, 88200, 2, 16)
    data = b"\x00\x00" * 8
    body = b"WAVE" + b"fmt " + struct.pack("<I", len(fmt)) + fmt
    body += b"data" + struct.pack("<I", len(data)) + data
    return b"RIFF" + struct.pack("<I", len(body)) + body


def ogg(codec: bytes = b"\x01vorbis") -> bytes:
    return b"OggS" + bytes(24) + codec + bytes(32)


MP3 = b"ID3\x04\x00" + bytes(32)


class AudioAssetTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.project = Path(self.temp.name)
        self.audio = self.project / MOD / "audio"
        self.code = self.project / f"{MOD}Code"
        self.audio.mkdir(parents=True)
        self.code.mkdir()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_audio(self, name: str, data: bytes) -> None:
        (self.audio / name).write_bytes(data)

    def write_source(self, text: str) -> None:
        (self.code / "ModAudio.cs").write_text(text, encoding="utf-8")

    def assert_rejects(self, fragment: str) -> None:
        with self.assertRaises(AudioAssetError) as caught:
            validate_project_audio(self.project, MOD)
        self.assertIn(fragment, str(caught.exception))

    def test_project_without_audio_passes(self) -> None:
        self.assertEqual(validate_project_audio(self.project, MOD), "no audio")

    def test_supported_files_and_existing_references_pass(self) -> None:
        self.write_audio("hit.wav", wav())
        self.write_audio("chime.ogg", ogg())
        self.write_audio("roar.mp3", MP3)
        self.write_source(
            'VirtualFmodEventRegistry.RegisterOneShot("event:/mods/soundmod/hit", '
            '"res://SoundMod/audio/hit.wav");\n'
        )
        self.assertEqual(validate_project_audio(self.project, MOD), "files=3 references=1")

    def test_float_and_extensible_wav_pass(self) -> None:
        self.write_audio("a.wav", wav(3))
        self.write_audio("b.wav", wav(0xFFFE))
        validate_project_audio(self.project, MOD)

    def test_unsupported_format_names_the_conversion(self) -> None:
        self.write_audio("theme.flac", b"fLaC" + bytes(16))
        self.assert_rejects("unsupported audio format .flac")

    def test_name_must_be_snake_case(self) -> None:
        self.write_audio("Big Hit.wav", wav())
        self.assert_rejects("lowercase snake_case")

    def test_content_must_match_suffix(self) -> None:
        self.write_audio("hit.ogg", MP3)
        self.assert_rejects("is not an Ogg file")

    def test_compressed_wav_is_rejected(self) -> None:
        self.write_audio("hit.wav", wav(0x11))
        self.assert_rejects("compressed WAV format 0x0011")

    def test_ogg_opus_is_rejected(self) -> None:
        self.write_audio("hit.ogg", ogg(b"OpusHead"))
        self.assert_rejects("Ogg Opus")

    def test_oversized_file_is_rejected(self) -> None:
        self.write_audio("hit.mp3", MP3)
        original = audio_assets.MAX_BYTES
        audio_assets.MAX_BYTES = 8
        try:
            self.assert_rejects("plays at most 8")
        finally:
            audio_assets.MAX_BYTES = original

    def test_nested_files_are_rejected(self) -> None:
        (self.audio / "sfx").mkdir()
        (self.audio / "sfx" / "hit.wav").write_bytes(wav())
        self.assert_rejects("keep sound files directly in audio/")

    def test_missing_referenced_file_is_rejected(self) -> None:
        self.write_source('const string Hit = "res://SoundMod/audio/hti.wav";\n')
        self.assert_rejects("res://SoundMod/audio/hti.wav does not exist")

    def test_reference_must_use_the_mod_root(self) -> None:
        self.write_audio("hit.wav", wav())
        self.write_source('const string Hit = "res://OtherMod/audio/hit.wav";\n')
        self.assert_rejects("must start with res://SoundMod/audio/")


if __name__ == "__main__":
    unittest.main()
