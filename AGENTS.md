# AGENTS.md

Repository guidance for coding agents working in open-mod.

## Project

open-mod is a free, open-source skill that turns a non-programmer's description into a
working game mod. The current target is **Slay the Spire 2 (STS2)**. The strategy remains
one game deep, then a reusable platform.

Read `documents/IMPLEMENTATION_PLAN.md` before substantive work. Completed milestone
records and long evidence logs live under `documents/history/`; they are not current
instructions.

## Current status

**M6 gameplay/programming core is complete. Direct next: M6 Static Art Expansion research
and implementation. M7 follows after that presentation pass. Animation is a later,
non-blocking expansion.**

Current pipeline-supported surfaces include:

- relic, potion, card, power, keyword, enchantment, and orb;
- monster + encounter, including deterministic/conditional move vocabulary;
- event / World Node;
- playable Character Foundation;
- combat resource with explicit all-or-nothing payment and generic live counter;
- bounded ordered **semantic** card-play buffer with visible state and deterministic output;
- stateful relic cadence for combat-local and run-persistent counters;
- placeholder or generated art for card/relic/power/potion, enchantment/orb icons, one
  static monster combat+bestiary body, and the normal event initial portrait, plus
  live-grounded text-only keyword card/tooltip
  presentation. Custom acquisition prefers a
  callable host-native raster image tool (`runtime-imagegen`; Codex `image_gen`), then the
  existing Vofy, BYO HTTP, or local-image routes; every source converges on
  `gen_sprite.py import`. Reference-capable routes use separate real-game pools for
  card/relic/power/potion/enchantment/orb/monster and randomly sample three type-matched
  images; event awaits its own bundled pool and must not borrow another family's
  references. An ignored local baseline currently inventories 56 deduplicated wiki.gg
  event PNGs as curation candidates; they are not pipeline samples until reviewed and
  attributed under `art-samples/event`.

Host-native image generation is an optional runtime capability, not a bundled model. Do
not infer it from the text-model name or the presence of an `imagegen` skill file: the
tool itself must be callable and return a local image. If it is absent or fails, keep the
placeholder unless the user explicitly selects another route. Never silently switch to a
paid backend. This route applies only to the eight already-grounded static specs and does
not advance any other M6 Static Art Expansion family.

Important correction from the real Wayfinder player run:

- Direction cards now use STS2's normal Play -> Discard lifecycle.
- The route stores only `RouteDirection` values in combat-scoped state and renders
  `Ink: N | Route: ...` through the verified fallback Label.
- Retaining played card instances in a `CustomPile` is **not supported**. The earlier
  model-only proof missed overlapping/stale card views. Do not generate a no-UI custom
  pile, `Vector2.Zero` card layout, or `skipVisuals: true` lifecycle as a substitute.

Still unsupported: editing vanilla content, retained-card zone UI, alternative-energy
engine hooks, production character art/animation, run-persistent character resources,
remote-player character UI, novel C/D patch targets, and one-click Workshop publishing.

## Direct next: M6 Static Art Expansion

M5.5 custom art covered card portraits and relic/power/potion icons. M6 Static Art Expansion now
also live-supports one normal event initial portrait at 3440x1613 and one 64x64
enchantment icon shared by the card tab and hover tooltip, plus one 100x100 orb icon shared
by the smart tooltip and trigger flash, all with checked fallbacks. Orb icon support is
deliberately separate from its persistent combat body: the latter still uses an explicit
Frost Spine scene and matching channel-SFX fallback.
Keyword presentation is also complete: the real hand card renders its auto-positioned
keyword text, its hover tooltip renders the localized title/description with an intentional
null icon, and the hosted proof preserves the keyword's behavior. A keyword owns no bitmap,
so it has no `gen_sprite.py` spec. Static monster art is also complete for the normal
profile: one checked 360x360 PNG feeds both combat and the default bestiary layout through
BaseLib's non-Spine factory, with correct bounds/intent placement and an explicit built-in
scene fallback. Finish the remaining M6 presentation work in this order:

- event reference curation, prompt maturity, phobia/later-page portraits, and non-animated
  custom/Ancient layouts;
- character select/static combat art and other non-animated character assets;
- richer character resource and ordered-buffer UI beyond the fallback Label.

All animation-bearing work is postponed to a later expansion: orb Spine bodies; monster
Spine and attack/hurt/cast/death/phobia/bestiary previews; character animation, trails, and
animated transitions; event portrait VFX; and optional UI motion. None blocks M6 or M7.

