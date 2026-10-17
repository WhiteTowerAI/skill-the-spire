from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

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
    mod = "ExampleMod"

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
            "framework=RitsuLib frameworkVersion=0.6.7 host=0.107.1 compat=0.107.1",
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
            "framework=RitsuLib frameworkVersion=0.6.8 host=0.107.1 compat=0.107.1",
        ])
        self.assertEqual(0, code)
        self.assertIn("Framework profile   : MATCH", output)

    def test_tier1_rejects_runtime_older_than_minimum(self) -> None:
        code, output = self.run_grep([
            "RUNNING MODDED",
            f"INFO [T2MOD-SELFTEST] {self.mod} loaded ok "
            "framework=RitsuLib frameworkVersion=0.6.6 host=0.107.1 compat=0.107.1",
        ])
        self.assertEqual(1, code)
        self.assertIn("frameworkVersion>=0.6.7", output)

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

    def abandon_missing_model(self, model: str, exception: str = "ModelNotFoundException",
                              abandon: bool = True) -> list[str]:
        # Observed 2026-10-17 when the harness abandoned a run whose character Mod was parked.
        lines = [
            "[ERROR] ERROR: Failed to upload run history/metrics: "
            f"MegaCrit.Sts2.Core.Models.Exceptions.{exception}: Model id={model} not found",
            "   at MegaCrit.Sts2.Core.Models.ModelDb.GetById[T](ModelId id)",
            "   at STS2RitsuLib.Unlocks.Patches.PostRunCharacterUnlockEpochCompatibilityPatch"
            ".Prefix(SerializablePlayer serializablePlayer, SerializableRun serializableRun)",
            "   at MegaCrit.Sts2.Core.Saves.SaveManager.UpdateProgressWithRunData("
            "SerializableRun serializableRun, Boolean victory)",
        ]
        if abandon:
            lines += [
                "   at MegaCrit.Sts2.Core.Nodes.Screens.MainMenu.NMainMenu.AbandonRun()",
                "   at MegaCrit.Sts2.Core.AutoSlay.Helpers.UiHelper.Click("
                "NClickableControl button, Int32 delayMs)",
            ]
        return lines

    def test_abandoning_a_parked_mods_run_is_ignored(self) -> None:
        code, output = self.run_grep(
            self.baseline() + self.abandon_missing_model("CHARACTER.ZHANG_JUE_CHARACTER_ZHANG_JUE")
        )
        self.assertEqual(0, code, output)
        self.assertIn("Known verification cleanup noise: IGNORED", output)

    def test_missing_model_near_misses_still_fail(self) -> None:
        cases = {
            "own model": self.abandon_missing_model("CHARACTER.EXAMPLE_MOD_CHARACTER_HERO"),
            "no abandon stack": self.abandon_missing_model(
                "CHARACTER.ZHANG_JUE_CHARACTER_ZHANG_JUE", abandon=False),
            "other exception": self.abandon_missing_model(
                "CHARACTER.ZHANG_JUE_CHARACTER_ZHANG_JUE", exception="NullReferenceException"),
        }
        for name, block in cases.items():
            with self.subTest(case=name):
                code, output = self.run_grep(self.baseline() + block)
                self.assertEqual(1, code, output)
                self.assertIn("[FAIL] Fresh-run error block", output)

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
                "framework=RitsuLib frameworkVersion=0.6.7 host=0.107.1 compat=0.107.1",
                "[ERROR] failure from the previous appended run",
                f"INFO [T2MOD-SELFTEST] {self.mod} loaded ok "
                "framework=RitsuLib frameworkVersion=0.6.7 host=0.107.1 compat=0.107.1",
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
        mod = "ExampleMod"
        stale = "\n".join([
            f"[T2MOD-SELFTEST] {mod} loaded ok",
            f"[T2MOD-SELFTEST] {mod} selftest done",
        ])
        self.assertEqual("", launch.log_since_launch(stale, stale))
        self.assertIsNone(
            launch.self_test_log_outcome(launch.log_since_launch(stale, stale), mod)
        )

    def test_terminal_requires_new_load_marker(self) -> None:
        mod = "ExampleMod"
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

    def test_tier1_ready_needs_this_launch_main_menu(self) -> None:
        menu = "[INFO] [Startup] Time to main menu: 10,516ms"
        self.assertIsNone(launch.tier1_log_outcome("[INFO] Preloading assets"))
        self.assertEqual("ready", launch.tier1_log_outcome(menu))
        self.assertIsNone(launch.tier1_log_outcome(launch.log_since_launch(menu, menu)))

    def test_failed_marker_dominates_done_in_current_launch(self) -> None:
        mod = "ExampleMod"
        current = "\n".join([
            f"[T2MOD-SELFTEST] {mod} loaded ok",
            f"[T2MOD-SELFTEST] {mod} selftest done",
            f"[T2MOD-SELFTEST] {mod} selftest FAILED: late assertion",
        ])
        self.assertEqual("failed", launch.self_test_log_outcome(current, mod))

    def test_failed_stage_separates_assertion_budget_and_setup(self) -> None:
        mod = "ExampleMod"
        cases = {
            "state proof: block expected=5 observed=3": "assertion-failed",
            "timeout: scenario budget 180s exceeded": "budget-exceeded",
            "AutoSlayTimeoutException: play phase not reached": "failed",
        }
        for stage, expected in cases.items():
            with self.subTest(stage=stage):
                current = "\n".join([
                    f"[T2MOD-SELFTEST] {mod} loaded ok",
                    f"[INFO] [T2MOD-SELFTEST] {mod} selftest FAILED: {stage}",
                ])
                self.assertEqual(expected, launch.self_test_log_outcome(current, mod))
                self.assertEqual(1, launch.self_test_exit_code(expected))

    def test_budget_is_read_after_this_launch_load_marker(self) -> None:
        mod = "ExampleMod"
        self.assertIsNone(launch.self_test_budget_seconds(
            f"[T2MOD-SELFTEST] {mod} selftest budget: 600s", mod))
        current = "\n".join([
            f"[T2MOD-SELFTEST] {mod} loaded ok",
            f"[INFO] [T2MOD-SELFTEST] {mod} selftest budget: 420s",
        ])
        self.assertEqual(420, launch.self_test_budget_seconds(current, mod))

    def test_logged_budget_extends_the_wait(self) -> None:
        clock = iter(range(100_000))
        with tempfile.TemporaryDirectory() as tmp:
            log_path = Path(tmp) / "godot.log"
            log_path.write_text("x", encoding="utf-8")
            for budget, expected in ((None, "timeout"), (300, "done")):
                with self.subTest(budget=budget):
                    reads = iter(range(100_000))
                    outcome_of = lambda _log: "done" if next(reads) >= 50 else None
                    with mock.patch.object(launch.time, "monotonic", lambda: next(clock)), \
                            mock.patch.object(launch.time, "sleep"), \
                            contextlib.redirect_stdout(io.StringIO()):
                        outcome = launch.poll_log(
                            FakeGame(), log_path, None, 10, outcome_of,
                            (lambda _log: budget) if budget else None,
                        )
                    self.assertEqual(expected, outcome)


