# STS2 verification ownership

Completed migration evidence is archived in
`documents/history/RITSULIB_MIGRATION_RESULTS.md`. Current claims are defined by
`AGENTS.md`, `content-capability-graph.md`, and focused tests under
`games/sts2/tools/tests/`.
The focused M6.6 computed-Card result is archived in
`documents/history/M66_COMPUTED_VALUES_RESULTS.md`.
The failed initial native Ancient-dialogue proof, repair, and successful recheck are recorded in
`documents/history/M66_ANCIENT_DIALOGUE_RESULTS.md`.
The bounded advanced-targeting proof and its manual-verification exception are recorded in
`documents/history/M66_ADVANCED_TARGETING_RESULTS.md`.
The Package 4 CardPile/ExtraHand result is retained in
`documents/history/M66_CARD_PILE_EXTRA_HAND_RESULTS.md` as repository-only experimental
evidence. It is not a current support claim or a formal skill route.

## Model

Support is not a test result. Official product semantics plus the pinned public RitsuLib
profile establish support for a documented Package and its public consumers. Tests and
real-host runs report what actually worked; missing proof stays visible but does not make a
public Package unsupported.

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
| `CombatPlayer` | content core, computed Card values, hand emphasis, Relic/Power extra labels, advanced targeting, stateful relics, Scry, Character combat cues |
| `CombatEnemy` | Monster + Encounter, move vocabulary, combat/bestiary body |
| `MapNode` / Character | Event outcomes/presentation, bounded forced follow-up, native Ancient/Architect dialogue |
| real Rest Site / `MapNode` | Relic-owned option absence/gray/payment/stay/repeat/icon matrix |
| `RunStart` / Character | Foundation, static art/theme, combat cues, resource/UI, ordered buffer |

Tier 1 requires the exact load marker and no fresh error block. Tier 2 requires a
structured post-state proof and `selftest done`. Trigger logs, terminal markers, and
model-only state are diagnostics, not behavior proof.

Use one representative real host for a shared Package lifecycle. Add separate cases only
for materially different behavior or presentation risks; do not create one support gate per
consumer merely to justify the Package name. State Tier 1, Tier 2, headed checks, waivers,
and skipped checks literally.

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

The bounded Package 3 Relic-owned Rest Site option slice is implemented after the
human lead accepted its focused native absence/gray/enabled/payment/outcome/stay/repeat/
controller/custom-icon/fallback matrix. Per lead instruction, no log read followed the
headed run, and no structured `selftest done` harness ran; the exact Tier 1 log gate and
strict Tier 2 remain explicit exceptions. The pinned dev-console `gold` command ignores
negative values, so future manual routes must use normal Shop spending for a low-Gold state
or a narrow proof driver for a render-time stale-payment check.

Package 2B/2C authoring is implemented. Its human-led hand/Relic/Power matrix and strict
Tier 1 passed after narrowing Power authoring to one top-left label; strict Tier 2 was not
run and remains an explicit exception.

Package 4 is excluded from formal verification ownership and generated payloads. Its
focused matrix passed only with a private RitsuLib lifecycle repair, while official `0.5.0`
does not provide the required behavior. Preserve the experiment and historical result, but
do not treat either as support or publication evidence.

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
