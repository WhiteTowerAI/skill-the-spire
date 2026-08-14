# Character Foundation design scenarios

These cases protect native grounding, exact starter proposals, separation of facts from creative
decisions, and deliberate implementable departures. They do not establish runtime behavior,
Tier 1, Tier 2, balance, or enjoyment.

Review behavior semantically. Exact headings and sentences may differ when the same facts,
recommendation logic, user choices, and boundaries are preserved.

## Common rubric

- **Lazy grounding:** load the Character Foundation grammar for Character work and no unrelated
  reference.
- **Evidence labels:** distinguish pinned `0.107.1` facts, observed native conventions, and
  creative decisions.
- **Actionable default:** recommend one exact deck with names, counts, base effects, upgrades,
  total, and a Starter relic lesson before asking for deck details.
- **Question economy:** ask about the core player decision only when it changes the teaching
  Cards; never ask the user to fill ten blank slots.
- **Native analogy:** explain the relevant native teaching pattern without claiming that `4/4/2`,
  ten Cards, or a creative value is mandatory.
- **Departure handling:** preserve an implementable departure after stating onboarding,
  compatibility, and early-balance consequences.
- **Scope honesty:** Foundation grammar does not replace separate content-set and balance planning
  or establish runtime behavior and playtest evidence.

## Case 1 - Character with unspecified starter deck

**Input**

> Make a playable storm caller. They build Charge, then spend it for lightning attacks. I have not
> designed the starter deck.

**Expected behavior**

1. Load the Character Foundation grammar and treat the Charge setup/payoff loop as settled.
2. Recommend a complete native-shaped 10-Card deck: four Character-specific Strike, four
   Character-specific Defend, one named Charge builder, and one named Charge spender, each with
   grounded base/upgrade effects. Include a named Starter relic that reinforces the lesson.
3. Label `4 Strike / 4 Defend / 2 identity` as an observed analogy, not a pinned rule. Label the
   Charge names and effects as creative decisions.
4. Ask no starter-count or Card-naming question when no other material decision is missing.

**Failure signals**

- asks the user to list ten starter Cards or choose a structure from scratch;
- presents placeholders instead of an exact proposal;
- attributes Charge or creative values to vanilla; or
- claims the deck is balanced or playtested.

## Case 2 - Character and content-set request starts from Foundation

**Input**

> Build a glassblower Character whose cards heat glass, then shape it into attacks and defenses. I
> also want a full card set around that idea.

**Expected behavior**

1. Load Character Foundation grounding without loading every API reference.
2. Propose an exact setup Basic, an exact payoff Basic, baseline Strike/Defend counts, and a
   reinforcing Starter relic.
3. Separate native starter facts, the observed setup/payoff analogy, and creative Heat mechanics.
4. Keep full pool roles, archetype coverage, economy, and balance in separate content-set and
   balance planning.

**Failure signals**

- skips the starter recommendation and emits a large card list;
- treats one native Character as a mandatory template;
- fabricates unsupported operations to complete the theme; or
- claims content-set coverage or balance evidence that was not produced.

## Case 3 - Deliberate implementable departure is preserved

**Input**

> Make a scholar Character with a 12-Card starter deck of twelve differently named Basic cards.
> None should display as Strike or Defend.

**Expected behavior**

1. Recognize the exact multiset as an implementable creative departure.
2. Explain the increased learning load, changed draw and upgrade/removal pressure, and possible
   loss of Strike/Defend interactions.
3. Ask at most whether the renamed baseline Cards retain `CardTag.Strike` and
   `CardTag.Defend`.
4. Preserve all twelve distinct names and the selected tag behavior in SPEC.

**Failure signals**

- rejects the request only because no native Character matches it;
- silently restores visible Strike/Defend names;
- omits onboarding, compatibility, or balance consequences; or
- calls the departure safe, balanced, or playtested without evidence.
