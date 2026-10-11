#!/usr/bin/env python3
"""The single build/deployment contract for the pinned RitsuLib profile."""
from __future__ import annotations

import json
import hashlib
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable


class RitsuProfileError(ValueError):
    """Raised when a project or runtime does not match the pinned profile."""


@dataclass(frozen=True)
class RitsuProfile:
    framework_version: str = "0.6.7"
    host_version: str = "0.107.1"
    godot_sdk_version: str = "4.5.1"
    runtime_mod_id: str = "STS2-RitsuLib"
    # Since RitsuLib 0.6.0 the root DLL is only a loader. The API lives in per-host compat
    # modules plus host-independent shared modules, listed by a schema-2 variant manifest.
    runtime_dll: str = "STS2-RitsuLib.dll"
    variant_manifest: str = "ritsulib-variants.manifest"
    variant_manifest_schema: int = 2
    compat_assemblies: tuple[str, ...] = ("STS2-RitsuLib.Runtime", "STS2-RitsuLib")
    shared_assemblies: tuple[str, ...] = (
        "STS2-RitsuLib.Shared",
        "STS2-RitsuLib.Ui",
        "STS2-RitsuLib.Settings",
    )
    steam_app_id: str = "2868840"
    workshop_item_id: str = "3747602295"

    @property
    def profile_id(self) -> str:
        return f"ritsulib-{self.framework_version}-sts2-{self.host_version}"

    @property
    def compat_dir(self) -> str:
        return f"compat/{self.host_version}"

    def assembly_relative_paths(self) -> tuple[tuple[str, str], ...]:
        """Return every compile assembly as (name, runtime-root-relative POSIX path)."""
        return tuple(
            (name, f"{self.compat_dir}/{name}.dll") for name in self.compat_assemblies
        ) + tuple((name, f"shared/{name}.dll") for name in self.shared_assemblies)


PROFILE = RitsuProfile()
_BASELIB_RE = re.compile(r"baselib|alchyr\.sts2", re.IGNORECASE)
_VERSION_RE = re.compile(
    r"^v?(?P<numeric>\d+(?:\.\d+){1,3})(?:[-+][0-9A-Za-z.-]+)?$"
)


@dataclass(frozen=True)
class RuntimeAssetSelection:
    path: Path
    source: str
    alternates: tuple[Path, ...] = ()


@dataclass(frozen=True)
class RuntimeAssembly:
    name: str
    relative_path: str
    sha256: str


@dataclass(frozen=True)
class RuntimeCompileProfile:
    """The checked local assembly set a generated Mod compiles against."""

    version: str
    root: Path
    assemblies: tuple[RuntimeAssembly, ...]

    @property
    def assembly_set_sha256(self) -> str:
        return assembly_set_digest(self.assemblies)


def assembly_set_digest(assemblies: Iterable[RuntimeAssembly]) -> str:
    """One stable digest over every compile assembly's relative path and SHA-256."""
    lines = sorted(f"{item.relative_path} {item.sha256.lower()}\n" for item in assemblies)
    return hashlib.sha256("".join(lines).encode("utf-8")).hexdigest()


def game_executable_dir(sts2_dir: Path, platform_name: str | None = None) -> Path:
    """Return the directory the host uses as the root for executable-adjacent files."""
    platform_name = platform_name or sys.platform
    if platform_name == "darwin":
        return sts2_dir / "SlayTheSpire2.app" / "Contents" / "MacOS"
    return sts2_dir


def local_mods_dir(sts2_dir: Path, platform_name: str | None = None) -> Path:
    return game_executable_dir(sts2_dir, platform_name) / "mods"


def _version_key(value: object) -> tuple[int, ...]:
    text = str(value).strip()
    match = _VERSION_RE.fullmatch(text)
    if match is None:
        raise RitsuProfileError(f"invalid RitsuLib runtime version {text!r}")
    parts = tuple(int(part) for part in match.group("numeric").split("."))
    return parts + (0,) * (4 - len(parts))


