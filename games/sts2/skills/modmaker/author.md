# Author — write the element, localization, and marker

Translate the accepted SPEC into code: fill only the effect logic, add localization, and keep the
shared diagnostics. Registration, model templates, localization keys, and asset profiles follow
the fixed shapes in each element recipe.

Emit only the current operations written in SPEC. Every emitted registration, behavior/data
operation, selected presentation, and placeholder follows its recipe or reference. Never emit
deferred, out-of-scope, or unresolved intent, and never add an unrequested convenience feature.

If authoring reveals that the selected route cannot produce the accepted operation, stop before
a workaround and follow `repair.md`. A local lowering omission may be corrected directly; a
different visible result returns to DESIGN and SPEC for acceptance; an absent or broken shared
route continues as a Mod-local route under `${STS2API_SKILL_DIR}/grounding.md` § Mod-local Routes.

On revision, update only the confirmed delta and its direct consumers: behavior, localization,
Event text, visual prompts/resources, Character identity, source, and SelfTest. Keep stable
runtime and localization identifiers unless the user changes identity. Rerun only the affected
PLAN stages and the nearest proportional check.

When SPEC selects generated art, start §4 first: get its one batch approval and start the calls,
then write §§1-3 while they run. C#, localization, and SelfTest never depend on art. If the host
cannot run generation in the background, do §4 after §3. Build waits until every approved asset
has landed or fallen back to placeholder.

## 0. Read before writing C#

- Read `quirks.md`, including § Multiplayer-safe by default: every Mod's gameplay code is
  written for multiplayer, whatever mode the user plays.
- For each element in SPEC, read its recipe `${STS2API_SKILL_DIR}/recipes/<surface>.md`. It names
  every reference that element needs; the `sts2api` file table says when each applies.
- For an ordered `effects.sequence`, read `reference/effect-primitives.md` once. Take command
  lowering and required inputs from it and the callback/context/owner/source/target bindings from
  the element recipe, then emit each awaited call in SPEC order. If the callback lacks a required
  input, stop and name that input plus the applicable specialized route.
- For a raw hook, read `reference/model-hook-participation.md`: the three declaration shapes, the
  per-surface owner property, and the guard-value-neutral body. An Enchantment uses its five
  `Enchant*` replacements, and a Rest Site option never goes through the raw hook.
- For selected bounded state, read `reference/stateful-mechanics.md` and emit only the selected
  schemas, owners/listeners, transitions, reset, persistence, visibility, and consumers; never infer
  lifetime from the C# field or hook that happens to be easiest.
- For a `Mod-local:` line, follow `${STS2API_SKILL_DIR}/grounding.md` § Mod-local Routes.
- For an existing vanilla model, read `reference/vanilla-overrides.md`, then the selected family
  reference. Resolve the exact catalog target, lower only its promoted public or fixed-Adapter
  routes, write every accepted operation to `skillthespire/vanilla-overrides.json`, and never
  register a replacement vanilla model. Emit no operation for a surface SPEC lists as `unchanged`,
  in particular no title operation unless SPEC renames the model.
- Never emit Settings, Progression, post-run Badge, Telemetry, Multiplayer, Update Check, or a
  connection to one of them. Never substitute alternative-Energy patches, C/D access,
  assembly-wide `PatchAll`, or `SkillTheSpire.Runtime`.
- Make every `.cs` file namespace-complete on its own: copy the `using` for every symbol into the
  file that uses it, never relying on another snippet or a non-global import (for example
  `RegisterPatch<T>()` needs `using STS2RitsuLib.Patching.Core;` and `GoldLossType` needs
  `using MegaCrit.Sts2.Core.Entities.Gold;`). Recheck imports per file before the first build.

## 1. Write the element classes

Each element recipe owns the file path, base template, content-pack registration, and lowering
rules. Emit the selected Monster and Encounter nodes with their exact roster edges.

