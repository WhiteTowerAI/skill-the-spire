from __future__ import annotations

import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


TOOLS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_DIR))
import build  # noqa: E402
import collect_vanilla_catalog as collector  # noqa: E402
import scaffold  # noqa: E402
import vanilla_overrides as overrides  # noqa: E402
from ritsu_profile import (  # noqa: E402
    PROFILE,
    local_mods_dir,
    resolve_runtime_asset,
    resolve_runtime_compile_profile,
)


ASSEMBLY_SHA256 = "a" * 64
LOCALIZATION_LANGUAGES = [
    "deu",
    "eng",
    "esp",
    "fra",
    "ita",
    "jpn",
    "kor",
    "pol",
    "ptb",
    "rus",
    "spa",
    "tha",
    "tur",
    "zhs",
]


def collector_snapshots() -> tuple[dict, dict]:
    models = [
        {
            "id": "RELIC.LOST_WISP",
            "type": "MegaCrit.Sts2.Core.Models.Relics.LostWisp",
            "content_kind": "relic",
            "is_debug": False,
            "title_localization": {
                "table": "relics",
                "key": "LOST_WISP.title",
                "localized_titles": {"eng": "Lost Wisp", "zhs": "迷失幽火"},
            },
            "properties": {"rarity": "Common"},
            "sources": {"relic_pools": ["RELIC_POOL.SHARED_RELIC_POOL"]},
        },
        {
            "id": "CARD.LOST_WISP",
            "type": "MegaCrit.Sts2.Core.Models.Cards.LostWisp",
            "content_kind": "card",
            "is_debug": False,
            "title_localization": {
                "table": "cards",
                "key": "LOST_WISP.title",
                "localized_titles": {"eng": "Lost Wisp", "zhs": "迷失幽火"},
            },
            "properties": {
                "card_type": "Skill",
                "dynamic_vars": [
                    {
                        "name": "Cards",
                        "type": "MegaCrit.Sts2.Core.Localization.DynamicVars.DynamicVar",
                        "base_value": 1,
                    }
                ],
                "energy_cost": 1,
                "energy_cost_x": False,
                "keywords": [],
                "max_upgrade_level": 1,
                "rarity": "Common",
                "star_cost": -1,
                "star_cost_x": False,
                "tags": [],
                "target_type": "Self",
                "upgrade_levels": [],
            },
            "sources": {"card_pools": ["CARD_POOL.COLORLESS_CARD_POOL"]},
        },
    ]
    runtime = {
        "schema": overrides.RUNTIME_SCHEMA,
        "host_version": PROFILE.host_version,
        "profile": PROFILE.profile_id,
        "assembly_sha256": ASSEMBLY_SHA256,
        "localization_languages": LOCALIZATION_LANGUAGES,
        "models": models,
    }
    assembly = {
        "schema": overrides.ASSEMBLY_SCHEMA,
        "host_version": PROFILE.host_version,
        "profile": PROFILE.profile_id,
        "assembly": {
            "name": "sts2",
            "version": "0.1.0.0",
            "sha256": ASSEMBLY_SHA256,
            "size": 123456,
            "mvid": "00000000-0000-0000-0000-000000000001",
            "metadata_version": "v4.0.30319",
        },
        "types": [
            {"full_name": model["type"], "metadata_token": 33554433 + index}
            for index, model in enumerate(models)
        ],
        "adapters": [],
    }
    return runtime, assembly


def make_catalog() -> dict:
    runtime, assembly = collector_snapshots()
    return overrides.merge_catalogs(runtime, assembly)


def make_operation(
    index: int,
    operation_id: str,
    *,
    target: str = "CARD.LOST_WISP",
    mode: str = "adjust",
    surface: str = "card.rarity",
    adjustment: str = "set",
    route: dict | None = None,
) -> dict:
    return {
        "order": index,
        "operation_id": operation_id,
        "target_model_id": target,
        "mode": mode,
        "surface": surface,
        "route": route
        or {"class": "public", "id": "card.property.rarity", "fingerprint": None},
        "expected_baseline": {
            "category": "CARD",
            "type": "MegaCrit.Sts2.Core.Models.Cards.LostWisp",
            "properties": {"rarity": "Common"},
        },
        "semantics": {"adjustment": adjustment, "value": "Rare"},
    }


def manifest_with(catalog: dict, operations: list[dict]) -> dict:
    manifest = overrides.create_empty_manifest("Proof", catalog)
    manifest["operations"] = operations
    return manifest


def enable_card_family(catalog: dict) -> dict:
    catalog["authorable_route_families"] = [overrides.PUBLIC_CARD_OVERRIDE_FAMILY]
    catalog["catalog_sha256"] = overrides.catalog_digest(catalog)
    return catalog


def make_visual_catalog() -> dict:
    runtime, assembly = collector_snapshots()
    existing = {(model["id"].split(".", 1)[0], model["content_kind"]) for model in runtime["models"]}
    required = {
        (route["category"], route["content_kind"] or route["category"].lower())
        for route in overrides.PUBLIC_VISUAL_ROUTES.values()
    }
    for index, (category, content_kind) in enumerate(sorted(required - existing), start=1):
        entry = f"VISUAL_{content_kind.upper()}"
        model_type = f"MegaCrit.Sts2.Core.Models.VisualProof.{category.title()}{index}"
        runtime["models"].append(
            {
                "id": f"{category}.{entry}",
                "type": model_type,
                "content_kind": content_kind,
                "is_debug": False,
                "title_localization": None,
                "properties": {},
                "sources": {},
            }
        )
        assembly["types"].append(
            {"full_name": model_type, "metadata_token": 33555000 + index}
        )
    return overrides.merge_catalogs(runtime, assembly)


def enable_visual_family(catalog: dict) -> dict:
    families = set(catalog["authorable_route_families"])
    families.add(overrides.PUBLIC_VISUAL_OVERRIDE_FAMILY)
    catalog["authorable_route_families"] = sorted(families)
    catalog["catalog_sha256"] = overrides.catalog_digest(catalog)
    return catalog


ANCIENT_ADAPTER_HASHES = {
    "ancient.flow.finish": "04fef98282aa7e01fbab7934c6f15ca5969b3029c32d4e83ae0ad3636dfcd060",
    "ancient.flow.set-state": "3a93f71ad25d06ad1470da740b5a4bc9095f8dbdb1c6f9d48fed397c0ce1c7b6",
    "ancient.initial-options.replace": "7645a9eea1118c340449e339ede4ce15169c72bed29a196990d8824bbdf12ca5",
}

AVAILABILITY_ADAPTER_HASHES = {
    "availability.card.pool-membership": "34a9ad59b7a7c2d05b312f2ba515969d3e78e09f903b0180025afeecb6a652d9",
    "availability.potion.epoch-gate": "2a4b5bb09b4e4e5e5b2c5895702a58a74cb79bde037c0a6d0908eef72607ce1a",
    "availability.potion.epoch-gate.defect": "f5122e44da2c313ab1accbc7af48967fb9761ed82b14615d412974c358aa9d05",
    "availability.potion.epoch-gate.ironclad": "e81f8255da2985e4c13234266af3286972ac1d16ea32d2114d8a5e0699cdc020",
    "availability.potion.epoch-gate.necrobinder": "efd1874a39de7fd19f5169de72429f89ff135256682840e14be77ccb15b107f8",
    "availability.potion.epoch-gate.regent": "5656947407b9a0e8785b01485ac42014ce082bc42b39aba0ff6b1f7e02307323",
    "availability.potion.epoch-gate.shared": "d35b374e4ceb12fa30dd114e030c72dc46c8e1be7f059856c3e90d5c9c1ad2f1",
    "availability.potion.epoch-gate.silent": "441e6df085104d62ce17e9ebcb287b3d29a1e3a734882acb499daf43e813382c",
    "availability.potion.pool-membership": "c1ea2c083548614d1ec4a46c49c67a8db9720361d3826a67c8166a4b26cc967b",
    "availability.relic.epoch-gate": "dca9123b8b3be8c27ce197513801232e0a640fa673f4ee314dbdeb3c39619ba1",
    "availability.relic.epoch-gate.defect": "b01ea54ca8727c2fe76cccd5f7ab6787bc8d029ba491443adfb96b0aff3ddc98",
    "availability.relic.epoch-gate.ironclad": "a4e14f2271c3df24593bca6118137ceaaceb24dae34d1e2a0b71f895155c0b11",
    "availability.relic.epoch-gate.necrobinder": "8b8c7559b12baadb0f5248c0649932e7081c39ce81ab605fff8536795054fce9",
    "availability.relic.epoch-gate.regent": "5012519dcf514196cecd9565853ca78649d17fb6e02f2f56868fdef56b4d90cf",
    "availability.relic.epoch-gate.shared": "37e2b57af7e86019b5af9923b946411fd0fa5b33d148d6ac9635611909358058",
    "availability.relic.epoch-gate.silent": "60108f1b02458188337f1b5bb937b7afce9d535f923afe87553380e436eecef1",
    "availability.relic.pool-membership": "3d6c4629d05021df4baeb0aed24b59c8af2d25bd8170194f28eac9fad9bd170b",
}


def vanilla_ref(model_id: str) -> dict:
    return {"source": "vanilla", "model_id": model_id}


def adapter_dependencies(catalog: dict, *adapter_ids: str) -> list[dict]:
    adapters = {adapter["id"]: adapter for adapter in catalog["adapters"]}
    return [
        {"id": adapter_id, "fingerprint": adapters[adapter_id]["il_sha256"]}
        for adapter_id in sorted(adapter_ids)
    ]


def make_non_card_operation(
    catalog: dict,
    target_id: str,
    route_id: str,
    *,
    index: int = 0,
    mode: str,
    route_class: str,
    semantics: dict,
    dependencies: tuple[str, ...] = (),
) -> dict:
    model = next(model for model in catalog["models"] if model["id"] == target_id)
    baseline = {key: copy.deepcopy(model[key]) for key in ("category", "type")}
    if route_id in overrides._NON_CARD_DATA_ROUTES:
        property_name = overrides._NON_CARD_DATA_ROUTES[route_id]["property"]
        baseline["properties"] = {
            property_name: copy.deepcopy(model["properties"][property_name])
        }
    return {
        "order": index,
        "operation_id": f"non-card.{index}.{target_id.lower().replace('_', '-')}",
        "target_model_id": target_id,
        "mode": mode,
        "surface": (
            f"{model['category'].lower()}.owner_hooks"
            if route_id in overrides._NON_CARD_OWNER_HOOK_ROUTES
            else route_id
        ),
        "route": {
            "class": route_class,
            "id": route_id,
            "fingerprint": None,
            "dependencies": adapter_dependencies(catalog, *dependencies),
        },
        "expected_baseline": baseline,
        "semantics": semantics,
    }


def make_ancient_catalog() -> dict:
    runtime, assembly = collector_snapshots()
    additional = [
        ("EVENT.DARV", "MegaCrit.Sts2.Core.Models.Events.Darv", "ancient"),
        ("EVENT.ORDINARY", "MegaCrit.Sts2.Core.Models.Events.Ordinary", "event"),
        ("POTION.PROOF", "MegaCrit.Sts2.Core.Models.Potions.Proof", "potion"),
        ("POWER.PROOF", "MegaCrit.Sts2.Core.Models.Powers.Proof", "power"),
        ("CHARACTER.PROOF", "MegaCrit.Sts2.Core.Models.Characters.Proof", "character"),
        (
            "ENCHANTMENT.PROOF",
            "MegaCrit.Sts2.Core.Models.Enchantments.Proof",
            "enchantment",
        ),
    ]
    for index, (model_id, model_type, content_kind) in enumerate(additional, start=1):
        runtime["models"].append(
            {
                "id": model_id,
                "type": model_type,
                "content_kind": content_kind,
                "is_debug": False,
                "title_localization": None,
                "properties": {},
                "sources": {},
            }
        )
        assembly["types"].append(
            {"full_name": model_type, "metadata_token": 33556000 + index}
        )

    adapter_shapes = {
        "ancient.flow.finish": (
            "MegaCrit.Sts2.Core.Models.AncientEventModel",
            "Done",
            "Void MegaCrit.Sts2.Core.Models.AncientEventModel.Done()",
        ),
        "ancient.flow.set-state": (
            "MegaCrit.Sts2.Core.Models.EventModel",
            "SetEventState",
            "Void MegaCrit.Sts2.Core.Models.EventModel.SetEventState(LocString, IEnumerable<EventOption>)",
        ),
        "ancient.initial-options.replace": (
            "MegaCrit.Sts2.Core.Models.AncientEventModel",
            "GenerateInitialOptionsWrapper",
            "IReadOnlyList<EventOption> MegaCrit.Sts2.Core.Models.AncientEventModel.GenerateInitialOptionsWrapper()",
        ),
    }
    for index, (adapter_id, (model_type, method, signature)) in enumerate(
        adapter_shapes.items(), start=1
    ):
        assembly["adapters"].append(
            {
                "id": adapter_id,
                "type": model_type,
                "method": method,
                "signature": signature,
                "metadata_token": 100680000 + index,
                "signature_sha256": f"{index}" * 64,
                "il_sha256": ANCIENT_ADAPTER_HASHES[adapter_id],
                "body_shape": {
                    "il_byte_count": 10 + index,
                    "max_stack": 2,
                    "local_signature_token": 0,
                    "exception_region_count": 0,
                },
            }
        )

    catalog = overrides.merge_catalogs(runtime, assembly)
    catalog["authorable_route_families"] = [overrides.ANCIENT_OVERRIDE_FAMILY]
    catalog["catalog_sha256"] = overrides.catalog_digest(catalog)
    return catalog


