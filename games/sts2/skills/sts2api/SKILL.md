---
name: sts2api
description: |
  Query the STS2 game pack for concrete modding knowledge: element recipes,
  command APIs, localization rules, error fixes. Use when the main pipeline
  needs a specific answer (hook signature, Cmd name, loc-key rule) rather than
  loading the whole pack into context.
---

# STS2 API Lookup

A narrow reference tool: answer only what the caller asked and read one file at a time.
**Never read all files at once.**

## Pinned profile

Generated Mods target RitsuLib `0.6.7` on STS2 stable `0.107.1` (compat `0.107.1`, profile
`ritsulib-0.6.7-sts2-0.107.1`). `scaffold.py`, `ritsu_profile.py`, and `build.py` own the profile,
the runtime module layout, and the identity the load marker reports; recipes never regenerate
them. Public types keep their `STS2RitsuLib.*` namespaces across RitsuLib's split modules.
RitsuLib is the only adapter: never add BaseLib or another framework dependency, copy another
scaffold, or infer a runtime dependency from a recipe name.

## How to answer

1. New content: the SPEC (`${MODMAKER_SKILL_DIR}/spec.md`) is the source of truth. Find the
   element's recipe in § New content, then read only the references it and § Behavior
   references name for the selected behavior.
2. An edit to existing vanilla content: § Vanilla overrides, before any new-content recipe.
3. An error signature: `errors.md`.
4. A vanilla analog or realistic numbers:
   `python ${GAME_TOOLS_DIR}/vanilla_overrides.py resolve <name> --category <card|relic|potion|power>`.
5. An exact public signature: `python ${GAME_TOOLS_DIR}/api.py search <Type> [<member>]` or
   `api.py find <member>`; where facts come from: `grounding.md`.
6. No maintained route: official tutorial semantics plus public members in the pinned profile
   make every documented consumer in a feature family supported, so a missing recipe means only
   that no maintained route exists. Ground a Mod-local route under `grounding.md` § Mod-local
   Routes; never guess a symbol.

Return only the relevant snippet (hook, Cmd, loc-key rule, error fix, one analog).

## Design planning

After `${MODMAKER_SKILL_DIR}/route.md` classifies the request, load only the design pages its
handoff names. Load the smallest set: an exact simple Card does not load balance planning
merely because it contains a number. They separate pinned facts, observed conventions,
creative decisions, and open hypotheses; they are design guidance, not runtime routes or
playtest results.

| File | Read when |
|---|---|
| `design/character-foundation.md` | a playable Character or Character/content set, before creative questions or a starter-deck proposal |
| `design/mechanic-planning.md` | a mechanic, resource, stateful loop, risk/reward structure, or interacting system lacks an exact core decision |
| `design/content-set-planning.md` | a Character card pool, archetype, multi-element set, or other content ecosystem |
| `design/balance-planning.md` | balance, a resource economy, a formula, or materially unresolved values are a design question |

## New content

Register every model exactly once in the scaffold's `MainFile.RegisterContent()` through one
`RitsuLibFramework.CreateContentPack(ModId) ... .Apply()` chain. Never add a pool attribute,
constructor registration, reflection discovery, or a second registration path. A simple surface
initializes no Character, Event, multiplayer, audio, material, or other unselected module.
Custom art reaches the game only through the template's asset profile; an empty profile keeps
the checked fallback.

