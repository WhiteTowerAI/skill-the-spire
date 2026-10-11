# CLAUDE.md

`AGENTS.md` is the canonical instruction file for every coding agent in this repo and is imported
below. This file only adds what is specific to running Claude Code here. When the two disagree,
`AGENTS.md` wins; fix this file rather than working around it.

@AGENTS.md

## Ship Targets

Development and local testing now happen in Claude Code on this machine. The product ships a
Codex plugin (marketplace `.agents/plugins/marketplace.json`) and a Claude Code plugin
(marketplace `.claude-plugin/marketplace.json`). Both plugins are rooted at the one generated
top-level `skills/`, which `npx skills add` also installs; their `plugin.json` sources live in
`scripts/publish/`. Never fork the skill text per agent or edit the generated payload. Keep both
plugins working.

## Shell On This Repo

- The Bash tool runs Git Bash, so `publish.sh` runs directly: `bash ./publish.sh --force`.
  The `& 'D:\Git\bin\bash.exe' ...` form in `AGENTS.md` is for the PowerShell tool.
- Run the `AGENTS.md` test commands in the PowerShell tool as written. From Git Bash, use
  `PYTHONUTF8=1 python -m unittest ...` instead of `$env:PYTHONUTF8='1'`.
- Build, launch, and log tools write detail to files and print a short verdict. Ad-hoc commands
  follow the same rule: write long output (dotnet builds, `godot.log`) to a file and return a
  summary, a count, or the last few matching lines.
- Launching STS2 and headed review need the user's machine and eyes. Ask plainly.

## Reference Material

- `baselines/` is gitignored, maintainer-only reference material (game decompile, RitsuLib source,
  other research checkouts). `@`-completion hides ignored paths, so read it by path with Read and
  Grep. Check API signatures by grepping `baselines/decomp/` and `baselines/STS2-RitsuLib/src/`
  before reaching for `ilspycmd`.
- Shipped files may cite `baselines/` as provenance but must never tell a user's runtime to read
  it. Never ship `baselines/`, absolute dev paths, or decompiled code.
- Pre-release planning docs (`documents/`, the old milestone history) were pruned from the public
  tree in `68074e0`. Read them from git history when needed, for example
  `git show 68074e0^:documents/PROJECT.md`. They are history, not current instructions.

## Memory

Machine-specific paths (game install, RitsuLib Workshop item, MegaDot, .NET, logs) live in Claude
Code auto-memory, not here. Memory is a point-in-time note: where it disagrees with `AGENTS.md`
or the code, the repo wins and the memory gets corrected.
