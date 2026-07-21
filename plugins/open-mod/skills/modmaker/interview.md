# Interview — one short intake round

Goal: turn the user's one sentence into enough certainty to write `SPEC.md`,
**asking as little as possible**. The user is a non-programmer; keep it plain.

## Rules

- **One round only.** Ask only what's genuinely ambiguous. Everything else gets a
  sensible default (state the default, don't ask).
- **No jargon.** Say "when does it happen?" not "which combat hook?". Never ask
  about classes, namespaces, or APIs.
- **Batch the questions.** Ask all needed clarifications together, not one by one.

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
     with deterministic output. Source cards use their normal result piles.
   - **Supported now: relic, potion, card, enemy encounter, event, and bounded character composition.**
     (*Editing* an existing
     vanilla card/relic/potion is not yet supported — if that's the ask, say so and offer to
     build the closest **new** element instead.)
   - If the request says played cards should physically remain in a special area, ask one
     short question: should the cards instead resolve normally while a visible text record
     tracks their order? Offer that as the supported default. Retained-card zone UI is a
     pack gap, not something AUTHOR should improvise.
2. **Trigger / usage / how it's played:**
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
     ambiguous.
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
     If the user asks for colored words in a Card, relic, potion, or Power description,
     infer bounded vanilla rich text and capture only the exact phrase plus plain-language
     color intent. Never ask for or preserve raw BBCode. Use the per-surface allowlist;
     SmartFormat owns Card upgrade highlighting, and titles remain plain.
   - **Enemy encounter**: an enemy is fought inside its encounter, so treat them as one
     unit. Resolve only what genuinely shapes the fight: the monster's **HP**, whether it
     is alone or in a group, and each move's visible warning, exact effect, and what comes
     next. If there are several moves, record the fixed order or the plain-language
     condition (for example, "below half health, heal instead"). Ask one sequence question
     only when the order/condition is genuinely unclear; default to the stated order in a
     repeating cycle. Don't ask about scenes, animations, intent class names, or APIs —
     those are the recipe's job.
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
     If the request says an earlier choice/card should guarantee a later special Event,
     capture one custom Quest Card token, one custom target Event, the exact target act,
     and the target option that completes the token. Offer the supported default: carrying
     the token forces the next entered Unknown MapPoint in that act. Do not broaden this
     into an arbitrary chain or promise multiplayer/save behavior.
     If the user explicitly asks for Event VFX, offer either the bounded generated
     `portrait_halo` or the curated built-in `trial_noble` profile and capture which normal
     pages use it; default is no VFX. Do not ask about `EventLoc`, room nodes, anchors, or
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
      offer the single `weak_short` screen-shake profile. Do not ask for strengths,
      durations, scene paths, or player preference values. Speech/thought bubbles are
      future outlook only.
   - **Character**: resolve the character's identity/theme, starting HP,
     exact starter deck counts, starter relic, and one starter card/relic mechanic that
     public/BaseLib APIs can prove in combat. Default to standard 3 energy and placeholder
     visuals. If it names a custom resource, capture its gain sources, spenders/payoff,
     floor, combat reset, and counter text. If it names a custom zone, capture accepted
     cards, order, capacity/overflow, compile trigger, deterministic formula, and output.
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
   - **Eight static specs — card portraits, relic icons, power icons, potion icons,
     enchantment icons, orb icons, static monster bodies, and normal-event portrait slots** can be generated
     (all live-verified as loose PNGs; orb support is icon-only, and Event raster support
     does not include custom phobia or custom-layout assets). Generate the initial event
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
   - **Static monster bodies are supported; monster animation and character visuals are not.**
     Monsters use one static combat/bestiary body or the built-in scene fallback. Preserve
     requests for Spine bodies, attack/hurt/cast/death animation, phobia variants, or
     bestiary move previews as later-animation gaps. Characters use the template/built-in
     placeholder shell; state that limitation if custom character visuals are requested and
     continue only if the user accepts it. For an event, offer the normal initial portrait
     and any explicitly requested later-page image change. The separate code-native
     `portrait_halo` and the built-in `trial_noble` profile need no image backend. Preserve
     requests for custom phobia art, arbitrary VFX, custom-layout, or Ancient art as gaps.

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
- **Name**: derive a short, flavorful name from the concept; confirm in the SPEC summary.
- **Acts** (event): all acts unless the user specifies a setting.
- **Event VFX**: none unless explicitly requested; then use only `portrait_halo` or
  `trial_noble` on named normal-layout pages.
- **Event acquisition presentation**: native whenever a successful option adds a known
  Card to the Deck or obtains a known relic; never a second grant.
- **Event screen shake**: none unless explicitly requested; then one `weak_short` call on
  the named successful option, inheriting the player's preference.
- **Event text effects**: none unless explicitly requested or clearly described; then use
  only the bounded vanilla rich-text vocabulary on named page/option description phrases.
- **Forced Event follow-up**: none unless explicitly described; then one custom Quest Card
  forces one custom target Event from an Unknown MapPoint in one specified act, and one
  named target option consumes the token.
- **Character Foundation**: 70 HP, standard 3 energy, a 10-card Basic starter deck,
  one Starter relic, valid character-scoped card/relic/potion pools, and template/built-in
  placeholder visuals. Derive starter effects from the user's stated theme.
- **Character resource** (only when requested): combat lifetime, starts at 0, nonnegative
  integer, all-or-nothing spend, generic text counter, and no alternative-energy payment.
- **Custom card zone** (only when requested): combat lifetime, hidden/no-art, finite
  capacity, reject overflow without mutation, preserve insertion order, and create one
  deterministic real output card.
- **Monster move order**: moves repeat in the order stated. Do not invent random choice;
  add a conditional branch only when the concept names a condition or the user confirms it.
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

A compact intake you carry into `spec.md`. For a **relic**:

```
element: relic
name: <proposed>
rarity: Common
trigger: start of combat (turn 1)
effect: <plain-language, with numbers>
state: none | event=<what advances>; threshold=<N>; lifetime=turn|combat|run;
  reset=<exact boundary>; persistence=field|SavedProperty
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
cost: 1
type: Attack | Skill | Power
target: one enemy | all enemies | self
effect: <plain-language, with numbers>
upgrade: <what improves, e.g. "damage 6 -> 9">
art: placeholder | generate: <subject/style, if the user asked for custom art>
art source: runtime-imagegen | vofy | byo-http | local-image  (generate only; no credentials/credits)
```

For an **enemy encounter** (monster + the encounter that spawns it, one unit):

```
element: enemy encounter
monster name: <proposed>
encounter name: <proposed, or "<Monster> Encounter">
hp: <int>
moves:
  - id: <plain name>; warning: <attack|buff|debuff|defend|heal or combination>;
    effect: <exact effects and numbers>; next: <next move id>
condition: none | <plain condition> -> <move id>; otherwise -> <move id>
loop: <move id> -> <move id> -> ...
group: single | <describe the group>
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
acquisition presentation: none | native Card <name> to Deck | native relic <name>
screen shake: none | weak_short on option <name>
event text effects: none | vanilla; <PAGE/OPTION_KEY>: "<exact phrase>" -> <emphasis/color/jitter/sine>
forced follow-up: none | quest token <name>; target Event <name>; target act <exact act>;
  completion option <name>; trigger next entered Unknown MapPoint in that act
art boundary: normal initial plus explicit page portraits; no custom phobia/custom-layout assets;
  VFX boundary: code-native portrait_halo or curated built-in trial_noble, no arbitrary VFX;
  text boundary: descriptions only, bounded vanilla tags, plain titles
```

For a **character**:

```
element: character
name: <display name>
starting HP: <int, default 70>
energy per turn: 3 (current grounded Foundation value)
starter deck: <exact card names and counts, total 10>
starter relic: <name + one public/BaseLib effect>
pools: character-scoped card/relic/potion pools with at least one concrete member each
scenario: RunStart + CombatPlayer
art: character-template/built-in placeholders
advanced mechanic: none | <unverified idea that remains beyond Foundation>
```

When the idea selects a verified 6d capability, replace `advanced mechanic` with one or
both compact semantic blocks:

```text
resource: <name>; gain <sources/amounts>; spend <cost/payoff>; floor 0; reset combat; UI <counter text>
zone: <name>; accepts <cards>; order <rule>; capacity <N>; overflow reject; compile <trigger/formula/output>
```

Do not write files here — `spec.md` does that. If nothing was ambiguous, skip
straight to `spec.md` with the inferred intake.