def make_availability_catalog() -> dict:
    runtime, assembly = collector_snapshots()
    additional = [
        (
            "POTION.PROOF",
            "MegaCrit.Sts2.Core.Models.Potions.Proof",
            "potion",
            False,
            {"potion_pools": ["POTION_POOL.SHARED_POTION_POOL"]},
        ),
        (
            "CHARACTER.PROOF",
            "MegaCrit.Sts2.Core.Models.Characters.Proof",
            "character",
            False,
            {},
        ),
        (
            "EVENT.ORDINARY",
            "MegaCrit.Sts2.Core.Models.Events.Ordinary",
            "event",
            False,
            {},
        ),
        (
            "EVENT.DARV",
            "MegaCrit.Sts2.Core.Models.Events.Darv",
            "ancient",
            False,
            {"shared_sources": ["ancients"]},
        ),
        (
            "EVENT.NEOW",
            "MegaCrit.Sts2.Core.Models.Events.Neow",
            "ancient",
            False,
            {"acts": ["ACT.OVERGROWTH"]},
        ),
        (
            "CARD_POOL.COLORLESS_CARD_POOL",
            "MegaCrit.Sts2.Core.Models.CardPools.ColorlessCardPool",
            "card_pool",
            False,
            {},
        ),
        (
            "CARD_POOL.IRONCLAD_CARD_POOL",
            "MegaCrit.Sts2.Core.Models.CardPools.IroncladCardPool",
            "card_pool",
            False,
            {},
        ),
        (
            "CARD_POOL.MOCK_CARD_POOL",
            "MegaCrit.Sts2.Core.Models.CardPools.MockCardPool",
            "card_pool",
            True,
            {},
        ),
        (
            "CARD_POOL.SILENT_CARD_POOL",
            "MegaCrit.Sts2.Core.Models.CardPools.SilentCardPool",
            "card_pool",
            False,
            {},
        ),
        (
            "POTION_POOL.MOCK_POTION_POOL",
            "MegaCrit.Sts2.Core.Models.PotionPools.MockPotionPool",
            "potion_pool",
            True,
            {},
        ),
        (
            "POTION_POOL.SHARED_POTION_POOL",
            "MegaCrit.Sts2.Core.Models.PotionPools.SharedPotionPool",
            "potion_pool",
            False,
            {},
        ),
        (
            "POTION_POOL.SILENT_POTION_POOL",
            "MegaCrit.Sts2.Core.Models.PotionPools.SilentPotionPool",
            "potion_pool",
            False,
            {},
        ),
        (
            "RELIC_POOL.EVENT_RELIC_POOL",
            "MegaCrit.Sts2.Core.Models.RelicPools.EventRelicPool",
            "relic_pool",
            False,
            {},
        ),
        (
            "RELIC_POOL.SHARED_RELIC_POOL",
            "MegaCrit.Sts2.Core.Models.RelicPools.SharedRelicPool",
            "relic_pool",
            False,
            {},
        ),
    ]
    for index, (model_id, model_type, content_kind, is_debug, sources) in enumerate(
        additional, start=1
    ):
        runtime["models"].append(
            {
                "id": model_id,
                "type": model_type,
                "content_kind": content_kind,
                "is_debug": is_debug,
                "title_localization": None,
                "properties": {},
                "sources": sources,
            }
        )
        assembly["types"].append(
            {"full_name": model_type, "metadata_token": 33557000 + index}
        )

    for index, (adapter_id, fingerprint) in enumerate(
        sorted(AVAILABILITY_ADAPTER_HASHES.items()), start=1
    ):
        assembly["adapters"].append(
            {
                "id": adapter_id,
                "type": f"MegaCrit.Sts2.Core.Models.AvailabilityAdapter{index}",
                "method": "Target",
                "signature": f"Void AvailabilityAdapter{index}.Target()",
                "metadata_token": 100690000 + index,
                "signature_sha256": f"{index:x}"[-1] * 64,
                "il_sha256": fingerprint,
                "body_shape": {
                    "il_byte_count": 10 + index,
                    "max_stack": 2,
                    "local_signature_token": 0,
                    "exception_region_count": 0,
                },
            }
        )

    catalog = overrides.merge_catalogs(runtime, assembly)
    catalog["authorable_route_families"] = [overrides.AVAILABILITY_OVERRIDE_FAMILY]
    catalog["catalog_sha256"] = overrides.catalog_digest(catalog)
    return catalog


def make_availability_epoch_operation(
    catalog: dict,
    target_id: str,
    *,
    index: int = 0,
    route_id: str = overrides.AVAILABILITY_PUBLIC_EPOCH_ROUTE,
    state: str = "require_epoch",
) -> dict:
    target = next(model for model in catalog["models"] if model["id"] == target_id)
    route = {
        "class": "public" if route_id == overrides.AVAILABILITY_PUBLIC_EPOCH_ROUTE else "adapter",
        "id": route_id,
        "fingerprint": None
        if route_id == overrides.AVAILABILITY_PUBLIC_EPOCH_ROUTE
        else AVAILABILITY_ADAPTER_HASHES[route_id],
    }
    dependencies = overrides.AVAILABILITY_EPOCH_ADAPTER_DEPENDENCIES.get(route_id)
    if dependencies is not None:
        route["dependencies"] = [
            {"id": adapter_id, "fingerprint": AVAILABILITY_ADAPTER_HASHES[adapter_id]}
            for adapter_id in dependencies
        ]
    return {
        "order": index,
        "operation_id": f"availability.epoch-{index}",
        "target_model_id": target_id,
        "mode": "availability",
        "surface": f"{target['category'].lower()}.epoch_gate",
        "route": route,
        "expected_baseline": {
            "category": target["category"],
            "type": target["type"],
            "content_kind": target["content_kind"],
        },
        "semantics": {
            "state": state,
            "epoch_id": "RELIC1_EPOCH" if state == "require_epoch" else None,
            "multiplayer": "singleplayer",
        },
    }


def make_pool_operation(
    catalog: dict,
    target_id: str,
    route_id: str,
    action: str,
    expected_primary: str,
    *,
    index: int = 0,
    source: str | None = None,
    destination: str | None = None,
) -> dict:
    target = next(model for model in catalog["models"] if model["id"] == target_id)
    contract = overrides._pool_contract(route_id)
    assert contract is not None
    semantics = {
        "action": action,
        "existing_instances": "preserve",
        "expected_primary_pool_model_id": expected_primary,
        "multiplayer": "singleplayer",
    }
    if source is not None:
        semantics["source_pool_model_id"] = source
    if destination is not None:
        semantics["destination_pool_model_id"] = destination
    return {
        "order": index,
        "operation_id": f"availability.pool-{index}",
        "target_model_id": target_id,
        "mode": "availability",
        "surface": contract["surface"],
        "route": {
            "class": "public" if route_id in overrides.AVAILABILITY_PUBLIC_POOL_ROUTES else "adapter",
            "id": route_id,
            "fingerprint": None
            if route_id in overrides.AVAILABILITY_PUBLIC_POOL_ROUTES
            else AVAILABILITY_ADAPTER_HASHES[route_id],
        },
        "expected_baseline": {
            "category": target["category"],
            "type": target["type"],
            "sources": {contract["source_key"]: target["sources"][contract["source_key"]]},
        },
        "semantics": semantics,
    }


def make_ancient_option(
    option_id: str,
    localization_key: str,
    *,
    next_step: dict | None = None,
    effects: list[dict] | None = None,
) -> dict:
    return {
        "id": option_id,
        "localization_key": localization_key,
        "visible_when": {"kind": "always", "parameters": {}},
        "enabled_when": {
            "kind": "owner_value",
            "parameters": {"field": "gold", "comparison": "gte", "value": 7},
        },
        "cost": {"kind": "gold", "amount": 7, "allow_lethal": False},
        "disable_on_chosen": True,
        "is_proceed": False,
        "hover_tips": [
            {"kind": "card", "model": vanilla_ref("CARD.LOST_WISP"), "upgraded": True},
            {"kind": "relic", "model": vanilla_ref("RELIC.LOST_WISP")},
            {"kind": "potion", "model": vanilla_ref("POTION.PROOF")},
            {"kind": "power", "model": vanilla_ref("POWER.PROOF"), "amount": 2},
        ],
        "relic": vanilla_ref("RELIC.LOST_WISP"),
        "effects": effects or [{"kind": "gain_gold", "amount": 17}],
        "next": next_step or {"kind": "finish"},
    }


def make_ancient_operation(
    catalog: dict,
    *,
    route_id: str = "ancient.initial-options.append",
    index: int = 0,
    option: dict | None = None,
    pages: list[dict] | None = None,
) -> dict:
    replacement = route_id.endswith("replace")
    route = {
        "class": "adapter" if replacement else "public",
        "id": route_id,
        "fingerprint": ANCIENT_ADAPTER_HASHES[route_id] if replacement else None,
    }
    selected_option = option or make_ancient_option(
        "take-the-road", "PROOF_ANCIENT_TAKE_THE_ROAD"
    )
    required = set()
    all_options = [selected_option]
    for page in pages or []:
        all_options.extend(page["options"])
    for item in all_options:
        if item["next"]["kind"] == "finish":
            required.add("ancient.flow.finish")
        elif item["next"]["kind"] == "page":
            required.add("ancient.flow.set-state")
    if required:
        route["dependencies"] = [
            {"id": adapter_id, "fingerprint": ANCIENT_ADAPTER_HASHES[adapter_id]}
            for adapter_id in sorted(required)
        ]
    target = next(model for model in catalog["models"] if model["id"] == "EVENT.DARV")
    return {
        "order": index,
        "operation_id": f"ancient.route-{index}",
        "target_model_id": target["id"],
        "mode": "replace" if replacement else "compose",
        "surface": "ancient.initial_options",
        "route": route,
        "expected_baseline": {
            "category": target["category"],
            "type": target["type"],
            "content_kind": target["content_kind"],
        },
        "semantics": {
            "condition": {
                "kind": "character",
                "parameters": {"model": vanilla_ref("CHARACTER.PROOF")},
            },
            "multiplayer": "singleplayer",
            "options": [selected_option],
            "pages": pages or [],
            "priority": 0,
            "skip_duplicate_text_keys": not replacement,
        },
    }


def make_visual_operation(
    catalog: dict,
    route_id: str,
    *,
    index: int = 0,
    required: bool = True,
) -> dict:
    route = overrides.PUBLIC_VISUAL_ROUTES[route_id]
    target = next(
        model
        for model in catalog["models"]
        if model["category"] == route["category"]
        and (
            route["content_kind"] is None
            or model["content_kind"] == route["content_kind"]
        )
    )
    suffix = {
        "compressed_texture": ".png",
        "material": ".tres",
        "packed_scene": ".tscn",
        "resource": ".png",
        "spine_resource": ".json",
        "texture": ".png",
    }
    resource_kind = route["resource_kind"]
    path = f"res://Proof/visual/{index}-{route_id.replace('.', '-')}"
    if resource_kind != "directory":
        path += suffix[resource_kind]
    resource = {"kind": resource_kind, "path": path, "required": required}
    semantics = (
        {"resource": resource}
        if route["cardinality"] == "one"
        else {
            "resources": [
                resource,
                {
                    "kind": resource_kind,
                    "path": path.replace(suffix[resource_kind], f"-second{suffix[resource_kind]}"),
                    "required": required,
                },
            ]
        }
    )
    return {
        "order": index,
        "operation_id": f"visual.route-{index}",
        "target_model_id": target["id"],
        "mode": "visual",
        "surface": route["surface"],
        "route": {"class": "public", "id": route_id, "fingerprint": None},
        "expected_baseline": {
            "category": target["category"],
            "type": target["type"],
            "content_kind": target["content_kind"],
        },
        "semantics": semantics,
    }


