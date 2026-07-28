# STS2 verification ownership

Completed migration evidence is archived in
`documents/history/RITSULIB_MIGRATION_RESULTS.md`. Current claims are defined by
`content-capability-graph.md` and focused tests under `games/sts2/tools/tests/`.

## Model

1. Use local assertions for deterministic calculations, state transitions, payment floors,
   capacity, ordering, and reset rules.
2. Reuse the closest real host for lifecycle behavior and presentation.
3. For an ordinary feature or bug fix, stop after the changed behavior is proved in that
   real host; do not add a complete demo-Mod run to every change.
4. Use a fresh natural-language acceptance Mod only when the active implementation plan
   schedules a full user-pipeline gate or the human lead requests one, then retire it after
   recording the outcome.

Host ownership:

| Host | Owns |
|---|---|
| `CombatPlayer` | content core, stateful relics, Scry, Character combat cues |
| `CombatEnemy` | Monster + Encounter, move vocabulary, combat/bestiary body |
| `MapNode` | Event outcomes/presentation and bounded forced follow-up |
| `RunStart` / Character | Foundation, static art/theme, combat cues, resource/UI, ordered buffer |

Tier 1 requires the exact load marker and no fresh error block. Tier 2 requires a
structured post-state proof and `selftest done`. Trigger logs, terminal markers, and
model-only state are diagnostics, not behavior proof.

Run one armed harness at a time. Preserve and restore unrelated user Mods. Do not reopen a
completed host proof unless a later source change exposes a real regression.

## Commands

```powershell
python games/sts2/tools/build.py --project-dir <project> --mod-name <ModName>
python games/sts2/tools/launch.py
python games/sts2/tools/grep_log.py --mod-name <ModName>
python games/sts2/tools/launch.py --self-test --mod-name <ModName>
python games/sts2/tools/grep_log.py --mod-name <ModName> --tier2-pattern "<structured state proof>"
```

Completed acceptance evidence is historical. Future bug fixes still require verification
proportional to the changed behavior; an earlier acceptance result is not a blanket
substitute for regression testing.
