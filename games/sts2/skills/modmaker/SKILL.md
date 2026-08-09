---
name: modmaker
description: |
  Build a working Slay the Spire 2 mod from a one-sentence natural-language
  description. Use when the user wants ${AGENT_NAME} to create, generate, or
  build an STS2 mod (a relic, card, potion, or similar element) end to end —
  scaffold, author, build, and verify it loads in-game.
---

# STS2 Mod Maker — Orchestrator

Routing loads only the relevant STS2-native design grammar and planning reference before
creative questions. Character Foundation uses
`sts2-api/design/character-foundation.md`; unresolved mechanics, content ecosystems, and
numeric/economy questions route independently to `design/mechanic-planning.md`,
`design/content-set-planning.md`, and `design/balance-planning.md`. They separate pinned
facts, observed conventions, creative decisions, and open hypotheses while preserving the
simple exact-content fast path. They change authoring guidance, not runtime support.

When a design has multiple intentional expressive surfaces, explicitly requests theme,
narrative, or presentation, or revises an identity anchor, routing also loads
`sts2-api/design/coherence-review.md`. It checks mechanics, naming, localization, visuals,
Event text, and Character identity against accepted design decisions and creates a bounded
impact/re-evaluation queue for revisions. It does not add runtime capabilities or turn a
placeholder into an invented visual identity.

Every route now writes an adaptive `DESIGN.md` through `design.md` before semantic SPEC.
Its current/future scope ledger uses stable design and operation IDs; `design_trace.py`
fails closed when current requirements lack SPEC operations, future items enter SPEC, or a
generated operation lacks a current design source and supported semantic route.
`coherence_trace.py` validates the proportional identity anchors, selected surface checks,
resolved conflict state, and revision impact queue before SPEC.

Turn a non-programmer's one-sentence idea into an STS2 mod that actually loads
and runs in-game. You drive a staged pipeline; each stage is a separate file you
read **only when you reach it** — this keeps context small.

## Scope right now — core elements; Character Foundation; RitsuLib resource/UI and ordered semantic buffer; interaction-aware two-tier verify

