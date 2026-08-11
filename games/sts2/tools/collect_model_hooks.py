#!/usr/bin/env python3
"""Maintainer-only extractor for the pinned `AbstractModel` scalar/decision hook surface.

Why this exists. A generated Mod can override a `public virtual` hook that the pinned host
never dispatches to that kind of model: it compiles, ships, and silently never fires. That is
the M7.6 Wrath failure shape — an identity-critical behavior absent while every local stage
passes — so the authoring surface has to know *which* hooks a given surface can actually
receive, not merely which ones exist.

`AbstractModel` declares them all in one place, but reachability is decided elsewhere, by
which listener set the dispatching iterator walks. `Hook` uses five distinct iterator forms
and their membership differs: the run-scope set carries no Powers, Orbs, or Monsters at all.
So the mapping this tool produces is (hook -> dispatcher -> iterator -> listener set ->
reachable surfaces), read out of the pinned source rather than assumed.

Maintainer-only, like `collect_vanilla_catalog.py`: it reads the gitignored decompile under
`baselines/decomp/`, which no user runtime has. The committed catalog it writes is the
shipped artifact. `publish.sh` excludes this file from both payloads.

Provenance caveat, from AGENTS.md: the decompile's original DLL hash sidecar was not
retained, so every fact here is a research result to recheck against the pinned assembly or
installed game before it is promoted into authoring instruction.

Usage:

    python collect_model_hooks.py extract            # write the catalog
    python collect_model_hooks.py extract --check    # fail if the committed copy is stale
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


SCHEMA = "openmod.sts2.model-hooks/v1"
HOST_VERSION = "0.107.1"
CATALOG_RELATIVE_PATH = Path("reference/catalogs/model-hooks-sts2-0.107.1.json")

TOOLS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TOOLS_DIR.parents[2]
DECOMP_ROOT = REPO_ROOT / "baselines" / "decomp" / "sts2_full" / "MegaCrit" / "sts2"

ABSTRACT_MODEL = Path("Core/Models/AbstractModel.cs")
HOOK = Path("Core/Hooks/Hook.cs")
MODELS_DIR = Path("Core/Models")

# Return types that make a hook a scalar modifier rather than an effect callback. `bool`
# is split out below into decision vs out-parameter families, which differ in how a SPEC
# declares them: a decision returns an answer, a TryModify writes a replacement value.
NUMERIC_RETURNS = {"decimal", "int", "float", "double"}

# Not a hook: `IComparable` plumbing that happens to be a public virtual int.
NOT_A_HOOK = {"CompareTo"}

# The listener sets the pinned `Hook` iterators walk, read from RunState.IterateHookListeners,
# CombatState.IterateHookListeners, and Hook.IterateCombatHookListeners. Membership is the
# whole reason a hook can be unreachable on a surface, so it is stated as data.
#
# `RunState.IterateHookListeners(childCombatState)` adds the player's deck Cards and their
# Enchantments unconditionally, then branches. Only when `childCombatState` is null does it
# add *run-scope* Relics, Potions, Modifiers, Badges, and MultiplayerScalingModel; when a
# combat state is passed it instead chains `childCombatState.IterateHookListeners()`.
#
# So the combat-state form reaches deck Cards and Enchantments plus the combat set, and since
# the combat set already contains Cards and Enchantments (from the piles), that form's
# membership equals the combat set exactly.
#
# `CombatState.IterateHookListeners()` walks creature Powers, Monsters, the player's Relics and
# PotionSlots, the Orb queue, every pile Card with its Affliction and Enchantment, and then
# `combatState.Modifiers` and `combatState.BadgeModels`. The run and combat sets therefore both
# contain Modifiers and Badges — what the run-only branch adds is the *run-scope* instances, not
# the family. An earlier revision of this comment concluded the combat set had neither, which
# under-specified `listener_families` on every combat-dispatched hook.
RUN_ONLY_LISTENERS = ("card", "enchantment", "relic", "potion", "modifier", "badge")
COMBAT_LISTENERS = (
    "affliction",
    "badge",
    "card",
    "enchantment",
    "modifier",
    "monster",
    "orb",
    "potion",
    "power",
    "relic",
)

# iterator form -> (scope label, listener families)
ITERATORS: dict[str, tuple[str, tuple[str, ...]]] = {
    "runState.IterateHookListeners(null)": ("run", RUN_ONLY_LISTENERS),
    "runState.IterateHookListeners(combatState)": ("run+combat", COMBAT_LISTENERS),
    "IterateCombatHookListeners(combatState)": ("combat", COMBAT_LISTENERS),
    "combatState.IterateHookListeners()": ("combat", COMBAT_LISTENERS),
    "CombatState.IterateHookListeners()": ("combat", COMBAT_LISTENERS),
}

# Surfaces this pack can generate, mapped to the listener family they register as. A
# surface absent here is not authorable regardless of hook reachability.
GENERATED_SURFACES: dict[str, str] = {
    "card": "card",
    "relic": "relic",
    "potion": "potion",
    "power": "power",
    "orb": "orb",
    "monster": "monster",
    "enchantment": "enchantment",
}

# `EnchantmentModel` documents its own replacements for five `AbstractModel` hooks, each
# "Enchantments MUST use this hook instead of" its counterpart and each running before all
# other modification hooks. An Enchantment overriding the general hook is wrong on the
# pinned host, so the catalog records the redirect rather than reporting reachability.
ENCHANTMENT_REDIRECTS = {
    "ModifyBlockAdditive": "EnchantBlockAdditive",
    "ModifyBlockMultiplicative": "EnchantBlockMultiplicative",
    "ModifyDamageAdditive": "EnchantDamageAdditive",
    "ModifyDamageMultiplicative": "EnchantDamageMultiplicative",
    "ModifyCardPlayCount": "EnchantPlayCount",
}

# Mutable collection parameter types. A hook carrying one does not return a replacement
# value; it edits a list the host owns and its `bool` reports only "I touched it". That is a
# different declaration shape from an `out` replacement, so the catalog records which one a
# hook needs rather than leaving authoring to infer it from the signature.
COLLECTION_TYPES = ("List<", "IList<", "ISet<", "ICollection<", "HashSet<")

# A hook whose surface an existing shipped route already owns. Offering the raw hook beside
# that route would let a generated Mod bypass the route's boundaries, so the catalog names
# the owner and step 3 must route through it rather than around it.
ROUTE_OWNERS = {
    "TryModifyRestSiteOptions": "reference/rest-site-options.md",
    "ShouldDisableRemainingRestSiteOptions": "reference/rest-site-options.md",
}


class ModelHookError(RuntimeError):
    """Raised when the pinned source cannot be read as one closed hook surface."""


@dataclass
class Hook:
    name: str
    family: str
    return_type: str
    signature: str
    parameters: list[str]
    neutral_default: str
    dispatchers: list[str] = field(default_factory=list)
    iterators: list[str] = field(default_factory=list)
    vanilla_implementors: dict[str, int] = field(default_factory=dict)
    unresolved: list[str] = field(default_factory=list)


def _read(relative: Path) -> str:
    path = DECOMP_ROOT / relative
    if not path.is_file():
        raise ModelHookError(
            f"missing pinned source {path}. This is a maintainer-only tool and needs the "
            f"gitignored decompile under baselines/decomp/."
        )
    return path.read_text(encoding="utf-8", errors="replace")


def _brace_body(src: str, open_index: int) -> str:
    """Return the balanced `{...}` body starting at `open_index`."""
    depth = 0
    for index in range(open_index, len(src)):
        char = src[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return src[open_index : index + 1]
    raise ModelHookError("unbalanced braces in pinned source")


def _split_parameters(raw: str) -> list[str]:
    """Split a C# parameter list on top-level commas (generics carry their own)."""
    parts: list[str] = []
    depth = 0
    current = ""
    for char in raw:
        if char in "<([":
            depth += 1
        elif char in ">)]":
            depth -= 1
        if char == "," and depth == 0:
            parts.append(current.strip())
            current = ""
        else:
            current += char
    if current.strip():
        parts.append(current.strip())
    return parts


