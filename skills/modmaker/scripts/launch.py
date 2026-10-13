#!/usr/bin/env python3
"""Launch STS2 out-of-Steam for verification, poll its fresh log, then close it.

Launch helper for modmaker's verify.md. Ensures steam_appid.txt (=2868840) exists in
the game dir so the game runs without Steam, launches it, polls this launch's
godot.log, then stops the process.

Two modes, both requiring --mod-name and bounded by --wait-seconds:
  default (tier-1) : poll until the game reaches its main menu, keep it open a few more
    seconds for late load errors, close, then run grep_log.py's Tier 1 check and print its
    verdict. One command proves the Mod loads.
  --self-test (t2) : pass --t2selftest so the mod's in-process harness drives itself
    from the main menu into the hosted scenario required by the mod and fires the
    effect with zero interaction. Poll until it prints its terminal marker
    ([T2MOD-SELFTEST] <ModName> selftest done | selftest FAILED), close, then pair with
    grep_log.py --tier2-pattern to verify the asserted state proof.

The game dir is auto-detected by probing the local
Steam libraries (registry/standard roots -> libraryfolders.vdf -> appmanifest_2868840),
so a game installed on any drive/library is found without a hardcoded path. Executable
name and log path default per-OS. Only the Windows path is verified on the dev box; the
macOS/Linux Steam roots and Godot user-data dir are best-effort -- override with
--game-dir / --log-path if detection misses.

Usage:
  python launch.py --mod-name ExampleMod                  # tier-1: load, verify, close
  python launch.py --self-test --mod-name ExampleMod      # tier-2: self-drive, poll
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import time
from pathlib import Path

import grep_log
from grep_log import default_log_path, load_marker, read_shared
from ritsu_profile import game_executable_dir

APPID = "2868840"
GAME_FOLDER = "Slay the Spire 2"
# STS2 0.107.1 logs this once the main menu is up. Mod initializers run before it, so a
# load marker that has not appeared by then never will.
MAIN_MENU_MARKER = "[Startup] Time to main menu"
TIER1_SETTLE_SECONDS = 5
DEFAULT_WAIT_SECONDS = {"tier1": 90, "self-test": 180}


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


def tier1_log_outcome(current_launch_log: str) -> str | None:
    """'ready' once this launch reached the main menu, after every Mod initializer ran."""
    return "ready" if MAIN_MENU_MARKER in current_launch_log else None


def self_test_log_outcome(current_launch_log: str, mod_name: str) -> str | None:
    """Read a terminal outcome only after this launch's exact mod-load marker."""
    load_index = current_launch_log.rfind(load_marker(mod_name))
    if load_index < 0:
        return None

    after_load = current_launch_log[load_index:]
    fail_marker = f"{grep_log.MARKER} {mod_name} selftest FAILED"
    done_marker = f"{grep_log.MARKER} {mod_name} selftest done"
    if fail_marker in after_load:
        return "failed"
    if done_marker in after_load:
        return "done"
    return None


def poll_log(proc: subprocess.Popen, log_path: Path, baseline: str | None,
             wait_seconds: int, outcome_of) -> str:
    """Poll this launch's log until outcome_of returns a value, the game exits, or timeout."""
    deadline = time.monotonic() + wait_seconds
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            return "process-exited"
        time.sleep(2)
        if not log_path.is_file():
            continue
        try:
            txt = read_shared(log_path)
        except OSError:
            continue
        outcome = outcome_of(log_since_launch(baseline, txt))
        if outcome is not None:
            return outcome
    return "timeout"


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
    ap.add_argument("--wait-seconds", type=int, default=None,
                    help="Max seconds to poll: main menu for Tier 1 (default 90), harness "
                         "terminal marker for --self-test (default 180).")
    ap.add_argument("--self-test", action="store_true",
                    help="Append --t2selftest and poll for the harness done/FAILED marker.")
    ap.add_argument("--mod-name", required=True,
                    help="Mod name (Mod.json 'id') whose markers are verified.")
    ap.add_argument("--log-path", default=None, help="godot.log location")
    args = ap.parse_args(argv)

    game_dir = Path(args.game_dir) if args.game_dir else default_game_dir()
    log_path = Path(args.log_path) if args.log_path else default_log_path()
    mode = "self-test" if args.self_test else "tier1"
    wait_seconds = args.wait_seconds or DEFAULT_WAIT_SECONDS[mode]

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
    # stale main-menu or terminal marker can never satisfy this launch.
    log_baseline: str | None = None
    if log_path.is_file():
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

    if not args.self_test:
        print(f"[launch] pid {proc.pid}; polling log up to {wait_seconds}s for the main menu")
        outcome = poll_log(proc, log_path, log_baseline, wait_seconds, tier1_log_outcome)
        if outcome == "ready":
            time.sleep(TIER1_SETTLE_SECONDS)
        elif outcome == "process-exited":
            print(f"[launch] game exited with code {proc.returncode} before the main menu",
                  file=sys.stderr)
        else:
            print(f"[launch] main menu not seen within {wait_seconds}s", file=sys.stderr)
        stop_process(proc)
        return grep_log.main(["--mod-name", args.mod_name, "--log-path", str(log_path)])

    print(f"[launch] pid {proc.pid}; polling log up to {wait_seconds}s "
          f"for '{args.mod_name} selftest done|FAILED'")
    outcome = poll_log(proc, log_path, log_baseline, wait_seconds,
                       lambda log: self_test_log_outcome(log, args.mod_name))
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

    stop_process(proc)

    print(f'[launch] done. Now run grep_log.py --mod-name {args.mod_name} '
          '--tier2-pattern "<state-proof-pattern>" to check the fresh log.')
    return self_test_exit_code(outcome)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
