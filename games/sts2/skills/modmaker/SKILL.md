---
name: modmaker
display_name: STS2 Mod Maker
short_description: Turn one sentence into a working Slay the Spire 2 mod
default_prompt: "Use ${MODMAKER_COMMAND} to build a Slay the Spire 2 mod from a natural-language description."
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

## Scope right now (M3 — relic, with a bounded repair loop)

This skeleton targets the **relic** path end to end: turn one sentence into a
known-good relic, and when a stage fails, run the **bounded automated repair loop**
(`repair.md`) to diagnose → fix → re-verify within a hard retry cap. Card/potion
recipes, automated tier-2 behavior testing, and the art-generation pipeline are
later milestones. If a request needs those, say so plainly rather than half-doing it.

## Stage files

Read each from `${MODMAKER_SKILL_DIR}/` only when you reach that stage.

| File | Purpose | When to read |
|------|---------|--------------|
| `interview.md` | One short clarifying round → intake | Pipeline start (after resume check) |
| `spec.md` | Write `SPEC.md` (the design contract) | After interview |
| `scaffold.md` | `dotnet new` + manifest + PckPacker wiring | After spec |
| `author.md` | Write the C# element + localization + marker | After scaffold |
| `build.md` | `dotnet build` → .dll/.pck/.json into mods/ | After author |
| `verify.md` | Launch + log-assert load (tier-1) + tier-2 guide | After build |
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
 4. AUTHOR (author.md) — query the sts2-api pack, pick the recipe, write the
    Custom*Model subclass filling ONLY the effect logic, add localization JSON,
    inject the [T2MOD-SELFTEST] marker.
    |
 5. BUILD (build.md) — tools/build.ps1 → .dll/.pck/.json into mods/. On failure:
    go to REPAIR (repair.md).
    |
 6. VERIFY (verify.md) — launch via steam_appid.txt, grep godot.log for the marker
    and mod-named errors (tier-1). Then guide the user through the dev-console
    tier-2 check. Never claim the effect is verified when only load was. On failure:
    go to REPAIR (repair.md).
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
no mod-named errors) and, ideally, its **effect must fire** (tier-2: observed via
the dev console). Report exactly which tier was reached. See `verify.md`.

## When you need a concrete STS2 answer

Use the **sts2-api** skill (`${STS2_API_SKILL_DIR}`) with a targeted query rather
than guessing an API — e.g. "relic: combat-start hook signature and energy Cmd",
or "errors.md: no .pck produced". Do not load the whole pack into context.
