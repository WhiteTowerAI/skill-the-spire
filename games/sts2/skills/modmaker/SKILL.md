---
name: modmaker
display_name: STS2 Mod Maker
short_description: Turn one sentence into a working Slay the Spire 2 mod
default_prompt: "Use /${MODMAKER_COMMAND} to build a Slay the Spire 2 mod from a natural-language description."
description: |
  Build a working Slay the Spire 2 mod from a one-sentence natural-language
  description. Use when the user wants ${AGENT_NAME} to create, generate, or
  build an STS2 mod (a relic, card, potion, or similar element) end to end —
  scaffold, author, build, and verify it loads in-game.
---

# STS2 Mod Maker — Orchestrator

Turn a non-programmer's one-sentence idea into an STS2 mod that actually loads
and runs in-game. You drive a staged pipeline; each stage is a separate file you
read **only when you reach it** — this keeps context small.

## Scope right now (M5 — relic + potion + card + combo, automated two-tier verify)

This skill turns one sentence into a known-good **relic, potion, or card** end to end,
verifies it **loads** (tier-1) AND that its **effect actually fires** (tier-2, now
automated by an in-process self-test harness — no dev-console typing), and when a stage
fails runs the **bounded automated repair loop** (`repair.md`) to diagnose → fix →
re-verify within a hard retry cap. A **custom power** (buff/debuff) is supported too,
usually as the dependency of a card/relic that applies it — and that card→power link is
checked as a **combo** by the tier-2 harness. **Custom art (M5.5)** is now wired and
live-verified for **card portraits, relic icons, and power icons** — the user picks
placeholder (default, fast) or generate via a bring-your-own image backend
(`tools/gen_sprite.py`; see `author.md` §4 and `sts2-api` → `reference/art-contract.md`).
Only potion art (a `.tres` atlas) is a separate pipeline, so it stays placeholder.
*Editing existing* vanilla content (needs Harmony patching, not a recipe) is still out.
If a request needs what isn't wired, say so plainly rather than half-doing it.

## Stage files

Read each from `${MODMAKER_SKILL_DIR}/` only when you reach that stage.

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
 2. SPEC (spec.md) — write SPEC.md: element type, name, rarity, trigger, effect
    in game terms, art plan. Show the user a plain-language summary to confirm.
    |
 3. SCAFFOLD (scaffold.md) — dotnet new from the Alchyr template (once), set the
    manifest, uncomment PckPacker.
    |
 4. AUTHOR (author.md) — query the sts2-api pack, pick the recipe (relic/potion/card,
    plus power.md if the effect needs a custom buff/debuff), write the Custom*Model
    subclass filling ONLY the effect logic, add localization JSON, inject both
    [T2MOD-SELFTEST] markers, and emit the arg-gated tier-2 self-test harness
    (SelfTest.cs, step 2.5 — reference/selftest-harness.md). Then the ART sub-step
    (author.md §4): per SPEC's art plan, leave placeholder (default) or generate a
    custom card portrait via tools/gen_sprite.py (BYO backend). Art never blocks —
    a missing sprite falls back to the template default. Regenerate = re-run + rebuild.
    |
 5. BUILD (build.md) — tools/build.py → .dll/.pck/.json into mods/ (the .pck rebuild is
    what makes any custom art reach the game). On failure: go to REPAIR (repair.md).
    |
 6. VERIFY (verify.md) — launch via steam_appid.txt, grep godot.log for the marker
    and mod-named errors (tier-1). Then run the tier-2 self-test unattended
    (launch.py --self-test → the harness drives itself into combat and fires the
    effect → grep the fired/used marker). Fall back to the manual dev-console guide
    only if the harness can't reach combat. Never claim the effect is verified when
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

- **SPEC.md** — the design contract (element, name, rarity, trigger, effect, art).
- **PLAN.md** — stage checklist + status; update after each stage.
- **MEMORY.md** — discoveries, chosen ids, derived loc keys, what worked/failed.

**Resume-check first**: if these exist, continue from the artifacts, not from
conversational memory.

## Verify on observed reality, never "it compiled"

A green build is not success. The mod must **load** (tier-1: log marker greppable,
no mod-named errors) and its **effect must fire** (tier-2: driven automatically by the
in-process self-test harness and grepped from the log — no human triggering). Report
exactly which tier was reached; a harness that couldn't reach combat is tier-1, not a
tier-2 failure of the mod. See `verify.md`.

## When you need a concrete STS2 answer

Use the **sts2-api** skill (`${STS2_API_SKILL_DIR}`) with a targeted query rather
than guessing an API — e.g. "relic: combat-start hook signature and energy Cmd",
or "errors.md: no .pck produced". Do not load the whole pack into context.
