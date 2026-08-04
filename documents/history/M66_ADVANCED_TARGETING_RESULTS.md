# M6.6 Package 1 advanced targeting results

Date: 2026-07-29

Environment: Windows, STS2 stable `0.107.1`, RitsuLib `0.4.62`, compat `0.107.1`, and a
generated runtime dependency on `STS2-RitsuLib >= 0.4.62` only.

## Outcome

The bounded Package 1 advanced creature-targeting slice is pipeline-supported for:

- a single-target Card;
- a single-target Potion; and
- a multi-target Card.

Generated Mods may register one stable Mod-local target identity backed by a deterministic
live-`Creature` predicate. Single-target predicates may read the candidate, acting player,
and declared source Card/Potion context. Multi-target predicates may read the candidate and
acting player. The normal native mouse/controller selection, cancellation, Card payment and
result pile, Potion belt lifecycle, and target reticles remain host-owned.

Custom multi-target Potions remain unsupported. On the pinned host/framework,
`UsePotionAction` accepts their `null` queued target and does not recheck an empty resolved
group before `OnUseWrapper` removes the Potion. Generated Mods must stop authoring that
combination instead of emitting Harmony, reflection, IL, Publicizer, or consume-and-restore
behavior.

## Pipeline contract

The pipeline now records consumer, one/many mode, stable target ID, candidate conditions,
acting-player conditions, optional single-target source conditions, zero-target behavior,
and exact resolution. The grounded recipe requires:

- one immediate target registration before deferred content construction;
- pure Boolean predicates with explicit alive/side conditions;
- selected-creature revalidation before single-target Card payment or Potion removal;
- live `GetTargets()` resolution inside a multi Card's `OnPlay`;
- a zero-target `IsPlayable` gate for multi Cards; and
- normal Card/Potion lifecycle with no cached creature references.

The semantic-contract regression test locks the required consumer/mode/ID fields, public
registration and resolution routes, ordering and revalidation rules, headed-check ownership,
and the unsupported `potion + many` stop condition across the source guidance. It is a
documentation contract gate, not a standalone generated-project validator.

## Automated evidence

- all 119 tools tests pass;
- source, plugin, and portable Python files compile;
- all six source/plugin/portable skill roots pass `quick_validate.py`;
- regenerated plugin and portable payloads each contain 148 shared files after excluding
  `__pycache__` and portable-only `GENERATED.md`;
- their relative paths and file contents have zero mismatch and the same aggregate SHA-256,
  `B885295D723E59EA61EB3A90D51996D5B416C5C922BEBEA14FFCA1511883FE75`; and
- `git diff --check` reports no whitespace error.

These checks prove the semantic and delivery contracts. They do not replace the hosted
selection and lifecycle evidence below or manufacture a strict Tier 2 result.

## Focused host

The disposable `M66TargetingProof` Mod registered four real consumers:

| Consumer | Role | Effect |
|---|---|---|
| `PrimeBlock` | setup Card | give one selected enemy 8 Block |
| `FocusedBreach` | source-aware single Card | select only a blocking enemy; deal 3 damage |
| `CrackFlask` | player-aware single Potion | select only a blocking enemy; deal 4 damage |
| `ShieldSweep` | player-aware multi Card | deal 2 damage once to every blocking enemy |

The deployed proof artifacts were:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `M66TargetingProof.dll` | 20,480 | `9F2715C2E9EBD2F1D2A3322EF23C0C72D18580342B5630BA62CFCA5E02C1DF0E` |
| `M66TargetingProof.json` | 361 | `84B082642FC5E64A239F5D03C2496F0B808CA73E192CE6981A4B81B40467F721` |
| `M66TargetingProof.pck` | 1,021 | `303D6E1630612BF4443DAB59C1A4D0B5A2CD12FB47443554D185C2E7D85BF267` |
| `M66TargetingProof.pdb` | 14,000 | `419D8093C928F9F040DA8B2B7ADAF6A39978BE46D2A359F254FA946F44D9BFC4` |

## Headed acceptance

The human lead reported all six requested groups normal and successful:

- zero-candidate Card/Potion rejection, unchanged payment/inventory, and clean cancel UI;
- mouse single-target filtering, invalid-enemy rejection, cancellation, and normal use;
- controller single-target filtering, invalid-enemy rejection, cancellation, and normal use;
- mouse multi-target reticles, one resolution per candidate, and cleanup;
- controller multi-target reticles, one resolution per candidate, and cleanup; and
- normal Card discard/Potion removal with no visible anomaly.

The exact observed setup/effect sequence was `8 -> 5 -> 1` for mouse single-target use,
`9 -> 6 -> 2` for controller single-target use, then two multi-target Card resolutions over
both enemies. The current `godot.log` corroborated:

- the exact `M66TargetingProof` load marker with RitsuLib `0.4.62`, host `0.107.1`, and
  compat `0.107.1`;
- all four deferred content registrations;
- `FocusedBreach` records `8->5` and `9->6` on creature `1`;
- `CrackFlask` records `5->1` and `6->2` on creature `1`;
- two `ShieldSweep` records with `targets=[1,2] count=2`; and
- no fresh target-Mod error block after load.

The log does not encode rejected targets, cancellation, input device, reticle appearance,
or post-resolution UI cleanup. Those claims are owned by the human lead's headed
observation.

After recording the headed result, current-run log evidence, artifact hashes, and delivery
checks, the disposable
`C:\Users\YY\AppData\Local\Temp\OpenModM66TargetingProofWork` project and deployed
`mods/M66TargetingProof` directory were deleted. They are retired proof artifacts, not
maintained product sources or future regression hosts.

## Verification exception

The proof intentionally had no automated hosted harness. It emitted no structured terminal
state proof and no `selftest done`, so strict Tier 2 was not run and is not reported as a
pass. The manual matrix also did not enqueue a valid single target and invalidate it before
execution, or enqueue a multi Card and remove every valid candidate before execution.
Those resolution-time cancellation cases remain explicit verification exceptions. They do
not broaden the supported consumer matrix or permit a multi-target Potion.

## Remaining boundary

Selecting Cards, corpses, map nodes, or arbitrary objects; target predicates with mutation,
RNG, logging, or retained creature references; source-aware multi-target registration;
global interoperability registration; custom targeting UI layouts; multiplayer-specific
presentation; and custom multi-target Potions remain unsupported.