This skill turns one sentence into a known-good **relic, potion, card, enemy encounter,
World Node/event, or minimal playable character Foundation** end to end, including custom card keywords, card enchantments,
and custom orbs when the concept needs reusable vocabulary, a persistent Card
modification, or an orb passive/evoke mechanic. It verifies the mod **loads** (tier-1)
AND that its **effect actually fires** (tier-2, now
automated by an in-process self-test harness — no dev-console typing), and when a stage
fails runs the **bounded automated repair loop** (`repair.md`) to diagnose → fix →
re-verify within a hard retry cap. A **custom power** (buff/debuff) is supported too,
usually as the dependency of a card/relic that applies it. An **enemy encounter** is a
custom monster + the encounter that spawns it, authored as one vertical slice and proven
through the **`CombatEnemy`** scenario (enter the encounter, confirm the monster, end the
turns needed to traverse its declared cycle/branches, and assert move history plus exact
player/monster HP, Block, Power, debuff, and multi-hit state). Grounded move vocabulary
includes self buff/custom Power with a downstream consequence, player debuff, block/heal,
multi-attack, composite actions, deterministic cycles, and conditional branches. One
checked 360×360 static monster body is supported in combat and bestiary, with an explicit
built-in fallback when absent. Spine and move animation are later extensions.
An **event** is a normal map event with nested pages/options, authored as one semantic
Event and proven through the **`MapNode`** scenario (enter the event room,
read its localized options, drive every independent SPEC outcome, and observe exact state,
page, overlay, combat, and map results). Supported outcomes include public Cmd
combinations, conditional/locked multi-page choices, blocking card-selection and custom-
reward overlays, plus one resumable or terminal special combat per mutable Event instance.
Special combat may carry extra rewards and always uses an explicit resume-vs-map branch;
direct merchant/rest/treasure room transitions remain unsupported. Its normal
initial portrait and explicitly authored later-page portraits can be generated as
3440×1613 loose PNGs. Initial art has an existence-checked vanilla fallback; missing page
art retains the current portrait. Normal-layout Events may also emit the one live-verified
code-native `portrait_halo` VFX profile with Fast Mode handling and explicit cleanup across
page, portrait, combat, and finish transitions. Page and option descriptions may also use
the live-verified bounded vanilla Event rich-text vocabulary (emphasis, semantic colors,
`jitter`, and `sine`) through the native label, with no generated VFX node. Custom phobia
art, arbitrary VFX, and custom/Ancient scenes remain out. Normal Events also support native
Card/relic acquisition presentation, one preference-respecting `weak_short` screen shake,
and the curated built-in `trial_noble` VFX at its vanilla host/placement with explicit
cleanup.
One additional bounded Event composition is implemented: a solo custom Quest Card
may force one custom Event from an Unknown MapPoint in one specified act. The target stays
out of ordinary Event pools and one named option completes/removes the token. This public-
hook path does not authorize arbitrary chains, vanilla edits, multiplayer semantics, or a
new save-roundtrip claim.
A **Character Foundation** uses the selected framework adapter's character template. It
appears in the real character-select UI, starts a run
with valid card/relic/potion pools and exact starter deck/relic, and proves HP, standard
3 energy, and one grounded public starter mechanic through `RunStart` + `CombatPlayer`.
The adapter owns exactly-once registration. Static presentation is a separate opt-in layer
with nine promoted profiles: selection portrait/background, top-panel icon, non-Spine
combat/rest/merchant bodies, five-layer energy, and distinct 256x256 large/24x24 rich-text
Energy icons. The Character-wide color/frame contract is also implemented.
Deterministic top-icon and generated-Relic outlines are implemented. A separate
bounded non-Spine combat layer supports private `Idle`/`Attack`/`Hit`/`Dead` frame
sequences with one shared geometry and an all-or-nothing static fallback. Locked selection,
map marker, custom Ancient models/layouts, `Cast`, Spine, trails, audio, and broader
animation retain explicit boundaries. Character-specific dialogue in the nine cataloged
native Ancient/Architect scenes is a separate localization-only capability: it preserves
native scenes/options/rewards/progression and uses RitsuLib's registered population patch.
Read `reference/ancient-dialogue.md`; do not generate Harmony/reflection injection.
Read `reference/character-presentation.md` and `reference/character-combat-cues.md` for
their respective visual layers.
Two **advanced capability contracts are implemented with RitsuLib**:
a combat-owned nonnegative resource using `SecondaryResourceCmd` with explicit
gain/affordability/all-or-nothing spend/reset plus public `RegisterCombatUi`, and a bounded
ordered semantic buffer using combat-attached semantic values while source Cards use native
Play -> Discard. The fixed 220x32 icon+text control keeps a text-only fallback and a 160px
offset from native Energy. Route only to `reference/character-resource.md` and
`reference/ordered-card-buffer.md`. Retaining played Cards in a `CustomPile` is unsupported.
Do not invent alternative-energy patches, zone UI, persistence, C/D access, or
`OpenMod.Runtime`.
The **Scry helper** is also implemented for a Card that inspects the top X Draw
cards and discards any number. It is generated-Mod-local, uses the native visible selector
and discard lifecycle, returns a structured result, and is explicitly singleplayer-only.
Route it only to `reference/scry-helper.md`; do not add BaseLib, global Scry hooks, or a
multiplayer fallback.
The bounded **advanced targeting** route supports deterministic filtered live-creature
targets for single-target Cards, single-target Potions, and multi-target Cards. It keeps
native mouse/controller selection, execution-time validation, payment/Potion retention,
and normal Card result piles. Route it only to `reference/advanced-targeting.md`.
Multi-target Potions have a pinned lifecycle limitation because queued empty-target
execution cannot cancel before consumption; do not generate a patch or restore the Potion.
The implemented **Relic-owned Rest Site option** route is singleplayer-only and bounded to
free or fixed Gold cost plus one deterministic preflightable outcome. It distinguishes
absence from native disabled state, rechecks payment at selection time, supports once per
Rest Site or once per run, and may preserve the other native options once. Route it only
to `reference/rest-site-options.md`. Card/Modifier owners, arbitrary transactions,
same-site repeat, and multiplayer remain unsupported until separate proof.
Multi-element mods record real content nodes plus directed **interactions**; tier-2 drives
the source by its actual type and checks the dependent observation, so a card→power link
cannot pass merely because both models loaded. “Combo” is not a content type.
Two core **stateful relic** families are implemented: Happy Flower-style counters
cross combats and save/resume through `SavedAttachedState<SpecificRelic,int/bool>`, while
Stone Calendar-style timing
reads the current combat's `TurnNumber`. Tier-2 proves `N-1`, threshold, reset/carry-over,
and the save round trip where applicable. Turn-local event counts, once-per-combat flags,
previous-turn memory, and limited run uses have grounded patterns but remain provisional
until their scenario canaries. A counter is state on its real element, not a new element
  type. **Custom static art** is now wired and live-verified for the established **eight specs — card
  portraits, relic icons, power icons, potion icons, enchantment icons, orb icons, static monster bodies, and normal-event
  initial/page portrait slots** (each a loose PNG the game loads directly; no `.tres` atlas authoring)
  plus nine Character static profiles: selection portrait/background, top-panel icon, static
  non-Spine combat/rest/merchant bodies, five-layer full energy, and distinct large/text
  Energy icons, and the optional bounded four-action Character combat-cue bundle.
  Orb support is icon-only and retains its explicit vanilla Spine scene/channel-SFX
  fallbacks. Locked Character selection and map-marker normalizers are grounded but not
  promoted; see `reference/character-presentation.md`. The
