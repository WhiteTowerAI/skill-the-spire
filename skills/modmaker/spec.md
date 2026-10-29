# Spec - write the implementation work order

`DESIGN.md` preserves human intent. `SPEC.md`, at the outer project root, is the only
implementation work order: exactly what to generate, which recipes and references support it, and
how the real host will prove it. Keep it readable by both the user and the authoring agent. Read
`DESIGN.md`, the selected element recipes (`../sts2api/recipes/<surface>.md`), and only
the reference pages the request needs. Each recipe owns its element's SPEC fields, vocabulary,
proof matrix, known limitations, and manual fallback.

## What every operation says

Write only the current supported work, in ordinary Markdown, using the selected recipe's SPEC
fields. For each content element or existing-content change, state the applicable facts:

- name, content identity, surface, pool/registration/availability, ownership, and relationships;
- trigger, target, conditions, ordered effects, exact values, upgrades, calculation timing, and
  native result pile;
- state owner, transition timing, bounds, lifetime, reset, persistence, visibility, and consumers;
- exact English and Simplified Chinese player-facing text in the vanilla style of
  `reference/vanilla-text-style.md`, including table/key intent, DynamicVar/SmartFormat names,
  variable parity, and hover tips for every named term;
- presentation, art choice, the user's sound files (`reference/audio.md`), native consumers, and
  checked fallback; and
- one or more autotest scenarios (§ Autotest).

Omit fields that do not apply rather than writing `none` into a generic schema. Never copy DESIGN
rationale, future ideas, verification outcomes, or stage status into SPEC, and never embed scope,
coherence, settlement, repair, or evidence JSON. A simple Mod has a simple SPEC. Framework class
names, manifest structure, packing, and concrete API signatures belong to the recipes, Scaffold,
and Build; SPEC names the recipe instead of copying them.

For a multi-surface request, keep each truthful owner and order the implementation and SelfTest
assertions by the real dependency flow. Never invent a combo surface, collapse one owner's
lifecycle into another, or use a deferred family as coordination.

## Check that every number can be reached

Build, Tier 1, and Tier 2 all pass on a condition that never fires in a real run. Before writing
Implementation, check in your head, writing nothing:

- every threshold, cost, or condition (for example "if you have 10 Strength") has a source the
  player can actually get in this Mod's pool, Character, or vanilla content; and
- every Mod-owned counter or resource has both a source and a spend or reset.

When one fails, ask the user one question with a recommended fix. Never silently change an
accepted value. Under delegation, fix a value marked `(delegated)` yourself, update DESIGN, and
say so in the confirmation; a value the user stated still gets the question.

## Implementation

End every new or revised SPEC with one short `## Implementation` section, the author's route
list:

```markdown
## Implementation

- recipes/card.md
- reference/card-computed-values.md
- reference/effect-primitives.md
- Hook: modify_damage_multiplicative on the custom Power (value shape), see reference/model-hook-participation.md
- Mod-local: grant gold - PlayerCmd.GainGold
```

- List each recipe and reference the current work uses once.
- Write ordinary player-visible results as one ordered `effects.sequence` in game terms. When it
  uses damage, Block/healing/HP, Powers, native resources, draw/discard/exhaust, known-Card
  creation, known run-content acquisition, or Orb queue/slot effects, list
  `reference/effect-primitives.md`. A sequence that needs selection, a Reward/Event/Rest Site
  transaction, Card-play lifecycle control, or a custom Card Pile also lists that owning route.
  If the callback cannot supply a primitive's required context, owner, source, or target, record
  the exact unsupported combination instead of changing the accepted result.
- For a raw model hook, name the hook, its owning element, and its catalog shape from
  `reference/catalogs/model-hooks-sts2-0.107.1.json`, and state the subject guard, condition,
  value or edit, neutral result, DynamicVar text binding, and ordering in the operation above.
  Build fails an override whose surface the hook never reaches. Ordinary recipe behavior needs no
  Hook line.
- For an operation with no maintained route, add `Mod-local: <operation> - <public Owner.Member
  list>`, grounded under `../sts2api/grounding.md` § Mod-local Routes.

Never put an unverified API symbol in SPEC; a prompt is never authority to invent one.

## Autotest

Sort the content first (`../sts2api/reference/selftest-harness.md` § Which content
gets which check):

- registration and bilingual text of every content model: the kit's roll call checks them on
  every run; write nothing;
- each **simple Card** (its Implementation lists only its recipe and
  `reference/effect-primitives.md`, its numbers are fixed, and it has no condition): list it
  under `Face checks:`; it gets no scenario; and
- everything else: one concrete scenario per selected behavior, never an evidence placeholder.

Each scenario names:

- a unique `snake_case` name, which `launch.py --only` reruns;
- `CombatPlayer`, `CombatEnemy`, `MapNode`, `RunStart`/Character, or the closest host;
- how it reaches and drives the real source interaction;
- exact expected post-state values and object identities;
- the neutral, rejection, degenerate, reset, branch, or unrelated-entry preservation cases the
  selected behavior requires; and
- any headed mouse/controller/art/animation/subjective observation, kept separate.

Every scenario runs in singleplayer and again in the two-instance multiplayer run with the same
expected values. Behavior that needs two players (ally targeting, a multiplayer-only Card, a
team effect) gets a `CoopPlayers` scenario instead, run only in multiplayer, naming what each
player does and what each sees.

Tier 2 asserts state after the host processes the action. A hook-fired log, preview value,
model-only mutation, resource path, or successful Build is not a scenario pass. Mouse/controller
UI, animation, image framing, and subjective experience stay headed human observations.

## Example

```markdown
# SPEC - Ember Step

## Card

- Create a shared Common Attack named Ember Step with logical id `ember_step`.
- Cost 1 Energy. On play, target one enemy, deal 9 Damage, then move normally to Discard.
- Upgrade changes Damage from 9 to 13.
- English: `Deal {Damage:diff()} damage.`
- Simplified Chinese: `造成{Damage:diff()}点伤害。`
- Use the checked placeholder Card portrait.

## Implementation

- recipes/card.md
- reference/effect-primitives.md

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
- [ ] scaffold
- [ ] author and SelfTest
- [ ] build
- [ ] Tier 2 (includes the Tier 1 load check)
- [ ] headed review (only when required)
- [ ] final report
```

`MEMORY.md` is the one technical log; never duplicate DESIGN or SPEC there. Every stage appends to
the same sections:

```markdown
# MEMORY

## Project
- project path: <absolute outer directory>; Mod name: <ModName>; profile: <profile id>
- deployed: <mods/<ModName>/ path once Build passed>

## Resolved identities
- <element>: class <Type>, entry <MOD_CATEGORY_TYPENAME>, loc keys <table: keys>, hooks used,
  state lifetime/reset/persistence, art outcome (placeholder or file, and why a fallback)

## Grounded signatures
- <Mod-local operation>: <exact public Owner.Member signatures>

## Commands and results
- <stage>: <command> -> <result line>

## Repair attempts
- <stage>: <failure signature> -> <one change> -> <result>
```
