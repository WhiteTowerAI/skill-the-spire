#!/usr/bin/env python3
"""Validate v3 surface data against shipped product-owned surface contracts.

The owner pages define the accepted vocabulary in parseable `open-mod-surface-contract/v1`
JSON blocks. A v3 SPEC carries one `open-mod-surface-data/v1` JSON block. This dispatcher
checks cardinality, allowlisted enums, route declarations, and obvious cross-field
contradictions. It does not prove generated C#, lifecycle behavior, presentation, or game
results.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import deque
from pathlib import Path
from typing import Any


CONTRACT_ID = "sts2-content-semantic/v3"
OWNER_BLOCK_RE = re.compile(
    r"<!--\s*open-mod-surface-contract/v1\s*\n(?P<body>\{.*?\})\s*-->",
    re.DOTALL,
)
DATA_BLOCK_RE = re.compile(
    r"<!--\s*open-mod-surface-data/v1\s*\n(?P<body>\{.*?\})\s*-->",
    re.DOTALL,
)
OWNER_DIRS = (
    Path("skills") / "modmaker" / "surfaces",
    Path("skills") / "sts2-api" / "reference",
)


class SurfaceContractError(ValueError):
    """Raised when a surface contract or v3 data declaration is invalid."""


def _tool_dir() -> Path:
    return Path(__file__).resolve().parent


def skill_root() -> Path:
    """Resolve `skills/` from the repository or published payload tool layout."""
    here = _tool_dir()
    candidates = (here.parent / "skills", here.parents[1])
    for candidate in candidates:
        if (candidate / "modmaker" / "surfaces").is_dir():
            return candidate
    raise SurfaceContractError("cannot locate shipped skills root")


def _json_object(raw: str, label: str) -> dict[str, Any]:
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SurfaceContractError(f"{label} is not valid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise SurfaceContractError(f"{label} must be a JSON object")
    return value


def _heading_slugs(text: str) -> set[str]:
    slugs: set[str] = set()
    for heading in re.findall(r"^#+\s+(.*?)\s*$", text, re.MULTILINE):
        slug = re.sub(r"[^a-z0-9\s-]", "", heading.lower()).strip()
        slugs.add(re.sub(r"\s", "-", slug))
    return slugs


def _validate_contract_routes(contract: dict[str, Any], family: str) -> None:
    route_root = skill_root() / "sts2-api"
    routes = contract.get("routes")
    if not isinstance(routes, list) or not routes:
        raise SurfaceContractError(f"surface contract {family!r} requires routes")
    for index, raw in enumerate(routes):
        route = _text(raw, f"surface contract {family}.routes[{index}]")
        route_path, separator, anchor = route.partition("#")
        route_file = route_root / route_path
        if not route_file.is_file():
            raise SurfaceContractError(
                f"surface contract {family!r} route does not exist: {route_path}"
            )
        if separator and anchor not in _heading_slugs(route_file.read_text(encoding="utf-8")):
            raise SurfaceContractError(
                f"surface contract {family!r} route anchor does not exist: {route}"
            )


def load_surface_contracts() -> dict[str, dict[str, Any]]:
    root = skill_root()
    contracts: dict[str, dict[str, Any]] = {}
    for relative in OWNER_DIRS:
        directory = root / relative.relative_to("skills")
        for page in sorted(directory.glob("*.md")):
            text = page.read_text(encoding="utf-8")
            matches = list(OWNER_BLOCK_RE.finditer(text))
            if len(matches) > 1:
                raise SurfaceContractError(f"{page.name} has more than one surface contract block")
            if not matches:
                continue
            contract = _json_object(matches[0].group("body"), f"{page.name} surface contract")
            family = contract.get("family")
            if not isinstance(family, str) or not family:
                raise SurfaceContractError(f"{page.name} surface contract has no family")
            if family in contracts:
                raise SurfaceContractError(f"duplicate surface contract family {family!r}")
            for key in (
                "owner",
                "spec_key",
                "profile",
                "fields",
                "enums",
                "conditions",
                "mutually_exclusive",
                "routes",
                "hard_boundaries",
                "generated_obligations",
                "evidence",
                "legacy",
            ):
                if key not in contract:
                    raise SurfaceContractError(
                        f"surface contract {family!r} is missing required field {key!r}"
                    )
            relative_parts = page.relative_to(root).parts
            expected_owner = Path(*relative_parts[1:]).as_posix()
            if contract["owner"] != expected_owner:
                raise SurfaceContractError(
                    f"surface contract {family!r} owner must be {expected_owner!r}"
                )
            if contract["spec_key"] != family:
                raise SurfaceContractError(
                    f"surface contract {family!r} spec_key must match its family"
                )
            expected_profile = {"sts2": "0.107.1", "ritsulib_compat": "0.5.4"}
            if contract["profile"] != expected_profile:
                raise SurfaceContractError(
                    f"surface contract {family!r} must use pinned profile {expected_profile}"
                )
            fields = contract["fields"]
            if not isinstance(fields, dict) or not fields:
                raise SurfaceContractError(
                    f"surface contract {family!r} requires object-valued fields"
                )
            for list_key in (
                "conditions",
                "mutually_exclusive",
                "hard_boundaries",
                "generated_obligations",
            ):
                if not isinstance(contract[list_key], list):
                    raise SurfaceContractError(
                        f"surface contract {family!r} field {list_key!r} must be a list"
                    )
            if not isinstance(contract["enums"], dict):
                raise SurfaceContractError(
                    f"surface contract {family!r} enums must be an object"
                )
            evidence = contract["evidence"]
            expected = {
                "framework_expressible": True,
                "open_mod_authorable": True,
                "game_observed": False,
            }
            if evidence != expected:
                raise SurfaceContractError(
                    f"surface contract {family!r} must keep independent evidence labels {expected}"
                )
            _validate_contract_routes(contract, family)
            contracts[family] = contract
    return contracts


def parse_surface_data(text: str) -> dict[str, Any]:
    matches = list(DATA_BLOCK_RE.finditer(text))
    if len(matches) != 1:
        raise SurfaceContractError(
            "v3 SPEC must contain exactly one open-mod-surface-data/v1 JSON block"
        )
    data = _json_object(matches[0].group("body"), "surface data block")
    if data.get("contract") != CONTRACT_ID:
        raise SurfaceContractError(f"surface data contract must be {CONTRACT_ID}")
    families = data.get("families")
    if not isinstance(families, dict):
        raise SurfaceContractError("surface data block requires an object-valued families field")
    return families


def _list(value: Any, label: str, *, nonempty: bool = False) -> list[Any]:
    if not isinstance(value, list) or (nonempty and not value):
        qualifier = "nonempty " if nonempty else ""
        raise SurfaceContractError(f"{label} must be a {qualifier}list")
    return value


def _object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SurfaceContractError(f"{label} must be an object")
    return value


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SurfaceContractError(f"{label} must be nonempty text")
    return value.strip()


def _integer(value: Any, label: str, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise SurfaceContractError(f"{label} must be an integer")
    if minimum is not None and value < minimum:
        raise SurfaceContractError(f"{label} must be >= {minimum}")
    return value


def _enum(value: Any, allowed: list[str], label: str) -> str:
    text = _text(value, label)
    if text not in allowed:
        raise SurfaceContractError(f"{label} must be one of: {', '.join(allowed)}")
    return text


def _unique_ids(items: list[Any], label: str, key: str = "id") -> set[str]:
    seen: set[str] = set()
    for index, raw in enumerate(items):
        item = _object(raw, f"{label}[{index}]")
        identity = _text(item.get(key), f"{label}[{index}].{key}")
        if identity in seen:
            raise SurfaceContractError(f"{label} has duplicate {key} {identity!r}")
        seen.add(identity)
    return seen


def _route(value: Any, label: str, contract: dict[str, Any]) -> str:
    route = _text(value, label)
    if ".md#" not in route:
        raise SurfaceContractError(f"{label} must be a declared Markdown route anchor")
    if route not in contract["routes"]:
        raise SurfaceContractError(f"{label} is not declared by its owner contract: {route}")
    return route


def _validate_secondary_resources(value: Any, contract: dict[str, Any]) -> None:
    block = _object(value, "secondary_resources")
    resources = _list(block.get("resources"), "secondary_resources.resources", nonempty=True)
    resource_ids = _unique_ids(resources, "secondary_resources.resources")
    for index, raw in enumerate(resources):
        item = _object(raw, f"secondary_resources.resources[{index}]")
        minimum = _integer(item.get("min"), f"resource[{index}].min", 0)
        default = _integer(item.get("default"), f"resource[{index}].default")
        maximum = _integer(item.get("max"), f"resource[{index}].max")
        if not minimum <= default <= maximum:
            raise SurfaceContractError("resource bounds must satisfy min <= default <= max")
        _enum(item.get("persistence"), contract["enums"]["persistence"], "resource.persistence")
        turn_start = _enum(
            item.get("turn_start"), contract["enums"]["turn_start"], "resource.turn_start"
        )
        if turn_start in {"reset_to_max", "add_max_to_current"} and maximum < 0:
            raise SurfaceContractError("max-based turn-start policy requires a nonnegative maximum")
        if item.get("native_energy") is not False:
            raise SurfaceContractError("secondary resource must declare native_energy=false")
        _route(item.get("route"), "resource.route", contract)

    uses = _list(block.get("uses"), "secondary_resources.uses")
    _unique_ids(uses, "secondary_resources.uses")
    for index, raw in enumerate(uses):
        use = _object(raw, f"secondary_resources.uses[{index}]")
        if _text(use.get("resource"), "resource use.resource") not in resource_ids:
            raise SurfaceContractError("resource use names an undeclared resource")
        _text(use.get("card"), "resource use.card")
        role = _enum(use.get("role"), contract["enums"]["role"], "resource use.role")
        cost = _enum(use.get("cost"), contract["enums"]["cost"], "resource use.cost")
        shortfall = _enum(
            use.get("shortfall"), contract["enums"]["shortfall"], "resource use.shortfall"
        )
        amount = _integer(use.get("amount"), "resource use.amount", -1)
        if cost == "fixed" and amount < 0:
            raise SurfaceContractError("fixed secondary-resource payment must be nonnegative")
        if cost == "x" and amount != -1:
            raise SurfaceContractError("secondary-resource X payment must use amount -1")
        if role == "repeatable_extra" and cost == "x":
            raise SurfaceContractError("X repeatable-extra secondary-resource payment is unsupported")
        if role == "required" and shortfall == "not_applicable":
            raise SurfaceContractError("required resource payment must declare a shortfall policy")
        if role != "required" and shortfall != "not_applicable":
            raise SurfaceContractError("only required resource payments declare shortfall policy")
        replacement = use.get("replacement_resource")
        if shortfall.startswith("replacement_then_"):
            replacement_id = _text(replacement, "replacement resource")
            if replacement_id not in resource_ids or replacement_id == use.get("resource"):
                raise SurfaceContractError(
                    "replacement payment must name a different declared secondary resource"
                )
            if use.get("planner_side_effect_free") is not True:
                raise SurfaceContractError("replacement payment planning must be side-effect-free")
        elif replacement is not None or use.get("planner_side_effect_free") is not None:
            raise SurfaceContractError(
                "replacement payment fields require a replacement_then_* shortfall policy"
            )
        max_stacks = use.get("max_stacks")
        if role == "repeatable_extra":
            if max_stacks is not None:
                _integer(max_stacks, "repeatable extra max_stacks", 1)
        elif max_stacks is not None:
            raise SurfaceContractError("max_stacks is only valid for repeatable-extra payments")
        if use.get("payoff_after_commit") is not True:
            raise SurfaceContractError("resource payoff must occur after authoritative payment commit")

    consumers = _list(block.get("ui_consumers"), "secondary_resources.ui_consumers")
    for raw in consumers:
        consumer = _object(raw, "secondary resource UI consumer")
        if _text(consumer.get("resource"), "UI consumer.resource") not in resource_ids:
            raise SurfaceContractError("UI consumer names an undeclared resource")
        _enum(consumer.get("host"), contract["enums"]["ui_host"], "UI consumer.host")
        _route(consumer.get("route"), "UI consumer.route", contract)


def _validate_monster_encounter(value: Any, contract: dict[str, Any]) -> None:
    block = _object(value, "monster_encounter")
    monsters = _list(block.get("monsters"), "monster_encounter.monsters", nonempty=True)
    monster_ids = _unique_ids(monsters, "monster_encounter.monsters")
    for index, raw in enumerate(monsters):
        monster = _object(raw, f"monster[{index}]")
        min_hp = _integer(monster.get("min_hp"), "monster.min_hp", 1)
        max_hp = _integer(monster.get("max_hp"), "monster.max_hp", 1)
        if min_hp > max_hp:
            raise SurfaceContractError("monster min_hp must be <= max_hp")
        _route(monster.get("reachability_route"), "monster.reachability_route", contract)
        moves = _list(monster.get("moves"), "monster.moves", nonempty=True)
        branches = _list(monster.get("branches"), "monster.branches")
        move_ids = _unique_ids(moves, "monster.moves")
        branch_ids = _unique_ids(branches, "monster.branches")
        states = move_ids | branch_ids
        initial = _text(monster.get("initial_state"), "monster.initial_state")
        if initial not in states:
            raise SurfaceContractError("monster initial_state is not a declared state")
        edges: dict[str, list[str]] = {}
        for move_raw in moves:
            move = _object(move_raw, "monster move")
            move_id = _text(move.get("id"), "monster move.id")
            _list(move.get("intents"), f"move {move_id}.intents", nonempty=True)
            _list(move.get("effects"), f"move {move_id}.effects", nonempty=True)
            successor = _text(move.get("next"), f"move {move_id}.next")
            edges[move_id] = [successor]
        for branch_raw in branches:
            branch = _object(branch_raw, "monster branch")
            branch_id = _text(branch.get("id"), "monster branch.id")
            kind = _enum(branch.get("kind"), contract["enums"]["branch_kind"], "branch.kind")
            targets = _list(branch.get("targets"), f"branch {branch_id}.targets", nonempty=True)
            successors: list[str] = []
            for target_raw in targets:
                target = _object(target_raw, "branch target")
                successors.append(_text(target.get("successor"), "branch target.successor"))
                if kind == "random":
                    weight = target.get("weight")
                    if isinstance(weight, bool) or not isinstance(weight, (int, float)) or weight <= 0:
                        raise SurfaceContractError("random branch targets require positive numeric weights")
                elif not _text(target.get("condition"), "conditional branch target.condition"):
                    raise SurfaceContractError("conditional branch targets require conditions")
            edges[branch_id] = successors
        for source, successors in edges.items():
            unknown = sorted(set(successors) - states)
            if unknown:
                raise SurfaceContractError(f"monster state {source!r} has unknown successors: {unknown}")
        reached: set[str] = set()
        pending = deque([initial])
        while pending:
            state = pending.popleft()
            if state in reached:
                continue
            reached.add(state)
            pending.extend(edges.get(state, []))
        if reached != states:
            raise SurfaceContractError(f"monster has unreachable states: {sorted(states - reached)}")

    encounters = _list(block.get("encounters"), "monster_encounter.encounters", nonempty=True)
    _unique_ids(encounters, "monster_encounter.encounters")
    reachable_monster_ids: set[str] = set()
    for raw in encounters:
        encounter = _object(raw, "encounter")
        actual = [_text(x, "encounter.actual_roster entry") for x in _list(
            encounter.get("actual_roster"), "encounter.actual_roster", nonempty=True
        )]
        possible = [_text(x, "encounter.all_possible entry") for x in _list(
            encounter.get("all_possible"), "encounter.all_possible", nonempty=True
        )]
        if set(actual) - monster_ids or set(possible) - monster_ids:
            raise SurfaceContractError("encounter roster references an unregistered Monster")
        if set(actual) - set(possible):
            raise SurfaceContractError("encounter actual_roster must be included in all_possible")
        reachable_monster_ids.update(actual)
        _route(encounter.get("placement_route"), "encounter.placement_route", contract)
    if reachable_monster_ids != monster_ids:
        raise SurfaceContractError(
            "every registered Monster must appear in at least one actual encounter roster"
        )


def _validate_character_starting(value: Any, contract: dict[str, Any]) -> None:
    block = _object(value, "character_starting")
    _integer(block.get("starting_hp"), "character.starting_hp", 1)
    _integer(block.get("starting_gold"), "character.starting_gold", 0)
    _integer(block.get("max_energy"), "character.max_energy", 1)
    _integer(block.get("base_orb_slots"), "character.base_orb_slots", 0)
    registered = _list(block.get("registered_content"), "character.registered_content")
    registered_keys: set[tuple[str, str, str]] = set()
    for raw in registered:
        item = _object(raw, "registered content")
        kind = _enum(item.get("kind"), contract["enums"]["starter_kind"], "registered.kind")
        identity = _text(item.get("id"), "registered.id")
        pool = _text(item.get("pool"), "registered.pool")
        registered_key = (kind, identity, pool)
        if registered_key in registered_keys:
            raise SurfaceContractError("character registered content contains a duplicate typed id")
        registered_keys.add(registered_key)
    for field, kind in (("cards", "card"), ("relics", "relic"), ("potions", "potion")):
        entries = _list(block.get(field), f"character.{field}")
        _unique_ids(entries, f"character.{field}")
        for raw in entries:
            entry = _object(raw, f"character.{field} entry")
            identity = _text(entry.get("id"), f"character.{field}.id")
            _integer(entry.get("count"), f"character.{field}.count", 1)
    pools = _object(block.get("pools"), "character.pools")
    pool_ids = {
        key: _text(pools.get(key), f"character.pools.{key}")
        for key in ("card", "relic", "potion")
    }
    for field, kind in (("cards", "card"), ("relics", "relic"), ("potions", "potion")):
        for raw in _list(block.get(field), f"character.{field}"):
            identity = _text(_object(raw, f"character.{field} entry").get("id"), f"character.{field}.id")
            if (kind, identity, pool_ids[kind]) not in registered_keys:
                raise SurfaceContractError(
                    f"starter {kind} {identity!r} is absent from its declared typed pool"
                )
    _route(block.get("route"), "character.route", contract)


def _validate_rest_site_options(value: Any, contract: dict[str, Any]) -> None:
    block = _object(value, "rest_site_options")
    options = _list(block.get("options"), "rest_site_options.options")
    _unique_ids(options, "rest_site_options")
    for raw in options:
        option = _object(raw, "Rest Site option")
        owner = _object(option.get("owner"), "Rest Site owner")
        state = _object(option.get("state_handle"), "Rest Site state_handle")
        owner_surface = _enum(owner.get("surface"), contract["enums"]["owner_surface"], "owner.surface")
        owner_id = _text(owner.get("id"), "owner.id")
        if state.get("surface") != owner_surface or state.get("id") != owner_id:
            raise SurfaceContractError("Rest Site ownership and state handles must agree")
        if option.get("owner_multiplicity") != "exactly_one":
            raise SurfaceContractError("Rest Site owner multiplicity must be exactly_one")
        _text(option.get("eligibility"), "Rest Site eligibility")
        _text(option.get("affordability"), "Rest Site affordability")
        transaction = _object(option.get("transaction"), "Rest Site transaction")
        if transaction.get("preflightable") is not True:
            raise SurfaceContractError("Rest Site transaction must be preflightable")
        _list(transaction.get("steps"), "Rest Site transaction.steps", nonempty=True)
        repeatability = _enum(
            option.get("repeatability"), contract["enums"]["repeatability"], "repeatability"
        )
        state_kind = _enum(
            state.get("kind"), contract["enums"]["state_kind"], "state_handle.kind"
        )
        expected_state = "saved_owner_bool" if repeatability == "once_per_run" else "host_visit_removal"
        if state_kind != expected_state:
            raise SurfaceContractError(
                f"{repeatability} Rest Site option requires state_handle.kind={expected_state}"
            )
        _enum(option.get("after_success"), contract["enums"]["after_success"], "after_success")
        if option.get("successful_same_visit_repeat") is not False:
            raise SurfaceContractError("a successful Rest Site option cannot repeat in the same visit")
        if option.get("multiplayer") != "singleplayer":
            raise SurfaceContractError("Rest Site options remain singleplayer")
        _route(option.get("route"), "Rest Site option.route", contract)


def _validate_computed_values(value: Any, contract: dict[str, Any]) -> None:
    block = _object(value, "computed_card_values")
    values = _list(block.get("values"), "computed_card_values.values")
    names: set[tuple[str, str]] = set()
    for raw in values:
        item = _object(raw, "computed Card value")
        card_id = _text(item.get("card_id"), "computed card_id")
        name = _text(item.get("name"), "computed name")
        key = (card_id, name)
        if key in names:
            raise SurfaceContractError("computed Card value names must be unique per Card")
        names.add(key)
        role = _enum(item.get("role"), contract["enums"]["role"], "computed role")
        formula = _text(item.get("formula"), "computed formula")
        if re.search(r"\b(rng|random|cmd|mutate|set|write)\b", formula, re.IGNORECASE):
            raise SurfaceContractError("computed formula must be pure and cannot name RNG/Cmd/mutation")
        inputs = {_text(x, "computed input") for x in _list(item.get("inputs"), "computed inputs")}
        declared = {
            _text(x, "declared computed input")
            for x in _list(item.get("declared_inputs"), "declared computed inputs")
        }
        if inputs != declared:
            raise SurfaceContractError("computed formula inputs and declared_inputs must match exactly")
        domain = _object(item.get("domain"), "computed domain")
        minimum = _integer(domain.get("min"), "computed domain.min")
        maximum = _integer(domain.get("max"), "computed domain.max")
        if minimum > maximum:
            raise SurfaceContractError("computed domain min must be <= max")
        evaluation = _enum(
            item.get("evaluation_point"), contract["enums"]["evaluation_point"], "evaluation_point"
        )
        if item.get("preview_point") != evaluation or item.get("execution_point") != evaluation:
            raise SurfaceContractError("computed preview/execution phases must use one evaluation point")
        binding = _enum(item.get("text_binding"), contract["enums"]["text_binding"], "text_binding")
        if role in {"energy_icons", "star_icons"} and binding != "icon_formatter":
            raise SurfaceContractError("icon-count roles require icon_formatter text binding")
        if role not in {"energy_icons", "star_icons"} and binding == "icon_formatter":
            raise SurfaceContractError("icon_formatter is incompatible with this computed role")
        expected_native = "exactly_once" if role in {"damage", "block", "applied_power"} else "none"
        if item.get("native_modifiers") != expected_native:
            raise SurfaceContractError(
                f"computed role {role!r} requires native_modifiers={expected_native!r}"
            )
        _text(item.get("upgrade_rule"), "computed upgrade_rule")
        _route(item.get("route"), "computed value.route", contract)


def _validate_bounded_state(value: Any, contract: dict[str, Any]) -> None:
    block = _object(value, "bounded_state")
    states = _list(block.get("states"), "bounded_state.states")
    _unique_ids(states, "bounded_state")
    for raw in states:
        state = _object(raw, "bounded state")
        owner = _object(state.get("owner"), "bounded state owner")
        owner_surface = _enum(owner.get("surface"), contract["enums"]["owner_surface"], "state owner.surface")
        _text(owner.get("id"), "state owner.id")
        schema = _list(state.get("schema"), "bounded state.schema", nonempty=True)
        _unique_ids(schema, "bounded state.schema", key="name")
        for field in schema:
            field_obj = _object(field, "state field")
            field_type = _enum(field_obj.get("type"), contract["enums"]["saved_type"], "state field.type")
            initial = field_obj.get("initial")
            if field_type in {"int", "decimal"}:
                minimum = field_obj.get("min")
                maximum = field_obj.get("max")
                if isinstance(minimum, bool) or not isinstance(minimum, (int, float)):
                    raise SurfaceContractError("numeric state field requires min")
                if isinstance(maximum, bool) or not isinstance(maximum, (int, float)) or minimum > maximum:
                    raise SurfaceContractError("numeric state field requires ordered finite max")
                if isinstance(initial, bool) or not isinstance(initial, (int, float)):
                    raise SurfaceContractError("numeric state field requires a numeric initial value")
                if not minimum <= initial <= maximum:
                    raise SurfaceContractError("numeric state initial value must be within bounds")
            elif field_type == "bool" and not isinstance(initial, bool):
                raise SurfaceContractError("bool state field requires a boolean initial value")
            elif field_type == "string":
                if not isinstance(initial, str):
                    raise SurfaceContractError("string state field requires a string initial value")
                max_length = _integer(field_obj.get("max_length"), "string state field.max_length", 1)
                if len(initial) > max_length:
                    raise SurfaceContractError("string state initial value exceeds max_length")
        lifetime = _enum(state.get("lifetime"), contract["enums"]["lifetime"], "state lifetime")
        persistence = _enum(
            state.get("persistence"), contract["enums"]["persistence"], "state persistence"
        )
        if persistence == "run_save":
            if lifetime != "run":
                raise SurfaceContractError("run_save state requires run lifetime")
            if owner_surface not in contract["enums"]["run_saved_owner_surface"]:
                raise SurfaceContractError(
                    "run_save state requires a SavedProperties-backed owner surface"
                )
            unsupported = [
                _object(field, "state field").get("type")
                for field in schema
                if _object(field, "state field").get("type")
                not in contract["enums"]["run_saved_type"]
            ]
            if unsupported:
                raise SurfaceContractError("run_save state contains an unsupported saved field type")
        elif lifetime == "run":
            raise SurfaceContractError("run lifetime requires run_save persistence")
        _text(state.get("reset"), "state reset")
        _text(state.get("visibility"), "state visibility")
        transitions = _list(state.get("transitions"), "state.transitions", nonempty=True)
        _unique_ids(transitions, "state.transitions")
        for transition in transitions:
            item = _object(transition, "state transition")
            listener = _object(item.get("listener"), "state transition.listener")
            listener_surface = _enum(
                listener.get("surface"),
                contract["enums"]["transition_surface"],
                "state transition.listener.surface",
            )
            _text(listener.get("id"), "state transition.listener.id")
            hook = _enum(
                item.get("hook"), contract["enums"]["transition_hook"], "state transition.hook"
            )
            allowed_listener_surfaces = contract["enums"].get("hook_listener_surfaces", {}).get(hook)
            if allowed_listener_surfaces is not None and listener_surface not in allowed_listener_surfaces:
                raise SurfaceContractError(
                    f"state transition hook {hook!r} cannot use listener surface {listener_surface!r}"
                )
            updates = {
                _text(name, "state transition update")
                for name in _list(item.get("updates"), "state transition.updates", nonempty=True)
            }
            schema_names = {
                _text(_object(field, "state field").get("name"), "state field.name")
                for field in schema
            }
            if updates - schema_names:
                raise SurfaceContractError("state transition updates an undeclared state field")
            _route(item.get("route"), "state transition.route", contract)
        consumers = _list(state.get("consumers"), "state.consumers")
        consumer_ids = _unique_ids(consumers, "state.consumers")
        for consumer in consumers:
            _route(
                _object(consumer, "state consumer").get("route"),
                "state consumer.route",
                contract,
            )
        for output in _list(state.get("outputs"), "state.outputs"):
            item = _object(output, "state output")
            if _text(item.get("consumer"), "state output.consumer") not in consumer_ids:
                raise SurfaceContractError("state output names an undeclared consumer")
            _route(item.get("route"), "state output.route", contract)


def _validate_forced_events(value: Any, contract: dict[str, Any]) -> None:
    block = _object(value, "forced_event_mappings")
    mappings = _list(block.get("mappings"), "forced_event_mappings.mappings")
    _unique_ids(mappings, "forced_event_mappings")
    priorities: set[int] = set()
    token_keys: set[tuple[str, tuple[int, ...]]] = set()
    for raw in mappings:
        mapping = _object(raw, "forced Event mapping")
        token = _text(mapping.get("token_id"), "forced mapping.token_id")
        condition = _enum(
            mapping.get("condition"), contract["enums"]["condition"], "forced mapping.condition"
        )
        acts = tuple(sorted(_integer(x, "forced mapping act", 0) for x in _list(
            mapping.get("act_set"), "forced mapping.act_set", nonempty=True
        )))
        if len(acts) != len(set(acts)):
            raise SurfaceContractError("forced Event act_set contains duplicate acts")
        priority = _integer(mapping.get("priority"), "forced mapping.priority")
        if priority in priorities:
            raise SurfaceContractError("forced Event mappings have ambiguous equal priority")
        priorities.add(priority)
        token_key = (token, acts)
        if token_key in token_keys:
            raise SurfaceContractError("forced Event mappings duplicate token/act identity")
        token_keys.add(token_key)
        target_event = _text(mapping.get("target_event"), "forced mapping.target_event")
        _enum(mapping.get("conflict"), contract["enums"]["conflict"], "forced mapping.conflict")
        _enum(mapping.get("consumption"), contract["enums"]["consumption"], "forced mapping.consumption")
        sequence = [_text(x, "forced sequence entry") for x in _list(
            mapping.get("sequence"), "forced mapping.sequence", nonempty=True
        )]
        if (
            len(sequence) != len(set(sequence))
            or sequence[0] != target_event
            or mapping.get("terminal") is not True
        ):
            raise SurfaceContractError("forced Event sequence must be finite, unique, and terminating")
        consume_at = _text(mapping.get("consume_at_event"), "forced mapping.consume_at_event")
        consumption = mapping.get("consumption")
        if consumption == "on_target_success" and (len(sequence) != 1 or consume_at != target_event):
            raise SurfaceContractError(
                "on_target_success consumption requires a one-Event sequence and target consumption"
            )
        if consumption == "on_sequence_complete" and consume_at != sequence[-1]:
            raise SurfaceContractError(
                "on_sequence_complete consumption must name the final sequence Event"
            )
        if mapping.get("progress_state") != "saved_card_index":
            raise SurfaceContractError("forced Event sequence requires saved_card_index progress")
        if mapping.get("save_claim") != "game-unobserved":
            raise SurfaceContractError("forced Event save/resume must remain game-unobserved")
        _route(mapping.get("route"), "forced mapping.route", contract)


def _validate_card_costs(value: Any, contract: dict[str, Any]) -> None:
    block = _object(value, "card_costs")
    costs = _list(block.get("costs"), "card_costs.costs")
    _unique_ids(costs, "card_costs", key="card_id")
    for raw in costs:
        item = _object(raw, "Card cost")
        energy = _object(item.get("energy"), "Card energy cost")
        stars = _object(item.get("stars"), "Card Star cost")
        energy_kind = _enum(energy.get("kind"), contract["enums"]["energy_kind"], "energy.kind")
        star_kind = _enum(stars.get("kind"), contract["enums"]["star_kind"], "stars.kind")
        for cost, kind, label in ((energy, energy_kind, "energy"), (stars, star_kind, "stars")):
            amount = _integer(cost.get("amount"), f"{label}.amount", -1)
            if kind == "fixed" and amount < 0:
                raise SurfaceContractError(f"fixed {label} cost must be nonnegative")
            if kind == "x" and amount != -1:
                raise SurfaceContractError(f"X {label} cost must use amount -1")
            if kind == "none" and amount != 0:
                raise SurfaceContractError(f"none {label} cost must use amount 0")
            _text(cost.get("upgrade"), f"{label}.upgrade")
        if energy_kind == "x" and star_kind == "x":
            raise SurfaceContractError("simultaneous Energy-X and Star-X is not authorable")
        if item.get("native_payment") is not True or item.get("native_ui") is not True:
            raise SurfaceContractError("Card costs require native payment and native UI")
        if item.get("combined_x_replay") != "game-unobserved":
            raise SurfaceContractError("new Energy/Star combinations remain game-unobserved")
        _route(item.get("route"), "Card cost.route", contract)


def _validate_event_profiles(value: Any, contract: dict[str, Any]) -> None:
    block = _object(value, "event_option_profiles")
    profiles = _list(block.get("profiles"), "event_option_profiles.profiles")
    option_keys: set[tuple[str, str]] = set()
    for raw in profiles:
        item = _object(raw, "Event option profile")
        key = (_text(item.get("event_id"), "Event profile.event_id"), _text(item.get("option_id"), "Event profile.option_id"))
        if key in option_keys:
            raise SurfaceContractError("duplicate Event option profile")
        option_keys.add(key)
        acquisitions = _list(item.get("acquisitions"), "Event acquisitions")
        acquisition_keys: set[tuple[str, str]] = set()
        for acquisition_raw in acquisitions:
            acquisition = _object(acquisition_raw, "Event acquisition")
            kind = _enum(acquisition.get("kind"), contract["enums"]["acquisition_kind"], "acquisition.kind")
            model_id = _text(acquisition.get("model_id"), "acquisition.model_id")
            acquisition_key = (kind, model_id)
            if acquisition_key in acquisition_keys:
                raise SurfaceContractError("Event option contains a duplicate acquisition")
            acquisition_keys.add(acquisition_key)
            expected = "native_card_preview" if kind == "card" else "native_relic_obtain"
            if acquisition.get("presentation") != expected:
                raise SurfaceContractError("Event acquisition presentation does not match its kind")
            if acquisition.get("grant_once") is not True:
                raise SurfaceContractError("Event acquisition must grant exactly once")
        shake = item.get("shake")
        if shake is not None:
            shake_obj = _object(shake, "Event shake")
            _enum(shake_obj.get("profile"), contract["enums"]["shake_profile"], "shake.profile")
            if shake_obj.get("respect_setting") is not True or shake_obj.get("once") is not True:
                raise SurfaceContractError("Event shake must be one-shot and respect the player setting")
        _route(item.get("route"), "Event profile.route", contract)


VALIDATORS = {
    "secondary_resources": _validate_secondary_resources,
    "monster_encounter": _validate_monster_encounter,
    "character_starting": _validate_character_starting,
    "rest_site_options": _validate_rest_site_options,
    "computed_card_values": _validate_computed_values,
    "bounded_state": _validate_bounded_state,
    "forced_event_mappings": _validate_forced_events,
    "card_costs": _validate_card_costs,
    "event_option_profiles": _validate_event_profiles,
}


def validate_spec_text(text: str) -> int:
    contracts = load_surface_contracts()
    missing_contracts = sorted(set(VALIDATORS) - set(contracts))
    if missing_contracts:
        raise SurfaceContractError(
            "shipped owner pages are missing surface contracts: " + ", ".join(missing_contracts)
        )
    families = parse_surface_data(text)
    unknown = sorted(set(families) - set(VALIDATORS))
    if unknown:
        raise SurfaceContractError("surface data declares unknown families: " + ", ".join(unknown))
    for family, value in families.items():
        contract = contracts[family]
        if contract.get("spec_key") != family:
            raise SurfaceContractError(f"surface contract {family!r} has mismatched spec_key")
        VALIDATORS[family](value, contract)
    return len(families)


def validate_spec_file(path: Path) -> int:
    return validate_spec_text(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate v3 surface data against shipped contracts.")
    parser.add_argument("--spec", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        families = validate_spec_file(args.spec)
    except (OSError, SurfaceContractError) as exc:
        print(f"[surface-contract] failed: {exc}", file=sys.stderr)
        return 2
    print(f"[surface-contract] ok contract={CONTRACT_ID} families={families}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
