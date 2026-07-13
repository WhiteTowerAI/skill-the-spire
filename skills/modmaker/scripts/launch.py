#!/usr/bin/env python3
"""Launch STS2 out-of-Steam for load verification, wait, then close it.

R2 launch step (modmaker's verify.md). Ensures steam_appid.txt (=2868840) exists in
the game dir so the game runs without Steam, launches it, waits, then stops the
process. Does NOT assert anything itself -- pair with grep_log.py to check for the
[T2MOD-SELFTEST] marker.

Two modes:
  default (tier-1) : launch, wait a fixed --wait-seconds, close. Proves it loads.
  --self-test (t2) : pass --t2selftest so the mod's in-process harness drives itself
    from the main menu into a minimal combat and fires the effect with zero
    interaction. Instead of a fixed wait, POLL the log until the harness prints its
    terminal marker ([T2MOD-SELFTEST] <ModName> selftest done | selftest FAILED),
    bounded by --wait-seconds. Requires --mod-name.

Cross-platform port of launch.ps1. Game dir, executable name, and log path default
per-OS; only the Windows values are verified on the dev box. On macOS/Linux the
defaults follow Steam's standard install layout and Godot's user-data dir
(best-effort) -- override with --game-dir / --log-path if they differ.

Usage:
  python launch.py                                        # tier-1: launch, wait, close
  python launch.py --self-test --mod-name CanaryCard      # tier-2: self-drive, poll
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import time
from pathlib import Path

APPID = "2868840"

def default_game_dir() -> Path:
    if sys.platform.startswith("win"):
        return Path(r"D:\Steam\steamapps\common\Slay the Spire 2")
    if sys.platform == "darwin":
        return (Path.home() / "Library" / "Application Support" / "Steam"
                / "steamapps" / "common" / "Slay the Spire 2")
    return (Path.home() / ".steam" / "steam" / "steamapps"
            / "common" / "Slay the Spire 2")


def default_exe_name() -> str:
    if sys.platform.startswith("win"):
        return "SlayTheSpire2.exe"
    if sys.platform == "darwin":
        # macOS ships an .app bundle; the inner binary is launched via `open`.
        return "SlayTheSpire2.app"
    return "SlayTheSpire2.x86_64"


def default_log_path() -> Path:
    if sys.platform.startswith("win"):
        base = os.environ.get("APPDATA", str(Path.home() / "AppData" / "Roaming"))
        return Path(base) / "SlayTheSpire2" / "logs" / "godot.log"
    if sys.platform == "darwin":
        return (Path.home() / "Library" / "Application Support"
                / "SlayTheSpire2" / "logs" / "godot.log")
    xdg = os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local" / "share"))
    return Path(xdg) / "SlayTheSpire2" / "logs" / "godot.log"


def launch_process(exe: Path, game_dir: Path, extra_args: list[str]) -> subprocess.Popen:
    """Start the game detached-ish. On macOS an .app bundle is opened via `open`."""
    if sys.platform == "darwin" and exe.suffix == ".app":
        cmd = ["open", "-a", str(exe)]
        if extra_args:
            cmd += ["--args", *extra_args]
        return subprocess.Popen(cmd, cwd=str(game_dir))
    return subprocess.Popen([str(exe), *extra_args], cwd=str(game_dir))


def read_shared(path: Path) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


def stop_process(proc: subprocess.Popen) -> None:
    if proc.poll() is not None:
        return
    print("[launch] closing game")
    proc.terminate()
    try:
        proc.wait(timeout=8)
    except subprocess.TimeoutExpired:
        proc.kill()


def self_test_exit_code(outcome: str) -> int:
    """Map a self-test terminal outcome to the CLI contract."""
    return 0 if outcome == "done" else 1


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Launch STS2 out-of-Steam for verification")
    ap.add_argument("--game-dir", default=None, help="STS2 install dir")
    ap.add_argument("--wait-seconds", type=int, default=25,
                    help="Tier-1: seconds to load before closing (default 25). "
                         "--self-test: max seconds to wait for the harness marker.")
    ap.add_argument("--self-test", action="store_true",
                    help="Append --t2selftest and poll for the harness done/FAILED marker.")
    ap.add_argument("--mod-name", default="",
                    help="Required with --self-test: whose 'selftest done' marker to poll for.")
    ap.add_argument("--log-path", default=None, help="godot.log location")
    args = ap.parse_args(argv)

    game_dir = Path(args.game_dir) if args.game_dir else default_game_dir()
    log_path = Path(args.log_path) if args.log_path else default_log_path()
    wait_seconds = args.wait_seconds

    if args.self_test:
        if not args.mod_name:
            print("--self-test requires --mod-name (whose 'selftest done' marker to wait for).",
                  file=sys.stderr)
            return 2
        if wait_seconds < 60:
            wait_seconds = 180  # self-test needs real time; don't inherit the 25s tier-1 default

    exe = game_dir / default_exe_name()
    if not exe.exists():
        print(f"{exe.name} not found in {game_dir}. Pass --game-dir with the real install path.",
              file=sys.stderr)
        return 2

    # No-Steam launch: steam_appid.txt must sit next to the exe.
    appid_file = game_dir / "steam_appid.txt"
    if not appid_file.exists():
        appid_file.write_text(APPID, encoding="ascii")
        print(f"[launch] created steam_appid.txt ({APPID}) for no-Steam launch")

    # STS2 archives the old log and starts a fresh godot.log on launch, so grep_log.py
    # just reads the whole current file afterward -- no offset bookkeeping needed here.
    extra_args: list[str] = []
    if args.self_test:
        extra_args.append("--t2selftest")
        print("[launch] SELF-TEST mode: passing --t2selftest; harness will self-drive to combat")

    print(f"[launch] starting {exe.name} ...")
    proc = launch_process(exe, game_dir, extra_args)

    if args.self_test:
        done_marker = f"[T2MOD-SELFTEST] {args.mod_name} selftest done"
        fail_marker = f"[T2MOD-SELFTEST] {args.mod_name} selftest FAILED"
        print(f"[launch] pid {proc.pid}; polling log up to {wait_seconds}s "
              f"for '{args.mod_name} selftest done|FAILED'")
        deadline = time.monotonic() + wait_seconds
        outcome = "timeout"
        while time.monotonic() < deadline:
            if proc.poll() is not None:
                outcome = "process-exited"
                break
            time.sleep(2)
            if not log_path.is_file():
                continue
            try:
                txt = read_shared(log_path)
            except OSError:
                continue
            if done_marker in txt:
                outcome = "done"
                break
            if fail_marker in txt:
                outcome = "failed"
                break
        if outcome == "done":
            print("[launch] harness reported: selftest DONE (effect driven; grep for the fired/used marker now)")
        elif outcome == "failed":
            print("[launch] harness reported: selftest FAILED (couldn't reach/drive combat) -- "
                  "verify.md: fall back to manual, report tier-1 only", file=sys.stderr)
        elif outcome == "process-exited":
            print(f"[launch] game exited with code {proc.returncode} before a harness terminal marker -- "
                  "treat as harness/setup failure", file=sys.stderr)
        else:
            print(f"[launch] TIMEOUT after {wait_seconds}s with no terminal marker -- "
                  "treat as harness setup failure (manual fallback)", file=sys.stderr)
    else:
        print(f"[launch] pid {proc.pid}; waiting {wait_seconds}s for load")
        time.sleep(wait_seconds)

    stop_process(proc)

    tier2_hint = ' --tier2-pattern "fired|used|played"' if args.self_test else ""
    print(f"[launch] done. Now run grep_log.py --mod-name {args.mod_name or '<ModName>'}{tier2_hint} "
          "to check the fresh log.")
    return self_test_exit_code(outcome) if args.self_test else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
