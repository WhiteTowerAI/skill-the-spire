# Current baseline

This file records the references that still inform active design after the RitsuLib
migration. It is intentionally short; Git history retains the earlier survey.

## Active Runtime Baseline

open-mod targets:

- Slay the Spire 2 stable `0.107.1`;
- RitsuLib `0.4.62` and `STS2.RitsuLib.Compat.0.107.1`;
- .NET SDK 9;
- Codex plugin distribution plus a portable Agent Skills payload;
- cross-platform Python tools, with the complete loop currently verified on Windows.

`baselines/STS2-RitsuLib` is the maintainer checkout for API and compat research. Runtime
projects use the pinned package and installed runtime variant rather than copying that
checkout.

## Reused Design Ideas

The active architecture still borrows these durable ideas from the initial survey:

- **godogen:** file-based staged skills, publish-time rendering, progressive disclosure,
  and resumable state files;
- **spire-codex:** content facts and vanilla analogs, never C# API authority or a runtime
  dependency;
- **STS2/game decompile:** exact public command, lifecycle, enum, and host signatures used
  by maintainers to improve the shipped pack;
- **image tool research:** acquisition is optional and source-independent; deterministic
  normalization and verified consumers matter more than the image backend.

## Archived Research

`baselines/BaseLib-StS2` and `baselines/downfall` are retained only as offline historical
research. They explain pre-migration behavior and implementation depth. They must not be
used to scaffold, author, build, repair, or run a generated Mod.

Claude-specific baseline repositories may remain locally for historical comparison, but
the product and publish flow now target Codex. They are not required to build or install
`0.6.0`.

## Decision Rules

1. Semantic intent is framework-neutral; RitsuLib owns the active adapter.
2. A successful build is not a behavior or presentation claim.
3. Public game/RitsuLib APIs are preferred; a private patch needs a separately grounded
   and hosted contract.
4. Do not add a helper unless an existing supported surface needs it and one focused proof
   can establish it.
5. Do not make a paid network call or switch image backends without explicit user choice.
6. Keep runtime sessions inside the shipped pack. Live decompilation and baseline research
   are maintainer work, not steps in `$modmaker`.
