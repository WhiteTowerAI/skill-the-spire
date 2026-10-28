#!/usr/bin/env python3
"""Reject generated Mod source that bypasses the pack's public routes.

Prose in the pack says never to generate prompt-derived Harmony, reflection, Publicizer, or IL,
and never to add `[Pool(...)]`. Nothing checked either, and a cheap model follows a long list of
prohibitions less reliably than a failing Build. This scan runs before MSBuild over the Mod's own
`.cs` files and its `.csproj`:

- `[Pool(...)]`: the content-pack pool generic is the only availability declaration.
- raw Harmony (`new Harmony`, `[HarmonyPatch]`, `AccessTools`, `Traverse`, transpilers, IL
  instructions) and member reflection (`BindingFlags`, `typeof(T).GetMethod(...)`,
  `System.Reflection.Emit`, `InvokeMember`): no public route needs them.
- Publicizer and `IgnoresAccessChecksTo`: they open private members.
- RitsuLib `IPatchMethod` classes: every `ModPatchTarget` must name a reviewed Adapter method
  from the pinned vanilla catalog, so a fixed override route passes and a prompt-derived patch
  does not.

Every Mod is multiplayer-safe: each peer runs the same actions and must reach the same state.
Three lockstep breakers are checkable:

- process-local nondeterminism (`System.Random`, Godot `GD.Rand*`/`RandomNumberGenerator`,
  `Guid.NewGuid`, wall-clock time, `Stopwatch`, `Environment.TickCount`) anywhere outside
  `SelfTestScenarios.cs`: gameplay draws from the game or Mod run RNG streams.
- `LocalContext.GetMe`/`LocalContext.NetId` inside a gameplay model class: they name this
  machine's player, not the model's `Owner`. `LocalContext.IsMe(Owner)` stays allowed as a
  local-presentation guard.
- a mutable static field in a gameplay model class: one process holds every player's models,
  so static state leaks between players and is never synchronized.

The fixed `SelfTestKit.cs` is checked separately by `selftest_kit.py` and skipped here. Reading
the loaded framework's assembly metadata (as the scaffolded load marker does) is not member
reflection and passes. The compiler and Tier 2 still own everything else.
"""
from __future__ import annotations

import re
from pathlib import Path

import selftest_kit

SKIPPED_DIRS = {"bin", "obj", "skillthespire"}

RULES: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\[\s*Pool\s*\("),
     "`[Pool(...)]`: declare availability only through the content-pack pool generic"),
    (re.compile(r"\bnew\s+Harmony\s*\(|\bHarmony\s*\.\s*CreateAndPatchAll\b"),
     "a raw Harmony instance: install only reviewed Adapters through RitsuLibFramework.CreatePatcher"),
    (re.compile(r"\[\s*Harmony(?:Patch|Prefix|Postfix|Transpiler|Finalizer)\b"),
     "a Harmony patch attribute: install only reviewed Adapters through IPatchMethod"),
    (re.compile(r"\bAccessTools\b|\bTraverse\s*\.\s*Create\b"),
     "Harmony reflection helpers"),
    (re.compile(r"\bTranspiler\s*\(|\bCodeInstruction\b|\bILGenerator\b|\bDynamicMethod\b"
                r"|\bSystem\s*\.\s*Reflection\s*\.\s*Emit\b"),
     "IL generation or rewriting"),
    (re.compile(r"\bBindingFlags\b|\.\s*InvokeMember\s*\("
                r"|(?:\btypeof\s*\([^()]*\)|\bGetType\s*\(\s*\))\s*\.\s*Get"
                r"(?:Method|Field|Property|Member|Constructor|NestedType|Event)s?\s*\("),
     "member reflection: use the pinned public API"),
    (re.compile(r"\bIgnoresAccessChecksTo\b"),
     "IgnoresAccessChecksTo: private members are off limits"),
)
CSPROJ_RULE = (re.compile(r"Publiciz|IgnoresAccessChecksTo"),
               "a Publicizer: private members are off limits")

