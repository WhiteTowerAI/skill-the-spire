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
- **Preserve settled decisions** (`INV-6`). Anything already fixed by the prompt or project
  artifacts is not a question.
- **No jargon.** Say "when does it happen?" not "which combat hook?". Never ask
  about classes, namespaces, or APIs.
- **Keep the interaction proportional.** Batch up to three independent short questions;
  keep dependent co-design decisions incremental.
- **Never ask for the deliverable claim.** Carry `deliverable signals` forward from
  `route.md` and let `design.md` write the claim from the settled intake. "What kind of
  deliverable do you want?" is exactly the workflow-mode question routing already refuses to
  ask. Ask only when the user's own words point at two materially different finished things
  and the answer changes which operations get generated.
- **Expose real conflicts.** Contradictory or unsupported requirements pause before SPEC;
  use `route.md`'s constrained resolution and explicit-acceptance rules.
- **Ground Character proposals first.** For a Character or Character/content-set request,
  load `${STS2_API_SKILL_DIR}/design/character-foundation.md` before creative questions.
  Recommend an exact native-shaped starter deck before asking for deck details, and label
  pinned facts, observed conventions, and creative decisions distinctly.
- **Plan only when routed.** Load only the mechanic, content-set, and balance references
  named by `route.md`. An exact narrow Card keeps the fast path and does not receive a
  general design review merely because it has numbers.
- **Review coherence only when routed.** Load `design/coherence-review.md` for multiple
  intentional expressive surfaces, explicit theme/narrative/presentation work, or an
  identity-changing revision. Derive anchors from settled decisions, not new lore. Name
  any exact cross-artifact conflict and ask only when the repair is a creative choice.

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
human play result stays an open hypothesis (`INV-4`).

This pass produces a compact planning capsule, not a durable artifact. The following
`design.md` stage records the capsule, current/future scope, and traceability without
re-asking its settled decisions.

## Compact coherence pass

Run this pass only when `route.md` selected coherence review. Use one to three observable
identity anchors from accepted decisions, then inspect only selected mechanics, naming,
localization, visuals, Event text, and Character identity. State how each applicable
surface communicates an anchor; do not force the same word, palette, or imagery everywhere.

If two surfaces contradict behavior, drift one gameplay term, break the accepted identity,
leak deferred/unsupported scope, or present flavor/build evidence as gameplay proof, name
both sides and the player-facing consequence. Offer the smallest resolution and pause
before DESIGN/SPEC until the user decides. Preserve an accepted contrast as deliberate
tension rather than repeatedly "fixing" it.

For revision, inspect only existing artifacts that can depend on the changed `D-###` item.
Prepare an ordered impact/re-evaluation queue with UPDATE, REVIEW, REVERIFY, and high-risk
PRESERVE entries. This is not permission to edit every downstream file or rerun a full
acceptance; `design.md` records the queue and reopens only invalidated stages.

## What to resolve (only if unclear from the sentence)

