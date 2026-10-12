#!/usr/bin/env python3
"""Check only capability existence and silent hook reachability before authoring.

The generated SPEC remains a human-readable implementation work order. It may contain these
declaration lines anywhere in the document:

    - Support: recipes/card.md
    - Support: reference/card-computed-values.md
    - Hook: modify_damage_multiplicative | surface: power | shape: value |
      route: reference/model-hook-participation.md
    - Mod-local: grant gold - PlayerCmd.GainGold

This tool deliberately does not validate Markdown structure, ordinary fields, business rules,
localization, manifests, lifecycle behavior, evidence, or project status. Build and real-host
verification own those checks. A Mod-local line must name at least one public Owner.Member; the
compiler checks that member. A SPEC made only of Mod-local routes is skipped, and a SPEC with no
Support, Hook, or Mod-local line fails because its Implementation section is missing.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


HOOK_CATALOG_NAME = "model-hooks-sts2-0.107.1.json"
CAPABILITY_DECLARATION_RE = re.compile(
    r"<!--\s*skillthespire-capabilities:\s*(.*?)\s*-->", re.DOTALL
)
SUPPORT_RE = re.compile(r"^\s*-\s*Support\s*:\s*`?(?P<route>[^`\s]+)`?\s*$", re.I)
HOOK_RE = re.compile(r"^\s*-\s*Hook\s*:\s*(?P<body>.+?)\s*$", re.I)
MOD_LOCAL_RE = re.compile(r"^\s*-\s*Mod-local\s*:\s*(?P<body>.+?)\s*$", re.I)
PUBLIC_MEMBER_RE = re.compile(r"\b[A-Za-z_]\w*\.[A-Za-z_]\w*")
ROUTE_RE = re.compile(r"^(?:recipes|reference)/[a-z0-9][a-z0-9_./-]*\.md$")
CAPABILITY_RE = re.compile(r"^[a-z][a-z0-9_]*$")
SURFACE_RE = re.compile(r"^[a-z][a-z0-9_-]*$")
SHAPES = {"scalar-return": "value", "out-replacement": "out-replacement", "collection-edit": "collection"}


class CapabilityPreflightError(ValueError):
    """Raised when a selected route or hook would be unsupported or silently unreachable."""


@dataclass(frozen=True)
class HookSelection:
    capability: str
    surface: str
    shape: str
    route: str
    line: int


def _tools_dir() -> Path:
    return Path(__file__).resolve().parent


def api_root() -> Path:
    """Resolve sts2api in the repository or in either published payload layout."""
    here = _tools_dir()
    candidates = (
        here.parent / "skills" / "sts2api",
        here.parents[1] / "sts2api",
    )
    for candidate in candidates:
        if (candidate / "reference").is_dir() and (candidate / "recipes").is_dir():
            return candidate
    raise CapabilityPreflightError("cannot locate the shipped sts2api root")


def hook_catalog_path() -> Path:
    path = api_root() / "reference" / "catalogs" / HOOK_CATALOG_NAME
    if not path.is_file():
        raise CapabilityPreflightError(f"cannot locate the shipped {HOOK_CATALOG_NAME}")
    return path


def declared_capabilities(text: str) -> set[str]:
    declared: set[str] = set()
    for match in CAPABILITY_DECLARATION_RE.findall(text):
        declared.update(
            token.strip() for token in match.replace(",", " ").split() if token.strip()
        )
    return declared


def load_hook_catalog() -> dict[str, dict]:
    raw = json.loads(hook_catalog_path().read_text(encoding="utf-8"))
    entries: dict[str, dict] = {}
    for hook in raw["hooks"]:
        entries[hook["semantic_id"]] = hook
        redirect = hook.get("enchantment_redirect")
        if redirect:
            redirect_id = re.sub(r"(?<!^)(?=[A-Z])", "_", redirect).lower()
            entries[redirect_id] = {
                "semantic_id": redirect_id,
                "declaration_shape": hook["declaration_shape"],
                "authorable_surfaces": ["enchantment"],
                "replaces": hook["semantic_id"],
            }
    return entries


def _clean(value: str) -> str:
    return value.strip().strip("`").strip()


def _route_file(route: str) -> Path:
    if "#" in route:
        raise CapabilityPreflightError(
            f"support route {route!r} must name a recipe/reference file, not a Markdown anchor"
        )
    if not ROUTE_RE.fullmatch(route):
        raise CapabilityPreflightError(f"invalid support route {route!r}")
    root = api_root().resolve()
    path = (root / route).resolve()
    if root not in path.parents or not path.is_file():
        raise CapabilityPreflightError(f"support route does not exist: {route}")
    return path


def _parse_hook(body: str, line_number: int) -> HookSelection:
    parts = [_clean(part) for part in body.split("|")]
    capability = parts[0] if parts else ""
    fields: dict[str, str] = {}
    for part in parts[1:]:
        key, separator, value = part.partition(":")
        if not separator:
            raise CapabilityPreflightError(f"invalid Hook field: {part!r}")
        fields[key.strip().lower()] = _clean(value)
    missing = [name for name in ("surface", "shape", "route") if not fields.get(name)]
    if missing:
        raise CapabilityPreflightError(f"Hook is missing: {', '.join(missing)}")
    if not CAPABILITY_RE.fullmatch(capability):
        raise CapabilityPreflightError(f"invalid hook capability {capability!r}")
    if not SURFACE_RE.fullmatch(fields["surface"]):
        raise CapabilityPreflightError(f"invalid hook surface {fields['surface']!r}")
    return HookSelection(
        capability, fields["surface"], fields["shape"], fields["route"], line_number
    )


def _check_mod_local(body: str) -> None:
    _, separator, members = body.partition(" - ")
    if not separator or not PUBLIC_MEMBER_RE.search(members):
        raise CapabilityPreflightError(
            "Mod-local must read '<operation> - <public Owner.Member list>'"
        )


def parse_implementation(
    text: str, errors: list[str]
) -> tuple[list[tuple[int, str]], list[HookSelection], int]:
    """Collect Support routes, Hook selections, and the Mod-local count; append line errors."""
    routes: list[tuple[int, str]] = []
    hooks: list[HookSelection] = []
    mod_local = 0
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line.strip() or line.lstrip().startswith("<!--"):
            continue
        support = SUPPORT_RE.match(line)
        if support:
            routes.append((line_number, _clean(support.group("route"))))
            continue
        hook = HOOK_RE.match(line)
        if hook:
            try:
                hooks.append(_parse_hook(hook.group("body"), line_number))
            except CapabilityPreflightError as exc:
                errors.append(f"line {line_number}: {exc}")
            continue
        local = MOD_LOCAL_RE.match(line)
        if local:
            mod_local += 1
            try:
                _check_mod_local(local.group("body"))
            except CapabilityPreflightError as exc:
                errors.append(f"line {line_number}: {exc}")
    return routes, hooks, mod_local


def _check_hook(hook: HookSelection, catalog: dict[str, dict]) -> None:
    route_file = _route_file(hook.route)
    entry = catalog.get(hook.capability)
    if entry is None:
        raise CapabilityPreflightError(
            f"hook capability {hook.capability!r} is not in {HOOK_CATALOG_NAME}"
        )
    owned_by = entry.get("owned_by_route")
    if owned_by:
        raise CapabilityPreflightError(
            f"hook capability {hook.capability!r} is owned by {owned_by}; use that route"
        )
    authorable = entry["authorable_surfaces"]
    if hook.surface not in authorable:
        raise CapabilityPreflightError(
            f"hook capability {hook.capability!r} cannot reach surface {hook.surface!r}; "
            f"authorable on: {', '.join(authorable)}"
        )
    expected_shape = SHAPES[entry["declaration_shape"]]
    if hook.shape != expected_shape:
        raise CapabilityPreflightError(
            f"hook capability {hook.capability!r} uses shape {hook.shape!r}; "
            f"the catalog requires {expected_shape!r}"
        )
    if hook.capability not in declared_capabilities(route_file.read_text(encoding="utf-8")):
        raise CapabilityPreflightError(
            f"hook route {hook.route} does not declare capability {hook.capability!r}"
        )


def validate_spec_text(text: str) -> tuple[int, int, bool]:
    """Return (support routes, hooks, skipped); raise once with every line error."""
    errors: list[str] = []
    routes, hooks, mod_local = parse_implementation(text, errors)
    if not routes and not hooks and not mod_local and not errors:
        raise CapabilityPreflightError(
            "SPEC declares no Support, Hook, or Mod-local line; write its ## Implementation section"
        )
    for line_number, route in routes:
        try:
            _route_file(route)
        except CapabilityPreflightError as exc:
            errors.append(f"line {line_number}: {exc}")
    catalog = load_hook_catalog() if hooks else {}
    for hook in hooks:
        try:
            _check_hook(hook, catalog)
        except CapabilityPreflightError as exc:
            errors.append(f"line {hook.line}: {exc}")
    if errors:
        raise CapabilityPreflightError("\n".join(errors))
    return len(routes), len(hooks), not routes and not hooks


def validate_spec_file(path: Path) -> tuple[int, int, bool]:
    return validate_spec_text(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check selected support routes and hook reachability before authoring."
    )
    parser.add_argument("--spec", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        routes, hooks, skipped = validate_spec_file(args.spec)
    except (CapabilityPreflightError, OSError, KeyError, json.JSONDecodeError) as exc:
        print("[capability-preflight] failed:", file=sys.stderr)
        for line in str(exc).splitlines():
            print(f"  {line}", file=sys.stderr)
        return 2
    if skipped:
        print("[capability-preflight] skipped: SPEC declares only Mod-local routes")
    else:
        print(f"[capability-preflight] ok support_routes={routes} hooks={hooks}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