# Peers diverge on any of these; SelfTestScenarios.cs (verification only) may read time.
NONDETERMINISM_RULE = (
    re.compile(r"\bSystem\s*\.\s*Random\b|\bnew\s+Random\s*\(|\bRandom\s*\.\s*Shared\b"
               r"|\bGD\s*\.\s*Rand\w*\b|\bRandomNumberGenerator\b|\bGuid\s*\.\s*NewGuid\b"
               r"|\bDateTime(?:Offset)?\s*\.\s*(?:Now|UtcNow|Today)\b|\bStopwatch\b"
               r"|\bEnvironment\s*\.\s*TickCount"),
    "process-local randomness or time differs per multiplayer peer: draw from the game or "
    "Mod run RNG (reference/lifecycle-state-rng.md)",
)
SCENARIOS_FILE = "SelfTestScenarios.cs"

# A class that ModelDb instantiates once per owning player.
GAMEPLAY_MODEL_RE = re.compile(
    r"\bclass\s+\w+(?:<[^>{]*>)?\s*:\s*(?:[\w.]+\.)?(?:Mod\w+Template|HookedSingletonModel|ModCustomReward"
    r"|CardModel|RelicModel|PotionModel|PowerModel|OrbModel|EnchantmentModel|AfflictionModel"
    r"|MonsterModel|EncounterModel|EventModel|AncientEventModel|ModifierModel)\b"
)
LOCAL_PLAYER_RULE = (
    re.compile(r"\bLocalContext\s*\.\s*(?:GetMe\s*\(|NetId\b)"),
    "LocalContext names this machine's player: gameplay uses the model's Owner "
    "(LocalContext.IsMe(Owner) may only gate local presentation)",
)
# Handles registered once and keyed by run/player/model inside; never per-player state.
STATIC_HANDLE_TYPES = ("RunSavedData", "PlayerRunSavedData", "ModelSavedData",
                       "SavedAttachedState", "AttachedState")
MUTABLE_STATIC_RE = re.compile(
    r"^[ \t]*(?:(?:private|public|internal|protected|new|volatile)\s+)*static\s+"
    r"(?!readonly\b|class\b|async\b|void\b|partial\b|extern\b|event\b)"
    r"(?P<type>[\w.]+(?:<[^;=(){}]*>)?\??(?:\[\])?)\s+\w+\s*(?:=(?!>)|;)",
    re.MULTILINE,
)
MUTABLE_STATIC_REASON = (
    "a mutable static field in a gameplay model is shared by every player in this process and "
    "never synchronized: keep state on the model or in a run/player saved-data slot"
)

PATCH_CLASS_RE = re.compile(r"\bIPatchMethod\b")
# new(typeof(Type), nameof(Type.Method) | "Method", ...[, MethodType.Getter])
PATCH_TARGET_RE = re.compile(
    r"\btypeof\s*\(\s*(?P<type>[\w.]+)\s*\)\s*,\s*"
    r"(?:nameof\s*\(\s*(?:[\w.]+\.)?(?P<nameof>\w+)\s*\)|\"(?P<literal>\w+)\")"
)
ACCESSOR_RE = re.compile(r"\bMethodType\s*\.\s*(?P<kind>Getter|Setter)\b")
COMMENT_RE = re.compile(r"//[^\n]*|/\*.*?\*/", re.DOTALL)


class SourceScanError(ValueError):
    """Mod source uses a forbidden route."""


def _strip_comments(text: str) -> str:
    # Keep line breaks so reported line numbers stay exact.
    return COMMENT_RE.sub(lambda match: "\n" * match.group(0).count("\n"), text)


def mod_sources(project_dir: Path, mod_name: str) -> list[Path]:
    kit = selftest_kit.kit_path(project_dir, mod_name).resolve()
    sources = []
    for path in sorted(project_dir.rglob("*.cs")):
        relative = path.relative_to(project_dir).parts
        if any(part in SKIPPED_DIRS or part.startswith(".") for part in relative[:-1]):
            continue
        if path.resolve() == kit:
            continue
        sources.append(path)
    return sources


