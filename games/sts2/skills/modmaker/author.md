# Author — write the element, localization, and marker

Goal: translate the accepted framework-neutral SPEC through the selected adapter,
fill only the effect logic, add localization, and inject the shared diagnostics.
Registration, model templates, localization-key derivation, and asset profiles come
from the adapter rather than the user-facing SPEC.

Before writing source, validate selected support routes and raw model-hook reachability:

```powershell
python ${GAME_TOOLS_DIR}/capability_preflight.py --spec SPEC.md
```

Emit only current operations written in the human-readable SPEC. Every emitted content
registration, behavior/data operation, selected presentation, and placeholder must follow its
stated recipe/reference. Never emit deferred, out-of-scope, or unresolved-gap intent, and never
add an unrequested convenience feature.

If authoring reveals that the selected route cannot produce the accepted complete operation,
stop before a workaround and follow `repair.md` from the observed failure. A local lowering
omission may be corrected directly; a different visible result returns to DESIGN and SPEC for
acceptance; an absent or broken shared route continues as a Mod-local route under
`${STS2API_SKILL_DIR}/grounding.md` § Mod-local Routes.

On revision, update only the confirmed delta and its direct consumers: behavior, localization,
Event text, visual prompts/resources, Character identity, generated source, and SelfTest.
Preserve stable runtime/localization identifiers unless the user changes identity. Re-run only
affected PLAN stages and the nearest proportional host/check; do not schedule a full acceptance
unless the user or active project plan explicitly selects it.

Read `semantic-contract.md` first, then read the selected framework reference
(`${STS2API_SKILL_DIR}/reference/ritsulib-adapter.md` for the current target). RitsuLib-specific
snippets live in that reference and the surface recipe it routes to; do not copy a
second framework branch into this file.

When the SPEC selects generated art, start §4 first: get its one batch approval and start the
calls, then write §§1-3 while they run. C#, localization, and SelfTest never depend on art.
If the host cannot run generation in the background, do §4 after §3 as written. Build waits
until every approved asset has landed or fallen back to placeholder.

## 0. Read before writing C#

- Read `quirks.md` before writing any C#.
- For each element in SPEC, read its `surfaces/<surface>.md`. Its "Author the element class",
  "Authoring route", and "Shared capability routes" sections name the recipe and every
  reference that element needs; the `sts2api` file table says when each reference applies.
- For an ordered `effects.sequence` with an ordinary player-visible effect, read
  `reference/effect-primitives.md` once. Take command lowering and required inputs from it and
  callback/context/owner/source/target bindings from the surface page, then emit each awaited
  call in SPEC order. If the callback lacks a required input, stop and name that input plus the
  applicable specialized route; do not invent a substitute for a maintained primitive.
- For a `Hook:` line, read `reference/model-hook-participation.md`. It owns the three
  declaration shapes, the per-surface owner property, and the guard-value-neutral body. An
  Enchantment uses its five `Enchant*` replacements, and a Rest Site option never goes through
  the raw hook.
- For selected bounded state, read `reference/stateful-mechanics.md` and emit only the selected
  schemas, owners/listeners, transitions, reset, persistence, visibility, and consumers; never
  infer lifetime from the C# field or hook that happens to be easiest.
- For a `Mod-local:` line, follow `${STS2API_SKILL_DIR}/grounding.md` § Mod-local Routes.
- For an existing vanilla model, read `reference/vanilla-overrides.md`, then the selected
  family reference (`vanilla-card-overrides.md`, `vanilla-visual-overrides.md`,
  `vanilla-ancient-overrides.md`, `vanilla-availability-overrides.md`, or
  `vanilla-non-card-overrides.md`). Each owns its authoring rules, manifest operation, and stop
  conditions. Resolve the exact catalog target, lower only promoted public/fixed-Adapter routes,
  write every accepted operation to `skillthespire/vanilla-overrides.json`, and never register a
  replacement vanilla model. If SPEC requests vanilla Card base-description replacement,
  removal, or hiding, stop until the user explicitly accepts before/after composition.
