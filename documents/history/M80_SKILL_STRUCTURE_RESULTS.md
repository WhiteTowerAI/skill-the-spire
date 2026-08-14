# M8.0 skill structure restructuring — results

Status: **closed by explicit human-lead decision on 2026-08-10.** All five approved changes are
implemented in source and both committed payloads are synchronized. The Package's own work order
is complete: card pilot, one real run, packaging fix, remaining nine surfaces, then changes 2, 3,
4, and 5, then payload regeneration.

Closing it did not make the pack internally consistent. Three of the thirteen recorded cross-check
mismatches are deliberately unresolved and were deferred to M8.2 by the human lead on the same
day: the two incompatible envelope forms, the character resource/ordered-buffer envelope-proof
split, and the absence of any check comparing a generated project's `SPEC.md` against its surface
envelope. They are live contradictions in the shipped pack, not oversights. Nine of the ten
co-located surfaces have never been piloted.

Payload state: both committed payloads were regenerated from source on 2026-08-10 after change 5,
and carry all five changes. See § Payload synchronization for what that was and was not verified
to establish.

Package contract: `documents/IMPLEMENTATION_PLAN.md` § M8.0.

## What the Package is for

The shipped pack was organized by authoring stage, so one element's rules were split across
three files: a Card's envelope in `spec.md`, its driver body in `author.md`, its proof matrix in
`verify.md`, hundreds of lines apart. The cost is not only tokens. When an element's envelope
and its proof matrix cannot be read together, a proof can demand a value the envelope has no
field to declare, and nothing in the workflow surfaces the contradiction.

Change 1 co-locates by element: `surfaces/<element>.md` holds {envelope + driver body + proof
matrix}, and the stage pages keep shared rules plus a pointer.

## Card pilot (commit `c5452d8`)

Done and proved. A pilot Mod authored only through `surfaces/card.md` reached
`[PASS] Tier-2 verified` on STS2 `0.107.1` with RitsuLib `0.5.4`, asserting 13 state proofs
across base and upgraded play, including result-pile membership.

The pilot's verdict on change 1's premise held: the contradiction now reads within one file —
the Card envelope had no field to declare a native keyword while the same file's proof matrix
required `result pile` as an invariant, 42 lines apart. The moved `relations:` line was
byte-identical before and after, confirming the refactor relocated text without altering it, so
the contradiction was inherited rather than introduced.

Recorded weakening: the pilot card was deliberately chosen to force a non-default result pile,
so that test was aimed rather than blind. The supportable claim was that co-location makes the
cross-check possible in a single read, not that it performs the check.

## Packaging defect (fixed 2026-08-07)

The build deployed `openmod/vanilla-overrides.json` inside the Mod tree, where the game's
recursive manifest scan parses every `.json` at any depth as a Mod manifest and logs a
missing-`id` error. Every generated Mod carried it. `scaffold.py` no longer copies the sidecar,
and `build.py` enforces the general rule: only `<ModName>.json` may be loose JSON in a deployed
Mod, an older build's copy is pruned so existing projects self-heal, and any other deployed
non-manifest `.json` fails the build. Proved on Windows in one log — a fresh probe scanned one
manifest with no error and passed Tier 1, while a Mod built by the older scaffold still showed
the phantom error in the same run.

## Remaining nine surfaces

All ten elements are now co-located. `relic`, `potion`, `power`, `orb`, `keyword`,
`enchantment`, `monster`, `event`, and `character` joined `card` under
`skills/modmaker/surfaces/`.

Deduplication is complete rather than partial, which matters because a co-located page beside a
still-live inline copy is worse than either alone — the two drift:

- `spec.md` carries a pointer for all ten surfaces. It shrank from 946 lines at `c5452d8` to
  roughly 690 after the shared engine-composed-text rule was added.
- `author.md` § 1 replaced nine inline element-class bodies with pointers, and § 2.5 replaced
  five inline driver bodies with one dispatch paragraph.
- `verify.md` replaced its Character Foundation, multi-move enemy, Event, Rest Site, character
  resource, and ordered-buffer bullets with pointers, and collapsed its per-element manual
  grant/trigger lists.

Detail that existed only in the stage pages was moved into the surface page that owns it, not
dropped: six Event author bullets (`portrait_halo` cleanup, bounded text tags, `HoverTipFactory`
tips, `ThatDoesDamage`/`ThatDecreasesMaxHp`, `CardPileCmd.Add` preview, `weak_short`,
`trial_noble`), the Event manual-trigger presentation cases, the Character manual trigger and
combat-cue observation, the Character driver's icon-resource-path button lookup,
`NRun.GlobalUi` wait, RestSite/Shop asserts, and the "never select the first unlocked vanilla
character" constraint. Detail that already lived in `reference/selftest-harness.md` was deleted
rather than moved, since the surface pages route there.