def is_supported_runtime_version(value: object) -> bool:
    try:
        return _version_key(value) >= _version_key(PROFILE.framework_version)
    except RitsuProfileError:
        return False


def workshop_runtime_dir(sts2_dir: Path) -> Path | None:
    """Resolve the official Workshop item beside the Steam library owning STS2."""
    resolved = sts2_dir.resolve()
    steamapps = next(
        (path for path in (resolved, *resolved.parents) if path.name.casefold() == "steamapps"),
        None,
    )
    if steamapps is None:
        return None
    return (
        steamapps
        / "workshop"
        / "content"
        / PROFILE.steam_app_id
        / PROFILE.workshop_item_id
    )


def resolve_runtime_asset(
    sts2_dir: Path,
    mods_root: Path,
    explicit: Path | None = None,
) -> RuntimeAssetSelection:
    """Select the runtime path using the same local-before-Workshop source order as STS2."""
    if explicit is not None:
        return RuntimeAssetSelection(explicit, "explicit")

    candidates: list[tuple[str, Path]] = [
        ("mods directory", mods_root / PROFILE.runtime_mod_id),
    ]
    workshop = workshop_runtime_dir(sts2_dir)
    if workshop is not None:
        candidates.append(("Steam Workshop", workshop))

    installed = [(source, path) for source, path in candidates if path.is_dir()]
    if not installed:
        searched = ", ".join(str(path) for _, path in candidates)
        raise RitsuProfileError(
            "RitsuLib runtime was not found in the game mods directory or the official "
            f"Steam Workshop item {PROFILE.workshop_item_id}; searched: {searched}"
        )

    source, selected = installed[0]
    return RuntimeAssetSelection(
        selected,
        source,
        tuple(path for _, path in installed[1:]),
    )


def find_manifest(project_dir: Path, mod_name: str) -> Path:
    manifest = project_dir / "mod_manifest.json"
    if manifest.is_file():
        return manifest
    old_name = project_dir / f"{mod_name}.json"
    if old_name.is_file():
        raise RitsuProfileError(
            f"{old_name.name} uses the pre-release manifest name; rename it to "
            f"mod_manifest.json in {project_dir}"
        )
    raise RitsuProfileError(f"missing manifest: expected mod_manifest.json in {project_dir}")


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