- Never emit Settings, Progression, post-run Badge, Telemetry, Multiplayer, Update Check, or a
  connection to one of those deferred families. Never substitute alternative-energy patches,
  C/D access, assembly-wide `PatchAll`, or `SkillTheSpire.Runtime`.
- Make every generated `.cs` file namespace-complete on its own. Copy the `using` required by
  every symbol into the file that uses it; never rely on a different snippet, file, or
  non-global import. In particular, `RegisterPatch<T>()` requires
  `using STS2RitsuLib.Patching.Core;`, and `GoldLossType` requires
  `using MegaCrit.Sts2.Core.Entities.Gold;`. Recheck imports per file before the first build.

## 1. Write the element classes

Each surface page's "Author the element class" section owns the file path, base template,
content-pack registration, and lowering rules for its element. Emit the selected Monster and
Encounter nodes plus their exact roster edges, with no `[Pool]` on either.

**Counter Power amount domain (applies to every source element).** Before writing any custom
Counter mutation, read that Power's `amount domain` from SPEC and follow
`recipes/power.md` § Amount domain: consume by clamping to the existing amount, never with a
negative `PowerCmd.Apply<T>`, and re-read the retained Power after amount hooks run.

## 2. Keep the load marker; add diagnostic markers

The scaffolded `MainFile.Initialize()` already emits the exact **load** marker with the loaded
framework version and host/compat profile that Tier 1 checks. Do not add, move, duplicate, or
rewrite any `loaded ok` line: verification reads the last one, so a second marker without the
profile fails Tier 1.

Log a **diagnostic** marker inside the trigger showing what code ran
(a relic's combat-start hook, a potion's `OnUse`, a card's `OnPlay`, an enemy's move body,
or an event option method):

```csharp
MainFile.Logger.Info($"[T2MOD-SELFTEST] <ElementName> fired/used: <requested outcome>");
```

The load marker proves Tier 1. The trigger marker stays for diagnosis, but it is **not**
Tier-2 proof: preview/calculation hooks may log without committing state. The harness in
the next step independently asserts post-state and emits the only accepted proof marker.

## 2.5 Emit the tier-2 self-test harness

This is what makes tier-2 automatic: the effect fires and is checked with no human at the
keyboard. Follow `${STS2API_SKILL_DIR}/reference/selftest-harness.md`:

1. Emit `<ModName>Code/SelfTest.cs` from that page. The arg gate, menu-to-run navigation,
   timeout, catch, terminal markers, and ship-safety are shared; the hosted room entry is
   scenario-specific. Keep it in the **same namespace as `MainFile.cs`**
   (`<ModName>`; the scaffold writes `namespace <ModName>;`) so it reaches `MainFile.Logger`.
2. Fill **exactly one** source driver body from the source element's surface page
   § Self-test driver body. A **power**, **keyword**, or **enchantment** adds its assertions to
   its host Card's run; an **orb** is driven through its channel host. For a multi-element SPEC,
   use that source driver, then observe each dependent state in dependency order; there is no
   `combo` element. Each selected capability (advanced targeting, calculated values, bounded
   state, secondary resources, ordered buffers, Rest Site options, Rewards, Card Piles, Runtime
   UI) adds only the cases SPEC selected, from its reference's proof matrix.
3. In every driver, snapshot concrete state, drive the real source, assert the SPEC's exact
   post-state, then call the shared `StateProof(...)`. Its structured
   `[T2MOD-SELFTEST] <ModName> state proof:` line must include the selected framework,
   framework version, host, compat target, expected value, and observed value. A broad
   `played/fired/used` marker never qualifies.
4. Add the **gated arm line** to `MainFile.Initialize()`, right after the load marker:

```csharp
if (CommandLineHelper.HasArg("t2selftest")) SelfTest.Arm();   // verification-only; dormant for end users
```
`using MegaCrit.Sts2.Core.Helpers;` for `CommandLineHelper`. The arg gate means a normal
user launch never arms it — no menu driving, fully inert. It ships dormant inside the mod.

