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


def make_cue_sheet(path: Path, action_name: str) -> None:
    action = gen_sprite.CHARACTER_ART_BUNDLE.cue_action(action_name)
    cell = 100
    image = Image.new(
        "RGBA", (action.columns * cell, action.rows * cell), (255, 0, 255, 255)
    )
    draw = ImageDraw.Draw(image)
    for index in range(action.frame_count):
        row, column = divmod(index, action.columns)
        left = column * cell + 30
        top = row * cell + 10
        draw.rectangle((left, top, left + 39, top + 79), fill=(40, 130, 190, 255))
    image.save(path)


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
            "event": (6, (1616, 1616)),
            "character_select": (3, (132, 195)),
            "character_icon": (3, (88, 88)),
            "character_combat": (3, (512, 512)),
            "character_rest": (3, (512, 512)),
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

    def test_character_specs_match_their_current_promotion_state(self) -> None:
        expected = {
            "character_select": ((132, 195), "contain", False, True),
            "character_select_locked": ((132, 195), "cover", False, False),
            "character_icon": ((88, 88), "contain", True, True),
            "character_map_marker": ((49, 64), "contain", True, False),
            "character_background": ((1920, 1200), "cover", False, True),
            "character_combat": ((512, 512), "contain", True, True),
            "character_rest": ((512, 512), "contain", True, True),
            "character_merchant": ((512, 512), "contain", True, True),
            "character_energy": ((256, 256), "contain", True, True),
            "character_energy_large": ((256, 256), "contain", True, True),
            "character_energy_text": ((24, 24), "contain", True, True),
        }
        for spec, (size, fit, chroma, verified) in expected.items():
            with self.subTest(spec=spec):
                info = gen_sprite.SPECS[spec]
                self.assertEqual(size, info["size"])
                self.assertEqual(fit, info["fit"])
                self.assertEqual(chroma, info["chroma"])
                self.assertEqual(verified, info["verified"])

    def test_character_cue_import_stages_until_complete_then_writes_atomic_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "project"
            images = project / "CueMod" / "images"
            inputs = root / "inputs"
            inputs.mkdir()

            for index, action in enumerate(
                gen_sprite.CHARACTER_ART_BUNDLE.combat_cues.actions
            ):
                source = inputs / f"{action.name}.png"
                make_cue_sheet(source, action.name)
                result = subprocess.run(
                    [
                        sys.executable, str(GEN_SPRITE), "import",
                        "--spec", action.source_spec,
                        "--slug", action.name,
                        "--input", str(source),
                        "--out", str(images),
                    ],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    check=False,
                )
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertTrue(
                    (project / "art-sources" / "character-cues" / f"{action.name}.png").is_file()
                )
                if index < 3:
                    self.assertIn("bundle incomplete", result.stdout)
                    self.assertFalse((images / "charui" / "cues").exists())

            self.assertIn("normalized complete bundle", result.stdout)
            runtime_frames = sorted((images / "charui" / "cues").rglob("*.png"))
            self.assertEqual(18, len(runtime_frames))
            self.assertTrue(
                (project / "art-review" / "character-cues" / "pipeline-meta.json").is_file()
            )
            self.assertTrue(
                (project / "art-review" / "character-cues" /
                 "character-cues-contact-sheet.png").is_file()
            )

    def test_character_icon_import_writes_exact_transparent_profile(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.png"
            out = root / "images"
            Image.new("RGBA", (20, 30), (40, 160, 120, 255)).save(source)

            result = subprocess.run(
                [
                    sys.executable, str(GEN_SPRITE), "import",
                    "--spec", "character_icon", "--slug", "wayfinder_icon",
                    "--input", str(source), "--out", str(out), "--chroma",
                ],
                capture_output=True, text=True, encoding="utf-8", check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            destination = out / "charui" / "wayfinder_icon.png"
            outline_path = out / "charui" / "wayfinder_icon_outline.png"
            self.assertTrue(destination.is_file())
            self.assertTrue(outline_path.is_file())
            with Image.open(destination) as image:
                self.assertEqual((88, 88), image.size)
                self.assertEqual("RGBA", image.mode)
                bounds = image.getchannel("A").getbbox()
                self.assertGreaterEqual(bounds[0], 3)
                self.assertGreaterEqual(bounds[1], 3)
                self.assertLessEqual(bounds[2], 85)
                self.assertLessEqual(bounds[3], 85)
            with Image.open(outline_path) as outline:
                self.assertEqual((88, 88), outline.size)
                self.assertEqual("RGBA", outline.mode)
                self.assertEqual(
                    {(255, 255, 255)},
                    {pixel[:3] for pixel in outline.getdata() if pixel[3]},
                )

    def test_character_cutout_removes_edge_connected_soft_magenta(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.png"
            out = root / "images"
            image = Image.new("RGBA", (100, 100), (222, 27, 136, 255))
            ImageDraw.Draw(image).rectangle(
                (35, 15, 64, 84), fill=(30, 80, 150, 255)
            )
            image.save(source)

            result = subprocess.run(
                [
                    sys.executable, str(GEN_SPRITE), "import",
                    "--spec", "character_rest", "--slug", "rest",
                    "--input", str(source), "--out", str(out), "--chroma",
                ],
                capture_output=True, text=True, encoding="utf-8", check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            with Image.open(out / "charui" / "rest.png") as normalized:
                self.assertEqual(0, normalized.getpixel((0, 0))[3])
                self.assertEqual(255, normalized.getpixel((256, 256))[3])
            log = (out / ".gen_sprite.log").read_text(encoding="utf-8")
            self.assertIn("edge-connected soft magenta", log)

    def test_character_icon_drops_disconnected_debris_before_outline(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.png"
            out = root / "images"
            image = Image.new("RGBA", (100, 100), (222, 27, 136, 255))
            draw = ImageDraw.Draw(image)
            draw.rectangle((35, 15, 64, 84), fill=(30, 80, 150, 255))
            draw.rectangle((0, 0, 4, 4), fill=(20, 40, 90, 255))
            draw.rectangle((95, 95, 99, 99), fill=(20, 40, 90, 255))
            image.save(source)

            result = subprocess.run(
                [
                    sys.executable, str(GEN_SPRITE), "import",
                    "--spec", "character_icon", "--slug", "icon",
                    "--input", str(source), "--out", str(out), "--chroma",
                ],
                capture_output=True, text=True, encoding="utf-8", check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            with Image.open(out / "charui" / "icon.png") as normalized:
                bounds = normalized.getchannel("A").getbbox()
                self.assertGreater(bounds[0], 3)
                self.assertLess(bounds[2], 85)
            with Image.open(out / "charui" / "icon_outline.png") as outline:
                self.assertEqual(0, outline.getpixel((0, 0))[3])
                self.assertEqual(0, outline.getpixel((87, 87))[3])
            log = (out / ".gen_sprite.log").read_text(encoding="utf-8")
            self.assertIn("disconnected Character cut-out", log)

    def test_alpha_outline_uses_exact_proportional_white_expansion(self) -> None:
        image = Image.new("RGBA", (88, 88), (0, 0, 0, 0))
        ImageDraw.Draw(image).rectangle((20, 30, 39, 49), fill=(30, 90, 170, 128))

        outline = gen_sprite.derive_alpha_outline(image)

        self.assertEqual((88, 88), outline.size)
        self.assertEqual(3, gen_sprite.outline_expansion_radius(outline.size))
        self.assertEqual(82 / 88, gen_sprite.outline_safe_fill(outline.size))
        self.assertEqual((17, 27, 43, 53), outline.getchannel("A").getbbox())
        self.assertEqual((255, 255, 255, 255), outline.getpixel((17, 27)))
        self.assertEqual((255, 255, 255, 255), outline.getpixel((20, 30)))
        self.assertEqual((255, 255, 255, 0), outline.getpixel((0, 0)))

    def test_alpha_outline_rejects_an_empty_main_icon(self) -> None:
        with self.assertRaisesRegex(SystemExit, "empty final alpha"):
            gen_sprite.derive_alpha_outline(
                Image.new("RGBA", (88, 88), (0, 0, 0, 0))
            )

    def test_relic_import_writes_main_big_and_derived_outline(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.png"
            out = root / "images"
            image = Image.new("RGBA", (80, 100), (0, 0, 0, 0))
            ImageDraw.Draw(image).ellipse((10, 20, 69, 79), fill=(40, 160, 120, 255))
            image.save(source)

            result = subprocess.run(
                [
                    sys.executable, str(GEN_SPRITE), "import",
                    "--spec", "relic", "--slug", "first_bearing",
                    "--input", str(source), "--out", str(out),
                ],
                capture_output=True, text=True, encoding="utf-8", check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            main_path = out / "relics" / "first_bearing.png"
            big_path = out / "relics" / "big" / "first_bearing.png"
            outline_path = out / "relics" / "first_bearing_outline.png"
            self.assertTrue(main_path.is_file())
            self.assertTrue(big_path.is_file())
            self.assertTrue(outline_path.is_file())
            self.assertEqual(main_path.read_bytes(), big_path.read_bytes())
            self.assertNotEqual(main_path.read_bytes(), outline_path.read_bytes())
            with Image.open(main_path) as main, Image.open(outline_path) as outline:
                self.assertEqual((256, 256), main.size)
                self.assertEqual(main.size, outline.size)
                self.assertEqual(8, gen_sprite.outline_expansion_radius(outline.size))
                bounds = main.convert("RGBA").getchannel("A").getbbox()
                self.assertGreaterEqual(bounds[0], 8)
                self.assertGreaterEqual(bounds[1], 8)
                self.assertLessEqual(bounds[2], 248)
                self.assertLessEqual(bounds[3], 248)
                main_alpha = main.convert("RGBA").getchannel("A")
                outline_alpha = outline.convert("RGBA").getchannel("A")
                self.assertTrue(all(
                    not main_value or outline_value
                    for main_value, outline_value in zip(
                        main_alpha.getdata(), outline_alpha.getdata()
                    )
                ))
                self.assertEqual(
                    {(255, 255, 255)},
                    {pixel[:3] for pixel in outline.convert("RGBA").getdata() if pixel[3]},
                )
                self.assertEqual(0, outline.getpixel((0, 0))[3])

    def test_character_background_import_writes_opaque_profile(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.png"
            out = root / "images"
            Image.new("RGB", (20, 10), (20, 80, 160)).save(source)

            result = subprocess.run(
                [
                    sys.executable, str(GEN_SPRITE), "import",
                    "--spec", "character_background", "--slug", "wayfinder_bg",
                    "--input", str(source), "--out", str(out),
                ],
                capture_output=True, text=True, encoding="utf-8", check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            destination = out / "charui" / "wayfinder_bg.png"
            self.assertTrue(destination.is_file())
            with Image.open(destination) as image:
                self.assertEqual((1920, 1200), image.size)
                self.assertEqual("RGBA", image.mode)
                self.assertEqual(255, image.getpixel((0, 0))[3])

    def test_character_selection_import_preserves_source_inside_safe_box(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.png"
            out = root / "images"
            image = Image.new("RGB", (132, 195), (20, 80, 160))
            ImageDraw.Draw(image).rectangle(
                (0, 0, 131, 194), outline=(240, 220, 40), width=3
            )
            image.save(source)

            result = subprocess.run(
                [
                    sys.executable, str(GEN_SPRITE), "import",
                    "--spec", "character_select", "--slug", "select",
                    "--input", str(source), "--out", str(out),
                ],
                capture_output=True, text=True, encoding="utf-8", check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            with Image.open(out / "charui" / "select.png") as normalized:
                self.assertEqual((132, 195), normalized.size)
                self.assertEqual((255, 255), normalized.getchannel("A").getextrema())
                self.assertNotEqual(
                    normalized.getpixel((0, 0)), normalized.getpixel((6, 9))
                )

    def test_character_combat_import_pins_alpha_box_and_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.png"
            out = root / "images"
            image = Image.new("RGBA", (240, 300), (0, 0, 0, 0))
            ImageDraw.Draw(image).rectangle(
                (40, 0, 199, 299), fill=(80, 160, 120, 255)
            )
            image.save(source)

            result = subprocess.run(
                [
                    sys.executable, str(GEN_SPRITE), "import",
                    "--spec", "character_combat", "--slug", "combat",
                    "--input", str(source), "--out", str(out),
                ],
                capture_output=True, text=True, encoding="utf-8", check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            with Image.open(out / "charui" / "combat.png") as normalized:
                bounds = normalized.getchannel("A").getbbox()
                self.assertGreaterEqual(bounds[0], 26)
                self.assertGreaterEqual(bounds[1], 26)
                self.assertLessEqual(bounds[2], 486)
                self.assertEqual(486, bounds[3])

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

    def test_character_reference_alias_never_falls_back_to_the_root_pool(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pool = root / "character_icon"
            pool.mkdir()
            expected = pool / "icon.png"
            expected.touch()
            (root / "wrong-family.png").touch()

            references = gen_sprite.resolve_references(
                str(root), 3, lambda _message: None, spec="character_energy_text"
            )

            self.assertEqual([expected], references)

    def test_character_background_uses_its_own_reference_pool(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            background_pool = root / "character_background"
            background_pool.mkdir()
            expected = background_pool / "defect.png"
            expected.touch()
            portrait_pool = root / "character_select"
            portrait_pool.mkdir()
            (portrait_pool / "wrong-small-portrait.png").touch()

            references = gen_sprite.resolve_references(
                str(root), 3, lambda _message: None, spec="character_background"
            )

            self.assertEqual([expected], references)

    def test_character_identity_routing_adds_portrait_only_for_identity_sensitive_specs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            identity = root / "select.png"
            Image.new("RGB", (132, 195), (80, 110, 140)).save(identity)
            messages: list[str] = []

            references = gen_sprite.resolve_references(
                None,
                3,
                messages.append,
                spec="character_combat",
                identity_reference=str(identity),
            )
            self.assertEqual([identity.resolve()], references)

            with self.assertRaisesRegex(SystemExit, "palette-only"):
                gen_sprite.resolve_references(
                    None,
                    3,
                    messages.append,
                    spec="character_icon",
                    identity_reference=str(identity),
                )

    def test_character_energy_import_preserves_shared_source_canvas(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.png"
            out = root / "images"
            image = Image.new("RGBA", (100, 100), (255, 0, 255, 255))
            ImageDraw.Draw(image).rectangle((40, 40, 59, 59), fill=(40, 160, 120, 255))
            image.save(source)

            result = subprocess.run(
                [
                    sys.executable, str(GEN_SPRITE), "import",
                    "--spec", "character_energy", "--slug", "orb_layer_1",
                    "--input", str(source), "--out", str(out), "--chroma",
                ],
                capture_output=True, text=True, encoding="utf-8", check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            with Image.open(out / "charui" / "orb_layer_1.png") as normalized:
                bbox = normalized.getchannel("A").getbbox()
                self.assertIsNotNone(bbox)
                self.assertLess(bbox[2] - bbox[0], 100)
                self.assertLess(bbox[3] - bbox[1], 100)

    def test_character_large_and_text_energy_imports_write_distinct_sizes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.png"
            out = root / "images"
            Image.new("RGBA", (80, 80), (40, 160, 120, 255)).save(source)

            for spec, slug, expected_size in (
                ("character_energy_large", "energy_large", (256, 256)),
                ("character_energy_text", "energy_text", (24, 24)),
            ):
                result = subprocess.run(
                    [
                        sys.executable, str(GEN_SPRITE), "import",
                        "--spec", spec, "--slug", slug,
                        "--input", str(source), "--out", str(out),
                    ],
                    capture_output=True, text=True, encoding="utf-8", check=False,
                )
                self.assertEqual(0, result.returncode, result.stderr)
                with Image.open(out / "charui" / f"{slug}.png") as normalized:
                    self.assertEqual(expected_size, normalized.size)

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

    def test_rest_site_option_import_writes_one_exact_verified_icon(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.png"
            out = root / "images"
            Image.new("RGB", (40, 20), (90, 50, 30)).save(source)

            result = subprocess.run(
                [
                    sys.executable,
                    str(GEN_SPRITE),
                    "import",
                    "--spec",
                    "rest_site_option",
                    "--slug",
                    "quiet-forge",
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
            destination = out / "rest_site_options" / "quiet-forge.png"
            self.assertTrue(destination.is_file())
            with Image.open(destination) as image:
                self.assertEqual((256, 169), image.size)
            self.assertEqual([destination], list(out.rglob("*.png")))

            listed = subprocess.run(
                [sys.executable, str(GEN_SPRITE), "list-specs"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(0, listed.returncode, listed.stderr)
            line = next(
                item for item in listed.stdout.splitlines()
                if item.startswith("rest_site_option")
            )
            self.assertIn("rest_site_options", line)
            self.assertIn("256x169", line)
            self.assertNotIn("*not live-verified", line)

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