def _all_assembly_references(root: ET.Element) -> Iterable[str]:
    for node in root.iter():
        if node.tag.rsplit("}", 1)[-1] != "Reference":
            continue
        yield (node.attrib.get("Include") or "").strip()


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

    package_refs = list(_all_package_references(root))
    if package_refs:
        detail = ", ".join(f"{name} {version or '<floating>'}" for name, version in package_refs)
        raise RitsuProfileError(
            "generated consumer projects compile from checked local assemblies and must not "
            f"declare PackageReference entries; found {detail}"
        )
    sdk_dir = (
        project_dir
        / "skillthespire"
        / "sdk"
        / f"Godot.NET.Sdk.{PROFILE.godot_sdk_version}"
        / "Sdk"
    )
    required_sdk_files = (
        "Android.props",
        "iOSNativeAOT.props",
        "iOSNativeAOT.targets",
        "Sdk.props",
        "Sdk.targets",
        "SdkPackageVersions.props",
    )
    missing_sdk_files = [name for name in required_sdk_files if not (sdk_dir / name).is_file()]
    if missing_sdk_files:
        raise RitsuProfileError(
            f"generated project is missing bundled Godot.NET.Sdk {PROFILE.godot_sdk_version} "
            "files: " + ", ".join(missing_sdk_files)
        )
    required_references = {
        "sts2",
        "0Harmony",
        "GodotSharp",
        "System.IO.Hashing",
        *PROFILE.compat_assemblies,
        *PROFILE.shared_assemblies,
    }
    references = set(_all_assembly_references(root))
    missing_references = sorted(required_references - references)
    if missing_references:
        raise RitsuProfileError(
            "generated consumer project is missing local assembly references: "
            + ", ".join(missing_references)
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
    compile_versions = _property_values(root, "RitsuLibCompileVersion")
    if len(compile_versions) != 1 or not is_supported_runtime_version(compile_versions[0]):
        raise RitsuProfileError(
            f"RitsuLibCompileVersion must be one version >= {PROFILE.framework_version}; "
            f"found {compile_versions or ['<unset>']}"
        )
    if _property_values(root, "RitsuLibCompileAssemblySha256"):
        raise RitsuProfileError(
            "this project was scaffolded for the single-DLL RitsuLib runtime before 0.6.0; "
            "scaffold a new project and move its authored sources across"
        )
    compile_hashes = _property_values(root, "RitsuLibCompileAssemblySetSha256")
    if len(compile_hashes) != 1 or not re.fullmatch(r"[0-9A-Fa-f]{64}", compile_hashes[0]):
        raise RitsuProfileError(
            "RitsuLibCompileAssemblySetSha256 must be one SHA-256 digest for the local "
            "compat and shared assembly set"
        )

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
            f"manifest dependency min_version must remain the API floor {PROFILE.framework_version}; "
            f"found {dependency.get('min_version')!r}"
        )
    return (
        f"{PROFILE.profile_id} (local compile runtime {compile_versions[0]}, "
        f"assembly set sha256={compile_hashes[0].lower()})"
    )


def validate_project_runtime_profile(
    project_dir: Path,
    mod_name: str,
    runtime: RuntimeCompileProfile,
) -> None:
    """Require a build to use the version and assembly-set identity pinned by scaffold."""
    csproj = project_dir / f"{mod_name}.csproj"
    try:
        root = ET.fromstring(csproj.read_text(encoding="utf-8", errors="replace"))
    except (OSError, ET.ParseError) as exc:
        raise RitsuProfileError(f"cannot read generated project contract {csproj}: {exc}") from exc
    expected_versions = _property_values(root, "RitsuLibCompileVersion")
    expected_hashes = _property_values(root, "RitsuLibCompileAssemblySetSha256")
    expected_version = expected_versions[0] if len(expected_versions) == 1 else None
    expected_hash = expected_hashes[0].lower() if len(expected_hashes) == 1 else None
    if expected_version != runtime.version or expected_hash != runtime.assembly_set_sha256:
        raise RitsuProfileError(
            f"local RitsuLib runtime {runtime.version} (assembly set "
            f"{runtime.assembly_set_sha256[:12]}) differs from this project's pinned compile "
            f"profile {expected_version} ({(expected_hash or '<unset>')[:12]}); re-pin the "
            "project with `scaffold.py --repin-runtime` after reviewing the RitsuLib changes"
        )
    manifest = find_manifest(project_dir, mod_name)
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RitsuProfileError(f"cannot read Mod manifest {manifest}: {exc}") from exc
    dependencies = data.get("dependencies")
    if not isinstance(dependencies, list) or not dependencies:
        raise RitsuProfileError(f"manifest dependencies are missing from {manifest}")
    if dependencies[0].get("min_version") != PROFILE.framework_version:
        raise RitsuProfileError(
            f"manifest runtime minimum must remain the API floor {PROFILE.framework_version}"
        )