## The carry-forward cross-check

The contract required three things: run an explicit envelope-versus-proof cross-check while
co-locating each surface, collect mismatches across all ten before fixing any of them so one fix
shape is decided from the full set, and record every mismatch including the unfixed ones.

All three ran. The full record, with per-mismatch origin and reasoning, is
`games/sts2/tests/m80-surface-cross-check.md`. Summary for the surface step: **eleven
mismatches, eight fixed, three open.** Change 2 later added mismatch 12 to the same record, so
that file now totals twelve found and nine fixed.

The most consequential finding is open. `semantic-contract.md` declares itself source-of-truth
for the SPEC envelope, specifies a nested `content:/surface:` form, and states that
surface-specific blocks "may add fields, but must not replace or rename the shared sections."
Card and Relic comply. Potion, Power, Orb, Monster, Event, and Character use a flat
`- **element**:` form that renames `content.surface` to `element`, drops `contract`, and
substitutes `observe:` for `proof:`. This is inherited and verifiable as such at `c5452d8`. It is
left open deliberately: normalizing six envelopes changes what a SPEC declares for most
surfaces, and the contract file states that changing the envelope requires a contract-version
bump and a migration note. That is a contract migration, not a file move, and it overlaps M8.2's
recorded ownership of grammar-gap-versus-capability-promotion decisions.

Also open: the character-resource and ordered-buffer envelopes stay in `spec.md` while their
proof moved to `surfaces/character.md`, so that capability pair is still split across two files —
the same shape change 1 targets.

The pilot deferred the engine-composed-text fix shape until the full cross-check. The full set
showed the same hazard on eight distinct paths, which split into two obligations covered by one
principle: do not hand-write text the engine composes, and do not hand-write a value the engine
substitutes. The fix is one shared rule in `spec.md` stated once, one `engine-composed text:`
field on the Card envelope so "declared, therefore not re-authored" is checkable, and each
surface keeping only its own instance. That is a rule about the engine, not a list of mechanics.

## The automated check found what the manual pass missed

`games/sts2/tools/tests/test_surface_cross_check.py` enforces the mechanically decidable part:
structural completeness of all ten pages, resolution of every `surfaces/<x>.md § Heading` pointer,
and the pairing of each mandatory envelope field with the proof case that observes it.

Mismatches 9 through 11 were found by that test, not by the manual read that produced 1 through 8:

- Relic and Potion both declare `keyword tips:` and both carry a section explaining that, unlike
  a Card, these surfaces produce no tooltip without an explicit `RegisteredKeywordIds` entry.
  Neither proof matrix observed it, so a description naming a keyword with no registration ships
  and the player hovers a term with nothing behind it.
- Relic and Potion both declare `displayed values:` to record the literal-versus-placeholder
  choice, and Potion's page notes the default recipe shape puts the number in two places where
  they can diverge. Neither proof matrix asserted the rendered text, so an unresolved
  `{Placeholder}` and a diverged hardcoded number both passed.
- Power's `amount domain` is mandatory and `author.md`'s Counter gate requires clamping to every
  finite bound, but the proof matrix asserted only the applied amount, which sits mid-domain.

Each is the same shape as the Relic `cadence` case the pilot found: a required field, a section
explaining why it matters, and no proof case that would fail if it were wrong. All three now owe
an explicit case.

This is the useful result. The manual pass over all ten surfaces was looking for exactly this
class and missed three instances of it, which is the strongest available evidence that a
mechanical check was the missing piece rather than more careful reading. It also narrows the
pilot's claim usefully: co-location made the check *possible* in one read, and the test is what
made it *happen*.

## Change 2: data into queryable form

Change 2 names two datasets. The first needed its direction decided before anything moved.

**The art contract's authority is code, not prose.** `gen_sprite.SPECS` (9 content specs) and
`character_art.CHARACTER_ART_BUNDLE` (16 slots, 4 cue actions) hold the exact values, and the
bundle's own docstring already claimed to be "the one source of truth". Three prose tables
restated it: the `art-contract.md` main table, its Character profile and cue tables, and
`character-presentation.md`'s profile matrix.

The human lead selected code-as-source with the catalog as a generated projection, rather than
the JSON-as-source shape used by vanilla-overrides. The reason the two differ: the
vanilla catalog is collected from the game assembly, so JSON is where the external fact lands.
Art has no external source to collect from — the code *is* the ground truth, and `fit`,
`chroma`, and the visible footprints are normalization behavior rather than documentation.
`gen_sprite.py export-contract` writes
`sts2-api/reference/catalogs/art-contract-sts2-0.107.1.json` (15 KB, `openmod.sts2.art-contract/v1`),
reusing the existing canonical-JSON digest convention. `--check` fails without rewriting, so
staleness is detectable in CI as well as in the test.

