# build-constraints.md — what the toolchain enforces at BUILD & LOAD time

> **The third source of truth.** spire-codex answers "what content exists"; the
> decompile answers "how to model it in C#"; **this page answers "what the toolchain
> refuses to build or load."** These are stricter than runtime — an element can be
> correct C# that *runs* fine and still fail here (the classic: a power runs without
> `.smartDescription` because it falls back to `.description`, but the analyzer
> **hard-fails the build** without it). Read this before authoring any element's
> localization + attributes; it is the single place that prevents STS001–004 and the
> BaseLib registration `throw`s.
>
> Facts below were mined from the actual validators, not guessed: the analyzer
> `Sts2ModAnalyzers.dll` v0.1.9 (§1–2, decompiled) and BaseLib's registration path
> `BaseLib` v3.3.2 (§3, decompiled — `CustomContentDictionary.AddModel`). A
> **game/analyzer/BaseLib version bump can add rows** — re-mine on upgrade (see
> "Re-mining" at the bottom).

## 1. The analyzer diagnostics — the COMPLETE set is STS001–STS004

The analyzer defines exactly four real diagnostics (confirmed against every
`DiagnosticDescriptor` in the decompiled source — there is no STS005+; `STS999` is an
internal logging-only descriptor, not a rule you can hit). Two are build **errors**
(fail the build), two are **warnings**.

| ID | Severity | Category | Fires when… | Fix |
|----|----------|----------|-------------|-----|
| **STS001** | **Error** | Localization | A model type is missing one of its **required localization keys** (table in §2). | Add every required key for that model type to its loc table. This is the one with an auto-fix (`FixableDiagnosticIds = STS001`). |
| **STS002** | Warning | Localization | Localization files were **not registered as analyzer additional files**, so the analyzer can't verify loc → it can't *prove* STS001 is satisfied. | Ensure the `.json` loc files are `AdditionalFiles` for analysis (the Alchyr template wires this; if you moved files, restore it). Fires at `CompilationEnd`. |
| **STS003** | Warning | Localization | A type looks like a game model but **does not inherit a `CustomModel`** base. | Inherit the correct `Custom*Model` (e.g. `CustomCardModel`), so BaseLib registers it and loc resolves. |
| **STS004** | Warning | Usage | A **poolable** model (`CustomCardModel` / `CustomPotionModel` / `CustomRelicModel`) has **no `[Pool]` attribute** (checked up the base-class chain). | Add `[Pool(typeof(<XPool>))]` (e.g. `ColorlessCardPool`, `SharedPotionPool`, `SharedRelicPool`). **Powers are NOT in this list** — a `CustomPowerModel` needs no `[Pool]` (BaseLib auto-discovers powers). |

Note STS004 is a *warning*, not an error — but a pooled model that isn't in a pool
won't appear in game, so treat it as load-bearing. STS004 recurses into base classes,
so `[Pool]` on a shared base class satisfies subclasses; abstract/static types are
exempt.

## 2. RequiredLocalization — which loc keys each model type MUST ship (drives STS001)

`SYMBOLID` = the element's full id `<PREFIX>-<SLUG>` uppercased (e.g.
`FIREBOLT-FIREBOLT`). Keys are flat entries in the named loc table (the JSON filename
column). **Missing any of these = STS001 build error.** This is the exact table the
analyzer checks (`NamedTypeLocData`), transcribed verbatim.

| Model type | Loc table (json) | Required keys (suffix on `SYMBOLID`) |
|------------|------------------|--------------------------------------|
| **CardModel** | `cards` | `.title`, `.description` |
| **PotionModel** | `potions` | `.title`, `.description` |
| **PowerModel** | `powers` | `.title`, `.description`, **`.smartDescription`** ← the one that bit us |
| **RelicModel** | `relics` | `.title`, `.description`, `.flavor` |
| **CharacterModel** | `characters` (+ `ancients`) | many — `.title`, `.titleObject`, `.description`, pronoun set, `.goldMonologue`, … (see §2a) |
| **AncientEventModel** | `ancients` | `.title`, `.epithet`, `.talk.firstVisitEver.0-0.ancient`, `.talk.ANY.0-0r.ancient` |

Enum-keyed loc (not a model but the analyzer checks it too):

| Enum type | Loc table | Required keys |
|-----------|-----------|---------------|
| **CardKeyword** | `card_keywords` | `.title`, `.description` |

**Mnemonic for the four common element types:** cards & potions = **title +
description**; relics = **+ flavor**; powers = **+ smartDescription**. Powers and
relics each add exactly one extra key, but a *different* one — don't cross them.

### 2a. CharacterModel (only if you ever add a playable character — large)

`characters` table keys: `.title`, `.titleObject`, `.description`, `.pronounObject`,
`.possessiveAdjective`, `.pronounPossessive`, `.pronounSubject`, `.goldMonologue`,
`.eventDeathPrevention`, `.aromaPrinciple`, `.cardsModifierTitle`,
`.cardsModifierDescription`, `.banter.alive.endTurnPing`, `.banter.dead.endTurnPing`.
Plus `ancients` table talk lines. Characters are far beyond current recipes — listed
for completeness; ground fully before attempting.

### 2b. Code-side localization classes (`*Loc`) — same key sets, cross-check

