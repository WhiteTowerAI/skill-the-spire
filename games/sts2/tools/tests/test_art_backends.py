from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

from PIL import Image


TOOLS_DIR = Path(__file__).resolve().parents[1]
GEN_SPRITE = TOOLS_DIR / "gen_sprite.py"
sys.path.insert(0, str(TOOLS_DIR))
import gen_sprite  # noqa: E402


# Stands in for any user CLI: records its argv, then writes images per FAKE_MODE.
FAKE_CLI = """
import os
import sys
import time
from pathlib import Path

from PIL import Image

args = sys.argv[1:]
mode = os.environ.get("FAKE_MODE", "success")
with Path(os.environ["FAKE_RECORD"]).open("a", encoding="utf-8") as handle:
    handle.write(repr(args) + "\\n")
if args == ["status"]:
    print("private account name; credits=999")
    sys.exit(4 if mode == "preflight_failure" else 0)
if mode == "failure":
    sys.exit(6)
if mode == "timeout":
    time.sleep(120)
out = Path(args[args.index("--out") + 1])
count = {"zero": 0, "multiple": 2}.get(mode, 1)
for index in range(count):
    Image.new("RGB", (64, 48), (200, 60, 40)).save(out / f"result{index}.png")
"""


class ArtBackendTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.fake = self.root / "fake cli.py"
        self.fake.write_text(textwrap.dedent(FAKE_CLI), encoding="utf-8")
        self.record = self.root / "calls.txt"
        self.out = self.root / "project" / "Mod" / "images"
        self.config = self.root / "art-backends.json"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_config(self, **extra) -> None:
        backend = {
            "mode": "command",
            "command": [sys.executable, str(self.fake), "--prompt", "{prompt}",
                        "--ratio", "{aspect_ratio}", "--out", "{out_dir}"],
            "reference_args": ["--image", "{image}"],
            **extra,
        }
        self.config.write_text(json.dumps({"backends": {
            "mine": backend,
            "other": {"mode": "images", "base_url": "https://x.test/v1",
                      "api_key": "k", "model": "m"},
        }}), encoding="utf-8")

    def generate(self, *extra: str, mode: str = "success", spec: str = "card"):
        env = os.environ.copy()
        env.update(FAKE_MODE=mode, FAKE_RECORD=str(self.record))
        return subprocess.run(
            [sys.executable, str(GEN_SPRITE), "generate", "--spec", spec,
             "--slug", "art", "--prompt", "First line.\r\n  Second line.",
             "--out", str(self.out), "--config", str(self.config), *extra],
            capture_output=True, text=True, encoding="utf-8", env=env, check=False,
        )

    def calls(self) -> list[list[str]]:
        if not self.record.exists():
            return []
        return [eval(line) for line in self.record.read_text(encoding="utf-8").splitlines()]

    def test_command_backend_imports_one_image_and_keeps_its_source(self) -> None:
        self.write_config()
        result = self.generate("--backend", "mine")
        self.assertEqual(0, result.returncode, result.stderr)
        destination = self.out / "card_portraits" / "art.png"
        self.assertEqual(str(destination), result.stdout.splitlines()[-1])
        with Image.open(destination) as image:
            self.assertEqual((1000, 760), image.size)
        kept = self.root / "project" / "art-sources" / "generated" / "card" / "art.png"
        self.assertTrue(kept.is_file())

        (call,) = self.calls()
        self.assertEqual("First line. Second line.", call[call.index("--prompt") + 1])
        self.assertEqual("4:3", call[call.index("--ratio") + 1])

    def test_command_backend_expands_reference_args(self) -> None:
        self.write_config()
        references = self.root / "refs"
        references.mkdir()
        for name in ("a.png", "b.png"):
            Image.new("RGB", (8, 8)).save(references / name)
        result = self.generate("--backend", "mine", "--reference", str(references))
        self.assertEqual(0, result.returncode, result.stderr)
        (call,) = self.calls()
        self.assertEqual(2, call.count("--image"))

    def test_preflight_failure_stops_before_generation_and_hides_output(self) -> None:
        self.write_config(preflight=[[sys.executable, str(self.fake), "status"]])
        result = self.generate("--backend", "mine", mode="preflight_failure")
        self.assertNotEqual(0, result.returncode)
        self.assertEqual([["status"]], self.calls())
        self.assertNotIn("credits", result.stdout + result.stderr)
        self.assertEqual([], list(self.root.rglob("art.png")))

    def test_failed_zero_or_multiple_outputs_import_nothing(self) -> None:
        self.write_config()
        for mode in ("failure", "zero", "multiple"):
            with self.subTest(mode=mode):
                result = self.generate("--backend", "mine", mode=mode)
                self.assertNotEqual(0, result.returncode)
                self.assertFalse((self.out / "card_portraits").exists())

    def test_timeout_warns_against_resubmitting(self) -> None:
        self.write_config(timeout=2)
        result = self.generate("--backend", "mine", mode="timeout")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("Do not resubmit", result.stderr)
        self.assertEqual(1, len(self.calls()))

    def test_named_config_requires_a_backend_choice_when_ambiguous(self) -> None:
        self.write_config()
        result = self.generate()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("mine", result.stderr)
        self.assertEqual([], self.calls())

    def test_single_backend_file_needs_no_name(self) -> None:
        self.config.write_text(json.dumps(
            {"base_url": "https://x.test/v1", "api_key": "k", "model": "m"}), encoding="utf-8")
        self.assertEqual("images", gen_sprite.load_config(self.config)["mode"])
        self.config.write_text(json.dumps({"backends": {"only": {
            "mode": "command", "command": ["tool"]}}}), encoding="utf-8")
        self.assertEqual(["tool"], gen_sprite.load_config(self.config)["command"])

    def test_nearest_aspect_ratio_matches_contract_shapes(self) -> None:
        self.assertEqual("4:3", gen_sprite.nearest_aspect_ratio((1000, 760)))
        self.assertEqual("21:9", gen_sprite.nearest_aspect_ratio((3440, 1613)))
        self.assertEqual("2:3", gen_sprite.nearest_aspect_ratio((132, 195)))
        self.assertEqual("1:1", gen_sprite.nearest_aspect_ratio((256, 256)))
        self.assertEqual("16:9", gen_sprite.nearest_aspect_ratio((3440, 1613), ("1:1", "16:9")))


if __name__ == "__main__":
    unittest.main()