**A projection alone would only add a fourth copy.** What makes it one contract is
`test_art_contract_catalog.py` (13 cases): the committed catalog must equal what the code
holds, its digest must be self-consistent, every size in all three prose views must equal the
catalog's, and every catalog spec must have a prose row. Both directions were verified to fail
by mutation — changing a size in code with no re-export fails two cases, and re-exporting
without updating prose fails a third.

The test deliberately does not compare `character-presentation.md`'s `consumer` column to the
bundle's `consumer` strings. That column is prose paraphrase of the same consumer
("player `NCreature.Visuals`" against `player NCreature.Visuals`), so exact comparison would
report normal rewording as drift. Only sizes and spec coverage are mechanically decidable
there, and claiming more would make the test a liability.

**Mismatch 12, found by that comparison.** Prose had been checked against prose before; this
was the first check of prose against the code that owns the value, and it found a live
contradiction. `CharacterCueAction("dead", ..., rows=3, columns=2)` yields a 1024x1536 sheet —
2 columns, 3 rows. Four prose copies wrote `2x3`, matching that geometry and `gen_sprite.py`'s
width-first convention everywhere else. `list-specs` printed rows-first, announcing `3x2`, and
`character_cues.py`'s divisibility error used the same reversed order. `Idle`/`Attack`/`Hit`
are 2x2, so only `Dead` exposed it: an author following `list-specs` would request a 3-wide by
2-tall sheet, which `character_cues.py` would then reject or mis-slice.

The prose was right and was left alone. Fixed by removing the ambiguity rather than by
correcting one number: `list-specs` prints pixel size width-first plus a labeled
`2 cols x 3 rows`, the error names its axes and the expected size, the catalog carries
`columns`, `rows`, and `sheet_px` as separate fields, and both cue tables label the order in
their headers. Recorded as mismatch 12 in `games/sts2/tests/m80-surface-cross-check.md`.

**The second dataset needed correcting on the facts before it needed work.** The Package
contract describes `character-foundation.md` as restating its JSON catalog in prose. It does
not. The overlap is partial: the JSON carries `starting_hp`, `starting_gold`, and
`starting_relic` that the prose never mentions, while the prose adds a `Total` column
(derivable) and an `Identity teaching cards` column (design commentary, not data). The only
duplicated data is the starter deck, and it sits in three places — the JSON, the prose table,
and `test_m72_native_grammar.py`'s `EXPECTED_DECKS`.

Here JSON is already the authority and is already checked against the pinned catalog and
research, so no extraction was needed. What was missing is that nothing checked the prose
table. One case was added to `test_m72_native_grammar.py` deriving each row's deck entries and
total from the inventory; `EXPECTED_DECKS` stays, because it is an independent expectation
checked against the pinned catalog rather than a restatement. Verified by mutation.

**The unobserved-field finding, and the lead's decision on it.** The inventory's
`starting_hp`, `starting_gold`, and `starting_relic` had no prose or test consumer — the same
shape as cross-check mismatches 9-11, a field that exists and nothing observes. It mattered
more than a bookkeeping gap: `surfaces/character.md` requires `starting HP` on every custom
Character, so the design conversation decides that number every time, and the file it loads
stated none of the five native values. The same table asks for a Starter relic recommendation
without naming the five native relics.

Raised as a design judgment rather than taken unilaterally. The human lead approved surfacing
it on 2026-08-10, so `character-foundation.md` now carries `HP` and `Starter relic` columns
derived from the inventory, states the native `66`-`80` range and the 99 Gold constant, and
`test_m72_native_grammar.py` derives both new columns and the range from the JSON.

Drafting those columns produced a second, sharper finding. The first draft also described what
each native Starter relic does, to give the recommendation more to reason from. Checking the
pinned catalog before shipping it showed that those descriptions had no grounding: the catalog
carries relic id, localized title, and rarity, but **no effect text** for
`BurningBlood`, `RingOfTheSnake`, `CrackedCore`, `BoundPhylactery`, or `DivineRight`. The
descriptions were recalled, not checked, so they were dropped rather than shipped.

The page now states that limit explicitly — name a native relic as an analogy, never describe
its behavior from memory — and a test asserts the caveat is present. That caveat is the more
durable half of this change: the columns give the design conversation a real anchor, and the
caveat marks exactly where the anchor stops.

