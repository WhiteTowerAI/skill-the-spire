# Grounding rules

The runtime skill reads this shipped pack only. It does not decompile local assemblies,
scan maintainer baselines, or browse for an API during a user's Mod build. If the pack does
not contain the needed signature, report a pack gap instead of guessing.

## Three Sources

| Source | Answers |
|---|---|
| spire-codex / curated snapshots | what vanilla content exists, does, and resembles |
| STS2 + RitsuLib source/decompile | exact C# commands, hooks, enums, templates, registries, and hosts |
| open-mod profile/tests/live runs | what builds, loads, packages, and is supported |

These are complementary. A vanilla analog does not prove a C# signature, a decompiled
signature does not prove the pinned build profile, and a compiling model does not prove
behavior or presentation.

## Runtime Lookup Order

1. Read the selected surface recipe.
2. Read only the referenced mechanics, state, presentation, art, or self-test page.
3. Check `errors.md` for an exact failure signature.
4. If the answer is absent, stop and identify the missing fact. Do not try a fourth guessed
   symbol or restore a historical framework path.

## Maintainer Research

Maintainers may improve the pack offline:

1. Use existing snapshots first.
2. Query a local spire-codex data dump or its attributed API for content facts.
3. Inspect the pinned STS2 `0.107.1` and RitsuLib `0.4.62` code for exact signatures.
4. Confirm build/load rules in `scaffold.py`, `ritsu_profile.py`, package metadata, and a
   focused hosted proof.
5. Promote the smallest reusable result into a recipe/reference/error entry with its
   version and support boundary.

`baselines/BaseLib-StS2` and `baselines/downfall` are historical research only and are not
authoring or runtime sources for `0.6.0`.
