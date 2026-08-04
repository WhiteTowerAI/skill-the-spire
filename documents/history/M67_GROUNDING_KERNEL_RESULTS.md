# M6.7.0 grounding kernel interim development record

Date: 2026-08-03

## Status

M6.7.0 source development is implemented for the pinned STS2 `0.107.1` / RitsuLib `0.5.4`
profile. It adds deterministic target grounding, checked localized display-title aliases,
and an empty semantic override manifest. It does not promote any gameplay override
operation, adapter target, or prompt-generated patch.

This is not a final package result. On 2026-08-03 the human lead deferred the
current-catalog no-op build/Tier 1, full repository regression, payload synchronization,
final result consolidation, and temporary-project/deployment cleanup into one consolidated
M6.7 closure pass. Earlier payload/no-op evidence in this file predates the localized-title
catalog and is explicitly superseded. M6.7.1 is authorized as the next development package
for a fresh session.

## Delivered kernel

- a one-shot real-host `ModelDb` collector filtered to concrete types from the game
  assembly;
- an offline PE metadata collector based on `System.Reflection.Metadata`, without loading
  `sts2.dll`;
- a merged, digest-checked per-version catalog and exact normalized internal/localized-title
  alias resolver;
- stable RitsuLib title table/key mappings plus checked title text for all 14 pinned game
  languages, collected through the public temporary-language route and rejected when local
  translation overrides are active;
- a semantic manifest pinned to Mod id, host, profile, and catalog digest;
- exact recursive expected-baseline comparison;
- reviewed adapter signature/IL/body-shape records and fingerprint checks, with an empty
  target set in this package;
- same-Mod overlap detection and rejection of unpromoted probes or implementation-shaped
  Harmony/reflection/Publicizer/IL fields;
- scaffold emission, pre-MSBuild validation, loose-artifact deployment, and exact deployed
  manifest comparison; and
- legacy-project compatibility when no source override manifest exists.

## Pinned catalog identity

```text
profile: ritsulib-0.5.4-sts2-0.107.1
sts2.dll SHA-256: a1f9e653f1e28e4076558fee1e60d218619cb7e057b887c6417f62c62c6d7a52
sts2.dll MVID: 97f10687-c306-4798-ab75-8b9f23f34dfb
sts2.dll size: 9364480
model-namespace metadata types: 3883
runtime vanilla models: 1624
models with stable title localization sources: 1580
models with English titles: 1537
models with Simplified Chinese titles: 1537
catalog languages: deu, eng, esp, fra, ita, jpn, kor, pol, ptb, rus, spa, tha, tur, zhs
catalog SHA-256: 4c930d9a6161ed52fa435df2c97e8d492efac571a04928811e5b9299d4e41311
serialized catalog file SHA-256: 20ca1e480393dc9954be40310bfda7e0cbb1958435d6f30e98310491f49cd9c0
adapter targets: 0
promoted operation packages: 0
```

The runtime inventory included 584 Cards, 297 Relics, 65 Potions, and 126 Monsters. It
also retained 45 cataloged debug/mock records, which normal target resolution excludes by
default.

## Collector corrections

The first real-host attempt failed after the load marker with
`CanonicalModelException` while reading `EnchantmentModel.ShouldReceiveCombatHooks`.
That property reaches mutable Card-instance state and is invalid on a canonical
Enchantment. The collector removed the unsafe universal property read and kept the
category-specific canonical fields that can be observed without bypassing the model's
mutability contract.

The first complete catalog used only internal `ModelId`/type-derived aliases. That was not
sufficient for non-programmers who name vanilla content by the title shown in game.
RitsuLib `0.5.4` publicly maps 14 title-bearing model families to stable localization
table/key pairs, and the pinned game publicly documents `LocManager.SetLanguage` as a
temporary change that does not update the player's saved setting. The collector now reads
all 14 pinned languages, restores the original language in `finally`, and refuses to write
machine-local translation overrides.

The localized-title collector wrote the complete snapshot twice with identical bytes:

```text
runtime snapshot SHA-256: 12e3d5dbbea9a828c23cdbeb16ece329cd8c24cbf83ccfa8ad15d8177c47a788
runtime models: 1624
assembly SHA-256: a1f9e653f1e28e4076558fee1e60d218619cb7e057b887c6417f62c62c6d7a52
```

Both current collector runs had the exact load/profile marker, structured catalog state,
`selftest done`, and no fresh error after load. `CARD.STRIKE_IRONCLAD` records `Strike`,
`打击`, and the other checked localized titles. `恶魔形态` resolves uniquely to
`CARD.DEMON_FORM`; `Strike`/`打击` correctly fail as ambiguous across the five
Character-specific starting Cards.

## Current development checks

Focused Python tests:

```text
python -m unittest games.sts2.tools.tests.test_vanilla_overrides -v
15 tests passed
```

They cover deterministic merge/digest, the checked real catalog identity and title counts,
exact localized-title resolution, ambiguous display names, unknown suggestions,
host/profile/assembly/catalog/baseline drift,
empty-manifest success, nonempty-package rejection, unknown targets, duplicate operation
ids, exclusive conflicts, ordered delta composition, probe rejection, adapter fingerprint
drift, forbidden implementation fields, scaffold emission, legacy compatibility,
pre-MSBuild rejection, and deployed-manifest equality.
The suite also locks the checked catalog digest and requires both authoring skills to route
existing-content requests through the grounding reference.

The current localized-title collector project compiled with no C# errors. The deployment
build retained two `NU1900` warnings because the offline environment could not reach NuGet
vulnerability data; those warnings did not change the already-resolved pinned `0.5.4`
package. Both current real-host runs produced:

```text
Tier 1 load marker: passed
profile match: passed
structured state proof: passed
selftest done: present
fresh errors after load: none
strict Tier 2: passed for catalog-file state
```

This collector-only strict Tier 2 proves that the current localized catalog file was written
with the expected model count and assembly/file hashes. It is not gameplay-behavior or
headed-presentation evidence for a vanilla edit.

## Deferred closure checks

The following checks have not run against the current localized-title catalog and must not
be reported as passes:

- the complete repository Python regression suite after the localized-title correction;
- the current-catalog fresh no-op Mod build, deployed-manifest equality, and Tier 1;
- plugin and portable payload regeneration, parity, and repeatable tree digest;
- final consolidated M6.7 real-host and headed matrices; and
- final result consolidation and disposable-project/deployment cleanup.

A new `M67NoopProof` was scaffolded with the current catalog digest, but it was not built or
launched before the human lead selected batched M6.7 verification. The source project and
collector deployment remain temporary development artifacts for later consolidated cleanup.

## Superseded pre-localization evidence

Before localized display titles changed the runtime/catalog schemas and digest, the earlier
internal-name-only kernel had passed 140 repository tests, Python compilation, a fresh no-op
Tier 1, and plugin/portable parity. Its payload tree digest was:

```text
7b5f99f998e07a09c72272a7d023544e65ea9871deee564511a60628bd79690c
```

Those checks describe the superseded `v1` catalog only. The committed/generated payload
directories still contain that older kernel and are intentionally stale during M6.7 batch
development. They do not deliver or validate the current `v2` localized-title catalog.

## Retained boundary

The catalog is compatibility data, not permission to copy game source/assets or invent a
patch. `promoted_operation_packages` is empty, so `build.py` rejects every nonempty
manifest. M6.7.0 does not support a Card number edit, visual replacement, pool change,
Ancient extension, behavior composition/replacement, or multiplayer override. Each begins
only in its scheduled later package with its own grounded route and focused development
checks; proportional real-host and delivery proof is consolidated at M6.7 closure.
