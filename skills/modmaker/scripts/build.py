#!/usr/bin/env python3
"""Build a local-runtime STS2/RitsuLib Mod into the game's mods/ folder.

Validates the skill-the-spire RitsuLib profile before MSBuild, then verifies the resolved local
assembly and deployed artifacts. Framework assemblies are supplied by the game/runtime
installation or bundled build SDK and are never copied into the generated Mod.

On success prints the artifacts found in the mods folder. On failure prints the
diagnostic lines from the dotnet output and exits non-zero (repair is handled by the
caller, M3+). `dotnet` is cross-platform, so this tool runs on Windows/macOS/Linux
unchanged; only the STS2 install/mods location differs, and that is resolved by the
csproj's Sts2PathDiscovery.props rather than here.

Usage:
  python build.py --project-dir D:/mods/example-mod
  python build.py --project-dir <dir> --mod-name ExampleMod
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from ancient_dialogue import (
    AncientDialogueValidationError,
    validate_project_ancient_dialogue,
)
from localization_contract import (
    LocalizationContractError,
    validate_project_localization,
)
import selftest_kit
from api import ApiError
from hook_reachability import HookReachabilityError, validate_built_mod
from pack_pck import PackError, pack_assets
from selftest_kit import SelfTestKitError
from ritsu_profile import (
    PROFILE,
    RitsuProfileError,
    find_manifest,
    resolve_runtime_asset,
    resolve_runtime_compile_profile,
    validate_host_version,
    validate_project_contract,
    validate_project_runtime_profile,
    validate_restore_assets,
    validate_runtime_asset,
)
from source_scan import SourceScanError, validate_project_sources
from text_style import TextStyleError, validate_project_text_style
from vanilla_overrides import VanillaOverrideError, validate_project_override_manifest

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


def get_msbuild_property(
    csproj: Path,
    property_name: str,
    dotnet_env: dict[str, str] | None = None,
) -> str | None:
    try:
        res = subprocess.run(
            ["dotnet", "msbuild", str(csproj), f"-getProperty:{property_name}", "-nologo"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            env=dotnet_env,
        )
    except OSError:
        return None
    if res.returncode != 0:
        return None
    lines = [line.strip() for line in res.stdout.splitlines() if line.strip()]
    return lines[-1] if lines else None


def locate_mods_dir(
    log_text: str,
    csproj: Path,
    mod_name: str,
    dotnet_env: dict[str, str] | None = None,
) -> Path | None:
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

    mods_root = get_msbuild_property(csproj, "ModsPath", dotnet_env)
    if mods_root:
        candidate = Path(mods_root) / mod_name
        if candidate.is_dir():
            return candidate
    return None


def pack_project_assets(project_dir: Path, mod_name: str, mods_dir: Path) -> bool:
    """Pack the generated Mod resource tree without a framework-specific pack target."""
    source_dir = project_dir / mod_name
    if not source_dir.is_dir() or not any(path.is_file() for path in source_dir.rglob("*")):
        return False
    output = mods_dir / f"{mod_name}.pck"
    pack_assets(source_dir, mod_name, output)
    print(f"[build] packed Mod resources -> {output.name}")
    return True


def validate_resource_manifest(project_dir: Path, mod_name: str) -> str:
    """Require the manifest's PCK declaration to match the authored resource tree."""
    source_dir = project_dir / mod_name
    has_resources = source_dir.is_dir() and any(
        path.is_file() for path in source_dir.rglob("*")
    )
    manifest = find_manifest(project_dir, mod_name)
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RitsuProfileError(f"invalid manifest JSON in {manifest}: {exc}") from exc
    has_pck = data.get("has_pck")
    if not isinstance(has_pck, bool) or has_pck != has_resources:
        expected = str(has_resources).lower()
        raise RitsuProfileError(
            f"manifest has_pck must be {expected} when the generated resource tree "
            f"is {'non-empty' if has_resources else 'empty'}; found {has_pck!r}"
        )
    return f"has_pck={str(has_pck).lower()}"


