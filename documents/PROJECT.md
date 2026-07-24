# open-mod project

## Product

open-mod gives non-programmers a credible path from one sentence to a working game mod.
It is a Codex plugin, not a web form or a code-snippet generator. The agent collaborates
with the user, records a semantic contract, writes the project, builds it, runs the real
game, and reports what was actually verified.

The first game is Slay the Spire 2. The project stays one game deep until the workflow and
support model are mature enough to extract a reusable platform.

## Release State

Version `0.6.0` is the first RitsuLib-only, externally accepted development baseline:

- host: STS2 stable `0.107.1`;
- compile package: `STS2.RitsuLib.Compat.0.107.1` `0.4.62`;
- runtime dependency: `STS2-RitsuLib >= 0.4.62`;
- primary runtime: Codex plugin;
- secondary distribution: portable Agent Skills payload.

BaseLib is no longer an implementation option. Historical BaseLib and Downfall checkouts
are offline research archives, not generated dependencies or runtime inputs.

The migration and clean-workspace Codex acceptance are complete. `0.6.0` remains
unreleased while user-test bugs are fixed and content quality is improved; no GitHub
release is currently planned.

## User Experience

The desired interaction is:

```text
plain-language idea
  -> one compact clarification round when needed
  -> plain-language plan
  -> semantic SPEC.md
  -> pinned scaffold and grounded recipes
  -> author and package
  -> real-game load proof
  -> hosted behavior proof or an honest manual boundary
```

The skill should preserve unusual mechanics instead of flattening them to the nearest easy
effect. It should recommend concrete defaults, avoid jargon, and tell the user when an idea
crosses the supported boundary.

## Architecture

The product has three layers:

1. `modmaker` owns the staged workflow and resumable project state (`SPEC.md`, `PLAN.md`,
   `MEMORY.md`).
2. `sts2-api` owns lazy, grounded game knowledge: recipes, lifecycle contracts, art
   consumers, verification hosts, and error fixes.
3. Python tools own deterministic scaffold, profile validation, build/package, launch,
   log parsing, and sprite normalization.

The semantic contract stays framework-neutral. RitsuLib details are concentrated in the
pinned scaffold/profile and the adapter/reference surface. Generated source is preferred
over a shared open-mod runtime until multiple independent consumers justify a versioned
binary.

## Verification Philosophy

Compilation is necessary but insufficient. A supported capability needs the lightest proof
that establishes its independent invariant:

- local assertions for pure calculations;
- a hosted real-game scenario for lifecycle and behavior;
- visible evidence when open-mod owns presentation;
- a fresh natural-language Mod for end-to-end acceptance.

Tier 1 means loaded with no fresh error. Tier 2 means a structured post-state marker plus
`selftest done`. Evidence density is not a goal; one proof per independent invariant is.

## Distribution

The Codex plugin manifest is `plugins/open-mod/.codex-plugin/plugin.json`; the repo-local
marketplace is `.agents/plugins/marketplace.json`. Both skills and their tools are bundled
inside the plugin with relative paths, so installation is independent of the user's current
workspace.

The portable payload at `skills/` follows the Agent Skills layout. Both payloads are
generated from `games/sts2/` and committed because installers consume repository content
directly.

## Product Boundaries

The current product supports the surfaces in
`games/sts2/tests/content-capability-graph.md`. It deliberately does not imply vanilla
editing, arbitrary patching, retained-card zones, alternative Energy, multiplayer UI,
production Character motion/audio, arbitrary Event layouts, or Workshop publishing.

M6.5 Character art and presentation is the active content-quality milestone, as scoped in
`documents/IMPLEMENTATION_PLAN.md`. M6.5.1 (CharacterArtBundle and the identity reference
chain) is complete; character-wide card/UI theming is next. User feedback and
explicit lead decisions may add later optimization work; no automatic milestone transition
follows from M6.5.
