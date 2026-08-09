# M8.0 surface cross-check: envelope versus proof matrix

M8.0 change 1 co-locates each element's SPEC envelope, author driver body, and proof matrix
into `skills/modmaker/surfaces/<element>.md`. The carry-forward contract for the nine
surfaces after the Card pilot requires three things: run an explicit envelope-versus-proof
cross-check while co-locating, collect mismatches across all ten elements before fixing any
of them, and record every mismatch found — including the ones left unfixed — so a co-located
surface is never mistaken for a validated one.

This file is that record. It is the answer to "has this surface been checked?", which is a
different question from "is this surface correct?".

**Method.** For each surface, read its envelope and its proof matrix in one pass and ask two
questions in both directions: does the proof require a value the envelope has no field to
declare, and does the envelope declare a field no proof case ever observes? A mismatch is
recorded whether or not it was fixed, and each one records whether it was inherited from the
pre-co-location layout or introduced by the co-location drafts themselves.

**Scope limit.** This is a static reading of shipped prose. It does not run the pipeline, does
not build a Mod, and does not prove any surface's behavior. Only the Card pilot has a real
run behind it (`[PASS] Tier-2 verified`, 13 state proofs); the other nine surfaces are
co-located and cross-checked but not independently piloted.

## Result

Ten surfaces checked. Thirteen mismatches found, in five classes. Ten fixed, three left open
with a recorded reason.

Mismatches 9-11 were found by the automated check in `tools/tests/test_surface_cross_check.py`,
not by the manual read that produced 1-8. That is the useful result of building it: the manual
pass over all ten surfaces missed three cases of exactly the class it was looking for.

Mismatch 12 was added by M8.0 change 2 and is a different axis: prose against the *code* that
owns the value, rather than prose against prose. It was invisible to both earlier passes
because neither compared a document to a Python literal.

Mismatch 13 came from change 5 and is a third axis again: prose against *itself across files*.
Nothing had compared two stage pages stating the same rule, so three non-matching versions of
the tier-honesty rule coexisted without any check noticing.

| # | Surface(s) | Mismatch | Origin | Found by | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | potion, power, orb, monster, event, character | Flat `element:` envelope contradicts the canonical nested `content:/surface:` envelope that `semantic-contract.md` declares itself source-of-truth for | Inherited | manual | **Open** |
| 2 | keyword, enchantment | `semantic-contract.md` lists both as `content.surface` enum values with their own Surface-inputs rows, while the surfaces declare no element block at all | Introduced | manual | Fixed |
| 3 | card | Host-Card fields that `keyword.md` and `enchantment.md` instruct the author to write are absent from the Card envelope | Introduced | manual | Fixed |
| 4 | card | No envelope field declares engine-composed keyword text, so the pilot's "do not re-author Exhaust" rule has nothing to check against | Inherited | manual | Fixed |
| 5 | potion | `boundary cases: <upgrade/state/relationship cases>` offers an upgrade case; Potions have no upgrade concept | Inherited | manual | Fixed |
| 6 | character | Proof matrix restates verify.md's character-resource and ordered-buffer bullets, so one proof has two homes that can drift | Introduced | manual | Fixed |
| 7 | character | The resource and ordered-buffer *envelopes* stay in `spec.md` while their proof moved to `surfaces/character.md`, so that capability pair is still split across two files | Inherited | manual | **Open** |
| 8 | all ten | Nothing mechanically compares an envelope against its own proof matrix, and `design_trace.py` validates only the DESIGN/SPEC-trace YAML, never envelope field names | Inherited | manual | Partly closed |
| 9 | relic, potion | Both declare `keyword tips:` and carry a section explaining that Relic/Potion tips are *not* automatic, but no proof case observes the registration | Inherited | automated | Fixed |
| 10 | relic, potion | Both declare `localization.displayed values:` with a literal-versus-placeholder decision, but no proof case observes that the value renders live | Inherited | automated | Fixed |
| 11 | power | `amount domain` is mandatory and the author page requires clamping to every finite bound, but no proof case asserts the bounds | Inherited | automated | Fixed |
| 12 | (art contract, not a surface page) | The combat-cue sheet grid is written columns-first in four prose copies and printed rows-first by `gen_sprite.py list-specs`, so the only non-square sheet is named `3x2` by the tool and `2x3` by every document | Inherited | change 2 | Fixed |
| 13 | (stage pages, not a surface page) | `verify.md`'s finalize told the reader to "be honest about the tier", `repair.md`'s hard limits said "never fake success", and `SKILL.md` said "a green build is not success" — three wordings of one rule, none of which named a canonical home | Inherited | change 5 | Fixed |

## The mismatches

### 1. Two incompatible envelope forms — open