**Counter Power amount domain (every source element).** Before writing a custom Counter
mutation, read that Power's `amount domain` from SPEC and follow `recipes/power.md` § Amount
domain: consume by clamping to the existing amount, never with a negative `PowerCmd.Apply<T>`,
and re-read the retained Power after amount hooks run.

## 2. Keep the load marker; add diagnostic markers

The scaffolded `MainFile.Initialize()` already emits the exact **load** marker with the loaded
framework version and host/compat profile that Tier 1 checks. Never add, move, duplicate, or
rewrite any `loaded ok` line: verification reads the last one, and a second marker without the
profile fails Tier 1.

Log a **diagnostic** marker inside each trigger (a Relic's combat-start hook, a Potion's `OnUse`,
a Card's `OnPlay`, an enemy's move body, an Event option method):

```csharp
MainFile.Logger.Info($"[T2MOD-SELFTEST] <ElementName> fired/used: <requested outcome>");
```

It locates a failure but is never Tier 2 proof: preview and calculation hooks may log without
committing state. The kit asserts post-state independently and emits the only accepted proof.

## 2.5 Write the Tier 2 scenarios

The scaffold already generated `<ModName>Code/SelfTestKit.cs` and armed it in
`MainFile.Initialize()`; never edit either (Build rejects a changed kit). Following
`${STS2API_SKILL_DIR}/reference/selftest-harness.md`, write only
`<ModName>Code/SelfTestScenarios.cs` in the `<ModName>` namespace:

1. Write nothing for registration and text: the roll call checks every model class and its text
   in both languages on every run.
2. Add one `plan.FaceCheck<TCard>()` line per simple Card from SPEC § Autotest.
3. Add one named scenario per remaining SPEC scenario (`plan.Combat`, `plan.Encounter`,
   `plan.RunStart`, `plan.Event`, `plan.Ancient`, `plan.RestSite`, `plan.Act`, or `plan.Custom`)
   from the source element's recipe § Self-test driver body (or § Proof matrix). A Power, Keyword,
   or Enchantment adds its assertions to its host Card's scenario; an Orb is driven through its
   channel host. For a multi-element SPEC, drive the real source, then observe each dependent
   state in dependency order. Each selected capability adds only the cases SPEC selected from its
   reference's proof matrix.
