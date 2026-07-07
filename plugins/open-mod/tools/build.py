#!/usr/bin/env python3
"""Build an STS2 content mod (.dll + .pck + .json) into the game's mods/ folder.

Wraps `dotnet build -c Release`. The Alchyr template's csproj auto-copies the
.dll/.pdb/.json (CopyToModsFolderOnBuild) and, when BSchneppe.StS2.PckPacker is
uncommented, the .pck (CopyQuickPck) into <game>/mods/<ModName>/. Game + mods paths
auto-resolve via Sts2PathDiscovery.props, so no override is normally needed. This is
the R1 build step used by modmaker's build.md.

On success prints the artifacts found in the mods folder. On failure prints the
diagnostic lines from the dotnet output and exits non-zero (repair is handled by the
caller, M3+). `dotnet` is cross-platform, so this tool runs on Windows/macOS/Linux
unchanged; only the STS2 install/mods location differs, and that is resolved by the
csproj's Sts2PathDiscovery.props rather than here.

Usage:
  python build.py --project-dir D:/26summer_intern/canary-card
  python build.py --project-dir <dir> --mod-name CanaryCard
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

DIAG_RE = re.compile(r"error|warning|错误|警告|CS\d|MSB\d", re.IGNORECASE)


def find_csproj(project_dir: Path, mod_name: str | None) -> Path | None:
    csprojs = sorted(project_dir.glob("*.csproj"))
    if not csprojs:
        return None
    if mod_name:
        for cs in csprojs:
            if cs.stem == mod_name:
                return cs
    return csprojs[0]


def locate_mods_dir(log_text: str, csproj: Path, mod_name: str) -> Path | None:
    """Find the mods/<ModName>/ folder the build copied into.

    1. Match a path ending in .../mods/<ModName> in the build log (locale-agnostic;
       the copy-confirmation wording is localized, so match the PATH not the words).
    2. Ask MSBuild for the resolved $(ModsPath) property (authoritative fallback).
    """
    escaped = re.escape(mod_name)
    # Accept either separator; stop at a separator, quote, space, or end.
    pat = re.compile(r"([A-Za-z]:[\\/].*?[\\/]mods[\\/]" + escaped + r")(?=[\\/'\" ]|$)")
    for line in log_text.split("\n"):
        m = pat.search(line)
        if m:
            return Path(m.group(1))

    try:
        res = subprocess.run(
            ["dotnet", "msbuild", str(csproj), "-getProperty:ModsPath", "-nologo"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        if res.returncode == 0 and res.stdout.strip():
            candidate = Path(res.stdout.strip()) / mod_name
            if candidate.is_dir():
                return candidate
    except OSError:
        pass
    return None


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Build an STS2 content mod into mods/")
    ap.add_argument("--project-dir", required=True,
                    help="Path to the mod project root (the dir holding <ModName>.csproj)")
    ap.add_argument("--mod-name", default=None,
                    help="Mod name = csproj base name = mods/<ModName>/ folder. "
                         "Defaults to the single .csproj found in project-dir.")
    args = ap.parse_args(argv)

    project_dir = Path(args.project_dir)
    if not project_dir.is_dir():
        print(f"project-dir not found: {project_dir}", file=sys.stderr)
        return 2

    csproj = find_csproj(project_dir, args.mod_name)
    if not csproj:
        print(f"No .csproj found in {project_dir}", file=sys.stderr)
        return 2
    mod_name = args.mod_name or csproj.stem

    print(f"[build] dotnet build -c Release  ({csproj.name})")
    res = subprocess.run(
        ["dotnet", "build", str(csproj), "-c", "Release"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    log_text = (res.stdout or "") + (res.stderr or "")
    code = res.returncode

    # Keep the console quiet: full output goes to a file, not the transcript.
    build_log = project_dir / ".build.log"
    build_log.write_text(log_text, encoding="utf-8")
    print(f"[build] full output -> {build_log}")

    if code != 0:
        print(f"[build] FAILED (exit {code}). Error/warning lines:")
        diag = [ln for ln in log_text.split("\n") if DIAG_RE.search(ln)]
        if diag:
            for ln in diag[:25]:
                print(f"  {ln}")
        else:
            for ln in log_text.split("\n")[-15:]:
                print(f"  {ln}")
        print(f"[build] dotnet build FAILED (exit {code}). Full log: {build_log}", file=sys.stderr)
        return code

    mods_dir = locate_mods_dir(log_text, csproj, mod_name)

    print()
    print(f"[build] OK. Artifacts for '{mod_name}':")
    if mods_dir and mods_dir.is_dir():
        for f in sorted(p for p in mods_dir.iterdir() if p.is_file()):
            print(f"  {f.name}  ({f.stat().st_size:,} bytes)")
        has_pck = (mods_dir / f"{mod_name}.pck").is_file()
        if not has_pck:
            print(f"[build] WARNING: No .pck in mods folder. If localization/images don't "
                  "show in-game, uncomment BSchneppe.StS2.PckPacker in the csproj (see errors.md).")
        # Emit the resolved mods dir as the last line (callers parse this).
        print(str(mods_dir))
    else:
        print(f"[build] WARNING: Build succeeded but could not locate mods/{mod_name}/ "
              "from the log. Check Sts2PathDiscovery.props resolved the game path.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
