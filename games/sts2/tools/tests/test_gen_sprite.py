from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from PIL import Image
from PIL import ImageDraw


TOOLS_DIR = Path(__file__).resolve().parents[1]
GEN_SPRITE = TOOLS_DIR / "gen_sprite.py"
sys.path.insert(0, str(TOOLS_DIR))
import gen_sprite  # noqa: E402


class GenSpriteTests(unittest.TestCase):
    def test_cutout_fragment_cleanup_keeps_subject_cluster_and_removes_debris(self) -> None:
        image = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.rectangle((30, 30, 70, 70), fill=(40, 160, 120, 255))
        draw.rectangle((45, 18, 55, 24), fill=(180, 240, 210, 255))
        draw.rectangle((2, 2, 4, 4), fill=(20, 20, 20, 255))
        draw.rectangle((90, 80, 94, 84), fill=(20, 20, 20, 255))
        draw.rectangle((0, 0, 99, 99), outline=(20, 20, 20, 255), width=5)

        cleaned = gen_sprite.remove_cutout_fragments(image)

        self.assertEqual(0, cleaned.getpixel((3, 3))[3])
        self.assertEqual(0, cleaned.getpixel((92, 82))[3])
        self.assertEqual(255, cleaned.getpixel((50, 20))[3])
        self.assertEqual(255, cleaned.getpixel((50, 50))[3])

    def test_shipped_m6_reference_pools_match_supported_profiles(self) -> None:
        root = TOOLS_DIR.parent / "skills" / "sts2-api" / "reference" / "art-samples"
        expected = {
            "enchantment": (20, (64, 64)),
            "orb": (5, (100, 100)),
            "monster": (3, (512, 512)),
        }

        for spec, (count, size) in expected.items():
            with self.subTest(spec=spec):
                paths = sorted((root / spec).glob("*.png"))
                self.assertEqual(count, len(paths))
                for path in paths:
                    with Image.open(path) as image:
                        self.assertEqual(size, image.size, path.name)

        self.assertEqual(
            {"axebot.png", "ceremonial_beast.png", "crossbow_ruby_raider.png"},
            {path.name for path in (root / "monster").glob("*.png")},
        )

    def test_reference_pool_selects_spec_subdir_and_randomly_caps_at_three(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pool = root / "enchantment"
            pool.mkdir()
            expected_pool = []
            for index in range(5):
                path = pool / f"style-{index}.png"
                path.touch()
                expected_pool.append(path)
            decoy = root / "card"
            decoy.mkdir()
            (decoy / "wrong-family.png").touch()
            chosen = [expected_pool[4], expected_pool[1], expected_pool[3]]

            with mock.patch.object(gen_sprite.random, "SystemRandom") as factory:
                factory.return_value.sample.return_value = chosen
                references = gen_sprite.resolve_references(
                    str(root), 3, lambda _message: None, spec="enchantment"
                )

            self.assertEqual(chosen, references)
            factory.return_value.sample.assert_called_once_with(expected_pool, 3)

    def test_monster_import_writes_one_exact_static_body(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.png"
            out = root / "images"
            Image.new("RGBA", (20, 30), (230, 170, 40, 255)).save(source)

            result = subprocess.run(
                [
                    sys.executable,
                    str(GEN_SPRITE),
                    "import",
                    "--spec",
                    "monster",
                    "--slug",
                    "canary_sentinel",
                    "--input",
                    str(source),
                    "--out",
                    str(out),
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            destination = out / "monsters" / "canary_sentinel.png"
            self.assertTrue(destination.is_file())
            with Image.open(destination) as image:
                self.assertEqual((360, 360), image.size)
                self.assertEqual("RGBA", image.mode)
            self.assertEqual([destination], list(out.rglob("*.png")))

    def test_orb_import_writes_one_exact_icon(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.png"
            out = root / "images"
            Image.new("RGBA", (20, 10), (90, 180, 230, 255)).save(source)

            result = subprocess.run(
                [
                    sys.executable,
                    str(GEN_SPRITE),
                    "import",
                    "--spec",
                    "orb",
                    "--slug",
                    "shelter_orb",
                    "--input",
                    str(source),
                    "--out",
                    str(out),
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            destination = out / "orbs" / "shelter_orb.png"
            self.assertTrue(destination.is_file())
            with Image.open(destination) as image:
                self.assertEqual((100, 100), image.size)
            self.assertEqual([destination], list(out.rglob("*.png")))

    def test_enchantment_import_writes_one_exact_icon(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.png"
            out = root / "images"
            Image.new("RGBA", (20, 10), (220, 180, 40, 255)).save(source)

            result = subprocess.run(
                [
                    sys.executable,
                    str(GEN_SPRITE),
                    "import",
                    "--spec",
                    "enchantment",
                    "--slug",
                    "guarded",
                    "--input",
                    str(source),
                    "--out",
                    str(out),
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            destination = out / "enchantments" / "guarded.png"
            self.assertTrue(destination.is_file())
            with Image.open(destination) as image:
                self.assertEqual((64, 64), image.size)
            self.assertEqual([destination], list(out.rglob("*.png")))

    def test_event_import_writes_one_exact_portrait(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.png"
            out = root / "images"
            Image.new("RGB", (20, 10), (20, 80, 160)).save(source)

            result = subprocess.run(
                [
                    sys.executable,
                    str(GEN_SPRITE),
                    "import",
                    "--spec",
                    "event",
                    "--slug",
                    "gilded-signpost",
                    "--input",
                    str(source),
                    "--out",
                    str(out),
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            destination = out / "events" / "gilded-signpost.png"
            self.assertTrue(destination.is_file())
            with Image.open(destination) as image:
                self.assertEqual((3440, 1613), image.size)
            self.assertEqual([destination], list(out.rglob("*.png")))

    def test_event_contract_is_live_verified(self) -> None:
        result = subprocess.run(
            [sys.executable, str(GEN_SPRITE), "list-specs"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )

        self.assertEqual(0, result.returncode, result.stderr)
        event_line = next(
            line for line in result.stdout.splitlines() if line.startswith("event")
        )
        self.assertIn("events", event_line)
        self.assertIn("3440x1613", event_line)
        self.assertNotIn("*not live-verified", event_line)

    def test_enchantment_contract_is_live_verified(self) -> None:
        result = subprocess.run(
            [sys.executable, str(GEN_SPRITE), "list-specs"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )

        self.assertEqual(0, result.returncode, result.stderr)
        enchantment_line = next(
            line for line in result.stdout.splitlines() if line.startswith("enchantment")
        )
        self.assertIn("enchantments", enchantment_line)
        self.assertIn("64x64", enchantment_line)
        self.assertNotIn("*not live-verified", enchantment_line)

    def test_orb_icon_contract_is_live_verified(self) -> None:
        result = subprocess.run(
            [sys.executable, str(GEN_SPRITE), "list-specs"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )

        self.assertEqual(0, result.returncode, result.stderr)
        orb_line = next(
            line for line in result.stdout.splitlines() if line.startswith("orb")
        )
        self.assertIn("orbs", orb_line)
        self.assertIn("100x100", orb_line)
        self.assertNotIn("*not live-verified", orb_line)
        self.assertNotIn("requires headed in-game proof", result.stdout)

    def test_monster_static_contract_is_live_verified(self) -> None:
        result = subprocess.run(
            [sys.executable, str(GEN_SPRITE), "list-specs"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )

        self.assertEqual(0, result.returncode, result.stderr)
        monster_line = next(
            line for line in result.stdout.splitlines() if line.startswith("monster")
        )
        self.assertIn("monsters", monster_line)
        self.assertIn("360x360", monster_line)
        self.assertNotIn("*not live-verified", monster_line)


if __name__ == "__main__":
    unittest.main()