`semantic-contract.md` opens by declaring itself "the source-of-truth for the product-level
`SPEC.md` envelope", specifies a nested canonical envelope keyed on
`- **content**:` / `surface:`, and constrains extensions explicitly: surface-specific blocks
"may add fields, but must not replace or rename the shared sections". The named shared
sections are `contract`, `content`, `registration`, `localization`, `effects`, `state`,
`presentation`, `fallback`, and `proof`.

Card and Relic comply. Potion, Power, Orb, Monster, Event, and Character use a flat form that
opens `- **element**: <slug>` and replaces the shared sections with ad-hoc top-level keys
(`rarity:`, `availability:`, `usage:`, `target:`, `effect:`, `display:`, `art:`, `observe:`).
That renames `content.surface` to `element`, drops `contract` on all six, and substitutes
`observe:` for `proof:` on three of them (`monster`, `event`, `character`; `potion`, `power`,
and `orb` keep `proof:`). An earlier revision of this record said four; recounted mechanically
across all ten pages.

Inherited, and verifiable as such: at `HEAD` (`c5452d8`) `spec.md` already carried
`- **element**: potion` at line 304, `power` at 413, `enemy encounter` at 490, `event` at 540,
and `character` at 622, while `relic` at 232 and the card page were already nested. Before the
pilot (`972f72f`) Card was nested at line 393. Co-location relocated this text; it did not
create the split.

**Deferred to M8.2 by the human lead on 2026-08-10.** Normalizing six envelopes to the canonical
form changes what a SPEC declares for most surfaces, and `semantic-contract.md` states that "a
change to this envelope requires a contract-version bump and a migration note". That is a
contract migration, not a file move, and it is larger than the co-location Package. It also
overlaps M8.2's recorded ownership of "whether a native engine capability the SPEC grammar cannot
yet declare is a grammar gap or a capability-promotion decision" — the same decision, so doing it
twice was the alternative rejected.

Until M8.2 resolves it, this stays a live contradiction in the shipped pack: `semantic-contract.md`
claims authority its six flat surfaces do not honor, and nothing mechanically enforces either
form. A reader following the contract file and a reader following `potion.md` produce differently
shaped SPECs, and both pass today.

This is the clearest evidence for change 1's premise so far. The contradiction is between a
surface page and the contract file that governs it, and reading either file alone cannot
reveal it — which is why it survived through M7.

### 2. keyword and enchantment: enum member versus no element block — fixed

`semantic-contract.md` lists `keyword` and `enchantment` among the legal `content.surface`
values and gives each its own Surface-inputs row with a `CombatPlayer` proof route. The
co-located pages state that neither has an element block, because a keyword owns shared
vocabulary whose behavior lives in a host, and an enchantment is always attached to a host
Card. Both pages record that as a human-lead decision on 2026-08-07, with `orb` receiving a
full envelope in the same decision.

The decision is authorized; the contract file was simply never synchronized to it, so the
enum and the surfaces disagreed about whether these two are standalone content.

Fixed by making the distinction explicit rather than by changing the enum: both remain
contract surface identities for adapter routing and keep their Surface-inputs rows, and
`semantic-contract.md` now records that they are declared nested inside their host Card's
`content:` block instead of as their own top-level block.

### 3. Host-Card fields with no envelope — fixed

`keyword.md` instructs the author to write `keywords:` and `behavior owner:` inside the host
Card's envelope. `enchantment.md` instructs `enchantment:`, `amount:`, `host restriction:`,
and `stacking:`. The Card envelope declared none of them; its only related field was
`relations: <none | custom power/keyword/enchantment/orb dependencies>`, which names the
dependency but carries none of those values.

So following `keyword.md` or `enchantment.md` as written produced SPEC fields no envelope
declares, and mismatch 8 means nothing would have rejected them. Introduced by the drafts.

Fixed by adding both nested blocks to the Card envelope in `surfaces/card.md`, keeping
`relations:` as the dependency edge and letting the nested blocks carry the values each
surface's proof matrix actually exercises — the keyword's shared rule and behavior owner, and
the enchantment's amount, host restriction, and stacking outcome.

### 4. Engine-composed text had no declaration — fixed

The pilot's first finding: a self-exhausting Card must not write "Exhaust" into its own
description, because `CardKeywordOrder` appends the keyword text automatically and vanilla
`Impervious`/`Offering` carry none of it. The pilot deliberately deferred the fix shape,
requiring it be decided from the full cross-check rather than from the Card alone.

The full set shows the same hazard on eight distinct paths: native keywords appended to a
Card description; mod keywords injected via `ModKeywordRegistry.GetCardText`; an
enchantment's `extraCardText` stamped into its host Card and its tip folded into the host's
`HoverTips`; SmartFormat/DynamicVar substitution in Relic and Potion descriptions; an Orb's
`{Passive}`/`{Evoke}` under `smartDescription`; a Power's `{Amount}` plus its composed
title+description tip; a Monster's intent label computed from live damage with Weak,
Vulnerable, and Strength applied; and Event `DynamicVars` substituted into option titles,
option descriptions, and page descriptions.