def _family(name: str, return_type: str) -> str | None:
    if name in NOT_A_HOOK:
        return None
    if return_type in NUMERIC_RETURNS:
        return "numeric"
    if return_type == "bool":
        return "trymodify" if name.startswith("TryModify") else "decision"
    return None


DECLARATION_RE = re.compile(
    r"public virtual\s+(?P<ret>decimal|int|float|double|bool)\s+(?P<name>\w+)\s*\((?P<params>[^)]*)\)"
)


def parse_declarations() -> dict[str, Hook]:
    """Every scalar/decision hook `AbstractModel` declares, with its neutral default.

    The neutral default matters as much as the signature: it is what a guard must return
    outside its intended case. A hook returning its modifier unconditionally changes every
    unrelated interaction in the game while still passing a single-value assertion.
    """
    src = _read(ABSTRACT_MODEL)
    hooks: dict[str, Hook] = {}
    for match in DECLARATION_RE.finditer(src):
        name = match.group("name")
        return_type = match.group("ret")
        family = _family(name, return_type)
        if family is None:
            continue
        brace = src.find("{", match.end())
        if brace < 0:
            raise ModelHookError(f"{name} has no body in AbstractModel")
        body = _brace_body(src, brace)
        returns = re.findall(r"return\s+([^;]+);", body)
        if not returns:
            raise ModelHookError(f"{name} has no return statement to read a default from")
        parameters = _split_parameters(match.group("params"))
        hooks[name] = Hook(
            name=name,
            family=family,
            return_type=return_type,
            signature=f"{return_type} {name}({match.group('params').strip()})",
            parameters=parameters,
            neutral_default=returns[-1].strip(),
        )
    if not hooks:
        raise ModelHookError("parsed no hooks from AbstractModel; the parse shape changed")
    return hooks