user picks placeholder (default, fast) or custom art. When the current agent runtime
actually exposes a host-native raster image tool, prefer that route (Codex calls it
`image_gen` and its built-in mode needs no `OPENAI_API_KEY`); otherwise use an already-
authenticated Vofy CLI, a bring-your-own HTTP backend, or a local image. Do not infer
native image capability from the text-model name or from an installed instruction file:
the tool itself must be callable. All custom routes converge on the `tools/gen_sprite.py`
normalization contract; native-tool, Vofy, and local-file outputs call its `import`
command. See `author.md` §4 and `sts2-api` → `reference/art-contract.md`. The
managed-credit route is live-verified through Vofy + an in-game `.pck` on Windows;
host-native tool availability is runtime-dependent, and macOS/Linux remains best-effort.
Requests against existing vanilla content are grounded on a checked `0.107.1` catalog, and
every new scaffold emits a semantic override manifest. Route existing content first to
`sts2-api/reference/vanilla-overrides.md`, then to the reference that owns the surface:

- a public visual surface — `reference/vanilla-visual-overrides.md` (44 providers);
- an exact existing Card's non-asset operations — `reference/vanilla-card-overrides.md`;
- an existing Ancient's initial options and page branches, by public append or the reviewed
  fixed replacement Adapter — `reference/vanilla-ancient-overrides.md`;
- pinned epoch gates and Card/Relic/Potion pool membership —
  `reference/vanilla-availability-overrides.md`;
- existing Relic/Potion/Power/Orb/Enchantment/Affliction/Monster/Encounter/ordinary Event
  data or behavior — `reference/vanilla-non-card-overrides.md`.

Other operations stop at their exact unpromoted boundary (INV-3, INV-7).

Vanilla Card base-description replacement is the case to recognize by name, because the
substitution looks harmless: when a user asks to replace, remove, or hide the original
description body, the pinned RitsuLib `0.5.4` route can only compose text **before or after**
it. That is a visible difference, so it is `INV-5` — explain it, stop before SPEC or scaffold,
and never downgrade `replace` to `compose` on your own.

A RitsuLib Package documented by the official tutorials is supported when its public API
exists in the pinned profile. If this shipped pack still lacks its SPEC block or recipe, that
is missing authoring work, not an unsupported API (INV-3).

## Stage files

Read each from `${MODMAKER_SKILL_DIR}/` only when you reach that stage. `invariants.md` is
the one exception: read it at pipeline start and keep it in context, because its rules
constrain every stage rather than one.

| File | Purpose | When to read |
|------|---------|--------------|
| `invariants.md` | The eight rules every stage obeys, stated once | Pipeline start; stays in context |
| `route.md` | Infer fast / co-design / revision and preserve settled decisions | Pipeline start (after state check) |
| `interview.md` | Resolve only material open decisions → intake | After routing when a decision is still open |
| `design.md` | Write adaptive `DESIGN.md`, current/future scope, coherence contract, and stable IDs | After Interview, or to backfill a pre-M7.4 project |
| `semantic-contract.md` | Framework-neutral SPEC envelope, adapter inputs, and diagnostic record | Before writing SPEC |
| `spec.md` | Write exact current `SPEC.md` plus validated coherence/design traces | After DESIGN |
| `scaffold.md` | Pinned RitsuLib project + manifest + compat wiring | After spec |
| `author.md` | Write the C# element + localization + marker | After scaffold |
| `build.md` | `dotnet build` → .dll/.pck/.json into mods/ | After author |
| `verify.md` | Launch + log-assert load (tier-1) + automated tier-2 self-test (manual fallback) | After build |
| `repair.md` | Bounded diagnose → fix → re-verify sub-loop | Whenever build/verify fails |
| `quirks.md` | STS2/selected-adapter gotchas | Before writing any C# |
| *(sts2-api skill)* | Recipes, command APIs, error fixes | Whenever you need a concrete STS2 answer |

## Pipeline

