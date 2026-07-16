# grounding.md — where facts come from (and who does the digging)

> When the pack doesn't already answer a question, **ground it — don't guess.**
> Project policy: "Reuse, don't rebuild grounding."
>
> **Read this first — who is asking matters:**
> - **At runtime (a `/modmaker` run), you read the PACK and nothing else.** The
>   recipes, `reference/*` pages (incl. `build-constraints.md` + snapshots), and
>   `errors.md` are the whole world. You do **not** live-decompile, hit the network,
>   or open any path outside the pack — those files don't exist on the user's machine.
>   If the pack genuinely lacks something the request needs, that's a **pack gap**:
>   say so plainly and stop, don't dig. Runtime decompilation is forbidden. The rest of
>   this page is what the *maintainer* did to build the pack - context, not a runtime
>   instruction.
> - **As a maintainer (extending the pack, offline, not during a user run)** you use
>   the three sources below to distill new recipe/reference/errors content. The result
>   ships; the source paths never do (`[[audience-split-pack-vs-maintainer]]`).

## The three sources (they answer three DIFFERENT questions)

| Source | Answers | Reach for it when… |
|--------|---------|--------------------|
| **spire-codex** (content DB + REST API) | *What content exists and what it does* — game-content facts | you need which effects/keywords exist, a vanilla analog, rarity/target/pool as **content**, the exact numbers a vanilla element uses |
| **the decompile** (`sts2.dll` + BaseLib) | *How to model it in C#* — code signatures | you need the real `Cmd` name + signature, the hook/override method, an enum's members, a `Custom*Model` base shape |
| **the toolchain validators** (analyzer + csproj/MSBuild targets + BaseLib registration `throw`s) | *What will BUILD and LOAD* — build/load constraints | you need the required loc keys, `[Pool]` rules, or any "why won't it compile / why did it throw at load" answer |

Complementary, and the split matters:
- spire-codex says **"a Fire Potion deals 20 damage to one enemy, Common, shared pool."**
- the decompile says **"that's `CreatureCmd.Damage(...)` in an `OnUse` override, `TargetType.AnyEnemy`."**
- the validators say **"and it will NOT build unless `potions.json` has `.title` + `.description`, and the class carries `[Pool]`."**

> **The asymmetry that hides bugs: "the decompile shows it RUNS" ≠ "it BUILDS."** A
> power runs fine without `.smartDescription` (runtime falls back to `.description`),
> but the analyzer **hard-fails the build** without it (STS001). A perfect read of the
> runtime code will still miss this — build/load constraints are a *separate* source
> (the third row), enforced by the analyzer/targets/registration code, and they are
> pre-mined into **`reference/build-constraints.md`**. Check that page for anything
> loc-key / `[Pool]` / "won't compile" shaped.

The recipe already fuses all three for the common cases — only reach past it when the
recipe lacks the specific effect, and even then the answer is usually already in
`build-constraints.md` or a snapshot.

---

# Maintainer digging (offline pack-building — NOT a runtime step)

> Everything below runs on a maintainer's dev box while *building* the pack. A
> `/modmaker` run never does any of it. Paths here are dev-box paths; they must never
> be copied into a shipped pack file (`[[audience-split-pack-vs-maintainer]]`).

## spire-codex — the content source

Reverse-engineered STS2 database with a REST API and web frontend
(`https://spire-codex.com`), STS2-specific, 14 languages. **PolyForm Noncommercial**
on the code; game data © Mega Crit (fair-use). open-mod is free/noncommercial, so
querying it for grounding is fine — **attribute it** wherever its facts land in the
pack (see `reference/potions-snapshot.md`).

Query order — cheapest first:
1. **The pack snapshot** (`reference/*-snapshot.md`) — already distills content facts
   for supported element types. Offline, instant. Look here first even as maintainer.
2. **A local data dump**, if you have one (a maintainer clone of the codex `data/`
   JSONs) — offline grep, no rate limit; parse with a script, don't dump 600 KB into
   the transcript.
3. **The live REST API** — only when neither has it (a field they didn't capture, a
   new element, a non-eng language):

   ```
   https://spire-codex.com/api/{cards,potions,powers,keywords}?lang=eng
   https://spire-codex.com/api/{monsters,relics}/{id}?lang=eng
   ```
   - **Browser User-Agent required** (`-A "Mozilla/5.0 ..."`), else `403`.
   - **Save to a file, inspect with a script** (`[[keep-tool-output-quiet]]`; `/cards`
     is ~600 KB). Reading a UTF-8 file back on Windows may hit a `gbk` decode error —
     pass `encoding='utf-8'`. Rate limit **60 req/min**, cached 5 min — fetch once.

## the decompile — the C# signature source

Local decompile of `sts2.dll` + BaseLib (via `ilspycmd`). Grep it for the exact `Cmd`
signature, an override method, an enum's members, or a vanilla element's class to copy
its `OnUse`/hook body. This is where `recipes/*.md` and the api-reference notes were
sourced. **When you confirm a new signature here, it's a recipe / `errors.md`
candidate** — fold it into the pack + note it in the maintainer `MEMORY.md` (same
compounding-moat rule as `errors.md`).

## the validators — the build/load-constraint source

The analyzer (`Sts2ModAnalyzers.dll`), the csproj/MSBuild targets, and BaseLib's
registration `throw`s. Already mined into `reference/build-constraints.md` (full
STS001–004 set + required-loc table + `[Pool]` rule). These gain rows on version
bumps → **re-mine on upgrade** (that page's "Re-mining" section), don't assume the
last dump is current.

## The rule

Guessing an API name is the #1 way the repair loop burns its attempts (`errors.md`
"Unknown type / member"). If the pack doesn't have it: **content → spire-codex; C#
signature → the decompile; won't-build / won't-load → the validators
(`build-constraints.md`).** Never a fourth guess — and at runtime, a pack gap is a
gap to report, not a dig to start.