1. **Element type.** Relic / card / potion / enemy / event / character? Infer if possible:
   - Owns a passive/triggered effect the player *has* → **relic**.
   - Something the player *plays from hand for an energy cost* → **card**.
   - A **one-shot consumable the player drinks/uses** → **potion**.
   - **A monster/enemy the player fights** → **enemy encounter** (a monster + the encounter
     that spawns it — always one unit; you never build a lone monster).
   - **A story/choice room on the map** where the player picks an option and gets a
     consequence → **event / World Node**.
   - **A new selectable hero** with their own starting deck/relic and card identity →
     **character**. Supported composition includes a named nonnegative combat resource with
     an explicit payoff/live counter and a bounded ordered semantic record of card plays
     with deterministic output. Source cards use their normal result piles. Character
     presentation can additionally select the supported selection portrait/background,
     top-panel icon, static combat/rest/merchant bodies, five-layer full energy, and compact
     resource icon. Locked selection and map marker remain grounded gaps with explicit
     fallbacks.
   - **A named place where Cards are stored, moved, inspected, or shown separately** is a
     **custom card pile**. The Custom Card Piles Package supports combat/run lifetime,
     headless/top-bar/bottom-left/bottom-right/ExtraHand presentation, public pile screens,
     and explicit Card movement.
   - **Current authoring recipes: relic, potion, card, custom card piles, enemy encounter,
     event, bounded character composition, and promoted existing-model overrides.** If the
     request edits an existing vanilla model, resolve it through
     `reference/vanilla-overrides.md`. A requested visual surface in the 44-provider matrix
     continues through `reference/vanilla-visual-overrides.md`. Non-asset operations for an
     exact `CARD.*` target continue through `reference/vanilla-card-overrides.md`. Initial
     options and subsequent pages for an exact existing Ancient continue through
     `reference/vanilla-ancient-overrides.md`. Pinned epoch gates and Card/Relic/Potion
     pool add/remove/move requests continue through
     `reference/vanilla-availability-overrides.md`. Existing Relic/Potion/Power/Orb/
     Enchantment/Affliction/Monster/Encounter/ordinary Event data and behavior continue
     through `reference/vanilla-non-card-overrides.md`; other operations report the
     unpromoted package and stop. Offer a closest **new** element only as a separate user
     choice, never as an automatic substitution.
   - **Fail closed on vanilla Card base-description replacement.** If the user asks to
     replace, remove, or hide the original description body, explain that RitsuLib `0.5.11`
     exposes only before/after description fragments and pause before writing SPEC or
     scaffolding. Never reinterpret the request as appended text. Continue only after the
     user explicitly accepts a before/after composition; confirmed numbers or a request not
     to repeat questions does not authorize that downgrade.
