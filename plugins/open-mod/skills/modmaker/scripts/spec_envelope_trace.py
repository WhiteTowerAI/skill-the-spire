#!/usr/bin/env python3
"""Validate a generated project's `SPEC.md` against its surface's v2 envelope.

This closes the half of M8.0 mismatch 8 that the envelope-form decision was blocking. The
other half is covered by `tests/test_surface_cross_check.py`, which pairs each mandatory
envelope field with the proof case that observes it -- but only inside the *shipped pack*.
Nothing checked a *generated* project, so a SPEC could invent a top-level key or drop a whole
shared section and every later stage would read it as authoritative.

That was only checkable once one canonical envelope form existed. Under v1 six surfaces used a
flat `element:` opening with ad-hoc keys while card and relic used the nested form, so there
was no single shape to validate against; `semantic-contract.md` claimed authority its own
surfaces did not honor. v2 normalizes all ten, which is what makes this tool possible.

Five checks, deliberately structural:

1. every shared section the canonical envelope names is present;
2. no top-level key outside the canonical set plus that surface's own declared fields; and
3. every localization section declares the required English and Simplified Chinese languages;
4. the contract line is v2, while v1/absent projects resume under their existing terms; and
   unchanged rather than failing; and
5. every declared `hook participation` names a capability the pinned catalog knows, with the
   shape the catalog records, on a surface that can actually receive it.

Check 4 is the one that closes the M7.6 Wrath class before generation. A hook declared on a
surface outside its dispatcher's listener set compiles, ships, and never fires -- every local
stage passes and the promised behavior is absent, which is the failure this Package exists for.

What it does not do: judge whether a declared value is *right*. A SPEC can pass this and still
describe the wrong Mod. It checks that the SPEC is shaped like the surface it claims to be.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


CONTRACT_V2 = "sts2-content-semantic/v2"
CONTRACT_V1 = "sts2-content-semantic/v1"

# The nine shared sections `semantic-contract.md` declares canonical, plus the envelope-level
# identity keys every surface page opens with.
REQUIRED_SECTIONS = (
    "content",
    "registration",
    "localization",
    "effects",
    "state",
    "presentation",
    "fallback",
    "proof",
)
IDENTITY_KEYS = ("contract", "mod id", "author")
REQUIRED_LOCALIZATION_LANGUAGES = ("eng", "zhs")

# Top-level keys a surface may add beside the shared sections. Read from the shipped surface
# pages rather than hardcoded, so a page and this validator cannot disagree about what that
# surface may declare.
SURFACE_PAGE_DIR = Path("skills") / "modmaker" / "surfaces"

TOP_LEVEL_RE = re.compile(r"^-\s+\*\*(?P<key>[^*]+)\*\*\s*:", re.MULTILINE)
SURFACE_RE = re.compile(r"^\s*(?:-\s+)?surface:\s*(?P<surface>[a-z][a-z ]*)", re.MULTILINE)
LOCALIZATION_BLOCK_RE = re.compile(
    r"^-\s+\*\*localization\*\*\s*:\s*$\n(?P<body>.*?)"
    r"(?=^-\s+\*\*[^*]+\*\*\s*:|\Z)",
    re.MULTILINE | re.DOTALL,
)
LOCALIZATION_LANGUAGES_RE = re.compile(
    r"^\s*-\s+languages:\s*\[(?P<languages>[^\]]*)\]\s*$", re.MULTILINE
)

# A hook participation entry opens with its capability id and carries `shape:` beneath it. The
# id is the pairing key `design_trace.py` matches against the route page; the shape is declared
# rather than derived so a mis-declared one is caught here instead of becoming generated C#.
CAPABILITY_ENTRY_RE = re.compile(
    r"^(?P<indent>\s*)-?\s*capability:\s*(?P<id>[a-z][a-z0-9_]*)\s*$", re.MULTILINE
)
ENCHANTMENT_RE = re.compile(r"^(?P<indent>\s*)(?:-\s+)?enchantment\s*:")
HOOK_PARTICIPATION_RE = re.compile(
    r"^(?P<indent>\s*)(?:-\s+)?(?:\*\*)?hook participation(?:\*\*)?\s*:\s*(?P<value>.*)$"
)
ENTRY_FIELD_RE = re.compile(r"^\s*(?P<field>[a-z][a-z -]*)\s*:\s*(?P<value>.*)$")
HOOK_CATALOG_NAME = "model-hooks-sts2-0.107.1.json"
# The declaration shapes the catalog uses, mapped to the SPEC-facing word an author writes.
SHAPE_ALIASES = {
    "scalar-return": "value",
    "out-replacement": "out-replacement",
    "collection-edit": "collection",
}


class SpecEnvelopeError(ValueError):
    """Raised when a generated SPEC does not match its surface's envelope."""