**Grounding rule still holds:** the harness uses only the confirmed public Cmds in
`selftest-harness.md` (`CardCmd.AutoPlay`, `PowerCmd.Apply`, `RelicCmd.Obtain`, potion
`EnqueueManualUse`, …). Do **not** invent an API or try `NDevConsole…ProcessCommand(string)`
— that path is unreachable (private field); the page explains why.

## 3. Write localization

For every player-facing string, author both
`<ModName>/localization/eng/` and `<ModName>/localization/zhs/` from the exact bilingual
SPEC text. The directory trees, table names, and keys are identical, and both languages
reference the same SmartFormat variables and the same `:diff()`/`energyIcons()`/`starIcons()`
values; grammar formatters such as English `{Cards:plural:card|cards}` may be dropped in
Chinese, as vanilla does. Do not satisfy the Chinese table by copying its English value
unchanged.

**Every string follows `reference/vanilla-text-style.md`.** It is the default, not an
option: look up each game term in `reference/catalogs/text-glossary-sts2-0.107.1.json` and
use its exact `eng`/`zhs` name and color; give each surface its vanilla number color and line
breaks (Card `:diff()` numbers uncolored and one effect per line; relic/potion/power/event
numbers `[blue]`, heals `[green]`, Event costs `[red]`); write Chinese with full-width
punctuation, no spaces, and the vanilla measure word; keep titles plain. Declare
`AdditionalHoverTips` for every Power, keyword, Orb, or Card a description names.

Only when SPEC selects `extra emphasis` (or Event `extra atmosphere`), apply those spans after
the default text is correct. Validate every tag against `reference/content-text-effects.md`
or `reference/event-text-effects.md`, keep tags balanced, do not wrap `:diff()` values in
another color, and never copy user-supplied raw markup.

For a **character**, write the 14 normalized flat keys to `characters.json` and the
complete `THE_ARCHITECT.talk.<CHAR_ID>` dialogue to `ancients.json`, as listed in
`recipes/character.md`. Lower every selected semantic Ancient group through
`reference/ancient-dialogue.md`: explicit zero-based `-visit`, one consistent repeat mode,
one speaker per line, and `.next` only on non-terminal lines. Generated Mods rely on
RitsuLib's registered population patch and emit no Harmony/reflection injection. For an
**event**, write the normalized title/page/option/result keys
to `events.json`; `InitialOptionKey` and `ModOptionKey` must match those explicit segments.