```text
User: one sentence ("a relic that ...")
    |
 0. STATE CHECK — read invariants.md, then DESIGN.md when present, then SPEC.md / PLAN.md / MEMORY.md.
    If the user requested no change, skip to the first unfinished stage. If they requested
    a change, preserve the existing artifacts and continue through the revision route.
    |
 1. ROUTE (route.md) — infer fast / co-design / revision and state it briefly. Do
    not ask the user to choose a workflow mode. Resume without an interview when no design
    change was requested.
    |
 2. INTERVIEW (interview.md) — resolve only material open decisions. Fast asks zero
    questions when complete and at most one compact round otherwise; co-design presents
    materially different player-facing options with trade-offs; revision discusses only
    the delta and never re-asks settled facts.
    |
 3. DESIGN (design.md) — write the adaptive durable intent, scope, and coherence artifact.
    Every current MUST/PLACEHOLDER receives stable design and operation IDs; DEFER and
    OUT-OF-SCOPE remain outside generation. Check only selected expressive surfaces against
    accepted identity anchors. On revision, record the ordered impact/re-evaluation queue.
    Stop while a blocking gap or coherence conflict is unresolved.
    |
 4. SPEC (semantic-contract.md + spec.md) — write a framework-neutral SPEC: element type,
    name, type-specific host/starter contract, trigger, effect in game terms, any state
    event/threshold/lifetime/reset/persistence, fallback, proof, art plan, and one supported
    semantic route per traced operation. Run design_trace.py, then show one combined
    DESIGN/current-slice/SPEC confirmation.
    |
 5. SCAFFOLD (scaffold.md) — resolve the selected framework/host profile once, then emit
    its project, manifest, and package wiring.
    |
 6. AUTHOR (author.md) — query the sts2-api pack, pick the recipe (relic/potion/card,
    monster+encounter/event/character, plus the selected Event outcome/VFX/rich-text/
    native-presentation/forced-follow-up/Scry references or power.md
    when selected by SPEC),
    translate the same semantic SPEC through the selected adapter, add localization,
    inject the shared framework/version and [T2MOD-SELFTEST] diagnostics, and emit the
    arg-gated tier-2 self-test harness
    (SelfTest.cs, step 2.5 — reference/selftest-harness.md). Then the ART sub-step
    (author.md §4): per SPEC's art plan, leave placeholder (default) or generate a
    custom source through the selected route and pass it to tools/gen_sprite.py import. Art never
    blocks —
    a missing sprite falls back to the template default. Regenerate = re-run + rebuild.
    |
 7. BUILD (build.md) — tools/build.py validates the pinned host/package/runtime profile,
    deploys the Mod's own DLL/manifest, and packs its resource tree when present. On
    failure: go to REPAIR (repair.md).
    |
 8. VERIFY (verify.md) — launch via steam_appid.txt, grep godot.log for the marker
    and fresh-run error blocks (tier-1). Then run the tier-2 self-test unattended
    (launch.py --self-test → the harness drives the required combat/event/run-start scenario and
    asserts concrete post-state → grep its structured state proof). Fall back to the manual dev-console guide
    only if the harness can't reach its scenario (INV-1). On failure: go to REPAIR (repair.md).
    |
 9. FINALIZE — summarize what was built, where the artifacts are, and which tier
    of verification was reached.
    |
10. REPAIR (repair.md) — shared sub-loop invoked by 7/8: read the real error,
    consult sts2-api errors.md, apply ONE fix, re-run only the failed stage.
    Bounded (max 3 attempts; stop if the same signature survives a fix). On
    convergence, resume the pipeline; on exhaustion, hand back a clear failure.
```

## Files are state (resume after compaction)

Keep important state in files in the work dir so the pipeline survives long
threads and context compaction:

- **DESIGN.md** — player intent, decisions, current/future scope, tuning hypotheses,
  coherence anchors/surface checks, revision impact queue, and accepted boundaries.
- **SPEC.md** — exact current generated operations, semantic behavior, supported routes,
  state lifetime/reset/persistence, presentation/fallback, and design trace.
- **PLAN.md** — stage checklist + status; update after each stage.
- **MEMORY.md** — discoveries, chosen ids, derived loc keys, and what worked/failed.

**State-check first**: if these exist, continue from the artifacts, not from
conversational memory. Read `DESIGN.md` first as authoritative creative/scope state. For a
pre-M7.4 unfinished project with SPEC but no DESIGN, use `design.md`'s compact backfill and
resume without a general interview.

## Verify on observed reality, never "it compiled"

`INV-1` and `INV-2` own this. What the two tiers concretely are: the mod must **load**
(tier-1: log marker greppable, no fresh-run errors) and its **effect must fire** (tier-2:
driven automatically by the in-process self-test harness, then independently state-asserted —
no human triggering). See `verify.md`.

## When you need a concrete STS2 answer

Use the **sts2-api** skill (`${STS2_API_SKILL_DIR}`) with a targeted query rather
than guessing an API — e.g. "relic: combat-start hook signature and energy Cmd",
or "errors.md: no .pck produced". Do not load the whole pack into context.