def patch_targets(code: str) -> list[tuple[str, str, int]]:
    """(simple type name, CLR method name, line) for each ModPatchTarget in the code."""
    targets = []
    for match in PATCH_TARGET_RE.finditer(code):
        method = match.group("nameof") or match.group("literal")
        tail = code[match.end():match.end() + 200]
        tail = re.split(r"\bnew\b|\btypeof\s*\(\s*[\w.]+\s*\)\s*,\s*(?:nameof|\")", tail)[0]
        accessor = ACCESSOR_RE.search(tail)
        if accessor:
            method = f"{'get' if accessor.group('kind') == 'Getter' else 'set'}_{method}"
        line = code.count("\n", 0, match.start()) + 1
        targets.append((match.group("type").rsplit(".", 1)[-1], method, line))
    return targets


def reviewed_adapter_methods(catalog: dict) -> set[tuple[str, str]]:
    return {
        (adapter["type"].rsplit(".", 1)[-1], adapter["method"])
        for adapter in catalog.get("adapters", [])
    }


def _multiplayer_findings(name: str, file_name: str, code: str) -> list[str]:
    findings = []

    def add(match: re.Match[str], reason: str) -> None:
        findings.append(f"{name}:{code.count(chr(10), 0, match.start()) + 1}: {reason}")

    if file_name != SCENARIOS_FILE:
        pattern, reason = NONDETERMINISM_RULE
        for match in pattern.finditer(code):
            add(match, reason)
    if GAMEPLAY_MODEL_RE.search(code):
        pattern, reason = LOCAL_PLAYER_RULE
        for match in pattern.finditer(code):
            add(match, reason)
        for match in MUTABLE_STATIC_RE.finditer(code):
            if not match.group("type").startswith(STATIC_HANDLE_TYPES):
                add(match, MUTABLE_STATIC_REASON)
    return findings


def scan(project_dir: Path, mod_name: str, *, catalog: dict | None = None) -> list[str]:
    """Return one finding per forbidden use; empty when the Mod source is clean."""
    findings: list[str] = []
    patch_files: list[tuple[Path, str]] = []
    for path in mod_sources(project_dir, mod_name):
        code = _strip_comments(path.read_text(encoding="utf-8", errors="replace"))
        name = path.relative_to(project_dir).as_posix()
        for pattern, reason in RULES:
            for match in pattern.finditer(code):
                line = code.count("\n", 0, match.start()) + 1
                findings.append(f"{name}:{line}: {reason}")
        findings.extend(_multiplayer_findings(name, path.name, code))
        if PATCH_CLASS_RE.search(code):
            patch_files.append((path, code))
    for csproj in sorted(project_dir.glob("*.csproj")):
        pattern, reason = CSPROJ_RULE
        if pattern.search(csproj.read_text(encoding="utf-8", errors="replace")):
            findings.append(f"{csproj.name}: {reason}")
    if patch_files:
        if catalog is None:
            from vanilla_overrides import load_catalog
            catalog = load_catalog()
        reviewed = reviewed_adapter_methods(catalog)
        for path, code in patch_files:
            name = path.relative_to(project_dir).as_posix()
            targets = patch_targets(code)
            if not targets:
                findings.append(
                    f"{name}: IPatchMethod targets are unreadable; write each as "
                    "new(typeof(Type), nameof(Type.Method), ...)"
                )
            for type_name, method, line in targets:
                if (type_name, method) not in reviewed:
                    findings.append(
                        f"{name}:{line}: patch target {type_name}.{method} is not a reviewed "
                        "Adapter in the pinned catalog; use a public route or a Mod-local route"
                    )
    return findings


def validate_project_sources(project_dir: Path, mod_name: str, *, catalog: dict | None = None) -> str:
    findings = scan(project_dir, mod_name, catalog=catalog)
    if findings:
        shown = "; ".join(findings[:8])
        more = f" (+{len(findings) - 8} more)" if len(findings) > 8 else ""
        raise SourceScanError(f"Mod source uses a forbidden route: {shown}{more}")
    return f"{len(mod_sources(project_dir, mod_name))} source files clean"
