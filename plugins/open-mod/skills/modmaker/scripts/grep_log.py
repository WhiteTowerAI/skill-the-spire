#!/usr/bin/env python3
"""Verify STS2 load and state-proof markers in the current godot.log.

R2 verify step (modmaker's verify.md). Reads the CURRENT godot.log in full. STS2
archives the previous log (renaming it to godot<timestamp>.log) and starts a fresh
godot.log on every launch, so the current file already contains exactly one run --
no byte-offset slicing is needed, and offsets from a prior file are meaningless
against the new one. Tier 1 requires the exact mod load marker. Tier 2 additionally
requires a structured state-proof marker and a successful harness terminal marker;
ordinary hook/preview logs and ``selftest done`` can never prove behavior.

Cross-platform port of grep_log.ps1. The log path defaults per-OS:
  Windows : %APPDATA%\\SlayTheSpire2\\logs\\godot.log
  macOS   : ~/Library/Application Support/SlayTheSpire2/logs/godot.log
  Linux   : ~/.local/share/SlayTheSpire2/logs/godot.log
Override with --log-path. Only the Windows path is verified on the dev box; the
mac/Linux defaults follow Godot's standard user-data dirs (best-effort).

Usage:
  python grep_log.py --mod-name CanaryCard
  python grep_log.py --mod-name CanaryCard --tier2-pattern "damage.*6"
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

from ritsu_profile import PROFILE


LOG_RECORD_RE = re.compile(
    r"^\s*(?:\d+\w*\s+)?\[(?P<level>TRACE|DEBUG|INFO|WARN|WARNING|ERROR|FATAL)\]",
    re.IGNORECASE,
)
PLAIN_ERROR_RE = re.compile(
    r"\b(?:ERROR|FATAL)\b|\b(?:Unhandled\s+)?[A-Za-z0-9_.]*Exception\b",
    re.IGNORECASE,
)
ABANDON_MISSING_BACKUP_RE = re.compile(
    r"^\s*\[ERROR\]\s+Error deleting path "
    r"modded[\\/]profile\d+[\\/]saves[\\/]current_run\.save\.backup: Failed\s*$",
    re.IGNORECASE,
)
SENTRY_SHUTDOWN_RE = re.compile(
    r"^\s*ERROR:\s+Sentry: Failed to close native SDK cleanly\. Error code: 1\s*$",
    re.IGNORECASE,
)
PROFILE_FIELDS = (
    "framework=RitsuLib",
    f"frameworkVersion={PROFILE.framework_version}",
    f"host={PROFILE.host_version}",
    f"compat={PROFILE.host_version}",
)


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


def is_error_record(line: str) -> bool:
    """Whether a line starts an error record rather than continuing one."""
    record = LOG_RECORD_RE.match(line)
    if record:
        return record.group("level").upper() in {"ERROR", "FATAL"}
    return PLAIN_ERROR_RE.search(line) is not None


def error_blocks(lines: list[str], start_index: int) -> list[list[str]]:
    """Collect error headers and their multiline context from a run window."""
    blocks: list[list[str]] = []
    index = max(0, start_index)
    while index < len(lines):
        if not is_error_record(lines[index]):
            index += 1
            continue
        end = index + 1
        while end < len(lines) and not LOG_RECORD_RE.match(lines[end]):
            end += 1
        blocks.append(lines[index:end])
        index = end
    return blocks


def is_known_verification_cleanup(block: list[str]) -> bool:
    """Match only grounded base-game noise caused by the verification lifecycle.

    STS2's abandon path unconditionally removes a backup; on Windows/Godot a missing
    backup can return ``Failed`` instead of ``FileNotFound``. The launcher can also
    make the native Sentry bridge report a close error while terminating the headed
    verification process. Require each exact header plus its base-game cleanup stack
    so similarly worded mod/runtime errors still fail.
    """
    if not block:
        return False
    header = block[0]
    context = "\n".join(block)
    if ABANDON_MISSING_BACKUP_RE.match(header):
        return all(
            frame in context
            for frame in (
                "RunSaveManager.DeleteCurrentRun()",
                "NMainMenu.AbandonRun()",
                "UiHelper.Click",
            )
        )
    if SENTRY_SHUTDOWN_RE.match(header):
        return all(
            frame in context
            for frame in (
                "sentry::native::NativeSDK::close",
                "MegaCrit.Sts2.Core.Debug.SentryService.Shutdown()",
            )
        )
    return False


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Verify STS2 mod load/effect from godot.log")
    ap.add_argument("--mod-name", required=True,
                    help="Mod name (Mod.json 'id', also the mods/<ModName> folder)")
    ap.add_argument("--log-path", default=None, help="Full path to godot.log")
    ap.add_argument("--tier2-pattern", default="",
                    help="Match this regex against structured '<ModName> state proof:' "
                         "lines. Empty = tier-1 only.")
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

    lines = content.splitlines()
    marker = "[T2MOD-SELFTEST]"
    load_marker = f"{marker} {mod} loaded ok"
    done_marker = f"{marker} {mod} selftest done"
    failed_marker = f"{marker} {mod} selftest FAILED"
    proof_marker = f"{marker} {mod} state proof:"

    # Tier-1: require the exact initialization marker. A later mod-named self-test
    # line does not prove that MainFile.Initialize emitted the load contract.
    load_matches = [(index, line) for index, line in enumerate(lines)
                    if load_marker in line]
    load_match = load_matches[-1] if load_matches else None
    load_index = load_match[0] if load_match else None
    load_line = load_match[1] if load_match else None
    profile_ok = load_line is not None and all(field in load_line for field in PROFILE_FIELDS)
    run_lines = lines[load_index:] if load_index is not None else lines
    done_line = next((ln for ln in run_lines if done_marker in ln), None)
    failed_line = next((ln for ln in run_lines if failed_marker in ln), None)

    # Tier-2 accepts only a harness state proof emitted after a concrete assertion.
    # Element hook logs are useful diagnostics but may also fire during previews.
    tier2_lines: list[str] = []
    if tier2_pattern:
        try:
            t2re = re.compile(tier2_pattern)
        except re.error as exc:
            print(f"Invalid --tier2-pattern regex: {exc}", file=sys.stderr)
            return 2
        tier2_lines = [
            ln for ln in run_lines
            if proof_marker in ln
            and t2re.search(ln)
        ]

    # Once this mod's current load marker appears, any error record is a fresh-run
    # failure, even when only a continuation line names the mod. Before that boundary,
    # retain only mod-named blocks for diagnostics and ignore unrelated old text.
    parsed_error_blocks = error_blocks(lines, load_index or 0)
    if load_index is None:
        parsed_error_blocks = [
            block for block in parsed_error_blocks if mod in "\n".join(block)
        ]
    ignored_cleanup_blocks = [
        block for block in parsed_error_blocks if is_known_verification_cleanup(block)
    ]
    parsed_error_blocks = [
        block for block in parsed_error_blocks if not is_known_verification_cleanup(block)
    ]

    modded = any("RUNNING MODDED" in ln for ln in lines)

    print()
    print(f"=== [T2MOD] Verify: {mod} ===")
    print(f"Log: {log_path} (current run; STS2 rotates on launch)")
    print()
    print(f"RUNNING MODDED flag : {'YES' if modded else 'NOT SEEN (mod may not have loaded)'}")
    print(f"Tier-1 load marker  : {('FOUND => ' + load_line) if load_line else 'NOT FOUND -- mod did not log its init marker'}")
    print(f"Framework profile   : {'MATCH' if profile_ok else 'MISSING/MISMATCHED -- expected ' + ' '.join(PROFILE_FIELDS)}")
    if tier2_pattern:
        if tier2_lines:
            print(f"Tier-2 state proof  : FOUND ({len(tier2_lines)}) => {tier2_lines[0]}")
        else:
            print(f"Tier-2 state proof  : NOT FOUND (pattern '{tier2_pattern}') -- asserted post-state not observed")
        print(f"Harness terminal     : {('FAILED => ' + failed_line) if failed_line else ('DONE => ' + done_line) if done_line else 'NOT FOUND'}")
    print()

    if parsed_error_blocks:
        print(f"Errors/exceptions after '{mod}' load marker:")
        for block in parsed_error_blocks:
            for line in block:
                print(f"  {line}")
    else:
        print(f"Fresh-run errors after '{mod}' load: none")
    if ignored_cleanup_blocks:
        print("Known verification cleanup noise: "
              f"IGNORED ({len(ignored_cleanup_blocks)} exact base-game block(s))")
    print()

    tier2_requested = bool(tier2_pattern)
    tier2_ok = (not tier2_requested) or (
        bool(tier2_lines) and done_line is not None and failed_line is None
    )

    if load_line and profile_ok and not parsed_error_blocks and tier2_ok:
        if tier2_requested:
            print(f"[PASS] Tier-2 verified: {mod} loaded AND asserted post-state matched.")
        else:
            print(f"[PASS] Tier-1 verified: {mod} loaded ok.")
        return 0

    if not load_line:
        print("[FAIL] Load marker missing. Check the RitsuLib scaffold, build copy, and compat diagnostics.")
    elif not profile_ok:
        print("[FAIL] RitsuLib framework/host/compat profile is missing or mismatched.")
    if parsed_error_blocks:
        print("[FAIL] Fresh-run error block(s) found. See errors.md for known fixes.")
    if tier2_requested and not tier2_lines:
        print(f"[FAIL] Tier-2 state proof not found (pattern '{tier2_pattern}'). "
              "Hook/preview and terminal markers are not post-state proof.")
    if tier2_requested and failed_line:
        print("[FAIL] Harness reported selftest FAILED. This is a setup/navigation miss; "
              "use the manual fallback and report tier-1 only unless the effect is observed.")
    elif tier2_requested and not done_line:
        print("[FAIL] Successful harness terminal marker missing; the scenario did not finish.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