| Surface | Recipe | Registration and template |
|---|---|---|
| Card | `recipes/card.md` | `.Card<TPool,T>()`; `ModCardTemplate` |
| Relic | `recipes/relic.md` | `.Relic<TPool,T>()`; `ModRelicTemplate` |
| Potion | `recipes/potion.md` | `.Potion<TPool,T>()`; `ModPotionTemplate` |
| Power (buff/debuff) | `recipes/power.md` | `.Power<T>()`; `ModPowerTemplate` |
| Keyword | `recipes/keyword.md` | `.CardKeywordOwnedByLocNamespace(...)`; text-only tooltip |
| Enchantment | `recipes/enchantment.md` | `.Enchantment<T>()`; `ModEnchantmentTemplate` |
| Orb | `recipes/orb.md` | `.Orb<T>()`; `ModOrbTemplate` |
| Monster and Encounter | `recipes/monster.md` | `.Monster<T>()` plus `.ActEncounter<TAct,T>()` or a global registration; `ModMonsterTemplate`, `ModEncounterTemplate` |
| Event | `recipes/event.md` | `.SharedEvent<T>()` or `.ActEvent<TAct,T>()`; `ModEventTemplate` |
| New Ancient | `recipes/ancient.md` | `.SharedAncient<T>()` or `.ActAncient<TAct,T>()`; `ModAncientEventTemplate` |
| Act | `recipes/act.md` | `.Act<T>()` plus one force/uniform/weighted entry policy; `ModActTemplate` |
| Character | `recipes/character.md` | `.Character<T>(starters)` plus type-list pools; `ModCharacterTemplate<...>` |
| Affliction | `recipes/affliction.md` | `.Affliction<T>()`; `ModAfflictionTemplate`; `CardCmd.Afflict` |
| Modifier | `recipes/modifier.md` | `.GoodModifier<T>()` or `.BadModifier<T>()`; `ModModifierTemplate` |
| Global Effect | `recipes/global-effect.md` | `.Singleton<T>()`; `HookedSingletonModel` with `HookType.Run` or `HookType.Combat` |
| Rest Site option | `recipes/rest-site.md` | owner `TryModifyRestSiteOptions`; `ModRestSiteOptionTemplate` |
| Reward | `recipes/reward.md` | `ModRewardRegistry.For(modId).RegisterOwned(...)`; `ModCustomReward` |
| Custom Card Pile | `recipes/card-pile.md` | `.CardPileOwned(...)`; `ModCardPileSpec` |
| Runtime UI workflow | `recipes/runtime-ui.md` | the selected top-bar, Toast, hotkey, screen, Catalog, window, search, attachment, and shell-token services |

Other public entry points: `RitsuLibFramework.SubscribeLifecycle<TEvent>`,
`GetRunSavedDataStore`, `GetSecondaryResourceRegistry`, `GetNodeAttachmentRegistry`,
`RegisterSingleTargetType`, `RegisterSingleTargetTypeWithContext`, `RegisterMultiTargetType`,
and, for fixed vanilla-override Adapters only, `CreatePatcher`.

## Behavior references

Read one only when the SPEC selects that behavior.

