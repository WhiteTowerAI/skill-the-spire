from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_DIR))


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
            f"INFO [T2MOD-SELFTEST] {self.mod} loaded ok "
            "framework=RitsuLib frameworkVersion=0.5.11 host=0.107.1 compat=0.107.1",
        ]

    def test_tier2_pass_requires_state_proof_and_done(self) -> None:
        code, output = self.run_grep(
            self.baseline()
            + [
                f"INFO [T2MOD-SELFTEST] {self.mod} state proof: damage 20 -> 14 delta=6",
                f"INFO [T2MOD-SELFTEST] {self.mod} selftest done",
            ],
            "damage.*delta=6",
        )
        self.assertEqual(0, code)
        self.assertIn("[PASS] Tier-2 verified", output)

    def test_preview_and_broad_markers_are_not_state_proof(self) -> None:
        code, output = self.run_grep(
            self.baseline()
            + [
                f"INFO [T2MOD-SELFTEST] {self.mod} Edge fired: preview added 4 damage",
                f"INFO [T2MOD-SELFTEST] {self.mod} Jolt played: 6 damage",
                f"INFO [T2MOD-SELFTEST] {self.mod} selftest done",
            ],
            "played|fired|used|damage",
        )
        self.assertEqual(1, code)
        self.assertIn("state proof not found", output)

    def test_done_alone_is_not_state_proof(self) -> None:
        code, output = self.run_grep(
            self.baseline() + [f"INFO [T2MOD-SELFTEST] {self.mod} selftest done"],
            "damage|selftest done",
        )
        self.assertEqual(1, code)
        self.assertIn("state proof not found", output)

    def test_failed_terminal_forces_failure_even_with_state_proof(self) -> None:
        code, output = self.run_grep(
            self.baseline()
            + [
                f"INFO [T2MOD-SELFTEST] {self.mod} state proof: damage 20 -> 14 delta=6",
                f"INFO [T2MOD-SELFTEST] {self.mod} selftest FAILED: play phase timeout",
            ],
            "damage.*delta=6",
        )
        self.assertEqual(1, code)
        self.assertIn("setup/navigation miss", output)

    def test_tier1_requires_exact_load_marker(self) -> None:
        code, _ = self.run_grep(
            ["RUNNING MODDED", f"INFO [T2MOD-SELFTEST] {self.mod} selftest done"]
        )
        self.assertEqual(1, code)

    def test_tier1_rejects_missing_framework_profile(self) -> None:
        code, output = self.run_grep([
            "RUNNING MODDED",
            f"INFO [T2MOD-SELFTEST] {self.mod} loaded ok",
        ])
        self.assertEqual(1, code)
        self.assertIn("profile is missing or mismatched", output)

    def test_tier1_accepts_newer_compatible_runtime_version(self) -> None:
        code, output = self.run_grep([
            "RUNNING MODDED",
            f"INFO [T2MOD-SELFTEST] {self.mod} loaded ok "
            "framework=RitsuLib frameworkVersion=0.5.12 host=0.107.1 compat=0.107.1",
        ])
        self.assertEqual(0, code)
        self.assertIn("Framework profile   : MATCH", output)

    def test_tier1_rejects_runtime_older_than_minimum(self) -> None:
        code, output = self.run_grep([
            "RUNNING MODDED",
            f"INFO [T2MOD-SELFTEST] {self.mod} loaded ok "
            "framework=RitsuLib frameworkVersion=0.5.10 host=0.107.1 compat=0.107.1",
        ])
        self.assertEqual(1, code)
        self.assertIn("frameworkVersion>=0.5.11", output)

    def test_mod_named_exception_fails(self) -> None:
        code, output = self.run_grep(
            self.baseline() + [f"ERROR {self.mod} NullReferenceException"]
        )
        self.assertEqual(1, code)
        self.assertIn("Fresh-run error block", output)

    def test_multiline_error_block_fails_when_continuation_names_mod(self) -> None:
        code, output = self.run_grep(
            self.baseline()
            + [
                "[ERROR] Failed to save progress: System.InvalidOperationException",
                "   at MegaCrit.Sts2.Core.Saves.SaveManager.Save()",
                f"   at {self.mod}.{self.mod}Code.SelfTest.RunAsync()",
            ]
        )
        self.assertEqual(1, code)
        self.assertIn("Failed to save progress", output)
        self.assertIn("SelfTest.RunAsync", output)

    def test_global_runtime_error_after_load_fails(self) -> None:
        code, output = self.run_grep(
            self.baseline() + ["[ERROR] Rendering device lost"]
        )
        self.assertEqual(1, code)
        self.assertIn("Rendering device lost", output)

    def test_exact_abandon_missing_backup_cleanup_is_ignored(self) -> None:
        code, output = self.run_grep(
            self.baseline()
            + [
                r"[ERROR] Error deleting path modded/profile1\saves\current_run.save.backup: Failed",
                "   at MegaCrit.Sts2.Core.Saves.Managers.RunSaveManager.DeleteCurrentRun()",
                "   at MegaCrit.Sts2.Core.Nodes.Screens.MainMenu.NMainMenu.AbandonRun()",
                "   at MegaCrit.Sts2.Core.AutoSlay.Helpers.UiHelper.Click(NClickableControl button, Int32 delayMs)",
            ]
        )
        self.assertEqual(0, code)
        self.assertIn("Known verification cleanup noise: IGNORED", output)

    def test_similar_backup_error_without_abandon_stack_still_fails(self) -> None:
        code, output = self.run_grep(
            self.baseline()
            + [
                r"[ERROR] Error deleting path modded/profile1\saves\current_run.save.backup: Failed",
                f"   at {self.mod}.{self.mod}Code.SelfTest.RunAsync()",
            ]
        )
        self.assertEqual(1, code)
        self.assertIn("Fresh-run error block", output)

    def test_exact_launcher_sentry_shutdown_cleanup_is_ignored(self) -> None:
        code, output = self.run_grep(
            self.baseline()
            + [
                "ERROR: Sentry: Failed to close native SDK cleanly. Error code: 1",
                "   at: sentry::native::NativeSDK::close (src/sentry/native/native_sdk.cpp:489)",
                "   at MegaCrit.Sts2.Core.Debug.SentryService.Shutdown()",
            ]
        )
        self.assertEqual(0, code)
        self.assertIn("Known verification cleanup noise: IGNORED", output)

    def test_similar_sentry_runtime_error_still_fails(self) -> None:
        code, output = self.run_grep(
            self.baseline()
            + [
                "ERROR: Sentry: Failed to send event. Error code: 1",
                "   at MegaCrit.Sts2.Core.Debug.SentryService.Shutdown()",
            ]
        )
        self.assertEqual(1, code)
        self.assertIn("Fresh-run error block", output)

    def test_unrelated_error_before_fresh_load_boundary_is_ignored(self) -> None:
        code, output = self.run_grep(
            [
                "[ERROR] HistoricalOtherMod failure",
                *self.baseline(),
            ]
        )
        self.assertEqual(0, code)
        self.assertIn("[PASS] Tier-1 verified", output)

    def test_last_load_marker_starts_fresh_appended_run(self) -> None:
        code, output = self.run_grep(
            [
                f"INFO [T2MOD-SELFTEST] {self.mod} loaded ok "
                "framework=RitsuLib frameworkVersion=0.5.11 host=0.107.1 compat=0.107.1",
                "[ERROR] failure from the previous appended run",
                f"INFO [T2MOD-SELFTEST] {self.mod} loaded ok "
                "framework=RitsuLib frameworkVersion=0.5.11 host=0.107.1 compat=0.107.1",
            ]
        )
        self.assertEqual(0, code)
        self.assertIn("[PASS] Tier-1 verified", output)

    def test_invalid_regex_is_usage_error(self) -> None:
        code, output = self.run_grep(self.baseline(), "[")
        self.assertEqual(2, code)
        self.assertIn("Invalid --tier2-pattern", output)


