# Spec - write the implementation work order

Read `DESIGN.md`, `semantic-contract.md`, the selected `surfaces/<surface>.md` pages, and only
the recipe/reference pages needed by the current request. Write `SPEC.md` at the outer project
root. This is the one artifact Author follows.

## Lower the accepted scope

Write only the current supported work. For every element or operation make these facts explicit
where applicable:

- name, logical identity, surface, pool/availability, owner, and relationships;
- trigger, target, conditions, ordered effects, values, upgrades, and calculation timing;
- state owner, transitions, bounds, lifetime, reset, persistence, visibility, and consumers;
- exact English and Simplified Chinese text, already written in the vanilla style of
  `reference/vanilla-text-style.md` (glossary terms, colors, line breaks, Chinese
  punctuation and measure words), localization table/key intent, formatting variables, and
  the hover tips each description needs;
- art/presentation choice, real consumer, and fallback;
- maintained recipe/reference routes in `## Implementation`; and
- real-host autotest scenarios in `## Autotest`.

Do not copy DESIGN rationale or deferred work into implementation. Do not embed scope,
deliverable, coherence, settlement, repair, surface-data, or evidence JSON. A simple Mod should
have a simple SPEC.

## Use the owner pages

Each selected surface page owns its exact domain vocabulary and proof matrix. Preserve all
current product capabilities, including:

- new Card/Relic/Potion/Power/Keyword/Enchantment/Orb content;
- complete singleplayer Acts with explicit entry policies, and new Shared/Act-scoped Ancients;
- combat Card Afflictions, selectable run Modifiers, scoped Global Effects, and independent Rest
  Site actions;
- custom Rewards with native claim/refusal and pending-save reconstruction, and independent Card
  Piles across the complete documented public API;
- local Mod-owned Runtime UI workflows using selected top-bar, Toast, runtime-hotkey, Capstone,
  Catalog, floating-window, search-expansion, fixed node-attachment, and shell-token routes;
- Monster move graphs and Encounter rosters;
- ordinary Events, supported native presentation, and bounded forced follow-up Events;
- playable Character Foundation, presentation, dialogue, combat cues, secondary resources,
  and ordered semantic buffers;
- computed Card values, advanced targeting, bounded state, Rest Site options,
  readability, and custom static art;
- grounded vanilla Card, visual, Ancient, availability, and non-Card overrides; and
- cataloged model-hook participation only on surfaces in its dispatch listener set.

For the exact current boundary, use the selected surface pages and `sts2api` references. When no
maintained route covers an operation, ground it as a Mod-local route under
`${STS2API_SKILL_DIR}/grounding.md` § Mod-local Routes and record it as a `- Mod-local:` line in
`## Implementation`. A prompt is never authority to invent an ungrounded API.

## Implementation

List every selected maintained route exactly once. Example:

```markdown
## Implementation

- Support: `recipes/card.md`
- Support: `reference/card-computed-values.md`
```

An operation with no maintained route adds one `Mod-local` line naming its grounded public members:

```markdown
- Mod-local: <operation> - <public Owner.Member list>
```

For raw model-hook participation, add one line per capability. Global Effect uses the exact
`global-effect-run` or `global-effect-combat` dispatcher surface from its selected singleton
scope:

```markdown
- Hook: modify_damage_multiplicative | surface: power | shape: value | route: reference/model-hook-participation.md
```

Do not add a Hook line for ordinary recipe behavior. Do not cite a heading fragment. For a hook,
copy `shape` from `reference/catalogs/model-hooks-sts2-0.107.1.json`, preserve unrelated
collection entries for collection edits, and state the subject guard, condition, value/edit,
neutral result, DynamicVar text binding, and ordering in the human-readable operation above.

Run the only pre-Author check after writing the SPEC:

```powershell
python ${GAME_TOOLS_DIR}/capability_preflight.py --spec SPEC.md
```

This check is intentionally thin. It does not judge missing ordinary fields, Markdown layout,
business rules, C# types, manifests, localization payloads, runtime lifecycle, visuals, or proof.

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

## Autotest

Write concrete scenarios, not evidence placeholders. Each scenario names:

- `CombatPlayer`, `CombatEnemy`, `MapNode`, `RunStart`/Character, or the closest maintained host;
- how SelfTest reaches and drives the real source interaction;
- exact expected post-state values and object identities;
- neutral, rejection, degenerate, reset, branch, or unrelated-entry preservation cases required
  by the selected behavior;
- the structured `state proof:` pattern emitted only after assertions pass; and
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

- `CombatPlayer`: add the real Card, play it against a live enemy, wait for queued commands,
  assert exact HP loss after native modifiers and assert the Card is in Discard.
- Emit `[T2MOD-SELFTEST] <ModName> state proof: card damage expected=9 observed=9; pile=Discard`
  only after both assertions pass, then emit `selftest done`.
```

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
