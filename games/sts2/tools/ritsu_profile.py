#!/usr/bin/env python3
"""The single build/deployment contract for the pinned RitsuLib profile."""
from __future__ import annotations

import json
import hashlib
import re
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


class RitsuProfileError(ValueError):
    """Raised when a project or runtime does not match the pinned profile."""


@dataclass(frozen=True)
class RitsuProfile:
    framework_version: str = "0.5.4"
    host_version: str = "0.107.1"
    package_id: str = "STS2.RitsuLib.Compat.0.107.1"
    runtime_mod_id: str = "STS2-RitsuLib"
    runtime_dll: str = "STS2-RitsuLib.dll"

    @property
    def profile_id(self) -> str:
        return f"ritsulib-{self.framework_version}-sts2-{self.host_version}"

    @property
    def package_name(self) -> str:
        return f"{self.package_id}.{self.framework_version}.nupkg"


PROFILE = RitsuProfile()
_BASELIB_RE = re.compile(r"baselib|alchyr\.sts2", re.IGNORECASE)


def find_manifest(project_dir: Path, mod_name: str) -> Path:
    candidates = (project_dir / f"{mod_name}.json", project_dir / "mod_manifest.json")
    for path in candidates:
        if path.is_file():
            return path
    raise RitsuProfileError(
        f"missing manifest: expected {mod_name}.json (or mod_manifest.json) in {project_dir}"
    )


def _xml_text(element: ET.Element) -> str:
    return "".join(element.itertext()).strip()


def _all_package_references(root: ET.Element) -> Iterable[tuple[str, str]]:
    for node in root.iter():
        if node.tag.rsplit("}", 1)[-1] != "PackageReference":
            continue
        package_id = node.attrib.get("Include") or node.attrib.get("Update") or ""
        version = node.attrib.get("Version", "")
        if not version:
            for child in node:
                if child.tag.rsplit("}", 1)[-1] == "Version":
                    version = _xml_text(child)
                    break
        yield package_id.strip(), version.strip()


def _property_values(root: ET.Element, name: str) -> list[str]:
    values: list[str] = []
    for node in root.iter():
        if node.tag.rsplit("}", 1)[-1] == name:
            values.append(_xml_text(node))
    return values


def validate_project_contract(project_dir: Path, mod_name: str | None = None) -> str:
    """Validate the source contract before invoking MSBuild."""
    if not project_dir.is_dir():
        raise RitsuProfileError(f"project directory not found: {project_dir}")
    csprojs = sorted(project_dir.glob("*.csproj"))
    if not csprojs:
        raise RitsuProfileError(f"no .csproj found in {project_dir}")
    csproj = next((p for p in csprojs if mod_name is None or p.stem == mod_name), csprojs[0])
    mod_name = mod_name or csproj.stem
    text = csproj.read_text(encoding="utf-8", errors="replace")
    if _BASELIB_RE.search(text):
        raise RitsuProfileError(
            f"BaseLib reference found in {csproj.name}; the RitsuLib path has no BaseLib fallback"
        )
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        raise RitsuProfileError(f"invalid project XML in {csproj}: {exc}") from exc

    refs = list(_all_package_references(root))
    selected = [ref for ref in refs if ref[0].lower() == PROFILE.package_id.lower()]
    ritsu_refs = [ref for ref in refs if "ritsulib" in ref[0].lower()]
    if (len(selected) != 1 or selected[0][1] != PROFILE.framework_version
            or ritsu_refs != selected):
        detail = ", ".join(f"{name} {version or '<floating>'}" for name, version in refs) or "none"
        raise RitsuProfileError(
            f"required compile asset is {PROFILE.package_id} {PROFILE.framework_version}; found {detail}. "
            "Do not use the default beta-facing STS2.RitsuLib package."
        )
    compat = _property_values(root, "Sts2ApiCompat")
    if PROFILE.host_version not in compat:
        raise RitsuProfileError(
            f"Sts2ApiCompat must be {PROFILE.host_version}; found {compat or ['<unset>']}"
        )
    autocopy = _property_values(root, "RitsuLibAutoCopy")
    if any(value.lower() != "false" for value in autocopy):
        raise RitsuProfileError(
            "RitsuLibAutoCopy must be false in a consumer project; install the framework separately"
        )
    deploy_dirs = _property_values(root, "RitsuLibDeployDir")
    if any(value for value in deploy_dirs):
        raise RitsuProfileError("RitsuLibDeployDir must be empty for a generated consumer Mod")

    manifest = find_manifest(project_dir, mod_name)
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RitsuProfileError(f"invalid manifest JSON in {manifest}: {exc}") from exc
    if not isinstance(data, dict):
        raise RitsuProfileError(f"manifest root must be an object: {manifest}")
    serialized = json.dumps(data, sort_keys=True)
    if _BASELIB_RE.search(serialized):
        raise RitsuProfileError(f"BaseLib dependency found in {manifest}")
    if data.get("min_game_version") != PROFILE.host_version:
        raise RitsuProfileError(
            f"manifest min_game_version must be {PROFILE.host_version}; found {data.get('min_game_version')!r}"
        )
    dependencies = data.get("dependencies")
    if not isinstance(dependencies, list) or len(dependencies) != 1:
        raise RitsuProfileError(
            f"manifest dependencies must contain only {PROFILE.runtime_mod_id} {PROFILE.framework_version}"
        )
    dependency = dependencies[0]
    if not isinstance(dependency, dict) or dependency.get("id") != PROFILE.runtime_mod_id:
        raise RitsuProfileError(
            f"manifest dependency must be {PROFILE.runtime_mod_id}; found {dependency!r}"
        )
    if dependency.get("min_version") != PROFILE.framework_version:
        raise RitsuProfileError(
            f"manifest dependency min_version must be {PROFILE.framework_version}; "
            f"found {dependency.get('min_version')!r}"
        )
    return f"{PROFILE.profile_id} ({PROFILE.package_id} {PROFILE.framework_version})"