# The game's mod scanner (ModManager.ReadModsInDirRecursive) walks a Mod directory to any
# depth and parses EVERY `.json` it finds as a Mod manifest, logging a load error for each
# one that has no `id`. A deployed Mod therefore contains exactly one loose `.json`: its own
# manifest. Localization and other authored JSON ship inside the `.pck`, never loose.
def validate_no_phantom_manifests(mods_dir: Path, deployed_manifest: Path) -> None:
    """Fail when the deployed tree holds a `.json` the game would misread as a manifest."""
    phantoms = sorted(
        path.relative_to(mods_dir).as_posix()
        for path in mods_dir.rglob("*.json")
        if path.is_file() and path != deployed_manifest
    )
    if phantoms:
        raise RitsuProfileError(
            "deployed Mod contains non-manifest .json the game parses as a Mod manifest "
            f"and rejects: {', '.join(phantoms)}. Keep authored JSON inside the .pck and "
            "keep build-time sidecars in the project directory only"
        )


def validate_deployed_artifacts(project_dir: Path, mod_name: str, mods_dir: Path) -> None:
    manifest = find_manifest(project_dir, mod_name)
    deployed_manifest = mods_dir / manifest.name
    required = (mods_dir / f"{mod_name}.dll", deployed_manifest)
    missing = [path.name for path in required if not path.is_file()]
    if missing:
        raise RitsuProfileError(f"deployed Mod is missing: {', '.join(missing)}")
    forbidden = (
        mods_dir / PROFILE.runtime_dll,
        *(
            mods_dir / f"{name}.dll"
            for name in (*PROFILE.compat_assemblies, *PROFILE.shared_assemblies)
        ),
        mods_dir / "BaseLib.dll",
        mods_dir / "BaseLib.pck",
    )
    present = [path.name for path in forbidden if path.exists()]
    if present:
        raise RitsuProfileError(
            f"generated Mod directory contains a framework payload: {', '.join(present)}"
        )
    validate_no_phantom_manifests(mods_dir, deployed_manifest)