def _tools_dir() -> Path:
    return Path(__file__).resolve().parent


def surface_page_root() -> Path:
    """Resolve the surface pages from either the repo layout or a published payload.

    Repo:    games/sts2/tools/            -> games/sts2/skills/modmaker/surfaces/
    Payload: skills/modmaker/scripts/     -> skills/modmaker/surfaces/

    The payload candidate must keep the `modmaker` segment. An earlier form omitted it and
    resolved to `skills/surfaces`, which exists in neither layout -- so the tool `spec.md` tells
    every project to run failed on any installed payload while passing in the repo.
    """
    here = _tools_dir()
    candidates = (
        here.parent / SURFACE_PAGE_DIR,
        here.parents[1] / "modmaker" / "surfaces",
    )
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    raise SpecEnvelopeError("cannot locate the shipped surfaces/ pages")


def allowed_top_level_keys(surface: str) -> set[str]:
    """Canonical sections plus the extra top-level keys this surface's page declares.

    The surface page is the source of truth: whatever top-level keys its own `## SPEC envelope`
    block shows are legal for a SPEC of that surface. A key appearing in neither the canonical
    set nor the page is invented, which is exactly what `design_trace.py` accepted silently.
    """
    allowed = set(REQUIRED_SECTIONS) | set(IDENTITY_KEYS)
    slug = surface.strip().replace(" ", "-")
    # `enemy encounter` is declared on the monster page.
    page = surface_page_root() / f"{'monster' if slug == 'enemy-encounter' else slug}.md"
    if not page.is_file():
        raise SpecEnvelopeError(f"no shipped surface page for surface {surface!r}")
    text = page.read_text(encoding="utf-8")
    envelope = re.search(
        r"##\s+SPEC envelope\n(.*?)(?=\n##\s|\Z)", text, re.DOTALL
    )
    if envelope is None:
        raise SpecEnvelopeError(f"surfaces/{slug}.md has no '## SPEC envelope' section")
    allowed.update(
        key.strip().lower() for key in TOP_LEVEL_RE.findall(envelope.group(1))
    )
    return allowed


def declared_surfaces(text: str) -> list[str]:
    return [match.strip() for match in SURFACE_RE.findall(text)]


def hook_catalog_path() -> Path:
    """Locate the shipped model-hook catalog from either the repo or a published payload."""
    here = _tools_dir()
    candidates = (
        here.parent / "skills" / "sts2-api" / "reference" / "catalogs" / HOOK_CATALOG_NAME,
        here.parents[1] / "sts2-api" / "reference" / "catalogs" / HOOK_CATALOG_NAME,
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise SpecEnvelopeError(f"cannot locate the shipped {HOOK_CATALOG_NAME}")


def load_hook_catalog() -> dict[str, dict]:
    """Catalog entries keyed by semantic id, plus the five Enchantment redirect ids.

    The redirects are `EnchantmentModel` methods rather than `AbstractModel` hooks, so they are
    not catalog entries of their own. They are synthesized here from the `enchantment_redirect`
    field so a SPEC can declare one, and so declaring one anywhere but an enchantment fails.
    """
    raw = json.loads(hook_catalog_path().read_text(encoding="utf-8"))
    entries: dict[str, dict] = {}
    for hook in raw["hooks"]:
        entries[hook["semantic_id"]] = hook
        redirect = hook.get("enchantment_redirect")
        if redirect:
            redirect_id = re.sub(r"(?<!^)(?=[A-Z])", "_", redirect).lower()
            entries[redirect_id] = {
                "hook": redirect,
                "semantic_id": redirect_id,
                "declaration_shape": hook["declaration_shape"],
                "authorable_surfaces": ["enchantment"],
                "replaces": hook["semantic_id"],
            }
    return entries


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip())


