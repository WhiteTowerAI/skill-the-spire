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
    grep_log.py --tier2-pattern to verify the asserted state proof. The wait follows the
    harness's logged `selftest budget: <N>s` plus boot time unless --wait-seconds is given.
    Every other Mod folder with a t2selftest gate is parked outside mods/ for the run and
    restored afterwards; any launch first restores Mods that a killed run left parked.

The game dir is auto-detected by probing the local
Steam libraries (registry/standard roots -> libraryfolders.vdf -> appmanifest_2868840),
so a game installed on any drive/library is found without a hardcoded path. Executable
name and log path default per-OS. Only the Windows path is verified on the dev box; the
macOS/Linux Steam roots and Godot user-data dir are best-effort -- override with
--game-dir / --log-path if detection misses.

Usage:
  python launch.py --mod-name ExampleMod                  # tier-1: load, verify, close
  python launch.py --self-test --mod-name ExampleMod      # tier-2: self-drive, poll
  python launch.py --self-test --only "face.*,spark" --mod-name ExampleMod   # rerun a subset
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

import grep_log
from grep_log import default_log_path, load_marker, read_shared
from ritsu_profile import game_executable_dir, local_mods_dir

APPID = "2868840"
GAME_FOLDER = "Slay the Spire 2"
# STS2 0.107.1 logs this once the main menu is up. Mod initializers run before it, so a
# load marker that has not appeared by then never will.
MAIN_MENU_MARKER = "[Startup] Time to main menu"
TIER1_SETTLE_SECONDS = 5
# The harness logs its whole-scenario budget when it arms during Mod initialization. Boot
# before that and shutdown after it need their own allowance on top.
SELF_TEST_BOOT_ALLOWANCE = 90
DEFAULT_SELF_TEST_BUDGET = 180
DEFAULT_WAIT_SECONDS = {
    "tier1": 90,
    "self-test": DEFAULT_SELF_TEST_BUDGET + SELF_TEST_BOOT_ALLOWANCE,
}
BUDGET_RE = re.compile(r"selftest budget: (?P<seconds>\d+)s")
# `--t2selftest` arms every loaded harness, so other harness Mods wait here during a run.
PARK_DIR_NAME = "mods-parked-by-skill-the-spire"
HARNESS_GATE = "t2selftest"
FAILURE_OUTCOMES = {"assertion": "assertion-failed", "budget": "budget-exceeded", "setup": "failed"}


class ParkError(RuntimeError):
    pass


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
    """Read a terminal outcome only after this launch's exact mod-load marker.

    A FAILED line maps by its stage to `assertion-failed`, `budget-exceeded`, or `failed`
    (setup/navigation).
    """
    load_index = current_launch_log.rfind(load_marker(mod_name))
    if load_index < 0:
        return None

    after_load = current_launch_log[load_index:]
    fail_marker = f"{grep_log.MARKER} {mod_name} selftest FAILED"
    done_marker = f"{grep_log.MARKER} {mod_name} selftest done"
    for line in after_load.splitlines():
        if fail_marker in line:
            return FAILURE_OUTCOMES[grep_log.failure_kind(line, mod_name)]
    if done_marker in after_load:
        return "done"
    return None


def self_test_budget_seconds(current_launch_log: str, mod_name: str) -> int | None:
    """The harness's logged scenario budget after this launch's load marker, if any."""
    load_index = current_launch_log.rfind(load_marker(mod_name))
    if load_index < 0:
        return None
    budget_marker = f"{grep_log.MARKER} {mod_name} selftest budget:"
    for line in current_launch_log[load_index:].splitlines():
        if budget_marker in line:
            match = BUDGET_RE.search(line)
            return int(match.group("seconds")) if match else None
    return None


def poll_log(proc: subprocess.Popen, log_path: Path, baseline: str | None,
             wait_seconds: int, outcome_of, budget_of=None) -> str:
    """Poll this launch's log until outcome_of returns a value, the game exits, or timeout.

    With budget_of, the deadline grows to the logged harness budget plus boot allowance.
    """
    started = time.monotonic()
    deadline = started + wait_seconds
    budget_seen = False
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
        current = log_since_launch(baseline, txt)
        if budget_of is not None and not budget_seen:
            budget = budget_of(current)
            if budget is not None:
                budget_seen = True
                wanted = started + budget + SELF_TEST_BOOT_ALLOWANCE
                if wanted > deadline:
                    deadline = wanted
                    print(f"[launch] harness budget {budget}s; waiting up to "
                          f"{budget + SELF_TEST_BOOT_ALLOWANCE}s in total")
        outcome = outcome_of(current)
        if outcome is not None:
            return outcome
    return "timeout"


def parked_dir(game_dir: Path) -> Path:
    return game_executable_dir(game_dir) / PARK_DIR_NAME


def has_selftest_gate(mod_dir: Path) -> bool:
    """True when a DLL in the Mod folder carries the t2selftest gate (C# literals are UTF-16)."""
    needles = (HARNESS_GATE.encode("utf-16-le"), HARNESS_GATE.encode("ascii"))
    for dll in mod_dir.glob("*.dll"):
        try:
            data = dll.read_bytes()
        except OSError:
            continue
        if any(needle in data for needle in needles):
            return True
    return False


def restore_parked(game_dir: Path) -> list[str]:
    """Move every parked Mod back into mods/; never overwrite a same-named folder."""
    park = parked_dir(game_dir)
    if not park.is_dir():
        return []
    mods = local_mods_dir(game_dir)
    mods.mkdir(parents=True, exist_ok=True)
    restored: list[str] = []
    for entry in sorted(park.iterdir()):
        target = mods / entry.name
        if target.exists():
            raise ParkError(
                f"cannot restore parked Mod {entry.name}: {target} already exists. "
                f"Keep one copy and move the other out of {park} by hand."
            )
        try:
            shutil.move(str(entry), str(target))
        except OSError as exc:
            raise ParkError(f"cannot restore parked Mod {entry.name} to {target}: {exc}") from exc
        restored.append(entry.name)
    park.rmdir()
    return restored


