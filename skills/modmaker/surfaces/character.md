# Surface: character (Character Foundation)

Everything the pipeline needs for one playable Character, in one place: the SPEC envelope it
must declare, the element class the author writes, and the proof its verification owes. Read
this page at the `spec.md`, `author.md`, and `verify.md` stages when `element: character`.

One selectable character shell plus its starter ecosystem; scenarios are `RunStart` +
`CombatPlayer`. Selected advanced capabilities keep their separate contracts in `spec.md`
(capability module, character resource, ordered card buffer) — this page owns the Foundation.

## SPEC envelope

```markdown
# SPEC — <Mod Name>

- **element**: character
- **logical id**: <stable character stem>
- **mod id**: <stable mod identity>
- **author**: <author>
- **display**:
  - title: <shown character name>
  - description: <short identity/theme>
  - pronouns: <subject/object/possessive adjective/possessive pronoun>
- **starting HP**: <int>
- **energy per turn**: 3 (current grounded Foundation value)
- **availability**: character-scoped card/relic/potion pools
- **native design basis**:
  - grammar profile: `design/character-foundation.md @ STS2 0.107.1`
  - pinned facts used: <exact native identities/values used in the proposal>
  - observed convention: <native shape used as the recommendation>
  - creative decision: <exact selected deck shape and teaching intent>
- **starter deck**: <exact Basic-card multiset, base effects, upgrades, and total count>
- **starter deck rationale**: <how its first-run decisions teach the core mechanic>
- **deliberate native departure**: none | <departure plus onboarding, compatibility, and
  balance consequences accepted by the user>
- **starter relic**: <exact Starter relic>
- **hosted mechanic**: <one starter card/relic grounded public mechanic with exact numbers>
- **pool cards**: <every non-Basic pool card, each with its exact effect and numbers; each one
  with a non-trivial mechanic also needs its own `surfaces/card.md` envelope>
- **scenario**: RunStart + CombatPlayer
- **observe**:
  - the character is registered exactly once and appears in character selection
  - real character-select button present and clicked
  - runtime identity, HP, three pool types/members, exact deck/relic multisets
  - combat `MaxEnergy=3` plus the hosted mechanic's independent state delta
  - every pool card whose mechanic SPEC describes behaviorally is played and asserted
- **advanced mechanic**: none | <selected verified capability or explicit pack gap>
- **art**: placeholder | generate (Character static profiles and optional combat cues;
  list each consumer and acquisition count)
- **art source**: runtime-imagegen | vofy | byo-http | local-image (generate only)
- **character art bundle**: one `CharacterArtBundle` row per selected slot; record
  required/optional, output path, dimensions, alpha policy, fallback, and real consumer
- **character identity route**: selection portrait is the sole identity bootstrap;
  combat/rest/merchant and combat cue sheets use identity + type-matched style;
  background/icon/Energy use palette/motif brief + type-matched style only
- **palette/motif brief**: concise colors, motif, material, and silhouette derived from
  the user's description and reviewed selection portrait; never a second canonical image
- **character theme contract**:
  - name color: `<RRGGBB>`
  - energy-label outline: `<RRGGBB>`
  - deck-entry color: `<RRGGBB>`
  - energy outline: `<RRGGBB>`
  - card-frame target RGB: `<0..1, 0..1, 0..1>`
  - card-frame brightness: `<0..2>`
  - energy-icon palette: `<primary/accent/outline colors plus motif/material>`
- **character art profiles**: none | selection | locked selection | top-panel icon |
  map marker | select background | combat body | rest body | merchant body | energy |
  large energy icon | text energy icon (do not infer one profile from another; mark
  unsupported consumers as explicit gaps per `reference/character-presentation.md`)
- **character combat cues**: none | fixed bounded bundle
  - actions: Idle `4 x 180ms, loop`; Attack `4 x 90ms, one-shot -> Idle`;
    Hit `4 x 80ms, one-shot -> Idle`; Dead `6 x 140ms, terminal final frame`
  - acquisition: four action sheets, normalized selection portrait as identity reference
  - neutral combat anchor: <one concise pose sentence derived once and repeated verbatim>
  - continuity lock: same identity, costume, proportions, equipment, facing, camera,
    apparent scale, pivot, and baseline across all four sheets
  - frame motion: adjacent cells are small, substantially overlapping in-between pose
    steps, not distant key poses; Attack/Hit begin near and recover toward Idle; Dead falls
    through six adjacent steps
  - geometry: shared 512x512 content box/baseline/style and Bounds/Intent/Center/Orb/Talk anchors
  - fallback: one missing or invalid frame disables all cues and uses static combat body
  - explicit gaps: Cast, Spine, trails, audio, animated merchant/rest bodies
- **Ancient dialogue**: none | one block per cataloged vanilla target
  - target: <natural-language Ancient name; adapter resolves the pinned entry>
  - groups:
    - visit rule: first | visit <one-based N> | repeat from visit <one-based N>
      - lines: ordered `speaker: Character|Ancient`, `text`, and a transition prompt on
        every non-terminal line
      - Architect only: start attackers and end attackers, each
        `None|Player|Architect|Both`
  - native priority: preserve the global first-visit-ever introduction before Character
    exact-visit and repeating dialogue
  - explicit gaps: custom Ancient/model/background/layout/options/rewards/audio/multiplayer
- **derived ids** (adapter resolves after the semantic SPEC is accepted):
  - character logical id
  - every starter content logical id and localization fields
  - flat Ancient dialogue keys and zero-based visit metadata from the semantic groups
```

