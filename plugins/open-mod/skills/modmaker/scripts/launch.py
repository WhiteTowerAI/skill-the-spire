#!/usr/bin/env python3
"""Launch STS2 out-of-Steam for load verification, wait, then close it.

R2 launch step (modmaker's verify.md). Ensures steam_appid.txt (=2868840) exists in
the game dir so the game runs without Steam, launches it, waits, then stops the
process. Pair with grep_log.py to verify the resulting state-proof marker.

Two modes:
  default (tier-1) : launch, wait a fixed --wait-seconds, close. Proves it loads.
  --self-test (t2) : pass --t2selftest so the mod's in-process harness drives itself
    from the main menu into the hosted scenario required by the mod and fires the
    effect with zero interaction. Instead of a fixed wait, POLL the log until it prints its
    terminal marker ([T2MOD-SELFTEST] <ModName> selftest done | selftest FAILED),
    bounded by --wait-seconds. Requires --mod-name.

Cross-platform port of launch.ps1. The game dir is auto-detected by probing the local
Steam libraries (registry/standard roots -> libraryfolders.vdf -> appmanifest_2868840),
so a game installed on any drive/library is found without a hardcoded path. Executable
name and log path default per-OS. Only the Windows path is verified on the dev box; the
macOS/Linux Steam roots and Godot user-data dir are best-effort -- override with
--game-dir / --log-path if detection misses.

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

from ritsu_profile import game_executable_dir

APPID = "2868840"
GAME_FOLDER = "Slay the Spire 2"


def steam_roots() -> list[Path]:
    """Candidate Steam install roots per-OS (the dir that contains steamapps/)."""
    roots: list[Path] = []
    if sys.platform.startswith("win"):
        # Prefer the registry's recorded path; fall back to the common defaults.
        try:
            import winreg  # Windows-only; import lazily so other OSes don't choke.

            for hive, key in ((winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam"),
                              (winreg.HKEY_LOCAL_MACHINE, r"Software\WOW6432Node\Valve\Steam")):
                try:
                    with winreg.OpenKey(hive, key) as handle:
                        value = winreg.QueryValueEx(handle, "SteamPath")[0]
                        if value:
                            roots.append(Path(value))
                except OSError:
                    continue
        except ImportError:
            pass
        for drive in ("C:", "D:", "E:"):
            roots.append(Path(f"{drive}\\Program Files (x86)\\Steam"))
            roots.append(Path(f"{drive}\\Steam"))
    elif sys.platform == "darwin":
        roots.append(Path.home() / "Library" / "Application Support" / "Steam")
    else:
        roots.append(Path.home() / ".steam" / "steam")
        roots.append(Path.home() / ".local" / "share" / "Steam")
        roots.append(Path.home() / ".var" / "app" / "com.valvesoftware.Steam"
                     / "data" / "Steam")  # Flatpak
    return roots


def library_dirs(root: Path) -> list[Path]:
    """Every steamapps dir Steam knows about, parsed from libraryfolders.vdf.

    Games can live in any library on any drive; the vdf lists them all. We only
    need the "path" entries, so a light regex over the file is enough (no vdf lib).
    """
    steamapps = root / "steamapps"
    dirs: list[Path] = [steamapps]
    vdf = steamapps / "libraryfolders.vdf"
    if vdf.is_file():
        try:
            text = vdf.read_text(encoding="utf-8", errors="replace")
        except OSError:
            text = ""
        for match in re.finditer(r'"path"\s*"([^"]+)"', text):
            lib = Path(match.group(1).replace("\\\\", "\\")) / "steamapps"
            if lib not in dirs:
                dirs.append(lib)
    return dirs


def detect_game_dir() -> Path | None:
    """Locate the STS2 install by walking Steam's libraries; None if not found."""
    seen: set[Path] = set()
    for root in steam_roots():
        if not root.is_dir():
            continue
        for steamapps in library_dirs(root):
            if steamapps in seen:
                continue
            seen.add(steamapps)
            # appmanifest is authoritative for the on-disk folder name.
            manifest = steamapps / f"appmanifest_{APPID}.acf"
            candidate = steamapps / "common" / GAME_FOLDER
            if manifest.is_file():
                try:
                    text = manifest.read_text(encoding="utf-8", errors="replace")
                    m = re.search(r'"installdir"\s*"([^"]+)"', text)
                    if m:
                        candidate = steamapps / "common" / m.group(1)
                except OSError:
                    pass
            if candidate.is_dir():
                return candidate
    return None


