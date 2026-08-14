# Implementation plan: release and maintenance

## Current Baseline

Skill the Spire `0.1.0` is the first public release line. The product identity is:

- display name: Skill the Spire;
- repository, plugin, and marketplace slug: `skill-the-spire`;
- primary skill: `modmaker`;
- API skill: `sts2api`;
- STS2 target: `0.107.1`;
- RitsuLib authoring/API baseline: `0.5.11`.

Later releases use normal SemVer. Publisher output must never add a timestamp or cache-specific
build suffix to the public version.

## Generated-Mod Workflow

```text
request -> DESIGN.md -> SPEC.md -> capability preflight -> scaffold
        -> Author + SelfTest -> Build -> Tier 1 -> Tier 2
        -> headed review when needed -> direct report
```

The preflight stays narrow: selected support routes must exist, selected raw hooks must exist and
be declared by their cited route, declaration shapes must match, route-owned hooks cannot be
authored as raw participation, and the selected surface must be reachable by the dispatcher.

Recipes and references guide implementation. Scaffold and Build own static project validity. The
real host owns behavior. People own visual, controller, animation, audio, translation-quality, and
subjective judgments.

## Source Maintenance

1. Read current source ownership and capability guidance.
2. Check worktree and branch state before edits.
3. Change authoritative source under `games/sts2/` or publisher metadata under
   `scripts/publish/`.
4. Run the closest focused tests, then the full surviving suite.
5. Regenerate plugin and portable payloads through `publish.sh` only.
6. Run each publisher mode twice and compare paths and hashes using publisher-aware parity.
7. Validate the plugin manifest and both skill roots.
8. Run Python compilation outside generated payloads and `git diff --check`.
9. State every verification boundary literally.

## Release Gate

A release is eligible only when:

- product names, slugs, skill directories, prompts, URLs, and versions agree;
- the repository contains no development-only experiments, audit ledgers, closeout artifacts, or
  generated cache files;
- the complete product-owned test suite passes;
- plugin and portable generation are deterministic;
- plugin/portable shared content matches after intentional publisher projection;
- plugin and skill validators pass;
- the default branch contains the intended public tree and README;
- the tag points at the exact released commit; and
- the release notes distinguish source/static validation from unrun game verification.

Repository visibility changes only after these checks and the release artifact are complete.

## Change Policy

Keep changes proportional. Preserve supported behavior while simplifying its implementation.
Route a player-visible semantic change through user acceptance. Do not infer runtime evidence from
source, tests, compilation, or payload presence. Do not add repository infrastructure unless a
separate request selects it.
