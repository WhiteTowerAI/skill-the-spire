from __future__ import annotations

import contextlib
import io
import re
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_DIR))

import selftest_kit  # noqa: E402
from scaffold import generate, refresh_selftest_kit  # noqa: E402
from selftest_kit import SelfTestKitError  # noqa: E402

MOD = "EmberMod"


class SelfTestKitTests(unittest.TestCase):
    def generated(self, tmp: str) -> Path:
        project = Path(tmp) / "ember-project"
        generate(project, MOD, "SkillTheSpire")
        return project

    def refresh(self, project: Path) -> tuple[int, str]:
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            code = refresh_selftest_kit(project, MOD)
        return code, output.getvalue()

    def test_render_puts_the_kit_in_the_mod_namespace(self) -> None:
        text = selftest_kit.render(MOD)
        self.assertIn(f"namespace {MOD};", text)
        self.assertNotIn(selftest_kit.KIT_TOKEN, text)
        self.assertEqual(selftest_kit.template_version(), selftest_kit.template_version(text))

    def test_kit_stays_inside_the_generated_code_boundary(self) -> None:
        # Generated Mods never ship Harmony, member reflection, Publicizer, or IL.
        text = selftest_kit.render(MOD)
        for forbidden in ("HarmonyLib", "BindingFlags", "GetField(", "GetMethod(", "GetProperty(",
                          "Publicizer", "System.Reflection.Emit"):
            self.assertNotIn(forbidden, text)
        self.assertIn("CommandLineHelper.GetValue(\"t2selftest\")", text)

    def test_generated_project_arms_and_matches_the_kit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = self.generated(tmp)
            main = (project / f"{MOD}Code" / "MainFile.cs").read_text(encoding="utf-8")
            self.assertIn(selftest_kit.ARM_LINE, main)
            self.assertIn("using MegaCrit.Sts2.Core.Helpers;", main)
            self.assertLess(main.index("loaded ok"), main.index(selftest_kit.ARM_LINE))
            self.assertIn("matches the bundled kit", selftest_kit.check(project, MOD))

    def test_hand_edited_kit_fails_and_refresh_restores_it(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = self.generated(tmp)
            path = selftest_kit.kit_path(project, MOD)
            path.write_text(path.read_text(encoding="utf-8").replace("Settle()", "Settled()"),
                            encoding="utf-8")
            with self.assertRaisesRegex(SelfTestKitError, "differs from the bundled kit"):
                selftest_kit.check(project, MOD)
            code, output = self.refresh(project)
            self.assertEqual(0, code, output)
            self.assertNotIn("NOTE", output)
            self.assertIn("matches the bundled kit", selftest_kit.check(project, MOD))

    def test_missing_or_older_kit_passes_with_a_note(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = self.generated(tmp)
            path = selftest_kit.kit_path(project, MOD)
            path.unlink()
            self.assertIn("predates the kit", selftest_kit.check(project, MOD))
            version = selftest_kit.template_version()
            older = selftest_kit.render(MOD).replace(
                f"// SelfTestKit {version} ", f"// SelfTestKit {version - 1} ", 1)
            path.write_text(older, encoding="utf-8")
            self.assertIn("older than the bundled", selftest_kit.check(project, MOD))
            path.write_text(older.replace(f"// SelfTestKit {version - 1} ", "// no header ", 1),
                            encoding="utf-8")
            with self.assertRaisesRegex(SelfTestKitError, "no '// SelfTestKit <version>' header"):
                selftest_kit.check(project, MOD)

    def test_refresh_notes_a_missing_arm_line_and_an_older_harness(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = self.generated(tmp)
            mainfile = project / f"{MOD}Code" / "MainFile.cs"
            text = mainfile.read_text(encoding="utf-8").replace(
                selftest_kit.ARM_LINE, 'if (CommandLineHelper.HasArg("t2selftest")) SelfTest.Arm();')
            mainfile.write_text(text, encoding="utf-8")
            code, output = self.refresh(project)
            self.assertEqual(0, code, output)
            self.assertIn("does not arm the kit", output)
            self.assertIn("older SelfTest.cs harness", output)

    def test_template_header_matches_the_parser(self) -> None:
        text = selftest_kit.template_path().read_text(encoding="utf-8")
        self.assertRegex(text.splitlines()[0], re.compile(r"^// SelfTestKit \d+ "))


if __name__ == "__main__":
    unittest.main()
