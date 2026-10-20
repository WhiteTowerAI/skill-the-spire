#!/usr/bin/env python3
"""Render, refresh, and check the fixed Tier 2 self-test kit of a generated Mod.

The kit is one generated C# file, `<ModName>Code/SelfTestKit.cs`, rendered from the bundled
template `modmaker/assets/selftest-kit/SelfTestKit.cs.tmpl` with only the Mod's namespace
substituted. It owns the arg gate, navigation, combat entry and reset, settling, the roll call,
face checks, the scenario filter, and the terminal markers. A Mod's own scenarios live in
`SelfTestScenarios.cs`, which the kit never touches.
"""
from __future__ import annotations

import re
from pathlib import Path

KIT_FILE = "SelfTestKit.cs"
KIT_TOKEN = "__MOD_NAME__"
KIT_HEADER_RE = re.compile(r"^// SelfTestKit (?P<version>\d+) ")
ARM_LINE = 'if (CommandLineHelper.HasArg("t2selftest")) SelfTestKit.Arm();'


class SelfTestKitError(ValueError):
    """A project's kit file is missing its header or differs from the bundled template."""


def template_path() -> Path:
    script_dir = Path(__file__).resolve().parent
    candidates = (
        script_dir.parent / "assets" / "selftest-kit" / "SelfTestKit.cs.tmpl",
        script_dir.parent / "skills" / "modmaker" / "assets" / "selftest-kit" / "SelfTestKit.cs.tmpl",
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise SelfTestKitError("bundled SelfTestKit.cs.tmpl is missing beside scaffold.py")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def template_version(text: str | None = None) -> int:
    match = KIT_HEADER_RE.match(text if text is not None else _read(template_path()))
    if match is None:
        raise SelfTestKitError("SelfTestKit template has no '// SelfTestKit <version>' header")
    return int(match.group("version"))


def render(mod_name: str) -> str:
    text = _read(template_path())
    if KIT_TOKEN not in text:
        raise SelfTestKitError(f"SelfTestKit template lacks the {KIT_TOKEN} token")
    return text.replace(KIT_TOKEN, mod_name)


def kit_path(project_dir: Path, mod_name: str) -> Path:
    return project_dir / f"{mod_name}Code" / KIT_FILE


def write(project_dir: Path, mod_name: str) -> Path:
    """Write (or overwrite) the kit file. It is generated, so refreshing it loses nothing."""
    path = kit_path(project_dir, mod_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render(mod_name), encoding="utf-8", newline="\n")
    return path


def check(project_dir: Path, mod_name: str) -> str:
    """Return a one-line verdict; raise when a current-version kit was edited by hand.

    A project without the kit (scaffolded before it existed) and a project whose kit is an older
    version both pass with a note: refreshing is the user's choice, because a newer kit may
    change the scenario API that `SelfTestScenarios.cs` was written against.
    """
    path = kit_path(project_dir, mod_name)
    if not path.is_file():
        return f"no {KIT_FILE} (project predates the kit)"
    actual = _read(path)
    match = KIT_HEADER_RE.match(actual)
    if match is None:
        raise SelfTestKitError(f"{path.name} has no '// SelfTestKit <version>' header; "
                               "run scaffold.py --refresh-selftest-kit")
    version = int(match.group("version"))
    current = template_version()
    if version < current:
        return (f"{KIT_FILE} v{version} is older than the bundled v{current}; "
                "scaffold.py --refresh-selftest-kit updates it")
    if version > current:
        raise SelfTestKitError(f"{path.name} v{version} is newer than the bundled v{current}")
    if actual != render(mod_name):
        raise SelfTestKitError(f"{path.name} differs from the bundled kit v{current}. It is generated: "
                               "put scenarios in SelfTestScenarios.cs and run "
                               "scaffold.py --refresh-selftest-kit to restore it")
    return f"{KIT_FILE} v{version} matches the bundled kit"