class LaunchOutcomeTests(unittest.TestCase):
    def test_steam_appid_is_written_beside_the_platform_executable(self) -> None:
        game = Path("steamapps") / "common" / "Slay the Spire 2"
        self.assertEqual(
            game / "steam_appid.txt",
            launch.steam_appid_path(game, "win32"),
        )
        self.assertEqual(
            game
            / "SlayTheSpire2.app"
            / "Contents"
            / "MacOS"
            / "steam_appid.txt",
            launch.steam_appid_path(game, "darwin"),
        )

    def test_done_is_success(self) -> None:
        self.assertEqual(0, launch.self_test_exit_code("done"))

    def test_failure_outcomes_are_nonzero(self) -> None:
        for outcome in ("failed", "timeout", "process-exited"):
            with self.subTest(outcome=outcome):
                self.assertEqual(1, launch.self_test_exit_code(outcome))

    def test_stale_terminal_marker_is_outside_current_launch_boundary(self) -> None:
        mod = "CanaryCard"
        stale = "\n".join([
            f"[T2MOD-SELFTEST] {mod} loaded ok",
            f"[T2MOD-SELFTEST] {mod} selftest done",
        ])
        self.assertEqual("", launch.log_since_launch(stale, stale))
        self.assertIsNone(
            launch.self_test_log_outcome(launch.log_since_launch(stale, stale), mod)
        )

    def test_terminal_requires_new_load_marker(self) -> None:
        mod = "CanaryCard"
        baseline = f"[T2MOD-SELFTEST] {mod} selftest done"
        appended_terminal = baseline + f"\n[T2MOD-SELFTEST] {mod} selftest done"
        current = launch.log_since_launch(baseline, appended_terminal)
        self.assertIsNone(launch.self_test_log_outcome(current, mod))

        appended_fresh_run = baseline + "\n" + "\n".join([
            f"[T2MOD-SELFTEST] {mod} loaded ok",
            f"[T2MOD-SELFTEST] {mod} selftest done",
        ])
        self.assertEqual("done", launch.self_test_log_outcome(
            launch.log_since_launch(baseline, appended_fresh_run), mod
        ))

        rotated = "\n".join([
            f"[T2MOD-SELFTEST] {mod} loaded ok",
            f"[T2MOD-SELFTEST] {mod} selftest done",
        ])
        self.assertEqual("done", launch.self_test_log_outcome(
            launch.log_since_launch(baseline, rotated), mod
        ))

    def test_failed_marker_dominates_done_in_current_launch(self) -> None:
        mod = "CanaryCard"
        current = "\n".join([
            f"[T2MOD-SELFTEST] {mod} loaded ok",
            f"[T2MOD-SELFTEST] {mod} selftest done",
            f"[T2MOD-SELFTEST] {mod} selftest FAILED: late assertion",
        ])
        self.assertEqual("failed", launch.self_test_log_outcome(current, mod))


if __name__ == "__main__":
    unittest.main()
