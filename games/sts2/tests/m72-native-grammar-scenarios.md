# M7.2 STS2-native design grammar scenarios

These repository-owned cases define the behavioral review surface for M7.2. They evaluate
native grounding, exact starter proposals, fact/convention/decision separation, and
deliberate departures. They do not prove runtime behavior, Tier 1, Tier 2, balance, or
enjoyment.

Review behavior semantically rather than matching preferred prose. A response passes when
it preserves the same facts, recommendation logic, user choices, and boundaries; exact
headings and sentences may differ.

## Common rubric

- **Lazy grounding:** load the Character Foundation grammar for Character work and no
  unrelated design reference.
- **Evidence labels:** keep pinned `0.107.1` facts, observed native conventions, and the
  custom Character's creative decisions distinguishable.
- **Actionable default:** recommend one exact deck with Card names, counts, base effects,
  upgrades, total, and Starter relic lesson before asking for deck details.
- **Question economy:** ask about the core player decision only when it materially changes
  the teaching Cards; never ask the user to fill ten blank Card slots.
- **Native analogy:** explain why the proposed shape resembles a relevant native teaching
  pattern without claiming that `4/4/2`, ten Cards, or any creative value is mandatory.
- **Departure handling:** preserve an implementable departure after stating onboarding,
  compatibility, and early-balance consequences.
- **Scope honesty:** Foundation grammar does not claim full content-set/balance planning,
  runtime support, playtest evidence, or M7.4 `DESIGN.md` traceability.

## Case 1 - Character with unspecified starter deck

**Input**

> Make a playable storm caller. They build Charge, then spend it for lightning attacks. I
> have not designed the starter deck.

**Expected behavior**

1. Load the Character Foundation grammar and treat the Charge setup/payoff loop as settled.
2. Recommend a complete native-shaped 10-Card deck before asking about deck details: four
   Character-specific Strike, four Character-specific Defend, one named low-complexity
   Charge builder, and one named low-complexity Charge spender, each with concrete grounded
   base/upgrade effects. Include one named Starter relic whose effect reinforces that
   lesson.
3. Identify `4 Strike / 4 Defend / 2 identity` as an observed native analogy, not a pinned
   rule. Identify names and Charge effects as creative decisions.
4. Ask no starter-count or Card-naming question. Proceed to the exact plain-language SPEC
   confirmation if no other material decision is missing.

**Failure signals**

- asks the user to list ten starter Cards or choose `4/4/2` versus `5/4/1` from scratch;
- presents placeholder teaching Cards as an exact proposal;
- attributes Charge or the proposed values to vanilla; or
- claims the deck is balanced or playtested.

## Case 2 - Character and content-set request starts from Foundation

**Input**

> Build a glassblower Character whose cards heat glass, then shape it into attacks and
> defenses. I also want a full card set around that idea.

**Expected behavior**

1. Load the Character Foundation grammar because the request includes a playable Character;
   do not load every API or invent a generic game-design framework.
2. Ground the first deliverable decision in a native teaching pair: propose an exact setup
   Basic that heats glass, an exact payoff Basic that shapes it, the baseline Strike/Defend
   counts, and a reinforcing Starter relic.
3. Keep exact native starter facts separate from the observed setup/payoff analogy and the
   creative Heat/shape mechanics.
4. State that full pool roles, archetype coverage, economy, and balance planning remain
   M7.3 work. Do not pretend that the Foundation recommendation already designs the entire
   content set.

**Failure signals**

- skips the starter recommendation and immediately emits a large card list;
- treats one native Character as a template that must be copied exactly;
- fabricates unsupported operations to complete the theme; or
- claims content-set coverage or balance evidence that was not produced.

## Case 3 - Deliberate implementable departure is preserved

**Input**

> Make a scholar Character with a 12-Card starter deck of twelve differently named Basic
> cards. None should display as Strike or Defend.

**Expected behavior**

1. Recognize that the exact multiset is an implementable creative departure, not an
   unsupported runtime request and not a native rule violation.
2. Explain before confirmation that twelve unique Basics increase first-combat learning
   load, change draw consistency and upgrade/removal pressure, and may lose Strike/Defend
   interactions if the corresponding tags are removed.
3. Ask at most the one unresolved compatibility question: should the renamed baseline
   attack/defense Cards retain `CardTag.Strike` and `CardTag.Defend`?
4. Once resolved, preserve all twelve distinct names and the selected tag behavior in the
   intake/SPEC. Do not silently normalize the deck back to `4/4/2`.

**Failure signals**

- rejects the request only because no native Character has twelve unique Basics;
- silently restores visible Strike/Defend names;
- omits the onboarding, compatibility, or balance consequence; or
- calls the departure safe, balanced, or playtested without evidence.

## Review record

Record the reviewer, date, cases inspected, and any deviation. A static contract pass means
only that the shipped instructions contain these behaviors. A forward-model run, if later
authorized, must record its actual outputs and may not be inferred from this file.

- **2026-08-04 source-contract review:** Codex inspected all three cases against
  `route.md`, `interview.md`, `spec.md`, and `design/character-foundation.md`. Character
  work loads the grammar before creative questions; a clear mechanic receives an exact
  starter proposal; Character/content-set work stops short of M7.3 claims; and an
  implementable departure is preserved with all three consequence classes. No independent
  forward-model output was produced or reviewed.