def _static_methods(src: str) -> dict[str, list[str]]:
    """Top-level static method bodies in `Hook`, by name.

    Parsing whole bodies rather than searching near a call site is the point. An earlier
    context-window heuristic misattributed hooks whose dispatch sits in a shared private
    helper — `ModifyDamageAdditive` and `ModifyDamageMultiplicative` both dispatch from
    `ModifyDamageInternal` — and produced a scope table that contradicted the vanilla
    implementors. Body-scoped attribution has no such failure mode.
    """
    methods: dict[str, list[str]] = {}
    pattern = re.compile(
        r"\n\t(?:public|private|internal|protected)\s+static\s+[\w<>?\[\], .]+?\s+(\w+)\s*\("
    )
    for match in pattern.finditer(src):
        brace = src.find("{", match.end() - 1)
        if brace < 0:
            continue
        methods.setdefault(match.group(1), []).append(_brace_body(src, brace))
    return methods


ITERATOR_RE = re.compile(r"(?:(\w+)\.)?Iterate(Combat)?HookListeners\(([^)]*)\)")


def _iterator_form(receiver: str | None, combat: str | None, argument: str) -> str:
    argument = argument.strip()
    if combat:
        return f"IterateCombatHookListeners({argument or 'combatState'})"
    prefix = f"{receiver}." if receiver else ""
    return f"{prefix}IterateHookListeners({argument})"


