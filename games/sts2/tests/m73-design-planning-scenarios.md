# M7.3 mechanic, content-set, and balance planning scenarios

These repository-owned cases define the behavioral review surface for M7.3. They evaluate
planning depth, question economy, evidence honesty, and semantic lowering. They do not
prove runtime behavior, Tier 1, Tier 2, balance, enjoyment, or human playtest results.

Review behavior semantically rather than matching preferred prose. A response passes when
it preserves the same decisions, calculations, relationships, assumptions, and boundaries;
exact headings and sentences may differ.

## Common rubric

- **Lazy planning:** load only the design references required by the request; keep a clear
  exact Card on the fast path.
- **Question economy:** resolve only the highest-impact open design decision and stop once
  safe defaults can complete the planning capsule.
- **Decision preservation:** preserve the user's fantasy, accepted mechanic structure,
  exact content rules, values, and explicit departures.
- **Meaningful alternatives:** when the mechanic is unclear, compare structures that
  change player action or timing, not number-only variants.
- **STS2-native pressure:** use Energy, Cards, enemy intent, targets, setup turns, deck
  dilution, and reset boundaries rather than invented PvP counterplay.
- **Interaction coverage:** use real content nodes and directed source-to-dependent edges;
  identify missing sources, payoffs, defense, scaling, bridges, or release valves.
- **Evidence honesty:** distinguish pinned facts, observed conventions, creative decisions,
  derived calculations, and open hypotheses. Never fabricate a benchmark or playtest.
- **Mod-forward power:** avoid a weak no-pick floor and prefer one legible advantage, while
  rejecting values or loops that erase choices, setup, costs, or ordinary opposition.
- **Scope honesty:** planning does not widen runtime support, create M7.4 `DESIGN.md`, or
  claim design-to-SPEC traceability.

## Case 1 - ambiguous heat mechanic gets one structural decision

**Input**

> I want a Heat mechanic. Attacks raise Heat, high Heat should feel powerful, and the
> player can overheat. Help me make the play pattern interesting.

**Expected behavior**

1. Select co-design and load mechanic planning. Do not load content-set planning or balance
   planning until the user requests a set or materially numeric decision.
2. Preserve the fantasy of deliberately building pressure for a dangerous payoff. Offer
   two or three materially different structures, such as voluntarily venting for safety,
   crossing a known threshold for a forced release, or selecting a payoff tier. Explain
   what the player does, the information they have, and the trade-off; recommend one.
3. Ask only which structural decision should define Heat. Do not ask for every threshold,
   Card, visual, or formula in the same turn.
4. After selection, carry the trigger, visible Heat state, competing spend/hold lines,
   payoff/reset, opportunity cost, zero/full/repeated-trigger edges, tuning knobs, and a
   dominance comparison across unfavorable, ordinary, and favorable states.
5. Treat exact thresholds and payoffs as open hypotheses until selected and grounded.

**Failure signals**

- asks a long mechanic questionnaire before resolving the central spend/hold decision;
- offers only low/medium/high damage variants;
- describes enemy counterplay as though STS2 were PvP;
- calls the first numbers balanced; or
- silently invents an unsupported runtime operation to preserve the theme.

## Case 2 - glassblower Character receives a connected content set

**Input**

> Build a glassblower Character. Cards build Heat, then Shape it into attacks or defenses.
> I want a complete card set with multiple viable approaches.

**Expected behavior**

1. Load Character Foundation and content-set planning. Load mechanic planning only if the
   build-versus-shape decision remains materially ambiguous, and balance planning only when
   exact economy values become a current decision.
2. Begin with the exact native-shaped Foundation proposal required by M7.2, then expand to
   real proposed content nodes. Do not treat the merchant-minimum inventory as a complete
   set or ask the user to fill a blank card list.
3. Cover access, attack and defense payoffs, consistency, scaling, at least one useful
   bridge/off-ramp, and a release valve. A role may be shared; no fixed card count or rarity
   quota is invented without evidence.
4. Record directed relationships such as Heat source -> Shaping payoff and consistency ->
   setup access. Flag a payoff with no source, a source with no ordinary-use floor, a
   circular prerequisite, or an archetype with easiest setup, safest defense, and highest
   ceiling at once.
5. Lower only accepted supported Cards/relics and exact interactions to SPEC. Keep role
   rationale, alternatives, coverage review, balance hypotheses, and future ideas out of
   SPEC until M7.4 owns the durable design artifact.

**Failure signals**

- emits a large disconnected card list with no interaction graph;
- equates shared Heat vocabulary with distinct archetypes;
- assumes each role must be exactly one Card;
- labels static role coverage complete, fun, or balanced; or
- creates `DESIGN.md` or claims M7.4 traceability.

## Case 3 - Ink economy uses a generous working hypothesis

**Input**

> Ink gains 1 whenever I play a Skill and spends 3 to deal 12 damage. Is that balanced?

**Expected behavior**

1. Load balance planning. Do not load Character Foundation or content-set planning; the
   core source-and-sink rule is already exact.
2. State the output unit, source and sink, trigger/payment timing, combat reset/cap
   assumptions, opportunity cost, and evidence basis. Ask only if a missing rule changes
   the current implementation and has no safe explicit working assumption.
3. Show `time to first payoff = ceil(3 / expected Skill triggers per turn)`: three turns at
   one trigger per turn, two turns at two triggers, and one turn at three triggers. State
   conversion efficiency as 4 damage per Ink while noting that Ink is not an Energy unit.
4. Apply the human lead's Mod-forward preference: 12 damage may remain as a clearly
   rewarding, generous working hypothesis if it has a plausible use case, but no fixed
   power percentage or unverified native benchmark is invented.
5. Check low/working/high trigger rates, immediate-spend versus hoard lines, setup and deck
   opportunity cost, and self-funding or unbounded interactions. Reduce access, tighten a
   condition/cap, or preserve a real cost before flattening the distinctive payoff when a
   dominance risk appears.
6. Do not answer "balanced." Record trigger-rate assumptions, closest pinned comparison,
   common-state pick rate, encounter performance, and human playtest observations as open
   evidence needs. Lower 12 damage only after it is accepted as the current working value.

**Failure signals**

- declares 12 damage balanced from arithmetic alone;
- invents a universal percentage above vanilla;
- compares Ink directly to Energy without naming the unit mismatch;
- ignores reset, cap, source cadence, opportunity cost, or self-funding loops; or
- fabricates playtest observations.

## Review record

Record the reviewer, date, cases inspected, and any deviation. A static contract pass means
only that the shipped instructions contain these behaviors. A forward-model run, if later
authorized, must record its actual outputs and may not be inferred from this file.

- **2026-08-04 source-contract review:** Codex inspected all three cases against
  `route.md`, `interview.md`, `spec.md`, and the three M7.3 design references. The source
  instructions route each case lazily, preserve the exact-Card fast path, carry a compact
  planning capsule, keep material open hypotheses out of SPEC, and apply the Mod-forward
  power bias without claiming balance. No independent forward-model output was produced or
  reviewed.
