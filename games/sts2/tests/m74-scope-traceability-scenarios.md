# M7.4 scope and design-to-SPEC traceability scenarios

These repository-owned cases define the behavioral review surface for M7.4. They evaluate
durable intent, explicit current/future scope, unsupported-route handling, bidirectional
DESIGN-to-SPEC traceability, and fast-path compactness. They do not prove runtime behavior,
Tier 1, Tier 2, design quality, balance, enjoyment, or human playtest results.

Review behavior semantically rather than matching preferred prose. A response passes when
it preserves the same intent, dispositions, supported current operations, future vision,
and trace invariants; exact headings and sentences may differ.

## Common rubric

- **Artifact ownership:** DESIGN owns creative intent/scope; SPEC owns exact current
  operations/routes; PLAN owns stage status; MEMORY owns technical resolution/build facts.
- **Explicit scope:** every requirement is current `MUST`, accepted `PLACEHOLDER`, future
  `DEFER`, or rejected `OUT-OF-SCOPE` after blockers are resolved.
- **Boundary honesty:** unsupported intent pauses once, stays literal, and enters no current
  operation without explicit acceptance of a genuinely supported alternative.
- **Bidirectional trace:** every current design item maps to one or more SPEC operations and
  every SPEC operation maps back only to current design items plus one shipped route.
- **No future leakage:** deferred and out-of-scope items produce no SPEC stub, source,
  resource, fallback, or promise of support.
- **Decision preservation:** revision/backfill keeps stable IDs and unrelated accepted or
  rejected decisions; it never invents historical rationale or future vision.
- **Question economy:** use one combined scope/SPEC confirmation and keep a complete exact
  Card's DESIGN capsule short.
- **Scope honesty:** M7.4 changes authoring artifacts and validation, not the runtime support
  graph or M7.5/M7.6 behavior.

## Case 1 - supported resource and unsupported Energy replacement fail closed

**Input**

> Build a Duelist Character with a Momentum resource and visible counter. Momentum should
> completely replace normal Energy.

After the boundary explanation, the user selects:

> Keep normal 3 Energy and add Momentum as a separate combat resource for this version.
> Preserve replacing Energy as a future idea.

**Expected behavior**

1. Identify the supported Character Foundation plus combat-lifetime secondary resource/UI,
   and the unsupported alternative-Energy replacement. Before the user's second message,
   keep one blocking gap and do not freeze DESIGN, write SPEC, or scaffold.
2. Explain the visible trade-off once: the supported current version keeps normal 3 Energy
   and adds Momentum; it cannot present Momentum as replacement Energy. Do not silently
   flatten the original wording or invent a patch.
3. After acceptance, write current `MUST` rows for Foundation and secondary Momentum, an
   accepted art `PLACEHOLDER` when applicable, and one future `DEFER` row preserving the
   exact replacement-Energy vision and current boundary.
4. Give only current rows `OP-###` mappings. SPEC traces Foundation and Momentum through
   their shipped semantic routes and contains no replacement-Energy field, stub, or code.
5. Run `design_trace.py` successfully and show one combined build-now/placeholder/later
   confirmation.

**Failure signals**

- marks replacement Energy `MUST` because the fantasy is compelling;
- writes a partial SPEC before the user accepts the supported version;
- deletes the original replacement idea instead of preserving the selected future vision;
- maps the deferred item to an operation; or
- claims `DEFER` means a future implementation route is known.

## Case 2 - larger frost-oracle vision is separated from the first playable slice

**Input**

> Eventually I want a Frost Oracle Character with a full card pool, custom Ancient, Spine
> animation, and voiced lines. For now build the playable Foundation: normal 3 Energy, an
> exact native-shaped starter deck, a Starter relic, and static placeholder presentation.

**Expected behavior**

1. Preserve the full Frost Oracle vision in DESIGN without asking whether the explicitly
   named future items belong in the first build.
2. Mark the exact Character Foundation and Starter relic behavior as current `MUST`, and
   the accepted static/template presentation as `PLACEHOLDER` with an explicit fallback
   operation.
3. Mark the full pool as supported-but-later `DEFER`; record custom Ancient, Spine, and
   audio/voice as deferred future intent with their current boundaries. Do not claim that
   those unsupported routes will exist later.
4. SPEC contains only the exact Foundation/relic/fallback operations, each linked to current
   design IDs and a shipped route. It contains no empty future sections or generated hooks.
5. A later edit to future prose alone updates DESIGN but does not reopen Author/Build. A
   change to the current starter deck updates DESIGN first, preserves stable IDs where the
   requirement remains the same, updates SPEC, and revalidates.

**Failure signals**

- silently attempts the complete future vision;
- discards future vision because it is not currently supported;
- treats placeholder as omission with no current operation;
- copies design rationale into SPEC; or
- reopens runtime work for a future-vision-only wording edit.

## Case 3 - exact Card keeps a compact DESIGN capsule

**Input**

> Make a 1-Energy Common Attack called Ember Step. It deals 9 damage, upgrades to 12, and
> uses placeholder art.

**Expected behavior**

1. Keep the fast route and ask no question. Do not load mechanic, content-set, or balance
   planning merely because the Card has numbers.
2. Write a short DESIGN with one-sentence intent, the exact accepted/defaulted Card
   decision, one current `MUST` row for Card registration/effect, one current
   `PLACEHOLDER` row for art, empty future vision, and empty blocking gaps.
3. Write matching SPEC operations through the Card recipe and checked art fallback, run the
   trace validator, and show one combined confirmation.
4. Do not add pillars, archetypes, rejected alternatives, tuning essays, future systems, or
   a second approval round.

**Failure signals**

- turns the exact Card into a full GDD;
- asks the user to approve ordinary defaults separately;
- omits DESIGN because the request is simple;
- marks placeholder art as deferred rather than current visible fallback; or
- creates an orphan design item or SPEC operation.

## Review record

Record the reviewer, date, cases inspected, and any deviation. A static contract pass and
trace-validator tests mean only that the shipped workflow contains and mechanically checks
these contracts. A forward-model run, if later authorized, must record its actual artifacts
and may not be inferred from this file.

- **2026-08-04 source-contract review:** Codex inspected all three cases against
  `route.md`, `interview.md`, `design.md`, `spec.md`, `author.md`, and
  `design_trace.py`. The source instructions fail closed on an unresolved unsupported
  request, separate current/future scope, validate the trace in both directions, preserve
  pre-M7.4 resume behavior, and keep the exact-Card artifact compact. No independent
  forward-model output was produced or reviewed.