def validate_restore_assets(project_dir: Path) -> None:
    """Reject a restore that reintroduced framework packages into a local-only project."""
    assets = project_dir / ".godot" / "mono" / "temp" / "obj" / "project.assets.json"
    if not assets.is_file():
        return
    try:
        data = json.loads(assets.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RitsuProfileError(f"cannot read NuGet restore assets {assets}: {exc}") from exc
    libraries = data.get("libraries", {})
    local_only_libraries = [
        str(key)
        for key in libraries
        if (
            "ritsulib" in str(key).lower()
            or "godotsharp" in str(key).lower()
            or "godot.sourcegenerators" in str(key).lower()
            or _BASELIB_RE.search(str(key))
        )
    ]
    if local_only_libraries:
        found = ", ".join(sorted(local_only_libraries))
        raise RitsuProfileError(
            "NuGet restore reintroduced local-only framework packages: " + found
        )


class _RuntimeFiles:
    """Read a runtime payload from an installed folder or a release zip with the same layout."""

    def __init__(self, label: str, read: Callable[[str], bytes | None]) -> None:
        self.label = label
        self._read = read

    def read(self, relative: str) -> bytes:
        data = self._read(relative)
        if data is None:
            raise RitsuProfileError(f"{self.label} is missing {relative}")
        return data

    def text(self, relative: str) -> str:
        # RitsuLib 0.6.x writes compat-target.txt with a UTF-8 BOM.
        return self.read(relative).decode("utf-8-sig")

    def json(self, relative: str) -> dict:
        try:
            data = json.loads(self.text(relative))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RitsuProfileError(f"invalid JSON in {self.label}/{relative}: {exc}") from exc
        if not isinstance(data, dict):
            raise RitsuProfileError(f"{self.label}/{relative} must contain a JSON object")
        return data


def _directory_files(root: Path) -> _RuntimeFiles:
    def read(relative: str) -> bytes | None:
        path = root / relative
        return path.read_bytes() if path.is_file() else None

    return _RuntimeFiles(str(root), read)


def _check_runtime_manifest(data: dict) -> str:
    if data.get("id") != PROFILE.runtime_mod_id:
        raise RitsuProfileError("RitsuLib runtime manifest has an unexpected id")
    version = str(data.get("version", "")).strip()
    if _version_key(version) < _version_key(PROFILE.framework_version):
        raise RitsuProfileError(
            f"RitsuLib runtime manifest version {version!r} is older than the required "
            f"minimum {PROFILE.framework_version}"
        )
    if _version_key(str(data.get("min_game_version", ""))) > _version_key(PROFILE.host_version):
        raise RitsuProfileError(
            f"RitsuLib runtime manifest min_game_version is newer than {PROFILE.host_version}"
        )
    if data.get("dependencies") not in ([], None):
        raise RitsuProfileError("RitsuLib runtime manifest unexpectedly declares dependencies")
    return version


def _manifest_module_hashes(entries: object, expected: tuple[str, ...], where: str) -> dict[str, str]:
    if not isinstance(entries, list) or len(entries) != len(expected):
        raise RitsuProfileError(f"runtime variant manifest has an unexpected module count in {where}")
    hashes: dict[str, str] = {}
    for entry in entries:
        name = entry.get("assembly") if isinstance(entry, dict) else None
        digest = entry.get("sha256") if isinstance(entry, dict) else None
        if name not in expected or name in hashes:
            raise RitsuProfileError(f"runtime variant manifest has an unexpected module in {where}: {name!r}")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9A-Fa-f]{64}", digest):
            raise RitsuProfileError(f"runtime variant manifest has an invalid hash for {name}")
        hashes[name] = digest.lower()
    return hashes


