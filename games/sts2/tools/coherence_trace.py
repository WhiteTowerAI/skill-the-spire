#!/usr/bin/env python3
"""Validate the M7.5 coherence contract embedded in DESIGN.md."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


COHERENCE_CONTRACT = "open-mod-coherence/v1"
COHERENCE_START = "<!-- open-mod-coherence:v1:start -->"
COHERENCE_END = "<!-- open-mod-coherence:v1:end -->"
ANCHOR_ID_RE = re.compile(r"^A-[0-9]{3}$")
QUEUE_ID_RE = re.compile(r"^Q-[0-9]{3}$")
DESIGN_ID_RE = re.compile(r"^D-[0-9]{3}$")
SURFACES = {
    "mechanics",
    "naming",
    "localization",
    "visuals",
    "event-text",
    "character-identity",
}
SURFACE_STATUSES = {"aligned", "deliberate-tension", "conflict"}
QUEUE_TARGETS = {
    "DESIGN",
    "SPEC",
    "localization",
    "visuals",
    "event-text",
    "character-identity",
    "generated-source",
    "verification",
}
QUEUE_ACTIONS = {"UPDATE", "REVIEW", "REVERIFY", "PRESERVE"}


class CoherenceTraceError(ValueError):
    """Raised when a DESIGN coherence contract is malformed or unresolved."""


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CoherenceTraceError(f"{label} must be a nonempty string")
    return value.strip()


def _require_string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list):
        raise CoherenceTraceError(f"{label} must be a list")
    result = [_require_string(entry, f"{label}[{index}]") for index, entry in enumerate(value)]
    if len(result) != len(set(result)):
        raise CoherenceTraceError(f"{label} contains duplicates")
    return result


def _extract_json_block(text: str, start: str, end: str, label: str) -> dict[str, Any]:
    pattern = re.compile(
        rf"{re.escape(start)}\s*```json\s*(.*?)\s*```\s*{re.escape(end)}",
        re.DOTALL,
    )
    matches = pattern.findall(text)
    if len(matches) != 1:
        raise CoherenceTraceError(f"{label} must contain exactly one marked JSON block")
    try:
        value = json.loads(matches[0])
    except json.JSONDecodeError as exc:
        raise CoherenceTraceError(f"{label} JSON is invalid: {exc.msg}") from exc
    if not isinstance(value, dict):
        raise CoherenceTraceError(f"{label} JSON root must be an object")
    return value


def load_coherence(path: Path) -> dict[str, Any]:
    return _extract_json_block(
        path.read_text(encoding="utf-8"),
        COHERENCE_START,
        COHERENCE_END,
        str(path),
    )


def _validate_ids(values: list[str], known_ids: set[str], label: str) -> None:
    for value in values:
        if not DESIGN_ID_RE.fullmatch(value):
            raise CoherenceTraceError(f"{label} has invalid design id: {value}")
        if value not in known_ids:
            raise CoherenceTraceError(f"{label} references unknown design item {value}")


def validate_coherence(
    data: dict[str, Any], *, known_design_ids: set[str], current_design_ids: set[str]
) -> tuple[int, int, int]:
    if data.get("contract") != COHERENCE_CONTRACT:
        raise CoherenceTraceError(f"coherence contract must be {COHERENCE_CONTRACT}")
    route = data.get("route")
    if route not in {"fast", "co-design", "revision"}:
        raise CoherenceTraceError("coherence route must be fast, co-design, or revision")

    anchor_entries = data.get("anchors")
    surface_entries = data.get("surface_checks")
    conflict_entries = data.get("conflicts")
    queue_entries = data.get("impact_queue")
    if not isinstance(anchor_entries, list) or not anchor_entries:
        raise CoherenceTraceError("anchors must be a nonempty list")
    if not isinstance(surface_entries, list) or not surface_entries:
        raise CoherenceTraceError("surface_checks must be a nonempty list")
    if not isinstance(conflict_entries, list):
        raise CoherenceTraceError("conflicts must be a list")
    if not isinstance(queue_entries, list):
        raise CoherenceTraceError("impact_queue must be a list")

    anchors: dict[str, dict[str, Any]] = {}
    for entry in anchor_entries:
        if not isinstance(entry, dict):
            raise CoherenceTraceError("anchor entries must be objects")
        anchor_id = _require_string(entry.get("anchor_id"), "anchor_id")
        if not ANCHOR_ID_RE.fullmatch(anchor_id):
            raise CoherenceTraceError(f"invalid anchor id: {anchor_id}")
        if anchor_id in anchors:
            raise CoherenceTraceError(f"duplicate anchor id: {anchor_id}")
        design_ids = _require_string_list(entry.get("design_ids"), f"{anchor_id}.design_ids")
        if not design_ids:
            raise CoherenceTraceError(f"{anchor_id} must reference at least one design id")
        _validate_ids(design_ids, known_design_ids, anchor_id)
        _require_string(entry.get("statement"), f"{anchor_id}.statement")
        anchors[anchor_id] = entry

    used_anchors: set[str] = set()
    seen_surfaces: set[str] = set()
    has_surface_conflict = False
    for entry in surface_entries:
        if not isinstance(entry, dict):
            raise CoherenceTraceError("surface_checks entries must be objects")
        surface = _require_string(entry.get("surface"), "surface")
        if surface not in SURFACES:
            raise CoherenceTraceError(f"invalid coherence surface: {surface}")
        if surface in seen_surfaces:
            raise CoherenceTraceError(f"duplicate coherence surface: {surface}")
        seen_surfaces.add(surface)
        design_ids = _require_string_list(entry.get("design_ids"), f"{surface}.design_ids")
        if not design_ids:
            raise CoherenceTraceError(f"{surface} must reference at least one design id")
        _validate_ids(design_ids, current_design_ids, surface)
        anchor_ids = _require_string_list(entry.get("anchor_ids"), f"{surface}.anchor_ids")
        if not anchor_ids:
            raise CoherenceTraceError(f"{surface} must reference at least one anchor")
        for anchor_id in anchor_ids:
            if anchor_id not in anchors:
                raise CoherenceTraceError(f"{surface} references unknown anchor {anchor_id}")
        used_anchors.update(anchor_ids)
        _require_string(entry.get("expression"), f"{surface}.expression")
        status = _require_string(entry.get("status"), f"{surface}.status")
        if status not in SURFACE_STATUSES:
            raise CoherenceTraceError(f"{surface} has invalid status: {status}")
        has_surface_conflict = has_surface_conflict or status == "conflict"

    unused_anchors = sorted(set(anchors) - used_anchors)
    if unused_anchors:
        raise CoherenceTraceError(f"anchors are not used by a surface check: {unused_anchors}")
    if has_surface_conflict and not conflict_entries:
        raise CoherenceTraceError("surface status conflict requires a conflicts entry")
    if conflict_entries and not has_surface_conflict:
        raise CoherenceTraceError("conflicts require at least one surface status conflict")
    if conflict_entries:
        raise CoherenceTraceError("conflicts must be empty before SPEC")

    queue_ids: set[str] = set()
    has_change = False
    for entry in queue_entries:
        if not isinstance(entry, dict):
            raise CoherenceTraceError("impact_queue entries must be objects")
        queue_id = _require_string(entry.get("queue_id"), "queue_id")
        if not QUEUE_ID_RE.fullmatch(queue_id):
            raise CoherenceTraceError(f"invalid queue id: {queue_id}")
        if queue_id in queue_ids:
            raise CoherenceTraceError(f"duplicate queue id: {queue_id}")
        queue_ids.add(queue_id)
        source_ids = _require_string_list(
            entry.get("source_design_ids"), f"{queue_id}.source_design_ids"
        )
        if not source_ids:
            raise CoherenceTraceError(f"{queue_id} must reference at least one design id")
        _validate_ids(source_ids, known_design_ids, queue_id)
        target = _require_string(entry.get("target"), f"{queue_id}.target")
        if target not in QUEUE_TARGETS:
            raise CoherenceTraceError(f"{queue_id} has invalid target: {target}")
        action = _require_string(entry.get("action"), f"{queue_id}.action")
        if action not in QUEUE_ACTIONS:
            raise CoherenceTraceError(f"{queue_id} has invalid action: {action}")
        _require_string(entry.get("reason"), f"{queue_id}.reason")
        has_change = has_change or action != "PRESERVE"

    if route == "revision" and (not queue_entries or not has_change):
        raise CoherenceTraceError(
            "revision coherence requires a nonempty impact_queue with an affected target"
        )
    if route != "revision" and queue_entries:
        raise CoherenceTraceError("new fast/co-design work requires an empty impact_queue")
    return len(anchors), len(surface_entries), len(queue_entries)


def validate_file(path: Path) -> tuple[int, int, int]:
    try:
        import design_trace
    except ImportError as exc:
        raise CoherenceTraceError("cannot import adjacent design_trace.py") from exc
    text = path.read_text(encoding="utf-8")
    design = design_trace._extract_json_block(
        text,
        design_trace.DESIGN_START,
        design_trace.DESIGN_END,
        str(path),
    )
    items, gaps = design_trace.validate_design(design)
    if gaps:
        raise CoherenceTraceError("blocking_gaps must be empty before coherence validation")
    coherence = _extract_json_block(text, COHERENCE_START, COHERENCE_END, str(path))
    if coherence.get("route") != design.get("route"):
        raise CoherenceTraceError("coherence route must match the DESIGN scope route")
    current_ids = {
        design_id
        for design_id, item in items.items()
        if item["disposition"] in design_trace.CURRENT_DISPOSITIONS
    }
    return validate_coherence(
        coherence,
        known_design_ids=set(items),
        current_design_ids=current_ids,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate open-mod DESIGN.md theme and presentation coherence."
    )
    parser.add_argument("--design", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        anchors, surfaces, queue = validate_file(args.design)
    except (CoherenceTraceError, OSError, ValueError) as exc:
        print(f"[coherence-trace] failed: {exc}", file=sys.stderr)
        return 2
    print(
        f"[coherence-trace] ok anchors={anchors} surfaces={surfaces} queue={queue}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
