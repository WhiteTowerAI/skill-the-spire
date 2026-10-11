# Grounding rules

Every symbol a generated Mod uses must be grounded before it is written: an exact public owner,
signature, lifecycle, and await behavior from one of the sources below. Never guess a name,
decompile code, or use a private or internal member.

## Four Sources

| Source | Answers |
|---|---|
| spire-codex / curated snapshots | what vanilla content exists, does, and resembles |
| pinned official RitsuLib tutorial distillations | player-facing purpose and documented feature-family membership |
| STS2 + RitsuLib source/decompile | exact C# commands, hooks, enums, templates, registries, and hosts |
| skill-the-spire profile/recipes/tests/live runs | what the generator implements and what was observed |

These are complementary. Official tutorial semantics plus public members in the pinned
profile make a documented feature family and all its public consumers supported. A vanilla
analog or tutorial example does not prove a stable-version C# signature, a decompiled
signature does not prove the pinned build profile, and a compiling model does not prove
behavior or presentation. Missing recipe or host verification does not remove support.
Record a concrete failure as the smallest known limitation.

## Runtime Lookup Order

1. Read the selected surface page and recipe.
2. Read only the referenced mechanics, state, presentation, art, or self-test page, and the
   shipped catalogs under `reference/catalogs/` when they cover the symbol.
3. Check `errors.md` for an exact failure signature.
4. If no maintained route covers the operation, implement it as a Mod-local route below.

## Mod-local Routes

A missing recipe is an authoring gap, not a stop condition. When no maintained route covers an
accepted operation:

1. Ground the exact public types and members in the pinned local assemblies the scaffold
   references (STS2, GodotSharp, RitsuLib). Use only public metadata: type and member names,
   signatures, and documentation. The compiler is the final check on every signature.
2. Write the smallest Mod-owned implementation that uses only those public members, ordinary
   C#/BCL, and Mod-owned state. Never use Harmony, reflection, Publicizer, IL, or runtime
   patching.
3. Record it in the SPEC `## Implementation` section as
   `- Mod-local: <operation> - <public Owner.Member list>`. The capability preflight ignores
   this line; keep `Support:` lines for the parts that do have maintained routes.
4. Record the grounded signatures in `MEMORY.md`.
5. Verify it in full: Build, Tier 1, and a Tier 2 SelfTest scenario that drives it through the
   real host and asserts its exact post-state, plus headed review when it has visible UI, input,
   or presentation. Until every required check passes, report it as unverified, not working.
6. Name every Mod-local route in the final report.

Stop and report the operation as unsupported only when it needs a private API, runtime patching,
or decompilation, or when it has no lifecycle the real host can verify. Offer a supported
alternative only with the user's explicit acceptance, because the player-visible result changes.

## Maintainer Research

Maintainers may improve the pack offline:

1. Use existing snapshots first.
2. Read the pinned official tutorial baseline for product semantics and feature-family
   membership. Its repository targets `public-beta`, so do not use it as stable-version
   signature authority.
3. Query a local spire-codex data dump or its attributed API for content facts.
4. Inspect the pinned STS2 `0.107.1` and RitsuLib `0.5.11` code for exact signatures.
5. Confirm build/load rules in `scaffold.py`, `ritsu_profile.py`, package metadata, and a
   focused hosted proof.
6. Add the complete documented API inventory and narrow known limitations to the
   capability graph. Add the smallest reusable semantic/API result to a shipped
   recipe/reference/error entry with its version and verification facts.

`baselines/BaseLib-StS2` and `baselines/downfall` are historical research only and are not
authoring or runtime sources for `0.1.0`. The official tutorial checkout is an active
maintainer semantics baseline but is likewise unavailable at runtime; only its reviewed
distillations belong in this shipped pack.
