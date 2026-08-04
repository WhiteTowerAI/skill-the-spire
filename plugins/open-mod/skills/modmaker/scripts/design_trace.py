#!/usr/bin/env python3
"""Validate M7.4 DESIGN.md scope against SPEC.md operation traceability."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


DESIGN_CONTRACT = "open-mod-design/v1"
SPEC_TRACE_CONTRACT = "open-mod-spec-trace/v1"
DESIGN_START = "<!-- open-mod-scope:v1:start -->"
DESIGN_END = "<!-- open-mod-scope:v1:end -->"
SPEC_START = "<!-- open-mod-trace:v1:start -->"
SPEC_END = "<!-- open-mod-trace:v1:end -->"
CURRENT_DISPOSITIONS = {"MUST", "PLACEHOLDER"}
FUTURE_DISPOSITIONS = {"DEFER", "OUT-OF-SCOPE"}
ROUTES = {"fast", "co-design", "revision"}
DESIGN_ID_RE = re.compile(r"^D-[0-9]{3}$")
OPERATION_ID_RE = re.compile(r"^OP-[0-9]{3}$")
SUPPORTED_ROUTE_RE = re.compile(
    r"^(?:recipes|reference)/[a-z0-9][a-z0-9_./-]*\.md(?:#[a-z0-9_-]+)?$"
)


class DesignTraceError(ValueError):
    """Raised when design scope and SPEC trace do not form one closed contract."""


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise DesignTraceError(f"{label} must be a nonempty string")
    return value.strip()


def _require_string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list):
        raise DesignTraceError(f"{label} must be a list")
    result: list[str] = []
    for index, entry in enumerate(value):
        result.append(_require_string(entry, f"{label}[{index}]"))
    if len(result) != len(set(result)):
        raise DesignTraceError(f"{label} contains duplicates")
    return result


def _extract_json_block(text: str, start: str, end: str, label: str) -> dict[str, Any]:
    pattern = re.compile(
        rf"{re.escape(start)}\s*```json\s*(.*?)\s*```\s*{re.escape(end)}",
        re.DOTALL,
    )
    matches = pattern.findall(text)
    if len(matches) != 1:
        raise DesignTraceError(f"{label} must contain exactly one marked JSON block")
    try:
        value = json.loads(matches[0])
    except json.JSONDecodeError as exc:
        raise DesignTraceError(f"{label} JSON is invalid: {exc.msg}") from exc
    if not isinstance(value, dict):
        raise DesignTraceError(f"{label} JSON root must be an object")
    return value


def load_design(path: Path) -> dict[str, Any]:
    return _extract_json_block(
        path.read_text(encoding="utf-8"), DESIGN_START, DESIGN_END, str(path)
    )


def load_spec(path: Path) -> dict[str, Any]:
    return _extract_json_block(
        path.read_text(encoding="utf-8"), SPEC_START, SPEC_END, str(path)
    )


def _validate_design_item(
    item: Any, *, section: str, expected_dispositions: set[str]
) -> dict[str, Any]:
    if not isinstance(item, dict):
        raise DesignTraceError(f"{section} entries must be objects")
    design_id = _require_string(item.get("design_id"), f"{section}.design_id")
    if not DESIGN_ID_RE.fullmatch(design_id):
        raise DesignTraceError(f"invalid design id: {design_id}")
    disposition = _require_string(
        item.get("disposition"), f"{design_id}.disposition"
    )
    if disposition not in expected_dispositions:
        expected = ", ".join(sorted(expected_dispositions))
        raise DesignTraceError(
            f"{design_id} disposition {disposition!r} is invalid for {section}; expected {expected}"
        )
    _require_string(item.get("summary"), f"{design_id}.summary")
    support = _require_string(item.get("support"), f"{design_id}.support")
    operations = _require_string_list(
        item.get("spec_operations"), f"{design_id}.spec_operations"
    )
    _require_string(item.get("reason"), f"{design_id}.reason")

    for operation_id in operations:
        if not OPERATION_ID_RE.fullmatch(operation_id):
            raise DesignTraceError(
                f"{design_id} has invalid operation id: {operation_id}"
            )

    if section == "current_slice":
        expected_support = (
            "confirmed" if disposition == "MUST" else "placeholder-fallback"
        )
        if support != expected_support:
            raise DesignTraceError(
                f"{design_id} {disposition} requires support={expected_support}"
            )
        if not operations:
            raise DesignTraceError(
                f"{design_id} current item must map to at least one SPEC operation"
            )
    else:
        if support != "not-current":
            raise DesignTraceError(
                f"{design_id} future item requires support=not-current"
            )
        if operations:
            raise DesignTraceError(
                f"{design_id} future item cannot map to a SPEC operation"
            )
    return item


def validate_design(data: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], list[str]]:
    if data.get("contract") != DESIGN_CONTRACT:
        raise DesignTraceError(f"design contract must be {DESIGN_CONTRACT}")
    if data.get("route") not in ROUTES:
        raise DesignTraceError("design route must be fast, co-design, or revision")

    current = data.get("current_slice")
    future = data.get("future_vision")
    if not isinstance(current, list) or not current:
        raise DesignTraceError("current_slice must be a nonempty list")
    if not isinstance(future, list):
        raise DesignTraceError("future_vision must be a list")
    gaps = _require_string_list(data.get("blocking_gaps"), "blocking_gaps")

    items: dict[str, dict[str, Any]] = {}
    for section, entries, dispositions in (
        ("current_slice", current, CURRENT_DISPOSITIONS),
        ("future_vision", future, FUTURE_DISPOSITIONS),
    ):
        for entry in entries:
            item = _validate_design_item(
                entry, section=section, expected_dispositions=dispositions
            )
            design_id = item["design_id"]
            if design_id in items:
                raise DesignTraceError(f"duplicate design id: {design_id}")
            items[design_id] = item
    return items, gaps


def validate_spec(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    if data.get("contract") != SPEC_TRACE_CONTRACT:
        raise DesignTraceError(f"SPEC trace contract must be {SPEC_TRACE_CONTRACT}")
    if data.get("design_contract") != DESIGN_CONTRACT:
        raise DesignTraceError(f"SPEC design_contract must be {DESIGN_CONTRACT}")
    entries = data.get("operations")
    if not isinstance(entries, list) or not entries:
        raise DesignTraceError("SPEC trace operations must be a nonempty list")

    operations: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise DesignTraceError("SPEC operation entries must be objects")
        operation_id = _require_string(entry.get("operation_id"), "operation_id")
        if not OPERATION_ID_RE.fullmatch(operation_id):
            raise DesignTraceError(f"invalid SPEC operation id: {operation_id}")
        if operation_id in operations:
            raise DesignTraceError(f"duplicate SPEC operation id: {operation_id}")
        _require_string_list(entry.get("design_ids"), f"{operation_id}.design_ids")
        if not entry["design_ids"]:
            raise DesignTraceError(
                f"{operation_id} must reference at least one design id"
            )
        _require_string(entry.get("semantic_target"), f"{operation_id}.semantic_target")
        supported_route = _require_string(
            entry.get("supported_route"), f"{operation_id}.supported_route"
        )
        if not SUPPORTED_ROUTE_RE.fullmatch(supported_route):
            raise DesignTraceError(
                f"{operation_id} has invalid supported route: {supported_route}"
            )
        operations[operation_id] = entry
    return operations


def validate_pair(design: dict[str, Any], spec: dict[str, Any]) -> tuple[int, int]:
    design_items, gaps = validate_design(design)
    if gaps:
        raise DesignTraceError(
            "blocking_gaps must be empty before SPEC: " + "; ".join(gaps)
        )
    operations = validate_spec(spec)
    current = {
        design_id: item
        for design_id, item in design_items.items()
        if item["disposition"] in CURRENT_DISPOSITIONS
    }
    expected_operations = {
        operation_id
        for item in current.values()
        for operation_id in item["spec_operations"]
    }
    actual_operations = set(operations)
    if expected_operations != actual_operations:
        missing = sorted(expected_operations - actual_operations)
        extra = sorted(actual_operations - expected_operations)
        raise DesignTraceError(
            f"DESIGN/SPEC operation mismatch; missing={missing}, extra={extra}"
        )

    for operation_id, operation in operations.items():
        linked_ids = set(operation["design_ids"])
        for design_id in linked_ids:
            if design_id not in current:
                raise DesignTraceError(
                    f"{operation_id} references non-current design item {design_id}"
                )
            if operation_id not in current[design_id]["spec_operations"]:
                raise DesignTraceError(
                    f"{operation_id} is not listed by design item {design_id}"
                )

    for design_id, item in current.items():
        for operation_id in item["spec_operations"]:
            if design_id not in operations[operation_id]["design_ids"]:
                raise DesignTraceError(
                    f"{design_id} is not referenced back by {operation_id}"
                )
    return len(design_items), len(operations)


def validate_files(design_path: Path, spec_path: Path) -> tuple[int, int]:
    design = load_design(design_path)
    spec = load_spec(spec_path)
    result = validate_pair(design, spec)
    tool_path = Path(__file__).resolve()
    candidates = (
        tool_path.parent.parent / "skills" / "sts2-api",
        tool_path.parents[2] / "sts2-api",
    )
    route_root = next((candidate for candidate in candidates if candidate.is_dir()), None)
    if route_root is None:
        raise DesignTraceError("cannot locate the shipped sts2-api route root")
    for operation in spec["operations"]:
        route_path = operation["supported_route"].split("#", 1)[0]
        if not (route_root / route_path).is_file():
            raise DesignTraceError(
                f"{operation['operation_id']} supported route does not exist: {route_path}"
            )
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate open-mod DESIGN.md to SPEC.md traceability."
    )
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--spec", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        design_items, operations = validate_files(args.design, args.spec)
    except (DesignTraceError, OSError) as exc:
        print(f"[design-trace] failed: {exc}", file=sys.stderr)
        return 2
    print(f"[design-trace] ok design_items={design_items} operations={operations}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
