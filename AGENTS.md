# AGENTS.md

Repository guidance for coding agents working on Skill the Spire.

## Product

Skill the Spire is a free Codex and Claude Code plugin that turns a non-programmer's description into a working
game Mod. Slay the Spire 2 is the first supported game. Version `0.2.0` targets STS2 stable
`0.107.1` and the RitsuLib `0.6.7` authoring/API baseline; `0.1.0` targeted RitsuLib
`0.5.11`.

The plugin ID, marketplace ID, and repository slug are `skill-the-spire`. The shipped skills are
`modmaker` and `sts2api`. Use normal SemVer for later releases.

## Workflow

```text
idea -> DESIGN.md -> SPEC.md -> capability_preflight.py -> scaffold and author
     -> Build -> Tier 1 -> Tier 2 / SelfTest -> headed review when needed
     -> direct report from actual results
```

`DESIGN.md` records intent, accepted decisions, current scope, and explicit `Not Now` items.
`SPEC.md` is the implementation work order: exact content, behavior, values, state, bilingual
text, presentation, selected support routes, and autotest scenarios. `PLAN.md` is a plain stage
checklist. `MEMORY.md` stores technical facts, commands/results, and repair attempts.

Run one pre-Author checker:

```powershell
python ${GAME_TOOLS_DIR}/capability_preflight.py --spec SPEC.md
```

It checks selected route existence and raw model-hook identity, shape, ownership, and surface
reachability. Do not turn it into a general Markdown, C#, manifest, localization, runtime, visual,
or evidence validator.

## Source Ownership

- `games/sts2/skills/modmaker/`: routing and generation stages.
- `games/sts2/skills/sts2api/`: design references, recipes, API contracts, catalogs, and errors.
- `games/sts2/tools/`: scaffold, build, pack, launch, log, profile, localization, art, catalog,
  and preflight tools.
- `games/sts2/tests/`: generated-Mod verification guidance.
- `scripts/publish/`: publisher helpers, the generated notice, and the Codex and Claude Code
  `plugin.json` sources. Keep the `version` in both equal.
- `.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json`: hand-maintained
  marketplace manifests. Both point at `./skills`.

Top-level `skills/` is the one generated payload and the plugin root for both Codex and Claude
Code; the publisher copies their `plugin.json` files into `skills/.codex-plugin/` and
`skills/.claude-plugin/`. `npx skills add` installs the same tree. Never hand-edit it. After
authoritative source validation, regenerate it with:

```powershell
& 'D:\Git\bin\bash.exe' './publish.sh' '--force'
```

Run it once and check that the payload diff matches the source change. Run it twice only when the
change touches `publish.sh` or `scripts/publish/`. The publisher owns payload layout, rendered
path tokens, and the generated notice. Skill text is shared by every agent, so keep it
agent-neutral.

## Runtime Contract

- Generated Mods target STS2 `0.107.1` and RitsuLib `0.6.7`, compiling against its
  `compat/0.107.1/` and `shared/` modules.
- Runtime manifests require only `STS2-RitsuLib >= 0.6.7` while generated code stays inside that
  API baseline.
- Runtime discovery accepts a validated game-local install or official Workshop item
  `3747602295`, with exact host/Compat identity checks.
- Generated projects have no framework `PackageReference` and no BaseLib dependency.
- Maintainer research and decompiled code are never generated-project inputs and are never copied,
  compiled, packaged, or shipped.
- Generated code may use pinned public STS2/RitsuLib APIs, ordinary C#/BCL, Mod-owned helpers and
  state, and maintained fixed Adapters. Never generate prompt-derived Harmony, reflection,
  Publicizer, or IL.

## Supported Boundary

The shipped pack is authoritative: `sts2api/SKILL.md` routes each feature family to its recipe
or reference, and that page states its own limitations and unsupported operations. Record a new
limitation or boundary there, not in a separate inventory. Keep these facts distinct:

- `framework-expressible`: the pinned public/fixed API can express the operation;
- `skill-the-spire-authorable`: shipped recipes/references cover implementation and proof; and
- `game-observed`: the exact shape ran successfully in the real host.

Missing runtime proof means unobserved, not automatically unsupported. A confirmed public/API or
lifecycle problem is recorded as the smallest exact limitation. A missing maintained route does
not block authoring: the generated Mod implements the operation as a Mod-local route from pinned
public APIs (`sts2api/grounding.md` § Mod-local Routes) and must pass Build, Tier 1, Tier 2, and
any needed headed review before it is reported as working. A broken maintained route is a pack
defect to repair.

