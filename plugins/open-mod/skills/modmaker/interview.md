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

1. **Element type.** Relic / card / potion / enemy / event? Infer if possible:
   - Owns a passive/triggered effect the player *has* → **relic**.
   - Something the player *plays from hand for an energy cost* → **card**.
   - A **one-shot consumable the player drinks/uses** → **potion**.
   - **A monster/enemy the player fights** → **enemy encounter** (a monster + the encounter
     that spawns it — always one unit; you never build a lone monster).
   - **A story/choice room on the map** where the player picks an option and gets a
     consequence → **event / World Node**.
   - **Supported now: relic, potion, card, enemy encounter, and event.** (*Editing* an existing
     vanilla card/relic/potion is not yet supported — if that's the ask, say so and offer to
     build the closest **new** element instead.)
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
   - **Enemy encounter**: an enemy is fought inside its encounter, so treat them as one
     unit. Resolve only what genuinely shapes the fight: the monster's **HP**, what its
     **move** does each turn (attack for N? gain block? apply a debuff?), and whether it's
     a **single monster or a group**. Don't ask about scenes, animations, intents-as-code,
     or any API — those are the recipe's job.
   - **Event / World Node**: resolve the event's opening situation, the option(s) the
     player can choose, and each option's concrete consequence (gold/HP/card/relic/etc.).
     A one-option event is valid for the fast path. Ask which acts only if the user cares;
     default is all acts. Do not ask about `EventLoc`, room nodes, or registration.
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
   - **All four element types — card portraits, relic icons, power icons, and potion
     icons** can be generated (all live-verified; each is a loose PNG the game loads
     directly, no `.tres` authoring).
   - Offer one available source in plain language: an already-installed and authenticated
     **Vofy CLI** (managed credits), their own OpenAI-compatible endpoint
     (`art-backend.json`), or an existing local image. Check Vofy only with
     `acquire_sprite.py preflight`; never install it, run `vofy login`, or expose account
     output. If no custom route is ready, record `art: placeholder` and move on.
   - Capture the intended **subject/style** in plain words (e.g. "a burning arrow, comic
     style") once, for the mod. If the mod has several cards and the user wants distinct
     art per card, take one overall style note here; `author.md` fills the per-card
     subject from each card's SPEC when it generates — but you still only *ask* once.
   - **Events and enemy encounters do not have custom-art generation yet.** If the user
     requests a custom event/monster visual, state the current placeholder limitation and
     continue only if they accept it.

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
- **State lifetime**: "every N turns" on a relic continues across combats in the current
  run; "on turn N of each combat" uses that combat's turn number. Turn-local/once-per-
  combat wording resets at the boundary it names. Ask one carry-over question only when
  the phrase could reasonably mean either behavior.
- **Art**: **placeholder** (the template's fallback icon). This is the default — do NOT
  proactively ask about art. Only switch to `generate` if the user's sentence asks for a
  custom look (e.g. "a card showing a red phoenix", "make it look like…"). All four types —
  card / relic / power / potion sprites — can be generated (see step 4). It is a
  **single mod-level choice**, asked at most once regardless of sprite count. Custom
  generation can use an already-authenticated Vofy CLI or a BYO HTTP backend; an existing
  local image uses the same deterministic import path.
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
art source: vofy | byo-http | local-image  (generate only; no credentials/credits)
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
art source: vofy | byo-http | local-image  (generate only; no credentials/credits)
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
art source: vofy | byo-http | local-image  (generate only; no credentials/credits)
```

For an **enemy encounter** (monster + the encounter that spawns it, one unit):

```
element: enemy encounter
monster name: <proposed>
encounter name: <proposed, or "<Monster> Encounter">
hp: <int>
move: <plain-language each-turn behavior, with numbers, e.g. "attack for 6">
group: single | <describe the group>
art: placeholder (custom monster scene/animation not yet supported)
```

For an **event / World Node**:

```
element: event
name: <proposed>
opening: <short situation/initial page>
options:
  - <option title> -> <precise consequence with numbers>
acts: all | <specified acts>
art: placeholder (custom event portrait/background not yet supported)
```

Do not write files here — `spec.md` does that. If nothing was ambiguous, skip
straight to `spec.md` with the inferred intake.
