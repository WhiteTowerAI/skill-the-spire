# STS2 verification

This directory contains the **current** verification model and support graph. Completed
run transcripts and retired canary/audit documents live in `documents/history/`.

## Keep it lean

Do not require one canary project per capability.

1. Use lightweight contract checks for deterministic formulas and state rules.
2. Reuse the closest hosted live suite.
3. Keep a separate project when it is genuinely clearer or isolates a distinct host risk.
4. Treat fresh acceptance mods as disposable after evidence capture unless they become the
   canonical suite.

## Hosted suites

| Host | Current canonical coverage |
|---|---|
| `CombatPlayer` | basic content matrix, interaction, keyword, enchantment, orb, cadence |
| `CombatEnemy` | encounter and monster move vocabulary |
| `MapNode` | event option UI and consequence |
| `RunStart` / Character | Wayfinder selection, pools/starters, resource/UI, semantic route buffer, dynamic output |

Wayfinder supersedes the isolated Foundation/resource/kernel composition path for current
character regression. The retired real-card `CustomPile` canary remains historical evidence
only; it does not represent player-facing support.

## Proof rule

```text
setup -> enter real host -> drive real source -> observe post-state -> terminal
```

- Tier 1: exact load marker plus no fresh error block.
- Tier 2: structured state proof plus `selftest done`.
- A trigger/preview log or terminal marker alone never proves behavior.
- Custom presentation requires a player-visible invariant; model state alone is
  insufficient.

The direct M6 art follow-up reuses these same hosts. An art claim additionally requires the
exact packed resource/scene to render in the headed game, with a screenshot or equivalent
visual assertion that distinguishes it from the fallback. Build success and resource-path
logs alone do not prove art. Extend a hosted suite when practical; there is still no
one-project-per-art-type rule.

Run only one armed harness mod at a time because `--t2selftest` arms every loaded harness.

## Commands

```bash
python games/sts2/tools/build.py --project-dir <project> --mod-name <ModName>
python games/sts2/tools/launch.py
python games/sts2/tools/grep_log.py --mod-name <ModName>
python games/sts2/tools/launch.py --self-test --mod-name <ModName>
python games/sts2/tools/grep_log.py --mod-name <ModName> \
  --tier2-pattern "<structured state proof>"
```

Current capability claims are in `content-capability-graph.md`. Historical exact markers,
failures, and repair chronology are indexed by `documents/history/README.md`.