**One-line path correction.** `art-contract.md` attributed the bundle to
`games/sts2/tools/character_art.py`, a maintainer repo path that does not exist inside either
payload, where the tools ship at `skills/modmaker/scripts/`. Same defect class as the
catalog's `source.definition` field above. Corrected to name the module only. Pre-existing,
found while auditing change 2's own additions for the same mistake.

## Change 3: split scars by kind

Both homes already existed, and `quirks.md` already stated the division: it is the "know it up
front" file, `errors.md` is signature-to-fix. What had drifted was which file held what.

The split was restated as a rule about *when* you need a line, because that is the only test an
author can apply without reading both files: `quirks.md` holds constraints you follow before
anything breaks, `errors.md` holds signatures you match after. A line needing no error code
belongs in the first; a line meaningless without a failing signature belongs in the second.

**What moved.** Three clusters of diagnostic scars sat on main paths:

- `build.md` § Failure classes, 8 entries. Four were already in `errors.md` verbatim in
  substance (compile asset, host branch, runtime not found, no matching variant), three existed
  only here (`[ancient-dialogue]`, `[vanilla-overrides]`, `has_pck` mismatch), and one was a
  pointer to `repair.md`. The three missing ones were added to `errors.md` first, plus the
  loose-`.json` manifest-scan diagnostic from this Package's own packaging fix, which had a
  build-time rule but no catalog signature. The section became a five-line pointer keeping only
  the two routing rules the catalog does not carry: a profile contract error is fixed at
  scaffold and never in a C# repair loop, and ordinary `CS*`/`MSB*` go to `repair.md`.
- `repair.md`'s per-mechanic localization paragraphs, 25 lines across stateful cadence,
  character resource, ordered buffer, and Scry. `errors.md` § Behavior already owned every
  signature but not the boundary discrimination — *which* boundary a symptom points at. That
  detail was merged into the four existing entries rather than appended as new ones, so the
  catalog gained precision instead of length, and `repair.md` kept its three tier-2 signature
  classes, which are loop logic rather than scars.
- `verify.md`'s tier-1 failure modes. The three-way distinction stayed, because deciding which
  failure you have is the stage's own job; the restated causes and fixes became pointers.

**What deliberately did not move.** `verify.md`'s log-rotation scar is preventive: never slice
the log by a pre-launch byte offset. It fires while reading the log, so it stays where it fires,
compressed from six lines of history to three lines of constraint. The same treatment removed
the error codes from `quirks.md`'s MSB1008 and CS8602 entries, leaving the rule and letting
`errors.md` own the signatures.

**A dangling pointer found while doing it.** `verify.md` sent the reader to `errors.md`
"Verification harness" for a console that will not open or a grant that says `Unable to create`.
No such section has ever existed, and `errors.md` had no console entry at all, so the pointer
had always landed nowhere. Fixed by adding the entry — built from the grounded dev-console
facts already in `quirks.md`, not invented — and correcting the pointer.

That is the same failure mode change 3 could have introduced at scale: trading inline detail for
a pointer only helps while the pointer resolves. So
`test_surface_cross_check.py` now resolves every `errors.md § Section` reference in the
modmaker pages and asserts the delegating stages do not keep a rival cause-and-fix list. Both
cases were verified to fail by mutation.

Net effect: 67 lines off the four main-path pages, 68 into the catalog, net +1 overall — the
console entry. Diagnostics were relocated, not deleted.

## Change 4: move project history out of runtime instruction

The shipped pack carried roughly 190 milestone-identifier occurrences across ~30 files. They
were not one thing, so the pass classified by what the id *does* rather than by file, and only
two classes were removed.

**Kept, because the id is load-bearing.** Five package ids like `m6.7.1-public-card-overrides`
are manifest keys with code constants in `vanilla_overrides.py` and matching values in the
catalog's `promoted_operation_packages`; changing prose that names them would desynchronize the
maintainer regeneration command. Tier 2 markers such as `R6 scry helper complete
expected=all observed=all` are grep contracts. `pre-M7.4` and `before M6.7.0` are
resume-compatibility boundaries that decide whether an unfinished project may skip an artifact.
Evidence attributions naming the run that grounded a fact stayed too: deleting "the R3 proof
observed capacity 1" and keeping "capacity 1" would make a proven value indistinguishable from
an assumed one, which works against the pack's own no-fabrication discipline.

**Removed: bookkeeping.** "M6.7.1 accepts the exact public Card routes" says nothing a reader
can act on; the reference file already owns those routes. Rewriting `build.md` and both
`SKILL.md` route lists by reference file instead of by milestone exposed a real gap: both lists
stopped at four packages while `build.py` validates five, so `vanilla-non-card-overrides.md`
was never named as a build-validated family. Table status cells like `M6.7 batch development`
became `source development`.

