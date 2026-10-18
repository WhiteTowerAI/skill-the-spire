# Interview - resolve only the open design decisions

Goal: turn the routed request into enough certainty to write or revise `DESIGN.md`, then
lower its current slice into `SPEC.md`,
**asking as little as possible**. Read `route.md` first and carry its settled decisions,
defaults, delta, and gaps forward. The user is a non-programmer; keep it plain.

## Rules

- **Follow the selected route.** Fast asks no question when complete and at most one compact
  round otherwise. Co-design resolves the smallest high-impact decision with materially
  different choices and trade-offs. Revision asks only about the requested delta.
- **Ask only material questions.** Everything else gets a sensible default that is stated
  later, not presented as another decision.
- **Preserve settled decisions.** Anything already fixed by the prompt or project artifacts is
  not a question.
- **No jargon.** Say "when does it happen?" not "which combat hook?". Never ask
  about classes, namespaces, or APIs.
- **Keep the interaction proportional.** Batch up to three independent short questions;
  keep dependent co-design decisions incremental.
- **Do not ask workflow questions.** Ask about the intended player result only when the user's
  words permit two materially different implementations.
- **Expose real conflicts.** Contradictory or unsupported requirements pause before SPEC;
  use `route.md`'s constrained resolution and explicit-acceptance rules.
- **Ground Character proposals first.** For a Character or Character/content-set request,
  load `${STS2API_SKILL_DIR}/design/character-foundation.md` before creative questions.
  Recommend an exact native-shaped starter deck before asking for deck details, and label
  pinned facts, observed conventions, and creative decisions distinctly.
- **Ground "like vanilla X" first.** When the user models a new element on an existing one,
  run `python ${GAME_TOOLS_DIR}/vanilla_overrides.py resolve <name> --category <card|relic|potion|power>`
  and pre-fill from the record: cost, type, values and upgrade, keywords, pool, and rules
  text. Restate it in one plain line for the user to confirm; the analog fills answers and
  skips no later stage. Changing X itself is an override (step 1 below), not a new element.
  - The user names Slay the Spire 1, or what they describe differs from the record: ask one
    question about which they mean.
  - Nothing resolves and the suggestions do not fit (a Slay the Spire 1 or other-Mod
    element): design it as a new element. Any recollection of it is an unverified draft
    the user confirms, never copied content. If it shares a name with a different STS2
    element, suggest a new name.
- **Plan only when routed.** Load only the mechanic, content-set, and balance references
  named by `route.md`. An exact narrow Card keeps the fast path and does not receive a
  general design review merely because it has numbers.
- **Check cross-surface consistency only when needed.** For multiple intentional expressive
  surfaces, explicit theme/narrative/presentation work, or an identity-changing revision,
  compare the selected mechanics, names, text, and visuals against the accepted decisions.
  Name an exact conflict and ask only when resolving it is a creative choice.

## Compact planning pass

Run this pass only when `route.md` selected one or more planning references. Resolve
the highest-impact open design decision first, then use accepted choices and safe defaults
to complete only the relevant parts of the capsule below.

- **Mechanic:** preserve one player fantasy, the competing actions/timings and state that
  favors each, the trigger-to-payoff/reset loop, risk/reward, singleplayer pressure or
  opportunity cost, exact edge rules, and independent tuning knobs. Compare plausible
  repeated lines in unfavorable, ordinary, and favorable states, including ignoring the
  mechanic.
- **Content set:** assign real proposed content nodes the smallest useful roles across
  Foundation, access, payoff, consistency, defense, scaling, bridge/off-ramp, and release
  valve. Record directed source-to-dependent relationships; flag isolated nodes, circular
  prerequisites, coverage gaps, unsupported edges, and an archetype that receives easier
  access, safer setup, and a higher ceiling at once.
- **Balance/economy:** name the output unit, deterministic formula, variables, timing,
  assumptions, constraints, comparison basis, every source and sink, opportunity cost,
  low/working/high sensitivity, and the evidence status. Default to a generous working
  hypothesis that is modestly stronger in its intended state, but repair any value that
  erases choices, bypasses setup/cost, trivializes ordinary opposition, or becomes
  deterministic, self-funding, or unbounded. Never invent a fixed power percentage.