def attribute_dispatch(hooks: dict[str, Hook]) -> None:
    """Map each hook to the `Hook` dispatchers that invoke it and the iterators they walk."""
    methods = _static_methods(_read(HOOK))
    if not methods:
        raise ModelHookError("parsed no static methods from Hook.cs")
    for name, hook in hooks.items():
        call = re.compile(rf"\.{re.escape(name)}\s*\(")
        for dispatcher, bodies in sorted(methods.items()):
            for body in bodies:
                if not call.search(body):
                    continue
                if dispatcher not in hook.dispatchers:
                    hook.dispatchers.append(dispatcher)
                for receiver, combat, argument in ITERATOR_RE.findall(body):
                    form = _iterator_form(receiver or None, combat or None, argument)
                    if form not in hook.iterators:
                        hook.iterators.append(form)
        hook.dispatchers.sort()
        hook.iterators.sort()


def collect_vanilla_implementors(hooks: dict[str, Hook]) -> None:
    """Count vanilla `override`s per model family.

    This is the cross-check on reachability rather than an authoring input: a hook the
    catalog calls unreachable on Powers, with vanilla Powers overriding it, means the
    reachability derivation is wrong. That contradiction is what invalidated the first pass.
    """
    models_root = DECOMP_ROOT / MODELS_DIR
    if not models_root.is_dir():
        raise ModelHookError(f"missing pinned model directory {models_root}")
    override = re.compile(
        r"public override\s+(?:decimal|int|float|double|bool)\s+(\w+)\s*\("
    )
    for path in sorted(models_root.rglob("*.cs")):
        relative = path.relative_to(models_root)
        family = relative.parts[0].lower() if len(relative.parts) > 1 else "root"
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in override.finditer(text):
            hook = hooks.get(match.group(1))
            if hook is None:
                continue
            hook.vanilla_implementors[family] = (
                hook.vanilla_implementors.get(family, 0) + 1
            )


# Vanilla model directory name -> the listener family it registers as. Used only to check
# reachability against real implementors, so a directory with no generated counterpart
# (`Singleton`, `Achievements`) maps to None and is skipped rather than guessed at.
VANILLA_FAMILY_TO_LISTENER: dict[str, str | None] = {
    "cards": "card",
    "relics": "relic",
    "potions": "potion",
    "powers": "power",
    "orbs": "orb",
    "monsters": "monster",
    "enchantments": "enchantment",
    "afflictions": "affliction",
    "modifiers": "modifier",
    "badges": "badge",
    "singleton": None,
    "achievements": None,
    "root": None,
    "mocks": None,
    "characters": None,
    "events": None,
    "acts": None,
    "encounters": None,
    "cardpools": None,
}


def _collection_parameter(hook: Hook) -> str | None:
    for parameter in hook.parameters:
        if any(token in parameter for token in COLLECTION_TYPES):
            return parameter
    return None


def _semantic_id(name: str) -> str:
    """The snake_case id a SPEC declares, e.g. `modify_damage_multiplicative`.

    Carried as data rather than derived by each consumer. `vanilla-non-card-overrides.md`
    already names hooks in this form for vanilla owners, so a custom surface declaring the
    same hook must use the same id — otherwise the two halves of one assembly fact drift
    apart, which is the failure the catalog pattern exists to prevent.
    """
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def _declaration_shape(hook: Hook) -> str:
    """Which SPEC declaration shape this hook needs.

    Three, and the distinction is load-bearing for authoring:

    - `scalar-return`  the hook returns the value. A guard returns the neutral default.
    - `out-replacement` the hook returns "I am replacing it" and writes the replacement to an
      `out` parameter. Semantically the same as scalar-return plus a taken/not-taken flag.
    - `collection-edit` the hook mutates a host-owned list/set and its `bool` reports only
      that it touched it. Nothing is replaced, so a declaration must instead say what is
      added or removed, under what condition, and how it composes with other editors.
    """
    if _collection_parameter(hook) is not None:
        return "collection-edit"
    if any(parameter.startswith("out ") for parameter in hook.parameters):
        return "out-replacement"
    return "scalar-return"


