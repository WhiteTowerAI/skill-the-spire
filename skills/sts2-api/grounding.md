# Grounding rules

The runtime skill reads this shipped pack only. It does not decompile local assemblies,
scan maintainer baselines, or browse for an API during a user's Mod build. If the pack does
not contain the needed signature, report a pack gap instead of guessing.

## Four Sources

| Source | Answers |
|---|---|
| spire-codex / curated snapshots | what vanilla content exists, does, and resembles |
| pinned official RitsuLib tutorial distillations | player-facing purpose and documented feature-Package membership |
| STS2 + RitsuLib source/decompile | exact C# commands, hooks, enums, templates, registries, and hosts |
| open-mod profile/recipes/tests/live runs | what the generator implements and what was observed |

These are complementary. Official tutorial semantics plus public members in the pinned
profile make a documented feature Package and all its public consumers supported. A vanilla
analog or tutorial example does not prove a stable-version C# signature, a decompiled
signature does not prove the pinned build profile, and a compiling model does not prove
behavior or presentation. Missing recipe or host verification does not remove support.
Record a concrete failure as the smallest known limitation.

## Runtime Lookup Order

1. Read the selected surface recipe.
2. Read only the referenced mechanics, state, presentation, art, or self-test page.
3. Check `errors.md` for an exact failure signature.
4. If the answer is absent, stop and identify what is missing. A supported surface with no
   recipe needs maintainer authoring work; an ungrounded symbol needs API research. Do not
   try a fourth guessed symbol or restore a historical framework path.

## Maintainer Research

Maintainers may improve the pack offline:

1. Use existing snapshots first.
2. Read the pinned official tutorial baseline for product semantics and feature-Package
   membership. Its repository targets `public-beta`, so do not use it as stable-version
   signature authority.
3. Query a local spire-codex data dump or its attributed API for content facts.
4. Inspect the pinned STS2 `0.107.1` and RitsuLib `0.5.11` code for exact signatures.
5. Confirm build/load rules in `scaffold.py`, `ritsu_profile.py`, package metadata, and a
   focused hosted proof.
6. Add the complete documented Package inventory and narrow known limitations to the
   capability graph. Add the smallest reusable semantic/API result to a shipped
   recipe/reference/error entry with its version and verification facts.

`baselines/BaseLib-StS2` and `baselines/downfall` are historical research only and are not
authoring or runtime sources for `0.7.0`. The official tutorial checkout is an active
maintainer semantics baseline but is likewise unavailable at runtime; only its reviewed
distillations belong in this shipped pack.
