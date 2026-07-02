# Author — write the element, localization, and marker

Goal: fill in ONLY the effect logic on top of the recipe skeleton, add the
localization JSON, and inject the self-test marker. Everything structural
(class skeleton, `[Pool]`, image paths) comes from the recipe — don't reinvent it.

## 0. Read the quirks and the recipe first

- Read `quirks.md` before writing any C#.
- Query the **sts2-api** skill for the element recipe (M2: `recipes/relic.md`).
  Pull the skeleton, the trigger-hook table, the effect building blocks, and the
  loc-key derivation rule. Do **not** guess API names — if the effect needs a Cmd
  not in the recipe, ask sts2-api ("commands for <effect>") or ground against the
  decompiled API rather than inventing one.

## 1. Write the relic class

Add `<ModName>Code/Relics/<RelicName>.cs`. Use the recipe skeleton verbatim, then:

- Set `Rarity` from SPEC.
- Keep `[Pool(typeof(<Pool>))]` — **omitting it throws at registration** (errors.md).
- Override the hook matching SPEC's trigger (recipe's "Trigger hooks" table). For
  combat-start: `AfterSideTurnStart` + `participants.Contains(Owner.Creature)` +
  `Owner.PlayerCombatState!.TurnNumber <= 1` guards.
- Fill **only** the effect block with the confirmed Cmds/RNG from the recipe's
  "Effect building blocks". `await` every Cmd. Use `Rng`, never `System.Random`.
- Call `Flash()` when the relic visibly triggers.

## 2. Inject the self-test markers

**Two markers.** The Alchyr template's `MainFile.cs` does NOT log anything by
default — you must add the **load** marker yourself, or tier-1 verify silently
finds nothing. In `MainFile.Initialize()`, right after `harmony.PatchAll();`:

```csharp
Logger.Info("[T2MOD-SELFTEST] <ModName> loaded ok");
```

Then, for **effect** proof, log a marker inside the trigger showing observed
before → after state:

```csharp
MainFile.Logger.Info($"[T2MOD-SELFTEST] <RelicName> fired: {outcome} <metric> {before} -> {after}");
```

verify.md greps the first for tier-1 and the second for tier-2. Keep both during
M1/M2 while verification is manual.

## 3. Write localization

Add entries to `<ModName>/localization/eng/relics.json`. **Keys are FLAT and
prefixed** (recipe's loc-key rule + errors.md "raw-key title"):

```json
{
  "<PREFIX>-<SLUG>.title": "<title from SPEC>",
  "<PREFIX>-<SLUG>.description": "<hover text from SPEC>",
  "<PREFIX>-<SLUG>.flavor": "<flavor from SPEC>"
}
```

Use the exact `<PREFIX>-<SLUG>` you derived in SPEC. Not nested JSON — a flat
`Dictionary<string,string>`.

## 4. Art (M2: placeholder)

Leave the template placeholder. The base class falls back to `relic.png` if
`images/relics/<slug>.png` is absent. Custom/generated art is M4 — don't block on it.

## 5. Update state

Record in `MEMORY.md`: the class name, the hook used, the exact loc keys written,
and any Cmd choices. Mark `author` done in `PLAN.md`. Then go to `build.md`.