**Removed: milestone ids standing in for the artifact that owns a contract.** `spec.md` said
"M7.4 owns the durable `DESIGN.md`" when the durable fact is that the `design.md` stage owns it.
Six such sentences now name the file. Section headings lost their numbering
(`## Compact M7.3 planning pass` → `## Compact planning pass`), with the one cross-reference to
a renamed heading updated in the same pass.

**The most consequential find was not bookkeeping at all.** Six reference pages instructed the
reader to run reduced checks "during the M6.7 batch window" and defer real-host verification to
"consolidated M6.7 closure". That window was a temporary human-lead-approved exception that
closed on 2026-08-04. A reader following the shipped pack was therefore following an expired
verification policy that authorized skipping exactly the real-host proof the current rules
require. Each was rewritten to the durable rule underneath: a manifest test and a successful
compile establish the manifest and the build, and nothing else — behavior and presentation are
proved only in the nearest real host.

Three example operation ids also carried milestone numbering into code an author copies
(`"m671-card-strike-ironclad"`, `"m673-ancient-overrides"`, `"m675-relic-akabeko-turn-rule"`).
The pages state these ids are the Mod's own choice, so a generated Mod was inheriting our
release history in its operation names; they now describe their target.

**Six tests pinned the removed wording** and were updated to assert the rule instead of the
sentence, per the existing standard that a phrase is pinned only when it is itself a
compatibility or output contract — a milestone number is not. For example the Intent boundary is
now pinned as "no Intent authoring recipe exists" plus "Do not adapt this Relic/Power recipe to
Intent" rather than "Intent authoring is not scheduled".

`test_surface_cross_check.py` guards the two removed classes: no milestone id in a heading, and
no expired-process instruction (`batch window`, `consolidated M6.7`, `At closure,`). It found a
seventh occurrence the manual sweep had missed, in `vanilla-overrides.md`. Both cases verified
to fail by mutation.

Result: ~190 occurrences down to 45, and every one that remains is a manifest key, a Tier 2
marker, a version boundary, or an evidence attribution.

## Change 5: consolidate hardening rules

The approved change named one symptom: "never misreport a Tier" was written in `SKILL.md`,
`verify.md`, and `repair.md` with wording that did not match. Reading for the pattern rather
than the instance found seven more rules in the same shape, and one design flaw in the fix as
specified.

**The flaw, which had to be corrected before the change was safe.** The pack is built on lazy
loading — `SKILL.md` says to read each stage file "only when you reach that stage". Under that
rule, moving a rule out of `verify.md` into `invariants.md` and leaving a pointer makes the rule
*weaker*: a run that reads `verify.md` and not `invariants.md` then has zero copies of it.
Drifting wording still states a rule three times; a dangling pointer states it none. So
`invariants.md` is the one page registered as read at pipeline start and kept in context, which
is what makes a stage pointer safe to follow. This is a deviation from the plain reading of
change 5 and is recorded as one.

**What qualified as an invariant.** Three tests, all of which had to hold: the rule fires at two
or more stages, violating it produces a false or ungrounded *product* rather than a suboptimal
technique, and it is currently restated or is load-bearing across stages. Eight qualified:
tier honesty (`INV-1`), observed reality over the artifact (`INV-2`), an ungrounded route is a
gap not a guess (`INV-3`), no manufactured evidence for a claim only observation settles
(`INV-4`), stop at a visible substitution (`INV-5`), preserve what the user settled (`INV-6`),
stay inside the pinned framework boundary (`INV-7`), and never edit the installed pack from
inside a run (`INV-8`).

What did **not** qualify is the more useful half of the result. The repair loop's "max 3
attempts, change the hypothesis after two failures" fires at exactly one stage, so it stayed in
`repair.md`; consolidating it would have moved a rule away from the only place it applies. The
art-route consent boundary is likewise author-only. `build.md`'s list of what `build.py`
validates reads like a restatement of `INV-7` but is a description of mechanical enforcement,
not a second copy of the rule, and was left alone.

**What each stage kept.** The same principle change 3 established: the rule has one home, and
the firing point keeps what is specific to it. `repair.md` keeps its per-stage re-verify signals
(`build 0/0`; marker greppable; effect observed) and drops the general sentence. `author.md`
keeps "an invented Cmd is the #1 way the repair loop burns its attempts", because the concrete
noun and its consequence are author-specific. `verify.md`'s headed-acceptance subsections keep
"an unrun structured harness remains an exception, never a pass" — an initial draft compressed
those to a bare `INV-1` tag, which went too far: that clause is specific to a reserved headed
review, and `AGENTS.md` requires exact wording for how a Tier result is reported.

