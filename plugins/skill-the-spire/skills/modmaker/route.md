# Route - continue, clarify, or revise

Read project state before asking questions. `DESIGN.md` holds accepted intent and scope,
`SPEC.md` is the current implementation work order, `PLAN.md` is only a stage checklist, and
`MEMORY.md` holds technical discoveries and attempt history.

Choose the smallest useful path and state it briefly:

- **Fast:** a narrow request already has one clear player-facing meaning. Ask no question when
  safe defaults complete it, otherwise ask one compact clarification round.
- **Co-design:** a mechanic, Character, content set, or interacting system has a material open
  choice. Present two or three genuinely different outcomes and their trade-offs.
- **Revision:** the user changes an existing Mod or reports a play result. Read the artifacts,
  preserve everything outside the requested delta, and ask only about a new contradiction.
- **Resume:** the user requested no change and work is unfinished. Continue from the first
  incomplete stage without another interview.

Load only the design references that the current question needs:

- Character/Foundation: `design/character-foundation.md`
- unclear mechanic or loop: `design/mechanic-planning.md`
- Character, archetype, or content set: `design/content-set-planning.md`
- material numeric/economy question: `design/balance-planning.md`

Do not ask for game, catalog, API, localization-key, or resource-path facts that the shipped
pack owns. Do not ask about optional polish the user did not request. A default stops being
safe when it changes the core player experience.

For contradictory input, name the conflict and ask one constrained resolution question. For
an unsupported operation, name the exact missing public/fixed route before SPEC or scaffold.
Offer a supported alternative only when it preserves the intent, and obtain explicit acceptance
because the player-visible result changes. Never invent Harmony, reflection, Publicizer, or IL.

Carry this compact handoff to Interview or DESIGN:

```text
path: fast | co-design | revision | resume
intent: <one player-facing sentence>
settled: <facts and choices to preserve>
open: none | <only material unresolved choices>
defaults: <safe inferred details to disclose>
references: none | <design references read>
current scope: <what the user wants now>
not now: none | <explicitly deferred or excluded work>
revision delta: none | <keep/change/reverify summary>
```
