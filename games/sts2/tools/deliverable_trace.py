#!/usr/bin/env python3
"""Validate the literal deliverable contract in DESIGN.md and its PLAN.md settlement.

Two modes, because the contract is checked at two different points:

- ``--design DESIGN.md`` (pre-SPEC): the claim exists, every required experience is
  well-formed and traces to a current design item, and each names how it will be settled.
- ``--design DESIGN.md --plan PLAN.md`` (finalize): every required experience has an
  outcome, and no outcome claims more than its evidence type can carry.

The second mode is the one neither existing validator can do: ``coherence_trace.py`` and
``design_trace.py`` both run before SPEC, so nothing today compares what was promised
against what the run actually earned.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


DELIVERABLE_CONTRACT = "open-mod-deliverable/v1"
DELIVERABLE_START = "<!-- open-mod-deliverable:v1:start -->"
DELIVERABLE_END = "<!-- open-mod-deliverable:v1:end -->"
SETTLEMENT_CONTRACT = "open-mod-settlement/v1"
SETTLEMENT_START = "<!-- open-mod-settlement:v1:start -->"
SETTLEMENT_END = "<!-- open-mod-settlement:v1:end -->"
EXPERIENCE_ID_RE = re.compile(r"^E-[0-9]{3}$")
DESIGN_ID_RE = re.compile(r"^D-[0-9]{3}$")
ROUTES = {"fast", "co-design", "revision"}

# How a required experience becomes settled. `user-decision` is deliberately not
# evidence of observation: it records that the user accepted a stated difference,
# which is where an accepted PLACEHOLDER lands (INV-5).
SETTLED_BY = {
    "tier-2-structured",
    "tier-1-load",
    "headed-human",
    "user-decision",
}
OUTCOMES = {"observed", "unobserved", "exception"}

# What each settlement method may report as `observed`. A method whose evidence
# requires a human or a harness cannot reach `observed` through any other route,
# which is the machine-checkable half of INV-1 and INV-4.
OBSERVED_EVIDENCE = {
    "tier-2-structured": {"tier-2-structured"},
    "tier-1-load": {"tier-1-load", "tier-2-structured"},
    "headed-human": {"headed-human"},
    "user-decision": {"user-decision"},
}


class DeliverableTraceError(ValueError):
    """Raised when the deliverable claim or its settlement is malformed."""


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise DeliverableTraceError(f"{label} must be a nonempty string")
    return value.strip()


def _require_string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list):
        raise DeliverableTraceError(f"{label} must be a list")
    result = [
        _require_string(entry, f"{label}[{index}]") for index, entry in enumerate(value)
    ]
    if len(result) != len(set(result)):
        raise DeliverableTraceError(f"{label} contains duplicates")
    return result


def _extract_json_block(text: str, start: str, end: str, label: str) -> dict[str, Any]:
    pattern = re.compile(
        rf"{re.escape(start)}\s*```json\s*(.*?)\s*```\s*{re.escape(end)}",
        re.DOTALL,
    )
    matches = pattern.findall(text)
    if len(matches) != 1:
        raise DeliverableTraceError(f"{label} must contain exactly one marked JSON block")
    try:
        value = json.loads(matches[0])
    except json.JSONDecodeError as exc:
        raise DeliverableTraceError(f"{label} JSON is invalid: {exc.msg}") from exc
    if not isinstance(value, dict):
        raise DeliverableTraceError(f"{label} JSON root must be an object")
    return value


def has_deliverable_block(text: str) -> bool:
    """Whether this DESIGN carries a claim at all.

    An absent block means the project predates M8.1 and resumes unchanged, the same
    way an absent coherence block signals a pre-M7.5 project. This is exactly why the
    claim is its own marked block: `absent` is unambiguous, where a missing key inside
    the scope block could not be told apart from an author who forgot it.
    """
    return DELIVERABLE_START in text and DELIVERABLE_END in text


def load_deliverable(path: Path) -> dict[str, Any]:
    return _extract_json_block(
        path.read_text(encoding="utf-8"),
        DELIVERABLE_START,
        DELIVERABLE_END,
        str(path),
    )


def load_settlement(path: Path) -> dict[str, Any]:
    return _extract_json_block(
        path.read_text(encoding="utf-8"),
        SETTLEMENT_START,
        SETTLEMENT_END,
        str(path),
    )


def _validate_experience(
    entry: Any, *, current_design_ids: set[str] | None
) -> dict[str, Any]:
    if not isinstance(entry, dict):
        raise DeliverableTraceError("required_experiences entries must be objects")
    experience_id = _require_string(entry.get("experience_id"), "experience_id")
    if not EXPERIENCE_ID_RE.fullmatch(experience_id):
        raise DeliverableTraceError(f"invalid experience id: {experience_id}")
    _require_string(entry.get("statement"), f"{experience_id}.statement")
    design_ids = _require_string_list(
        entry.get("design_ids"), f"{experience_id}.design_ids"
    )
    if not design_ids:
        raise DeliverableTraceError(
            f"{experience_id} must reference at least one design id"
        )
    for design_id in design_ids:
        if not DESIGN_ID_RE.fullmatch(design_id):
            raise DeliverableTraceError(
                f"{experience_id} has invalid design id: {design_id}"
            )
        if current_design_ids is not None and design_id not in current_design_ids:
            raise DeliverableTraceError(
                f"{experience_id} references non-current design item {design_id}"
            )
    settled_by = _require_string(entry.get("settled_by"), f"{experience_id}.settled_by")
    if settled_by not in SETTLED_BY:
        expected = ", ".join(sorted(SETTLED_BY))
        raise DeliverableTraceError(
            f"{experience_id} has invalid settled_by {settled_by!r}; expected one of {expected}"
        )
    return entry


def validate_deliverable(
    data: dict[str, Any], *, current_design_ids: set[str] | None = None
) -> tuple[int, int]:
    """Check the claim itself. `shape` is presence-only, never an enum.

    prototype / slice / run-capable are optional descriptions, so the validator must
    not decide which words are allowed here — only that the author said something.
    """
    if data.get("contract") != DELIVERABLE_CONTRACT:
        raise DeliverableTraceError(
            f"deliverable contract must be {DELIVERABLE_CONTRACT}"
        )
    if data.get("route") not in ROUTES:
        raise DeliverableTraceError(
            "deliverable route must be fast, co-design, or revision"
        )
    _require_string(data.get("claim"), "claim")
    _require_string(data.get("shape"), "shape")

    entries = data.get("required_experiences")
    if not isinstance(entries, list) or not entries:
        raise DeliverableTraceError("required_experiences must be a nonempty list")
    excluded = data.get("excluded_experiences")
    if not isinstance(excluded, list):
        raise DeliverableTraceError("excluded_experiences must be a list")
    for index, item in enumerate(excluded):
        _require_string(item, f"excluded_experiences[{index}]")

    experiences: dict[str, dict[str, Any]] = {}
    for entry in entries:
        experience = _validate_experience(entry, current_design_ids=current_design_ids)
        experience_id = experience["experience_id"]
        if experience_id in experiences:
            raise DeliverableTraceError(f"duplicate experience id: {experience_id}")
        experiences[experience_id] = experience
    return len(experiences), len(excluded)


def validate_settlement(
    data: dict[str, Any], *, experiences: dict[str, dict[str, Any]]
) -> tuple[int, int]:
    """Check the finalize ledger against the claim it settles."""
    if data.get("contract") != SETTLEMENT_CONTRACT:
        raise DeliverableTraceError(
            f"settlement contract must be {SETTLEMENT_CONTRACT}"
        )
    entries = data.get("settlements")
    if not isinstance(entries, list) or not entries:
        raise DeliverableTraceError("settlements must be a nonempty list")

    seen: dict[str, str] = {}
    observed = 0
    for entry in entries:
        if not isinstance(entry, dict):
            raise DeliverableTraceError("settlement entries must be objects")
        experience_id = _require_string(entry.get("experience_id"), "experience_id")
        if not EXPERIENCE_ID_RE.fullmatch(experience_id):
            raise DeliverableTraceError(f"invalid experience id: {experience_id}")
        if experience_id in seen:
            raise DeliverableTraceError(f"duplicate settlement for {experience_id}")
        if experience_id not in experiences:
            raise DeliverableTraceError(
                f"{experience_id} is settled but not required by the claim"
            )
        outcome = _require_string(entry.get("outcome"), f"{experience_id}.outcome")
        if outcome not in OUTCOMES:
            expected = ", ".join(sorted(OUTCOMES))
            raise DeliverableTraceError(
                f"{experience_id} has invalid outcome {outcome!r}; expected one of {expected}"
            )
        evidence = _require_string(entry.get("evidence"), f"{experience_id}.evidence")
        note = entry.get("note")
        if note is not None:
            _require_string(note, f"{experience_id}.note")

        settled_by = experiences[experience_id]["settled_by"]
        if outcome == "observed":
            allowed = OBSERVED_EVIDENCE[settled_by]
            evidence_kind = _require_string(
                entry.get("evidence_kind"), f"{experience_id}.evidence_kind"
            )
            if evidence_kind not in SETTLED_BY:
                raise DeliverableTraceError(
                    f"{experience_id} has invalid evidence_kind: {evidence_kind}"
                )
            if evidence_kind not in allowed:
                raise DeliverableTraceError(
                    f"{experience_id} claims observed on {evidence_kind} evidence, but "
                    f"settled_by={settled_by} requires one of {', '.join(sorted(allowed))}"
                )
            observed += 1
        else:
            # An outcome short of `observed` must say what is missing, so an
            # exception can never read as a quiet pass (INV-1).
            _require_string(note, f"{experience_id}.note")
        seen[experience_id] = outcome

    missing = sorted(set(experiences) - set(seen))
    if missing:
        raise DeliverableTraceError(
            "required experiences have no settlement: " + ", ".join(missing)
        )
    return len(seen), observed


def _current_design_ids(design_text: str, label: str) -> set[str]:
    """Current design ids from the scope block, for the experience trace.

    Read through `design_trace` rather than re-parsing the scope block, so the two
    validators cannot disagree about what `current` means.
    """
    try:
        import design_trace
    except ImportError as exc:  # pragma: no cover - packaging guard
        raise DeliverableTraceError("cannot import adjacent design_trace.py") from exc
    scope = design_trace._extract_json_block(
        design_text,
        design_trace.DESIGN_START,
        design_trace.DESIGN_END,
        label,
    )
    try:
        items, gaps = design_trace.validate_design(scope)
    except design_trace.DesignTraceError as exc:
        raise DeliverableTraceError(f"design scope is invalid: {exc}") from exc
    if gaps:
        raise DeliverableTraceError(
            "blocking_gaps must be empty before the deliverable claim is validated"
        )
    return {
        design_id
        for design_id, item in items.items()
        if item["disposition"] in design_trace.CURRENT_DISPOSITIONS
    }


def validate_design_file(path: Path) -> tuple[int, int]:
    text = path.read_text(encoding="utf-8")
    data = _extract_json_block(text, DELIVERABLE_START, DELIVERABLE_END, str(path))
    current_ids = _current_design_ids(text, str(path))
    scope = _extract_json_block(
        text,
        "<!-- open-mod-scope:v1:start -->",
        "<!-- open-mod-scope:v1:end -->",
        str(path),
    )
    if data.get("route") != scope.get("route"):
        raise DeliverableTraceError(
            "deliverable route must match the DESIGN scope route"
        )
    return validate_deliverable(data, current_design_ids=current_ids)


def validate_finalize(design_path: Path, plan_path: Path) -> tuple[int, int]:
    design_text = design_path.read_text(encoding="utf-8")
    data = _extract_json_block(
        design_text, DELIVERABLE_START, DELIVERABLE_END, str(design_path)
    )
    current_ids = _current_design_ids(design_text, str(design_path))
    validate_deliverable(data, current_design_ids=current_ids)
    experiences = {
        entry["experience_id"]: entry for entry in data["required_experiences"]
    }
    settlement = load_settlement(plan_path)
    return validate_settlement(settlement, experiences=experiences)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate the open-mod literal deliverable claim and its settlement."
    )
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument(
        "--plan",
        type=Path,
        help="PLAN.md holding the settlement ledger; enables the finalize check.",
    )
    args = parser.parse_args(argv)
    try:
        if args.plan is None:
            experiences, excluded = validate_design_file(args.design)
            print(
                f"[deliverable-trace] ok experiences={experiences} excluded={excluded}"
            )
        else:
            settled, observed = validate_finalize(args.design, args.plan)
            print(
                f"[deliverable-trace] ok settled={settled} observed={observed} "
                f"unobserved_or_exception={settled - observed}"
            )
    except (DeliverableTraceError, OSError, ValueError) as exc:
        print(f"[deliverable-trace] failed: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