def fallback_game_dir() -> Path:
    """Standard per-OS install path, used only when Steam-library detection misses."""
    if sys.platform.startswith("win"):
        return Path(r"C:\Program Files (x86)\Steam\steamapps\common") / GAME_FOLDER
    if sys.platform == "darwin":
        return (Path.home() / "Library" / "Application Support" / "Steam"
                / "steamapps" / "common" / GAME_FOLDER)
    return (Path.home() / ".steam" / "steam" / "steamapps" / "common" / GAME_FOLDER)


def default_game_dir() -> Path:
    return detect_game_dir() or fallback_game_dir()


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


def steam_appid_path(game_dir: Path, platform_name: str | None = None) -> Path:
    return game_executable_dir(game_dir, platform_name) / "steam_appid.txt"


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


def log_since_launch(baseline: str | None, current: str) -> str:
    """Return only log text produced by the current launch.

    Godot normally replaces godot.log on startup, but polling can begin before that
    rotation. If it appends instead, retain only the suffix beyond the captured
    baseline. A replacement/truncation cannot start with the complete old content,
    so its full contents belong to this launch.
    """
    if baseline is None:
        return current
    if current.startswith(baseline):
        return current[len(baseline):]
    return current


def self_test_log_outcome(current_launch_log: str, mod_name: str) -> str | None:
    """Read a terminal outcome only after this launch's exact mod-load marker."""
    marker = "[T2MOD-SELFTEST]"
    load_marker = f"{marker} {mod_name} loaded ok"
    load_index = current_launch_log.rfind(load_marker)
    if load_index < 0:
        return None

    after_load = current_launch_log[load_index:]
    fail_marker = f"{marker} {mod_name} selftest FAILED"
    done_marker = f"{marker} {mod_name} selftest done"
    if fail_marker in after_load:
        return "failed"
    if done_marker in after_load:
        return "done"
    return None


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
    appid_file = steam_appid_path(game_dir)
    if not appid_file.exists():
        appid_file.write_text(APPID, encoding="ascii")
        print(f"[launch] created steam_appid.txt ({APPID}) for no-Steam launch")

    # Polling can start before Godot rotates godot.log. Capture the old contents so a
    # stale terminal marker can never satisfy this launch's self-test.
    log_baseline: str | None = None
    if args.self_test and log_path.is_file():
        try:
            log_baseline = read_shared(log_path)
        except OSError as exc:
            print(f"Could not capture pre-launch log boundary from {log_path}: {exc}",
                  file=sys.stderr)
            return 2

    extra_args: list[str] = []
    if args.self_test:
        extra_args.append("--t2selftest")
        print("[launch] SELF-TEST mode: passing --t2selftest; harness will self-drive its scenario")

    print(f"[launch] starting {exe.name} ...")
    proc = launch_process(exe, game_dir, extra_args)

    if args.self_test:
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
            current_outcome = self_test_log_outcome(log_since_launch(log_baseline, txt),
                                                    args.mod_name)
            if current_outcome is not None:
                outcome = current_outcome
                break
        if outcome == "done":
            print("[launch] harness reported: selftest DONE (scenario driven; verify its asserted state proof now)")
        elif outcome == "failed":
            print("[launch] harness reported: selftest FAILED (couldn't reach/drive its scenario) -- "
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

    tier2_hint = ' --tier2-pattern "<state-proof-pattern>"' if args.self_test else ""
    print(f"[launch] done. Now run grep_log.py --mod-name {args.mod_name or '<ModName>'}{tier2_hint} "
          "to check the fresh log.")
    return self_test_exit_code(outcome) if args.self_test else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