Those split into two obligations that a single rule covers: do not hand-write text the engine
will compose, and do not hand-write a value the engine will substitute. Both are one
principle — engine-composed player-facing text is not author-written text.

Fixed at the shape the full set implies rather than the Card alone:

- one shared rule in `spec.md`, stated once, naming both obligations and the surfaces they
  land on, since it spans ten surfaces and belongs with the other shared declarations;
- one `engine-composed text:` field in the Card envelope, listing the tokens the engine will
  append for this Card — native keyword, mod keyword, or enchantment `extraCardText` — so the
  "declared, therefore not re-authored" pair is a checkable statement rather than a
  convention; and
- each surface keeps only its own instance of the rule, which the drafts already carry.

### 5. Potion upgrade case — fixed

`potion.md` offered `boundary cases: <upgrade/state/relationship cases, or none>`. Potions do
not upgrade in STS2; `recipes/potion.md` has no upgrade concept, and the Potion envelope has
no upgrade field to pair with such a case. Inherited copy-paste from the Card envelope, where
`upgrade:` is real. Fixed by replacing the upgrade case with the boundary cases a Potion can
actually have.

### 6. Character proof duplicated in two files — fixed

`surfaces/character.md`'s proof matrix restated `verify.md`'s character-resource and
ordered-semantic-buffer bullets. Both copies listed the same requirements, so the resource
proof had two homes and could drift. Introduced by the draft.

Fixed the way the pilot fixed Scry: the surface page owns the proof, and `verify.md` points to
it. That is now the established direction for anything a single surface owns.

### 7. Resource and buffer envelope/proof still split — open

The same two capabilities keep their *envelopes* in `spec.md` (capability module, character
resource, ordered semantic buffer) while their proof now lives in `surfaces/character.md`.
Character is the only surface that can select them, so under change 1 they would ideally sit
in `character.md` too, which would make that page the single read for a resource Character.

Left open, and now travelling with mismatch 1. It is the same envelope-and-proof-in-different-files
shape change 1 targets, but moving them is a further relocation of shared declarations rather than
part of co-locating the nine surfaces, and `character.md` is already the largest surface page.
Since these two envelopes live in `spec.md`'s shared section, where they land depends on the
envelope form M8.2 selects; moving them first and normalizing them second would touch the same
text twice.

### 8. No mechanical cross-check — partly closed

The plan records two enforcement gaps: `design_trace.py` accepted invented SPEC fields
silently, and no automated check compares an envelope against its own proof matrix.

Confirmed for the first: `design_trace.py` validates the `open-mod-design/v1` and
`open-mod-spec-trace/v1` YAML contracts and nothing else. It never reads envelope field names,
so mismatch 3 could not have been caught by it.

Partly closed for the second. `tools/tests/test_surface_cross_check.py` now enforces the
structural and pairing properties that are mechanically decidable: every surface page has the
four required sections or an explicit no-envelope statement, every cross-reference to another
surface page resolves to a real file and heading, and each mandatory field established by this
cross-check is paired with the proof case that observes it — Relic `cadence` with its cadence
case, Power `lifetime` with its lifetime case, Potion `target`/`usage` with their assertions,
Orb's three behaviors, Enchantment `host restriction` with its illegal-host case, Monster
`moves`/`branches` with their traversal, Event option availability with its both-ways case,
and Character `pool cards` with its play-every-behavioral-card case.

Still open: whether a *generated* project's `SPEC.md` conforms to its surface envelope. That
needs the envelope schema mismatch 1 leaves unresolved, so it cannot be closed before that
contract decision.

### 9-11. Declared fields no proof case observed — fixed

The three the automated pairing check caught, all the same shape as the Relic `cadence` case
the pilot found: a field the envelope requires, with a whole explanatory section behind it, and
no proof case that would fail if it were wrong.

- **Relic and Potion keyword tips.** Both pages explain at length that, unlike a Card, these
  surfaces surface no tooltip from merely naming a keyword — it needs an explicit
  `RegisteredKeywordIds` entry. Both declare `keyword tips:` for that decision. Neither proof
  matrix observed it, so a description naming a keyword with no registration ships and the
  player hovers a term with nothing behind it. No effect assertion sees that.
- **Relic and Potion displayed values.** Both declare `displayed values:` to record the
  literal-versus-placeholder choice, and Potion's page notes the default recipe shape puts the
  number in two places where they can diverge. Neither proof matrix asserted the rendered text,
  so an unresolved `{Placeholder}` and a diverged hardcoded number both passed.