The analyzer also carries a `CodeLocalizationData` map for the code-level `*Loc`
classes, which agrees with the model table above and is a useful cross-check:
`PowerLoc` = title+description+**smartDescription**, `RelicLoc` = title+description+
**flavor**, `OrbLoc` = title+description+**smartDescription**, `CardLoc`/`PotionLoc`/
`ModifierLoc`/`CardModifierLoc` = title+description, `MonsterLoc` = `name`,
`ActLoc` = `title`, `EncounterLoc` = title+`loss`.

### 2c. Power override-satisfy escape hatch

For `PowerModel`, the analyzer's `OverrideIgnores` lets a power satisfy the loc
requirement by **overriding the C# members** `Title` / `Description` /
`SmartDescriptionLocKey` instead of shipping the loc keys. The recipe path (ship the
three loc keys) is simpler and what `recipes/power.md` uses — but if you see STS001 on
a power that *does* override these, that's why.

## 3. BaseLib registration-time constraints (load-time throws)

These fire at **mod load**, not at build — the analyzer (§1) cannot see them. The
registration path is short and deterministic: **every `Custom{Card,Potion,Relic}Model`
registers itself in its own constructor** (`autoAdd: true` by default) by calling
`CustomContentDictionary.AddModel(GetType())`. So "instantiate the model" *is*
"register it" — these throws happen the moment BaseLib news up your element during
load, aborting that mod's initialization. `AddModel` (+ its `IsValidPool` helper) is
the **only** place in the registration path that throws; the throw set below is
complete for it.

| Throw message (verbatim) | Fires when… | Fix |
|--------------------------|-------------|-----|
| `Model <FullName> must be marked with a PoolAttribute to determine which pool to add it to.` | The model type has **no `[Pool]`**. | Add `[Pool(typeof(<XPool>))]`. **This is the load-time twin of build warning STS004** — see the note below on why both exist. |
| `Model <FullName> is assigned to incorrect type of pool <PoolFullName>.` | The `[Pool]` points at a real pool family, but the **model's type doesn't match that family** (e.g. a `CustomCardModel` given a relic pool). | Point `[Pool]` at the pool that matches the element type: cards → a `CardPoolModel` subclass (e.g. `ColorlessCardPool`), potions → a `PotionPoolModel` subclass (e.g. `SharedPotionPool`), relics → a `RelicPoolModel` subclass (e.g. `SharedRelicPool`). |
| `Model <FullName> is assigned to <PoolFullName> which is not a valid pool type.` | The `[Pool]` type is **not in any pool family at all** — walking its base classes never reaches `CardPoolModel` / `RelicPoolModel` / `PotionPoolModel`. | Use an actual pool class (one deriving from a `*PoolModel` base), not an arbitrary type. |

### Why STS004 (warning) *and* a load-time throw both exist for missing `[Pool]`

STS004 is a **build warning** — it does not fail the build. BaseLib then **hard-throws
at load** on the same condition. So a `Custom{Card,Potion,Relic}Model` with no `[Pool]`
compiles (with a yellow squiggle), ships, and then **aborts its mod's load**. Treat
STS004 as load-bearing, exactly as §1 says. **Powers are exempt on both sides**:
`CustomPowerModel`'s constructor does **not** call `AddModel` (powers are auto-discovered,
no pool), so none of these three throws can hit a power — consistent with STS004
covering only the three poolable types.

### What is NOT a throw here (guess corrected by the decompile)

**Registering the same type twice is a silent no-op, not a throw.** `RegisterType`
is a `HashSet<Type>.Add`; the second `AddModel` for a type returns early. So there is
**no "duplicate id" load-time throw** in this path (the original plan guessed one).
Duplicate *ids* across different types are a content/authoring concern, not a
registration throw.

### Advanced: code-inline localization (only if you skip JSON loc tables)

If an element supplies loc via C# (`ILocalizationProvider.Localization` non-null)
instead of the JSON loc tables the recipes use, BaseLib's `AddModelLoc` can throw
`Override LocTable in your ILocalizationProvider.` (no `LocTable` given and the model's
category has no default table) or `Failed to get localization dictionary.`. **The
recipe path ships JSON loc tables and never hits this** — listed only so a mod that
opts into inline loc knows where these come from.

## Re-mining (maintainer)

This page is generated from the analyzer DLL + BaseLib decompile, which gain rows on
version bumps. To refresh:
- **§1–2 (analyzer):** decompile the current
  `alchyr.sts2.modanalyzers/<ver>/analyzers/dotnet/cs/Sts2ModAnalyzers.dll` with
  `ilspycmd`, re-read `NamedTypeLocData` (the §2 table) and every `DiagnosticDescriptor`
  (the §1 set), and diff against the above.
- **§3 (BaseLib):** decompile the current `alchyr.sts2.baselib/<ver>` DLL, re-read
  `CustomContentDictionary.AddModel` + `IsValidPool` and confirm the throw set, and
  check whether the `Custom*Model` constructors still self-register via `AddModel`
  (the registration entry point). §3 above was mined at BaseLib **v3.3.2**.

Deliverable is this re-runnable habit, not a one-time dump. See `grounding.md` (three
sources) and `errors.md` (STS001 entry).

---
*Analyzer data © its authors (Alchyr `Sts2ModAnalyzers`); transcribed for grounding.*
