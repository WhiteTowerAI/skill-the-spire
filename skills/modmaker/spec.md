# Spec - write the implementation work order

Read `DESIGN.md`, `semantic-contract.md`, the selected `surfaces/<surface>.md` pages, and only
the recipe/reference pages needed by the current request. Write `SPEC.md` at the outer project
root. This is the one artifact Author follows.

## Lower the accepted scope

Write only the current supported work. For every element or operation make explicit the facts
`semantic-contract.md` § What every current operation says lists.

Do not copy DESIGN rationale or deferred work into implementation. Do not embed scope,
deliverable, coherence, settlement, repair, surface-data, or evidence JSON. A simple Mod should
have a simple SPEC.

Before preflight, check in your head that every number can actually be reached. Build, Tier 1,
and Tier 2 all pass on a condition that never fires in a real run. Two checks, nothing written:

- every threshold, cost, or condition (for example "if you have 10 Strength") has a source the
  player can actually get in this Mod's pool, Character, or vanilla content; and
- every Mod-owned counter or resource has both a source and a spend or reset.

When one fails, ask the user one question with a recommended fix. Never silently change an
accepted value. Under delegation, fix a value marked `(delegated)` yourself, update DESIGN,
and say so in the confirmation; a value the user stated still gets the question.

## Use the owner pages

Each selected surface page owns its exact domain vocabulary and proof matrix. Every capability in
`SKILL.md`'s supported product boundary stays authorable; use the selected surface pages and
`sts2api` references for its exact current limits. When no maintained route covers an operation,
ground it under `../sts2api/grounding.md` § Mod-local Routes. A prompt is never
authority to invent an ungrounded API.

## Implementation

Write `## Implementation` in the line format `semantic-contract.md` defines: `Support:` for each
maintained route, `Hook:` for each raw model-hook capability, and `Mod-local:` for each grounded
operation without a maintained route.

Do not add a Hook line for ordinary recipe behavior. For a hook, copy `shape` from
`reference/catalogs/model-hooks-sts2-0.107.1.json`, preserve unrelated collection entries for
collection edits, and state the subject guard, condition, value/edit, neutral result,
DynamicVar text binding, and ordering in the human-readable operation above.

Write ordinary player-visible results as one ordered `effects.sequence` in game terms. When that
sequence uses damage, Block/healing/HP changes, Powers, native resources, draw/discard/exhaust,
known-Card creation, known run-content acquisition, or Orb queue/slot effects, add exactly one:

```markdown
- Support: `reference/effect-primitives.md`
```

The element recipe owns its callback and lifecycle; the shared reference owns command lowering.
Do not put API symbols in SPEC. A sequence that needs selection, a Reward/Event/Rest Site
transaction, Card-play lifecycle control, a custom Card Pile, or another specialized operation
also cites that owning route. If the selected callback cannot provide a primitive's required
context/owner/source/target, record the exact unsupported combination instead of changing the
accepted result.

Once every route is listed, run the only pre-Author check:

```powershell
python ../modmaker/scripts/capability_preflight.py --spec SPEC.md
```

## Autotest

Sort the content first (`../sts2api/reference/selftest-harness.md` § Which content
gets which check):

- registration and bilingual text of every Card, Relic, Potion, Power, Character, Monster, and
  Encounter: the self-test kit's roll call checks them on every run; write nothing;
- each **simple Card** (its Implementation cites only its recipe and
  `reference/effect-primitives.md`, its numbers are fixed, and it has no condition): list it
  under `Face checks:`; it gets no scenario; and
- everything else: one concrete scenario per selected behavior, not an evidence placeholder.

Each scenario names:

- a unique `snake_case` name, which `launch.py --only` reruns;
- `CombatPlayer`, `CombatEnemy`, `MapNode`, `RunStart`/Character, or the closest maintained host;
- how it reaches and drives the real source interaction;
- exact expected post-state values and object identities;
- neutral, rejection, degenerate, reset, branch, or unrelated-entry preservation cases required
  by the selected behavior; and
- any headed mouse/controller/art/animation/subjective observation that remains separate.

Tier 2 must assert state after the host processes the action. A hook-fired log, preview value,
model-only mutation, resource path, or successful Build is not a scenario pass.

## Example

```markdown
# SPEC - Ember Step

## Card

- Create a shared Common Attack named Ember Step with logical id `ember_step`.
- Cost 1 Energy. On play, target one enemy, deal 9 Damage, then move normally to Discard.
- Upgrade changes Damage from 9 to 13.
- English: `Deal {Damage} damage.`
- Simplified Chinese: `造成 {Damage} 点伤害。`
- Use the checked placeholder Card portrait.

## Implementation

- Support: `recipes/card.md`

## Autotest

- Face checks: Ember Step (Damage 9, upgraded 13; result pile Discard).
- Scenarios: none; Ember Step is a simple Card.
```

A Card that applied a custom Power, chose a Card, or counted turns would add a scenario instead,
for example `ember_brand_burns_next_turn`: `CombatPlayer`, play the real Card, end the turn,
assert 3 HP lost by every enemy at the start of the next player turn.

## Project state

Create or update a plain `PLAN.md` checklist:

```markdown
# PLAN

- [x] design
- [x] spec
- [x] capability preflight
- [ ] scaffold
- [ ] author and SelfTest
- [ ] build
- [ ] Tier 1
- [ ] Tier 2
- [ ] headed review (only when required)
- [ ] final report
```

`MEMORY.md` records technical discoveries, chosen IDs/keys, actual commands/results, and repair
attempts. Do not duplicate DESIGN or SPEC state there.
