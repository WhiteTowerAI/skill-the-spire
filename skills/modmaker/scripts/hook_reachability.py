#!/usr/bin/env python3
"""Fail a Build whose compiled Mod overrides a model hook its surface never receives.

A Mod element can override any `public virtual` hook on `AbstractModel`, but the host dispatches
each hook only through certain listener sets: a run-scope hook never reaches a Power, Orb, or
Monster. Such an override compiles, ships, and silently never fires. The model-hook catalog
records, per hook, the surfaces it can reach. This check reads the built Mod DLL's public
metadata (no loading, no decompiling), finds each override of a cataloged hook, and requires its
surface to be among them. It replaces declaring the hook by hand in SPEC.

A Global Effect's scope comes from its `HookType.Run`/`HookType.Combat` constructor argument in
source; when that cannot be read, either global scope is accepted.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import api

HOOK_CATALOG_NAME = "model-hooks-sts2-0.107.1.json"

# The first base type outside the Mod assembly decides the surface.
SURFACE_BASES = {
    "ModCardTemplate": "card", "CardModel": "card",
    "ModRelicTemplate": "relic", "RelicModel": "relic",
    "ModPotionTemplate": "potion", "PotionModel": "potion",
    "ModPowerTemplate": "power", "PowerModel": "power",
    "ModOrbTemplate": "orb", "OrbModel": "orb",
    "ModEnchantmentTemplate": "enchantment", "EnchantmentModel": "enchantment",
    "ModAfflictionTemplate": "affliction", "AfflictionModel": "affliction",
    "ModMonsterTemplate": "monster", "MonsterModel": "monster",
    "ModModifierTemplate": "modifier", "ModifierModel": "modifier",
    "HookedSingletonModel": "global-effect",
}
GLOBAL_SCOPE_RE = re.compile(r"\bHookType\s*\.\s*(Run|Combat)\b")


class HookReachabilityError(ValueError):
    """A compiled override can never be dispatched to its surface."""


class ModAssembly(api.Assembly):
    """The Mod's own assembly: internal content types count too."""

    def type_access(self, row: int) -> str | None:
        return "public"


def hook_catalog_path() -> Path:
    here = Path(__file__).resolve().parent
    for root in (here.parent / "skills" / "sts2api", here.parents[1] / "sts2api"):
        path = root / "reference" / "catalogs" / HOOK_CATALOG_NAME
        if path.is_file():
            return path
    raise HookReachabilityError(f"cannot locate the shipped {HOOK_CATALOG_NAME}")


def load_hooks(path: Path | None = None) -> dict[str, dict]:
    raw = json.loads((path or hook_catalog_path()).read_text(encoding="utf-8"))
    return {hook["hook"]: hook for hook in raw["hooks"]}


def _base_name(assembly: api.Assembly, info: api.TypeInfo) -> tuple[str | None, bool]:
    """(simple name of the base type, whether it lies outside this assembly)."""
    base = info.base
    if base is None:
        return None, True
    if base.kind == "spec":
        spec = assembly.spec(base.code)
        base = spec.args[0] if spec.kind == "generic" else spec
    if base.kind not in ("def", "ref"):
        return None, True
    _ns, display, _doc = assembly.named(base)
    return display.rsplit(".", 1)[-1], base.kind == "ref"


def surface_of(assembly: api.Assembly, info: api.TypeInfo, by_name: dict[str, api.TypeInfo]) -> str | None:
    seen: set[str] = set()
    current = info
    while current is not None and current.name not in seen:
        seen.add(current.name)
        name, external = _base_name(assembly, current)
        if name is None:
            return None
        if external:
            return SURFACE_BASES.get(name)
        current = by_name.get(name)
    return None


def global_scopes(project_dir: Path | None, type_name: str) -> set[str]:
    if project_dir is not None:
        class_re = re.compile(rf"\bclass\s+{re.escape(type_name)}\b")
        for path in project_dir.rglob("*.cs"):
            text = path.read_text(encoding="utf-8", errors="replace")
            if class_re.search(text):
                kinds = set(GLOBAL_SCOPE_RE.findall(text))
                if len(kinds) == 1:
                    return {f"global-effect-{kinds.pop().lower()}"}
    return {"global-effect-run", "global-effect-combat"}


def unreachable_overrides(dll: Path, *, project_dir: Path | None = None,
                          hooks: dict[str, dict] | None = None) -> list[str]:
    hooks = hooks if hooks is not None else load_hooks()
    assembly = ModAssembly("mod", dll)
    assembly.build()
    by_name = {info.name: info for info in assembly.types}
    findings = []
    for info in assembly.types:
        surface = surface_of(assembly, info, by_name)
        if surface is None:
            continue
        candidates = (global_scopes(project_dir, info.name) if surface == "global-effect"
                      else {surface})
        for member in info.members:
            hook = hooks.get(member.name)
            if member.kind != "method" or hook is None or " override " not in f" {member.text} ":
                continue
            allowed = set(hook["authorable_surfaces"])
            if candidates & allowed:
                continue
            shown = " or ".join(sorted(candidates))
            if surface == "enchantment" and hook.get("enchantment_redirect"):
                fix = f"override {hook['enchantment_redirect']} instead"
            else:
                fix = f"move the rule to one of: {', '.join(sorted(allowed))}"
            findings.append(
                f"{info.name}.{member.name}: the host never dispatches this hook to a {shown}; {fix}"
            )
    return findings


def validate_built_mod(dll: Path, project_dir: Path | None = None) -> str:
    findings = unreachable_overrides(dll, project_dir=project_dir)
    if findings:
        raise HookReachabilityError(
            "overrides that compile but never fire (reference/model-hook-participation.md): "
            + "; ".join(findings)
        )
    return "every cataloged hook override reaches its surface"
