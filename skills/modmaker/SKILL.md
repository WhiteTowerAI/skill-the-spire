---
name: modmaker
display_name: STS2 Mod Maker
short_description: Turn one sentence into a working Slay the Spire 2 mod
default_prompt: "Use /modmaker to build a Slay the Spire 2 mod from a natural-language description."
description: |
  Build a working Slay the Spire 2 mod from a one-sentence natural-language
  description. Use when the user wants Claude to create, generate, or
  build an STS2 mod (a relic, card, potion, or similar element) end to end —
  scaffold, author, build, and verify it loads in-game.
---

# STS2 Mod Maker — Orchestrator

Turn a non-programmer's one-sentence idea into an STS2 mod that actually loads
and runs in-game. You drive a staged pipeline; each stage is a separate file you
read **only when you reach it** — this keeps context small.

## Scope right now — core elements; Character Foundation; scenario-verified resource/UI and zone/dynamic capabilities; interaction-aware two-tier verify

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
An **event** is a normal map event with nested pages/options, authored as one
`CustomEventModel` and proven through the **`MapNode`** scenario (enter the event room,
read its localized option, click it, and observe the run-state consequence). Its normal
initial portrait can be generated as one 3440×1613 loose PNG with an existence-checked
vanilla fallback. Phobia/later-page portraits, VFX, and custom/Ancient scenes remain out.
A **Character Foundation** uses the Alchyr character template plus BaseLib's
`PlaceholderCharacterModel`. It appears in the real character-select UI, starts a run
with valid card/relic/potion pools and exact starter deck/relic, and proves HP, standard
3 energy, and one public/BaseLib starter mechanic through `RunStart` + `CombatPlayer`.
The constructor already registers the character; generated code never calls
`AddCharacter`. Custom character art/animation remains outside this Foundation boundary.
The **6c capability kernel** is separately scenario-verified as maintainer infrastructure:
combat-scoped state, deterministic typed hooks, descriptor-based fallback UI, and one
version/MVID-gated B-risk combat-UI postfix. It is not a user-facing mechanic by itself.
Two **advanced capability contracts are pipeline-supported through the corrected Wayfinder
acceptance**: a combat-owned
nonnegative resource with explicit gain/affordability/all-or-nothing spend/reset plus a
generic live counter, and a bounded ordered semantic buffer whose source cards use native
Discard while its snapshot creates a deterministic per-instance output card. Route only
to `reference/character-resource.md` and `reference/ordered-card-buffer.md`; resource UI may
select the exact 6c combat-UI adapter. Retaining played cards in a `CustomPile` is not
supported. Do not invent alternative-energy patches, zone UI, persistence, C/D access, or
`OpenMod.Runtime`.
Multi-element mods record real content nodes plus directed **interactions**; tier-2 drives
the source by its actual type and checks the dependent observation, so a card→power link
cannot pass merely because both models loaded. “Combo” is not a content type.
Two core **stateful relic** families are pipeline-supported: Happy Flower-style counters
cross combats and save/resume through `[SavedProperty]`, while Stone Calendar-style timing
reads the current combat's `TurnNumber`. Tier-2 proves `N-1`, threshold, reset/carry-over,
and the save round trip where applicable. Turn-local event counts, once-per-combat flags,
previous-turn memory, and limited run uses have grounded patterns but remain provisional
until their scenario canaries. A counter is state on its real element, not a new element
  type. **Custom static art** is now wired and live-verified for **eight specs — card
  portraits, relic icons, power icons, potion icons, enchantment icons, orb icons, static monster bodies, and normal-event
  initial portraits** (each a loose PNG the game loads directly; no `.tres` atlas authoring)
  — orb support is icon-only and retains its explicit vanilla Spine scene/channel-SFX
  fallbacks. The
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
*Editing existing* vanilla content is still out; the verified 6c lifecycle bridge is not
a general vanilla-editing recipe.
If a request needs what isn't wired, say so plainly rather than half-doing it.

## Stage files

Read each from `./` only when you reach that stage.

