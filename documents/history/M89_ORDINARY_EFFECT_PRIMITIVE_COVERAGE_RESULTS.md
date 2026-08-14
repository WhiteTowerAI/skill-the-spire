# M8.9 Ordinary Effect Primitive Coverage Results

## Status

M8.9 is closed. The human lead explicitly accepted and closed the Package on 2026-08-14.

The authoritative source/static stage and both generated payload forms were delivered before this
closure record. Closing M8.9 synchronized documentation only; it did not regenerate either
payload, install the skill, run the game, or start M8.6.

## Profile And Evidence Boundary

- Target game: STS2 stable `0.107.1`.
- Authoring/API baseline: RitsuLib/Compat `0.5.11` and .NET 9.
- RitsuLib source tag: `v0.5.11` at `8a2eb7c756d926287078f953f2fac1d47ec014b4`.
- Compat DLL SHA-256:
  `6c2f65d2245207226aba80d3ea83b928871bd6e9fb7584d28b2669e10d335413`.
- STS2 public assembly SHA-256:
  `a1f9e653f1e28e4076558fee1e60d218619cb7e057b887c6417f62c62c6d7a52`.
- Source and payload delivery commit: `97347099752256d220d8588203e496da2c22aca1`.

`framework-expressible`, `open-mod-authorable`, and `game-observed` remain independent facts.
Compile probes and public/fixed API research establish selected call-shape compatibility. Source,
tests, and synchronized payloads establish maintained authoring routes. None of those facts is
real-host or gameplay observation.

## Closed Result

M8.9 replaced repeated per-recipe command lookup with one maintained flow:

```text
SPEC effects.sequence -> selected surface callback -> reference/effect-primitives.md
                      -> exact owner/context/source/target binding -> ordered awaited commands
```

Nine ordinary player-result families are admitted:

1. attack or effect damage;
2. Block, healing, and bounded HP changes;
3. Power application, amount changes, and removal;
4. Energy, Stars, Gold, and potion-capacity changes;
5. ordinary Card draw;
6. discard or Exhaust of known combat Cards;
7. creation of a known Card in combat;
8. acquisition of a known Card, Relic, or Potion in a run; and
9. Orb channel/evoke and slot changes.

`games/sts2/skills/sts2-api/reference/effect-primitives.md` owns exact public/fixed lowerings,
required bindings, await/result behavior, neutral and partial outcomes, value bounds, lifecycle
limits, and rejection. Executable surface pages own only the callback values they truthfully
supply. Author stops and names the missing input when a requested primitive cannot bind; it does
not invent a global owner, target, source, `PlayerChoiceContext`, or substitute lifecycle.

The audit recorded twelve excluded or specialized groups. Card-play control, selection and deck
transactions, arbitrary/custom pile movement, Reward claims, Rest Site/Event/map transactions,
creature state machines, direct setters, secondary resources/payment, queries/RNG/state,
presentation, registration/composition, and the existing deferred product groups retain their
dedicated routes or exclusions. No runtime EffectEngine was introduced.

The durable discovery and decision basis remains in
`games/sts2/experimental/M89_EFFECT_PRIMITIVE_AUDIT.md`. Current supported behavior remains in
`games/sts2/tests/content-capability-graph.md`.

## Verification Facts

### Framework-expressible

`yes` for the representative public call shapes compiled by the grouped M8.9 probe against the
pinned STS2/RitsuLib profile. The probe passed with `0` warnings and `0` errors. This is not a
generated-Mod Build or runtime result.

### Open-mod-authorable

`yes` for the nine admitted families at the exact callback and lifecycle boundaries documented by
the shared reference and executable surface projections. Three requirement-to-authoring scenarios
cover active-owner composition, attached/passive-owner composition, and a blocking world
transaction. Unsupported binding combinations fail explicitly.

### Game-observed

`no` for every M8.9 primitive/surface combination. No M8.9 behavior ran in STS2.

## Checks Run

- Grouped C# compile probe: `0` warnings and `0` errors.
- Focused requirement-to-authoring suite: `12/12` passed, including exactly three M8.9 scenarios.
- Full `games/sts2/tools/tests` regression: `248/248` passed.
- Payload layout suite: `3/3` passed.
- Python `compileall` passed for source tools, publish scripts, and both payload trees.
- `git diff --check` passed.

## Payload Delivery

After separate human authorization, `publish.sh --plugin --force` and
`publish.sh --portable --force` succeeded. Each publisher run reported 53 `modmaker` files, 159
`sts2-api` files, and 14 bundled tool files. The plugin tree contained 212 files and the portable
tree 213; portable-only `GENERATED.md` was the sole path difference, and all 212 shared paths had
matching SHA-256 content.

Repeated publication produced stable whole-tree digests:

- plugin: `f95889884e4a21075a20214f89b3a1827f72787778df4df3e511e203e27f6663`;
- portable: `b7a7173b3ef11e37768adf9566ef24218c070f76ba54bbf515d0f147172ac38f`.

This closure step did not run either publisher again. It accepts the already committed payloads
from `9734709` without changing them.

## Unrun Verification

The following remain unrun and must not be inferred from closure:

- no generated M8.9 Mod Build or package;
- no payload installation or installed-skill execution;
- no game launch, Tier 1 load proof, or Tier 2 structured SelfTest;
- no fresh natural-language acceptance Mod;
- no headed UI, mouse/controller, animation, audio, or subjective review;
- no save/load, language-switch, multiplayer, or cross-platform runtime proof;
- no gameplay observation for any primitive/surface combination; and
- no M8.6 whole-skill acceptance.

## Close-Criteria Audit

- Every discovered semantic family has one include or exclude/specialized decision: satisfied.
- Every admitted family has shared lowering and binding guidance: satisfied.
- Executable surfaces expose truthful callback projections and missing-context rejection:
  satisfied.
- Grouped compile probes and exactly three authoring scenarios: passed.
- Full static suite, payload layout, `compileall`, and whitespace checks: passed.
- Plugin and portable payloads synchronized and repeatable: satisfied before closure.
- Literal runtime and game-observation boundaries: preserved.
- Durable result record and explicit human-lead acceptance: satisfied on 2026-08-14.

No M8.9 work remains open. M8.6 is now eligible but remains unselected and unstarted until the
human lead supplies its exact request, host, execution contract, and authorization.
