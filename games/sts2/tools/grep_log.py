#!/usr/bin/env python3
"""Grep godot.log for the [T2MOD-SELFTEST] load marker and any mod-related errors.

R2 verify step (modmaker's verify.md). Reads the CURRENT godot.log in full. STS2
archives the previous log (renaming it to godot<timestamp>.log) and starts a fresh
godot.log on every launch, so the current file already contains exactly one run --
no byte-offset slicing is needed, and offsets from a prior file are meaningless
against the new one (that was the tier-1 false-FAIL bug). Exits 0 if the mod's load
marker is found AND no error lines name the mod; exits 1 otherwise.

Cross-platform port of grep_log.ps1. The log path defaults per-OS:
  Windows : %APPDATA%\\SlayTheSpire2\\logs\\godot.log
  macOS   : ~/Library/Application Support/SlayTheSpire2/logs/godot.log
  Linux   : ~/.local/share/SlayTheSpire2/logs/godot.log
Override with --log-path. Only the Windows path is verified on the dev box; the
mac/Linux defaults follow Godot's standard user-data dirs (best-effort).

Usage:
  python grep_log.py --mod-name CanaryCard
  python grep_log.py --mod-name CanaryCard --tier2-pattern "played|fired|used"
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path


def default_log_path() -> Path:
    if sys.platform.startswith("win"):
        base = os.environ.get("APPDATA", str(Path.home() / "AppData" / "Roaming"))
        return Path(base) / "SlayTheSpire2" / "logs" / "godot.log"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "SlayTheSpire2" / "logs" / "godot.log"
    # Linux / other: Godot's standard XDG user-data location.
    xdg = os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local" / "share"))
    return Path(xdg) / "SlayTheSpire2" / "logs" / "godot.log"


def read_shared(path: Path) -> str:
    """Read the whole log even while the game still holds it open (tier-2 case).

    Python's open() uses a shared handle on all platforms, so unlike .NET's
    exclusive File.ReadAllText this does not throw 'file in use' while the game
    is running. errors='replace' guards against a partial multibyte tail.
    """
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Verify STS2 mod load/effect from godot.log")
    ap.add_argument("--mod-name", required=True,
                    help="Mod name (Mod.json 'id', also the mods/<ModName> folder)")
    ap.add_argument("--log-path", default=None, help="Full path to godot.log")
    ap.add_argument("--tier2-pattern", default="",
                    help="Also report [T2MOD-SELFTEST] lines matching this regex "
                         "(e.g. 'played|fired|used'). Empty = tier-1 only.")
    args = ap.parse_args(argv)

    log_path = Path(args.log_path) if args.log_path else default_log_path()
    mod = args.mod_name
    tier2_pattern = args.tier2_pattern

    if not log_path.is_file():
        print(f"godot.log not found: {log_path}", file=sys.stderr)
        return 2
    try:
        content = read_shared(log_path)
    except OSError as exc:
        print(f"Could not read {log_path}: {exc}", file=sys.stderr)
        return 2

    lines = content.split("\n")
    marker = "[T2MOD-SELFTEST]"

    def names_mod(line: str) -> bool:
        return marker in line and mod in line

    # Tier-1: load marker (the mod logged its init marker).
    load_line = next((ln for ln in lines if names_mod(ln)), None)

    # Tier-2: effect marker (only when a pattern is requested).
    tier2_lines: list[str] = []
    if tier2_pattern:
        t2re = re.compile(tier2_pattern)
        tier2_lines = [ln for ln in lines if names_mod(ln) and t2re.search(ln)]

    # Error lines naming the mod.
    err_re = re.compile(r"\bERROR\b|Exception", re.IGNORECASE)
    error_lines = [ln for ln in lines if err_re.search(ln) and mod in ln]

    modded = any("RUNNING MODDED" in ln for ln in lines)

    print()
    print(f"=== [T2MOD] Verify: {mod} ===")
    print(f"Log: {log_path} (current run; STS2 rotates on launch)")
    print()
    print(f"RUNNING MODDED flag : {'YES' if modded else 'NOT SEEN (mod may not have loaded)'}")
    print(f"Tier-1 load marker  : {('FOUND => ' + load_line) if load_line else 'NOT FOUND -- mod did not log its init marker'}")
    if tier2_pattern:
        if tier2_lines:
            print(f"Tier-2 effect marker: FOUND ({len(tier2_lines)}) => {tier2_lines[0]}")
        else:
            print(f"Tier-2 effect marker: NOT FOUND (pattern '{tier2_pattern}') -- effect not observed in this log yet")
    print()

    if error_lines:
        print(f"Errors/exceptions naming '{mod}':")
        for ln in error_lines:
            print(f"  {ln}")
    else:
        print(f"Errors naming '{mod}'   : none")
    print()

    tier2_requested = bool(tier2_pattern)
    tier2_ok = (not tier2_requested) or (len(tier2_lines) > 0)

    if load_line and not error_lines and tier2_ok:
        if tier2_requested:
            print(f"[PASS] Tier-2 verified: {mod} loaded AND effect marker fired.")
        else:
            print(f"[PASS] Tier-1 verified: {mod} loaded ok.")
        return 0

    if not load_line:
        print("[FAIL] Load marker missing. Check: was PckPacker uncommented? did build copy to mods/? see errors.md.")
    if error_lines:
        print("[FAIL] Error lines found. See errors.md for known fixes.")
    if tier2_requested and not tier2_lines:
        print(f"[FAIL] Tier-2 effect marker not found (pattern '{tier2_pattern}'). "
              "Was the effect triggered before this grep? Don't close the game first.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