**Enforcement.** `test_invariants.py` holds both sides of the contract: every `INV-n` reference
resolves to a defined rule, every defined rule is named by at least one stage (an invariant
nobody points at is one the pipeline never reaches), eight canonical phrasings appear in exactly
one file, the specific removed restatements stay removed, and `SKILL.md` still registers the page
as eagerly loaded. All five checks were verified to fail by mutation rather than assumed: a
re-added "Be honest about the tier." in `verify.md`, a dangling `INV-9`, a demotion of the page
to lazy loading, a renamed heading, and a stripped reference each produce the matching failure.

`skill_prose.py` gained `invariants.md` in every stage corpus, which is the same move the helper
was written for — it exists so a test pins a *rule* without pinning which file holds it. Five
assertions in four existing tests were repointed from the removed wording to the rule, and one
was not: `test_vanilla_overrides.py` pins "base-description replacement" across seven files as a
cross-file contract, and my rewrite had dropped the phrase from `SKILL.md`. That test was right
and the source was fixed.

## Verification

`256/256` focused tool tests pass. Test count before the surface work: `222/222`; after it,
`231/231`; change 2 adds 13 art-contract catalog cases and two Character grammar cases; change
3 adds two pointer/duplication cases; change 4 adds one history-in-runtime guard; change 5 adds
seven invariant cases.

What that does and does not establish:

- It establishes that the shipped prose no longer contradicts itself on the checked properties,
  that every dedup pointer resolves, and that the mandatory field/case pairs hold.
- It does not establish that any of the nine surfaces generates a working Mod. Only Card has a
  real authoring run behind it. The other nine are co-located and cross-checked, never piloted.
- No game launch, Tier 1, Tier 2, or headed review ran for this step, and none is required: the
  changes are documentation and prose-contract tests that cannot affect generated runtime
  behavior or presentation. The packaging fix earlier in this Package did affect runtime and has
  its own Windows log evidence.
- Open mismatches 1 and 7 are live contradictions in the shipped pack, recorded and unfixed.

For change 2 specifically:

- The catalog was verified repeatable — two consecutive exports produced byte-identical files —
  and `export-contract --check` agrees with the committed copy.
- Both drift directions were verified by mutation rather than assumed: a size changed in code
  with no re-export fails, and a catalog re-exported without a prose update fails. A lock that
  has never been observed failing is not known to be a lock. The Character-grammar locks were
  checked the same way — a wrong HP number, a misspelled relic id, and a deleted relic-effect
  caveat each fail.
- The five Starter relic **effects** remain unproved and unstated. The catalog cannot ground
  them, and no game was launched to observe them, so the page names the relics and explicitly
  forbids describing their behavior. Anyone later adding those effects owes a checked source.

For change 4:

- The classification was mechanical and re-run after every batch, so "no bookkeeping remains"
  is a measured statement rather than an impression. An early version of the classifier missed
  the lowercase manifest keys entirely because its gate was uppercase-only; that was caught
  before any edit, which is why the load-bearing ids were never at risk.
- Every replacement asserted an exact single occurrence before writing, so no edit silently hit
  a second site.
- It changes shipped prose only. No route, contract value, or runtime behavior moved, so no game
  run was required. The rewritten verification paragraphs *tighten* what the pack claims — they
  remove permission to defer real-host proof — and none of them weakens a rule.
- It does not re-verify anything the removed batch-window text had deferred. Those paths remain
  as recorded in the M6.7 result: unrun exceptions, not passes.
- The 45 remaining occurrences were reviewed individually, not sampled.

For change 5:

- All five enforcement checks were verified to fail by mutation. A lock never observed failing is
  not known to be a lock, and the eager-load registration in particular is the check the whole
  design rests on.
- It does not establish that a run actually obeys an invariant it reaches only through a pointer.
  The registration is checked; the behavior is not observed. That is the one thing change 5 trades
  away relative to the drifting-wording status quo, and it is the reason the page is eagerly
  loaded rather than lazily.
- The single-definition check covers eight canonical phrasings, not every sentence. A ninth
  restatement of an invariant could still be added elsewhere without failing a test.
- Eagerly loading a page costs context on every run, including a trivial resume that reads one
  stage. A full pipeline previously paid for these rules across several files, so the trade is
  expected to be favorable, but it was not measured.
- Two rules were deliberately left un-consolidated (the repair attempt cap, the art-consent
  boundary) because each fires at one stage. Change 5 is not "every hardening rule in one file".
- One prose credit was dropped rather than relocated: `repair.md` attributed its debugging
  discipline to `godogen`, which appears nowhere else in the shipped pack and is maintainer
  research in `documents/BASELINE_RESEARCH.md`. The rule survives as `INV-2`; the credit was
  narrative, not a version-bound evidence attribution of the kind change 4 preserved.
