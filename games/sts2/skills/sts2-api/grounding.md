# grounding.md — where facts come from (spire-codex + our decompile)

> When the pack doesn't already answer a question, **ground it — don't guess.**
> IMPLEMENTATION_PLAN.md §3: "Reuse, don't rebuild grounding." Two sources, two
> different jobs. Know which one answers your question before you reach for it.

## The two sources (they answer different questions)

| Source | Answers | Use it for |
|--------|---------|------------|
| **spire-codex** (queryable decompiled DB + REST API) | *What content exists and what it does* — the game-content facts | Which effects/keywords exist, a vanilla analog for the request, rarity/target/pool values as **content**, exact numbers a vanilla element uses |
| **our decompile** (`sts2.dll` + BaseLib, local) | *How to model it in C#* — the code signatures | The real `Cmd` name + signature, the hook/override method, enum definitions, `Custom*Model` base-class shape |

They are complementary. spire-codex tells you **"a Fire Potion deals 20 damage to
one enemy, Common, shared pool"**; the decompile tells you **"that's
`CreatureCmd.Damage(...)` in an `OnUse` override with `TargetType.AnyEnemy`"**. The
recipe already fuses both for the common cases — only reach past it when the recipe
lacks the specific effect.

## spire-codex — the content source (prefer the pack snapshot first)

Reverse-engineered STS2 database with a REST API and web frontend
(`https://spire-codex.com`). STS2-specific, 14 languages. **PolyForm Noncommercial**
license on the code; game data is © Mega Crit (served fair-use). open-mod is a free
noncommercial tool, so querying it for grounding is fine — **attribute it** wherever
its facts land in the pack (see `reference/potions-snapshot.md`).

**Query order — cheapest first:**

1. **The pack snapshot.** `reference/*-snapshot.md` already distills the content
   facts for the element types we support (e.g. every potion's name/rarity/effect/
   target). Offline, instant, no rate limit. **Look here before hitting the network.**
2. **The live REST API** — only when the snapshot lacks it (a field the snapshot
   didn't capture, a newly added element, a language other than eng):

   ```
   https://spire-codex.com/api/{cards,potions,powers,keywords}?lang=eng
   https://spire-codex.com/api/{monsters,relics}/{id}?lang=eng
   ```

   Rules when you call it:
   - **Browser User-Agent is required** — a bare request returns `403`. Use
     `-A "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"`.
   - **Save to a file, inspect with a script — do NOT dump JSON into the transcript**
     (`[[keep-tool-output-quiet]]`; `/cards` is ~600 KB). Pattern:
     ```bash
     curl -sS -A "Mozilla/5.0" "https://spire-codex.com/api/potions?lang=eng" -o /tmp/p.json
     python -c "import json;d=json.load(open('/tmp/p.json',encoding='utf-8'));print(d[0].keys());print(d[0])"
     ```
     (On this Windows box, reading a UTF-8 file back may hit a `gbk` decode error —
     pass `encoding='utf-8'` explicitly.)
   - Rate limit **60 req/min per IP**, responses GZip + cached 5 min. Fetch once,
     inspect locally; don't loop the endpoint.
   - Or run it **locally** (`docker compose up --build` in the spire-codex repo →
     `http://localhost:8000`) if you're doing heavy offline work.

## our decompile — the C# modeling source

The code signatures live in the local decompile, not spire-codex:

- **Game:** `D:\26summer_intern\decomp\sts2_full` (3425 files via `ilspycmd`).
- **BaseLib:** `D:\26summer_intern\decomp\baselib\BaseLib.decompiled.cs`.

Grep these for the exact `Cmd` signature, the override method, an enum's members, or
a vanilla element's class to copy its `OnUse`/hook body. This is where
`recipes/*.md` and `sts2-relic-api-reference` were sourced — the recipe should
already carry the answer; go here only for an effect the recipe doesn't cover.

**When you confirm a new signature here, it's an errors.md / recipe candidate** —
note it in the project `MEMORY.md` so the maintainer can fold it into the pack (same
compounding-moat rule as `errors.md` and `quirks.md`).

## The rule

Guessing an API name is the #1 way the repair loop burns its attempts
(`errors.md` "Unknown type / member"). If the recipe doesn't have it: **content
question → spire-codex; code question → the decompile.** Never a third guess.
