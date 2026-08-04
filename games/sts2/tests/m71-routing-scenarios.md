# M7.1 adaptive routing scenarios

These repository-owned cases define the behavioral review surface for M7.1. They evaluate
route choice, question economy, meaningful alternatives, and preservation of settled
decisions. They do not prove runtime behavior, Tier 1, Tier 2, balance, or enjoyment.

Review behavior semantically rather than matching preferred prose. A response passes when
it preserves the same decisions and interaction boundary; exact headings and sentences may
differ.

## Common rubric

- **Route fit:** infer fast, co-design, revision, or direct resume from the actual state;
  never ask the user to choose the workflow mode.
- **Question economy:** ask only when different answers change player behavior, supported
  operations, scope, state, or proof.
- **Alternatives:** when co-design is needed, offer two or three materially different
  player-facing outcomes with concrete trade-offs and a reasoned recommendation.
- **Decision preservation:** carry prompt facts and artifact decisions forward; never
  replace, omit, or re-ask them without a stated conflict.
- **Boundary honesty:** stop before SPEC/scaffold on unresolved contradictions or unsupported
  behavior; continue only after explicit acceptance of a different result.
- **Proportionality:** a clear Card stays short; a resumed build does not become a design
  interview; a revision touches only its affected delta.

## Case 1 - clear Card uses fast

**Input**

> Create a Common Attack called Ember Jab. It costs 1 Energy, deals 7 damage to one enemy,
> upgrades to 10 damage, and uses placeholder art.

**Expected behavior**

1. Select fast and state it briefly.
2. Ask zero clarification questions.
3. Preserve the exact name, rarity, type, cost, target, base/upgrade damage, and art choice.
4. Apply only non-material defaults such as the shared/colorless pool and proceed to the
   plain-language SPEC confirmation.

**Failure signals**

- asks the user to choose fast versus co-design;
- asks about any value already supplied, framework/API details, author, or custom art; or
- invents a larger mechanic, Character, design pillars, or future roadmap.

## Case 2 - vague risk mechanic uses co-design

**Input**

> Make a card about gambling your health for a big payoff.

**Expected behavior**

1. Select co-design because the risk decision has multiple player-facing interpretations.
2. Address the highest-impact risk model before cost, rarity, exact numbers, naming, or art.
3. Offer two or three genuinely different structures, such as a known HP payment for a
   reliable payoff, a conditional loss for a stronger swing, or a player-selected risk
   tier. Explain predictability, agency, and tuning trade-offs.
4. Recommend one structure with a reason while leaving the creative choice to the user.
5. Preserve the chosen structure in later questions and stop offering alternatives once
   safe defaults can finish the Card.

**Failure signals**

- sends an exhaustive Card questionnaire;
- presents cosmetic number variants as different mechanics;
- chooses a mechanic without giving the user the material trade-off; or
- reopens the selected risk model later without a conflict.

## Case 3 - contradictory cost pauses once

**Input**

> Make a card whose play cost must be both 0 Energy and 2 Energy. Do not ask me any
> questions.

**Expected behavior**

1. Identify the conflicting play-cost requirements without selecting one silently.
2. Explain that the two values produce different playability and Card text.
3. Ask one constrained resolution question, optionally including a separately described
   supported mechanic if it preserves the intent.
4. Stop before SPEC and scaffold until the user resolves the conflict.

**Failure signals**

- treats "do not ask" as permission to choose a value;
- writes both values into an incoherent SPEC; or
- silently reframes one value as an unrelated effect payment.

## Case 4 - unsupported request preserves intent

**Input**

> Build a multiplayer card that stays in a new retained-card zone and plays voiced audio.

**Expected behavior**

1. State the current multiplayer, retained-card-zone, and audio boundaries before SPEC.
2. Preserve the intended persistent-card identity rather than silently emitting a normal
   discard Card.
3. Offer at most two supported alternatives only if they retain useful intent, with the
   visible loss of multiplayer, retention, or audio stated plainly.
4. Continue only after the user explicitly accepts a supported result.

**Failure signals**

- generates Harmony, reflection, IL, a fake retained zone, or silent singleplayer behavior;
- labels missing authoring or verification as a passed runtime route; or
- scaffolds before an alternative is accepted.

## Case 5 - unfinished project resumes directly

**Fixture**

- `SPEC.md` exists with an accepted Ember Jab contract.
- `PLAN.md` marks interview and spec complete and scaffold as the first unfinished stage.
- The user requests no design change.

**Input**

> Continue this Mod.

**Expected behavior**

1. Read the project artifacts and continue at scaffold.
2. Do not call the request a revision and do not rerun route selection as a user decision.
3. Ask zero design questions and preserve every accepted SPEC value.

**Failure signals**

- asks for the Card idea, name, numbers, art, or approval again;
- restarts from a blank interview; or
- overwrites completed PLAN state.

## Case 6 - existing Card receives a bounded revision

**Fixture**

- `SPEC.md` defines Ember Jab as a 1-cost Common Attack dealing `7 -> 10` damage to one
  enemy with placeholder art.
- `PLAN.md` records a completed build and verification.

**Input**

> Change Ember Jab to 9 damage and 12 when upgraded. Keep everything else.

**Expected behavior**

1. Select revision and read the existing artifacts before proposing edits.
2. Show a compact delta: keep identity/type/cost/target/art and unrelated behavior; change
   base/upgrade damage; check generated text/value consistency; re-verify the affected Card
   behavior.
3. Ask zero questions because the delta is complete.
4. After confirmation, update only the affected SPEC fields and reopen only author, build,
   and the proportional behavior proof. Do not reopen art or unrelated content.

**Failure signals**

- restarts the general interview;
- changes any preserved field;
- treats the old verification as proof of the new values; or
- claims a user-reported observation or build result that did not occur.

## Review record

Record the reviewer, date, cases inspected, and any deviation. A static contract pass means
only that the shipped instructions contain these behaviors. A forward model run, if later
authorized, must record its actual outputs and may not be inferred from this file.

- **2026-08-04 source-contract review:** Codex inspected all six cases against `route.md`,
  `interview.md`, `SKILL.md`, and `spec.md`. The fast case asks zero questions; the vague
  case receives distinct trade-offs; contradiction and unsupported cases stop before SPEC;
  resume skips Interview; revision preserves unrelated fields and reopens proportional
  stages. No independent forward-model output was produced or reviewed.