2. **Trigger / usage / how it's played:**
   - **Custom Card Piles Package**: infer every stated pile and ask only for player-visible
     ambiguity: does it reset each fight or persist for the run; is it hidden, a top-bar/
     bottom-corner button, or visible as extra Cards; what exact action moves Cards in and
     out; and may visible Cards be played normally? When placement, pile-screen tools,
     sorting, hotkeys, hover behavior, or visual callbacks are requested, record the
     requested behavior in game terms. Do not ask for enum names, delegates, or framework
     APIs; ask for exact coordinates only when the user requested an exact custom layout.
   - **Existing vanilla Ancient**: resolve the exact Ancient first, then determine whether
     the Mod appends choices or replaces the complete initial choice list. For every choice,
     capture when it is visible, when it is locked, its one fixed Gold/HP/Max HP/no cost,
     any Card/Relic/Potion/Power shown on hover, ordered consequences, and whether it stays,
     opens a named page, or finishes the Ancient. Capture every reachable page the same way.
     Ask about lethal HP/Max HP payment only when the wording leaves it unclear. Preserve
     the Ancient's original model, room, opening dialogue, save identity, and native finish
     history without asking; replacing those is a separate unsupported request.
   - **Existing vanilla non-Card data/behavior**: resolve the exact target and capture only
     player-facing intent. For data, capture the desired final enum/boolean/integer or
     integer delta. For an owner hook, capture the real trigger, owner/side scope, condition,
     ordered fixed result, and whether it composes before/after the original owner or
     completely replaces that owner's hook stream. For complete Relic/Potion/Power/Orb/
     Enchantment/Affliction behavior, Monster moves, Encounter roster, or ordinary Event
     options, confirm that all behavior on that named surface is being replaced and freeze
     the whole lifecycle/state/roster/page graph. Do not ask for hook names, getter names,
     patch methods, or fingerprints.
   - **Relic**: when does the effect happen? Map the user's words to a lifecycle
     moment — "start of combat", "start of each turn", "when you play a card",
     "start of each floor". If they said it, don't re-ask. If it remembers progress
     ("every 3 turns", "the third Attack", "once per combat"), resolve whether that
     progress resets each **turn**, each **fight**, or continues across fights in the
     current run. Ask only when the wording is genuinely ambiguous: "Should progress
     continue into the next fight, or restart each fight?" Offer continue-across-fights
     as the default for "every N turns" (Happy Flower semantics); "on turn N" defaults
     to restarting each fight (Stone Calendar semantics).
   - **Potion**: potions fire when *used*, so there's no trigger to pick — instead
     resolve **when it can be used** (in combat only? any time?) and **what it
     targets** (yourself, one enemy, all enemies) only if the effect makes that
     ambiguous. If it asks for a filtered creature such as "an attacking enemy" or
     "an enemy with Block", record an advanced target. A filtered single target is
     supported; a filtered many-target Potion is a pinned-profile gap, so offer a
     filtered single-target Potion or a filtered many-target Card instead.
   - **Card**: cards fire when *played*, so resolve **energy cost** (default 1),
     **type** (deals damage → Attack; block/utility → Skill; a permanent buff →
     Power), and **what it targets** (one enemy / all enemies / yourself) only if the
     effect makes that ambiguous. If the effect needs a buff/debuff no vanilla power
     covers, note it — `author.md` will add a custom power as a dependency. If the user
     names a reusable rule that several cards should share, record a **custom keyword**
     plus its plain-language behavior. If they want a persistent modification attached to
     a particular Card (often granted by an event/relic), record a **card enchantment** and
     what it changes. If a Card/relic/power channels a persistent orb, record the orb's
     **passive** and **evoke** effects separately. Do not call either a run modifier, and
     never ask about enum fields or APIs.
     A Card may instead select one or affect many live creatures matching a deterministic
     filter. Ask only for the missing game rule: who can be affected, whether it chooses
     one or affects all matches, and whether the answer depends on the acting player or
     this source Card. Never ask for a predicate, enum, or registration API.
     If the user asks for colored words in a Card, relic, potion, or Power description,
     infer bounded vanilla rich text and capture only the exact phrase plus plain-language
     color intent. Never ask for or preserve raw BBCode. Use the per-surface allowlist;
     SmartFormat owns Card upgrade highlighting, and titles remain plain.
     If a displayed Card number is calculated from live state, capture one named formula,
     every input it reads, an integer minimum/maximum, its base and upgraded behavior, and
     whether it is plain, damage, Block, Energy icons, Star icons, a raw typed buff/debuff
     amount, or an amount the Card applies. Ask one plain timing question only when playing
     the Card changes an input: "Should this count the state before this card spends its
     energy and leaves your hand, or just after?" Record any variable tooltip's title,
     description, and whether it has a custom icon. Do not ask about preview classes,
     formatters, delegates, or hooks.
    If the user wants a Card highlighted in hand under one or more conditions, capture each
    actionable meaning, plain-language condition, gold/red/custom color, priority relative
    to the other active rules, and whether it remains visible while unplayable. Preserve
    the rules in precedence order. Infer gold for a bonus and red for a warning when the
    meaning is clear. Never ask about registries, predicates, polling, or framework color
    objects.
     If a Relic owns player-readable numbers distinct from its native main amount, capture
    up to three extra badges: meaning, bounded value rule, one distinct
    top-left/top-right/bottom-left corner, plain/bounded-color intent, refresh state change,
    and removal condition. Relic labels have at most 4 visible characters. If a custom
    Power owns a second player-readable number, capture exactly the same semantics for at
    most one top-left badge with at most 6 visible characters. This is supplemental UI, not
    a replacement for the main counter. Never collect raw BBCode, arbitrary strings,
    custom rectangles, or a bottom-right label.
   - **Enemy encounter**: resolve Monsters and Encounters as separate content nodes joined
     by explicit roster edges. A Monster may be reused, and an Encounter may contain
     multiple or repeated Monster models. Capture each Monster's positive HP value/range,
     visible warning/effect per move, and deterministic, conditional, or explicitly
     requested fixed-weight random successor. Default to the stated repeating order; never
     invent randomness. Ask one sequence/roster question only when it changes the fight.
     Don't ask about scenes, intent class names, RNG objects, or APIs — those are the recipe's job.
     If the user asks for auxiliary information on one monster intent, recognize the
     supported Extra Badges Package but report that Intent authoring is not implemented in
     the current pack. Do not rewrite a separate debuff as an attack badge, and keep an
     ordinary repeated identical attack as the native multi-attack intent.
   - **Event / World Node**: resolve the event's opening situation, the option(s) the
     player can choose, and each option's concrete consequence (gold/HP/card/relic/etc.).
     Record whether each option finishes, opens another choice page, blocks on a card/
     reward selection, or enters special combat. For combat, resolve whether victory
     returns to a named Event page or proceeds directly to the map, plus any extra reward.
     Also capture the special encounter's monster/group, HP, visible moves, and order or
     branch condition using the enemy-encounter defaults above; "special combat" is not a
     complete encounter spec by itself.
     One mutable Event instance supports at most one special combat. A one-option event is
     valid for the fast path. Ask which acts only if the user cares; default is all acts.
     If the request says an earlier choice/Card should guarantee later special Events,
     capture a bounded mapping: custom Quest token, nonempty act set, globally ordered
     priority, finite unique custom-Event sequence, fail-closed conflict, and exact terminal
     consumption option. Offer the supported one-step default. Do not invent a loop,
     vanilla target, fixed map node, multiplayer behavior, or observed save claim.
     If the user explicitly asks for Event VFX, offer either the bounded generated
     `portrait_halo` or the curated built-in `trial_noble` profile and capture which normal
     pages use it; default is no VFX. Do not ask about localization key builders, room nodes, anchors, or
     registration. If the user asks for words
      that shake, wave, change color, or look emphatic, infer bounded vanilla Event rich text
      and capture only the exact phrase plus plain-language effect; never ask for BBCode.
      If an enabled option should preview known generated content, capture the exact Card
      (and upgrade state), relic, potion, or Power (and amount) for its typed Hover Tips.
      Locked-option tips do not render natively, so preserve that request as a presentation
      gap. A normal relic-backed option may show its native title/description and metadata,
      but its image is Ancient-only and remains a gap. For any HP or Max HP cost, capture the
      exact cost so the author can attach the native inclusive lethal warning to the same
      value used by the consequence. When an option actually grants a known Card or relic,
      infer its matching native acquisition presentation; this is separate from the typed
      pre-choice Hover Tip. If the user asks for an impact/jolt on a successful option,
       offer `weak_short` or the heavier `strong_normal` profile and explain the visible
       intensity difference. Do not collect arbitrary strengths, durations, scene paths,
       or player preference values. Speech/thought bubbles are
      future outlook only.
   - **Character**: resolve the character's identity/theme, starting HP, starter relic, and
     one starter card/relic mechanic that a grounded public game/framework API can prove in
     combat. Use the loaded Character Foundation grammar to recommend the exact Card names,
     counts, base effects, upgrades, and total before asking the user for deck details. If
     the core mechanic is materially unclear, ask about that one decision first, then make
     the complete deck proposal; never ask the user to name ten Cards from a blank form.
     Starting HP, Gold, MaxEnergy, base Orb slots, typed pools, and starter Card/Relic/Potion
     multisets are explicit current decisions. Use the native inventory as recommendations,
     not forced defaults, and preserve an explicit
     implementable departure after explaining its onboarding, Strike/Defend-tag
     compatibility, and early-balance consequences. If it names secondary resources,
     capture every stable id, min/default/max, combat/run persistence, turn-start policy,
     gain sources, Card payment uses, shortfall/replacement policy, post-commit payoff, and
     selected counter/Card UI consumers. If it describes an ordered card-play record,
     capture semantic values, normal source destination, order, capacity/overflow, compile
     trigger, deterministic formula, and output. If physical played Cards must remain in a
     custom zone, preserve that as an explicit unsupported gap.
     If it requests dialogue with a vanilla Ancient, resolve each natural-language target
     through the pinned `0.107.1` catalog and capture ordered groups. Each group records
     `first`, `visit N`, or `repeat from visit N`; every line records Character/Ancient
     speaker and text, and every non-terminal line records its transition prompt. Architect
     groups also record start/end attackers as None, Player, Architect, or Both. Explain
     that the native global first-visit introduction wins on a never-visited profile.
     Ask only for missing semantics and offer the verified defaults below. Any other
     Harmony/Publicizer seam stays an explicit pack gap; do not silently flatten it.
