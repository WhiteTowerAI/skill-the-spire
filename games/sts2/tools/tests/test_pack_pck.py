from __future__ import annotations

import struct
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image


TOOLS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_DIR))
import pack_pck  # noqa: E402


def read_entries(path: Path) -> tuple[tuple[int, int, int], dict[str, bytes]]:
    with path.open("rb") as handle:
        if handle.read(4) != b"GDPC":
            raise AssertionError("missing PCK magic")
        format_version = struct.unpack("<I", handle.read(4))[0]
        engine = struct.unpack("<III", handle.read(12))
        _flags = struct.unpack("<I", handle.read(4))[0]
        file_base = struct.unpack("<q", handle.read(8))[0]
        directory_offset = struct.unpack("<q", handle.read(8))[0]
        if format_version != 3:
            raise AssertionError(f"unexpected format {format_version}")
        handle.seek(directory_offset)
        count = struct.unpack("<I", handle.read(4))[0]
        index = []
        for _ in range(count):
            path_size = struct.unpack("<I", handle.read(4))[0]
            entry_path = handle.read(path_size).rstrip(b"\0").decode("utf-8")
            offset = struct.unpack("<q", handle.read(8))[0]
            size = struct.unpack("<q", handle.read(8))[0]
            handle.read(16)
            handle.read(4)
            index.append((entry_path, offset, size))
        entries = {}
        for entry_path, offset, size in index:
            handle.seek(file_base + offset)
            entries[entry_path] = handle.read(size)
        return engine, entries


class PackPckTests(unittest.TestCase):
    def test_pack_preserves_raw_scene_and_imports_png(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            assets = root / "ExampleMod"
            scene = assets / "scenes" / "background.tscn"
            image = assets / "images" / "background.png"
            scene.parent.mkdir(parents=True)
            image.parent.mkdir(parents=True)
            scene_text = '[gd_scene format=3]\n\n[node name="Bg" type="Control"]\n'
            scene.write_text(scene_text, encoding="utf-8")
            Image.new("RGBA", (8, 6), (20, 40, 60, 255)).save(image)
            output = root / "ExampleMod.pck"

            pack_pck.pack_assets(assets, "ExampleMod", output)
            engine, entries = read_entries(output)

            self.assertEqual((4, 5, 1), engine)
            self.assertEqual(
                scene.read_bytes(),
                entries["ExampleMod/scenes/background.tscn"],
            )
            import_path = "ExampleMod/images/background.png.import"
            self.assertIn(import_path, entries)
            import_text = entries[import_path].decode("utf-8")
            self.assertIn('source_file="res://ExampleMod/images/background.png"', import_text)
            ctex_path = next(path for path in entries if path.endswith(".ctex"))
            self.assertTrue(entries[ctex_path].startswith(b"GST2"))

    def test_pack_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            assets = root / "ExampleMod"
            assets.mkdir()
            (assets / "scene.tscn").write_text("[gd_scene format=3]\n", encoding="utf-8")
            first = root / "first.pck"
            second = root / "second.pck"

            pack_pck.pack_assets(assets, "ExampleMod", first)
            pack_pck.pack_assets(assets, "ExampleMod", second)

            self.assertEqual(first.read_bytes(), second.read_bytes())

    def test_shader_and_script_sources_remain_blocked(self) -> None:
        for suffix in sorted(pack_pck.UNSUPPORTED_SUFFIXES):
            with self.subTest(suffix=suffix), tempfile.TemporaryDirectory() as tmp:
                assets = Path(tmp) / "ExampleMod"
                assets.mkdir()
                (assets / f"unsupported{suffix}").write_text("source", encoding="utf-8")
                with self.assertRaisesRegex(pack_pck.PackError, "remain unsupported"):
                    pack_pck.pack_assets(assets, "ExampleMod", Path(tmp) / "out.pck")


if __name__ == "__main__":
    unittest.main()