- `games/sts2/skills/modmaker/quirks.md` was briefly reverted mid-task by a `git checkout` on a
  file holding uncommitted change-3 work, and was restored from context: the `errors.md` boundary
  paragraph, the `CS8602`-free nullable rule, and the `MSB1008`-free toolchain rule. Verified by
  diffing against the committed version, which shows only those three regions plus the `INV-8`
  reference, and by `test_surface_cross_check.py`'s existing guard that both error codes stay out
  of that file.

For change 3:

- Every fact removed from a main path was checked to have a home in `errors.md` before the
  removal, mechanically, across all 21 moved diagnostics. None was dropped.
- The moved text is reorganized shipped prose, not new claims. No diagnostic gained or lost
  grounding, and no runtime behavior changed, so no game run was required.
- It does not establish that any cataloged fix works. `errors.md` entries carry the grounding
  they had before this change; relocating a diagnostic neither proves nor weakens it.
- The console entry is new prose, built from `quirks.md`'s existing grounded dev-console facts
  (`ModManager.IsRunningModded()`, the key list, `relic add` uppercased `Contains` matching).
  Its `Unable to create` signature was not reproduced in a live run.
- `gen_sprite.py`'s normalization behavior is unchanged. Change 2 adds a subcommand and rewords
  two diagnostic strings, so no generated-Mod behavior or presentation moved and nothing needed
  re-proving in a real host. Mismatch 12's fix changes what the tool *prints*, not what it
  writes: no existing correct sheet becomes invalid.
- It does not establish that any size is correct in-game. Sizes remain grounded by the headed
  runs already recorded in `art-contract.md`; these tests only hold the copies together.
- The cue grid was proved contradictory by reading code and prose against each other, not by a
  game run. No cue bundle was regenerated or re-observed, so `Dead` remains proved only by the
  2026-07-27 Meridian record.

## Documents synchronized

Facts changed, so these were edited:

- `AGENTS.md` — M8 status carried from "has not started" through in-progress to closed, plus the
  co-location state, the three open mismatches, the instruction to read the cross-check
  record before treating a surface page as validated, and the M8.1-selectable handoff.
- `documents/IMPLEMENTATION_PLAN.md` — Progress records all five changes plus payload
  regeneration; the recorded-weakening paragraph reflects that one enforcement gap is
  partly closed and states what the automated check proved. At closure: the Status section, both
  Package Plan rows, M8.2's inherited mismatches, and the start-protocol step that used to point
  at M8.0's contract. That contract is retained as a closed record with an explicit
  do-not-re-execute note, since its found-mismatch reasoning is what a later Package needs.
- `games/sts2/tests/README.md` — records what `test_surface_cross_check.py` owns and what it
  cannot establish, and for change 2 what `test_art_contract_catalog.py` owns, why the
  `consumer` column is deliberately not compared, and the Character starter-table case.
- `documents/history/README.md` — new M8 Results section indexing this file.
- `games/sts2/tests/m80-surface-cross-check.md` — mismatches 12 and 13 and the corrected totals
  (thirteen found, ten fixed, three open), plus the two new axes: prose against code, and prose
  against the same rule stated in another file.
- `games/sts2/skills/sts2-api/reference/art-contract.md` — the "keep them in sync" instruction
  replaced by the catalog route and the test that enforces it; the cue table labeled
  `cols x rows` with source sizes added.
- `games/sts2/skills/sts2-api/reference/character-presentation.md` and
  `reference/character-combat-cues.md` — catalog route added; the cue table's column order
  labeled.
- `games/sts2/skills/sts2-api/design/character-foundation.md` — `HP` and `Starter relic`
  columns, the native HP range and Gold constant, and the relic-effect grounding limit.
- `games/sts2/skills/sts2-api/errors.md` — four new Build And Profile signatures, one new
  Verification console signature, and boundary discrimination merged into four Behavior entries.
- `games/sts2/skills/modmaker/build.md`, `verify.md`, `repair.md` — diagnostic scars replaced by
  resolving catalog pointers; the tier-1/tier-2 verdict logic and the repair loop kept.
- `games/sts2/skills/modmaker/quirks.md` — the when-you-need-it split stated as the rule, and
  the two error codes `errors.md` owns removed from its preventive entries.
- `games/sts2/tools/tests/test_surface_cross_check.py` — `errors.md` pointer resolution, the
  no-rival-list check, and change 4's history-in-runtime guard.
- 22 shipped pack pages across `modmaker/` and `sts2-api/` — change 4's bookkeeping,
  artifact-ownership, heading, example-id, and expired-verification-policy rewrites.