3. **Effect**: what exactly happens, in game terms (energy, damage, block, draw,
   heal, a power/status). Get numbers if they matter ("double", "gain 2", "20 damage").
   For a card, also ask what **upgrading** it should improve if not obvious (default:
   bump the main number). When any effect counts events, also record the exact event and
   threshold; do not collapse "every N" into "on the Nth" or omit whether the triggering
   event counts before the check.
4. **Art — ONE question for the whole mod (only if the user signalled they care about
   the look).** Default is placeholder — skip this entirely unless their sentence
   implies a custom visual. This is a **single mod-level decision**: placeholder or
   generate for the mod, asked **once** no matter how many cards/sprites it has. Do NOT
   ask per sprite. If they want custom art:
    - **Eight established static specs plus nine Character static specs and one bounded
      four-action cue bundle** can be generated. The
     established set is card portraits, relic/power/potion/enchantment/orb icons, static
     monster bodies, and normal-event portrait slots. The Character set is selection
     portrait/background, top-panel icon, static non-Spine combat/rest/merchant bodies,
      five-layer full energy, a large pool Energy icon, and a small text Energy icon. The
      optional combat bundle is four acquired action sheets that normalize to eighteen
      runtime frames: Idle 4, Attack 4, Hit 4, and Dead 6. Full energy is five image assets
      but only layer 1 is acquired; show the one Energy call and four cue calls before a
      paid route. Derive one concise neutral combat-anchor pose from the Character
      description and reviewed selection portrait; do not ask another user question for
      it. The same identity, costume, camera, apparent scale, pivot, and baseline remain
      locked across all four sheets, and adjacent cells use small in-between pose changes
      because the sequences play quickly. The established
     static specs and all nine Character output specs are live-verified. M6.7.2 may reuse a
     matching static spec for a vanilla texture override, but its Material, PackedScene,
     Spine-resource, and background-directory routes require an existing local authored
     resource rather than an image call. Orb support is
     icon-only, and Event raster support does not include custom phobia or custom-layout
     assets. Generate the initial event
     portrait plus only later-page portraits the user's concept explicitly calls for; do
     not turn every result page into another image spend.
   - Prefer a **host-native image generator** when the current runtime actually exposes
     one. In Codex this is the built-in `image_gen` tool governed by the installed
     `imagegen` skill and it needs no separate `OPENAI_API_KEY`. Do not infer availability
     from the text-model name or from the presence of a skill file; the image tool itself
     must be callable. Record this route as `runtime-imagegen`.
   - Otherwise offer one available source in plain language: an already-installed and
     authenticated **Vofy CLI** (managed credits), their own OpenAI-compatible endpoint
     (`art-backend.json`), or an existing local image. Check Vofy only with
     `acquire_sprite.py preflight`; never install it, run `vofy login`, or expose account
     output. If no custom route is ready, record `art: placeholder` and move on.
   - Capture the intended **subject/style** in plain words (e.g. "a burning arrow, comic
     style") once, for the mod. If the mod has several generated assets, take one overall
     style note here; `author.md` fills each asset's subject from its element SPEC when it
     generates — but you still only *ask* once.
    - **Static monster bodies and the bounded Character combat cues are supported.**
      Monsters use one static combat/bestiary body or the built-in scene fallback. Character
      generation supports selection/background, top-panel icon, static combat/rest/merchant
      bodies, five-layer full energy, distinct large/text Energy icons, and the fixed
      non-Spine Idle/Attack/Hit/Dead cue bundle. Preserve locked/map requests as explicit
      gaps with inherited fallbacks. Preserve requests for Spine, Cast, trails, audio,
      animated merchant/rest bodies, phobia variants, or
     bestiary move previews as later-animation gaps. For an event, offer the normal initial portrait
     and any explicitly requested later-page image change. The separate code-native
     `portrait_halo` and the built-in `trial_noble` profile need no image backend. Preserve
     requests for new-content custom phobia art or behavior-bearing arbitrary VFX/layouts
     as gaps. An exact existing Event/Ancient visual consumer may use only the promoted
     resource route in `vanilla-visual-overrides.md`.

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
- **Owned Rest Site option** (only when requested on a Card or Relic): singleplayer only; distinguish
  when it is absent from when it is visible but gray; default to once per Rest Site,
  normal leave behavior, checked native Heal-icon fallback, and free cost unless the idea
  names a fixed Gold price. Ask only for an unresolved repeatability or stay/leave choice.
  A Card owner requires exactly one matching deck instance. Modifier owners, arbitrary
  costs, post-payment choices, and same-site repeat remain unsupported.
- **Name**: derive a short, flavorful name from the concept; confirm in the SPEC summary.
- **Acts** (event): all acts unless the user specifies a setting.
- **Event VFX**: none unless explicitly requested; then use only `portrait_halo` or
  `trial_noble` on named normal-layout pages.
- **Event acquisition presentation**: native whenever a successful option adds a known
  Card to the Deck or obtains a known relic; never a second grant.
- **Event screen shake**: none unless explicitly requested; then one `weak_short` or
  `strong_normal` call on the named successful option, inheriting the player's preference.
- **Event text effects**: none unless explicitly requested or clearly described; then use
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
- **Art**: **placeholder** (the template/game fallback). This is the default — do NOT
  proactively ask about art. Only switch to `generate` if the user's sentence asks for a
  custom look (e.g. "a card showing a red phoenix", "make it look like…"). Eight static
  specs — card / relic / power / potion / enchantment / orb icon / monster body /
  normal-event portrait slots — can be generated (see step 4). It is a
  **single mod-level choice**, asked at most once regardless of sprite count. Custom
  generation prefers a callable host-native image tool, then can use an already-
  authenticated Vofy CLI or a BYO HTTP backend; an existing local image uses the same
  deterministic import path. If no selected route is available, keep the placeholder.
- **Author**: reuse the project's configured author, else "OpenMod".

## Output

A compact intake you carry into `spec.md`. Prefix every intake with:

```text
route: fast | co-design | revision
intent: <one player-facing sentence>
settled decisions: <choices preserved from the request and project artifacts>
defaults: <inferred values to state in the confirmation>
native grammar: none | <loaded native grammar and pinned profile>
planning references: none | <loaded mechanic/content-set/balance references>
coherence reference: none | design/coherence-review.md
revision delta: none | <keep/change/check/re-verify summary>
gaps: none | <unsupported intent awaiting explicit acceptance>
scope signals: <requested now; explicitly later; accepted placeholder; explicitly excluded>
deliverable signals: <expected finished thing in the user's words; the player experiences
  they would check first; what their wording implies that this will not contain>
identity anchors: none | <one to three accepted observable promises>
coherence surfaces: none | <selected surface -> anchor expression or deliberate tension>
coherence conflicts: none | <exact conflicting artifacts/decisions awaiting resolution>
impact queue: none | <ordered revision-only UPDATE/REVIEW/REVERIFY/PRESERVE targets>
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

For a **relic**:

```
element: relic
name: <proposed>
rarity: Common
trigger: start of combat (turn 1)
effect: <plain-language, with numbers>
state: none | event=<what advances>; threshold=<N>; lifetime=turn|combat|run;
  reset=<exact boundary>; persistence=field|AttachedState|SavedAttachedState
owned Rest Site option: none | title=<title>; description=<description>;
  owner=relic; owner multiplicity=exactly one;
  eligibility=<absence rule>; repeatability=once per Rest Site|once per run;
  enabled=<rule>; cost=free|<N> Gold; outcome=<deterministic exact operations>;
  after success=leave|keep remaining options; icon=fallback|generate;
  multiplayer=singleplayer only
art: placeholder | generate: <subject/style, if requested>
art source: runtime-imagegen | vofy | byo-http | local-image  (generate only; no credentials/credits)
```

For a **potion** (usage/target instead of trigger):

```
element: potion
name: <proposed>
rarity: Common
usage: CombatOnly | AnyTime
target: self | one enemy | all enemies
effect: <plain-language, with numbers>
art: placeholder | generate: <subject/style, if requested>
art source: runtime-imagegen | vofy | byo-http | local-image  (generate only; no credentials/credits)
```

For a **card** (cost/type/target + upgrade instead of trigger):

```
element: card
name: <proposed>
rarity: Common
energy cost: fixed 1 | X
Star cost: none | fixed <N> | X
cost upgrade: same | Energy <delta> | Stars <delta>
type: Attack | Skill | Power
target: one enemy | all enemies | self
effect: <plain-language, with numbers>
upgrade: <what improves, e.g. "damage 6 -> 9">
calculated values: none | <name; role; one formula; inputs; integer min/max; base/upgrade;
  before-play or after-payment-and-move evaluation>
variable tooltips: none | <value name -> title; description; optional custom icon>
owned Rest Site option: none | title=<title>; description=<description>;
  owner=card; owner multiplicity=exactly one in the owner's deck;
  state handle=host visit removal|saved owner bool;
  eligibility=<absence rule>; repeatability=once per Rest Site|once per run;
  enabled=<rule>; cost=free|<N> Gold; outcome=<deterministic preflightable operations>;
  after success=leave|keep remaining options; icon=fallback|generate;
  multiplayer=singleplayer only
art: placeholder | generate: <subject/style, if the user asked for custom art>
art source: runtime-imagegen | vofy | byo-http | local-image  (generate only; no credentials/credits)
```

When either Card or Potion uses a filtered live-creature target, append this semantic
summary. Translate the user's words; do not expose these labels as programming questions:

```text
advanced target:
  consumer: card | potion
  mode: one | many
  target id: <stable Mod-local stem>
  candidate conditions: <alive side/intent/Block/current-or-maximum-HP rules>
  acting-player conditions: none | <plain-language player-relative rules>
  source conditions: none | <single-target source Card/Potion rule>
  zero-target behavior: reject or cancel without payment/consumption
```

If this produces `consumer: potion` plus `mode: many`, stop and offer the two supported
alternatives above. Do not silently weaken the zero-target behavior.

For an **enemy encounter graph**:

```
element: enemy encounter graph
monsters:
  - id/name: <stable id / proposed name>; hp: <positive min..max>
    moves: <visible intent/effect states>
    branches: deterministic | conditional <guards> | random <positive fixed weights>
encounters:
  - id/name: <stable id / proposed name>; roster: [<Monster ids, repetitions allowed>]
    all possible: [<registered Monster ids>]; placement: <grounded act/global route>
art: placeholder | generate: <one full creature in a neutral combat-ready pose>
art source: runtime-imagegen | vofy | byo-http | local-image  (generate only)
art boundary: one static 360x360 body shared by combat+bestiary; no animation/phobia variant
```

For an **event / World Node**:

```
element: event
name: <proposed>
opening: <short situation/initial page>
options:
  - <option title> -> <precise consequence with numbers>; next: finish | page <KEY> |
    special combat <encounter>, then resume page <KEY> | special combat, then map
acts: all | <specified acts>
art: placeholder | generate: <opening scene; focal subject left, dark UI space right>
page portraits: none | <PAGE_KEY>: <replacement scene>  (only when explicitly requested)
art source: runtime-imagegen | vofy | byo-http | local-image  (generate only)
event VFX: none | portrait_halo on <page keys>; <color/mood> |
  trial_noble on <page keys>
acquisition presentation: none | ordered [native Card <name> to Deck | native relic <name>]
screen shake: none | weak_short | strong_normal on option <name>
event text effects: none | vanilla; <PAGE/OPTION_KEY>: "<exact phrase>" -> <emphasis/color/jitter/sine>
forced follow-up mappings: none | [id=<id>; token=<name>; acts=[...]; priority=<int>;
  sequence=[<unique custom Events>]; consumption=target success|sequence complete;
  completion option=<name>; conflict=fail closed; save claim=game-unobserved]
art boundary: normal initial plus explicit page portraits; no custom phobia/custom-layout assets;
  VFX boundary: code-native portrait_halo or curated built-in trial_noble, no arbitrary VFX;
  text boundary: descriptions only, bounded vanilla tags, plain titles
```

For an **existing vanilla Ancient override**:

```
element: existing vanilla Ancient override
target: <user wording> -> <exact resolved Ancient and current display title>
initial choices: append | replace all
rule: always | <plain condition>; priority <int, append only>;
  duplicate text: skip | keep (append only)
options:
  - id: <stable local id>; text: <title and description>; visible when <condition>;
    enabled when <condition>; cost <none|N Gold|N HP|N Max HP, lethal yes/no>;
    hover <none|known Card/Relic/Potion/Power>; relic image <none|known relic>;
    effects <ordered damage/heal/Gold/Max HP/model grant/deck selection/custom reward/shake>;
    next <stay|page PAGE_ID|finish>
pages:
  - id: <PAGE_ID>; description: <text>; options: <same option shape>
visual composition: none | <exact Ancient/Event visual surfaces>
preserve: original Ancient model, room, opening dialogue, save identity, allowance gate,
  and native finish/choice-history lifecycle
boundary: singleplayer; no new Ancient, global dialogue replacement, line audio,
  randomized outcome rewrite, special combat, or direct merchant/rest/treasure transition
```

Default to `append`, `always`, priority `0`, skipping duplicate text, nonlethal payment,
no hover/relic image/shake, and `finish` only when those choices are not stated and the
default cannot alter the user's concept. A replacement must describe the complete initial
choice list and at least one reachable finish path; never silently preserve unspecified
vanilla choices inside a replacement.

For a **character**:

```
element: character
name: <display name>
starting HP: <positive int; native-shaped starting point 70>
starting Gold: <nonnegative int; native-shaped starting point 99>
MaxEnergy: <positive int; native-shaped starting point 3>
base Orb slots: <nonnegative int; native-shaped starting point 0>
native grammar: design/character-foundation.md @ STS2 0.107.1
pinned facts used: <exact native identities/values used in the proposal>
observed convention: <native shape used as the recommendation>
starter deck: <exact creative Card names, counts, base effects, upgrades, and total>
starter deck rationale: <how the teaching Cards and Starter relic introduce the mechanic>
deliberate departure: none | <departure; onboarding; compatibility; balance consequences>
starter relics: [<name x count + grounded public effect>]
starter Potions: [<name x count>] | none
pools: character-scoped card/relic/potion pools with at least one concrete member each;
  if Shop/merchant is selected, at least 2 non-Basic Attacks, 2 Skills, and 1 Power
scenario: RunStart + CombatPlayer
art: placeholder | generate: selected Character static profiles and optional combat cues
art profiles: selection | background | top-panel icon | combat body | rest body |
merchant body | five-layer full energy | large energy icon | text energy icon |
explicit gap: locked selection/map marker
art bundle: one structured row per selected slot with required/optional, output path,
dimensions, alpha policy, fallback, and real consumer
identity route: selection portrait bootstrap; identity+style for combat/rest/merchant;
  combat cue sheets; palette/motif brief + style only for background/icon/Energy
theme contract: four named UI colors | card-frame target RGB/brightness |
  one shared motif/palette rendered separately at 256x256 and 24x24
static merchant patch: selected only with merchant body; inherited fallback on mismatch
combat cues: none | fixed Idle4@180ms loop, Attack4@90ms one-shot, Hit4@80ms one-shot,
  Dead6@140ms terminal; four acquired sheets; all-or-nothing static combat fallback
combat continuity: one derived neutral anchor repeated verbatim across all four prompts;
  identity/costume/camera/scale/pivot/baseline locked; adjacent cells are small,
  substantially overlapping in-between poses; Attack/Hit recover toward Idle
Ancient dialogue: none | target <natural name>; groups <first|visit N|repeat from visit N>;
  ordered speaker/text/non-terminal transition prompt; Architect start/end attackers
Ancient boundary: preserve native model/scene/background/options/rewards/progression;
  deferred custom Ancient/layout/audio/multiplayer
advanced mechanic: none | <unverified idea that remains beyond Foundation>
```

When the idea selects a supported advanced capability, replace `advanced mechanic` with one or
both compact semantic blocks:

```text
resource: <name>; gain <sources/amounts>; spend <cost/payoff>; floor 0; reset combat; UI <counter text>
buffer: <name>; values <semantic values>; source destination Discard; order <rule>; capacity <N>; overflow reject; compile <trigger/formula/output>
```

Do not write files here — `design.md` writes the durable claim, intent, and scope, and
`spec.md` lowers the current slice. If fast routing found nothing material to ask, skip straight to `design.md`
with the inferred intake. If this is a revision, preserve every unrelated design decision,
stable ID, and existing SPEC operation outside the confirmed delta.
