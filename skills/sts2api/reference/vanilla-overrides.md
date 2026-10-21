# Vanilla override grounding and routing

This page supplies version grounding for edits to existing STS2 content. The promoted route
families each have their own reference: public Card behavior in `vanilla-card-overrides.md`,
all 44 public visual registry routes in `vanilla-visual-overrides.md`, existing Ancient
initial-option append plus reviewed replacement/page-flow routes in
`vanilla-ancient-overrides.md`, checked unlock gating and Card/Relic/Potion pool membership in
`vanilla-availability-overrides.md`, and non-Card data and behavior in
`vanilla-non-card-overrides.md`. New scaffolds still emit an empty
semantic manifest; author a nonempty operation only through a route family listed in the checked
catalog. `build.py` rejects every other route before MSBuild.

Read this reference whenever a request targets an existing vanilla Card, Relic, Potion,
Power, Monster, Encounter, Event, or other model. Resolve the target and report the exact
current boundary. Route a selected public visual surface to `vanilla-visual-overrides.md`.
Route a non-asset Card operation to `vanilla-card-overrides.md`, starting at its § Pick
routes table. Route checked epoch/pool availability operations to
`vanilla-availability-overrides.md`. Route non-Card data, behavior, rules text, and Relic
variable values to `vanilla-non-card-overrides.md`. For an exact `content_kind: ancient`
target, route option/branch behavior to `vanilla-ancient-overrides.md` and visual surfaces
separately to the visual route. Do not fall back to a new-content recipe or derive
Harmony/reflection/Publicizer/IL from a prompt.

An override changes only what the user named. A changed number or behavior keeps the
model's name and every other unnamed surface vanilla, and it changes the rules text exactly
as far as needed to keep that text true. Each family reference names its text route.

## Pinned catalog

The checked catalog is `reference/vanilla-overrides/catalogs/sts2-0.107.1.json`, the
inventory of every vanilla model in the pinned game. Read it only through
`vanilla_overrides.py`. Each record carries the stable ID and type, category properties,
Card base/upgrade costs and typed dynamic variables, Card/Relic/Potion pool membership,
Act/shared source membership, and localized titles.

Card, Relic, Potion, and Power records also carry `description_localization`: the English
and Simplified Chinese rules-text template from the same table as the title
(`<ENTRY>.description`), with its SmartFormat variables intact. It is reference text for
"like vanilla X" lookups and the drift baseline of a rules-text replacement. Curse/Status
Cards and some Powers have no description key and carry none.

## Exact target resolution

Resolve through `vanilla_overrides.py`, not a handwritten target whitelist:

```powershell
python ../modmaker/scripts/vanilla_overrides.py resolve STRIKE_IRONCLAD --category card
```

Aliases come from the complete `ModelId`, its entry, concrete type name, and every checked
localized display title. Matching uses Unicode NFKC normalization, case folding, and
removal of non-alphanumeric separators. It is exact after normalization. Debug/mock models
are excluded unless a maintainer explicitly requests `--include-debug`.

- one match returns the checked catalog record;
- multiple matches fail and require a category or complete `ModelId`;
- no match fails with close catalog suggestions;
- a guessed, fuzzy, or post-update substitute is never selected automatically.

For example, `恶魔形态` resolves to `CARD.DEMON_FORM`. `Strike` and `打击` are both
ambiguous across the five Character-specific starting Cards even with category `card`, so
the resolver lists all five and requires a complete `ModelId` or another grounded
disambiguation. This is localized display-name resolution, not a general parser for free-
form grammar, synonyms, translated Character qualifiers, or gameplay descriptions.

## Semantic manifest

Every new scaffold contains `skillthespire/vanilla-overrides.json`:

```json
{
  "schema": "skillthespire.sts2.vanilla-overrides/v1",
  "mod_id": "ExampleMod",
  "profile": "ritsulib-0.6.7-sts2-0.107.1",
  "host_version": "0.107.1",
  "catalog_sha256": "c56bbcf3ac07f06e8644b43e536f6180c20b3d318f742ef7945a73eeb1f6791f",
  "operations": []
}
```

`build.py` validates this document before MSBuild. It is a build-time input that stays in
the project directory and is never deployed into `mods/<ModName>/`: the game parses every
`.json` under a deployed Mod directory as a Mod manifest and logs a load error for each one
without an `id`. The generated C# carries the accepted operations at runtime, so the
deployed Mod needs only its own `mod_manifest.json`. `build.py` fails on any
deployed non-manifest `.json`. A project without this file builds with no vanilla overrides.

Every authorable operation carries `order`, stable `operation_id`, resolved
`target_model_id`, semantic `mode`, affected `surface`, selected route, expected catalog
baseline, and semantic payload. The expected baseline is a recursive subset of the checked
target record, for example:

```json
{
  "expected_baseline": {
    "properties": {
      "rarity": "Common"
    }
  }
}
```

Types and values must match exactly. Missing or changed fields are baseline drift. Card
operations include exact category/type baselines and the surface-specific fields in
`vanilla-card-overrides.md`; a rules-text replacement also pins the vanilla
`description_localization` text, so a game update that rewrites it is drift. Visual operations also require exact content kind and a
checked Mod-local resource contract from `vanilla-visual-overrides.md`. No other operation
is authorized merely because this generic shape can identify its target. Existing-Ancient
operations additionally require exact `content_kind`, singleplayer semantics, Mod-local
`events.json`, and every selected flow/route fingerprint from
`vanilla-ancient-overrides.md`. Availability operations require the exact epoch or
pool membership semantics, complete source baselines, fixed Adapter dependencies, and
post-operation primary pool from `vanilla-availability-overrides.md`.

## Fail-closed rules

Validation rejects:

- wrong host/profile or a changed catalog digest;
- unknown targets, ambiguous names, duplicate operation IDs, or out-of-order operations;
- a baseline value/type that differs from the selected catalog model;
- an unlisted `probe` route;
- an unknown adapter or IL fingerprint that differs from its checked catalog record;
- an ordinary Event routed as an Ancient, unknown/unreachable Ancient page, replacement
  without a finish path, or missing/empty Mod-local Ancient option/page text;
- a made-up epoch, an unfiltered act-owned Ancient, incomplete Relic/Potion override
  dependencies, a wrong/debug pool, duplicate/missing membership transition, removal of a
  final pool, or a primary-pool assertion that disagrees with pinned `ModelDb` order;
- semantic fields that request Harmony, prefix/postfix/transpiler bodies, reflection,
  private fields, Publicizer, or IL; and
- visual paths outside exact `res://<ModId>/`, traversal/backslashes, script resources,
  wrong resource kinds, required project files that are absent, or unusable layer
  directories; and
- a rules-text replacement whose key is not the target's vanilla description key, whose
  shipped `eng`/`zhs` (or other shipped language) value is missing or empty, or whose text
  references a variable the vanilla description cannot resolve; and
- ambiguous same-Mod overlap on one target/surface.

Ordered Card tag/text/tip/glow/playability/owner-hook and behavior composition is preserved.
Costs allow one `set` followed by deltas, or deltas alone; a later `set` conflicts. Multiple
exclusive property/result/replacement operations conflict on the same target/surface, and
two variable-value operations conflict on the same target variable.
Ancient append rules compose with other appends; one same-target replacement conflicts with
every append or replacement in the generated Mod.
External Mod compatibility is not inferred from this same-Mod check.

A vanilla edit's behavior and presentation are proved only in its nearest real consumer, never
by the catalog or a successful Build.