| File | Read when |
|---|---|
| `reference/vanilla-text-style.md` | writing **any** player-facing text: glossary terms and colors, numbers, line breaks, Chinese style, hover tips |
| `reference/mechanics.md` | before a Card or Power: DynamicVars, SmartFormat descriptions, shared enums |
| `reference/effect-primitives.md` | an ordered `effects.sequence`: exact commands, context, await order; in-combat Card choice, top-of-Draw-Pile placement, free-this-turn, Stun |
| `reference/stateful-mechanics.md` | an effect that remembers progress, limits uses, or compares turns |
| `reference/lifecycle-state-rng.md` | behavior that crosses callback, combat, room, run, save, or profile boundaries, persists state, or makes gameplay-random choices |
| `reference/model-hook-participation.md` | a raw hook rule in SPEC |
| `reference/shared-effect-hooks.md` | per-hit attack, healing, Energy/Stars gain, or maximum-hand-size effects |
| `reference/model-capabilities.md` | separable behavior or state bundled onto a model; Card transform carry-over |
| `reference/card-play-lifecycle.md` | behavior around Card play: before/after `OnPlay`, suppression, free play, transform listeners |
| `reference/card-computed-values.md` | calculated Card values or DynamicVar tooltips |
| `reference/advanced-targeting.md` | a filtered custom Card/Potion target |
| `reference/card-hand-emphasis.md` | conditional Card hand glow or outline |
| `reference/ancient-card.md` | a Card with rarity `Ancient`: acquisition route, pool, full-card art, native rules |
| `reference/extra-corner-labels.md` | extra value badges on a Relic or Power |
| `reference/model-right-click.md` | a right-click or controller-cancel action on a Mod model |
| `reference/card-piles.md` | the complete Custom Card Piles API |
| `reference/rest-site-options.md` | any Rest Site option: owner, state, cost, repeatability, stay/leave, icon |
| `reference/character-resource.md` | secondary resources and their payment |
| `reference/ordered-card-buffer.md` | an ordered card-play record with dynamic output |
| `reference/character-presentation.md` | Character static/native presentation and the Character art slot table |
| `reference/character-combat-cues.md` | Character Idle/Attack/Hit/Dead combat cues |
| `reference/ancient-dialogue.md` | custom-Character dialogue in native Ancient scenes |
| `reference/event-outcomes.md` | an Event beyond the one-Cmd fast path: pages, card selections, rewards, special combat |
| `reference/event-option-presentation.md` | Event option Hover Tips, relic-backed options, lethal-choice warnings |
| `reference/event-native-presentation.md` | native Card/relic acquisition previews, screen shake, `trial_noble` VFX in an Event |
| `reference/event-vfx.md` | the `portrait_halo` Event portrait VFX |
| `reference/event-text-effects.md` | requested atmospheric Event text effects |
| `reference/content-text-effects.md` | requested colored words on Card, relic, potion, or power text beyond the default style |
| `reference/forced-followup-event.md` | a delayed or conditional Quest Card follow-up Event |
| `reference/lobby-options.md` | a choice made in the start-run lobby (a host run rule or a per-player pick) |

## Verification, art, and repair

| File | Read when |
|---|---|
| `reference/selftest-harness.md` | writing `SelfTestScenarios.cs`; any Tier 2 question. A non-combat host's driver lives in its recipe |
| `reference/art-setup.md` | the user picked art choice 1, 2, or 3 at interview: route record, style note, call count, Character art tier |
| `reference/art-contract.md` | the art step: paths, sizes, fallbacks, prompts, consent, and import |
| `reference/art-character.md` | Character art: tiers, sheets, identity routing, and prompts |
| `reference/art-backends.md` | the user selected a `backend:<name>` art route |
| `reference/art-samples/` | passed as `--reference` in the art step; type-matched style samples, never mixed across families (© Mega Crit, reference-only; see `ATTRIBUTION.md`) |
| `grounding.md` | an answer the recipe lacks; the Mod-local route procedure |
| `errors.md` | a Build or load failure; the repair loop |

## Vanilla overrides

When the request edits an existing vanilla model, read `reference/vanilla-overrides.md` before
any new-content recipe. It resolves the pinned target, then routes to one category reference
below. Never derive a patch body from the prompt or silently turn the request into new content.

An override changes only what the request names. A changed number or behavior keeps the model's
name and its other surfaces vanilla, and rewrites the rules text only as far as the change
requires: `card.vars.base` for a number the text already shows, and
`card.description.localization` (or the Relic/Potion equivalent) for new behavior. Never add a
title change unless the request asks for a new name.

| File | Read when |
|---|---|
| `reference/vanilla-card-overrides.md` | an exact existing `CARD.*` target: properties, costs, play state, text and tips, glow, owner hooks, `OnPlay` |
| `reference/vanilla-visual-overrides.md` | a visual change to an exact existing model |
| `reference/vanilla-ancient-overrides.md` | options or pages of an existing Ancient |
| `reference/vanilla-availability-overrides.md` | epoch gates or Card/Relic/Potion pool membership |
| `reference/vanilla-non-card-overrides.md` | data or behavior of an existing Relic, Potion, Power, Orb, Enchantment, Affliction, Monster, Encounter, or Event |