def resolve_reachability(hook: Hook) -> tuple[list[str], list[str]]:
    """Listener families this hook reaches, and any unresolved finding.

    A hook whose dispatch iterator is not one of the five pinned forms is recorded
    unresolved and stays unauthorable. That is INV-3 applied to research: an unknown route
    is a gap to report, not a default to assume.
    """
    findings: list[str] = []
    if not hook.iterators:
        findings.append(
            "no dispatch iterator found in Hook.cs; scope could not be derived"
        )
        return [], findings

    listeners: set[str] = set()
    for form in hook.iterators:
        known = ITERATORS.get(form)
        if known is None:
            findings.append(f"unknown dispatch iterator form {form!r}")
            continue
        listeners.update(known[1])
    if not listeners and not findings:
        findings.append("dispatch iterators yielded no listener family")
    return sorted(listeners), findings


def check_reachability_against_vanilla(hooks: dict[str, Hook]) -> list[str]:
    """A vanilla override on a family the catalog calls unreachable is a hard contradiction."""
    contradictions: list[str] = []
    for hook in hooks.values():
        listeners, _ = resolve_reachability(hook)
        if not listeners:
            continue
        for family, count in sorted(hook.vanilla_implementors.items()):
            listener = VANILLA_FAMILY_TO_LISTENER.get(family, "?")
            if listener is None:
                continue
            if listener == "?":
                contradictions.append(
                    f"{hook.name}: vanilla family {family!r} has no listener mapping"
                )
            elif listener not in listeners:
                contradictions.append(
                    f"{hook.name}: {count} vanilla {family} override(s) but "
                    f"reachability says {listeners}"
                )
    return contradictions


def _canonical_json(value) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def catalog_digest(catalog: dict) -> str:
    payload = {key: value for key, value in catalog.items() if key != "catalog_sha256"}
    return hashlib.sha256(_canonical_json(payload)).hexdigest()


def build_catalog() -> dict:
    hooks = parse_declarations()
    attribute_dispatch(hooks)
    collect_vanilla_implementors(hooks)

    contradictions = check_reachability_against_vanilla(hooks)
    entries = []
    unresolved_names: list[str] = []
    for name in sorted(hooks):
        hook = hooks[name]
        listeners, findings = resolve_reachability(hook)
        surfaces = sorted(
            surface
            for surface, listener in GENERATED_SURFACES.items()
            if listener in listeners
        )
        redirect = ENCHANTMENT_REDIRECTS.get(name)
        if redirect is not None and "enchantment" in surfaces:
            # The general hook is documented as wrong for an Enchantment, so it is not an
            # authorable surface for it; the redirect target is.
            surfaces.remove("enchantment")
        entry = {
            "hook": name,
            "semantic_id": _semantic_id(name),
            "family": hook.family,
            "return_type": hook.return_type,
            "signature": hook.signature,
            "parameters": hook.parameters,
            "neutral_default": hook.neutral_default,
            "declaration_shape": _declaration_shape(hook),
            "dispatchers": hook.dispatchers,
            "dispatch_iterators": hook.iterators,
            "listener_families": listeners,
            "authorable_surfaces": surfaces,
            "vanilla_implementors": dict(sorted(hook.vanilla_implementors.items())),
        }
        collection = _collection_parameter(hook)
        if collection is not None:
            entry["collection_parameter"] = collection
        out_parameter = next(
            (p for p in hook.parameters if p.startswith("out ")), None
        )
        if out_parameter is not None:
            entry["out_parameter"] = out_parameter
        if redirect is not None:
            entry["enchantment_redirect"] = redirect
        owner = ROUTE_OWNERS.get(name)
        if owner is not None:
            entry["owned_by_route"] = owner
        if findings:
            entry["unresolved"] = findings
            entry["authorable_surfaces"] = []
            unresolved_names.append(name)
        entries.append(entry)

    counts = {"numeric": 0, "decision": 0, "trymodify": 0}
    shapes = {"scalar-return": 0, "out-replacement": 0, "collection-edit": 0}
    for entry in entries:
        counts[entry["family"]] += 1
        shapes[entry["declaration_shape"]] += 1

    catalog = {
        "schema": SCHEMA,
        "host_version": HOST_VERSION,
        "framework_profile": "ritsulib-0.5.4-sts2-0.107.1",
        "source": {
            "definition": (
                "pinned STS2 0.107.1 decompile: Core/Models/AbstractModel.cs declarations, "
                "Core/Hooks/Hook.cs dispatchers, Core/Models/** vanilla overrides"
            ),
            "projection": "python collect_model_hooks.py extract",
            "note": (
                "Generated projection of a maintainer-only decompile; never hand-edit it. "
                "The decompile's DLL provenance sidecar was not retained, so recheck any "
                "fact against the pinned assembly or installed game before promoting it "
                "into authoring instruction."
            ),
        },
        "listener_sets": {
            "run": list(RUN_ONLY_LISTENERS),
            "combat": list(COMBAT_LISTENERS),
            "note": (
                "Reachability is decided by which listener set the dispatching iterator "
                "walks. The run-scope set carries no Powers, Orbs, or Monsters, so a "
                "run-only hook overridden on a Power compiles and never fires."
            ),
        },
        "iterator_forms": {
            form: {"scope": scope, "listener_families": list(families)}
            for form, (scope, families) in sorted(ITERATORS.items())
        },
        "declaration_shapes": {
            **shapes,
            "note": (
                "A collection-edit hook mutates a host-owned list and its bool reports only "
                "that it was touched. It cannot be declared as a replacement value, so it "
                "needs an add/remove declaration with a composition rule."
            ),
        },
        "counts": {
            **counts,
            "total": len(entries),
            "unresolved": len(unresolved_names),
        },
        "unresolved_hooks": unresolved_names,
        "reachability_contradictions": contradictions,
        "hooks": entries,
    }
    catalog["catalog_sha256"] = catalog_digest(catalog)
    return catalog