- `test_semantic_contract.py`, `test_m71_routing.py`, `test_m72_native_grammar.py`,
  `test_m73_design_planning.py` — six assertions repointed from milestone wording to the rule
  each sentence carries.
- `games/sts2/skills/modmaker/invariants.md` — new: `INV-1` through `INV-8`, the one home for
  the rules that fire at every stage.
- `games/sts2/skills/modmaker/SKILL.md` — `invariants.md` registered in the stage table as read
  at pipeline start and kept in context, added to pipeline step 0, and the observed-reality
  section reduced to the two-tier definition plus `INV-1`/`INV-2`.
- `games/sts2/skills/modmaker/route.md`, `interview.md`, `design.md`, `spec.md`, `scaffold.md`,
  `author.md`, `verify.md`, `repair.md`, `quirks.md` — general restatements replaced by the
  named invariant; each kept its own stage-specific detail.
- `games/sts2/tools/tests/test_invariants.py` — new: reference resolution, orphan detection,
  single-definition, removed-restatement, and eager-load-registration checks.
- `games/sts2/tools/tests/skill_prose.py` — `invariants.md` added to every stage corpus, plus
  `with_invariants()` for the stages that have no surface dispatch.
- `test_m71_routing.py`, `test_m73_design_planning.py`, `test_m74_scope_traceability.py` — five
  assertions repointed from change 5's removed wording to the rule.

## Documents reviewed and left unchanged

- `README.md` — no file-layout or milestone-status claim to correct.
- `documents/PROJECT.md` — its `surfaces` matches are M7.5 expression surfaces and multiplayer
  wording, unrelated to the file layout; it owns release state, which did not change.
- `documents/BASELINE_RESEARCH.md` — baseline roles unchanged.
- `games/sts2/tests/content-capability-graph.md` — the active runtime support graph is
  unchanged. No surface gained or lost support; the new proof cases are obligations on surfaces
  already supported. Its one `surfaces` match is M7.5 expression surfaces.

Re-checked for change 5 specifically: none of the four names an invariant, a hardening rule, or
the stage files that changed, and change 5 moved no support row, route, or contract value. The
`documents/history/README.md` index entry for this file needed no edit, since the file it points
at is the same one.

## Payload synchronization

Both committed payloads were regenerated from source on 2026-08-10 with `publish.sh --plugin`
and `--portable`, after change 5. Each carries 38 modmaker files (24 source pages plus the 14
bundled Python tools) and 145 sts2-api files.

Checked: `invariants.md` is present in both, all eight `INV-n` ids resolve in both, `SKILL.md`
retains the eager-load registration in both, change 2's art-contract catalog is present, change
3's removed `## Failure classes` stays removed, and change 4's expired batch-window instruction
appears nowhere. The two payloads' modmaker trees are identical to each other. Rendering is
repeatable: two consecutive `--plugin` renders produced byte-identical trees.

No unrendered `${VAR}` placeholder survives in either payload. Three `baselines/` matches were
reviewed and left: `build.md`'s "grounded baselines/routes" is the unrelated sense of the word,
while `grounding.md` and `character-foundation.md` attribute a maintainer research checkout and
each state in the same breath that it is not a runtime or authoring source — the attribution side
of the pack/maintainer split, not an instruction to a user's runtime.

Not established: no payload was installed and run. The checks above are structural, and the last
observed installed-plugin behavior remains the M6.7 closure record.

## What this Package did not finish

Open mismatches 1, 7, and the second half of 8 are deferred to M8.2 by human-lead decision on
2026-08-10. Mismatch 1 is a contract-version migration that overlaps M8.2's recorded ownership of
whether a grammar gap or a capability promotion is the right answer; doing the envelope decision
twice was the rejected alternative. Mismatch 7 travels with it, because where the character
resource and ordered-buffer envelopes land depends on the envelope form M8.2 selects. Mismatch 8's
remaining half — nothing checks a *generated* project's `SPEC.md` against its surface envelope —
cannot be built before there is one envelope schema to check against. All three remain live
contradictions in the shipped pack until then, recorded in
`games/sts2/tests/m80-surface-cross-check.md`.

Nine of the ten co-located surfaces have no authoring run behind them. The Card pilot is the only
one, and the pilot's second finding names the per-surface identity mechanic each of the other nine
still owes a proof for. Co-located and cross-checked is not piloted.

Also carried forward, unscheduled: grounding the five native Starter relic effects. The pinned
catalog has no effect text, so `character-foundation.md` names them and forbids describing their
behavior. Adding the effects needs a checked source — the current game, or a reviewed decompile
route — not recall.

Nothing here authorizes a fresh acceptance Mod, a payload publication, or a release.

