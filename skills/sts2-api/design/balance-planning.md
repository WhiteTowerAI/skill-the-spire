# Numeric and economy planning

Load this reference when a request asks whether values are balanced, introduces a resource
economy, needs a formula or range, or leaves numbers that materially change the mechanic
unresolved. Do not load it merely because every Card happens to contain a number.

## Evidence and product bias

Separate the basis for every claim:

1. user-provided measurements or human playtest observations;
2. exact pinned `0.107.1` values from a checked vanilla analog;
3. a transparent calculation with named assumptions; or
4. an open creative hypothesis that still needs evidence.

Never invent a missing formula, native benchmark, probability, tolerance band, or playtest
result. Compilation and static reasoning do not prove balance or enjoyment.

open-mod uses a deliberate **Mod-forward power bias** selected by the human lead: when the
user gives no contrary direction, prefer a working value that is clearly rewarding and
modestly stronger than the closest relevant native comparison in its intended state. This
is a creative product preference, not an STS2 fact and not a fixed percentage.

Apply that bias asymmetrically:

- **Weak floor:** a new option that has no plausible pick/use case, or is worse than the
  closest alternative after accounting for setup and opportunity cost, fails the design.
- **Working target:** grant one legible advantage or stronger payoff that rewards the Mod's
  intended mechanic; do not stack several free advantages merely to look powerful.
- **Playability ceiling:** reduce or constrain a value when it makes one line correct in
  most common states, erases Energy/Card/HP/resource trade-offs, bypasses setup, trivializes
  ordinary opposition, or creates a deterministic/self-funding/unbounded loop.

When evidence is absent, call the result a generous working hypothesis, not balanced. A
user-specified power fantasy may intentionally move the target, but the same playability
ceiling and explicit-consequence rule still apply.

## Formula contract

Before judging or recommending a value, write:

```text
output: <what is being valued; unit and integer/real domain>
formula: <one deterministic relationship>
variables: <name, meaning, source, min/max if known>
timing: <when inputs are observed and output applies>
assumptions: <draw rate, trigger rate, target availability, encounter length, etc.>
constraints: <floor, cap, payment, reset, invariants>
comparison: <pinned analog or none>
status: checked fact | derived result | generous working hypothesis
```

If a required variable or relation is missing, stop the calculation at that gap and name
the input needed. Do not backfill it with a familiar number from another game or Mod.

## Economy audit

For a resource or repeating value, inventory:

- all sources, amounts, conditions, and expected cadence;
- all sinks, costs, payoff, and whether payment is optional or mandatory;
- start, floor, cap, reset, persistence, overflow, and unused-state behavior;
- opportunity cost in Energy, Cards, HP, targets, turns, or deck slots; and
- feedback/readability that lets the player plan around the economy.

Use explicit relationships where applicable:

```text
net per window = total expected sources - total expected sinks
time to first payoff = ceil(payoff cost / expected gain per turn), when gain > 0
conversion efficiency = payoff output / total paid resource, with units stated
```

Treat `expected` inputs as assumptions until measured. Check starvation, effortless
hoarding, dead overflow, repeated full-state triggers, self-funding conversion, and whether
the optimal line is always "never spend" or always "spend immediately."

## Sensitivity and tuning

Evaluate low, working, and high scenarios. Change one independent knob at a time and state
what player behavior it affects:

- access or trigger rate changes frequency;
- cost/threshold changes time to payoff and commitment;
- payoff changes reward without changing cadence;
- cap/decay/reset changes hoarding and ceiling;
- reliability/target restriction changes failure risk; and
- upgrade delta changes progression rather than the base loop.

Prefer a small set of knobs with non-overlapping jobs. When the design is too weak, first
restore a real pick/use case by improving access, floor, or intended payoff. When it is too
strong, preserve the fantasy where possible by tightening access, condition, timing,
opportunity cost, or cap before flattening the distinctive payoff.

Do not claim BALANCED from a formula alone. Report the working value, comparison,
sensitivity, dominance risk, and evidence needed from a human playtest. M7.6 owns the
observation-driven tuning loop and must not fabricate those observations.

## Handoff

Carry the formula contract, economy audit, chosen working values, independent tuning knobs,
low/working/high sensitivity, dominance risks, and open evidence needs into the M7.3 design
capsule. Lower only the exact accepted current values and supported operations into
`SPEC.md`; M7.4 owns durable design rationale and traceability.
