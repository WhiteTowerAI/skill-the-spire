# Mechanic planning

Load this reference only when a request introduces or revises a mechanic, resource,
stateful loop, risk/reward structure, or interacting system whose player-facing decision is
not already exact. Do not load it for a complete narrow Card whose remaining fields have
safe defaults.

## Boundary and evidence

This page is a design method, not an STS2 fact inventory and not a runtime route. Resolve
exact vanilla analogies through the pinned `0.107.1` catalog and `grounding.md`. Resolve
implementation through the capability graph and shipped recipes only after the design is
accepted. Label an unsupported operation as a gap; never redesign it into a supported
operation without explicit user acceptance.

Keep four evidence classes distinct:

- **Pinned fact:** exact current-game data or supported behavior from a checked reference.
- **Observed convention:** a recurring native pattern used as an analogy, not a rule.
- **Creative decision:** the selected player experience, rule, trade-off, or value.
- **Open hypothesis:** a prediction that needs calculation, implementation evidence, or
  human playtest observation. Never present it as proven or balanced.

## Compact mechanic pass

Resolve only the fields that materially shape play:

1. **Player fantasy:** one sentence in the form "the player repeatedly does X to feel Y."
   Describe an action and payoff, not lore alone.
2. **Core decision:** name at least two viable actions or timings and the game state that
   makes each preferable. If one line is always correct, the mechanic is not yet a
   meaningful decision.
3. **Loop:** state the trigger or input, visible state change, player choice, immediate
   feedback, payoff, and reset/carry boundary.
4. **Risk and reward:** identify what is committed or delayed, what the player knows before
   choosing, how much agency they retain, and what payoff justifies the risk.
5. **Counterplay or pressure:** in a singleplayer deckbuilder this usually means enemy
   intent, timing, Energy/Card opportunity cost, setup exposure, deck dilution, exhaust,
   target availability, or a reset boundary. Do not invent PvP counterplay.
6. **Rules and edge cases:** define zero, cap/full, insufficient payment, repeated trigger,
   invalid target, ordering, reset, and any save boundary selected by the mechanic.
7. **Tuning knobs:** name the smallest independent values that can change cadence, access,
   payoff, reliability, or ceiling without rewriting the mechanic.

For a clear mechanic, draft this compact pass and move to confirmation. For an ambiguous
mechanic, use co-design on the highest-impact decision first. Offer two or three structures
that change what the player does, such as known payment versus conditional risk versus a
player-selected tier. Number-only variants are not different mechanics. Recommend one and
explain the trade-off, then preserve the user's selection.

## Dominant-strategy review

List the plausible repeated lines of play, including "ignore this mechanic." Compare them
across at least an unfavorable, ordinary, and favorable state:

- immediate value and delayed ceiling;
- Energy, Card, HP, resource, target, and setup opportunity cost;
- reliability and failure state;
- interaction with defense, scaling, draw, and reset timing; and
- whether a loop becomes self-funding, deterministic, or unbounded.

A line is a dominance concern when it is at least as useful in common states and strictly
better in one without a meaningful extra cost or condition. Repair the decision by changing
access, timing, condition, opportunity cost, cap, or competing payoff. Do not add arbitrary
punishment that erases the intended fantasy.

## Handoff

Carry a compact mechanic capsule into `interview.md`:

```text
player fantasy: <repeated action -> intended feeling>
core decision: <line A versus line B; state that favors each>
loop: <input -> visible state -> choice -> feedback/payoff -> reset>
risk/reward: <commitment, information, agency, payoff>
counterplay/pressure: <player-facing constraint>
rules/edge cases: <exact selected rules and boundaries>
tuning knobs: <independent values and what each changes>
dominant-strategy check: <plausible lines, concern, mitigation or none>
open hypotheses: none | <claim and evidence needed>
```

This capsule guides confirmation and semantic lowering into `SPEC.md`. Lower only accepted,
supported, exact current rules and values. This reference does not create the durable `DESIGN.md`
schema; the `design.md` stage owns the durable intent and scope.
