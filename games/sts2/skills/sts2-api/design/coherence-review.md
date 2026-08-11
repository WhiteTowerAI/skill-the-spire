# Theme, narrative, presentation, and coherence review

Load this reference when a new or revised design has more than one intentional expressive
surface, explicitly requests a theme/narrative/presentation direction, or changes an
existing identity anchor. It guides DESIGN review and revision propagation. It is not a
runtime route and does not add art, localization, Event, Character, or other capabilities.

## Start from durable decisions

Derive one to three concise identity anchors from accepted `D-###` decisions. An anchor is
an observable promise such as "build pressure deliberately, then release it" or "a careful
oracle who turns foreknowledge into defense." It is not a mood adjective by itself and it
must not invent lore, mechanics, assets, or future support.

Use only the current surfaces selected by the design:

- **mechanics:** repeated player action, decision, feedback, and payoff;
- **naming:** Character, mechanic, Card, relic, option, and page vocabulary;
- **localization:** stable gameplay meaning, terminology, numbers, and intended tone across
  required `eng`/`zhs` and any additional shipped languages, without requiring word-for-word
  phrasing;
- **visuals:** selected motif, palette, silhouette/focal subject, and supported consumer;
- **Event text:** situation, option wording, speaker voice, consequence, and page arc; and
- **Character identity:** fantasy, Foundation teaching pair, Starter relic, resource, and
  selected presentation as one player-facing identity.

A checked placeholder is a delivery state, not an expressive visual claim. Do not invent a
palette or lore for placeholder art. A narrow exact Card may need only one anchor and a
compact mechanics/naming check; keep it on the fast path and ask no style questionnaire.

## Review relationships, not adjective matching

For each applicable surface, state how it communicates an anchor to the player. Repeating
the same color or word everywhere is not coherence. Prefer complementary signals: mechanics
teach the decision, names expose the vocabulary, visuals make state legible, and narrative
frames why the choice matters.

Treat an unusual contrast as `deliberate-tension` when the user selected it and its purpose
is recorded. Irony, deceptive names, or a visual/narrative contrast are not automatically
errors. Never normalize a settled creative departure merely because a more literal theme
would be easier.

Flag a material conflict when one selected artifact or planned output:

1. **contradicts behavior:** text or presentation promises a result different from SPEC;
2. **drifts terminology:** the same gameplay concept has incompatible names or meanings;
3. **breaks identity:** a Character/content surface teaches or celebrates the opposite of
   its accepted fantasy and no deliberate tension explains it;
4. **leaks scope:** theme polish introduces a deferred, out-of-scope, or unsupported
   operation; or
5. **inverts evidence:** build/static reasoning, a visual, or flavor text is presented as
   proof of behavior, balance, or player experience.

Name the exact two decisions/artifacts and the player-facing consequence. Temporarily mark
the affected surface `conflict` and add the specific conflict record. Offer the
smallest repair: align the downstream expression, revise the anchor with explicit user
acceptance, or record the contrast as a deliberate tension. Keep the conflict unresolved
until the user selects one; do not write SPEC or author while conflicts remain. Resolution
changes the surface to `aligned` or `deliberate-tension` and clears the conflict record.

## Localization boundary

Check semantic parity, not literal sentence parity. Names for a gameplay term, costs,
numbers, conditions, targets, and outcomes must preserve the same rule. Flavor, rhythm,
idiom, and sentence structure may adapt by language. Do not claim translation quality for
languages that were not reviewed, and do not turn a localization correction into a design
change unless the intended meaning itself changes.

## Revision impact queue

Before editing a revised project, compare the requested delta with current DESIGN, SPEC,
localization, visual prompts/resources, Event text, Character identity, generated source,
and verification evidence only where they exist and can depend on the changed `D-###`
items. Produce an ordered `Q-###` queue:

- `UPDATE`: the artifact directly encodes the changed decision;
- `REVIEW`: it may express or depend on the changed anchor and needs a bounded check;
- `REVERIFY`: generated behavior or presentation changed, so name the closest proportional
  verification host/check; and
- `PRESERVE`: explicitly protect a settled or rejected decision at real risk of accidental
  change or reintroduction.

Order DESIGN before SPEC, then localization/narrative/visual expressions, generated source,
and verification. Do not list every repository file, reopen unaffected PLAN stages, or
rerun a full acceptance. A future-vision prose edit with no current dependency may have a
DESIGN-only update. Prompt-only wording changes need no runtime proof. Actual generated
behavior or presentation changes follow the nearest-host rule.

Stable runtime/localization identifiers are technical facts in MEMORY; a display-name
revision does not rename them automatically. Put them in `REVIEW` and change them only when
the implementation contract requires it.

## Artifact handoff

Write one `open-mod-coherence/v1` block in DESIGN after the scope ledger. New fast/co-design
work has an empty queue. Revision work records every affected or deliberately preserved
target. All anchors and surface checks reference stable design IDs, and `conflicts` must be
empty before SPEC.

Run `coherence_trace.py --design <outer-dir>/DESIGN.md`. The validator checks structure,
references, current-surface ownership, and revision queue completeness. It cannot decide
whether prose, art, localization, or gameplay is genuinely coherent; the semantic scenario
rubric and human decisions own that judgment.
