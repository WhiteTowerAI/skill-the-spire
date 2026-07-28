from __future__ import annotations

import ast
import base64
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

from PIL import Image


TOOLS_DIR = Path(__file__).resolve().parents[1]
ACQUIRE = TOOLS_DIR / "acquire_sprite.py"
sys.path.insert(0, str(TOOLS_DIR))
import acquire_sprite  # noqa: E402
PNG = "iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAYAAABytg0kAAAAFElEQVR4nGP4z8Dwn4GBgYGJAQoAHwUCAbo3z9UAAAAASUVORK5CYII="


FAKE_VOFY = f"""
import base64
import os
import sys
import time
from pathlib import Path

args = sys.argv[1:]
mode = os.environ.get("FAKE_VOFY_MODE", "success")
record = os.environ.get("FAKE_VOFY_RECORD")
if record:
    with Path(record).open("a", encoding="utf-8") as handle:
        handle.write(repr(args) + "\\n")

if args == ["status"]:
    print("private account name; credits=999")
    sys.exit(4 if mode == "auth_failure" else 0)
if args[:1] == ["models"]:
    print("model capability output")
    sys.exit(5 if mode == "model_failure" else 0)
if args[:2] == ["image", "create"]:
    if mode == "task_failure":
        sys.exit(6)
    if mode == "timeout":
        time.sleep(2)
    output = Path(args[args.index("--download-to") + 1])
    output.mkdir(parents=True, exist_ok=True)
    if mode != "zero":
        (output / "source.png").write_bytes(base64.b64decode({PNG!r}))
    if mode == "multiple":
        (output / "second.png").write_bytes(base64.b64decode({PNG!r}))
    sys.exit(0)
sys.exit(9)
"""


class AcquireSpriteTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.fake = self.root / "fake vofy.py"
        self.fake.write_text(textwrap.dedent(FAKE_VOFY), encoding="utf-8")
        self.cmd = self.root / "fake vofy.cmd"
        self.cmd.write_text(
            f'@echo off\r\n"{sys.executable}" "{self.fake}" %*\r\n',
            encoding="utf-8",
        )
        self.record = self.root / "calls.txt"
        self.out = self.root / "mod images"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_tool(self, *args: str, mode: str = "success") -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["FAKE_VOFY_MODE"] = mode
        env["FAKE_VOFY_RECORD"] = str(self.record)
        return subprocess.run(
            [sys.executable, str(ACQUIRE), *args, "--vofy-command", str(self.fake)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env,
            check=False,
        )

    def create_args(self, spec: str = "card") -> list[str]:
        return [
            "create",
            "--model", "test-model",
            "--spec", spec,
            "--slug", "paid-art",
            "--prompt", "one approved image",
            "--out", str(self.out),
        ]

    def test_preflight_hides_account_output(self) -> None:
        result = self.run_tool("preflight", "--model", "test-model")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertNotIn("private account", result.stdout)
        self.assertNotIn("999", result.stdout)

    def test_windows_npm_cmd_shim_is_supported(self) -> None:
        env = os.environ.copy()
        env["FAKE_VOFY_MODE"] = "success"
        result = subprocess.run(
            [sys.executable, str(ACQUIRE), "preflight", "--model", "test-model",
             "--vofy-command", str(self.cmd)],
            capture_output=True, text=True, encoding="utf-8", env=env, check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr)

    def test_windows_cmd_receives_complete_prompt_on_one_line(self) -> None:
        env = os.environ.copy()
        env["FAKE_VOFY_MODE"] = "success"
        env["FAKE_VOFY_RECORD"] = str(self.record)
        prompt = "First sentence.\r\nSecond sentence.\n  Final constraint."
        result = subprocess.run(
            [sys.executable, str(ACQUIRE), *self.create_args(),
             "--prompt", prompt, "--yes", "--vofy-command", str(self.cmd)],
            capture_output=True, text=True, encoding="utf-8", env=env, check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr)

        calls = [ast.literal_eval(line) for line in self.record.read_text(
            encoding="utf-8").splitlines()]
        create = next(args for args in calls if args[:2] == ["image", "create"])
        received = create[create.index("--prompt") + 1]
        self.assertEqual(
            "First sentence. Second sentence. Final constraint.", received
        )
        self.assertNotIn("\r", received)
        self.assertNotIn("\n", received)

    def test_missing_cli_is_actionable_and_never_logs_in(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ACQUIRE), "preflight", "--model", "test-model",
             "--vofy-command", str(self.root / "missing-vofy")],
            capture_output=True, text=True, encoding="utf-8", check=False,
        )
        self.assertEqual(2, result.returncode)
        self.assertIn("never install it or launch `vofy login`", result.stderr)

    def test_auth_and_model_failures_stop_at_preflight(self) -> None:
        for mode, expected in (("auth_failure", "status/auth/credits"),
                               ("model_failure", "capability lookup")):
            with self.subTest(mode=mode):
                result = self.run_tool("preflight", "--model", "test-model", mode=mode)
                self.assertNotEqual(0, result.returncode)
                self.assertIn(expected, result.stderr)
                self.assertNotIn("private account", result.stdout + result.stderr)

    def test_create_requires_explicit_paid_approval_before_cli_calls(self) -> None:
        result = self.run_tool(*self.create_args())
        self.assertEqual(2, result.returncode)
        self.assertIn("Paid generation was not approved", result.stderr)
        self.assertFalse(self.record.exists())

    def test_whitespace_only_prompt_stops_before_cli_calls(self) -> None:
        result = self.run_tool(
            *self.create_args(), "--prompt", " \r\n\t ", "--yes"
        )
        self.assertEqual(2, result.returncode)
        self.assertIn("cannot be empty or whitespace-only", result.stderr)
        self.assertFalse(self.record.exists())

    def test_invalid_local_references_stop_before_cli_calls(self) -> None:
        cases = (
            (["--reference", str(self.root / "missing.png")], "Reference image not found"),
            (["--reference", str(self.fake)] * 4, "at most three"),
        )
        for reference_args, expected in cases:
            with self.subTest(expected=expected):
                self.record.unlink(missing_ok=True)
                result = self.run_tool(*self.create_args(), *reference_args, "--yes")
                self.assertEqual(2, result.returncode)
                self.assertIn(expected, result.stderr)
                self.assertFalse(self.record.exists())

    def test_task_failure_timeout_and_ambiguous_downloads_do_not_retry(self) -> None:
        cases = (
            ("task_failure", [], "image generation failed"),
            ("timeout", ["--generation-timeout", "0.05"], "Do not submit it again"),
            ("zero", [], "contained 0 images"),
            ("multiple", [], "contained 2 images"),
        )
        for mode, extra, expected in cases:
            with self.subTest(mode=mode):
                self.record.unlink(missing_ok=True)
                result = self.run_tool(*self.create_args(), *extra, "--yes", mode=mode)
                self.assertNotEqual(0, result.returncode)
                self.assertIn(expected, result.stderr)
                calls = self.record.read_text(encoding="utf-8")
                self.assertEqual(1, calls.count("'image', 'create'"))
                self.assertFalse(any(self.out.rglob("*.png")))

    def test_card_uses_one_paid_task_then_imports_to_contract(self) -> None:
        reference = self.root / "style reference.png"
        reference.write_bytes(base64.b64decode(PNG))
        result = self.run_tool(
            *self.create_args(),
            "--reference", str(reference),
            "--aspect-ratio", "4:3",
            "--resolution", "2K",
            "--yes",
        )
        self.assertEqual(0, result.returncode, result.stderr)
        destination = self.out / "card_portraits" / "paid-art.png"
        with Image.open(destination) as image:
            self.assertEqual((1000, 760), image.size)
        calls = self.record.read_text(encoding="utf-8")
        self.assertEqual(1, calls.count("'image', 'create'"))
        for token in ("'--yes'", "'--n', '1'", "'--image'", "'--aspect-ratio', '4:3'"):
            self.assertIn(token, calls)

    def test_reference_root_selects_matching_spec_and_randomly_caps_at_three(self) -> None:
        root = self.root / "art-samples"
        pool = root / "orb"
        pool.mkdir(parents=True)
        for index in range(5):
            (pool / f"orb-{index}.png").write_bytes(base64.b64decode(PNG))
        decoy = root / "card"
        decoy.mkdir()
        (decoy / "card.png").write_bytes(base64.b64decode(PNG))

        result = self.run_tool(
            *self.create_args("orb"), "--reference", str(root), "--yes"
        )

        self.assertEqual(0, result.returncode, result.stderr)
        calls = [ast.literal_eval(line) for line in self.record.read_text(
            encoding="utf-8"
        ).splitlines()]
        create = next(args for args in calls if args[:2] == ["image", "create"])
        references = [Path(create[index + 1]) for index, value in enumerate(create) if value == "--image"]
        self.assertEqual(3, len(references))
        self.assertEqual(3, len(set(references)))
        self.assertTrue(all(path.parent == pool.resolve() for path in references))
        self.assertIn("[acquire_sprite] selected references:", result.stdout)

    def test_character_reference_alias_never_uses_unrelated_root_images(self) -> None:
        root = self.root / "art-samples"
        pool = root / "character_combat"
        pool.mkdir(parents=True)
        expected = pool / "combat.png"
        expected.write_bytes(base64.b64decode(PNG))
        (root / "wrong-family.png").write_bytes(base64.b64decode(PNG))

        references = acquire_sprite.resolve_reference_inputs(
            [str(root)], "character_merchant"
        )

        self.assertEqual([expected.resolve()], references)

    def test_character_background_uses_its_own_reference_pool(self) -> None:
        root = self.root / "art-samples"
        background_pool = root / "character_background"
        background_pool.mkdir(parents=True)
        expected = background_pool / "defect.png"
        expected.write_bytes(base64.b64decode(PNG))
        portrait_pool = root / "character_select"
        portrait_pool.mkdir()
        (portrait_pool / "wrong-small-portrait.png").write_bytes(base64.b64decode(PNG))

        references = acquire_sprite.resolve_reference_inputs(
            [str(root)], "character_background"
        )

        self.assertEqual([expected.resolve()], references)

    def test_identity_sensitive_character_adds_selection_portrait_reference(self) -> None:
        identity = self.root / "select.png"
        Image.new("RGB", (132, 195), (80, 110, 140)).save(identity)

        result = self.run_tool(
            *self.create_args("character_combat"),
            "--identity-reference", str(identity),
            "--yes",
        )

        self.assertEqual(0, result.returncode, result.stderr)
        calls = [ast.literal_eval(line) for line in self.record.read_text(
            encoding="utf-8"
        ).splitlines()]
        create = next(args for args in calls if args[:2] == ["image", "create"])
        references = [Path(create[index + 1]) for index, value in enumerate(create) if value == "--image"]
        self.assertEqual([identity.resolve()], references)
        self.assertIn("identity reference: select.png", result.stdout)

    def test_character_cue_acquisition_uses_identity_and_stages_through_gen_sprite(self) -> None:
        identity = self.root / "select.png"
        Image.new("RGB", (132, 195), (80, 110, 140)).save(identity)
        images = self.root / "project" / "CueMod" / "images"

        result = self.run_tool(
            "create",
            "--model", "test-model",
            "--spec", "character_cue_idle",
            "--slug", "idle",
            "--prompt", "four idle frames on flat magenta",
            "--out", str(images),
            "--identity-reference", str(identity),
            "--yes",
        )

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertTrue(
            (self.root / "project" / "art-sources" / "character-cues" / "idle.png").is_file()
        )
        self.assertFalse((images / "charui" / "cues").exists())
        calls = [ast.literal_eval(line) for line in self.record.read_text(
            encoding="utf-8"
        ).splitlines()]
        create = next(args for args in calls if args[:2] == ["image", "create"])
        references = [
            Path(create[index + 1])
            for index, value in enumerate(create)
            if value == "--image"
        ]
        self.assertEqual([identity.resolve()], references)

    def test_palette_character_rejects_identity_portrait_and_identity_asset_requires_one(self) -> None:
        identity = self.root / "select.png"
        Image.new("RGB", (132, 195), (80, 110, 140)).save(identity)

        result = self.run_tool(
            *self.create_args("character_icon"),
            "--identity-reference", str(identity),
            "--yes",
        )
        self.assertEqual(2, result.returncode)
        self.assertIn("palette-only", result.stderr)
        self.assertFalse(self.record.exists())

        result = self.run_tool(*self.create_args("character_rest"), "--yes")
        self.assertEqual(2, result.returncode)
        self.assertIn("requires", result.stderr)
        self.assertFalse(self.record.exists())

    def test_cutout_uses_import_chroma_and_emits_both_relic_paths(self) -> None:
        result = self.run_tool(*self.create_args("relic"), "--yes")
        self.assertEqual(0, result.returncode, result.stderr)
        small = self.out / "relics" / "paid-art.png"
        big = self.out / "relics" / "big" / "paid-art.png"
        with Image.open(small) as image:
            self.assertEqual((256, 256), image.size)
            self.assertEqual("RGBA", image.mode)
        with Image.open(big) as image:
            self.assertEqual((256, 256), image.size)

    def test_event_uses_opaque_import_and_emits_one_portrait(self) -> None:
        result = self.run_tool(*self.create_args("event"), "--yes")
        self.assertEqual(0, result.returncode, result.stderr)
        destination = self.out / "events" / "paid-art.png"
        with Image.open(destination) as image:
            self.assertEqual((3440, 1613), image.size)
        self.assertEqual([destination], list(self.out.rglob("*.png")))

    def test_enchantment_emits_one_exact_icon(self) -> None:
        result = self.run_tool(*self.create_args("enchantment"), "--yes")
        self.assertEqual(0, result.returncode, result.stderr)
        destination = self.out / "enchantments" / "paid-art.png"
        with Image.open(destination) as image:
            self.assertEqual((64, 64), image.size)
            self.assertEqual("RGBA", image.mode)
        self.assertEqual([destination], list(self.out.rglob("*.png")))

    def test_orb_emits_one_exact_icon(self) -> None:
        result = self.run_tool(*self.create_args("orb"), "--yes")
        self.assertEqual(0, result.returncode, result.stderr)
        destination = self.out / "orbs" / "paid-art.png"
        with Image.open(destination) as image:
            self.assertEqual((100, 100), image.size)
            self.assertEqual("RGBA", image.mode)
        self.assertEqual([destination], list(self.out.rglob("*.png")))

    def test_monster_emits_one_exact_static_body(self) -> None:
        result = self.run_tool(*self.create_args("monster"), "--yes")
        self.assertEqual(0, result.returncode, result.stderr)
        destination = self.out / "monsters" / "paid-art.png"
        with Image.open(destination) as image:
            self.assertEqual((360, 360), image.size)
            self.assertEqual("RGBA", image.mode)
        self.assertEqual([destination], list(self.out.rglob("*.png")))

    def test_character_icon_uses_chroma_import(self) -> None:
        result = self.run_tool(*self.create_args("character_icon"), "--yes")
        self.assertEqual(0, result.returncode, result.stderr)
        destination = self.out / "charui" / "paid-art.png"
        outline = self.out / "charui" / "paid-art_outline.png"
        with Image.open(destination) as image:
            self.assertEqual((88, 88), image.size)
            self.assertEqual("RGBA", image.mode)
        with Image.open(outline) as image:
            self.assertEqual((88, 88), image.size)
            self.assertEqual("RGBA", image.mode)
        self.assertEqual([destination, outline], list(self.out.rglob("*.png")))

        log = (self.out / ".gen_sprite.log").read_text(encoding="utf-8")
        self.assertIn("chroma=True", log)
        self.assertIn("applied magenta chroma-key", log)

    def test_character_background_keeps_opaque_full_bleed_import(self) -> None:
        result = self.run_tool(*self.create_args("character_background"), "--yes")
        self.assertEqual(0, result.returncode, result.stderr)
        destination = self.out / "charui" / "paid-art.png"
        with Image.open(destination) as image:
            self.assertEqual((1920, 1200), image.size)
            self.assertEqual("RGBA", image.mode)
            self.assertEqual(255, image.getpixel((0, 0))[3])
        self.assertEqual([destination], list(self.out.rglob("*.png")))

        log = (self.out / ".gen_sprite.log").read_text(encoding="utf-8")
        self.assertIn("chroma=False", log)
        self.assertNotIn("applied magenta chroma-key", log)


if __name__ == "__main__":
    unittest.main()
