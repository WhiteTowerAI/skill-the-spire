#!/usr/bin/env python3
"""Check only capability existence and silent hook reachability before authoring.

The generated SPEC remains a human-readable implementation work order. It may contain these
declaration lines anywhere in the document:

    - Support: recipes/card.md
    - Support: reference/card-computed-values.md
    - Hook: modify_damage_multiplicative | surface: power | shape: value |
      route: reference/model-hook-participation.md

This tool deliberately does not validate Markdown structure, ordinary fields, business rules,
localization, manifests, lifecycle behavior, evidence, or project status. Build and real-host
verification own those checks. A SPEC with no Support or Hook declarations is treated as an
unchanged legacy SPEC and skipped.
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
    r"<!--\s*openmod-capabilities:\s*(.*?)\s*-->", re.DOTALL
)
SUPPORT_RE = re.compile(r"^\s*-\s*Support\s*:\s*`?(?P<route>[^`\s]+)`?\s*$", re.I)
HOOK_RE = re.compile(r"^\s*-\s*Hook\s*:\s*(?P<body>.+?)\s*$", re.I)
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


def _tools_dir() -> Path:
    return Path(__file__).resolve().parent


def api_root() -> Path:
    """Resolve sts2-api in the repository or in either published payload layout."""
    here = _tools_dir()
    candidates = (
        here.parent / "skills" / "sts2-api",
        here.parents[1] / "sts2-api",
    )
    for candidate in candidates:
        if (candidate / "reference").is_dir() and (candidate / "recipes").is_dir():
            return candidate
    raise CapabilityPreflightError("cannot locate the shipped sts2-api root")


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
            raise CapabilityPreflightError(
                f"Implementation line {line_number} has an invalid Hook field: {part!r}"
            )
        fields[key.strip().lower()] = _clean(value)
    missing = [name for name in ("surface", "shape", "route") if not fields.get(name)]
    if missing:
        raise CapabilityPreflightError(
            f"Implementation line {line_number} Hook is missing: {', '.join(missing)}"
        )
    if not CAPABILITY_RE.fullmatch(capability):
        raise CapabilityPreflightError(f"invalid hook capability {capability!r}")
    if not SURFACE_RE.fullmatch(fields["surface"]):
        raise CapabilityPreflightError(f"invalid hook surface {fields['surface']!r}")
    return HookSelection(capability, fields["surface"], fields["shape"], fields["route"])


def parse_implementation(text: str) -> tuple[list[str], list[HookSelection]] | None:
    routes: list[str] = []
    hooks: list[HookSelection] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line.strip() or line.lstrip().startswith("<!--"):
            continue
        support = SUPPORT_RE.match(line)
        if support:
            routes.append(_clean(support.group("route")))
            continue
        hook = HOOK_RE.match(line)
        if hook:
            hooks.append(_parse_hook(hook.group("body"), line_number))
    if not routes and not hooks:
        return None
    return routes, hooks


def validate_spec_text(text: str) -> tuple[int, int, bool]:
    parsed = parse_implementation(text)
    if parsed is None:
        return 0, 0, True
    routes, hooks = parsed
    for route in routes:
        _route_file(route)

    catalog = load_hook_catalog()
    for hook in hooks:
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
        if hook.capability not in declared_capabilities(
            route_file.read_text(encoding="utf-8")
        ):
            raise CapabilityPreflightError(
                f"hook route {hook.route} does not declare capability {hook.capability!r}"
            )
    return len(routes), len(hooks), False


def validate_spec_file(path: Path) -> tuple[int, int, bool]:
    return validate_spec_text(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check selected support routes and hook reachability before authoring."
    )
    parser.add_argument("--spec", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        routes, hooks, legacy = validate_spec_file(args.spec)
    except (CapabilityPreflightError, OSError, KeyError, json.JSONDecodeError) as exc:
        print(f"[capability-preflight] failed: {exc}", file=sys.stderr)
        return 2
    if legacy:
        print("[capability-preflight] skipped: unchanged legacy SPEC has no Support or Hook declarations")
    else:
        print(f"[capability-preflight] ok support_routes={routes} hooks={hooks}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