class VanillaOverrideCatalogTests(unittest.TestCase):
    def test_merge_and_catalog_digest_are_deterministic(self) -> None:
        runtime, assembly = collector_snapshots()
        first = overrides.merge_catalogs(runtime, assembly)
        second = overrides.merge_catalogs(copy.deepcopy(runtime), copy.deepcopy(assembly))

        self.assertEqual(first, second)
        self.assertEqual(first["catalog_sha256"], overrides.catalog_digest(first))
        self.assertEqual(
            ["CARD.LOST_WISP", "RELIC.LOST_WISP"],
            [model["id"] for model in first["models"]],
        )

    def test_maintainer_merge_promotes_sorted_unique_packages_and_rehashes(self) -> None:
        runtime, assembly = collector_snapshots()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            runtime_path = root / "runtime.json"
            assembly_path = root / "assembly.json"
            output_path = root / "catalog.json"
            runtime_path.write_text(json.dumps(runtime), encoding="utf-8")
            assembly_path.write_text(json.dumps(assembly), encoding="utf-8")

            collector.merge(
                runtime_path,
                assembly_path,
                output_path,
                [
                    overrides.ANCIENT_OVERRIDE_FAMILY,
                    overrides.PUBLIC_CARD_OVERRIDE_FAMILY,
                    overrides.ANCIENT_OVERRIDE_FAMILY,
                    overrides.PUBLIC_VISUAL_OVERRIDE_FAMILY,
                ],
            )

            catalog = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(
                sorted(
                    {
                        overrides.PUBLIC_CARD_OVERRIDE_FAMILY,
                        overrides.PUBLIC_VISUAL_OVERRIDE_FAMILY,
                        overrides.ANCIENT_OVERRIDE_FAMILY,
                    }
                ),
                catalog["authorable_route_families"],
            )
            self.assertEqual(catalog["catalog_sha256"], overrides.catalog_digest(catalog))

    def test_non_card_adapter_targets_are_deterministic_and_complete(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = root / "first.json"
            second = root / "second.json"
            collector.generate_non_card_adapter_targets(
                overrides.default_catalog_path(), first
            )
            collector.generate_non_card_adapter_targets(
                overrides.default_catalog_path(), second
            )

            self.assertEqual(first.read_bytes(), second.read_bytes())
            document = json.loads(first.read_text(encoding="utf-8"))
            targets = document["targets"]
            non_card = [target for target in targets if target["id"].startswith("non-card.")]
            self.assertEqual("skillthespire.sts2.adapter-targets/v1", document["schema"])
            self.assertEqual(4165, len(targets))
            self.assertEqual(4145, len(non_card))
            self.assertEqual(
                [target["id"] for target in targets],
                sorted(target["id"] for target in targets),
            )
            self.assertEqual(len(targets), len({target["id"] for target in targets}))
            self.assertTrue(
                all(
                    set(target) == {"id", "method", "signature_label", "type"}
                    for target in non_card
                )
            )
            self.assertLessEqual(
                {
                    "non-card.event.flow.finish",
                    "non-card.event.flow.set-state",
                    "non-card.owner-hook-stream.combat",
                    "non-card.owner-hook-stream.run",
                },
                {target["id"] for target in non_card},
            )

    def test_checked_real_catalog_has_pinned_host_identity(self) -> None:
        catalog = overrides.load_catalog()

        self.assertEqual("0.107.1", catalog["host_version"])
        self.assertEqual("0.6.7", catalog["framework_version"])
        self.assertEqual(
            "a1f9e653f1e28e4076558fee1e60d218619cb7e057b887c6417f62c62c6d7a52",
            catalog["assembly"]["sha256"],
        )
        self.assertEqual(1624, len(catalog["models"]))
        self.assertEqual(3883, catalog["assembly"]["model_namespace_type_count"])
        self.assertEqual(LOCALIZATION_LANGUAGES, catalog["localization_languages"])
        self.assertEqual(
            "c56bbcf3ac07f06e8644b43e536f6180c20b3d318f742ef7945a73eeb1f6791f",
            catalog["catalog_sha256"],
        )
        adapter_hashes = {
            adapter["id"]: adapter["il_sha256"] for adapter in catalog["adapters"]
        }
        self.assertEqual(4165, len(adapter_hashes))
        self.assertLessEqual(
            (ANCIENT_ADAPTER_HASHES | AVAILABILITY_ADAPTER_HASHES).items(),
            adapter_hashes.items(),
        )
        self.assertEqual(
            [
                overrides.PUBLIC_CARD_OVERRIDE_FAMILY,
                overrides.PUBLIC_VISUAL_OVERRIDE_FAMILY,
                overrides.ANCIENT_OVERRIDE_FAMILY,
                overrides.AVAILABILITY_OVERRIDE_FAMILY,
                overrides.NON_CARD_OVERRIDE_FAMILY,
            ],
            catalog["authorable_route_families"],
        )
        self.assertEqual(57, len(overrides.VANILLA_EPOCH_IDS))
        self.assertEqual(
            {6},
            {
                len(dependencies)
                for dependencies in overrides.AVAILABILITY_EPOCH_ADAPTER_DEPENDENCIES.values()
            },
        )
        for category, pool_order in overrides.VANILLA_POOL_ORDER.items():
            with self.subTest(pool_order=category):
                catalog_pool_ids = {
                    model["id"]
                    for model in catalog["models"]
                    if model["category"] == f"{category}_POOL"
                }
                non_debug_pool_ids = {
                    model["id"]
                    for model in catalog["models"]
                    if model["category"] == f"{category}_POOL" and not model["is_debug"]
                }
                self.assertEqual(len(pool_order), len(set(pool_order)))
                self.assertLessEqual(non_debug_pool_ids, set(pool_order))
                self.assertLessEqual(set(pool_order), catalog_pool_ids)
        title_models = [model for model in catalog["models"] if model["title_localization"]]
        self.assertEqual(1580, len(title_models))
        self.assertEqual(
            1537,
            sum("zhs" in model["title_localization"]["localized_titles"] for model in title_models),
        )
        strike = next(model for model in catalog["models"] if model["id"] == "CARD.STRIKE_IRONCLAD")
        self.assertEqual("cards", strike["title_localization"]["table"])
        self.assertEqual("STRIKE_IRONCLAD.title", strike["title_localization"]["key"])
        self.assertEqual("Strike", strike["title_localization"]["localized_titles"]["eng"])
        self.assertEqual("打击", strike["title_localization"]["localized_titles"]["zhs"])
        self.assertEqual(
            "CARD.DEMON_FORM",
            overrides.resolve_model(catalog, "恶魔形态", category="card")["id"],
        )
        with self.assertRaisesRegex(overrides.VanillaOverrideError, "ambiguous vanilla target"):
            overrides.resolve_model(catalog, "打击", category="card")

    def test_alias_resolution_is_exact_and_ambiguity_fails(self) -> None:
        catalog = make_catalog()

        with self.assertRaisesRegex(overrides.VanillaOverrideError, "ambiguous vanilla target"):
            overrides.resolve_model(catalog, "lost wisp")
        with self.assertRaisesRegex(overrides.VanillaOverrideError, "ambiguous vanilla target"):
            overrides.resolve_model(catalog, "迷失幽火")
        resolved = overrides.resolve_model(catalog, "lost wisp", category="card")
        self.assertEqual("CARD.LOST_WISP", resolved["id"])
        localized = overrides.resolve_model(catalog, "迷失幽火", category="relic")
        self.assertEqual("RELIC.LOST_WISP", localized["id"])
        self.assertEqual("relics", localized["title_localization"]["table"])

    def test_unknown_alias_reports_close_catalog_suggestions(self) -> None:
        with self.assertRaisesRegex(
            overrides.VanillaOverrideError,
            r"unknown vanilla target.*Suggestions:.*LOST_WISP",
        ):
            overrides.resolve_model(make_catalog(), "lost wis", category="card")

    def test_descriptions_attach_without_changing_catalog_identity(self) -> None:
        catalog = make_catalog()
        tables = {
            "eng": {
                "cards": {"LOST_WISP.description": "Draw {Cards} card."},
                "relics": {"LOST_WISP.description": "Gain 1 Energy."},
            },
            "zhs": {"cards": {"LOST_WISP.description": "抽{Cards}张牌。"}},
        }

        updated, attached = collector.attach_descriptions(catalog, tables)

        self.assertEqual(2, attached)
        self.assertEqual(catalog["catalog_sha256"], updated["catalog_sha256"])
        self.assertEqual(catalog["catalog_sha256"], overrides.catalog_digest(updated))
        card = overrides.resolve_model(updated, "迷失幽火", category="card")
        self.assertEqual(
            {"eng": "Draw {Cards} card.", "zhs": "抽{Cards}张牌。"},
            card["description_localization"]["localized_descriptions"],
        )
        keys = list(card)
        self.assertEqual(keys.index("title_localization") + 1, keys.index("description_localization"))
        relic = overrides.resolve_model(updated, "迷失幽火", category="relic")
        self.assertEqual(
            {"eng": "Gain 1 Energy."},
            relic["description_localization"]["localized_descriptions"],
        )
        self.assertEqual(updated, collector.attach_descriptions(updated, tables)[0])

    def test_description_localization_accepts_only_nonempty_eng_and_zhs(self) -> None:
        updated, _ = collector.attach_descriptions(
            make_catalog(), {"eng": {"cards": {"LOST_WISP.description": "Draw."}}, "zhs": {}}
        )
        for language, text in (("deu", "Ziehe."), ("eng", " ")):
            broken = copy.deepcopy(updated)
            broken["models"][0]["description_localization"]["localized_descriptions"] = {
                language: text
            }
            with self.assertRaises(overrides.VanillaOverrideError):
                overrides.validate_catalog(broken)

    def test_checked_real_catalog_carries_bilingual_rules_text(self) -> None:
        catalog = overrides.load_catalog()

        bash = overrides.resolve_model(catalog, "痛击", category="card")
        descriptions = bash["description_localization"]["localized_descriptions"]
        self.assertIn("{Damage:diff()}", descriptions["eng"])
        self.assertIn("易伤", descriptions["zhs"])
        for model in catalog["models"]:
            if model["category"] in {"RELIC", "POTION"} and not model["is_debug"]:
                record = model.get("description_localization")
                self.assertIsNotNone(record, model["id"])
                self.assertEqual({"eng", "zhs"}, set(record["localized_descriptions"]), model["id"])

    def test_wrong_profile_hash_and_collector_hash_fail_closed(self) -> None:
        catalog = make_catalog()
        wrong_profile = copy.deepcopy(catalog)
        wrong_profile["profile"] = "ritsulib-wrong"
        with self.assertRaisesRegex(overrides.VanillaOverrideError, "profile must be"):
            overrides.validate_catalog(wrong_profile)

        drifted = copy.deepcopy(catalog)
        drifted["models"][0]["properties"]["rarity"] = "Rare"
        with self.assertRaisesRegex(overrides.VanillaOverrideError, "catalog digest drift"):
            overrides.validate_catalog(drifted)

        runtime, assembly = collector_snapshots()
        runtime["assembly_sha256"] = "b" * 64
        with self.assertRaisesRegex(overrides.VanillaOverrideError, "different sts2.dll hashes"):
            overrides.merge_catalogs(runtime, assembly)


class VanillaOverrideManifestTests(unittest.TestCase):
    def test_empty_manifest_is_valid_and_nonempty_requires_promoted_package(self) -> None:
        catalog = make_catalog()
        empty = overrides.create_empty_manifest("Proof", catalog)
        summary = overrides.validate_override_manifest(empty, catalog, expected_mod_id="Proof")
        self.assertIn("operations=0", summary)

        nonempty = manifest_with(catalog, [make_operation(0, "card.rarity")])
        with self.assertRaisesRegex(overrides.VanillaOverrideError, "requires authorable route family"):
            overrides.validate_override_manifest(nonempty, catalog)

        promoted = enable_card_family(catalog)
        nonempty = manifest_with(promoted, [make_operation(0, "card.rarity")])
        summary = overrides.validate_override_manifest(nonempty, promoted)
        self.assertIn("operations=1", summary)

    def test_manifest_host_catalog_and_expected_baseline_drift_fail(self) -> None:
        catalog = make_catalog()
        wrong_host = overrides.create_empty_manifest("Proof", catalog)
        wrong_host["host_version"] = "0.999.0"
        with self.assertRaisesRegex(overrides.VanillaOverrideError, "host_version must be"):
            overrides.validate_override_manifest(wrong_host, catalog)

        wrong_digest = overrides.create_empty_manifest("Proof", catalog)
        wrong_digest["catalog_sha256"] = "b" * 64
        with self.assertRaisesRegex(overrides.VanillaOverrideError, "catalog digest"):
            overrides.validate_override_manifest(wrong_digest, catalog)

        operation = make_operation(0, "card.rarity")
        operation["expected_baseline"]["properties"]["rarity"] = "Rare"
        with self.assertRaisesRegex(overrides.VanillaOverrideError, "baseline drift"):
            overrides.validate_override_manifest(
                manifest_with(catalog, [operation]),
                catalog,
                allow_unlisted_operations=True,
            )

    def test_unknown_target_and_duplicate_operation_ids_fail(self) -> None:
        catalog = make_catalog()
        unknown = make_operation(0, "card.unknown", target="CARD.DOES_NOT_EXIST")
        with self.assertRaisesRegex(overrides.VanillaOverrideError, "unknown ModelId"):
            overrides.validate_override_manifest(
                manifest_with(catalog, [unknown]),
                catalog,
                allow_unlisted_operations=True,
            )

        duplicate = [make_operation(0, "card.same"), make_operation(1, "card.same")]
        with self.assertRaisesRegex(overrides.VanillaOverrideError, "duplicate operation id"):
            overrides.validate_override_manifest(
                manifest_with(catalog, duplicate),
                catalog,
                allow_unlisted_operations=True,
            )

    def test_exclusive_sets_conflict_but_ordered_cost_changes_compose(self) -> None:
        catalog = make_catalog()
        conflicting = [
            make_operation(0, "card.set"),
            make_operation(1, "card.second-set"),
        ]
        with self.assertRaisesRegex(overrides.VanillaOverrideError, "conflicting operations"):
            overrides.validate_override_manifest(
                manifest_with(catalog, conflicting),
                catalog,
                allow_unlisted_operations=True,
            )

        def cost_operation(index: int, operation_id: str, adjustment: str, value: int) -> dict:
            operation = make_operation(
                index,
                operation_id,
                surface="card.energy_cost",
                route={"class": "public", "id": "card.cost.energy", "fingerprint": None},
            )
            operation["expected_baseline"]["properties"] = {
                "energy_cost": 1,
                "energy_cost_x": False,
            }
            operation["semantics"] = {"adjustment": adjustment, "value": value}
            return operation

        deltas = [
            cost_operation(0, "card.delta-one", "delta", -1),
            cost_operation(1, "card.delta-two", "delta", 2),
        ]
        summary = overrides.validate_override_manifest(
            manifest_with(catalog, deltas),
            catalog,
            allow_unlisted_operations=True,
        )
        self.assertIn("operations=2", summary)

        set_then_delta = [
            cost_operation(0, "card.set-cost", "set", 0),
            cost_operation(1, "card.raise-cost", "delta", 1),
        ]
        self.assertIn(
            "operations=2",
            overrides.validate_override_manifest(
                manifest_with(catalog, set_then_delta),
                catalog,
                allow_unlisted_operations=True,
            ),
        )

        delta_then_set = [
            cost_operation(0, "card.lower-cost", "delta", -1),
            cost_operation(1, "card.set-after-delta", "set", 2),
        ]
        with self.assertRaisesRegex(overrides.VanillaOverrideError, "set followed by deltas"):
            overrides.validate_override_manifest(
                manifest_with(catalog, delta_then_set),
                catalog,
                allow_unlisted_operations=True,
            )

    def test_public_card_family_accepts_the_grounded_contributor_surface(self) -> None:
        catalog = enable_card_family(make_catalog())
        card = next(model for model in catalog["models"] if model["id"] == "CARD.LOST_WISP")

        def operation(
            index: int,
            operation_id: str,
            route_id: str,
            surface: str,
            mode: str,
            semantics: dict,
            properties: dict | None = None,
            *,
            title: bool = False,
        ) -> dict:
            baseline = {
                "category": "CARD",
                "type": card["type"],
            }
            if properties is not None:
                baseline["properties"] = properties
            if title:
                baseline["title_localization"] = card["title_localization"]
            return {
                "order": index,
                "operation_id": operation_id,
                "target_model_id": card["id"],
                "mode": mode,
                "surface": surface,
                "route": {"class": "public", "id": route_id, "fingerprint": None},
                "expected_baseline": baseline,
                "semantics": semantics,
            }

        always = {"kind": "always", "parameters": {}}
        loc = {"table": "cards", "key": "PROOF_MODEL_CAPABILITY_OVERRIDE.fragment"}
        operations = [
            operation(
                0,
                "card.type",
                "card.property.type",
                "card.type",
                "adjust",
                {"adjustment": "set", "value": "Power"},
                {"card_type": "Skill"},
            ),
            operation(
                1,
                "card.tags",
                "card.property.tags",
                "card.tags",
                "compose",
                {"action": "append", "values": ["Strike", "Shiv"]},
                {"tags": []},
            ),
            operation(
                2,
                "card.energy",
                "card.cost.energy",
                "card.energy_cost",
                "adjust",
                {"adjustment": "set", "value": 0},
                {"energy_cost": 1, "energy_cost_x": False},
            ),
            operation(
                3,
                "card.can-play",
                "card.play-state.can-play",
                "card.playability",
                "availability",
                {"decision": False, "when": always},
                {"energy_cost": 1, "star_cost": -1, "target_type": "Self"},
            ),
            operation(
                4,
                "card.result",
                "card.play-result.pile",
                "card.result_pile",
                "adjust",
                {"pile": {"kind": "vanilla", "value": "Exhaust"}},
            ),
            operation(
                5,
                "card.title-prefix",
                "card.title.fragments",
                "card.title",
                "compose",
                {"localization": loc, "placement": "before_base"},
                title=True,
            ),
            operation(
                6,
                "card.description",
                "card.description.fragments",
                "card.description",
                "compose",
                {"localization": loc, "placement": "after_base"},
                title=True,
            ),
            operation(
                7,
                "card.type-text",
                "card.type-text",
                "card.type_text",
                "compose",
                {"composition": "wrap", "localization": loc},
                title=True,
            ),
            operation(
                8,
                "card.hover-tip",
                "card.hover-tips",
                "card.hover_tips",
                "compose",
                {
                    "tip": {
                        "kind": "localized",
                        "title": {"table": "static_hover_tips", "key": "proof.title"},
                        "description": {
                            "table": "static_hover_tips",
                            "key": "proof.description",
                        },
                    }
                },
            ),
            operation(
                9,
                "card.gold-glow",
                "card.glow.gold",
                "card.glow.gold",
                "visual",
                {"when": always},
            ),
            operation(
                10,
                "card.variables",
                "card.capability.dynamic-vars",
                "card.capability_variables",
                "compose",
                {
                    "variables": [
                        {
                            "name": "BonusBlock",
                            "kind": "block",
                            "base_value": 3,
                            "upgrade_delta": 2,
                            "power": None,
                        }
                    ]
                },
                {"dynamic_vars": card["properties"]["dynamic_vars"], "max_upgrade_level": 1},
            ),
            operation(
                11,
                "card.before-play",
                "card.play.on-play",
                "card.on_play",
                "compose",
                {
                    "timing": "before",
                    "run_after_replacement": False,
                    "effects": [
                        {
                            "kind": "block",
                            "amount": {"source": "capability_var", "value": "BonusBlock"},
                            "target": "owner",
                        }
                    ],
                },
            ),
            operation(
                12,
                "card.on-draw",
                "card.owner-hooks",
                "card.owner_hooks",
                "compose",
                {
                    "trigger": "after_owner_drawn",
                    "when": always,
                    "effects": [
                        {
                            "kind": "draw",
                            "amount": {"source": "literal", "value": 1},
                            "target": "owner",
                        }
                    ],
                },
            ),
        ]

        summary = overrides.validate_override_manifest(manifest_with(catalog, operations), catalog)
        self.assertIn("operations=13", summary)

    def test_non_card_owner_hooks_cover_effect_numeric_decision_and_complete_replace(self) -> None:
        catalog = overrides.load_catalog()
        always = {"kind": "always", "parameters": {}}
        effect = make_non_card_operation(
            catalog,
            "RELIC.AKABEKO",
            "behavior.relic.owner-hooks",
            index=0,
            mode="compose",
            route_class="public",
            semantics={
                "multiplayer": "singleplayer",
                "rule": {
                    "kind": "effect",
                    "hook": "after_side_turn_start",
                    "order": -10,
                    "scope": "owner_side",
                    "when": always,
                    "effects": [
                        {
                            "kind": "block",
                            "amount": {"source": "literal", "value": 3},
                            "target": "owner",
                        }
                    ],
                },
            },
        )
        numeric = make_non_card_operation(
            catalog,
            "POWER.STRENGTH_POWER",
            "behavior.power.owner-hooks",
            index=1,
            mode="compose",
            route_class="public",
            semantics={
                "multiplayer": "singleplayer",
                "rule": {
                    "kind": "numeric",
                    "hook": "modify_damage_additive",
                    "order": 0,
                    "scope": "owner",
                    "when": always,
                    "adjustment": "delta",
                    "value": 2,
                },
            },
        )
        decision = make_non_card_operation(
            catalog,
            "MONSTER.AEONGLASS",
            "behavior.monster.owner-hooks",
            index=2,
            mode="compose",
            route_class="public",
            semantics={
                "multiplayer": "singleplayer",
                "rule": {
                    "kind": "decision",
                    "hook": "should_die",
                    "order": 5,
                    "scope": "owner",
                    "when": always,
                    "decision": False,
                },
            },
        )
        replacement = make_non_card_operation(
            catalog,
            "POTION.BLOCK_POTION",
            "behavior.potion.owner-hooks",
            index=3,
            mode="replace",
            route_class="adapter",
            dependencies=(
                "non-card.owner-hook-stream.combat",
                "non-card.owner-hook-stream.run",
            ),
            semantics={
                "complete": True,
                "multiplayer": "singleplayer",
                "rules": [],
            },
        )
        self.assertIn(
            "operations=4",
            overrides.validate_override_manifest(
                manifest_with(catalog, [effect, numeric, decision, replacement]), catalog
            ),
        )

        conflict = copy.deepcopy(effect)
        conflict["order"] = 1
        conflict["operation_id"] = "non-card.replace-conflict"
        conflict["mode"] = "replace"
        conflict["route"]["class"] = "adapter"
        conflict["route"]["dependencies"] = adapter_dependencies(
            catalog,
            "non-card.owner-hook-stream.combat",
            "non-card.owner-hook-stream.run",
        )
        conflict["semantics"] = {
            "complete": True,
            "multiplayer": "singleplayer",
            "rules": [],
        }
        with self.assertRaisesRegex(overrides.VanillaOverrideError, "conflicting operations"):
            overrides.validate_override_manifest(manifest_with(catalog, [effect, conflict]), catalog)

        undeclared_variable = copy.deepcopy(effect)
        undeclared_variable["semantics"]["rule"]["effects"][0]["amount"] = {
            "source": "capability_var",
            "value": "Amount",
        }
        with self.assertRaisesRegex(overrides.VanillaOverrideError, "literal, owner_var"):
            overrides.validate_override_manifest(
                manifest_with(catalog, [undeclared_variable]), catalog
            )

    def test_non_card_data_routes_cover_all_cataloged_fields(self) -> None:
        catalog = overrides.load_catalog()
        cases = [
            ("RELIC.AKABEKO", "data.relic.rarity", "set", "Rare"),
            ("POTION.BLOCK_POTION", "data.potion.rarity", "set", "Uncommon"),
            ("POTION.BLOCK_POTION", "data.potion.target-type", "set", "AnyEnemy"),
            ("POTION.BLOCK_POTION", "data.potion.usage", "set", "AnyTime"),
            ("POWER.STRENGTH_POWER", "data.power.allow-negative", "set", True),
            ("POWER.STRENGTH_POWER", "data.power.type", "set", "Debuff"),
            ("POWER.STRENGTH_POWER", "data.power.scales-in-multiplayer", "set", True),
            ("POWER.STRENGTH_POWER", "data.power.stack-type", "set", "Single"),
            ("ENCHANTMENT.ADROIT", "data.enchantment.stackable", "set", True),
            ("AFFLICTION.BOUND", "data.affliction.can-afflict-unplayable", "set", False),
            ("AFFLICTION.BOUND", "data.affliction.stackable", "set", True),
            ("MONSTER.AEONGLASS", "data.monster.max-initial-hp", "set", 500),
            ("MONSTER.AEONGLASS", "data.monster.min-initial-hp", "delta", -10),
            ("MONSTER.AEONGLASS", "data.monster.show-in-compendium", "set", False),
            ("ENCOUNTER.AEONGLASS_BOSS", "data.encounter.is-weak", "set", True),
            ("ENCOUNTER.AEONGLASS_BOSS", "data.encounter.room-type", "set", "Elite"),
        ]
        operations = []
        for index, (target, route_id, adjustment, value) in enumerate(cases):
            contract = overrides._NON_CARD_DATA_ROUTES[route_id]
            adapter_id = (
                f"non-card.{target.lower().replace('_', '-')}.{contract['adapter']}"
            )
            operations.append(
                make_non_card_operation(
                    catalog,
                    target,
                    route_id,
                    index=index,
                    mode="adjust",
                    route_class="adapter",
                    dependencies=(adapter_id,),
                    semantics={
                        "adjustment": adjustment,
                        "multiplayer": "singleplayer",
                        "value": value,
                    },
                )
            )
        self.assertIn(
            "operations=16",
            overrides.validate_override_manifest(manifest_with(catalog, operations), catalog),
        )

    def test_non_card_complete_lifecycle_and_body_routes_cover_nine_families(self) -> None:
        catalog = overrides.load_catalog()
        empty_effect = {"complete": True, "multiplayer": "singleplayer"}
        event_option = make_ancient_option(
            "leave", "PROOF_EVENT_LEAVE", next_step={"kind": "finish"}
        )
        event_option.update(
            {
                "cost": {"kind": "none", "amount": 0, "allow_lethal": False},
                "enabled_when": {"kind": "always", "parameters": {}},
                "hover_tips": [],
                "relic": None,
            }
        )
        cases = [
            (
                "RELIC.AKABEKO",
                "behavior.relic.lifecycle",
                {**empty_effect, "after_obtained": [], "after_removed": []},
            ),
            (
                "POTION.BLOCK_POTION",
                "behavior.potion.use",
                {**empty_effect, "effects": []},
            ),
            (
                "POWER.STRENGTH_POWER",
                "behavior.power.lifecycle",
                {**empty_effect, "before_applied": [], "after_applied": [], "after_removed": []},
            ),
            (
                "ORB.FROST_ORB",
                "behavior.orb.lifecycle",
                {**empty_effect, "before_turn_end": [], "after_turn_start": [], "passive": [], "evoke": []},
            ),
            (
                "ENCHANTMENT.ADROIT",
                "behavior.enchantment.on-play",
                {**empty_effect, "effects": []},
            ),
            (
                "AFFLICTION.BOUND",
                "behavior.affliction.lifecycle",
                {**empty_effect, "after_applied": [], "before_removed": [], "on_play": []},
            ),
            (
                "MONSTER.AEONGLASS",
                "behavior.monster.moves",
                {
                    **empty_effect,
                    "initial_state": "STRIKE",
                    "states": [
                        {
                            "kind": "move",
                            "id": "STRIKE",
                            "intents": [{"kind": "attack", "amount": 7}],
                            "effects": [
                                {
                                    "kind": "attack",
                                    "amount": {"source": "literal", "value": 7},
                                    "target": "all_enemies",
                                }
                            ],
                            "next": "STRIKE",
                        }
                    ],
                },
            ),
            (
                "ENCOUNTER.AEONGLASS_BOSS",
                "behavior.encounter.monsters",
                {
                    **empty_effect,
                    "monsters": [
                        {"model": vanilla_ref("MONSTER.AEONGLASS"), "slot": None}
                    ],
                },
            ),
            (
                "EVENT.THE_ARCHITECT",
                "behavior.event.options",
                {
                    **empty_effect,
                    "condition": {"kind": "always", "parameters": {}},
                    "options": [event_option],
                    "pages": [],
                },
            ),
        ]
        operations = []
        for index, (target, route_id, semantics) in enumerate(cases):
            _, suffixes = overrides._NON_CARD_LIFECYCLE_ROUTES[route_id]
            prefix = f"non-card.{target.lower().replace('_', '-')}"
            dependencies = [f"{prefix}.{suffix}" for suffix in suffixes]
            if route_id == "behavior.event.options":
                dependencies.append("non-card.event.flow.finish")
            operations.append(
                make_non_card_operation(
                    catalog,
                    target,
                    route_id,
                    index=index,
                    mode="replace",
                    route_class="adapter",
                    dependencies=tuple(dependencies),
                    semantics=semantics,
                )
            )
        self.assertIn(
            "operations=9",
            overrides.validate_override_manifest(manifest_with(catalog, operations), catalog),
        )

        invalid_affliction = copy.deepcopy(operations[5])
        invalid_affliction["order"] = 0
        invalid_affliction["semantics"]["after_applied"] = [
            {
                "kind": "gain_energy",
                "amount": {"source": "literal", "value": 1},
                "target": "owner",
            }
        ]
        with self.assertRaisesRegex(
            overrides.VanillaOverrideError, "pinned Affliction callback is synchronous"
        ):
            overrides.validate_override_manifest(
                manifest_with(catalog, [invalid_affliction]), catalog
            )

    def test_non_card_routes_fail_closed_on_package_category_and_fingerprint_drift(self) -> None:
        catalog = overrides.load_catalog()
        contract = overrides._NON_CARD_DATA_ROUTES["data.relic.rarity"]
        operation = make_non_card_operation(
            catalog,
            "RELIC.AKABEKO",
            "data.relic.rarity",
            mode="adjust",
            route_class="adapter",
            dependencies=(
                f"non-card.relic.akabeko.{contract['adapter']}",
            ),
            semantics={"adjustment": "set", "multiplayer": "singleplayer", "value": "Rare"},
        )
        drift = copy.deepcopy(operation)
        drift["route"]["dependencies"][0]["fingerprint"] = "f" * 64
        with self.assertRaisesRegex(overrides.VanillaOverrideError, "fingerprint drift"):
            overrides.validate_override_manifest(manifest_with(catalog, [drift]), catalog)

        wrong_category = copy.deepcopy(operation)
        wrong_category["target_model_id"] = "POTION.BLOCK_POTION"
        potion = next(model for model in catalog["models"] if model["id"] == "POTION.BLOCK_POTION")
        wrong_category["expected_baseline"] = {
            "category": potion["category"],
            "type": potion["type"],
            "properties": {"rarity": potion["properties"]["rarity"]},
        }
        with self.assertRaisesRegex(overrides.VanillaOverrideError, "requires a RELIC target"):
            overrides.validate_override_manifest(manifest_with(catalog, [wrong_category]), catalog)

        unlisted = copy.deepcopy(catalog)
        unlisted["authorable_route_families"].remove(overrides.NON_CARD_OVERRIDE_FAMILY)
        unlisted["catalog_sha256"] = overrides.catalog_digest(unlisted)
        unlisted_operation = copy.deepcopy(operation)
        with self.assertRaisesRegex(overrides.VanillaOverrideError, "requires authorable route family"):
            overrides.validate_override_manifest(
                manifest_with(unlisted, [unlisted_operation]), unlisted
            )

    def test_availability_public_epoch_route_covers_grounded_vanilla_hosts(self) -> None:
        catalog = make_availability_catalog()
        operations = [
            make_availability_epoch_operation(catalog, "CARD.LOST_WISP", index=0),
            make_availability_epoch_operation(catalog, "CHARACTER.PROOF", index=1),
            make_availability_epoch_operation(catalog, "EVENT.ORDINARY", index=2),
            make_availability_epoch_operation(catalog, "EVENT.DARV", index=3),
        ]
        self.assertIn(
            "operations=4",
            overrides.validate_override_manifest(manifest_with(catalog, operations), catalog),
        )

        unlisted = copy.deepcopy(catalog)
        unlisted["authorable_route_families"] = []
        unlisted["catalog_sha256"] = overrides.catalog_digest(unlisted)
        operation = make_availability_epoch_operation(unlisted, "CARD.LOST_WISP")
        with self.assertRaisesRegex(overrides.VanillaOverrideError, "requires authorable route family"):
            overrides.validate_override_manifest(
                manifest_with(unlisted, [operation]), unlisted
            )

        act_ancient = make_availability_epoch_operation(catalog, "EVENT.NEOW")
        with self.assertRaisesRegex(overrides.VanillaOverrideError, "shared Darv only"):
            overrides.validate_override_manifest(
                manifest_with(catalog, [act_ancient]), catalog
            )

        relic = make_availability_epoch_operation(catalog, "RELIC.LOST_WISP")
        with self.assertRaisesRegex(overrides.VanillaOverrideError, "shared Darv only"):
            overrides.validate_override_manifest(manifest_with(catalog, [relic]), catalog)

        disabled = make_availability_epoch_operation(
            catalog, "CARD.LOST_WISP", state="disabled"
        )
        with self.assertRaisesRegex(overrides.VanillaOverrideError, "permanent disable"):
            overrides.validate_override_manifest(
                manifest_with(catalog, [disabled]), catalog
            )

        unknown_epoch = make_availability_epoch_operation(catalog, "CARD.LOST_WISP")
        unknown_epoch["semantics"]["epoch_id"] = "PROMPT_INVENTED_EPOCH"
        with self.assertRaisesRegex(overrides.VanillaOverrideError, "57 pinned vanilla epochs"):
            overrides.validate_override_manifest(
                manifest_with(catalog, [unknown_epoch]), catalog
            )

    def test_relic_and_potion_epoch_adapters_require_complete_fingerprints(self) -> None:
        catalog = make_availability_catalog()
        relic = make_availability_epoch_operation(
            catalog,
            "RELIC.LOST_WISP",
            route_id="availability.relic.epoch-gate",
        )
        potion = make_availability_epoch_operation(
            catalog,
            "POTION.PROOF",
            index=1,
            route_id="availability.potion.epoch-gate",
            state="disabled",
        )
        self.assertIn(
            "operations=2",
            overrides.validate_override_manifest(
                manifest_with(catalog, [relic, potion]), catalog
            ),
        )

        missing = copy.deepcopy(relic)
        missing["route"]["dependencies"].pop()
        with self.assertRaisesRegex(overrides.VanillaOverrideError, "dependencies must be exactly"):
            overrides.validate_override_manifest(manifest_with(catalog, [missing]), catalog)

        drifted = copy.deepcopy(relic)
        drifted["route"]["dependencies"][0]["fingerprint"] = "f" * 64
        with self.assertRaisesRegex(overrides.VanillaOverrideError, "fingerprint drift"):
            overrides.validate_override_manifest(manifest_with(catalog, [drifted]), catalog)

        invalid_disabled = copy.deepcopy(potion)
        invalid_disabled["order"] = 0
        invalid_disabled["semantics"]["epoch_id"] = "POTION1_EPOCH"
        with self.assertRaisesRegex(overrides.VanillaOverrideError, "requires epoch_id null"):
            overrides.validate_override_manifest(
                manifest_with(catalog, [invalid_disabled]), catalog
            )

    def test_availability_pool_routes_cover_card_relic_and_potion_add(self) -> None:
        catalog = make_availability_catalog()
        operations = [
            make_pool_operation(
                catalog,
                "CARD.LOST_WISP",
                "availability.card.pool-add",
                "add",
                "CARD_POOL.IRONCLAD_CARD_POOL",
                index=0,
                destination="CARD_POOL.IRONCLAD_CARD_POOL",
            ),
            make_pool_operation(
                catalog,
                "RELIC.LOST_WISP",
                "availability.relic.pool-add",
                "add",
                "RELIC_POOL.EVENT_RELIC_POOL",
                index=1,
                destination="RELIC_POOL.EVENT_RELIC_POOL",
            ),
            make_pool_operation(
                catalog,
                "POTION.PROOF",
                "availability.potion.pool-add",
                "add",
                "POTION_POOL.SILENT_POTION_POOL",
                index=2,
                destination="POTION_POOL.SILENT_POTION_POOL",
            ),
        ]
        self.assertIn(
            "operations=3",
            overrides.validate_override_manifest(manifest_with(catalog, operations), catalog),
        )

    def test_pool_membership_sequence_tracks_move_remove_and_primary_pool(self) -> None:
        catalog = make_availability_catalog()
        operations = [
            make_pool_operation(
                catalog,
                "CARD.LOST_WISP",
                "availability.card.pool-add",
                "add",
                "CARD_POOL.IRONCLAD_CARD_POOL",
                index=0,
                destination="CARD_POOL.IRONCLAD_CARD_POOL",
            ),
            make_pool_operation(
                catalog,
                "CARD.LOST_WISP",
                "availability.card.pool-membership",
                "move",
                "CARD_POOL.IRONCLAD_CARD_POOL",
                index=1,
                source="CARD_POOL.COLORLESS_CARD_POOL",
                destination="CARD_POOL.SILENT_CARD_POOL",
            ),
            make_pool_operation(
                catalog,
                "CARD.LOST_WISP",
                "availability.card.pool-membership",
                "remove",
                "CARD_POOL.SILENT_CARD_POOL",
                index=2,
                source="CARD_POOL.IRONCLAD_CARD_POOL",
            ),
        ]
        self.assertIn(
            "operations=3",
            overrides.validate_override_manifest(manifest_with(catalog, operations), catalog),
        )

    def test_pool_membership_rejects_unsafe_or_ambiguous_transitions(self) -> None:
        catalog = make_availability_catalog()
        duplicate = make_pool_operation(
            catalog,
            "CARD.LOST_WISP",
            "availability.card.pool-add",
            "add",
            "CARD_POOL.COLORLESS_CARD_POOL",
            destination="CARD_POOL.COLORLESS_CARD_POOL",
        )
        final_remove = make_pool_operation(
            catalog,
            "CARD.LOST_WISP",
            "availability.card.pool-membership",
            "remove",
            "CARD_POOL.COLORLESS_CARD_POOL",
            source="CARD_POOL.COLORLESS_CARD_POOL",
        )
        missing_source = make_pool_operation(
            catalog,
            "CARD.LOST_WISP",
            "availability.card.pool-membership",
            "move",
            "CARD_POOL.IRONCLAD_CARD_POOL",
            source="CARD_POOL.SILENT_CARD_POOL",
            destination="CARD_POOL.IRONCLAD_CARD_POOL",
        )
        wrong_type = make_pool_operation(
            catalog,
            "CARD.LOST_WISP",
            "availability.card.pool-add",
            "add",
            "RELIC_POOL.EVENT_RELIC_POOL",
            destination="RELIC_POOL.EVENT_RELIC_POOL",
        )
        debug_pool = make_pool_operation(
            catalog,
            "POTION.PROOF",
            "availability.potion.pool-add",
            "add",
            "POTION_POOL.MOCK_POTION_POOL",
            destination="POTION_POOL.MOCK_POTION_POOL",
        )
        wrong_primary = make_pool_operation(
            catalog,
            "CARD.LOST_WISP",
            "availability.card.pool-add",
            "add",
            "CARD_POOL.COLORLESS_CARD_POOL",
            destination="CARD_POOL.IRONCLAD_CARD_POOL",
        )
        cases = [
            (duplicate, "already a membership"),
            (final_remove, "final pool membership"),
            (missing_source, "not a current membership"),
            (wrong_type, "must select a CARD_POOL model"),
            (debug_pool, "rejects debug pool"),
            (wrong_primary, "pinned ModelDb order selects"),
        ]
        for operation, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(overrides.VanillaOverrideError, message):
                    overrides.validate_override_manifest(
                        manifest_with(catalog, [operation]), catalog
                    )

    def test_public_visual_package_accepts_all_44_registry_routes(self) -> None:
        catalog = enable_visual_family(make_visual_catalog())

        self.assertEqual(44, len(overrides.PUBLIC_VISUAL_ROUTES))
        for route_id in overrides.PUBLIC_VISUAL_ROUTES:
            with self.subTest(route=route_id):
                operation = make_visual_operation(catalog, route_id)
                summary = overrides.validate_override_manifest(
                    manifest_with(catalog, [operation]), catalog
                )
                self.assertIn("operations=1", summary)

    def test_public_visual_routes_require_the_package_target_kind_and_visual_mode(self) -> None:
        catalog = make_visual_catalog()
        operation = make_visual_operation(catalog, "visual.relic.icon-path")
        with self.assertRaisesRegex(overrides.VanillaOverrideError, "requires authorable route family"):
            overrides.validate_override_manifest(manifest_with(catalog, [operation]), catalog)

        catalog = enable_visual_family(catalog)
        card = next(model for model in catalog["models"] if model["category"] == "CARD")
        wrong_category = copy.deepcopy(operation)
        wrong_category["target_model_id"] = card["id"]
        wrong_category["expected_baseline"] = {
            key: card[key] for key in ("category", "type", "content_kind")
        }
        with self.assertRaisesRegex(overrides.VanillaOverrideError, "requires a RELIC target"):
            overrides.validate_override_manifest(
                manifest_with(catalog, [wrong_category]), catalog
            )

        ordinary_event = next(
            model
            for model in catalog["models"]
            if model["category"] == "EVENT" and model["content_kind"] == "event"
        )
        wrong_ancient = make_visual_operation(catalog, "visual.ancient.map-icon-path")
        wrong_ancient["target_model_id"] = ordinary_event["id"]
        wrong_ancient["expected_baseline"] = {
            key: ordinary_event[key] for key in ("category", "type", "content_kind")
        }
        with self.assertRaisesRegex(overrides.VanillaOverrideError, "requires content_kind ancient"):
            overrides.validate_override_manifest(
                manifest_with(catalog, [wrong_ancient]), catalog
            )

        wrong_mode = make_visual_operation(catalog, "visual.relic.icon-path")
        wrong_mode["mode"] = "adjust"
        with self.assertRaisesRegex(overrides.VanillaOverrideError, "mode visual"):
            overrides.validate_override_manifest(
                manifest_with(catalog, [wrong_mode]), catalog
            )

    def test_public_visual_resource_paths_fail_closed(self) -> None:
        catalog = enable_visual_family(make_visual_catalog())
        cases = []

        wrong_prefix = make_visual_operation(catalog, "visual.relic.icon-path")
        wrong_prefix["semantics"]["resource"]["path"] = "res://Other/visual/relic.png"
        cases.append((wrong_prefix, "must stay under res://Proof/"))

        backslash = make_visual_operation(catalog, "visual.relic.icon-path")
        backslash["semantics"]["resource"]["path"] = r"res://Proof\visual\relic.png"
        cases.append((backslash, "forward slashes"))

        traversal = make_visual_operation(catalog, "visual.relic.icon-path")
        traversal["semantics"]["resource"]["path"] = "res://Proof/visual/../relic.png"
        cases.append((traversal, "traversal segments"))

        wrong_kind = make_visual_operation(catalog, "visual.relic.icon-path")
        wrong_kind["semantics"]["resource"]["kind"] = "packed_scene"
        cases.append((wrong_kind, "kind must be texture"))

        script = make_visual_operation(catalog, "visual.relic.icon-path")
        script["semantics"]["resource"]["path"] = "res://Proof/visual/relic.gd"
        cases.append((script, "must not select executable or script resource"))

        duplicate = make_visual_operation(
            catalog, "visual.encounter.map-node-asset-paths"
        )
        duplicate["semantics"]["resources"][1]["path"] = duplicate["semantics"][
            "resources"
        ][0]["path"]
        cases.append((duplicate, "must not contain duplicate paths"))

        for operation, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(overrides.VanillaOverrideError, message):
                    overrides.validate_override_manifest(
                        manifest_with(catalog, [operation]), catalog
                    )

    def test_alternative_visual_providers_for_one_surface_conflict(self) -> None:
        catalog = enable_visual_family(make_visual_catalog())
        cases = [
            ("visual.relic.icon-path", "visual.relic.icon-texture"),
            ("visual.event.background-scene-path", "visual.event.background-scene"),
            ("visual.affliction.overlay-path", "visual.affliction.overlay-scene"),
        ]
        for first_route, second_route in cases:
            first = make_visual_operation(catalog, first_route, index=0)
            second = make_visual_operation(catalog, second_route, index=1)
            with self.subTest(routes=(first_route, second_route)):
                with self.assertRaisesRegex(overrides.VanillaOverrideError, "conflicting operations"):
                    overrides.validate_override_manifest(
                        manifest_with(catalog, [first, second]), catalog
                    )

    def test_project_visual_resources_enforce_required_optional_directory_and_list(self) -> None:
        catalog = enable_visual_family(make_visual_catalog())
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            catalog_path = root / "catalog.json"
            catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
            manifest_path = root / overrides.MANIFEST_RELATIVE_PATH
            manifest_path.parent.mkdir(parents=True)

            operation = make_visual_operation(catalog, "visual.relic.icon-path")
            manifest_path.write_text(
                json.dumps(manifest_with(catalog, [operation])), encoding="utf-8"
            )
            with self.assertRaisesRegex(overrides.VanillaOverrideError, "required but missing"):
                overrides.validate_project_override_manifest(
                    root, "Proof", catalog_path=catalog_path
                )

            resource_path = overrides._project_resource_path(
                root, operation["semantics"]["resource"]["path"]
            )
            resource_path.parent.mkdir(parents=True)
            resource_path.write_bytes(b"png")
            self.assertIn(
                "visual_resources=1 required=1 optional_missing=0",
                overrides.validate_project_override_manifest(
                    root, "Proof", catalog_path=catalog_path
                ),
            )

            resource_path.unlink()
            operation["semantics"]["resource"]["required"] = False
            manifest_path.write_text(
                json.dumps(manifest_with(catalog, [operation])), encoding="utf-8"
            )
            self.assertIn(
                "visual_resources=1 required=0 optional_missing=1",
                overrides.validate_project_override_manifest(
                    root, "Proof", catalog_path=catalog_path
                ),
            )

            directory = make_visual_operation(
                catalog, "visual.encounter.background-layers-directory"
            )
            manifest_path.write_text(
                json.dumps(manifest_with(catalog, [directory])), encoding="utf-8"
            )
            directory_path = overrides._project_resource_path(
                root, directory["semantics"]["resource"]["path"]
            )
            directory_path.mkdir(parents=True)
            with self.assertRaisesRegex(overrides.VanillaOverrideError, "direct .tscn"):
                overrides.validate_project_override_manifest(
                    root, "Proof", catalog_path=catalog_path
                )
            (directory_path / "layer.tscn").write_text("[gd_scene]\n", encoding="utf-8")
            self.assertIn(
                "visual_resources=1",
                overrides.validate_project_override_manifest(
                    root, "Proof", catalog_path=catalog_path
                ),
            )

            resource_list = make_visual_operation(
                catalog, "visual.encounter.map-node-asset-paths"
            )
            resource_list["semantics"]["resources"][1]["required"] = False
            manifest_path.write_text(
                json.dumps(manifest_with(catalog, [resource_list])), encoding="utf-8"
            )
            first_path = overrides._project_resource_path(
                root, resource_list["semantics"]["resources"][0]["path"]
            )
            first_path.parent.mkdir(parents=True, exist_ok=True)
            first_path.write_bytes(b"png")
            self.assertIn(
                "visual_resources=2 required=1 optional_missing=1",
                overrides.validate_project_override_manifest(
                    root, "Proof", catalog_path=catalog_path
                ),
            )

    def test_public_card_routes_reject_non_card_targets_and_forbidden_semantics(self) -> None:
        catalog = enable_card_family(make_catalog())
        non_card = make_operation(0, "relic.rarity", target="RELIC.LOST_WISP")
        non_card["expected_baseline"] = {
            "category": "RELIC",
            "type": "MegaCrit.Sts2.Core.Models.Relics.LostWisp",
            "properties": {"rarity": "Common"},
        }
        with self.assertRaisesRegex(overrides.VanillaOverrideError, "requires a CARD target"):
            overrides.validate_override_manifest(manifest_with(catalog, [non_card]), catalog)

        canonical_var = make_operation(0, "card.canonical-var")
        canonical_var["route"]["id"] = "card.canonical.dynamic-var"
        with self.assertRaisesRegex(overrides.VanillaOverrideError, "no authorable route family"):
            overrides.validate_override_manifest(manifest_with(catalog, [canonical_var]), catalog)

    def test_public_card_base_description_replacement_fails_closed(self) -> None:
        catalog = enable_card_family(make_catalog())
        card = next(model for model in catalog["models"] if model["id"] == "CARD.LOST_WISP")
        replacement = make_operation(
            0,
            "card.replace-description",
            surface="card.description",
            mode="replace",
            route={
                "class": "public",
                "id": "card.description.fragments",
                "fingerprint": None,
            },
        )
        replacement["expected_baseline"] = {
            "category": "CARD",
            "type": card["type"],
            "title_localization": card["title_localization"],
        }
        replacement["semantics"] = {
            "localization": {
                "table": "cards",
                "key": "PROOF_MODEL_CAPABILITY_OVERRIDE.description",
            },
            "placement": "after_base",
        }

        with self.assertRaisesRegex(
            overrides.VanillaOverrideError, "base-description replacement is unsupported"
        ):
            overrides.validate_override_manifest(manifest_with(catalog, [replacement]), catalog)

    def test_public_card_behavior_rejects_recursive_or_unbound_semantics(self) -> None:
        catalog = enable_card_family(make_catalog())
        card_type = "MegaCrit.Sts2.Core.Models.Cards.LostWisp"

        playability = {
            "order": 0,
            "operation_id": "card.recursive-playability",
            "target_model_id": "CARD.LOST_WISP",
            "mode": "availability",
            "surface": "card.playability",
            "route": {
                "class": "public",
                "id": "card.play-state.can-play",
                "fingerprint": None,
            },
            "expected_baseline": {
                "category": "CARD",
                "type": card_type,
                "properties": {
                    "energy_cost": 1,
                    "star_cost": -1,
                    "target_type": "Self",
                },
            },
            "semantics": {
                "decision": False,
                "when": {"kind": "playable", "parameters": {}},
            },
        }
        with self.assertRaisesRegex(overrides.VanillaOverrideError, "cannot query playability"):
            overrides.validate_override_manifest(manifest_with(catalog, [playability]), catalog)

        behavior = {
            "order": 0,
            "operation_id": "card.unbound-variable",
            "target_model_id": "CARD.LOST_WISP",
            "mode": "compose",
            "surface": "card.on_play",
            "route": {"class": "public", "id": "card.play.on-play", "fingerprint": None},
            "expected_baseline": {"category": "CARD", "type": card_type},
            "semantics": {
                "timing": "before",
                "run_after_replacement": False,
                "effects": [
                    {
                        "kind": "block",
                        "amount": {"source": "capability_var", "value": "Missing"},
                        "target": "owner",
                    }
                ],
            },
        }
        with self.assertRaisesRegex(overrides.VanillaOverrideError, "unknown capability DynamicVar"):
            overrides.validate_override_manifest(manifest_with(catalog, [behavior]), catalog)

    def test_ancient_append_accepts_multi_option_rules_pages_and_full_outcomes(self) -> None:
        catalog = make_ancient_catalog()
        effects = [
            {"kind": "damage", "amount": 1},
            {"kind": "gain_gold", "amount": 2},
            {"kind": "gain_max_hp", "amount": 3},
            {"kind": "heal", "amount": 4},
            {"kind": "lose_gold", "amount": 5},
            {"kind": "lose_max_hp", "amount": 1},
            {
                "kind": "add_card",
                "model": vanilla_ref("CARD.LOST_WISP"),
                "preview": True,
            },
            {"kind": "obtain_relic", "model": vanilla_ref("RELIC.LOST_WISP")},
            {"kind": "procure_potion", "model": vanilla_ref("POTION.PROOF")},
            {
                "kind": "deck_selection",
                "action": "enchant",
                "amount": 2,
                "count": 1,
                "enchantment": vanilla_ref("ENCHANTMENT.PROOF"),
            },
            {
                "kind": "deck_selection",
                "action": "upgrade",
                "amount": 0,
                "count": 1,
                "enchantment": None,
            },
            {
                "kind": "offer_rewards",
                "rewards": [
                    {"kind": "gold", "amount": 11},
                    {"kind": "card", "model": vanilla_ref("CARD.LOST_WISP")},
                    {"kind": "relic", "model": vanilla_ref("RELIC.LOST_WISP")},
                    {"kind": "potion", "model": vanilla_ref("POTION.PROOF")},
                ],
            },
            {"kind": "screen_shake", "profile": "weak_short"},
        ]
        initial = make_ancient_option(
            "open-gate",
            "PROOF_ANCIENT_OPEN_GATE",
            next_step={"kind": "page", "page": "AFTER_GATE"},
            effects=effects,
        )
        page = {
            "id": "AFTER_GATE",
            "description_key": "PROOF_ANCIENT_AFTER_GATE",
            "options": [
                make_ancient_option(
                    "finish-gate", "PROOF_ANCIENT_FINISH_GATE"
                )
            ],
        }
        operation = make_ancient_operation(
            catalog, option=initial, pages=[page]
        )
        operation["semantics"]["options"].append(
            make_ancient_option(
                "wait-here",
                "PROOF_ANCIENT_WAIT_HERE",
                next_step={"kind": "stay"},
                effects=[],
            )
        )
        operation["semantics"]["condition"] = {
            "kind": "all",
            "conditions": [
                {
                    "kind": "character",
                    "parameters": {"model": vanilla_ref("CHARACTER.PROOF")},
                },
                {
                    "kind": "deck_contains",
                    "parameters": {
                        "minimum": 1,
                        "model": vanilla_ref("CARD.LOST_WISP"),
                    },
                },
                {
                    "kind": "not",
                    "condition": {
                        "kind": "owns_potion",
                        "parameters": {
                            "minimum": 1,
                            "model": vanilla_ref("POTION.PROOF"),
                        },
                    },
                },
            ],
        }
        operation["semantics"]["priority"] = 25

        summary = overrides.validate_override_manifest(
            manifest_with(catalog, [operation]), catalog
        )
        self.assertIn("operations=1", summary)
        self.assertEqual(
            ["ancient.flow.finish", "ancient.flow.set-state"],
            [item["id"] for item in operation["route"]["dependencies"]],
        )

    def test_ancient_replacement_requires_exact_route_and_flow_fingerprints(self) -> None:
        catalog = make_ancient_catalog()
        initial = make_ancient_option(
            "replace-road",
            "PROOF_ANCIENT_REPLACE_ROAD",
            next_step={"kind": "page", "page": "REPLACED"},
        )
        page = {
            "id": "REPLACED",
            "description_key": "PROOF_ANCIENT_REPLACED",
            "options": [
                make_ancient_option("replace-end", "PROOF_ANCIENT_REPLACE_END")
            ],
        }
        operation = make_ancient_operation(
            catalog,
            route_id="ancient.initial-options.replace",
            option=initial,
            pages=[page],
        )
        self.assertIn(
            "operations=1",
            overrides.validate_override_manifest(
                manifest_with(catalog, [operation]), catalog
            ),
        )

        route_drift = copy.deepcopy(operation)
        route_drift["route"]["fingerprint"] = "f" * 64
        with self.assertRaisesRegex(overrides.VanillaOverrideError, "fingerprint drift"):
            overrides.validate_override_manifest(
                manifest_with(catalog, [route_drift]), catalog
            )

        dependency_drift = copy.deepcopy(operation)
        dependency_drift["route"]["dependencies"][0]["fingerprint"] = "f" * 64
        with self.assertRaisesRegex(overrides.VanillaOverrideError, "fingerprint drift"):
            overrides.validate_override_manifest(
                manifest_with(catalog, [dependency_drift]), catalog
            )

        missing_dependency = copy.deepcopy(operation)
        missing_dependency["route"]["dependencies"].pop()
        with self.assertRaisesRegex(overrides.VanillaOverrideError, "must be exactly"):
            overrides.validate_override_manifest(
                manifest_with(catalog, [missing_dependency]), catalog
            )

    def test_ancient_routes_reject_non_ancients_unsupported_flags_and_dead_pages(self) -> None:
        catalog = make_ancient_catalog()
        operation = make_ancient_operation(catalog)
        ordinary = next(model for model in catalog["models"] if model["id"] == "EVENT.ORDINARY")
        wrong_target = copy.deepcopy(operation)
        wrong_target["target_model_id"] = ordinary["id"]
        wrong_target["expected_baseline"] = {
            key: ordinary[key] for key in ("category", "type", "content_kind")
        }
        with self.assertRaisesRegex(overrides.VanillaOverrideError, "content_kind ancient"):
            overrides.validate_override_manifest(
                manifest_with(catalog, [wrong_target]), catalog
            )

        proceed = copy.deepcopy(operation)
        proceed["semantics"]["options"][0]["is_proceed"] = True
        with self.assertRaisesRegex(overrides.VanillaOverrideError, "native Done owns"):
            overrides.validate_override_manifest(manifest_with(catalog, [proceed]), catalog)

        unreachable = copy.deepcopy(operation)
        unreachable["semantics"]["pages"] = [
            {
                "id": "NOWHERE",
                "description_key": "PROOF_ANCIENT_NOWHERE",
                "options": [
                    make_ancient_option("nowhere", "PROOF_ANCIENT_NOWHERE_OPTION")
                ],
            }
        ]
        with self.assertRaisesRegex(overrides.VanillaOverrideError, "unreachable pages"):
            overrides.validate_override_manifest(
                manifest_with(catalog, [unreachable]), catalog
            )

        no_finish = make_ancient_operation(
            catalog,
            route_id="ancient.initial-options.replace",
            option=make_ancient_option(
                "never-finish",
                "PROOF_ANCIENT_NEVER_FINISH",
                next_step={"kind": "stay"},
            ),
        )
        with self.assertRaisesRegex(overrides.VanillaOverrideError, "finish path"):
            overrides.validate_override_manifest(
                manifest_with(catalog, [no_finish]), catalog
            )

    def test_ancient_append_composes_but_replacement_conflicts(self) -> None:
        catalog = make_ancient_catalog()
        first = make_ancient_operation(catalog, index=0)
        second = make_ancient_operation(
            catalog,
            index=1,
            option=make_ancient_option("second", "PROOF_ANCIENT_SECOND"),
        )
        self.assertIn(
            "operations=2",
            overrides.validate_override_manifest(
                manifest_with(catalog, [first, second]), catalog
            ),
        )

        replacement = make_ancient_operation(
            catalog, route_id="ancient.initial-options.replace", index=1
        )
        with self.assertRaisesRegex(overrides.VanillaOverrideError, "conflicting operations"):
            overrides.validate_override_manifest(
                manifest_with(catalog, [first, replacement]), catalog
            )

    def test_project_ancient_localization_is_required_for_each_shipped_language(self) -> None:
        catalog = make_ancient_catalog()
        operation = make_ancient_operation(catalog)
        manifest = manifest_with(catalog, [operation])
        required = sorted(set(overrides._iter_ancient_localization_keys([operation])))
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            catalog_path = project / "catalog.json"
            catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
            manifest_path = project / overrides.MANIFEST_RELATIVE_PATH
            manifest_path.parent.mkdir(parents=True)
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

            with self.assertRaisesRegex(overrides.VanillaOverrideError, "eng/events.json"):
                overrides.validate_project_override_manifest(
                    project, "Proof", catalog_path=catalog_path
                )

            for language in ("eng", "zhs"):
                localization = project / "Proof" / "localization" / language
                localization.mkdir(parents=True)
                (localization / "events.json").write_text(
                    json.dumps({key: f"{language}:{key}" for key in required}),
                    encoding="utf-8",
                )
            self.assertIn(
                f"event_localizations=2 keys={len(required)}",
                overrides.validate_project_override_manifest(
                    project, "Proof", catalog_path=catalog_path
                ),
            )

            zhs_path = project / "Proof" / "localization" / "zhs" / "events.json"
            zhs_table = json.loads(zhs_path.read_text(encoding="utf-8"))
            zhs_table.pop(required[0])
            zhs_path.write_text(json.dumps(zhs_table), encoding="utf-8")
            with self.assertRaisesRegex(overrides.VanillaOverrideError, "missing Event/Ancient"):
                overrides.validate_project_override_manifest(
                    project, "Proof", catalog_path=catalog_path
                )

    def test_project_ordinary_event_localization_uses_event_namespace(self) -> None:
        catalog = overrides.load_catalog()
        option = make_ancient_option(
            "leave", "PROOF_EVENT_LEAVE", next_step={"kind": "finish"}
        )
        option.update(
            {
                "cost": {"kind": "none", "amount": 0, "allow_lethal": False},
                "enabled_when": {"kind": "always", "parameters": {}},
                "hover_tips": [],
                "relic": None,
            }
        )
        target = "EVENT.THE_ARCHITECT"
        route_id = "behavior.event.options"
        prefix = f"non-card.{target.lower().replace('_', '-')}"
        operation = make_non_card_operation(
            catalog,
            target,
            route_id,
            mode="replace",
            route_class="adapter",
            dependencies=(
                f"{prefix}.behavior.initial-options",
                "non-card.event.flow.finish",
            ),
            semantics={
                "complete": True,
                "condition": {"kind": "always", "parameters": {}},
                "multiplayer": "singleplayer",
                "options": [option],
                "pages": [],
            },
        )
        manifest = manifest_with(catalog, [operation])
        required = sorted(set(overrides._iter_ancient_localization_keys([operation])))

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            manifest_path = project / overrides.MANIFEST_RELATIVE_PATH
            manifest_path.parent.mkdir(parents=True)
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            for language in ("eng", "zhs"):
                localization = project / "Proof" / "localization" / language
                localization.mkdir(parents=True)
                (localization / "events.json").write_text(
                    json.dumps({key: f"{language}:{key}" for key in required}),
                    encoding="utf-8",
                )

            self.assertIn(
                f"event_localizations=2 keys={len(required)}",
                overrides.validate_project_override_manifest(project, "Proof"),
            )

    def test_probe_adapter_fingerprint_and_implementation_fields_fail_closed(self) -> None:
        catalog = make_catalog()
        probe = make_operation(
            0,
            "card.probe",
            route={"class": "probe", "id": "candidate.route", "fingerprint": None},
        )
        with self.assertRaisesRegex(overrides.VanillaOverrideError, "unlisted probe"):
            overrides.validate_override_manifest(
                manifest_with(catalog, [probe]),
                catalog,
                allow_unlisted_operations=True,
            )

        catalog["adapters"] = [
            {
                "id": "card.on-play",
                "type": "MegaCrit.Sts2.Core.Models.Cards.LostWisp",
                "method": "OnPlay",
                "signature": "Void MegaCrit.Sts2.Core.Models.Cards.LostWisp.OnPlay()",
                "metadata_token": 100663297,
                "signature_sha256": "b" * 64,
                "il_sha256": "c" * 64,
                "body_shape": {
                    "il_byte_count": 12,
                    "max_stack": 2,
                    "local_signature_token": 0,
                    "exception_region_count": 0,
                },
            }
        ]
        catalog["catalog_sha256"] = overrides.catalog_digest(catalog)
        adapter = make_operation(
            0,
            "card.adapter",
            route={"class": "adapter", "id": "card.on-play", "fingerprint": "d" * 64},
        )
        with self.assertRaisesRegex(overrides.VanillaOverrideError, "fingerprint drift"):
            overrides.validate_override_manifest(
                manifest_with(catalog, [adapter]),
                catalog,
                allow_unlisted_operations=True,
            )
        adapter["route"]["fingerprint"] = "c" * 64
        with self.assertRaisesRegex(overrides.VanillaOverrideError, "unknown adapter operation"):
            overrides.validate_override_manifest(
                manifest_with(catalog, [adapter]),
                catalog,
                allow_unlisted_operations=True,
            )

        dangerous = make_operation(0, "card.dangerous")
        dangerous["semantics"] = {"effect": {"reflection": "private member"}}
        with self.assertRaisesRegex(overrides.VanillaOverrideError, "forbidden implementation field"):
            overrides.validate_override_manifest(
                manifest_with(make_catalog(), [dangerous]),
                make_catalog(),
                allow_unlisted_operations=True,
            )


class VanillaOverridePipelineTests(unittest.TestCase):
    def test_reference_docs_list_every_route_the_validator_accepts(self) -> None:
        sts2_root = TOOLS_DIR.parent
        for reference in (
            "vanilla-overrides.md",
            "vanilla-card-overrides.md",
            "vanilla-visual-overrides.md",
            "vanilla-ancient-overrides.md",
            "vanilla-availability-overrides.md",
            "vanilla-non-card-overrides.md",
        ):
            with self.subTest(reference=reference):
                self.assertTrue(
                    (sts2_root / "skills" / "sts2api" / "reference" / reference).is_file()
                )

        card_reference = (
            sts2_root / "skills" / "sts2api" / "reference" / "vanilla-card-overrides.md"
        ).read_text(encoding="utf-8")
        for route_id in overrides._CARD_PUBLIC_ROUTES:
            self.assertIn(route_id, card_reference)

        visual_reference = (
            sts2_root / "skills" / "sts2api" / "reference" / "vanilla-visual-overrides.md"
        ).read_text(encoding="utf-8")
        for route_id in overrides.PUBLIC_VISUAL_ROUTES:
            self.assertIn(route_id, visual_reference)

        ancient_reference = (
            sts2_root / "skills" / "sts2api" / "reference" / "vanilla-ancient-overrides.md"
        ).read_text(encoding="utf-8")
        for route_id in overrides.ANCIENT_ROUTES:
            self.assertIn(route_id, ancient_reference)
        for adapter_id in ANCIENT_ADAPTER_HASHES:
            self.assertIn(adapter_id, ancient_reference)

        availability_reference = (
            sts2_root
            / "skills"
            / "sts2api"
            / "reference"
            / "vanilla-availability-overrides.md"
        ).read_text(encoding="utf-8")
        for route_id in (
            overrides.AVAILABILITY_PUBLIC_EPOCH_ROUTE,
            *overrides.AVAILABILITY_PUBLIC_POOL_ROUTES,
            *overrides.AVAILABILITY_ADAPTER_ROUTES,
        ):
            self.assertIn(route_id, availability_reference)
        for adapter_id in AVAILABILITY_ADAPTER_HASHES:
            self.assertIn(adapter_id, availability_reference)

        non_card_reference = (
            sts2_root
            / "skills"
            / "sts2api"
            / "reference"
            / "vanilla-non-card-overrides.md"
        ).read_text(encoding="utf-8")
        for route_id in (
            set(overrides._NON_CARD_OWNER_HOOK_ROUTES)
            | set(overrides._NON_CARD_DATA_ROUTES)
            | set(overrides._NON_CARD_LIFECYCLE_ROUTES)
        ):
            self.assertIn(route_id, non_card_reference)
        for hook_id in (
            overrides._NON_CARD_EFFECT_HOOKS
            | overrides._NON_CARD_ORB_EFFECT_HOOKS
            | overrides._NON_CARD_NUMERIC_HOOKS
            | overrides._NON_CARD_DECISION_HOOKS
        ):
            self.assertIn(hook_id, non_card_reference)

    def test_reference_only_symbols_have_local_imports(self) -> None:
        sts2_root = TOOLS_DIR.parent
        ancient_reference = (
            sts2_root / "skills" / "sts2api" / "reference" / "vanilla-ancient-overrides.md"
        ).read_text(encoding="utf-8")
        event_outcomes = (
            sts2_root / "skills" / "sts2api" / "reference" / "event-outcomes.md"
        ).read_text(encoding="utf-8")

        self.assertIn("using STS2RitsuLib.Patching.Core;", ancient_reference)
        self.assertIn("using MegaCrit.Sts2.Core.Entities.Gold;", event_outcomes)

    def test_reference_only_symbol_namespaces_compile_in_a_fresh_scaffold(self) -> None:
        dotnet = shutil.which("dotnet")
        if not dotnet:
            self.skipTest("dotnet is unavailable")

        configured = os.environ.get("OPEN_MOD_STS2_DIR")
        candidates = [Path(configured)] if configured else []
        candidates.extend(
            [
                Path("D:/Steam/steamapps/common/Slay the Spire 2"),
                Path("C:/Program Files (x86)/Steam/steamapps/common/Slay the Spire 2"),
                Path.home() / ".local/share/Steam/steamapps/common/Slay the Spire 2",
            ]
        )
        host_and_data = next(
            (
                (host, data)
                for host in candidates
                for data in (
                    host / "data_sts2_windows_x86_64",
                    host / "data_sts2_linuxbsd_x86_64",
                    host / "SlayTheSpire2.app/Contents/Resources/data_sts2_macos_arm64",
                    host / "SlayTheSpire2.app/Contents/Resources/data_sts2_macos_x86_64",
                )
                if (data / "sts2.dll").is_file()
            ),
            None,
        )
        if host_and_data is None:
            self.skipTest("STS2 host is unavailable; set OPEN_MOD_STS2_DIR")
        host, data_dir = host_and_data
        try:
            runtime = resolve_runtime_asset(host, local_mods_dir(host))
            compile_profile = resolve_runtime_compile_profile(runtime.path)
        except ValueError as exc:
            self.skipTest(f"checked local RitsuLib runtime is unavailable: {exc}")

        source = """using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Gold;
using MegaCrit.Sts2.Core.Entities.Players;
using STS2RitsuLib;
using STS2RitsuLib.Patching.Core;
using STS2RitsuLib.Patching.Models;

namespace ReferenceCompile;

internal sealed class ReferencePatch : IPatchMethod
{
    public static string PatchId => "reference_compile";
    public static ModPatchTarget[] GetTargets() => [];
}

public static partial class MainFile
{
    static partial void RegisterContent()
    {
        var patcher = RitsuLibFramework.CreatePatcher(
            ModId, "reference-compile", "Reference compile");
        patcher.RegisterPatch<ReferencePatch>();
    }

    private static async Task SpendGold(Player owner)
    {
        await PlayerCmd.LoseGold(1, owner, GoldLossType.Spent);
    }
}
"""

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "reference-compile-project"
            scaffold.generate(
                project,
                "ReferenceCompile",
                "SkillTheSpire",
                compile_profile=compile_profile,
            )
            (project / "ReferenceCompileCode" / "ReferenceImports.cs").write_text(
                source, encoding="utf-8", newline="\n"
            )
            mods_path = root / "mods"
            result = subprocess.run(
                [
                    dotnet,
                    "build",
                    str(project / "ReferenceCompile.csproj"),
                    "-c",
                    "Release",
                    "--nologo",
                    f"-p:Sts2Dir={host}",
                    f"-p:Sts2DataDir={data_dir}",
                    f"-p:ModsPath={mods_path.as_posix()}/",
                    f"-p:RitsuLibRuntimeRoot={compile_profile.root.resolve().as_posix()}",
                    "-p:RestoreIgnoreFailedSources=true",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=120,
                env={
                    **os.environ,
                    "NUGET_PACKAGES": str(Path.home() / ".nuget" / "packages"),
                },
            )
            output = (result.stdout or "") + (result.stderr or "")
            self.assertEqual(0, result.returncode, output)

    def test_scaffold_emits_a_valid_pinned_noop_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "outer"
            scaffold.generate(project, "Proof", "SkillTheSpire")

            manifest_path = project / overrides.MANIFEST_RELATIVE_PATH
            self.assertTrue(manifest_path.is_file())
            csproj = (project / "Proof.csproj").read_text()
            self.assertIn("<None Include=\"skillthespire\\vanilla-overrides.json\"", csproj)
            # It is a build-time input, so it must never be copied into mods/<ModName>/.
            self.assertNotIn("DestinationFolder=\"$(ModsPath)$(MSBuildProjectName)\\skillthespire\"", csproj)
            summary = overrides.validate_project_override_manifest(project, "Proof")
            self.assertIn("operations=0", summary)

    def test_projects_without_an_override_manifest_have_no_overrides(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIn(
                "no vanilla overrides",
                overrides.validate_project_override_manifest(Path(tmp), "Proof"),
            )

    def test_build_stops_before_msbuild_on_an_invalid_override_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / "Proof.csproj").write_text("<Project />", encoding="utf-8")
            override_path = project / overrides.MANIFEST_RELATIVE_PATH
            override_path.parent.mkdir(parents=True)
            override_path.write_text("{}\n", encoding="utf-8")

            with (
                mock.patch.object(build, "validate_project_contract", return_value="ok"),
                mock.patch.object(build, "validate_resource_manifest", return_value="has_pck=false"),
                mock.patch.object(build, "validate_project_ancient_dialogue", return_value="none"),
                mock.patch.object(build.subprocess, "run") as run,
                mock.patch("builtins.print"),
            ):
                self.assertEqual(
                    2,
                    build.main(
                        [
                            "--project-dir",
                            str(project),
                            "--mod-name",
                            "Proof",
                        ]
                    ),
                )
                run.assert_not_called()

    def _deployed_proof_tree(self, root: Path) -> tuple[Path, Path]:
        """A validated source project plus its deployed Mod directory."""
        project = root / "project"
        deployed = root / "mods" / "Proof"
        source_override = project / overrides.MANIFEST_RELATIVE_PATH
        source_override.parent.mkdir(parents=True)
        deployed.mkdir(parents=True)
        (project / "mod_manifest.json").write_text("{}\n", encoding="utf-8")
        (deployed / "mod_manifest.json").write_text("{}\n", encoding="utf-8")
        (deployed / "Proof.dll").write_bytes(b"proof")
        source_override.write_text('{"source": true}\n', encoding="utf-8")
        return project, deployed

    def test_the_override_sidecar_is_not_deployed_into_the_mod_tree(self) -> None:
        """The game parses every deployed `.json` as a manifest, so the sidecar stays home."""
        with tempfile.TemporaryDirectory() as tmp:
            project, deployed = self._deployed_proof_tree(Path(tmp))

            build.validate_deployed_artifacts(project, "Proof", deployed)

            self.assertTrue((project / overrides.MANIFEST_RELATIVE_PATH).is_file())
            self.assertFalse((deployed / overrides.MANIFEST_RELATIVE_PATH).exists())

    def test_any_other_deployed_json_fails_the_build(self) -> None:
        """One rule, not one exception: only the Mod's own manifest may be loose JSON."""
        with tempfile.TemporaryDirectory() as tmp:
            project, deployed = self._deployed_proof_tree(Path(tmp))
            phantom = deployed / "data" / "future-sidecar.json"
            phantom.parent.mkdir(parents=True)
            phantom.write_text('{"schema": "whatever"}\n', encoding="utf-8")

            with self.assertRaisesRegex(build.RitsuProfileError, "data/future-sidecar.json"):
                build.validate_deployed_artifacts(project, "Proof", deployed)


if __name__ == "__main__":
    unittest.main()