Do not reopen the completed M6 behavior canaries or jump to M7. First inventory the real
asset/scene contracts for these families, then extend the source-independent acquisition ->
normalization -> placement -> `.pck` path only where grounded. Reuse the existing hosted
suites; do not require one project per asset type. Art support advances only after the real
headed game renders the intended asset with visual evidence. A model path, successful build,
or fallback visual is not enough. Record exact blockers and keep an honest fallback for any
static scene family that cannot yet be generated safely. Do not reopen animation work.

The `runtime-imagegen` edge may be reused for card/relic/power/potion, enchantment/orb
icons, a static monster body, and a normal event initial portrait because their import and headed render contracts are
live-grounded. A universal first-party Codex native-tool claim still requires a dedicated
acceptance run; the current third-party Codex route exposes the instructions but not a
callable `image_gen` tool.

## Architecture

- `games/sts2/skills/modmaker/`: staged orchestrator
  (`interview -> spec -> scaffold -> author -> build -> verify -> repair`).
- `games/sts2/skills/sts2-api/`: lazy game pack with recipes, references, and errors.
- `games/sts2/tools/`: cross-platform Python build/launch/log/art wrappers.
- `games/sts2/tests/`: current verification strategy and support graph only.
- `plugins/open-mod/`: committed Claude plugin payload, generated by `publish.sh --plugin`.
- `skills/`: committed portable Agent Skills payload, generated by
  `publish.sh --portable`.
- `documents/history/`: completed milestone/process evidence. Never use it as the current
  API or support contract.

Edit source under `games/sts2/`; never hand-edit generated payloads. Regenerate both
committed payloads after source changes.

## Verification model

Keep verification lean. Do not automatically create a new canary project for every
capability or bug.

1. **Contract checks:** deterministic calculations and state rules use the lightest local
   assertion/test available.
2. **Hosted live suites:** reuse the closest real scenario (`CombatPlayer`, `CombatEnemy`,
   `MapNode`, `RunStart`/Character). Add a separate project only when it is the clearest
   maintainable shape; there is no project-count rule.
3. **Acceptance mods:** fresh natural-language runs prove the pipeline end to end, then
   their one-off work directories may be retired after durable evidence is recorded.

One live proof per independent semantic invariant. Do not repeat additive values merely to
make evidence look denser. For any custom presentation or lifecycle, player-visible state
is part of correctness; model state alone is insufficient.

Tier 1 requires the exact load marker and no fresh error block. Tier 2 requires a structured
post-state proof plus `selftest done`; trigger/preview logs and terminal markers alone never
prove behavior. Run one armed harness mod at a time.

See `games/sts2/tests/README.md` for current suite ownership and commands.

## Branch model

| Branch | Role | Who writes |
|---|---|---|
| `main` | Public release branch | Human lead via PR only |
| `Henry's_branch` | Milestone snapshot/backup | Human lead/checkpoint work |
| `Henry's_cc` | Agent working branch | AI agent work |

Hard rules:

1. Work on `Henry's_cc`.
2. Never merge into `main` or open a PR to it.
3. `Henry's_branch` is snapshot-only; merge direction is `Henry's_cc` ->
   `Henry's_branch` only when the lead asks.
4. Preserve unrelated dirty-worktree changes.

## Commits

- Wait to be asked before committing.
- Use Conventional Commit messages and an appropriate AI co-author trailer.
- Stage specific files, never blanket `git add .`.
- Flag anything resembling a secret before staging.

## Toolchain

Verified Windows environment:

- STS2 stable `0.107.1`
- .NET SDK `9.0.300`
- BaseLib `3.3.5`
- Python 3

Scaffold from a dedicated empty outer directory whose name differs from the mod name:

```bash
dotnet new install Alchyr.Sts2.Templates
dotnet new alchyrsts2contentmod -n <ModName> -M <Author>
# Character projects:
dotnet new alchyrsts2charmod -n <ModName> -M <Author>
```

Enable `BSchneppe.StS2.PckPacker`, then use:

```bash
python games/sts2/tools/build.py --project-dir <project> --mod-name <ModName>
python games/sts2/tools/launch.py
python games/sts2/tools/grep_log.py --mod-name <ModName>
python games/sts2/tools/launch.py --self-test --mod-name <ModName>
python games/sts2/tools/grep_log.py --mod-name <ModName> \
  --tier2-pattern "<structured state proof>"
```

`launch.py --self-test` arms every loaded harness mod. Keep only the target harness in the
game's `mods/` directory for that run and restore any parked user mods afterward.

## Documentation

Active planning/research:

- `documents/PROJECT.md`
- `documents/IMPLEMENTATION_PLAN.md`
- `documents/BASELINE_RESEARCH.md`
- `games/sts2/tests/README.md`
- `games/sts2/tests/content-capability-graph.md`

Historical evidence is indexed at `documents/history/README.md`.
