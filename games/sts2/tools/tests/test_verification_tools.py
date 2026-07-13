from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


launch = load_module("open_mod_launch", TOOLS_DIR / "launch.py")
grep_log = load_module("open_mod_grep_log", TOOLS_DIR / "grep_log.py")


class GrepLogTests(unittest.TestCase):
    mod = "CanaryCard"

    def run_grep(self, lines: list[str], pattern: str | None = None) -> tuple[int, str]:
        with tempfile.TemporaryDirectory() as tmp:
            log_path = Path(tmp) / "godot.log"
            log_path.write_text("\n".join(lines), encoding="utf-8")
            argv = ["--mod-name", self.mod, "--log-path", str(log_path)]
            if pattern is not None:
                argv += ["--tier2-pattern", pattern]
            output = io.StringIO()
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                code = grep_log.main(argv)
            return code, output.getvalue()

    def baseline(self) -> list[str]:
        return [
            "RUNNING MODDED",
            f"INFO [T2MOD-SELFTEST] {self.mod} loaded ok",
        ]

    def test_tier2_pass_requires_effect_and_done(self) -> None:
        code, output = self.run_grep(
            self.baseline()
            + [
                f"INFO [T2MOD-SELFTEST] {self.mod} Jolt played: 6 dmg",
                f"INFO [T2MOD-SELFTEST] {self.mod} selftest done",
            ],
            "played",
        )
        self.assertEqual(0, code)
        self.assertIn("[PASS] Tier-2 verified", output)

    def test_done_alone_is_not_effect_proof(self) -> None:
        code, output = self.run_grep(
            self.baseline() + [f"INFO [T2MOD-SELFTEST] {self.mod} selftest done"],
            "played|selftest done",
        )
        self.assertEqual(1, code)
        self.assertIn("effect marker not found", output)

    def test_failed_terminal_forces_failure_even_with_effect(self) -> None:
        code, output = self.run_grep(
            self.baseline()
            + [
                f"INFO [T2MOD-SELFTEST] {self.mod} Jolt played: 6 dmg",
                f"INFO [T2MOD-SELFTEST] {self.mod} selftest FAILED: play phase timeout",
            ],
            "played",
        )
        self.assertEqual(1, code)
        self.assertIn("setup/navigation miss", output)

    def test_tier1_requires_exact_load_marker(self) -> None:
        code, _ = self.run_grep(
            ["RUNNING MODDED", f"INFO [T2MOD-SELFTEST] {self.mod} selftest done"]
        )
        self.assertEqual(1, code)

    def test_mod_named_exception_fails(self) -> None:
        code, output = self.run_grep(
            self.baseline() + [f"ERROR {self.mod} NullReferenceException"]
        )
        self.assertEqual(1, code)
        self.assertIn("Error lines found", output)

    def test_invalid_regex_is_usage_error(self) -> None:
        code, output = self.run_grep(self.baseline(), "[")
        self.assertEqual(2, code)
        self.assertIn("Invalid --tier2-pattern", output)


class LaunchOutcomeTests(unittest.TestCase):
    def test_done_is_success(self) -> None:
        self.assertEqual(0, launch.self_test_exit_code("done"))

    def test_failure_outcomes_are_nonzero(self) -> None:
        for outcome in ("failed", "timeout", "process-exited"):
            with self.subTest(outcome=outcome):
                self.assertEqual(1, launch.self_test_exit_code(outcome))


if __name__ == "__main__":
    unittest.main()