def report_text_style(project_dir: Path, mod_name: str) -> None:
    """Fail on broken rich-text markup; list vanilla-style drift without failing the Build."""
    summary, warnings = validate_project_text_style(project_dir, mod_name)
    if not warnings:
        print(f"[build] text style OK: {summary}")
        return
    style_log = project_dir / ".text-style.log"
    style_log.write_text("\n".join(warnings) + "\n", encoding="utf-8")
    print(f"[build] text style WARNING: {summary}; fix each line in {style_log}")
    # Warnings quote Chinese text; a legacy console code page must not crash the Build.
    sys.stdout.reconfigure(errors="backslashreplace")
    for warning in warnings[:5]:
        print(f"  {warning}")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Build an STS2 content mod into mods/")
    ap.add_argument("--project-dir", required=True,
                    help="Path to the mod project root (the dir holding <ModName>.csproj)")
    ap.add_argument("--mod-name", default=None,
                    help="Mod name = csproj base name = mods/<ModName>/ folder. "
                         "Defaults to the single .csproj found in project-dir.")
    ap.add_argument("--runtime-dir", default=None,
                    help="Installed RitsuLib directory. Defaults to "
                         "the game mods directory, then the official Steam Workshop item.")
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
    try:
        summary = validate_project_contract(project_dir, mod_name)
        print(f"[build] profile OK: {summary}")
        resource_summary = validate_resource_manifest(project_dir, mod_name)
        print(f"[build] resource manifest OK: {resource_summary}")
        localization_summary = validate_project_localization(project_dir, mod_name)
        print(f"[build] localization OK: {localization_summary}")
        report_text_style(project_dir, mod_name)
        dialogue_summary = validate_project_ancient_dialogue(project_dir, mod_name)
        print(f"[build] Ancient dialogue OK: {dialogue_summary}")
        override_summary = validate_project_override_manifest(project_dir, mod_name)
        print(f"[build] vanilla override manifest OK: {override_summary}")
        print(f"[build] self-test kit OK: {selftest_kit.check(project_dir, mod_name)}")
        print(f"[build] source routes OK: {validate_project_sources(project_dir, mod_name)}")
        sts2_dir_text = get_msbuild_property(csproj, "Sts2Dir")
        mods_root_text = get_msbuild_property(csproj, "ModsPath")
        if not sts2_dir_text or not mods_root_text:
            raise RitsuProfileError(
                "MSBuild did not resolve Sts2Dir/ModsPath; set Sts2Dir in local.props"
            )
        print(f"[build] host OK: {validate_host_version(Path(sts2_dir_text))}")
        runtime = resolve_runtime_asset(
            Path(sts2_dir_text),
            Path(mods_root_text),
            Path(args.runtime_dir) if args.runtime_dir else None,
        )
        if runtime.alternates:
            alternatives = ", ".join(str(path) for path in runtime.alternates)
            print(
                "[build] WARNING: duplicate RitsuLib installs found; "
                f"using {runtime.source} and ignoring {alternatives}"
            )
        print(f"[build] runtime source: {runtime.source} -> {runtime.path}")
        compile_runtime = resolve_runtime_compile_profile(runtime.path)
        validate_project_runtime_profile(project_dir, mod_name, compile_runtime)
        print(f"[build] runtime OK: {validate_runtime_asset(runtime.path)}")
    except (
        OSError,
        AncientDialogueValidationError,
        LocalizationContractError,
        RitsuProfileError,
        SelfTestKitError,
        SourceScanError,
        TextStyleError,
        VanillaOverrideError,
    ) as exc:
        print(f"[build] RitsuLib profile FAILED: {exc}", file=sys.stderr)
        return 2

    print(f"[build] dotnet build -c Release  ({csproj.name})")
    build_command = [
        "dotnet",
        "build",
        str(csproj),
        "-c",
        "Release",
        "-p:RestoreIgnoreFailedSources=true",
        "-p:NuGetAudit=false",
        f"-p:RitsuLibRuntimeRoot={compile_runtime.root.resolve().as_posix()}",
    ]
    res = subprocess.run(
        build_command,
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env=None,
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

    try:
        validate_restore_assets(project_dir)
    except RitsuProfileError as exc:
        print(f"[build] RitsuLib restore FAILED: {exc}", file=sys.stderr)
        return 2

    mods_dir = locate_mods_dir(log_text, csproj, mod_name)

    if mods_dir and mods_dir.is_dir():
        try:
            pack_project_assets(project_dir, mod_name, mods_dir)
            validate_deployed_artifacts(project_dir, mod_name, mods_dir)
        except (OSError, PackError, RitsuProfileError) as exc:
            print(f"[build] artifact packaging FAILED: {exc}", file=sys.stderr)
            return 1
        try:
            reachability = validate_built_mod(mods_dir / f"{mod_name}.dll", project_dir)
            print(f"[build] hook reachability OK: {reachability}")
        except (OSError, ApiError, HookReachabilityError) as exc:
            print(f"[build] hook reachability FAILED: {exc}", file=sys.stderr)
            return 1

    print()
    print(f"[build] OK. Artifacts for '{mod_name}':")
    if mods_dir and mods_dir.is_dir():
        for f in sorted(p for p in mods_dir.iterdir() if p.is_file()):
            print(f"  {f.name}  ({f.stat().st_size:,} bytes)")
        # Emit the resolved mods dir as the last line (callers parse this).
        print(str(mods_dir))
    else:
        print(f"[build] FAILED: Build succeeded but could not locate deployed "
              f"mods/{mod_name}/. Check Sts2PathDiscovery.props and the copy target.",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