def validate_restore_assets(project_dir: Path) -> None:
    """Reject a resolved assets file that silently selected another Ritsu package."""
    assets = project_dir / ".godot" / "mono" / "temp" / "obj" / "project.assets.json"
    if not assets.is_file():
        return
    try:
        data = json.loads(assets.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RitsuProfileError(f"cannot read NuGet restore assets {assets}: {exc}") from exc
    libraries = data.get("libraries", {})
    expected = f"{PROFILE.package_id.lower()}/{PROFILE.framework_version}"
    matches = [str(key).lower() for key in libraries if str(key).lower() == expected]
    framework_libraries = [
        str(key) for key in libraries
        if "ritsulib" in str(key).lower() or _BASELIB_RE.search(str(key))
    ]
    if not matches or [item.lower() for item in framework_libraries] != [expected]:
        found = ", ".join(sorted(str(key) for key in libraries if "ritsulib" in str(key).lower())) or "none"
        raise RitsuProfileError(
            f"NuGet restore did not resolve {PROFILE.package_id} {PROFILE.framework_version}; found {found}"
        )


def _variant_entries(manifest: dict) -> list[dict]:
    variants = manifest.get("variants")
    return variants if isinstance(variants, list) else []


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _sha256_zip_entry(archive: zipfile.ZipFile, name: str) -> str:
    digest = hashlib.sha256()
    with archive.open(name) as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_zip_text(archive: zipfile.ZipFile, name: str) -> str:
    with archive.open(name) as stream:
        return stream.read().decode("utf-8")


def _check_variant_manifest_entry(entry: dict, dll_hash: str) -> None:
    if str(entry.get("compatTarget")) != PROFILE.host_version:
        raise RitsuProfileError(f"runtime variant manifest does not declare {PROFILE.host_version}")
    if entry.get("directory") != f"lib/{PROFILE.host_version}":
        raise RitsuProfileError("runtime variant manifest points the stable target at an unexpected directory")
    if entry.get("assembly") != PROFILE.runtime_dll:
        raise RitsuProfileError("runtime variant manifest points at an unexpected assembly")
    if str(entry.get("sha256", "")).lower() != dll_hash.lower():
        raise RitsuProfileError("runtime variant DLL hash does not match ritsulib-variants.manifest")


def _check_runtime_manifest(data: dict) -> None:
    if data.get("id") != PROFILE.runtime_mod_id:
        raise RitsuProfileError("RitsuLib runtime manifest has an unexpected id")
    if data.get("version") != PROFILE.framework_version:
        raise RitsuProfileError(
            f"RitsuLib runtime manifest version is not {PROFILE.framework_version}"
        )
    if str(data.get("min_game_version", "")).removeprefix("v") != PROFILE.host_version:
        raise RitsuProfileError(
            f"RitsuLib runtime manifest min_game_version is not {PROFILE.host_version}"
        )
    if data.get("dependencies") not in ([], None):
        raise RitsuProfileError("RitsuLib runtime manifest unexpectedly declares dependencies")


def validate_runtime_asset(path: Path) -> str:
    """Validate an installed RitsuLib folder or release zip without loading a DLL."""
    if path.suffix.lower() == ".zip":
        if not path.is_file():
            raise RitsuProfileError(f"RitsuLib runtime asset not found: {path}")
        with zipfile.ZipFile(path) as archive:
            names = {name.replace("\\", "/").lstrip("./") for name in archive.namelist()}
            variant_prefix = f"lib/{PROFILE.host_version}/"
            has_variant = variant_prefix + PROFILE.runtime_dll in names
            has_direct = PROFILE.runtime_dll in names and "compat-target.txt" in names
            if not has_variant and not has_direct:
                raise RitsuProfileError(
                    f"runtime asset {path.name} does not contain the {PROFILE.host_version} compat DLL/marker"
                )
            if "mod_manifest.json" not in names:
                raise RitsuProfileError("RitsuLib runtime asset is missing mod_manifest.json")
            try:
                _check_runtime_manifest(json.loads(_read_zip_text(archive, "mod_manifest.json")))
            except json.JSONDecodeError as exc:
                raise RitsuProfileError(f"invalid RitsuLib runtime manifest: {exc}") from exc
            if has_variant:
                marker_name = variant_prefix + "compat-target.txt"
                manifest_name = "ritsulib-variants.manifest"
                if marker_name not in names or manifest_name not in names:
                    raise RitsuProfileError(
                        f"runtime variant is missing {marker_name} or {manifest_name}"
                    )
                if _read_zip_text(archive, marker_name).strip() != PROFILE.host_version:
                    raise RitsuProfileError(f"runtime marker {marker_name} is not {PROFILE.host_version}")
                try:
                    manifest = json.loads(_read_zip_text(archive, manifest_name))
                except (json.JSONDecodeError, OSError) as exc:
                    raise RitsuProfileError(f"invalid runtime variant manifest {manifest_name}: {exc}") from exc
                entries = _variant_entries(manifest)
                entry = next((item for item in entries if str(item.get("compatTarget")) == PROFILE.host_version), None)
                if entry is None:
                    raise RitsuProfileError(f"runtime variant manifest does not declare {PROFILE.host_version}")
                _check_variant_manifest_entry(entry, _sha256_zip_entry(archive, variant_prefix + PROFILE.runtime_dll))
            elif _read_zip_text(archive, "compat-target.txt").strip() != PROFILE.host_version:
                raise RitsuProfileError(f"runtime marker compat-target.txt is not {PROFILE.host_version}")
        return f"{path.name}: compat {PROFILE.host_version}"

    root = path
    if root.is_dir() and root.name.lower() != PROFILE.runtime_mod_id.lower():
        candidate = root / PROFILE.runtime_mod_id
        if candidate.is_dir():
            root = candidate
    if not root.is_dir():
        raise RitsuProfileError(f"RitsuLib runtime directory not found: {path}")
    root_dll = root / PROFILE.runtime_dll
    runtime_manifest = root / "mod_manifest.json"
    if not root_dll.is_file() or not runtime_manifest.is_file():
        raise RitsuProfileError(
            f"runtime directory {root} is missing {PROFILE.runtime_dll} or mod_manifest.json"
        )
    try:
        _check_runtime_manifest(json.loads(runtime_manifest.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError) as exc:
        raise RitsuProfileError(f"invalid RitsuLib runtime manifest {runtime_manifest}: {exc}") from exc
    variant_dir = root / "lib" / PROFILE.host_version
    direct_marker = root / "compat-target.txt"
    if variant_dir.is_dir():
        dll = variant_dir / PROFILE.runtime_dll
        marker = variant_dir / "compat-target.txt"
        if not dll.is_file() or marker.read_text(encoding="utf-8").strip() != PROFILE.host_version:
            raise RitsuProfileError(
                f"runtime variant {variant_dir} is missing {PROFILE.runtime_dll} or the matching compat marker"
            )
        manifest_path = root / "ritsulib-variants.manifest"
        if not manifest_path.is_file():
            raise RitsuProfileError(f"runtime variant is missing {manifest_path.name}")
        try:
            variants = _variant_entries(json.loads(manifest_path.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError) as exc:
            raise RitsuProfileError(f"invalid runtime variant manifest {manifest_path}: {exc}") from exc
        entry = next((item for item in variants if str(item.get("compatTarget")) == PROFILE.host_version), None)
        if entry is None:
            raise RitsuProfileError(f"runtime variant manifest does not declare {PROFILE.host_version}")
        _check_variant_manifest_entry(entry, _sha256_file(dll))
        return f"{root}: compat {PROFILE.host_version}"
    if direct_marker.is_file():
        if direct_marker.read_text(encoding="utf-8").strip() != PROFILE.host_version:
            raise RitsuProfileError(f"runtime marker {direct_marker} is not {PROFILE.host_version}")
        return f"{root}: compat {PROFILE.host_version}"
    raise RitsuProfileError(
        f"runtime directory {root} has no matching {PROFILE.host_version} RitsuLib variant; "
        "refusing to fall back to the beta-facing DLL"
    )


def validate_host_version(sts2_dir: Path) -> str:
    candidates = [
        sts2_dir / "release_info.json",
        sts2_dir / "data_sts2_windows_x86_64" / "game" / "release_info.json",
        sts2_dir / "data_sts2_linuxbsd_x86_64" / "game" / "release_info.json",
        sts2_dir / "SlayTheSpire2.app" / "Contents" / "Resources" / "game" / "release_info.json",
    ]
    for path in candidates:
        if path.is_file():
            try:
                value = json.loads(path.read_text(encoding="utf-8")).get("version")
            except (OSError, json.JSONDecodeError) as exc:
                raise RitsuProfileError(f"cannot read host release metadata {path}: {exc}") from exc
            normalized = str(value).removeprefix("v") if value is not None else None
            if normalized != PROFILE.host_version:
                raise RitsuProfileError(
                    f"STS2 host at {sts2_dir} reports {value!r}; required stable {PROFILE.host_version}"
                )
            return f"{path}: {PROFILE.host_version}"
    raise RitsuProfileError(
        f"could not find release_info.json under STS2 directory {sts2_dir}; "
        "refusing to claim the stable 0.107.1 host"
    )
