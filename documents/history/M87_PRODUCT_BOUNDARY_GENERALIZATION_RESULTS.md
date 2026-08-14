# M8.7 Product Boundary Generalization Results

## Status

M8.7 is closed. The human lead explicitly accepted and closed the Package on 2026-08-14.

The implementation was delivered earlier in authoritative source and both generated payload forms.
This record closes the outstanding documentation and human-acceptance gate; it does not reimplement
the Package or infer runtime evidence that never ran.

## Profile And Evidence Boundary

- Target game: STS2 stable `0.107.1`.
- Authoring/API baseline at closure: RitsuLib/Compat `0.5.11` and .NET 9.
- Primary implementation commit: `37219cf7dbf077e987def771596aa030e55edb2f`.
- The later workflow simplification in `adcd957a4603c2e94ddf2f63875635b9e4b4c099`
  retained the generalized capabilities while removing management-heavy contracts.
- The M8.8 closeout in `69c1ead` preserved all nine M8.7 families and synchronized the current
  authoritative source and both payload forms.

`framework-expressible`, `open-mod-authorable`, and `game-observed` remain independent facts.
The public/fixed profile and maintained authoring routes establish the first two facts for the
admitted boundaries below. No M8.7-specific generated-Mod Build, Tier 1, Tier 2, headed review,
game launch, install, save/load, or gameplay run occurred. Newly generalized variants therefore
remain `game-unobserved`.

## Closed Product Boundary

M8.7 replaced early proof-fixture restrictions with reusable bounded authoring contracts for nine
families:

| Family | Closed authoring result | Retained boundary |
|---|---|---|
| Secondary resources and payment/UI | One or more named bounded RitsuLib resources, declared combat/run and turn-start policies, fixed/X required/optional/extra payment, and selected supported counter/Card UI | Native Energy remains separate; payment precedes payoff; repeatable-extra X and multiplayer remain excluded |
| Monster moves, Encounter composition, and HP ranges | Deterministic, conditional, or supplied-RNG weighted move graphs; independently reusable Monster/Encounter nodes; checked actual/all-possible rosters; positive ordered HP ranges | Dynamic prompt-authored weight delegates, ungrounded placement, and inferred range-distribution proof remain excluded |
| Character starting fields | Current-SPEC HP, Gold, MaxEnergy, Orb slots, typed pools, and starter Card/Relic/Potion multisets | Values and starters must be game-valid and resolve through the registered typed graph |
| Card- or Relic-owned Rest Site options | Card and Relic owners share the public hook/template route with truthful owner/state handles and deterministic preflight | Singleplayer and existing transaction/lifecycle limits remain; M8.7 did not admit a generic Modifier owner |
| Multiple computed Card values | Zero or more uniquely named bounded formulas with independent inputs, upgrades, text binding, preview/execution parity, and typed execution reads | No RNG, mutation, hidden inputs, or duplicate native-hook application |
| Reusable bounded state | Closed scalar/transition vocabulary with explicit owner, lifetime, reset, persistence, visibility, consumers, outputs, and grounded hooks | Arbitrary executable state machines, unsupported saved types, retained Card instances, and invented refresh routes remain excluded |
| Bounded forced Event mappings | Finite prioritized act-set/custom-Event mappings or sequences with saved index, exact terminal consumption, pool exclusion, neutral returns, and fail-closed conflicts | Singleplayer only; no canonical-cache mutation, fixed map-node guarantee, or inferred save/resume observation |
| Native Star costs for new Cards | Independent native Energy and fixed-or-X Star declarations, upgrades, text/icons, and payment flags | No parallel Star store; simultaneous Energy-X and Star-X remain excluded pending grounded replay/payment semantics |
| Event acquisition and shake profiles | Ordered unique known Card/relic acquisition with matching native consumers and one optional allowlisted shake profile | No duplicate/custom holder, arbitrary VFX, rumble, hit stop, custom target, or unbounded shake |

The exact current support rows remain in
`games/sts2/tests/content-capability-graph.md`. The lowering and lifecycle contracts remain owned by
the relevant `games/sts2/skills/modmaker/` surface pages and
`games/sts2/skills/sts2-api/` recipes/references. The classification evidence that preceded
implementation remains in `games/sts2/tests/m87-boundary-audit.md`.

## Preserved Non-Goals

M8.7 did not generalize keyword icons, broader target predicates, per-frame hand emphasis,
parameterized Character combat cues, multiplayer, arbitrary custom UI/VFX, physical retained-Card
zones, cross-Mod conflict coordination, or generated Harmony/reflection/Publicizer/IL. A missing
public/fixed route continues to block authoring instead of receiving a consumer-local approximation.

M8.8 subsequently added other surface and lifecycle capabilities, but did not reopen, narrow, or
relabel these M8.7 results. M8.7 closure does not authorize or start M8.6.

## Delivery And Verification

The authoritative implementation and both generated payload forms were already committed before
closure. The existing unrelated modification to `plugins/open-mod/.codex-plugin/plugin.json` was
not part of this closeout and was preserved.

Closure-time checks on 2026-08-14:

- `$env:PYTHONUTF8='1'; python -m unittest discover -s games/sts2/tools/tests -p
  'test_*.py'`: `244` tests passed;
- `python -m compileall -q games/sts2/tools scripts/publish plugins/open-mod/skills skills`:
  passed;
- `git diff --check`: passed on the final closeout diff.

These checks protect the current integrated repository state. They are not retroactive M8.7
runtime evidence and do not change any `game-observed` label.

## Closure Decision

On 2026-08-14 the human lead explicitly stated that M8.7 is closed. With the implemented source,
committed payload forms, this durable result record, synchronized active status, and literal
evidence boundaries above, no M8.7 work remains open.
