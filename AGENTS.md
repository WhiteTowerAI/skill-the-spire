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

**M0-M6 are complete at their grounded support boundaries. The final Character/tooling pass
promoted eight static Character consumers and a richer icon+text mechanic UI, inventoried the
wider Downfall/BaseLib surface, and completed the requested Ancient name-banner/Architect
research without claiming an unrun native-host proof. Direct next: M7 proactive interview
work. Animation, materials, multiplayer presentation, and audio are a later,
non-blocking expansion.**

Current pipeline-supported surfaces include:

- relic, potion, card, power, keyword, enchantment, and orb;
- monster + encounter, including deterministic/conditional move vocabulary;
- event / World Node, including Cmd/page/selection/reward outcomes, resumable or terminal
  special combat, bounded normal-layout `portrait_halo` VFX, and vanilla-observed rich
  text in page/option descriptions; enabled typed option Hover Tips, normal relic-backed
  title/description/metadata, native exact-lethal HP/Max HP warnings, Card/relic acquisition
  presentation, preference-respecting `weak_short` screen shake, curated built-in
  `trial_noble` VFX, and a solo bounded Quest Card that forces one custom Event from an
  Unknown MapPoint in one specified act;
- bounded per-surface rich text in Card bodies and standard Card/relic/potion/power Hover
  Tips, including SmartFormat and auto-keyword composition;
- playable Character Foundation;
- combat resource with explicit all-or-nothing payment and a fixed icon+text live counter
  with checked text-only fallback;
- bounded ordered **semantic** card-play buffer with visible state and deterministic output;
- stateful relic cadence for combat-local and run-persistent counters;
- Character static presentation for the 132x195 selection portrait, 1920x1200 selection
  background, 88x88 top-panel icon, 512x512 non-Spine combat/rest/merchant bodies, five
  256x256 full-energy layers, and 24x24 compact resource icon;
- placeholder or generated art for card/relic/power/potion, enchantment/orb icons, one
  static monster combat+bestiary body, and normal event initial/explicit page portraits, plus
  live-grounded text-only keyword card/tooltip
  presentation. Custom acquisition prefers a
  callable host-native raster image tool (`runtime-imagegen`; Codex `image_gen`), then the
  existing Vofy, BYO HTTP, or local-image routes; every source converges on
  `gen_sprite.py import`. Reference-capable routes use separate real-game pools for
  card/relic/power/potion/enchantment/orb/monster/event and four Character reference families,
  and randomly sample three
  type-matched images. Event's six reviewed samples were promoted from the actual local
  inventory of 55 deduplicated wiki.gg PNGs and are attributed under `art-samples/event`.

Host-native image generation is an optional runtime capability, not a bundled model. Do
not infer it from the text-model name or the presence of an `imagegen` skill file: the
tool itself must be callable and return a local image. If it is absent or fails, keep the
placeholder unless the user explicitly selects another route. Never silently switch to a
paid backend. This route applies to the eight established static specs plus the eight
promoted Character specs; full energy uses five `character_energy` outputs. It does not
advance an unverified consumer.

Important correction from the real Wayfinder player run:

- Direction cards now use STS2's normal Play -> Discard lifecycle.
- The route stores only `RouteDirection` values in combat-scoped state and renders
  `Ink: N | Route: ...` through the verified 220x32 icon+text control, with the live Label
  retained as its checked fallback.
- Retaining played card instances in a `CustomPile` is **not supported**. The earlier
  model-only proof missed overlapping/stale card views. Do not generate a no-UI custom
  pile, `Vector2.Zero` card layout, or `skipVisuals: true` lifecycle as a substitute.

Still unsupported: editing vanilla content, retained-card zone UI, alternative-energy
engine hooks, production character art/animation, native custom-Character Ancient presentation,
run-persistent character resources,
remote-player character UI, novel C/D patch targets, direct Event transitions to merchant/
rest/treasure rooms, more than one special combat per mutable Event instance, arbitrary
Event VFX/custom/Ancient layouts, locked-option Hover Tips, relic images in normal Event
options, arbitrary forced Event chains/multiplayer/save-roundtrip claims, and one-click
Workshop publishing.

## Completed: M6 native presentation quick wins

M5.5 custom art covered card portraits and relic/power/potion icons. M6 Static Art Expansion now
also live-supports normal event initial/explicit page portraits at 3440x1613 and one 64x64
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
scene fallback. The Event runtime/static contract is also complete: six attributed
references feed its source-grounded prompt; initial and explicit page portraits share the
checked 3440x1613 profile; phobia mode retains the current portrait; and custom phobia,
custom layout, and Ancient assets are explicitly deferred behind grounded BaseLib/scene
blockers. That acquisition gate closed on 2026-07-20: one approved
`seedream-5.0-lite` `21:9`/`2K` request used three randomly selected Event references,
produced an inspected 3440x1613 portrait, and rendered from the rebuilt `.pck` in the real
Event room with strict Tier 2 and no fresh error. The first three native-presentation
candidates closed on 2026-07-20; items 4-6 closed together in one compact headed proof on
2026-07-21:

1. **complete:** bounded rich text in Card bodies and standard Hover Tips;
2. **complete at the normal-layout boundary:** enabled Event option Hover Tips and normal
   relic-backed text/metadata; locked tips are suppressed and relic images are Ancient-only;