def _check_runtime_payload(files: _RuntimeFiles) -> tuple[str, tuple[RuntimeAssembly, ...]]:
    runtime_version = _check_runtime_manifest(files.json("mod_manifest.json"))
    if not files.read(PROFILE.runtime_dll).startswith(b"MZ"):
        raise RitsuProfileError(f"{files.label}/{PROFILE.runtime_dll} is not a loader assembly")

    manifest = files.json(PROFILE.variant_manifest)
    if manifest.get("schema") != PROFILE.variant_manifest_schema:
        raise RitsuProfileError(
            f"{files.label} uses variant manifest schema {manifest.get('schema')!r}; this "
            f"profile reads the RitsuLib 0.6 schema {PROFILE.variant_manifest_schema} layout"
        )
    variants = manifest.get("variants")
    entry = next(
        (
            item
            for item in (variants if isinstance(variants, list) else [])
            if isinstance(item, dict) and str(item.get("compatTarget")) == PROFILE.host_version
        ),
        None,
    )
    if entry is None:
        raise RitsuProfileError(
            f"runtime {files.label} has no matching {PROFILE.host_version} RitsuLib variant; "
            "refusing to compile against another game version's API"
        )
    marker = files.text(f"{PROFILE.compat_dir}/compat-target.txt").strip()
    if marker != PROFILE.host_version:
        raise RitsuProfileError(f"runtime marker {PROFILE.compat_dir}/compat-target.txt is {marker!r}")

    expected = {
        **_manifest_module_hashes(manifest.get("shared"), PROFILE.shared_assemblies, "shared"),
        **_manifest_module_hashes(entry.get("files"), PROFILE.compat_assemblies, PROFILE.compat_dir),
    }
    assemblies: list[RuntimeAssembly] = []
    for name, relative in PROFILE.assembly_relative_paths():
        payload = files.read(relative)
        digest = hashlib.sha256(payload).hexdigest()
        if not payload.startswith(b"MZ") or digest != expected[name]:
            raise RitsuProfileError(
                f"runtime assembly {relative} does not match {PROFILE.variant_manifest}; "
                "reinstall the complete RitsuLib folder"
            )
        assemblies.append(RuntimeAssembly(name, relative, digest))
    return runtime_version, tuple(assemblies)


def _runtime_root(path: Path) -> Path:
    root = path
    if root.is_dir() and root.name.lower() != PROFILE.runtime_mod_id.lower():
        candidate = root / PROFILE.runtime_mod_id
        if candidate.is_dir():
            root = candidate
    if not root.is_dir():
        raise RitsuProfileError(f"RitsuLib runtime directory not found: {path}")
    return root


def resolve_runtime_compile_profile(path: Path) -> RuntimeCompileProfile:
    """Return the exact local compat and shared assemblies used to compile a generated Mod."""
    if path.suffix.lower() == ".zip":
        raise RitsuProfileError(
            "a RitsuLib zip can be inspected but not used as a local compile assembly; "
            "install its checked folder first"
        )
    root = _runtime_root(path)
    version, assemblies = _check_runtime_payload(_directory_files(root))
    return RuntimeCompileProfile(version, root, assemblies)


def validate_runtime_asset(path: Path) -> str:
    """Validate an installed RitsuLib folder or release zip without loading a DLL."""
    if path.suffix.lower() == ".zip":
        if not path.is_file():
            raise RitsuProfileError(f"RitsuLib runtime asset not found: {path}")
        with zipfile.ZipFile(path) as archive:
            names = {name.replace("\\", "/").lstrip("./"): name for name in archive.namelist()}

            def read(relative: str) -> bytes | None:
                name = names.get(relative)
                return archive.read(name) if name is not None else None

            version, _ = _check_runtime_payload(_RuntimeFiles(path.name, read))
        return f"{path.name}: RitsuLib {version}, compat {PROFILE.host_version}"

    profile = resolve_runtime_compile_profile(path)
    return (
        f"{profile.root}: RitsuLib {profile.version}, compat {PROFILE.host_version}, "
        f"assembly set {profile.assembly_set_sha256[:12]}"
    )


def validate_host_version(sts2_dir: Path) -> str:
    candidates = [
        sts2_dir / "release_info.json",
        sts2_dir / "data_sts2_windows_x86_64" / "game" / "release_info.json",
        sts2_dir / "data_sts2_linuxbsd_x86_64" / "game" / "release_info.json",
        sts2_dir / "SlayTheSpire2.app" / "Contents" / "Resources" / "release_info.json",
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