- **Power amount domain.** `amount domain` is mandatory for every custom Counter, and
  `author.md`'s Counter gate requires clamping gain and consumption to every finite bound. The
  proof matrix asserted the applied amount, which sits in the middle of the domain — an
  unclamped Counter exceeding its maximum, or going negative on consumption, passed.

Each now owes an explicit case, and the pairing test holds the field and its case together.

### 12. The cue sheet grid had two opposite conventions — fixed

Found by change 2's mechanical comparison of the art-contract prose against the code that
owns it. Not a surface page, but the same class as 9-11 and recorded here because this file
is where the class is tracked.

`CharacterCueAction("dead", ..., rows=3, columns=2)` produces a sheet whose geometry is
`columns * 512` by `rows * 512` — 1024 wide by 1536 tall, so 2 columns and 3 rows. Four
prose copies (`art-contract.md` twice, `character-combat-cues.md`, `author.md`) all wrote
`2x3`, agreeing with that geometry and with `gen_sprite.py`'s width-first convention for
every other size. `list-specs` printed `f"{action.rows}x{action.columns}"`, so it announced
`3x2`. `character_cues.py`'s divisibility error used the same rows-first order.

`Idle`, `Attack`, and `Hit` are all 2x2, so the disagreement was invisible on three of the
four actions. On `Dead` it was live: an author following `list-specs` would request a
3-wide by 2-tall sheet, and `character_cues.py` would then either reject the 1536x1024
source or slice the wrong cells out of it.

The prose was right and was not changed. Fixed on the two code paths that printed the
opposite order, and prevented from recurring by three things rather than by a corrected
number: `list-specs` now prints the pixel size width-first plus the labeled
`2 cols x 3 rows`; the error message names its axes and states the expected size; and the
catalog carries `columns`, `rows`, and `sheet_px` as separate fields, so no consumer has to
infer an order from a concatenated string. Both cue tables now label the column order in
their headers, and `test_art_contract_catalog.py` asserts that label is present.

This is the first mismatch found by comparing prose against *code* rather than prose against
prose, which is a different axis from mismatches 1-11.

### 13. One rule, three non-matching wordings — fixed

Found by change 5. Not a surface page either, and a third axis: prose against the same rule
stated elsewhere in prose. Mismatches 1-11 compared two things inside one stage's own scope,
and 12 compared prose to code. Nothing had ever compared `verify.md`'s statement of a rule
against `repair.md`'s.

The rule that a run must report the verification tier it actually reached appeared three times:

- `SKILL.md`: "A green build is not success… Report exactly which tier was reached";
- `verify.md`: "Always report which tier you reached; never claim the effect is verified when
  only load was", and again at finalize as "Be honest about the tier";
- `repair.md`: "**Never fake success.** Only report a tier as passed when its *own* re-verify
  passed on observed reality."

Three wordings is not three reminders. It is three chances to follow the weakest one, and no
file claimed to be the source of truth, so a later edit to any single copy silently produced a
fourth variant. The same pattern held for six other cross-stage rules: grounding a route rather
than guessing it, refusing to manufacture evidence, stopping at a visible substitution,
preserving settled decisions, staying inside the pinned framework boundary, and not editing the
installed pack from inside a run.

Fixed by giving each rule one home in `modmaker/invariants.md` as `INV-1` through `INV-8`, and
leaving each stage page to name the invariant and add only its own stage-specific detail.

**The correction that mattered more than the consolidation.** Moving a rule out of a lazily
loaded stage page and leaving a pointer behind makes the rule *weaker*, not stronger: a run
that reads `verify.md` without reading `invariants.md` then has zero copies of it. Drifting
wording at least states a rule three times; a dangling pointer states it none. So
`invariants.md` is registered as read once at pipeline start and kept in context, which is what
makes a pointer safe. `test_invariants.py` asserts that registration, and would fail if a later
edit demoted the page to lazy loading while the pointers remained.

Two things this fix does **not** establish. The single-definition check covers eight canonical
phrasings, not every sentence in the pack, so a ninth restatement could still be added
elsewhere without failing. And an eagerly loaded page costs context on every run, including a
trivial resume that reads one stage; the trade was accepted because a full pipeline previously
paid for these rules in several files at once, but it was not measured.

- No surface here except Card has been piloted through a real authoring run.
- A fixed mismatch means the shipped prose no longer contradicts itself. It does not mean the
  surface generates a working Mod.
- Mismatches 1 and 7 are live contradictions in the shipped pack, recorded and unfixed.
- The static reading may have missed mismatches. Absence from this table is not proof of
  consistency.
- Mismatch 13's fix is a prose and loading-order change. No run has yet been observed obeying
  an invariant it reached only through a pointer, so "the pointer is safe because the page is
  eagerly loaded" is a checked registration, not observed behavior.