| File | Purpose | When to read |
|------|---------|--------------|
| `interview.md` | One short clarifying round → intake | Pipeline start (after resume check) |
| `spec.md` | Write `SPEC.md` (the design contract) | After interview |
| `scaffold.md` | `dotnet new` + manifest + PckPacker wiring | After spec |
| `author.md` | Write the C# element + localization + marker | After scaffold |
| `build.md` | `dotnet build` → .dll/.pck/.json into mods/ | After author |
| `verify.md` | Launch + log-assert load (tier-1) + automated tier-2 self-test (manual fallback) | After build |
| `repair.md` | Bounded diagnose → fix → re-verify sub-loop | Whenever build/verify fails |
| `quirks.md` | STS2/BaseLib gotchas | Before writing any C# |
| *(sts2-api skill)* | Recipes, command APIs, error fixes | Whenever you need a concrete STS2 answer |

## Pipeline

```text
User: one sentence ("a relic that ...")
    |
 0. RESUME CHECK — if SPEC.md / PLAN.md exist in the work dir, read them and skip
    to the first unfinished stage. Files are state; do not restart from scratch.
    |
 1. INTERVIEW (interview.md) — ONE short round, only for genuinely ambiguous
    things (element type? rarity? exact trigger?). Non-blocking defaults for the rest.
    |
 2. SPEC (spec.md) — write SPEC.md: element type, name, type-specific host/starter contract, trigger, effect
    in game terms, any state event/threshold/lifetime/reset/persistence, and art plan.
    Show the user a plain-language summary to confirm.
    |
 3. SCAFFOLD (scaffold.md) — dotnet new from the Alchyr template (once), set the
    manifest, uncomment PckPacker.
    |
 4. AUTHOR (author.md) — query the sts2-api pack, pick the recipe (relic/potion/card,
    monster+encounter/event/character, plus power.md if the effect needs a custom buff/debuff),
    write the Custom*Model
    subclass filling ONLY the effect logic, add localization JSON, inject the load +
    diagnostic [T2MOD-SELFTEST] markers, and emit the arg-gated tier-2 self-test harness
    (SelfTest.cs, step 2.5 — reference/selftest-harness.md). Then the ART sub-step
    (author.md §4): per SPEC's art plan, leave placeholder (default) or generate a
    custom source through the selected route and pass it to tools/gen_sprite.py import. Art never
    blocks —
    a missing sprite falls back to the template default. Regenerate = re-run + rebuild.
    |
 5. BUILD (build.md) — tools/build.py → .dll/.pck/.json into mods/ (the .pck rebuild is
    what makes any custom art reach the game). On failure: go to REPAIR (repair.md).
    |
 6. VERIFY (verify.md) — launch via steam_appid.txt, grep godot.log for the marker
    and fresh-run error blocks (tier-1). Then run the tier-2 self-test unattended
    (launch.py --self-test → the harness drives the required combat/event/run-start scenario and
    asserts concrete post-state → grep its structured state proof). Fall back to the manual dev-console guide
    only if the harness can't reach its scenario. Never claim the effect is verified when
    only load was. On failure: go to REPAIR (repair.md).
    |
 7. FINALIZE — summarize what was built, where the artifacts are, and which tier
    of verification was reached.
    |
 8. REPAIR (repair.md) — shared sub-loop invoked by 5/6: read the real error,
    consult sts2-api errors.md, apply ONE fix, re-run only the failed stage.
    Bounded (max 3 attempts; stop if the same signature survives a fix). On
    convergence, resume the pipeline; on exhaustion, hand back a clear failure.
```

## Files are state (resume after compaction)

Keep important state in files in the work dir so the pipeline survives long
threads and context compaction:

- **SPEC.md** — the design contract (element, name, rarity, trigger, effect, state
  lifetime/reset/persistence when applicable, art).
- **PLAN.md** — stage checklist + status; update after each stage.
- **MEMORY.md** — discoveries, chosen ids, derived loc keys, what worked/failed.

**Resume-check first**: if these exist, continue from the artifacts, not from
conversational memory.

## Verify on observed reality, never "it compiled"

A green build is not success. The mod must **load** (tier-1: log marker greppable,
no fresh-run errors) and its **effect must fire** (tier-2: driven automatically by the
in-process self-test harness, then independently state-asserted — no human triggering). Report
exactly which tier was reached; a harness that couldn't reach its scenario is tier-1, not a
tier-2 failure of the mod. See `verify.md`.

## When you need a concrete STS2 answer

Use the **sts2-api** skill (`.`) with a targeted query rather
than guessing an API — e.g. "relic: combat-start hook signature and energy Cmd",
or "errors.md: no .pck produced". Do not load the whole pack into context.