def write_mod(mods: Path, name: str, gated: bool) -> None:
    folder = mods / name
    folder.mkdir(parents=True)
    body = "t2selftest".encode("utf-16-le") if gated else b"plain"
    (folder / f"{name}.dll").write_bytes(b"MZ" + body)


class ParkingTests(unittest.TestCase):
    def test_parks_only_other_gated_mods_and_restores_them(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            game = Path(tmp)
            mods = game / "mods"
            write_mod(mods, "Target", True)
            write_mod(mods, "OtherHarness", True)
            write_mod(mods, "PlainMod", False)
            parked = launch.park_other_harnesses(game, "target")
            self.assertEqual(["OtherHarness"], parked)
            self.assertEqual({"PlainMod", "Target"}, {p.name for p in mods.iterdir()})
            self.assertEqual(["OtherHarness"], launch.restore_parked(game))
            self.assertEqual({"OtherHarness", "PlainMod", "Target"},
                             {p.name for p in mods.iterdir()})
            self.assertFalse(launch.parked_dir(game).exists())

    def test_restore_refuses_to_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            game = Path(tmp)
            write_mod(game / "mods", "Other", True)
            write_mod(launch.parked_dir(game), "Other", True)
            with self.assertRaisesRegex(launch.ParkError, "already exists"):
                launch.restore_parked(game)

    def run_self_test(self, game: Path, log_lines: list[str], during=None) -> tuple[int, str]:
        (game / launch.default_exe_name()).write_text("", encoding="utf-8")
        log_path = game / "godot.log"

        def start_game(*_args):
            if during:
                during()
            log_path.write_text("\n".join(log_lines), encoding="utf-8")
            return FakeGame()

        output = io.StringIO()
        with mock.patch.object(launch, "launch_process", start_game), \
                mock.patch.object(launch.time, "sleep"), \
                contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            code = launch.main([
                "--self-test", "--mod-name", "Target", "--game-dir", str(game),
                "--log-path", str(log_path), "--wait-seconds", "5",
            ])
        return code, output.getvalue()

    def test_self_test_run_parks_during_and_restores_after(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            game = Path(tmp)
            mods = game / "mods"
            write_mod(mods, "Target", True)
            write_mod(mods, "OtherHarness", True)
            seen: list[set[str]] = []
            code, output = self.run_self_test(game, [
                "[T2MOD-SELFTEST] Target loaded ok",
                "[T2MOD-SELFTEST] Target selftest FAILED: state proof: block observed=3",
            ], during=lambda: seen.append({p.name for p in mods.iterdir()}))
            self.assertEqual(1, code)
            self.assertEqual([{"Target"}], seen)
            self.assertIn("behavior bug", output)
            self.assertEqual({"OtherHarness", "Target"}, {p.name for p in mods.iterdir()})

    def test_leftover_parked_mods_are_restored_first(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            game = Path(tmp)
            write_mod(game / "mods", "Target", True)
            write_mod(launch.parked_dir(game), "Forgotten", True)
            seen: list[set[str]] = []
            code, output = self.run_self_test(game, [
                "[T2MOD-SELFTEST] Target loaded ok",
                "[T2MOD-SELFTEST] Target selftest done",
            ], during=lambda: seen.append(
                {p.name for p in launch.parked_dir(game).iterdir()}))
            self.assertEqual(0, code, output)
            self.assertEqual([{"Forgotten"}], seen)
            self.assertEqual({"Forgotten", "Target"},
                             {p.name for p in (game / "mods").iterdir()})

    def test_restore_runs_when_polling_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            game = Path(tmp)
            mods = game / "mods"
            write_mod(mods, "Target", True)
            write_mod(mods, "OtherHarness", True)
            with mock.patch.object(launch, "poll_log", side_effect=KeyboardInterrupt), \
                    self.assertRaises(KeyboardInterrupt):
                self.run_self_test(game, [])
            self.assertEqual({"OtherHarness", "Target"}, {p.name for p in mods.iterdir()})


class FakeGame:
    returncode = None

    def __init__(self) -> None:
        self.pid = 1
        self.stopped = False

    def poll(self):
        return 0 if self.stopped else None

    def terminate(self) -> None:
        self.stopped = True

    def wait(self, timeout: float | None = None) -> int:
        return 0

    def kill(self) -> None:
        self.stopped = True


class Tier1CommandTests(unittest.TestCase):
    mod = "ExampleMod"

    def run_tier1(self, fresh_log: list[str]) -> tuple[int, str]:
        with tempfile.TemporaryDirectory() as tmp:
            game_dir = Path(tmp) / "game"
            game_dir.mkdir()
            (game_dir / launch.default_exe_name()).write_text("", encoding="utf-8")
            log_path = Path(tmp) / "godot.log"
            log_path.write_text(
                f"[T2MOD-SELFTEST] {self.mod} loaded ok from an older launch\n"
                "[INFO] [Startup] Time to main menu: 1ms\n",
                encoding="utf-8",
            )

            def start_game(*_args):
                log_path.write_text("\n".join(fresh_log), encoding="utf-8")
                return FakeGame()

            output = io.StringIO()
            with mock.patch.object(launch, "launch_process", start_game), \
                    mock.patch.object(launch.time, "sleep"), \
                    contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                code = launch.main([
                    "--mod-name", self.mod,
                    "--game-dir", str(game_dir),
                    "--log-path", str(log_path),
                    "--wait-seconds", "5",
                ])
            return code, output.getvalue()

    def loaded(self) -> list[str]:
        return [
            "RUNNING MODDED",
            f"[INFO] [T2MOD-SELFTEST] {self.mod} loaded ok "
            "framework=RitsuLib frameworkVersion=0.6.7 host=0.107.1 compat=0.107.1",
            "[INFO] [Startup] Time to main menu: 10,516ms",
        ]

    def test_tier1_command_prints_pass_verdict(self) -> None:
        code, output = self.run_tier1(self.loaded())
        self.assertEqual(0, code, output)
        self.assertIn("[PASS] Tier-1 verified", output)

    def test_tier1_command_fails_on_fresh_error(self) -> None:
        code, output = self.run_tier1(
            self.loaded() + ["[ERROR] System.NullReferenceException: boom"]
        )
        self.assertEqual(1, code)
        self.assertIn("[FAIL] Fresh-run error block", output)

    def test_tier1_command_fails_without_load_marker(self) -> None:
        code, output = self.run_tier1(["[INFO] [Startup] Time to main menu: 10,516ms"])
        self.assertEqual(1, code)
        self.assertIn("[FAIL] Load marker missing", output)

    def test_mod_name_is_required(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as caught:
            launch.main([])
        self.assertEqual(2, caught.exception.code)


if __name__ == "__main__":
    unittest.main()
