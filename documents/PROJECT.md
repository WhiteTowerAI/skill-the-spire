# Skill the Spire project

## Product

Skill the Spire is a free Codex plugin that turns a plain-language request into a working Slay the
Spire 2 Mod. The user-facing product name is Skill the Spire; the repository, plugin, and
marketplace slug is `skill-the-spire`. The shipped skills are `modmaker` and `sts2api`.

Version `0.1.0` is the first public release. It targets STS2 stable `0.107.1` and the RitsuLib
`0.5.11` authoring/API baseline.

## Experience

A user describes a Mod in ordinary language. The skill resumes existing work when present,
otherwise chooses a fast, co-design, or revision path and asks only questions that materially
change the result.

```text
idea -> concise DESIGN -> implementable SPEC -> thin capability preflight
     -> scaffold and author -> Build -> Tier 1 -> Tier 2
     -> headed review when needed -> direct report
```

`DESIGN.md` owns player intent, accepted decisions, current scope, and `Not Now` items. `SPEC.md`
is the sole implementation work order. `PLAN.md` is a simple stage checklist. `MEMORY.md` stores
technical discoveries and exact command results.

## Architecture

- `games/sts2/skills/modmaker/`: workflow and per-surface routing.
- `games/sts2/skills/sts2api/`: lazy design knowledge, recipes, API references, catalogs, and
  diagnostics.
- `games/sts2/tools/`: cross-platform generation, build, verification, localization, art, and
  catalog tooling.
- `games/sts2/tests/`: current capability and verification ownership.
- `scripts/publish/`: deterministic payload rendering and plugin metadata.
- `plugins/skill-the-spire/`: generated Codex plugin.
- `skills/`: generated portable Agent Skills distribution.

Authoritative changes happen under `games/sts2/` and `scripts/publish/`. Generated payloads are
replaced only through `publish.sh`.

## Runtime Profile

Generated projects target STS2 `0.107.1`, compile against a validated local RitsuLib Compat
`0.5.11` assembly, and require `STS2-RitsuLib >= 0.5.11` at runtime. They use bundled Godot.NET
SDK imports and local game/runtime assemblies, with no framework `PackageReference` and no
BaseLib dependency.

The official RitsuLib Workshop item is `3747602295`. Exact host, Compat, version, and assembly
identity checks prevent accidental compilation against another profile.

## Product Boundary

The authoritative inventory is `games/sts2/tests/content-capability-graph.md`. It separates:

- what the pinned public/fixed profile can express;
- what the shipped skills can author; and
- what an actual real-host scenario observed.

Generated code may combine public STS2/RitsuLib APIs, ordinary C#/BCL, Mod-owned helpers/state,
and maintained fixed Adapters. Prompt-derived Harmony, reflection, Publicizer, and IL are outside
the product. Missing shared authoring knowledge blocks generation until repaired or narrowed.

The product includes new content and world surfaces, bounded behavior/state/resources,
presentation and art routes, ordinary effect primitives, model-hook participation, and selected
vanilla override families. Exact restrictions stay with their recipes and capability rows rather
than a parallel management ledger.

## Localization And Presentation

A Mod with no localization tables is language-neutral. Once any table exists, `eng` and `zhs`
must have identical tables, keys, SmartFormat token multisets, and nonempty values. Build owns the
static check; the real host owns consumer resolution.

Art normalization and Character art bundles are code-owned. Placeholder art is the default.
External or paid image generation is selected only with explicit user choice. Bundled STS2 art
samples are reference-only and retain their original ownership.

## Verification

Build proves compilation and static packaging. Tier 1 proves load identity and absence of a fresh
error block. Tier 2 proves exact structured state in the real host plus `selftest done`. Headed
review proves only what a person actually observed. Every report names failed and unrun checks
directly.

## Distribution

The repository publishes one Codex plugin and one portable skills tree from the same authoritative
source. Releases use strict SemVer, deterministic publisher output, plugin/skill validators,
payload layout and parity checks, Python compilation, the complete owned source suite, and
`git diff --check`.