3. **complete:** native exact-lethal warnings for HP/Max HP costs;
4. **complete:** native Card/relic acquisition previews with exact single-grant ordering;
5. **complete:** the preference-respecting `weak_short` one-shot screen-shake profile;
6. **complete:** the curated built-in `trial_noble` noncombat Event VFX with exact
   placement, inherited process mode, and cleanup.

The final M6 Character pass completed on 2026-07-21. One headed Wayfinder run visibly
proved the custom selection portrait/button, top-panel identity, exact 512x512 non-Spine
combat body, and compact 24x24 icon inside the fixed resource/route control. Its full
two-combat Foundation/resource/buffer suite reached `selftest done`, strict Tier 2, and no
fresh error. A follow-up then proved raw `.tscn` selection-background/rest/merchant wrappers
and BaseLib's five-layer full-energy factory without Godot/MegaDot. `build.py` automatically
repacked the mod through the bundled `pack_pck.py`; real selection, CombatPlayer, RestSite,
and Shop hosts rendered the exact resources. Static merchant requires the version/MVID-gated
`NMerchantCharacter._Ready()` B-prefix because BaseLib 3.3.5 assumes Spine in that method;
the getter retains its inherited fallback when the patch is unavailable. Locked selection
and map marker still need visible-host proof.

The same pass completed the requested Ancient/Architect research: the native banner uses
`NAncientNameBanner` plus `RichTextAncientBanner` for uppercase title/epithet; Architect
dialogue and attacks consume Character speech color, four required loc keys, and
`GetArchitectAttackVfx()`. No headed custom-Character Ancient run occurred, so native
Ancient presentation and custom Ancient layouts remain unsupported. Vofy preflight stopped
at status/auth before submission; no paid task ran and no credits were spent.

The Event outcome/VFX follow-up is also complete. One final headed `CanaryEvent` run drove
page Cmd, upgrade selection, resumable custom combat, custom Gold reward, terminal custom
combat from a fresh Event instance, and explicit VFX cleanup. Its expected/observed outcome
families matched, `resumes=1/0`, `selftest done`, and no fresh error. That suite's generated
VFX is one code-native normal-layout `portrait_halo` with Fast Mode handling; BaseLib's
`CustomVfxPath` remains unused.

The bounded forced-follow-up Event composition is also complete. One custom unplayable
Quest Card may override the public Unknown-room and next-Event hooks only in one specified
act; its custom target Event stays out of ordinary pools with `IsAllowed == false`, and one
named option completes/removes the token. A single successful 37.5-second headed
`CanaryForcedEvent` run proved no-token/wrong-act pass-through, real Unknown MapPoint room
and Event forcing, visible target UI, token `1 -> 0`, restored hook outputs, `selftest done`,
and no fresh error. This does not generalize arbitrary chains, multiplayer, duplicate-token
rewards, fixed-node ordering, or save/resume.

The same hosted Event suite now also proves normal-layout rich text without generated VFX
code. Page and option descriptions may use the vanilla Event subset: `b`; `aqua`, `blue`,
`gold`, `green`, `orange`, `purple`, `red`; and `jitter`/`sine`. Titles stay plain. The
headed proof resolved the real BBCode label and required effect types, showed the initial
styled text, replaced it on a later page, and passed the existing strict outcome proof with
`richText` added and no fresh error. Ancient name-banner text is not part of this support;
it is a dedicated Character-phase presentation item.

The disposable `CanaryPresentation` suite proved the first three native-presentation
items. A real hand Card and standard typed Card/relic/potion/power Hover Tips rendered their
surface-specific bounded colors while preserving SmartFormat and keyword composition.
Enabled Event options displayed typed tips; locked options kept tip data but did not render
it; normal `RelicOption<T>` displayed text/metadata but no image. Separate settled HP and
Max HP pages showed native red glow only at the inclusive exact-lethal boundary. All three
structured proofs reached `selftest done` with no fresh error. The source was retired after
durable evidence was recorded.

The disposable `CanaryNativePresentation` suite then closed items 4-6 in one final
35-second headed `MapNode` run. It rendered a real Card acquisition preview and native
relic inventory acquisition with exact deck/relic deltas `1/1`; observed the `weak_short`
shake move and return at preference index 2; and rendered the exact built-in
`trial_noble` scene at its vanilla portrait-local position with inherited process mode.
Three settled screenshots showed the initial VFX, Card preview plus top-bar relic, and the
clean result page. Preview/VFX cleanup, `selftest done`, strict Tier 2, and no fresh error
all passed.

The later Character presentation expansion has four independent tracks: animation
(Spine bodies, combat/rest/merchant states, transitions, Event motion, optional UI motion),
materials (card trails, transition materials, shaders and cleanup), multiplayer
presentation (remote hands/identity/ownership/rebuild), and audio (voice/combat/energy/UI/
scene cues, registration, mix, fallback and cleanup). Positioned speech/thought bubbles
are future outlook only and are not planned for M6 or M7. None of these tracks blocks M6
or M7, and proof in one track never promotes another.

Do not reopen the completed M6 behavior canaries while starting M7. Character art support
advances beyond the eight promoted static profiles only after the real headed game renders
the intended consumer with visual evidence. A model path, successful build, or fallback
visual is not enough. Preserve the Ancient blocker and inherited fallbacks. Do not open the
animation/material/multiplayer/audio expansion during M7.

The `runtime-imagegen` edge may be reused for card/relic/power/potion, enchantment/orb
icons, a static monster body, normal event portrait slots, and the eight promoted Character
static profiles because their import and headed render contracts are live-grounded. A universal first-party Codex native-tool claim still requires a dedicated
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
