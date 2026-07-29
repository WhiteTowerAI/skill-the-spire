# STS2 verification ownership

Completed migration evidence is archived in
`documents/history/RITSULIB_MIGRATION_RESULTS.md`. Current claims are defined by
`content-capability-graph.md` and focused tests under `games/sts2/tools/tests/`.
The focused M6.6 computed-Card result is archived in
`documents/history/M66_COMPUTED_VALUES_RESULTS.md`.
The failed initial native Ancient-dialogue proof, repair, and successful recheck are recorded in
`documents/history/M66_ANCIENT_DIALOGUE_RESULTS.md`.
The bounded advanced-targeting proof and its manual-verification exception are recorded in
`documents/history/M66_ADVANCED_TARGETING_RESULTS.md`.

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
| `CombatPlayer` | content core, computed Card values, advanced targeting, stateful relics, Scry, Character combat cues |
| `CombatEnemy` | Monster + Encounter, move vocabulary, combat/bestiary body |
| `MapNode` / Character | Event outcomes/presentation, bounded forced follow-up, native Ancient/Architect dialogue |
| `RunStart` / Character | Foundation, static art/theme, combat cues, resource/UI, ordered buffer |

Tier 1 requires the exact load marker and no fresh error block. Tier 2 requires a
structured post-state proof and `selftest done`. Trigger logs, terminal markers, and
model-only state are diagnostics, not behavior proof.

The M6.6 Package 2A proof is an explicit exception: the human lead accepted its complete
manual behavior/presentation matrix after Tier 1, while the structured Tier 2 harness was
not run. Preserve that wording; do not report the omitted harness as passed.

Package 5 has the same explicit boundary. Its first headed Darv/Architect run failed, then
the repaired proof passed the human lead's visible native-flow recheck and the current log
showed the mounted PCK, both routes, clean progression, and no fresh error block. The log
did not contain the structured state proof or `selftest done`; strict Tier 2 remains an
exception rather than a pass.

Package 1 also uses that explicit boundary. The human lead accepted its complete zero-,
single-, and multi-candidate mouse/controller matrix, while current-run logs corroborated
the exact successful consumers and no fresh error block. No automated `selftest done`
harness ran, and queued-target invalidation was not exercised; strict Tier 2 remains an
exception rather than a pass.

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