For the JSON-backed types, add the same keys to
`<ModName>/localization/<lang>/<table>.json` for both `eng` and `zhs` — **`relics.json`** for a
relic, **`potions.json`** for a potion, **`cards.json`** for a card, **`powers.json`**
for a custom power, **`monsters.json`** + **`encounters.json`** for an enemy encounter,
**`events.json`** for an Event, and **`characters.json`** + **`ancients.json`** for a
Character.
**Keys are FLAT and prefixed** (recipe's loc-key rule + errors.md "raw-key title"):

```json
{
  "<MOD>_<CATEGORY>_<TYPE>.title": "<title from SPEC>",
  "<MOD>_<CATEGORY>_<TYPE>.description": "<hover text from SPEC>",
  "<MOD>_<CATEGORY>_<TYPE>.flavor": "<relic flavor - relics only>"
}
```

Relics take `.title/.description/.flavor`; potions take `.title/.description` (plus
`.selectionScreenPrompt` only if the effect prompts a choice — no `.flavor`); cards take
`.title/.description` (plus `.selectionScreenPrompt` if it prompts a choice — no
`.flavor`, no separate upgrade key). A **card description uses SmartFormat placeholders**
for scaling numbers — `"Deal {Damage:diff()} damage."` not `"Deal 6 damage."` — so the
upgraded value renders automatically (`reference/mechanics.md` §2). A **power** takes
`.title/.description` with `{Amount}` for the stack count. An **enemy encounter** takes
two tables: `monsters.json` with just `<MOD>_MONSTER_<TYPE>.name`, and `encounters.json`
with `<MOD>_ENCOUNTER_<TYPE>.title` + `.loss`. Use the exact normalized public entries
produced by the RitsuLib adapter. Not nested JSON — a flat `Dictionary<string,string>`.
An owned Rest Site option adds its stable namespaced `.title` and `.description` keys to
the same `relics.json`; these are separate from the owner Relic's three model keys.
When a calculated Card value declares a tooltip, also add its resolved `.title` and
`.description` keys to each required language's `static_hover_tips.json`; omit the icon argument
for the native null-icon fallback.

## 4. Art (per SPEC's art plan - placeholder or generate)

Read the SPEC's one Mod-level art choice made at interview time. Do NOT re-ask here.

### Placeholder (the default - do nothing)

Leave the art file absent. Every surface's checked fallback applies, as listed in
`${STS2API_SKILL_DIR}/reference/art-contract.md` and the surface page's `fallback` field. A
Character sets `PlaceholderCharacterId => "ironclad"` and leaves optional profile rows unset
(`reference/character-presentation.md`). An existing vanilla visual override may use
placeholder only when its manifest resource is optional; a required resource stops before
build until the user supplies it.

### Generate (acquire one source, then deterministic `gen_sprite.py import`)

1. Follow `reference/art-contract.md` for each spec's path, size, chroma, prompt template, and
   import command. Character art also follows `reference/character-presentation.md` and
   `reference/character-combat-cues.md`: normalize the selection portrait first, because it is
   the only identity reference for later Character assets. Material, PackedScene, Spine, and
   layer-directory inputs must already be authored local resources; never ask an image model
   for them.
2. **Respect the route's consent boundary.** For `host-tool`, the user's Mod-level
   `generate` choice authorizes the initial one-image-per-asset run; follow any approval or
   usage warning the host presents and never claim host usage is free. For `backend:<name>`,
   get **one** yes for the whole initial run from the batch list in `reference/art-contract.md`
   § Consent and the regenerate loop (a Character asks twice: portrait, then the rest). Every
   regeneration, on any route, needs a new confirmation after the user sees the current result.
3. Acquire through the SPEC's `art source`, then normalize into
   `<work dir>/<ModName>/images`: `host-tool` and `local-image` sources go through
   `gen_sprite.py import`; `backend:<name>` runs `gen_sprite.py generate --backend <name>`,
   which imports for you. Use a host image tool only when it is actually callable; in Codex,
   follow the `imagegen` skill's built-in `image_gen` mode, not its API fallback.
4. **Unavailable or failed means a bounded fallback, not a block.** A missing tool, missing
   output file, missing backend config, a failed or timed-out generation, zero or multiple
   images, or an import failure stops that route and keeps the placeholder unless the user
   explicitly selects another route. Never silently choose a paid backend or retry a
   possibly charged generation. Record only the route and outcome in `MEMORY.md`, never
   account or credit output.

Whether placeholder or generated, the `.pck` build (`build.md`) is what makes the art reach the
game; a code-only `dotnet build` won't (same rule as localization).

## 4.5 Trace each Autotest scenario before Build

A failed Tier 2 costs a full game launch. Before Build, walk every `## Autotest` scenario
through the code you just wrote, in your head, and write nothing down:

- the driver reaches the source the scenario names and triggers it the way the SPEC says;
- the effect code produces exactly the expected post-state values, after upgrades and the
  calculation timing the SPEC states;
- every neutral, rejection, reset, or edge case in the scenario takes the branch it expects; and
- the `state proof:` line is emitted only after its assertions pass.

Fix any mismatch now. This trace is not a check result and is never reported as one.

## 5. Update state

Record in `MEMORY.md`: the class name, the hook used, the exact loc keys written,
any Cmd choices, the state lifetime/reset/persistence (when present), which DRIVER body
the harness uses, and the **art outcome**
(placeholder, or generated `<slug>.png`/`big/<slug>.png` — and if generate was chosen
but fell back to placeholder, why). Mark `author and SelfTest` done in `PLAN.md`. Then go
to `build.md`.
