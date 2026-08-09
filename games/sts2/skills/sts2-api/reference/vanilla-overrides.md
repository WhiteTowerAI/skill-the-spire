# Vanilla override grounding and routing

This page supplies version grounding for edits to existing STS2 content. The promoted route
families each have their own reference: public Card behavior in `vanilla-card-overrides.md`,
all 44 public visual registry routes in `vanilla-visual-overrides.md`, existing Ancient
initial-option append plus reviewed replacement/page-flow routes in
`vanilla-ancient-overrides.md`, checked unlock gating and Card/Relic/Potion pool membership in
`vanilla-availability-overrides.md`, and non-Card data and behavior in
`vanilla-non-card-overrides.md`. New scaffolds still emit an empty
semantic manifest; author a nonempty operation only through a package listed in the checked
catalog. `build.py` rejects every other route before MSBuild.

Read this reference whenever a request targets an existing vanilla Card, Relic, Potion,
Power, Monster, Encounter, Event, or other model. Resolve the target and report the exact
current boundary. Route a selected public visual surface to `vanilla-visual-overrides.md`.
Route a non-asset Card operation to `vanilla-card-overrides.md`. Other behavior/data/
availability operations remain grounding-only until their later package is promoted. Route
checked epoch/pool availability operations to `vanilla-availability-overrides.md`. For
an exact `content_kind: ancient` target, route option/branch behavior to
`vanilla-ancient-overrides.md` and visual surfaces separately to the visual Package. Do not
fall back to a new-content recipe or derive Harmony/reflection/Publicizer/IL from a prompt.

## Pinned catalog

The checked catalog is
`reference/vanilla-overrides/catalogs/sts2-0.107.1.json` and has this identity:

```text
host: 0.107.1
framework: RitsuLib 0.5.4
profile: ritsulib-0.5.4-sts2-0.107.1
sts2.dll SHA-256: a1f9e653f1e28e4076558fee1e60d218619cb7e057b887c6417f62c62c6d7a52
assembly MVID: 97f10687-c306-4798-ab75-8b9f23f34dfb
runtime vanilla models: 1624
model-namespace metadata types: 3883
models with stable title localization sources: 1580
models with English and Simplified Chinese titles: 1537 each
catalog languages: deu, eng, esp, fra, ita, jpn, kor, pol, ptb, rus, spa, tha, tur, zhs
catalog SHA-256: 0279fd5e95e7fc9a076f2319bc5ec74952389045f26837c0d72c89d6f416dd73
adapter targets: 20
promoted operation packages: m6.7.1-public-card-overrides,
  m6.7.2-public-visual-overrides, m6.7.3-existing-ancient-overrides,
  m6.7.4-availability
```

The runtime collector subscribes once to `ModelPreloadingCompletedEvent`, reads `ModelDb`,
and retains only concrete model types whose assembly is the game's `ModelDb` assembly. A
loaded Mod therefore cannot add its own models to this vanilla inventory. It records stable
IDs/types, category properties, Card base/upgrade costs and typed dynamic variables,
Card/Relic/Potion pool membership, Act/shared source membership, and stable title
localization table/key pairs from RitsuLib's public `ModelTitleExtensions` mappings.

For title-bearing model families, the collector uses the game's public
`LocManager.SetLanguage` route to read each local title in all 14 pinned languages. That
API explicitly changes the runtime language temporarily without writing the player's
settings. The collector restores the original language in a `finally` block and refuses to
write a catalog when `OverridesActive` reports machine-local translation overrides. Run it
with only the pinned framework and collector Mods; do not turn other Mods' localization
contributions into vanilla catalog data.

The offline collector reads PE metadata with `System.Reflection.Metadata`; it never loads
`sts2.dll`. It records the assembly hash/MVID and the exact signature, signature hash, IL
hash, metadata token, and method-body shape for each reviewed target in
`adapter-targets-0.107.1.json`. The three existing-Ancient targets are the exact protected native
Ancient finish/page-flow methods and the initial-options replacement boundary. The 17
Availability targets cover the three cached pool getters plus Relic/Potion base and six concrete
unlock-filter overrides per category. Add no adapter merely to make a prompt pass.

## Exact target resolution

Resolve through `vanilla_overrides.py`, not a handwritten target whitelist:

```powershell
python ${GAME_TOOLS_DIR}/vanilla_overrides.py resolve STRIKE_IRONCLAD --category card
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

Every new scaffold contains `openmod/vanilla-overrides.json`:

```json
{
  "schema": "openmod.sts2.vanilla-overrides/v1",
  "mod_id": "ExampleMod",
  "profile": "ritsulib-0.5.4-sts2-0.107.1",
  "host_version": "0.107.1",
  "catalog_sha256": "0279fd5e95e7fc9a076f2319bc5ec74952389045f26837c0d72c89d6f416dd73",
  "operations": []
}
```

`build.py` validates this document before MSBuild. It is a build-time input that stays in
the project directory and is never deployed into `mods/<ModName>/`: the game parses every
`.json` under a deployed Mod directory as a Mod manifest and logs a load error for each one
without an `id`. The generated C# carries the accepted operations at runtime, so the
deployed Mod needs only its own `<ModName>.json`. `build.py` deletes a copy left by an older
build and fails on any other deployed non-manifest `.json`. Projects created before M6.7.0
remain buildable without a manifest and are reported as legacy/non-override projects.

Every promoted operation carries `order`, stable `operation_id`, resolved
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
Card operations include exact category/type baselines and the surface-specific fields in
`vanilla-card-overrides.md`. Visual operations also require exact content kind and a
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
- an unpromoted `probe` route;
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
- ambiguous same-Mod overlap on one target/surface.

Ordered Card tag/text/tip/glow/playability/owner-hook and behavior composition is preserved.
Costs allow one `set` followed by deltas, or deltas alone; a later `set` conflicts. Multiple
exclusive property/result/replacement operations conflict on the same target/surface.
Ancient append rules compose with other appends; one same-target replacement conflicts with
every append or replacement in the generated Mod.
External Mod compatibility is not inferred from this same-Mod check.

## Maintainer collection

The collectors are maintainer tools, not generated-Mod runtime dependencies:

```powershell
python games/sts2/tools/collect_vanilla_catalog.py create-runtime-project `
  --project-dir <empty-outer-dir> --mod-name OpenModM67Catalog

python games/sts2/tools/collect_vanilla_catalog.py collect-assembly `
  --assembly <sts2-data-dir>/sts2.dll --output <assembly-json>

python games/sts2/tools/collect_vanilla_catalog.py merge `
  --runtime <runtime-json> --assembly <assembly-json> `
  --promote-package m6.7.1-public-card-overrides `
  --promote-package m6.7.2-public-visual-overrides `
  --promote-package m6.7.3-existing-ancient-overrides `
  --promote-package m6.7.4-availability `
  --output games/sts2/skills/sts2-api/reference/vanilla-overrides/catalogs/sts2-0.107.1.json
```

Supporting another STS2 version requires a new runtime snapshot, assembly snapshot,
reviewed adapter-target file, merged catalog, and proof. Never change the version label on
an old catalog.

The collector's own development evidence established the exact profile, a repeatable
localized 1624-model snapshot, an identical assembly hash, a structured state proof,
`selftest done`, and no fresh collector error. That proves the collector, and nothing else.
No collector result is headed or behavioral proof for a vanilla edit, and neither is source
authoring plus focused checks on any override route: real-host behavior and presentation are
proved only by observing them in the nearest real consumer.