## Localization And Art

Mods without localization tables remain language-neutral. Once any table exists, generated Mods
require `eng` and `zhs`, identical table/key sets, the same SmartFormat variables and
`:diff()`/`energyIcons()`/`starIcons()` values (grammar formatters such as `plural` may differ
per language, as in vanilla Chinese), and nonempty values. Build checks the static contract;
Tier 2 resolves both languages in real consumers and restores the original language.

Player-facing text follows the pinned vanilla style in
`games/sts2/skills/sts2api/reference/vanilla-text-style.md`: glossary terms and highlight
colors, per-surface number presentation and line breaks, and native Chinese punctuation and
measure words. The glossary `text-glossary-sts2-0.107.1.json` is generated from the installed
game by `collect_text_glossary.py`; never hand-edit it. Build fails on broken rich-text markup
and reports style drift as warnings. Translation quality beyond that is human-owned.

Art normalization facts live in `gen_sprite.SPECS`, `character_art.CHARACTER_ART_BUNDLE`, and the
generated art catalog. Never hand-edit that catalog. Generated art passes through
`gen_sprite.py import`; placeholder is the default unless the user selects a callable image route.
Do not silently select a paid backend.

## Verification

- Build proves compilation, packaging, manifests, resources, localization shape, and deployable
  static artifacts under the pinned profile.
- Tier 1 proves the exact load marker, framework/host/Compat identity, and no fresh error block.
- Tier 2 runs the arg-gated `SelfTest.cs` in real STS2, drives the selected scenario, waits for
  queued behavior, asserts exact structured post-state, and requires `selftest done`.
- `played`, `fired`, and `used` logs are diagnostics only.
- Headed review owns images, UI, mouse/controller interaction, animation, audio, and subjective
  judgment.

Report only checks that actually ran. Source/static/payload results are not Tier 1, Tier 2,
cross-platform, headed, or gameplay proof.

## Tests

Keep tests that protect supported authoring routes, generated artifacts, static build boundaries,
or real verification mechanisms. Remove tests that only enforce prose, headings, milestone
wording, management schemas, or historical evidence.

Use UTF-8 explicitly:

```powershell
$env:PYTHONUTF8='1'
python -m unittest discover -s games/sts2/tools/tests -p 'test_*.py'
git diff --check
```

Before release, install the plugin from this checkout on the maintainer's machine and invoke the
skill once: in Claude Code with `claude plugin marketplace add <repo>` and
`claude plugin install skill-the-spire@skill-the-spire`, then `/modmaker`. Also install it in Codex
with `codex plugin marketplace add <repo>` and `codex plugin add skill-the-spire@skill-the-spire`,
then `$modmaker`, when `scripts/publish/codex-plugin.json` or `.agents/plugins/` changed. Do not leave `__pycache__`
or other build output inside `skills/`; it invalidates payload parity.

## Git

`main` holds released, reviewed work. Do not develop on `main` and never commit to it directly;
changes reach `main` only through a merged PR.

The agent ships its own work end to end. Once a change is done, commit it on its branch, push,
open the PR, and merge it yourself with a merge commit (`gh pr merge --merge`). Then switch
back to `main` and pull. Do not stop at an open PR. Merge only when every check the
Verification and Tests sections require has run and passed, and the PR's CI, if any, is
green. Leave the PR open and say why when a check fails, the merge conflicts, or the user asked
to review first.

- Prefer small PRs focused on one feature, one bug fix, one chore, or one refactor.
- Use branches:
  - `feat/<short-name>`
  - `fix/<short-name>`
  - `chore/<short-name>`
  - `refactor/<short-name>`
  - `docs/<short-name>`
- Use Conventional Commit style for PR titles:
  - `feat(editor): add marquee selection`
  - `fix(runtime): handle missing tween state`
  - `docs(agents): update collaboration rules`
- PR descriptions must include:
  - What changed
  - Why it changed
  - How it was checked: only checks that actually ran, per the Verification section above

Check `git status` before editing. Preserve unrelated dirty/untracked work. Stage only intended
paths. Never reset, clean, rewrite history, force-push, install, launch, tag, release, or
change repository visibility without explicit authorization. Merging your own PR as described
above needs no further authorization.