def _hook_participation_entries(text: str) -> list[tuple[str, dict[str, str], str]]:
    """Return capability fields and their indentation-scoped owning surfaces."""
    lines = text.splitlines()
    current_surface = ""
    enchantment_indent: int | None = None
    declarations: list[tuple[str, dict[str, str], str]] = []

    for index, line in enumerate(lines):
        if not line.strip():
            continue
        indent = _indent(line)
        if enchantment_indent is not None and indent <= enchantment_indent:
            enchantment_indent = None

        surface_match = SURFACE_RE.match(line)
        if surface_match:
            current_surface = surface_match.group("surface").strip()

        enchantment_match = ENCHANTMENT_RE.match(line)
        if enchantment_match:
            enchantment_indent = len(enchantment_match.group("indent"))

        capability_match = CAPABILITY_ENTRY_RE.match(line)
        if capability_match is None:
            continue

        fields: dict[str, str] = {}
        capability_indent = len(capability_match.group("indent"))
        for following in lines[index + 1 :]:
            if not following.strip():
                continue
            if _indent(following) <= capability_indent:
                break
            field_match = ENTRY_FIELD_RE.match(following)
            if field_match:
                fields[field_match.group("field").strip()] = field_match.group("value").strip()

        owner = "enchantment" if enchantment_indent is not None else current_surface
        declarations.append((capability_match.group("id"), fields, owner))
    return declarations


def hook_participations(text: str) -> list[tuple[str, str | None, str]]:
    """Every declared `(capability id, shape or None, owning surface)` in SPEC order."""
    return [
        (capability_id, fields.get("shape"), owner)
        for capability_id, fields, owner in _hook_participation_entries(text)
    ]


def _validate_nonempty_hook_blocks(text: str) -> None:
    """A participation block claiming entries must contain at least one capability."""
    lines = text.splitlines()
    for index, line in enumerate(lines):
        match = HOOK_PARTICIPATION_RE.match(line)
        if match is None or match.group("value").strip().lower() == "none":
            continue

        block_indent = len(match.group("indent"))
        has_capability = False
        for following in lines[index + 1 :]:
            if not following.strip():
                continue
            following_indent = _indent(following)
            capability_match = CAPABILITY_ENTRY_RE.match(following)
            if following_indent < block_indent:
                break
            if following_indent == block_indent and capability_match is None:
                break
            if capability_match:
                has_capability = True
                break
        if not has_capability:
            raise SpecEnvelopeError(
                f"hook participation block at line {index + 1} has no capability entry"
            )


def validate_hook_participation(text: str) -> int:
    """Reject a hook the declaring surface cannot receive, and a contradicted shape.

    This is the check that closes the M7.6 Wrath class at preflight rather than at review. A
    declaration naming a hook its own surface is not in the listener set for compiles, ships, and
    never fires — the exact failure shape where every local stage passes and the promised
    behavior is absent. A shape the catalog contradicts is the same class one step later: a
    collection edit written as a replacement value cannot express what it needs to.
    """
    _validate_nonempty_hook_blocks(text)
    declarations = _hook_participation_entries(text)
    if not declarations:
        return 0

    catalog = load_hook_catalog()
    for capability_id, fields, owning_surface in declarations:
        entry = catalog.get(capability_id)
        if entry is None:
            raise SpecEnvelopeError(
                f"hook participation declares unknown capability {capability_id!r}; it is not "
                f"in {HOOK_CATALOG_NAME}"
            )
        owned_by = entry.get("owned_by_route")
        if owned_by:
            raise SpecEnvelopeError(
                f"hook participation declares {capability_id!r}, which is owned by "
                f"{owned_by} and must be declared through that route instead"
            )
        authorable = entry["authorable_surfaces"]
        surface = owning_surface or "?"
        if surface not in authorable:
            raise SpecEnvelopeError(
                f"hook participation declares {capability_id!r} on surface {surface!r}, which "
                f"cannot receive it; authorable on: {', '.join(authorable)}"
            )
        shape = fields.get("shape")
        if not shape:
            raise SpecEnvelopeError(
                f"hook participation declares {capability_id!r} without required field 'shape'"
            )
        expected = SHAPE_ALIASES[entry["declaration_shape"]]
        if shape != expected:
            raise SpecEnvelopeError(
                f"hook participation declares {capability_id!r} with shape {shape!r}, but "
                f"the catalog records {expected!r}"
            )

        required_fields = [
            "player-facing",
            "subject",
            "condition",
            "dynamic value name",
            "outside the condition",
        ]
        if shape == "value":
            required_fields.append("value")
        elif shape == "out-replacement":
            required_fields.extend(("value", "replaces"))
        elif shape == "collection":
            required_fields.extend(("edit", "other entries", "ordering"))
        for field in required_fields:
            if not fields.get(field):
                raise SpecEnvelopeError(
                    f"hook participation declares {capability_id!r} without required field "
                    f"{field!r}"
                )
    return len(declarations)