4. In every scenario, snapshot concrete state, drive the real source (`t.Play`, `t.UsePotion`, a
   real room or button), and assert SPEC's exact post-state with `t.Proof(condition,
   observation)`, naming expected and observed values.

Scenarios use pinned public STS2/RitsuLib APIs, starting with the kit's own helpers. Never invent
an API or try `NDevConsole…ProcessCommand(string)`: that path is unreachable (private field).

## 3. Write localization

For every player-facing string, author both `<ModName>/localization/eng/` and
`<ModName>/localization/zhs/` from the exact bilingual SPEC text. The trees, table names, and keys
are identical, and both languages use the same SmartFormat variables and the same
`:diff()`/`energyIcons()`/`starIcons()` values; grammar formatters such as English
`{Cards:plural:card|cards}` may be dropped in Chinese, as vanilla does. Never satisfy the Chinese
table by copying the English value.

Each element recipe's Localization section gives its table, its flat keys under the exact
RitsuLib entry, and examples. Keys are flat strings, never nested JSON (`quirks.md`).

**Every string follows `reference/vanilla-text-style.md`.** Look up each game term in
`reference/catalogs/text-glossary-sts2-0.107.1.json` and use its exact `eng`/`zhs` name and
color; give each surface its vanilla number color and line breaks (Card `:diff()` numbers
uncolored and one effect per line; Relic/Potion/Power/Event numbers `[blue]`, heals `[green]`,
Event costs `[red]`); write Chinese with full-width punctuation, no spaces, and the vanilla
measure word; keep titles plain. Declare `AdditionalHoverTips` for every Power, keyword, Orb, or
Card a description names. Only when SPEC selects `extra emphasis` (or Event `extra atmosphere`),
add those spans after the default text is correct, validated against
`reference/content-text-effects.md` or `reference/event-text-effects.md`; never copy
user-supplied raw markup.

Localization and art reach the game only through the `.pck` that Build packs; a code-only
`dotnet build` changes neither.

## 4. Art (per SPEC's art plan: placeholder or generate)

Read the SPEC's one Mod-level art choice; never re-ask here.

### Placeholder (the default: do nothing)

Leave the art file absent. Every element's checked fallback applies, as listed in
`${STS2API_SKILL_DIR}/reference/art-contract.md` and the recipe's SPEC `fallback` field. A
Character sets `PlaceholderCharacterId => "ironclad"` and leaves optional profile rows unset. An
existing vanilla visual override may use placeholder only when its manifest resource is optional;
a required resource stops before Build until the user supplies it.

### Generate (acquire one source, then deterministic `gen_sprite.py import`)

1. Follow `reference/art-contract.md` for each spec's path, size, chroma, prompt template, and
   import command. Character art follows `reference/art-character.md` and the slot table in
   `reference/character-presentation.md` (plus `reference/character-combat-cues.md` for cues), and
   a `backend:<name>` route reads `reference/art-backends.md`. Normalize the selection portrait first, because it is the
   only identity reference for later Character assets. Acquire only the slots of the SPEC's
   `character art tier`, and acquire bodies and icons as one sheet each. A slot outside the tier
   gets no wrapper scene and no profile path, so RitsuLib keeps the Ironclad fallback. Material,
   PackedScene, Spine, and layer-directory inputs must already be authored local resources; never
   ask an image model for them.
2. **Respect the route's consent boundary.** For `host-tool`, the Mod-level `generate` choice
   authorizes the initial one-image-per-asset run; follow any approval or usage warning the host
   presents and never claim host usage is free. For `backend:<name>`, get **one** yes for the whole
   initial run from the batch list in `reference/art-contract.md` § Consent and the regenerate loop
   (a Character asks twice: portrait, then the rest). Every regeneration needs a new confirmation
   after the user sees the current result, at most two per asset.
3. Acquire through the SPEC's `art source`, then normalize into `<work dir>/<ModName>/images`:
   `host-tool` and `local-image` sources go through `gen_sprite.py import`; `backend:<name>` runs
   `gen_sprite.py generate --backend <name>`, which imports for you. Use a host image tool only
   when it is actually callable; in Codex, follow the `imagegen` skill's built-in `image_gen` mode,
   not its API fallback.
4. **Unavailable or failed means a bounded fallback, not a block.** A missing tool, output file,
   or backend config, a failed or timed-out generation, zero or several images, or an import
   failure stops that route and keeps the placeholder unless the user explicitly selects another
   route. Never silently choose a paid backend or retry a possibly charged generation. Record only
   the route and outcome in `MEMORY.md`, never account or credit output.

## 4.5 Trace each Autotest scenario before Build

A failed Tier 2 costs a full game launch. Before Build, walk every `## Autotest` scenario through
the code you just wrote, in your head, writing nothing down:

- the driver reaches the source the scenario names and triggers it the way SPEC says;
- the effect code produces exactly the expected post-state, after upgrades and the calculation
  timing SPEC states;
- every neutral, rejection, reset, or edge case takes the branch it expects; and
- the `state proof:` line is emitted only after its assertions pass.

Fix any mismatch now. This trace is not a check result and is never reported as one.

## 5. Update state

Record in `MEMORY.md` (template in `spec.md` § Project state) each element's class, hooks, exact
loc keys, Cmd choices, state lifetime/reset/persistence, the scenario names in
`SelfTestScenarios.cs`, and the art outcome (placeholder or the generated file, and why a chosen
generation fell back). Mark `author and SelfTest` done in `PLAN.md`, then go to `build.md`.