Ask only about an unresolved choice whose answers change player behavior or the current
supported implementation. Offer two or three structures rather than number-only variants
when the mechanic itself is unclear. A missing measurement, trigger rate, formula input, or
human play result stays an open hypothesis.

This pass produces a compact planning capsule, not a durable artifact. The following
`design.md` stage records the accepted intent and scope without re-asking settled decisions.

## Compact consistency pass

Run this pass only when multiple intentional surfaces or a related revision make it useful.
Inspect selected mechanics, naming, localization, visuals, Event text, and Character identity
against accepted decisions. Do not force the same word, palette, or imagery everywhere.

If two surfaces contradict behavior, drift one gameplay term, break the accepted identity,
leak deferred/unsupported scope, or present flavor/build evidence as gameplay proof, name
both sides and the player-facing consequence. Offer the smallest resolution and pause
before DESIGN/SPEC until the user decides. Preserve an accepted contrast as deliberate
tension rather than repeatedly "fixing" it.

For revision, inspect only artifacts that can depend on the changed decision. Carry a plain
keep/change/reverify summary forward; do not create a queue or edit every downstream file.

## What to resolve (only if unclear from the sentence)

1. **Surface.** Infer the element from the player's words, then read its page under
   `surfaces/`:
   - a passive or triggered effect the player *has* -> `relic`;
   - something played from hand for a cost -> `card` (a shared rule several Cards use ->
     `keyword`; a persistent change attached to one Card -> `enchantment`; a buff/debuff no
     vanilla Power covers -> `power`; a channeled orb -> `orb`);
   - a one-shot consumable -> `potion`;
   - a monster the player fights -> `monster` (Monster plus the Encounter that spawns it);
   - a story/choice room on the map -> `event`;
   - a complete playable chapter -> `act`; a new Ancient encounter -> `ancient`;
   - a claimable option on the native rewards screen -> `reward`;
   - a named place where Cards are stored, moved, or shown -> `card-pile`;
   - a Mod-owned top-bar workflow, notification, hotkey, local screen, or catalog ->
     `runtime-ui`;
   - a new selectable hero -> `character`; a Card affliction, run Modifier, global rule, or Rest
     Site action -> `affliction`, `modifier`, `global-effect`, or `rest-site`.

   A change to an existing vanilla model starts at `reference/vanilla-overrides.md`, which
   routes to the Card, visual, Ancient, availability, or non-Card override reference. Offer a
   closest **new** element only as a separate user choice, never as an automatic substitution.
   **Change only what was named, and keep the text true.** For a vanilla Card, pick the
   operations from the § Pick routes table in `reference/vanilla-card-overrides.md`: a changed
   number is one variable-value change, and a changed behavior also rewrites the Card's rules
   text. Never rename the model, add a name marker, or touch another surface the user did not
   ask about. Do not ask whether the description should change with the effect; it does.