def validate_localization_languages(text: str) -> int:
    """Require every v2 surface localization block to name the fixed language pair."""
    blocks = list(LOCALIZATION_BLOCK_RE.finditer(text))
    if not blocks:
        raise SpecEnvelopeError("SPEC has no readable localization section")
    for index, block in enumerate(blocks, start=1):
        match = LOCALIZATION_LANGUAGES_RE.search(block.group("body"))
        if match is None:
            raise SpecEnvelopeError(
                f"localization section {index} is missing required languages [eng, zhs]"
            )
        languages = tuple(
            language.strip() for language in match.group("languages").split(",")
        )
        if languages != REQUIRED_LOCALIZATION_LANGUAGES:
            raise SpecEnvelopeError(
                f"localization section {index} languages must be [eng, zhs]; "
                f"found [{', '.join(languages)}]"
            )
    return len(blocks)


def validate_spec_text(text: str) -> tuple[str, int]:
    """Return the contract version validated and how many top-level keys were checked."""
    if CONTRACT_V2 not in text:
        if CONTRACT_V1 in text:
            # A pre-v2 project resumes unchanged, the same precedent an absent coherence or
            # deliverable block sets. Only new or revised SPECs are written as v2.
            return CONTRACT_V1, 0
        if "contract" not in text:
            return "absent", 0
        raise SpecEnvelopeError(
            f"SPEC declares a contract line that is neither {CONTRACT_V2} nor {CONTRACT_V1}"
        )

    surfaces = declared_surfaces(text)
    if not surfaces:
        raise SpecEnvelopeError(
            "SPEC declares no `surface:` line, so its envelope cannot be resolved"
        )

    allowed: set[str] = set()
    for surface in surfaces:
        allowed |= allowed_top_level_keys(surface)

    present = {key.strip().lower() for key in TOP_LEVEL_RE.findall(text)}
    missing = [section for section in REQUIRED_SECTIONS if section not in present]
    if missing:
        raise SpecEnvelopeError(
            "SPEC is missing required shared sections: " + ", ".join(missing)
        )
    validate_localization_languages(text)

    invented = sorted(present - allowed)
    if invented:
        raise SpecEnvelopeError(
            "SPEC declares top-level keys no surface envelope allows: "
            + ", ".join(invented)
        )
    validate_hook_participation(text)
    return CONTRACT_V2, len(present)


def validate_spec_file(path: Path) -> tuple[str, int]:
    return validate_spec_text(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate a generated SPEC.md against its surface's v2 envelope."
    )
    parser.add_argument("--spec", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        contract, keys = validate_spec_file(args.spec)
    except (SpecEnvelopeError, OSError) as exc:
        print(f"[spec-envelope] failed: {exc}", file=sys.stderr)
        return 2
    if contract == CONTRACT_V2:
        print(f"[spec-envelope] ok contract={contract} top_level_keys={keys}")
    else:
        print(f"[spec-envelope] ok contract={contract} (pre-v2; resumes unchanged)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
