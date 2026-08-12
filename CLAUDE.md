# CLAUDE.md

This repo is developed Codex-first. `AGENTS.md` is the canonical instruction file and is
kept current; this file exists only so Claude Code loads it too, plus the few notes that
are specific to running Claude Code here.

@AGENTS.md

## Precedence

1. `AGENTS.md` — canonical.
2. `documents/PROJECT.md` (release state), `documents/IMPLEMENTATION_PLAN.md` (milestones),
   `documents/history/*_RESULTS.md` (what each closed milestone actually proved).
3. Auto-memory — point-in-time notes, not live state. Where memory disagrees with
   `AGENTS.md` or `documents/`, the repo wins and the memory should be corrected.

## Claude-Code-specific notes

- `baselines/` is gitignored dev-only reference material. `@`-completion hides ignored
  paths, so read it by absolute path with Read/Grep. Never commit it, never let
  `publish.sh` ship it, and never write its paths into files the pack ships.
- Per-machine absolute paths (game install, .NET SDK, logs, workshop libs) stay in
  auto-memory rather than here, since this repo is meant to be portable.
