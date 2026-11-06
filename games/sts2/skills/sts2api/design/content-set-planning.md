# Character and content-set planning

Load this reference for a Character card pool, archetype, multi-element set, or another
request where several pieces must form a coherent playable ecosystem. For a Character,
also load `design/character-foundation.md`. Load `design/mechanic-planning.md` when the set's
core decision is unresolved, and `design/balance-planning.md` only when numeric or economy
questions are material.

## Boundary and evidence

Content-set structure is a creative recommendation unless a checked reference supplies an
exact native fact. A vanilla analogy must resolve against the pinned `0.107.1` catalog
before being named as fact. Do not copy another Mod's content, source, or assets.

The Character recipe's `2 non-Basic Attacks / 2 Skills / 1 Power` merchant floor is a
technical minimum for the selected host, not evidence of a complete, varied, or balanced
card pool.

Pinned fact (`reference/vanilla-overrides/catalogs/sts2-0.107.1.json`, Card `card_pools`):
every native Character pool holds 20 Common, 36 Uncommon, and 26 Rare Cards, plus 3-4 Basic
and 2 Ancient Cards, and no native Common is a Power. That is the shape of a complete
shipped Character, not a target size for a Mod set; there is no native archetype count.

## Set architecture

Start with the shared player fantasy and one core decision. Then describe the smallest
role coverage that lets the set teach, function, vary, and recover:

- **Foundation:** Basic Cards and Starter relic deliver a first, low-complexity access and
  payoff so the opening deck already shows the mechanic.
- **Access/enabler:** creates the state, resource, target, or condition the mechanic needs.
- **Payoff:** converts setup into immediate defense, damage, control, or scaling.
- **Consistency:** draw, selection, generation, or flexible timing that helps assemble a
  line without making it automatic.
- **Defense/safety:** lets the player survive setup turns or choose a lower-risk line.
- **Scaling:** converts repeated investment into later strength without being the only
  viable plan.
- **Bridge/off-ramp:** remains useful with partial commitment and connects two archetypes or
  ordinary deck needs.
- **Release valve:** spends, clears, caps, or converts accumulated state so hoarding is not
  always correct.

These are design roles, not mandatory one-Card slots. One Card may own several compatible
roles; a role may need several Cards at different access points. Avoid keyword islands in
which only one enabler and one payoff can find each other.

**Purpose test.** Every item needs a reason to be picked in some state:

- **Staple:** a real floor, worth taking in an ordinary deck that ignores the archetype.
  Bridges and most defense and consistency items are staples.
- **Build-around:** a real ceiling inside its archetype. It may be weak alone, so its
  archetype needs access the player can reach before it is offered.

An item with neither a real floor nor a real ceiling has no role; cut it or give it one.
An item with the set's best floor and its highest ceiling is an always-pick and a dominance
concern.

**Access points.** As an observed convention, not a rule: put enablers, staples, and bridges
at Common so an archetype can start from ordinary rewards, and put build-around payoffs and
scaling engines at Uncommon or Rare. A payoff whose only enabler is Rare is a keyword island
in practice.

For each proposed content item, record:

```text
name/id: <stable creative identity>
surface and availability: <Card/Relic/etc.; Basic/Common/etc. when selected>
primary role: <foundation/access/payoff/consistency/defense/scaling/bridge/release>
purpose: staple | build-around | both (dominance check)
player-facing rule: <exact accepted behavior>
mechanic input/output: <what it consumes, creates, or checks>
floor/ceiling: <use when unsupported by the archetype; best intended state>
relationships: <directed source -> dependent edges>
open hypothesis: none | <claim and evidence needed>
```

## Archetypes and interactions

Define an archetype by its distinct repeated decision, not by sharing a keyword or color.
For each selected archetype state:

- entry condition and common access;
- payoff and intended tempo;
- defensive plan and failure state;
- scaling path and release valve;
- bridge Cards that keep partial commitment useful; and
- what makes its preferred decisions differ from the other archetypes.

Build a directed interaction graph before writing a long card list. Every dependent payoff
needs at least one plausible source, and every major source needs a payoff or ordinary-use
floor. Mark isolated nodes, circular prerequisites, and interactions that require an
unsupported runtime route. The later semantic SPEC uses real content nodes and directed
`interactions`; it never invents a generic `combo` element.

## Coverage and dominance review

Review the set against these questions:

- Can the starter teach the core action without exposing the full set at once?
- Can rewards offer useful floor value before the player commits to an archetype?
- Does every item pass the purpose test, and can each archetype start from Common access?
- Do offense against one and several enemies, defense, consistency, and scaling each have a
  plausible route?
- Does one archetype get easier access, safer setup, and a higher ceiling at the same time?
- Is one source/payoff package so self-contained that bridge and alternative Cards become
  false choices?
- Can hoarding, generation, draw, cost reduction, or recursive creation become
  self-funding or unbounded?

If data is missing, record the concern and observation needed. Do not label role coverage
or a static card list as balanced, complete, or fun.

## Handoff

Carry the selected set architecture, role rows, interaction graph, coverage gaps, dominance
concerns, and open hypotheses into the compact design capsule. Lower only accepted,
supported, exact content rules and relationships into `SPEC.md`. `DESIGN.md` owns durable
intent and current/not-now scope; do not fabricate those artifacts here.