2. **Open fields.** The selected surface page's SPEC fields (or "DESIGN and SPEC vocabulary")
   list everything SPEC must settle. Ask only about a field the request leaves materially open;
   fill the rest from the defaults below and state them at confirmation. Never ask about
   classes, enums, hooks, keys, delegates, or APIs. Surface-specific question rules:
   - **Relic:** map the trigger to a lifecycle moment. When it counts progress ("every 3
     turns", "once per combat"), ask only if the reset boundary is genuinely ambiguous:
     "Should progress continue into the next fight, or restart each fight?"
   - **Potion:** resolve usage window and target only when the effect leaves them ambiguous. A
     filtered single target is supported; a filtered many-target Potion is a pinned-profile gap,
     so offer a filtered single-target Potion or a filtered many-target Card instead.
   - **Card:** resolve cost, type, and target only when ambiguous. For a filtered target, ask
     only the missing game rule. Vanilla text coloring is automatic
     (`reference/vanilla-text-style.md`); never ask about it. Only when the user asks for extra
     colored words, capture the exact phrase and plain color intent, never raw BBCode. For a calculated number, capture one formula, its inputs, an
     integer range, and base/upgrade behavior; when playing the Card changes an input, ask:
     "Should this count the state before this card spends its energy and leaves your hand, or
     just after?" For hand highlights or Relic/Power extra badges, capture meaning, condition,
     color, and priority; the limits live in their references.
   - **Monster:** capture each Monster's HP, visible moves, and successor order. Default to the
     stated repeating order and never invent randomness. Intent extra badges have no
     maintained route; treat them as a Mod-local route under
     `${STS2API_SKILL_DIR}/grounding.md` § Mod-local Routes.
   - **Event:** capture the opening, each option's exact consequence, and whether it finishes,
     opens a page, blocks on a selection/reward, or enters the one special combat an Event
     instance allows (with its full encounter). Offer VFX, screen shake, text effects, or a
     forced follow-up only when the user asks, and only as the bounded profiles on the Event
     page.
   - **Existing vanilla Ancient:** resolve the exact Ancient, then append versus replace-all.
     Capture every choice's visibility, lock, single fixed cost, hover content, ordered
     consequences, and next step. A replacement must describe the complete initial list with a
     reachable finish; never silently keep unspecified vanilla choices inside it.
   - **Existing vanilla Card:** capture the new numbers (and the new upgrade amount, when it
     changes) or the complete new behavior. Draft the new `eng`/`zhs` rules text yourself in
     the vanilla style and show it at confirmation next to the vanilla text.
   - **Existing vanilla non-Card data/behavior:** capture the final value or delta, or the real
     trigger, scope, condition, and ordered result. For a complete behavior replacement, confirm
     that everything on that named surface is being replaced. A Relic or Potion whose
     description stops being true gets new rules text the same way as a Card.
   - **Character:** load `${STS2API_SKILL_DIR}/design/character-foundation.md` first. If the
     core mechanic is unclear, ask that one decision, then propose a complete exact starter deck;
     never ask the user to name ten Cards from a blank form. Secondary resources, ordered buffers,
     and Ancient dialogue capture the fields in their references. Physical played Cards kept in
     a custom zone are unsupported.

3. **Effect numbers.** Record exact game-term numbers. For a card, also capture what upgrading
   improves (default: the main number). When an effect counts events, record the exact event
   and threshold; do not collapse "every N" into "on the Nth", and state whether the triggering
   event counts before the check.

4. **Art: one question for the whole Mod.** Ask it once, in the same round as the other open
   questions, never per sprite. When the route would otherwise ask nothing, do not open a
   round just for art: use placeholder and say in the final report that art can be added
   later with these choices. Offer the choices in the user's language and plain words:
   - **0. Placeholder art everywhere** — the default and the fastest way to a playable Mod;
     art can be added later.
   - **1. Your agent's own image tool** — no setup; uses the current subscription. List it
     only when this runtime actually exposes a callable raster image tool that yields a
     local file (`host-tool`). In Codex that is the built-in `image_gen` tool from the
     `imagegen` skill, which needs no `OPENAI_API_KEY`. Claude Code has none built in; list
     it there only when the user has connected an image tool that writes local files. A
     model name or skill file alone does not prove the tool exists.
   - **2. Your own image service** — an API key (OpenAI, Gemini, OpenRouter, or another
     compatible platform) or a local command such as ComfyUI or a script. Spends the user's
     own credit.
   - **3. Images you already have** — the user supplies the files; import fits and places
     them.

   No answer means 0. The supported specs and their boundaries live in
   `${STS2API_SKILL_DIR}/reference/art-contract.md`; requests outside them (Spine,
   animation, phobia variants, custom layouts) stay explicit gaps. Then set up only the
   chosen route, never probe the others:
   - **0**: record `art: placeholder`.
   - **1**: record `art source: host-tool`.
   - **2**: ask which service. For OpenAI, Gemini, or OpenRouter, the user sets
     `OPENAI_API_KEY`, `GEMINI_API_KEY`, or `OPENROUTER_API_KEY` in their own environment;
     the built-in backend names are `openai`, `gemini`, and `openrouter`. A newly set
     variable reaches only a newly started agent session. For any other endpoint or a local
     command, the user adds a named entry to `~/.skill-the-spire/art-backends.json` per
     `art-contract.md` § Backend config; offer to write it with `api_key_env` instead of the
     key. Never ask the user to paste a key into the conversation. Then run
     `python ${GAME_TOOLS_DIR}/gen_sprite.py check --backend <name>` once (it requests no
     image). On success record `art source: backend:<name>`; on failure say what is missing
     and let the user fix it, pick another choice, or keep placeholder.
   - **3**: ask which file belongs to which asset; record `art source: local-image`. When
     the art sits inside a larger picture (a whole card with frame and text), crop it
     with `gen_sprite.py grid` and `import --crop` per `art-contract.md`; anything beyond a
     rectangular crop is the user's own edit.
   - For 1 and 2, capture one overall subject/style note. `author.md` derives each asset's
     subject from its SPEC. Before any paid route, show how many image calls it will spend.
   - For a Character with 1 or 2, offer its art tier in the same message, with the call
     counts from `character_art_tiers` in
     `${STS2API_SKILL_DIR}/reference/catalogs/art-contract-sts2-0.107.1.json`:
     **minimal** (selection portrait plus the combat, rest, and merchant bodies; everything
     else keeps the base-game Ironclad art), **standard** (all static Character art, no
     combat animation), or
     **full** (standard plus one combat-animation sheet; offer it only when the chosen
     route returns 2048x2048 images, see `reference/character-combat-cues.md`). No answer
     means minimal.
     Record `character art tier: <name>`. The locked selection portrait and map marker are
     in no tier; generate them only when the user names them.

## Defaults (apply silently unless the user specified otherwise)

- **Rarity**: Common.
- **Pool**: the shared/colorless pool (`SharedRelicPool` for a relic,
  `SharedPotionPool` for a potion, `ColorlessCardPool` for a card) — any character.
- **Usage** (potion): `CombatOnly` unless the effect only makes sense out of combat
  (heal, max-HP, card generation → `AnyTime`).
- **Target** (potion): self-buff → the player; damage → one enemy. Only ask if genuinely unclear.
- **Cost** (card): 1 energy unless the effect implies otherwise.
- **Type** (card): infer from the effect — damage → `Attack`, block/utility → `Skill`,
  permanent buff → `Power`.
- **Target** (card): damage → one enemy (`AnyEnemy`); block/self-buff → `Self`. Only
  ask if genuinely unclear.
- **Upgrade** (card): improve the main number (more damage/block/stacks). State it.
- **Rest Site option** (standalone or requested on a Card, Relic, or Modifier): singleplayer only; distinguish
  when it is absent from when it is visible but gray; default to once per Rest Site,
  normal leave behavior, checked native Heal-icon fallback, and free cost unless the idea
  names a fixed Gold price. Ask only for an unresolved repeatability or stay/leave choice.
  A Card owner requires exactly one matching deck instance. A Modifier owner requires that exact
  selected run Modifier. Arbitrary costs, post-payment choices, and same-site repeat remain
  unsupported.
- **Runtime UI**: local-only; one owning coordinator; pure null-player-safe top-bar providers;
  text-input/dev-console hotkey suppression; controller focus/back behavior; deterministic local
  search; explicit close/disposal; and Mod-scoped shell tokens. Do not silently add a custom icon,
  saved geometry, search provider, node attachment, or any deferred-family UI when the request does
  not need it.
- **Name**: derive a short, flavorful name from the concept; confirm in the SPEC summary.
- **Acts** (event): all acts unless the user specifies a setting.
- **Event VFX**: none unless explicitly requested; then use only `portrait_halo` or
  `trial_noble` on named normal-layout pages.
- **Event acquisition presentation**: native whenever a successful option adds a known
  Card to the Deck or obtains a known relic; never a second grant.
- **Event screen shake**: none unless explicitly requested; then one `weak_short` or
  `strong_normal` call on the named successful option, inheriting the player's preference.
- **Text style**: vanilla, always (`reference/vanilla-text-style.md`): glossary terms and
  colors, per-surface numbers and line breaks, native Chinese. Not a question.
- **Event extra atmosphere**: none unless explicitly requested or clearly described; then use
  only the bounded vanilla rich-text vocabulary on named page/option description phrases.
- **Forced Event follow-up**: none unless explicitly described; default to one custom Quest
  Card forcing one custom Event from the next Unknown MapPoint in one act. When the request
  needs more, use only a finite prioritized mapping/sequence with exact terminal consumption.
- **Character Foundation**: 70 HP, 99 Gold, 3 MaxEnergy, zero base Orb slots, one Starter
  relic, no starter Potions, and valid character-scoped pools are native-shaped creative
  starting points, not mandatory output values. Record the exact current selections.
  Unless the idea supports another native analogy, propose an exact 10-Card Basic deck of
  4 Character-specific Strike, 4 Character-specific Defend, and 2 low-complexity identity
  Cards that teach setup/payoff. Preserve the pinned Strike/Defend names, values, upgrades,
  and tags by default. This is an observed native-shaped recommendation, not a universal
  `4/4/2` or ten-Card rule. Derive the teaching Cards and Starter relic from the stated
  theme, state the complete proposal at confirmation, and accept deliberate implementable
  departures after recording their consequences.
- **Character Ancient dialogue** (only when requested): Character first-visit group plus a
  repeat group from visit 2; preserve the native global first-visit-ever introduction. A
  complete Architect group remains mandatory for every Character; default its start
  attackers to None and end attackers to Architect when the user does not specify them.
- **Secondary resources** (only when requested): one or more bounded nonnegative resources;
  default to combat persistence, zero start, no turn-start change, required fixed payment,
  and a built-in combat counter/Card line only when visible. Never reinterpret native Energy.
- **Ordered semantic buffer** (only when requested): combat lifetime, normal Play ->
  Discard source lifecycle, finite capacity, reject overflow without mutation, preserve
  semantic insertion order, show compact state, and create one deterministic real output
  Card. Retained-card zone UI is unsupported.
- **Monster move order**: moves repeat in the order stated. Add a conditional or fixed-weight
  random branch only when the concept names it or the user confirms it; never invent random choice.
- **State lifetime**: "every N turns" on a relic continues across combats in the current
  run; "on turn N of each combat" uses that combat's turn number. Turn-local/once-per-
  combat wording resets at the boundary it names. Ask one carry-over question only when
  the phrase could reasonably mean either behavior.
- **Art**: placeholder unless the user picks another choice in step 4.
- **Author**: reuse the project's configured author, else "SkillTheSpire".

## Output

A compact intake you carry into `design.md` and `spec.md`. Prefix every intake with:

```text
path: fast | co-design | revision | resume
intent: <one player-facing sentence>
settled: <choices preserved from the request and project artifacts>
defaults: <inferred values to state in the confirmation>
native grammar: none | <loaded native grammar and pinned profile>
planning references: none | <loaded mechanic/content-set/balance references>
revision delta: none | <keep/change/reverify summary>
current scope: <requested now>
not now: none | <placeholder, deferred, unsupported, or explicitly excluded work>
consistency conflicts: none | <exact conflicting decisions or surfaces awaiting resolution>
player fantasy: none | <repeated action -> intended feeling>
core decision: none | <line A versus line B; state that favors each>
loop: none | <input -> visible state -> choice -> feedback/payoff -> reset>
risk/reward: none | <commitment, information, agency, payoff>
counterplay/pressure: none | <player-facing constraint or opportunity cost>
rules/edge cases: none | <accepted exact rules and boundaries>
content roles: none | <real content nodes and selected roles>
interaction graph: none | <directed source -> dependent relationships and gaps>
formula/economy: none | <formula contract, sources/sinks, assumptions, sensitivity>
tuning knobs: none | <independent values and the behavior each changes>
dominant-strategy check: none | <lines compared, concern, mitigation or none>
open hypotheses: none | <unproven claim and evidence needed>
```

Then list, in plain language, the selected surface page's SPEC fields for each element,
omitting fields that do not apply. A vanilla override lists its target reference's operation
fields instead, plus one `unchanged:` line naming the surfaces that stay vanilla (always the
name, unless the user asked for a new one).

Do not write files here - `design.md` writes the durable intent, decisions, and scope, and
`spec.md` lowers the current slice. If fast routing found nothing material to ask, skip straight to `design.md`
with the inferred intake. If this is a revision, preserve every unrelated design decision,
runtime/localization identifier, and existing SPEC operation outside the confirmed delta.