def park_other_harnesses(game_dir: Path, mod_name: str) -> list[str]:
    """Park every other Mod folder with a self-test gate; undo all of it on any failure."""
    mods = local_mods_dir(game_dir)
    if not mods.is_dir():
        return []
    park = parked_dir(game_dir)
    parked: list[str] = []
    try:
        for entry in sorted(mods.iterdir()):
            if not entry.is_dir() or entry.name.casefold() == mod_name.casefold():
                continue
            if not has_selftest_gate(entry):
                continue
            park.mkdir(exist_ok=True)
            shutil.move(str(entry), str(park / entry.name))
            parked.append(entry.name)
    except OSError as exc:
        restore_parked(game_dir)
        raise ParkError(f"could not park other self-test Mods: {exc}") from exc
    return parked


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
                         "terminal marker for --self-test (default: the harness's logged "
                         f"budget + {SELF_TEST_BOOT_ALLOWANCE}s, at least "
                         f"{DEFAULT_WAIT_SECONDS['self-test']}s).")
    ap.add_argument("--self-test", action="store_true",
                    help="Append --t2selftest and poll for the harness done/FAILED marker.")
    ap.add_argument("--only", default=None, metavar="NAME[,NAME...]",
                    help="With --self-test: run only these SelfTestKit scenarios (a trailing * "
                         "matches a prefix). A partial run is never the final Tier 2.")
    ap.add_argument("--mod-name", required=True,
                    help="Mod name (Mod.json 'id') whose markers are verified.")
    ap.add_argument("--log-path", default=None, help="godot.log location")
    args = ap.parse_args(argv)
    if args.only is not None and not args.self_test:
        ap.error("--only needs --self-test")
    if args.only is not None and (not args.only.strip() or any(c.isspace() for c in args.only)):
        ap.error("--only takes comma-separated scenario names without spaces")

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

    # A run killed before its cleanup leaves user Mods parked; put them back first.
    if not restore_after_run(game_dir):
        return 2

    extra_args: list[str] = []
    if args.self_test:
        try:
            parked = park_other_harnesses(game_dir, args.mod_name)
        except ParkError as exc:
            print(f"[launch] {exc}", file=sys.stderr)
            return 2
        if parked:
            print(f"[launch] parked other self-test Mods for this run: {', '.join(parked)}")
        gate = f"--{HARNESS_GATE}" + (f"={args.only}" if args.only else "")
        extra_args.append(gate)
        print(f"[launch] SELF-TEST mode: passing {gate}; harness will self-drive its scenario")

    print(f"[launch] starting {exe.name} ...")
    try:
        proc = launch_process(exe, game_dir, extra_args)
    except BaseException:
        restore_after_run(game_dir)
        raise

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

    try:
        print(f"[launch] pid {proc.pid}; polling log up to {wait_seconds}s "
              f"for '{args.mod_name} selftest done|FAILED'")
        outcome = poll_log(
            proc, log_path, log_baseline, wait_seconds,
            lambda log: self_test_log_outcome(log, args.mod_name),
            None if args.wait_seconds else lambda log: self_test_budget_seconds(log, args.mod_name),
        )
        report_self_test_outcome(outcome, proc, wait_seconds, args.wait_seconds is not None)
    finally:
        stop_process(proc)
        restored_ok = restore_after_run(game_dir)
    if not restored_ok:
        return 2

    print(f'[launch] done. Now run grep_log.py --mod-name {args.mod_name} '
          '--tier2-pattern "<state-proof-pattern>" to check the fresh log.')
    return self_test_exit_code(outcome)


def report_self_test_outcome(outcome: str, proc: subprocess.Popen, wait_seconds: int,
                             explicit_wait: bool) -> None:
    if outcome == "done":
        print("[launch] harness reported: selftest DONE (scenario driven; verify its asserted state proof now)")
    elif outcome == "assertion-failed":
        print("[launch] harness reported: state proof FAILED (the scenario ran; the post-state "
              "was wrong) -- a behavior bug, classify it in repair.md", file=sys.stderr)
    elif outcome == "budget-exceeded":
        print("[launch] harness reported: scenario budget exceeded -- raise that scenario's "
              "budgetSeconds (or Budget in an older SelfTest.cs) for a long scenario, or repair "
              "the stalled step", file=sys.stderr)
    elif outcome == "failed":
        print("[launch] harness reported: selftest FAILED (couldn't reach/drive its scenario) -- "
              "verify.md: fall back to manual, report tier-1 only", file=sys.stderr)
    elif outcome == "process-exited":
        print(f"[launch] game exited with code {proc.returncode} before a harness terminal marker -- "
              "treat as harness/setup failure", file=sys.stderr)
    else:
        hint = ("rerun with a larger --wait-seconds" if explicit_wait
                else "no harness budget line was seen; check the load marker and the "
                     "SelfTestKit.Arm line in MainFile.cs")
        print(f"[launch] TIMEOUT after {wait_seconds}s with no terminal marker -- the launcher "
              f"stopped waiting; this is not evidence about the Mod ({hint})", file=sys.stderr)


def restore_after_run(game_dir: Path) -> bool:
    try:
        restored = restore_parked(game_dir)
    except ParkError as exc:
        print(f"[launch] {exc}", file=sys.stderr)
        return False
    if restored:
        print(f"[launch] restored parked Mods: {', '.join(restored)}")
    return True


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
