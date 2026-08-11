#!/usr/bin/env python3
"""Validate active semantic-repair routing in PLAN.md."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


REPAIR_CONTRACT = "open-mod-repair-routing/v1"
REPAIR_START = "<!-- open-mod-repair-routing:v1:start -->"
REPAIR_END = "<!-- open-mod-repair-routing:v1:end -->"

CLASS_OWNERS = {
    "implementation-equivalent": "MEMORY.md",
    "contract-fulfillment": "SPEC.md",
    "accepted-semantic-change": "DESIGN.md",
    "missing-capability": "shared recipe/reference",
}
CLASS_STATUSES = {
    "implementation-equivalent": {"repairing", "blocked"},
    "contract-fulfillment": {"repairing", "blocked"},
    "accepted-semantic-change": {
        "awaiting-user-acceptance",
        "revision-accepted",
        "blocked",
    },
    "missing-capability": {"blocked-upstream"},
}
TRIGGER_STAGES = {
    "author",
    "build",
    "verify-tier-1",
    "verify-tier-2",
    "verify-headed",
    "repair",
    "finalize",
}
STAGE_ORDER = (
    "design",
    "spec",
    "scaffold",
    "author",
    "art",
    "build",
    "verify-tier-1",
    "verify-tier-2",
    "verify-headed",
    "finalize",
)
ACTIVE_FIELDS = {
    "trigger_stage",
    "observed_difference",
    "classification",
    "owning_artifact",
    "affected_design_ids",
    "affected_experience_ids",
    "affected_operation_ids",
    "invalidated_stages",
    "reopened_stage",
    "routing_status",
}


class RepairTraceError(ValueError):
    """Raised when PLAN repair state contradicts DESIGN, SPEC, or settlement state."""


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RepairTraceError(f"{label} must be a nonempty string")
    return value.strip()


def _require_string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list):
        raise RepairTraceError(f"{label} must be a list")
    result = [
        _require_string(entry, f"{label}[{index}]")
        for index, entry in enumerate(value)
    ]
    if len(result) != len(set(result)):
        raise RepairTraceError(f"{label} contains duplicates")
    return result


def has_repair_block(text: str) -> bool:
    return REPAIR_START in text or REPAIR_END in text


def load_repair(path: Path) -> dict[str, Any] | None:
    text = path.read_text(encoding="utf-8")
    if not has_repair_block(text):
        return None
    pattern = re.compile(
        rf"{re.escape(REPAIR_START)}\s*```json\s*(.*?)\s*```\s*{re.escape(REPAIR_END)}",
        re.DOTALL,
    )
    matches = pattern.findall(text)
    if len(matches) != 1:
        raise RepairTraceError("PLAN.md must contain exactly one marked repair-routing block")
    try:
        data = json.loads(matches[0])
    except json.JSONDecodeError as exc:
        raise RepairTraceError(f"repair-routing JSON is invalid: {exc.msg}") from exc
    if not isinstance(data, dict):
        raise RepairTraceError("repair-routing JSON root must be an object")
    return data


def _load_artifacts(
    design_path: Path, spec_path: Path, *, allow_blocking_gaps: bool
) -> tuple[
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
    list[str],
]:
    try:
        import deliverable_trace
        import design_trace
    except ImportError as exc:  # pragma: no cover - packaging guard
        raise RepairTraceError("cannot import adjacent trace validators") from exc

    try:
        design = design_trace.load_design(design_path)
        spec = design_trace.load_spec(spec_path)
        design_items, gaps = design_trace.validate_design(design)
        operations = design_trace.validate_spec(spec)
        pair_design = dict(design)
        pair_design["blocking_gaps"] = []
        design_trace.validate_pair(pair_design, spec)
    except (design_trace.DesignTraceError, OSError) as exc:
        raise RepairTraceError(f"DESIGN/SPEC trace is invalid: {exc}") from exc
    if gaps and not allow_blocking_gaps:
        raise RepairTraceError("active repair cannot bypass DESIGN blocking_gaps")

    current = {
        design_id: item
        for design_id, item in design_items.items()
        if item["disposition"] in design_trace.CURRENT_DISPOSITIONS
    }
    experiences: dict[str, dict[str, Any]] = {}
    design_text = design_path.read_text(encoding="utf-8")
    if deliverable_trace.has_deliverable_block(design_text):
        try:
            deliverable = deliverable_trace.load_deliverable(design_path)
            deliverable_trace.validate_deliverable(
                deliverable, current_design_ids=set(current)
            )
        except (deliverable_trace.DeliverableTraceError, OSError) as exc:
            raise RepairTraceError(f"DESIGN deliverable is invalid: {exc}") from exc
        experiences = {
            entry["experience_id"]: entry
            for entry in deliverable["required_experiences"]
        }
    return current, operations, experiences, gaps


def _settled_ids(plan_path: Path) -> set[str]:
    try:
        import deliverable_trace
    except ImportError as exc:  # pragma: no cover - packaging guard
        raise RepairTraceError("cannot import adjacent deliverable_trace.py") from exc
    text = plan_path.read_text(encoding="utf-8")
    if deliverable_trace.SETTLEMENT_START not in text:
        return set()
    try:
        settlement = deliverable_trace.load_settlement(plan_path)
    except (deliverable_trace.DeliverableTraceError, OSError) as exc:
        raise RepairTraceError(f"PLAN settlement is invalid: {exc}") from exc
    if settlement.get("contract") != deliverable_trace.SETTLEMENT_CONTRACT:
        raise RepairTraceError(
            f"settlement contract must be {deliverable_trace.SETTLEMENT_CONTRACT}"
        )
    entries = settlement.get("settlements")
    if not isinstance(entries, list):
        raise RepairTraceError("settlements must be a list")
    settled: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise RepairTraceError("settlement entries must be objects")
        experience_id = _require_string(entry.get("experience_id"), "experience_id")
        if experience_id in settled:
            raise RepairTraceError(f"duplicate settlement for {experience_id}")
        settled.add(experience_id)
    return settled


def validate_active_repair(
    active: Any,
    *,
    current_design: dict[str, dict[str, Any]],
    operations: dict[str, dict[str, Any]],
    experiences: dict[str, dict[str, Any]],
    settled_ids: set[str],
) -> str:
    if not isinstance(active, dict):
        raise RepairTraceError("active_repair must be null or an object")
    unknown = set(active) - ACTIVE_FIELDS
    missing = ACTIVE_FIELDS - set(active)
    if unknown or missing:
        raise RepairTraceError(
            f"active_repair fields mismatch; missing={sorted(missing)} unknown={sorted(unknown)}"
        )

    trigger = _require_string(active["trigger_stage"], "trigger_stage")
    if trigger not in TRIGGER_STAGES:
        raise RepairTraceError(f"invalid trigger_stage: {trigger}")
    _require_string(active["observed_difference"], "observed_difference")
    classification = _require_string(active["classification"], "classification")
    if classification not in CLASS_OWNERS:
        raise RepairTraceError(f"invalid repair classification: {classification}")
    owner = _require_string(active["owning_artifact"], "owning_artifact")
    if owner != CLASS_OWNERS[classification]:
        raise RepairTraceError(
            f"{classification} must be owned by {CLASS_OWNERS[classification]}"
        )
    status = _require_string(active["routing_status"], "routing_status")
    if status not in CLASS_STATUSES[classification]:
        raise RepairTraceError(
            f"{classification} cannot use routing_status={status!r}"
        )

    design_ids = _require_string_list(
        active["affected_design_ids"], "affected_design_ids"
    )
    experience_ids = _require_string_list(
        active["affected_experience_ids"], "affected_experience_ids"
    )
    operation_ids = _require_string_list(
        active["affected_operation_ids"], "affected_operation_ids"
    )
    if not design_ids or not operation_ids:
        raise RepairTraceError(
            "active repair must name affected_design_ids and affected_operation_ids"
        )
    unknown_design = sorted(set(design_ids) - set(current_design))
    unknown_operations = sorted(set(operation_ids) - set(operations))
    unknown_experiences = sorted(set(experience_ids) - set(experiences))
    if unknown_design:
        raise RepairTraceError(f"affected design ids are not current: {unknown_design}")
    if unknown_operations:
        raise RepairTraceError(f"affected operation ids are unknown: {unknown_operations}")
    if unknown_experiences:
        raise RepairTraceError(f"affected experience ids are unknown: {unknown_experiences}")
    if classification == "implementation-equivalent" and experience_ids:
        raise RepairTraceError(
            "implementation-equivalent cannot invalidate player experiences"
        )

    design_id_set = set(design_ids)
    for operation_id in operation_ids:
        linked = set(operations[operation_id]["design_ids"])
        if not linked & design_id_set:
            raise RepairTraceError(
                f"{operation_id} does not trace to an affected design id"
            )
    for experience_id in experience_ids:
        linked = set(experiences[experience_id]["design_ids"])
        if not linked & design_id_set:
            raise RepairTraceError(
                f"{experience_id} does not trace to an affected design id"
            )
    stale = sorted(set(experience_ids) & settled_ids)
    if stale:
        raise RepairTraceError(
            "affected experience settlements must be cleared: " + ", ".join(stale)
        )

    invalidated = _require_string_list(
        active["invalidated_stages"], "invalidated_stages"
    )
    unknown_stages = sorted(set(invalidated) - set(STAGE_ORDER))
    if unknown_stages:
        raise RepairTraceError(f"invalid invalidated_stages: {unknown_stages}")
    expected_order = sorted(invalidated, key=STAGE_ORDER.index)
    if invalidated != expected_order:
        raise RepairTraceError("invalidated_stages must be in pipeline order")
    if (
        experience_ids
        and classification != "missing-capability"
        and "finalize" not in invalidated
    ):
        raise RepairTraceError(
            "an affected experience must invalidate finalize for fresh settlement"
        )
    reopened = active["reopened_stage"]

    if classification == "missing-capability":
        if invalidated or reopened is not None:
            raise RepairTraceError(
                "missing-capability blocks upstream and cannot reopen a consumer stage"
            )
    else:
        if not invalidated:
            raise RepairTraceError(f"{classification} must invalidate at least one stage")
        reopened = _require_string(reopened, "reopened_stage")
        if reopened != invalidated[0]:
            raise RepairTraceError(
                "reopened_stage must be the earliest invalidated stage"
            )
        if classification == "implementation-equivalent" and reopened in {"design", "spec"}:
            raise RepairTraceError(
                "implementation-equivalent cannot reopen DESIGN or SPEC"
            )
        if classification == "contract-fulfillment" and reopened == "design":
            raise RepairTraceError("contract-fulfillment cannot reopen DESIGN")
        if classification == "accepted-semantic-change" and reopened != "design":
            raise RepairTraceError(
                "accepted-semantic-change must reopen DESIGN first"
            )
    return classification


def validate_files(
    plan_path: Path,
    *,
    design_path: Path | None = None,
    spec_path: Path | None = None,
    require_clear: bool = False,
) -> tuple[str, str | None]:
    data = load_repair(plan_path)
    if data is None:
        return "legacy", None
    if set(data) != {"contract", "active_repair"}:
        raise RepairTraceError(
            "repair-routing root must contain only contract and active_repair"
        )
    if data.get("contract") != REPAIR_CONTRACT:
        raise RepairTraceError(f"repair contract must be {REPAIR_CONTRACT}")
    active = data.get("active_repair")
    if active is None:
        return "clear", None
    if require_clear:
        raise RepairTraceError("Finalize is blocked while active_repair is not null")
    if design_path is None or spec_path is None:
        raise RepairTraceError("active repair validation requires --design and --spec")
    current, operations, experiences, gaps = _load_artifacts(
        design_path,
        spec_path,
        allow_blocking_gaps=(
            active.get("classification")
            in {"accepted-semantic-change", "missing-capability"}
        )
        if isinstance(active, dict)
        else False,
    )
    classification = validate_active_repair(
        active,
        current_design=current,
        operations=operations,
        experiences=experiences,
        settled_ids=_settled_ids(plan_path),
    )
    if classification == "missing-capability" and not gaps:
        raise RepairTraceError(
            "missing-capability requires the exact project gap in DESIGN blocking_gaps"
        )
    if (
        classification == "accepted-semantic-change"
        and active.get("routing_status") == "revision-accepted"
        and gaps
    ):
        raise RepairTraceError(
            "revision-accepted cannot retain unresolved DESIGN blocking_gaps"
        )
    return "active", classification


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate open-mod semantic repair routing state."
    )
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--design", type=Path)
    parser.add_argument("--spec", type=Path)
    parser.add_argument(
        "--finalize",
        action="store_true",
        help="require active_repair to be clear before final reporting",
    )
    args = parser.parse_args(argv)
    try:
        state, classification = validate_files(
            args.plan,
            design_path=args.design,
            spec_path=args.spec,
            require_clear=args.finalize,
        )
    except (RepairTraceError, OSError, ValueError) as exc:
        print(f"[repair-trace] failed: {exc}", file=sys.stderr)
        return 2
    suffix = f" classification={classification}" if classification else ""
    print(f"[repair-trace] ok state={state}{suffix}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