Do not add a manual registration line or invent a nonstandard energy override. If
`advanced mechanic` is not `none`, also record the capability-module envelope in `spec.md`.
Author it only when the named semantic capability has its own recipe in the shipped pack;
Package support alone does not provide missing runtime instructions. The current implemented
public framework routes are exactly `reference/character-resource.md` and
`reference/ordered-card-buffer.md`. If neither can express the mechanic, mark it unsupported
and report a pack gap.

## Pool cards are content, not filler

A Foundation needs enough unlocked non-Basic cards to fill the merchant's colored slots, so
the natural failure is to treat them as inventory that only has to *exist*. Pool membership is
what the Foundation proof asserts, and membership is satisfied by a card whose behavior is
entirely broken.

Declare every pool card's effect in `pool cards`. Any pool card carrying a real mechanic —
anything beyond a plain damage or block number — also gets its own `surfaces/card.md` envelope
and owes that surface's proof. A Foundation whose signature mechanic lives in a pool card has
not been verified until that card has been played.

## Author the element class

**Character Foundation** - use the pinned scaffold and `recipes/character.md`:

- Fill `ModCharacterTemplate<TCardPool,TRelicPool,TPotionPool>` with every required public
  abstract member. Extend the three public `TypeList*PoolModel` bases.
- Register the Character, exact Basic starters, Starter relic, every concrete pool member,
  and every supporting Power once through one content pack. Do not instantiate the
  character, add pool attributes, or add a second registration path.
- If Shop/static merchant is selected, author enough unlocked non-Basic cards to provide
  at least two Attacks, two Skills, and one Power after filters; the native merchant fills
  those exact slots and otherwise throws before its UI appears. Author each one through
  `surfaces/card.md`, not as a bare pool entry. Do not require the historical
  static-merchant patch.
- Add all 14 normalized `characters.json` values and a complete repeating Architect
  dialogue. When SPEC selects other Ancient targets or richer Architect groups, lower the
  semantic blocks through `reference/ancient-dialogue.md`; do not author an injection patch.
- Keep `CharacterAssetProfile` partial fallback semantics; selected Character static
  profiles fill only the matching fields after headed proof. When combat cues are selected,
  read `reference/character-combat-cues.md` and emit only its private combat-owned
  Idle/Attack/Hit/Dead state machine; never fill profile-global `VisualCues`. A
  Foundation-only SPEC emits no patch infrastructure. A resource SPEC
  registers one `SecondaryResourceDefinition`, uses `SecondaryResourceCmd` for amount and
  all-or-nothing payment, and mounts the fixed control through public `RegisterCombatUi`.
  An ordered-buffer SPEC uses `AttachedState<PlayerCombatState,TState>`, native source-card
  result piles, visible state text, and one configured output card. Never emit a retained-
  card `CustomPile` without a separately grounded UI lifecycle. Keep proof-only observers
  and assertions out of generated gameplay.

Ancient dialogue text may use the engine's `{character}` and pronoun tokens. Prefer them over
a hardcoded character name in any line that refers to the Character, so shipped non-English
dialogue keeps grammatical agreement.

## Self-test driver body

**character** → the **`RunStart` + `CombatPlayer`** variant: locate the real custom
character-select button, click it, then assert runtime identity in combat. The focused body is
in `reference/selftest-harness.md`.

Find the button by its normalized icon resource path, click it and Confirm, and wait for
`NRun.GlobalUi` before asserting runtime HP/pools/starter multisets. Enter combat, then assert
designed `MaxEnergy` and the starter mechanic's independent state delta. When those profiles
are selected, also enter the real RestSite and Shop hosts and assert background/rest/merchant/
full-energy resources through `CharacterAssetProfile`. Never select the first unlocked vanilla
character.

## Proof matrix

The final proof is valid only after the harness has asserted exactly one content-pack-
registered model, the real selected/unlocked button, runtime identity and exact SPEC HP/Max HP,
exact typed Card/Relic/Potion pools and member models, every independently registered
supporting Power, exact starter deck/relic multisets, and designed MaxEnergy. The unlocked Card
pool must also fill Shop's native colored Attack, Skill, and Power slots without falling back
to another character's pool.

- Derive every expected identity, count, value, and terminal summary from the current
  `SPEC.md`; never reuse a retired proof Mod's constants or marker.
- Assert the hosted mechanic's independent state delta.
- **Play every behavioral pool card.** Pool assertions prove membership, not `OnPlay`: a
  Foundation whose pool cards are entirely broken passes as long as the right models appear in
  the right multisets. For each pool card with its own `surfaces/card.md` envelope, drive it
  and assert its concrete state delta in the same run.
- For a character resource, require gain, affordable and unaffordable checks, one exact
  successful payoff, one rejected spend with no mutation/negative state, live counter
  values, public `RegisterCombatUi` attachment, the fixed 220x32 control at offset 160,
  a disjoint native-Energy global rect, and a distinct zero state/counter in combat 2.
- For an ordered semantic buffer/dynamic output, require exact source/compile-card result
  piles, visible order, capacity and overflow behavior, one generated-history entry, exact
  configured output/effect, `AttachedState` ownership, and a distinct empty state/UI in
  combat 2. Reject retained-card, hidden-zone, and `skipVisuals` substitutions.
- The Character-wide theme contract asserts all four colors, shader parameters, distinct
  paths, exact 256x256/24x24 textures, and both real consumers before it emits the theme
  marker.

## Manual fallback (only when the harness cannot reach its scenario)

Grant it:

   - **character:** select the custom character on the real character screen and click
     Confirm; there is no console shortcut that proves character-select presence.

Trigger it:

   **character** → confirm HP, starter deck/relic, and standard 3 energy after run start;
   enter combat and observe the named starter mechanic's exact state delta. When combat
   cues are selected, watch one full Idle loop, play an Attack, take one Hit, and reach Dead;
   confirm the first two return to Idle, Dead holds its last pose, and no anchor jumps.