def default_catalog_path() -> Path:
    return TOOLS_DIR.parent / "skills" / "sts2-api" / CATALOG_RELATIVE_PATH


def cmd_extract(args: argparse.Namespace) -> int:
    catalog = build_catalog()
    destination = Path(args.output) if args.output else default_catalog_path()
    rendered = json.dumps(catalog, ensure_ascii=False, indent=2) + "\n"

    if args.check:
        if not destination.is_file():
            print(f"[model-hooks] missing catalog: {destination}", file=sys.stderr)
            return 1
        if destination.read_text(encoding="utf-8") != rendered:
            print(
                f"[model-hooks] {destination} is stale; re-run "
                f"`collect_model_hooks.py extract`",
                file=sys.stderr,
            )
            return 1
        print(f"[model-hooks] catalog is current: {destination}")
        return 0

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(rendered, encoding="utf-8")
    counts = catalog["counts"]
    print(
        f"[model-hooks] wrote {counts['total']} hooks "
        f"(numeric={counts['numeric']} decision={counts['decision']} "
        f"trymodify={counts['trymodify']} unresolved={counts['unresolved']})"
    )
    if catalog["reachability_contradictions"]:
        print(
            f"[model-hooks] {len(catalog['reachability_contradictions'])} reachability "
            f"contradiction(s); reachability derivation needs repair before promotion:",
            file=sys.stderr,
        )
        for line in catalog["reachability_contradictions"]:
            print(f"  - {line}", file=sys.stderr)
    print(str(destination))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    extract = subparsers.add_parser(
        "extract", help="project the pinned hook surface into the committed catalog"
    )
    extract.add_argument("--output", help="override the catalog destination")
    extract.add_argument(
        "--check",
        action="store_true",
        help="fail when the committed catalog is stale instead of rewriting it",
    )
    extract.set_defaults(func=cmd_extract)
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except ModelHookError as exc:
        print(f"[model-hooks] failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
