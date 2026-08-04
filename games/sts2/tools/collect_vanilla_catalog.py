#!/usr/bin/env python3
"""Maintainer workflow for the M6.7.0 runtime and assembly catalog collectors."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from ritsu_profile import PROFILE
from scaffold import generate
from vanilla_overrides import (
    VanillaOverrideError,
    catalog_digest,
    merge_catalogs,
    validate_catalog,
)


TOOLS_DIR = Path(__file__).resolve().parent
RUNTIME_TEMPLATE = TOOLS_DIR / "templates" / "m67_runtime_catalog_collector.cs.tmpl"
ASSEMBLY_PROJECT = TOOLS_DIR / "assembly_catalog" / "OpenMod.Sts2.AssemblyCatalog.csproj"
POWERSHELL_ASSEMBLY_COLLECTOR = TOOLS_DIR / "assembly_catalog" / "Collect-AssemblyCatalog.ps1"
DEFAULT_TARGETS = (
    TOOLS_DIR.parent
    / "skills"
    / "sts2-api"
    / "reference"
    / "vanilla-overrides"
    / "adapter-targets-0.107.1.json"
)

NON_CARD_DATA_TARGETS: dict[str, tuple[tuple[str, str, str], ...]] = {
    "RELIC": (("rarity", "data.rarity", "get_Rarity"),),
    "POTION": (
        ("rarity", "data.rarity", "get_Rarity"),
        ("target_type", "data.target-type", "get_TargetType"),
        ("usage", "data.usage", "get_Usage"),
    ),
    "POWER": (
        ("allow_negative", "data.allow-negative", "get_AllowNegative"),
        ("power_type", "data.type", "get_Type"),
        ("scales_in_multiplayer", "data.scales-in-multiplayer", "get_ShouldScaleInMultiplayer"),
        ("stack_type", "data.stack-type", "get_StackType"),
    ),
    "ENCHANTMENT": (("stackable", "data.stackable", "get_IsStackable"),),
    "AFFLICTION": (
        ("can_afflict_unplayable", "data.can-afflict-unplayable", "get_CanAfflictUnplayableCards"),
        ("stackable", "data.stackable", "get_IsStackable"),
    ),
    "MONSTER": (
        ("max_initial_hp", "data.max-initial-hp", "get_MaxInitialHp"),
        ("min_initial_hp", "data.min-initial-hp", "get_MinInitialHp"),
        ("show_in_compendium", "data.show-in-compendium", "get_ShouldShowInCompendium"),
    ),
    "ENCOUNTER": (
        ("is_weak", "data.is-weak", "get_IsWeak"),
        ("room_type", "data.room-type", "get_RoomType"),
    ),
}

NON_CARD_LIFECYCLE_TARGETS: dict[str, tuple[tuple[str, str], ...]] = {
    "RELIC": (
        ("lifecycle.after-obtained", "AfterObtained"),
        ("lifecycle.after-removed", "AfterRemoved"),
    ),
    "POTION": (("lifecycle.use", "OnUse"),),
    "POWER": (
        ("lifecycle.before-applied", "BeforeApplied"),
        ("lifecycle.after-applied", "AfterApplied"),
        ("lifecycle.after-removed", "AfterRemoved"),
    ),
    "ORB": (
        ("lifecycle.before-turn-end", "BeforeTurnEndOrbTrigger"),
        ("lifecycle.after-turn-start", "AfterTurnStartOrbTrigger"),
        ("lifecycle.passive", "Passive"),
        ("lifecycle.evoke", "Evoke"),
    ),
    "ENCHANTMENT": (("lifecycle.on-play", "OnPlay"),),
    "AFFLICTION": (
        ("lifecycle.after-applied", "AfterApplied"),
        ("lifecycle.before-removed", "BeforeRemoved"),
        ("lifecycle.on-play", "OnPlay"),
    ),
    "MONSTER": (("behavior.move-state-machine", "GenerateMoveStateMachine"),),
    "ENCOUNTER": (
        ("behavior.monster-roster", "GenerateMonsters"),
        ("behavior.all-possible-monsters", "get_AllPossibleMonsters"),
    ),
    "EVENT": (("behavior.initial-options", "GenerateInitialOptionsWrapper"),),
}

NON_CARD_SHARED_TARGETS: tuple[dict[str, str], ...] = (
    {
        "id": "non-card.event.flow.finish",
        "type": "MegaCrit.Sts2.Core.Models.EventModel",
        "method": "SetEventFinished",
        "signature_label": "pinned EventModel.SetEventFinished flow boundary",
    },
    {
        "id": "non-card.event.flow.set-state",
        "type": "MegaCrit.Sts2.Core.Models.EventModel",
        "method": "SetEventState",
        "signature_label": "pinned EventModel.SetEventState flow boundary",
    },
    {
        "id": "non-card.owner-hook-stream.combat",
        "type": "MegaCrit.Sts2.Core.Combat.CombatState",
        "method": "IterateHookListeners",
        "signature_label": "pinned CombatState.IterateHookListeners owner-stream boundary",
    },
    {
        "id": "non-card.owner-hook-stream.run",
        "type": "MegaCrit.Sts2.Core.Runs.RunState",
        "method": "IterateHookListeners",
        "signature_label": "pinned RunState.IterateHookListeners owner-stream boundary",
    },
)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _adapter_slug(model_id: str) -> str:
    return model_id.lower().replace("_", "-")


def generate_non_card_adapter_targets(catalog_path: Path, output: Path) -> None:
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    validate_catalog(catalog)

    existing_document = json.loads(DEFAULT_TARGETS.read_text(encoding="utf-8"))
    existing = [
        target
        for target in existing_document["targets"]
        if not str(target.get("id", "")).startswith("non-card.")
    ]
    generated: list[dict[str, str]] = [dict(target) for target in NON_CARD_SHARED_TARGETS]
    for model in catalog["models"]:
        category = model["category"]
        target_prefix = f"non-card.{_adapter_slug(model['id'])}"
        for property_name, route_suffix, method in NON_CARD_DATA_TARGETS.get(category, ()):
            if property_name not in model.get("properties", {}):
                continue
            generated.append(
                {
                    "id": f"{target_prefix}.{route_suffix}",
                    "type": model["type"],
                    "method": method,
                    "signature_label": (
                        f"pinned {{declaring_type}}.{method} for {model['id']} {route_suffix}"
                    ),
                }
            )
        for route_suffix, method in NON_CARD_LIFECYCLE_TARGETS.get(category, ()):
            generated.append(
                {
                    "id": f"{target_prefix}.{route_suffix}",
                    "type": model["type"],
                    "method": method,
                    "signature_label": (
                        f"pinned {{declaring_type}}.{method} for {model['id']} {route_suffix}"
                    ),
                }
            )

    targets = sorted([*existing, *generated], key=lambda target: target["id"])
    duplicate = next(
        (target["id"] for index, target in enumerate(targets[1:], 1)
         if target["id"] == targets[index - 1]["id"]),
        None,
    )
    if duplicate is not None:
        raise VanillaOverrideError(f"duplicate generated adapter target {duplicate}")
    _write(
        output,
        json.dumps(
            {"schema": "openmod.sts2.adapter-targets/v1", "targets": targets},
            indent=2,
        )
        + "\n",
    )
    print(
        f"[catalog] adapter targets existing={len(existing)} "
        f"non_card={len(generated)} total={len(targets)}"
    )


def create_runtime_collector(project_dir: Path, mod_name: str, author: str) -> None:
    generate(project_dir, mod_name, author, emit_override_manifest=False)
    template = RUNTIME_TEMPLATE.read_text(encoding="utf-8")
    source = (
        template.replace("__MOD_NAME__", mod_name)
        .replace("__HOST_VERSION__", PROFILE.host_version)
        .replace("__PROFILE_ID__", PROFILE.profile_id)
    )
    _write(project_dir / f"{mod_name}Code" / "RuntimeCatalogCollector.cs", source)
    manifest_path = project_dir / f"{mod_name}.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["description"] = "open-mod M6.7.0 no-op vanilla runtime catalog collector"
    manifest["affects_gameplay"] = False
    _write(manifest_path, json.dumps(manifest, indent=2) + "\n")


def collect_assembly(assembly: Path, targets: Path, output: Path) -> None:
    command = [
        "dotnet",
        "run",
        "--project",
        str(ASSEMBLY_PROJECT),
        "--configuration",
        "Release",
        "--",
        str(assembly),
        str(targets),
        PROFILE.profile_id,
        str(output),
    ]
    result = subprocess.run(command, text=True, encoding="utf-8", errors="replace")
    if result.returncode != 0:
        raise VanillaOverrideError(f"assembly collector failed with exit {result.returncode}")


def collect_assembly_powershell(assembly: Path, targets: Path, output: Path) -> None:
    command = [
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(POWERSHELL_ASSEMBLY_COLLECTOR),
        "-AssemblyPath",
        str(assembly),
        "-TargetsPath",
        str(targets),
        "-Profile",
        PROFILE.profile_id,
        "-OutputPath",
        str(output),
    ]
    result = subprocess.run(command, text=True, encoding="utf-8", errors="replace")
    if result.stdout:
        print(result.stdout, end="")
    if result.returncode != 0:
        if result.stderr:
            print(result.stderr, file=sys.stderr, end="")
        raise VanillaOverrideError(
            f"PowerShell assembly collector failed with exit {result.returncode}"
        )


def merge(
    runtime_path: Path,
    assembly_path: Path,
    output: Path,
    promoted_packages: list[str] | None = None,
) -> None:
    runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
    assembly = json.loads(assembly_path.read_text(encoding="utf-8"))
    catalog = merge_catalogs(runtime, assembly)
    catalog["promoted_operation_packages"] = sorted(set(promoted_packages or []))
    catalog["catalog_sha256"] = catalog_digest(catalog)
    validate_catalog(catalog)
    _write(output, json.dumps(catalog, ensure_ascii=False, indent=2) + "\n")
    print(
        f"[catalog] merged models={len(catalog['models'])} "
        f"adapters={len(catalog['adapters'])} sha256={catalog['catalog_sha256']}"
    )


def refresh_adapters(
    catalog_path: Path,
    assembly_path: Path,
    output: Path,
    promoted_packages: list[str] | None = None,
) -> None:
    current = json.loads(catalog_path.read_text(encoding="utf-8"))
    validate_catalog(current)
    runtime = {
        "schema": "openmod.sts2.vanilla-runtime-catalog/v2",
        "host_version": current["host_version"],
        "profile": current["profile"],
        "assembly_sha256": current["assembly"]["sha256"],
        "localization_languages": current["localization_languages"],
        "models": [
            {
                key: model[key]
                for key in (
                    "id",
                    "type",
                    "content_kind",
                    "is_debug",
                    "title_localization",
                    "properties",
                    "sources",
                )
            }
            for model in current["models"]
        ],
    }
    assembly = json.loads(assembly_path.read_text(encoding="utf-8"))
    refreshed = merge_catalogs(runtime, assembly)
    refreshed["promoted_operation_packages"] = sorted(
        set(current["promoted_operation_packages"]) | set(promoted_packages or [])
    )
    refreshed["catalog_sha256"] = catalog_digest(refreshed)
    validate_catalog(refreshed)
    _write(output, json.dumps(refreshed, ensure_ascii=False, indent=2) + "\n")
    print(
        f"[catalog] refreshed models={len(refreshed['models'])} "
        f"adapters={len(refreshed['adapters'])} sha256={refreshed['catalog_sha256']}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collect the pinned STS2 vanilla catalog")
    subparsers = parser.add_subparsers(dest="command", required=True)

    runtime = subparsers.add_parser("create-runtime-project")
    runtime.add_argument("--project-dir", required=True)
    runtime.add_argument("--mod-name", default="OpenModM67Catalog")
    runtime.add_argument("--author", default="OpenMod")

    assembly = subparsers.add_parser("collect-assembly")
    assembly.add_argument("--assembly", required=True)
    assembly.add_argument("--targets", default=str(DEFAULT_TARGETS))
    assembly.add_argument("--output", required=True)

    powershell_assembly = subparsers.add_parser("collect-assembly-powershell")
    powershell_assembly.add_argument("--assembly", required=True)
    powershell_assembly.add_argument("--targets", default=str(DEFAULT_TARGETS))
    powershell_assembly.add_argument("--output", required=True)

    merge_parser = subparsers.add_parser("merge")
    merge_parser.add_argument("--runtime", required=True)
    merge_parser.add_argument("--assembly", required=True)
    merge_parser.add_argument("--output", required=True)
    merge_parser.add_argument("--promote-package", action="append", default=[])

    target_parser = subparsers.add_parser("generate-adapter-targets")
    target_parser.add_argument("--catalog", required=True)
    target_parser.add_argument("--output", default=str(DEFAULT_TARGETS))

    refresh_parser = subparsers.add_parser("refresh-adapters")
    refresh_parser.add_argument("--catalog", required=True)
    refresh_parser.add_argument("--assembly", required=True)
    refresh_parser.add_argument("--output", required=True)
    refresh_parser.add_argument("--promote-package", action="append", default=[])

    args = parser.parse_args(argv)
    try:
        if args.command == "create-runtime-project":
            create_runtime_collector(Path(args.project_dir), args.mod_name, args.author)
            print(f"[catalog] runtime collector -> {Path(args.project_dir).resolve()}")
        elif args.command == "collect-assembly":
            collect_assembly(Path(args.assembly), Path(args.targets), Path(args.output))
        elif args.command == "collect-assembly-powershell":
            collect_assembly_powershell(Path(args.assembly), Path(args.targets), Path(args.output))
        elif args.command == "generate-adapter-targets":
            generate_non_card_adapter_targets(Path(args.catalog), Path(args.output))
        elif args.command == "refresh-adapters":
            refresh_adapters(
                Path(args.catalog),
                Path(args.assembly),
                Path(args.output),
                args.promote_package,
            )
        else:
            merge(
                Path(args.runtime),
                Path(args.assembly),
                Path(args.output),
                args.promote_package,
            )
    except (OSError, ValueError, json.JSONDecodeError, VanillaOverrideError) as exc:
        print(f"[catalog] FAILED: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
