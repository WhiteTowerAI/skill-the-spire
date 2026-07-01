# CLAUDE.md

Repo-specific rules for AI agents working in this repository. General Git/PR
conventions live in [AGENTS.md](./AGENTS.md); read that too. This file only
covers what is unique to **open-mod** and overrides AGENTS.md on conflict.

## Project

open-mod is a free, open-source project: a skill that enables text-to-mod
generation for supported games. It will eventually be published publicly, so
keep the public-facing history clean and professional.

## Branch model — READ THIS FIRST

There are three long-lived branches. Their roles are **not symmetric**. Know
which one you are on before doing anything.

| Branch          | Role                                                                 | Who writes                     |
| --------------- | -------------------------------------------------------------------- | ------------------------------ |
| `main`          | Public release branch. What the world / the boss sees. Must stay clean. | Boss, via PR only              |
| `Henry's_branch`| Henry's personal branch. Milestone snapshots and backups.            | Henry (the lead)               |
| `Henry's_cc`    | **Your working branch.** Edit freely here.                           | You (the AI agent)             |

### Hard rules

1. **`Henry's_cc` is your home.** Do all work here. You may modify anything and
   commit when it makes sense (see below).
2. **NEVER merge into `main`.** Not directly, not via PR, not ever. `main` is
   updated only by the human lead / boss through their own PR flow. This is a
   hard stop — if a task seems to require touching `main`, stop and ask.
3. **`Henry's_branch` is snapshot/backup only.** From time to time you may merge
   `Henry's_cc` into `Henry's_branch` locally to record a milestone, then commit
   there. Treat it as a checkpoint, not a place to develop.
4. Direction of merges is one-way: `Henry's_cc` → `Henry's_branch`. Never the
   reverse without the lead asking for it. Never anything → `main`.

## Commits

- **Wait to be asked before committing.** Don't commit automatically after every
  change. When work reaches a sensible checkpoint, either commit if the user has
  told you to, or ask if you should.
- **You write the commit message yourself** — follow the Conventional Commit
  style from AGENTS.md (`feat(...)`, `fix(...)`, `docs(...)`, etc.).
- Keep the `Co-Authored-By: Claude` trailer on commits you make, so AI
  authorship stays transparent in history.
- Commit specific files rather than blanket `git add .`, and flag anything that
  looks like a secret before staging it.

## Typical loop

1. Work on `Henry's_cc`.
2. Reach a checkpoint → commit on `Henry's_cc` (when asked / after confirming).
3. Occasionally merge `Henry's_cc` → `Henry's_branch` and commit there as a
   milestone/backup.
4. `main` is left alone. The lead PRs into it separately.

## Docs

Planning and research live in `documents/` (PROJECT.md, IMPLEMENTATION_PLAN.md,
BASELINE_RESEARCH.md, and the competitive-landscape notes). Read the relevant
ones before starting substantive work; keep them updated when plans change.
