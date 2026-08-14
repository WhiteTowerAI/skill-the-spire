from __future__ import annotations

import sys
import unittest
from pathlib import Path


TOOLS_DIR = Path(__file__).resolve().parents[1]
SKILLS_DIR = TOOLS_DIR.parent / "skills"
sys.path.insert(0, str(TOOLS_DIR))
import capability_preflight as preflight  # noqa: E402


EMBER_STEP_SPEC = """# SPEC - Ember Step

## Card

- Create a shared Common Attack named Ember Step with logical id `ember_step`.
- Cost 1 Energy. On play, target one enemy, deal 9 Damage, then move normally to Discard.
- Upgrade changes Damage from 9 to 13.
- English: `Deal {Damage} damage.`
- Simplified Chinese: `造成 {Damage} 点伤害。`

## Implementation

- Support: `recipes/card.md`

## Autotest

- `CombatPlayer`: add the real Card, play it against a live enemy, wait for queued commands,
  assert exact HP loss after native modifiers and assert the Card is in Discard.
"""


COMPOSED_CARD_SPEC = """# SPEC - Echoing Edge

## Card

- Create a Card whose attached Echo capability has a saved bounded charge count.
- On the owning Card's next successful play, run before its normal OnPlay, make that play free,
  add 1 Damage to each hit from that Card, then remove the capability even if its effect throws.
- Other Cards, rejected plays, later plays, and the next combat remain unchanged.
- Carry the capability to a transformed replacement only when the replacement is an Attack.

## Implementation

- Support: `recipes/card.md`
- Support: `reference/model-capabilities.md`
- Support: `reference/lifecycle-state-rng.md`
- Support: `reference/shared-effect-hooks.md`
- Support: `reference/card-play-lifecycle.md`

## Autotest

- `CombatPlayer`: attach the real capability, drive a rejected play and an unrelated Card first,
  then play the owner; assert callback order, no resource spend, exact per-hit damage, result pile,
  removal despite completion, neutral second play, transform copy/drop identity, and combat reset.
"""


MULTI_SURFACE_SPEC = """# SPEC - Multi-Surface Composition

## Affliction

- Create a stackable combat Affliction on Skills; apply amount 2, run its attached play effect,
  and clear it before combat ends.

## Modifier

- Create a good custom-run Modifier after the built-in segment and make it mutually exclusive
  with a bad Modifier. Keep new-run initialization separate from load restoration.

## Global Effect

- Create one Combat Global Effect that can deny a guarded draw and remains neutral otherwise.

## Rest Site

- Create a standalone once-per-run free option that keeps the other native options.

## Implementation

- Support: `recipes/affliction.md`
- Support: `recipes/modifier.md`
- Support: `recipes/global-effect.md`
- Support: `recipes/rest-site.md`
- Support: `reference/rest-site-options.md`
- Hook: should_draw | surface: global-effect-combat | shape: value | route: reference/model-hook-participation.md

## Autotest

- Drive real combat Card attachment/play/clear, real modifier selection and reload, real combat
  hook delivery/reset, and the complete native Rest Site state matrix.
"""


WORLD_CONTENT_SPEC = """# SPEC - World Content

## Act

- Create a complete first-slot singleplayer Act entered from a weighted pool. Give the existing
  chapter weight 1 and the new Act weight 2. Include nonempty weak, regular, elite, and Boss
  Encounter groups, ordinary Events, and the scoped Ancient below.

## Ancient

- Create one Act-scoped Ancient with a deterministic initial option set, first-visit and ANY
  dialogue, and one option that finishes through native choice history.

## Implementation

- Support: `recipes/act.md`
- Support: `recipes/ancient.md`

## Autotest

- Enter the Act through its real singleplayer resolver, reach every required room family, then
  drive the real Ancient room and assert options, dialogue, outcome, and choice history.
"""


REWARD_CARD_PILE_SPEC = """# SPEC - Reward and Card Pile

## Reward

- Register a custom pending reward with a typed amount payload. Refuse the claim without mutation
  when the amount is zero; otherwise grant the exact outcome. Offer two children as choose-one and
  also insert one reward into the current combat's end rewards.

## Card Pile

- Register a run-persistent top-bar pile with deck-like inspection. Move the exact Card instance
  with native awaited movement and preserve contents across save/load.

## Implementation

- Support: `recipes/reward.md`
- Support: `recipes/card-pile.md`
- Support: `reference/card-piles.md`

## Autotest

- Drive the real rewards screen claim/refusal/reload and the real run pile movement/UI/reload,
  asserting exact post-state and instance identity.
"""


RUNTIME_UI_SPEC = """# SPEC - Runtime Codex

## Runtime UI

- Register one top-bar button and Ctrl+Shift+M runtime hotkey that toggle a local-only Capstone
  screen. The per-frame button state is pure and safe before a Player exists.
- Show a tracked loading Toast, then update and close it.
- Present stable entries through a grid Catalog with a drawer, one fixed pre-tree filter, and
  deterministic local search expansions.
- Attach the owning coordinator to the public top bar, dispose every registration with that
  owner, and use only Mod-scoped shell tokens in this UI.

## Implementation

- Support: `recipes/runtime-ui.md`
- Support: `reference/lifecycle-state-rng.md`

## Autotest

- Drive the real top bar, input router, Capstone, Toast, Catalog, and attachment; assert exact
  open/close, selection, search, action, suppression, disposal, and cleanup state, then perform
  separate headed mouse/controller/layout review.
"""


INTEGRATED_OWNER_SPEC = """# SPEC - Archive Delivery

## Event and Reward

- A real Event offers one pending custom Reward. Refusal changes nothing. A successful claim
  creates one exact Card and continues only after its awaited outcome completes.

## Card Pile

- Move that same Card instance into a run-persistent archive pile through the native awaited pile
  command. Preserve identity and contents across the selected run save/load boundary.

## Runtime UI

- A local top-bar entry shows the archive count and opens a searchable Catalog of the pile's live
  Cards. Providers are null-player safe; the coordinator owns and disposes every handle.

## Implementation

- Support: `recipes/event.md`
- Support: `recipes/reward.md`
- Support: `recipes/card-pile.md`
- Support: `reference/card-piles.md`
- Support: `recipes/runtime-ui.md`
- Support: `reference/lifecycle-state-rng.md`

## Autotest

- Drive the real Event and reward screen, assert refusal is neutral, claim once, await the exact
  Card result, move that instance into the real run pile, round-trip it through run save/load, then
  drive the real top-bar/Catalog host and assert count, identity, search, close, and cleanup.
"""


ACTIVE_OWNER_EFFECT_SPEC = """# SPEC - Charged Strike

## Card

- Create a targeted Attack. On play, deal 8 Damage, apply 2 Weak, draw 1 Card, then gain 1 Energy
  in that exact order. If the selected target is absent, authoring stops before emitting effects.

## Implementation

- Support: `recipes/card.md`
- Support: `reference/effect-primitives.md`

## Autotest

- `CombatPlayer`: play the real Card, assert ordered target damage/Weak/draw/Energy post-state and
  its normal result pile after queued commands complete.
"""


ATTACHED_OWNER_EFFECT_SPEC = """# SPEC - Guarded Script

## Enchantment

- Attach an Enchantment to one playable Card. After that host Card's own OnPlay body, gain 5 Block
  using the same play context. An unenchanted Card and a rejected attachment remain unchanged.

## Implementation

- Support: `recipes/enchantment.md`
- Support: `reference/effect-primitives.md`

## Autotest

- `CombatPlayer`: attach to the exact Card, play it, assert host-body then attached-Block order,
  and assert the unenchanted and rejected-host neutral cases.
"""


BLOCKING_WORLD_EFFECT_SPEC = """# SPEC - Curator's Gift

## Event

- One enabled option gains 25 Gold, creates one known Card in the owner's run, adds that exact
  Card to Deck, then obtains one known Relic. Finish the Event only after all awaited results
  complete. A failed preflight leaves the Event and run unchanged.

## Implementation

- Support: `recipes/event.md`
- Support: `reference/event-outcomes.md`
- Support: `reference/effect-primitives.md`

## Autotest

- `MapNode`: click the real option, assert ordered Gold/Card/Relic state and exact Card identity,
  then assert the result page appears only after acquisition completion.
"""


class RequirementToAuthoringTests(unittest.TestCase):
    def test_effect_reference_covers_supported_families_and_rejections(self) -> None:
        reference = (
            SKILLS_DIR / "sts2api" / "reference" / "effect-primitives.md"
        ).read_text(encoding="utf-8")
        family_symbols = (
            "DamageCmd.Attack",
            "CreatureCmd.GainBlock",
            "PowerCmd.Apply<TPower>",
            "PlayerCmd.GainEnergy",
            "CardPileCmd.Draw",
            "CardCmd.DiscardAndDraw",
            "CardPileCmd.AddGeneratedCardToCombat",
            "PotionCmd.TryToProcure<TPotion>",
            "OrbCmd.Channel<TOrb>",
        )
        for symbol in family_symbols:
            with self.subTest(symbol=symbol):
                self.assertIn(symbol, reference)

        specialized_routes = (
            "recipes/card-pile.md",
            "reference/rest-site-options.md",
            "reference/character-resource.md",
        )
        for route in specialized_routes:
            with self.subTest(route=route):
                self.assertIn(route, reference)

        self.assertNotIn("EffectEngine", reference.replace("runtime EffectEngine", ""))
        self.assertIn("report it literally", reference)

    def test_simple_card_request_reaches_an_implementable_authoring_route(self) -> None:
        self.assertEqual((1, 0, False), preflight.validate_spec_text(EMBER_STEP_SPEC))

        recipe = (SKILLS_DIR / "sts2api" / "recipes" / "card.md").read_text(
            encoding="utf-8"
        )
        author = (SKILLS_DIR / "modmaker" / "author.md").read_text(encoding="utf-8")
        verify = (SKILLS_DIR / "modmaker" / "verify.md").read_text(encoding="utf-8")

        for implementation_ingredient in (
            "ModCardTemplate",
            ".Card<",
            "DamageVar",
            "DamageCmd.Attack",
            "UpgradeValueBy",
            "cards.json",
        ):
            self.assertIn(implementation_ingredient, recipe)

        self.assertIn("<ModName>Code/SelfTest.cs", author)
        self.assertIn("independently asserted state proof", verify)
        self.assertIn("concrete structured state assertion", verify)

    def test_composed_card_reaches_owner_bound_shared_routes(self) -> None:
        self.assertEqual((5, 0, False), preflight.validate_spec_text(COMPOSED_CARD_SPEC))

        api_root = SKILLS_DIR / "sts2api"
        api_skill = (api_root / "SKILL.md").read_text(encoding="utf-8")
        card_surface = (SKILLS_DIR / "modmaker" / "surfaces" / "card.md").read_text(
            encoding="utf-8"
        )
        card_recipe = (api_root / "recipes" / "card.md").read_text(encoding="utf-8")
        references = {
            name: (api_root / "reference" / name).read_text(encoding="utf-8")
            for name in (
                "model-capabilities.md",
                "lifecycle-state-rng.md",
                "shared-effect-hooks.md",
                "card-play-lifecycle.md",
            )
        }

        for name in references:
            route = f"reference/{name}"
            self.assertIn(route, api_skill)
            self.assertIn(route, card_surface)
            self.assertIn(route, card_recipe)

        capability = references["model-capabilities.md"]
        for contract in (
            "OwnerHookOrder < 0",
            "OneShotCardPlayCapability",
            "finally",
            "ICardTransformCarryOverCapability",
            "neutral event outside the guard",
        ):
            self.assertIn(contract, capability)

        lifecycle = references["lifecycle-state-rng.md"]
        for contract in (
            "retain/dispose",
            "SyncLobbyOnChange = false",
            "never consume RNG for preview, disabled",
            "choices, or rejected actions",
            "no callback after disposal",
        ):
            self.assertIn(contract, lifecycle)

        effects = references["shared-effect-hooks.md"]
        for contract in (
            "IAttackHitHookListener",
            "Card source",
            "Return `currentMaxHandSize` outside",
            "process-wide",
            "neutral",
        ):
            self.assertIn(contract, effects)

        card_lifecycle = references["card-play-lifecycle.md"]
        for contract in (
            "OriginalOnPlayRan",
            "MarkCardFreeNextPlay",
            "ICardTransformCarryOverCapability",
            "end-turn/combat cleanup",
            "neutral Card unchanged",
        ):
            self.assertIn(contract, card_lifecycle)

    def test_shared_routes_keep_truthful_surface_owners(self) -> None:
        surface_root = SKILLS_DIR / "modmaker" / "surfaces"
        recipe_root = SKILLS_DIR / "sts2api" / "recipes"

        model_and_effect_owners = (
            "card",
            "enchantment",
            "monster",
            "orb",
            "potion",
            "power",
            "relic",
        )
        for owner in model_and_effect_owners:
            surface = (surface_root / f"{owner}.md").read_text(encoding="utf-8")
            recipe = (recipe_root / f"{owner}.md").read_text(encoding="utf-8")
            for route in ("model-capabilities.md", "shared-effect-hooks.md"):
                self.assertIn(route, surface, owner)
                self.assertIn(route, recipe, owner)
            self.assertIn("process-wide", surface, owner)

        for owner in ("event", "character"):
            surface = (surface_root / f"{owner}.md").read_text(encoding="utf-8")
            recipe = (recipe_root / f"{owner}.md").read_text(encoding="utf-8")
            self.assertIn("lifecycle-state-rng.md", surface, owner)
            self.assertIn("lifecycle-state-rng.md", recipe, owner)

        keyword_surface = (surface_root / "keyword.md").read_text(encoding="utf-8")
        keyword_recipe = (recipe_root / "keyword.md").read_text(encoding="utf-8")
        for route in ("model-capabilities.md", "shared-effect-hooks.md"):
            self.assertIn(route, keyword_surface)
            self.assertIn(route, keyword_recipe)
        self.assertIn("must not select", keyword_surface)
        self.assertIn("never selects", keyword_recipe)

    def test_multi_surface_spec_reaches_independent_authoring_routes(self) -> None:
        self.assertEqual((5, 1, False), preflight.validate_spec_text(MULTI_SURFACE_SPEC))

        surface_root = SKILLS_DIR / "modmaker" / "surfaces"
        recipe_root = SKILLS_DIR / "sts2api" / "recipes"
        expected = {
            "affliction": ("ModAfflictionTemplate", "CardCmd.Afflict"),
            "modifier": ("ModModifierTemplate", "MutuallyExclusiveModifierGroup"),
            "global-effect": ("HookedSingletonModel", "global-effect-combat"),
            "rest-site": ("ModRestSiteOptionTemplate", "AttachedState<Player, bool>"),
        }
        for slug, ingredients in expected.items():
            with self.subTest(surface=slug):
                surface = (surface_root / f"{slug}.md").read_text(encoding="utf-8")
                recipe = (recipe_root / f"{slug}.md").read_text(encoding="utf-8")
                self.assertIn("Proof matrix", surface)
                for ingredient in ingredients:
                    self.assertIn(ingredient, recipe)

        rest_site = (
            SKILLS_DIR / "sts2api" / "reference" / "rest-site-options.md"
        ).read_text(encoding="utf-8")
        for owner in ("standalone", "Card", "Relic", "Modifier"):
            self.assertIn(owner, rest_site)
        self.assertIn("before the first mutation", rest_site)

    def test_world_content_spec_reaches_act_and_ancient_authoring_routes(self) -> None:
        self.assertEqual((2, 0, False), preflight.validate_spec_text(WORLD_CONTENT_SPEC))

        surface_root = SKILLS_DIR / "modmaker" / "surfaces"
        recipe_root = SKILLS_DIR / "sts2api" / "recipes"
        act_surface = (surface_root / "act.md").read_text(encoding="utf-8")
        ancient_surface = (surface_root / "ancient.md").read_text(encoding="utf-8")
        act_recipe = (recipe_root / "act.md").read_text(encoding="utf-8")
        ancient_recipe = (recipe_root / "ancient.md").read_text(encoding="utf-8")

        for contract in (
            ".Act<T>()",
            "Registration and reachability are separate",
            "!ctx.IsMultiplayer",
            "ActEnterWeightedPoolBaseline",
            "weak, regular, elite, and Boss",
            "ChestSpineResourcePath",
        ):
            self.assertIn(contract, act_surface + act_recipe)

        for contract in (
            ".SharedAncient<",
            ".ActAncient<",
            "Func<Task>",
            "Task.CompletedTask",
            "firstVisitEver",
            "ANY",
            "supplied `Rng`",
        ):
            self.assertIn(contract, ancient_surface + ancient_recipe)

        self.assertIn("real transition", act_surface)
        self.assertIn("game-unobserved", act_surface)
        self.assertIn("real Ancient room", ancient_surface)
        self.assertIn("game-unobserved", ancient_surface)

    def test_reward_and_card_pile_spec_reaches_authoring_routes(self) -> None:
        self.assertEqual((3, 0, False), preflight.validate_spec_text(REWARD_CARD_PILE_SPEC))

        surface_root = SKILLS_DIR / "modmaker" / "surfaces"
        recipe_root = SKILLS_DIR / "sts2api" / "recipes"
        reward = (surface_root / "reward.md").read_text(encoding="utf-8") + (
            recipe_root / "reward.md"
        ).read_text(encoding="utf-8")
        pile = (surface_root / "card-pile.md").read_text(encoding="utf-8") + (
            recipe_root / "card-pile.md"
        ).read_text(encoding="utf-8")
        pile_reference = (
            SKILLS_DIR / "sts2api" / "reference" / "card-piles.md"
        ).read_text(encoding="utf-8")

        for contract in (
            "ModRewardRegistry",
            "ModCustomReward",
            "JsonSerializerContext",
            "RewardsCmd.OfferCustom",
            "AddExtraReward",
            "LinkedRewardSets.Create",
            "1..128",
            "Returning `false` means unavailable/cancelled",
        ):
            self.assertIn(contract, reward)

        for contract in (
            "ModCardPileSpec",
            "RunPersistent",
            "TopBarDeck",
            "ModCardPileRegistry.GetPileType",
            "awaited `CardPileCmd`",
            "ExtraHand",
            "game-unobserved",
        ):
            self.assertIn(contract, pile + pile_reference)

        for slug in ("reward", "card-pile"):
            self.assertIn("Proof matrix", (surface_root / f"{slug}.md").read_text(encoding="utf-8"))

    def test_runtime_ui_spec_reaches_authoring_route(self) -> None:
        self.assertEqual((2, 0, False), preflight.validate_spec_text(RUNTIME_UI_SPEC))

        surface = (SKILLS_DIR / "modmaker" / "surfaces" / "runtime-ui.md").read_text(
            encoding="utf-8"
        )
        recipe = (SKILLS_DIR / "sts2api" / "recipes" / "runtime-ui.md").read_text(
            encoding="utf-8"
        )

        for contract in (
            "ModTopBarButtonSpec",
            "RitsuToastService.ShowTracked",
            "RuntimeHotkeyOptions",
            "NetScreenType.None",
            "RitsuFloatingWindow",
            "RitsuCatalogBrowser",
            "RitsuSearchExpansionRegistry.Register",
            "ModNodeAttachmentRegistry.For",
            "RitsuShellThemeRuntime",
            "16,384",
            "512",
        ):
            self.assertIn(contract, surface + recipe)

        for boundary in (
            "Settings",
            "Progression",
            "post-run Badge",
            "Telemetry",
            "Update Check",
            "Multiplayer",
        ):
            self.assertIn(boundary, surface)
        self.assertIn("Proof matrix", surface)
        self.assertIn("game-unobserved", surface)

    def test_integrated_spec_composes_truthful_owners_without_a_combo_surface(self) -> None:
        self.assertEqual((6, 0, False), preflight.validate_spec_text(INTEGRATED_OWNER_SPEC))

        modmaker = SKILLS_DIR / "modmaker"
        api = SKILLS_DIR / "sts2api"
        semantic_contract = (modmaker / "semantic-contract.md").read_text(encoding="utf-8")
        author = (modmaker / "author.md").read_text(encoding="utf-8")
        verify = (modmaker / "verify.md").read_text(encoding="utf-8")

        for owner in ("Event", "Reward", "Card Pile", "Runtime UI"):
            self.assertIn(owner, semantic_contract)
        self.assertIn("do not invent a combo", semantic_contract)
        self.assertIn("dependency order", author)
        self.assertIn("independently asserted state proof", verify)

        routes = {
            "event": api / "recipes" / "event.md",
            "reward": api / "recipes" / "reward.md",
            "card-pile": api / "recipes" / "card-pile.md",
            "runtime-ui": api / "recipes" / "runtime-ui.md",
            "card-piles": api / "reference" / "card-piles.md",
            "lifecycle": api / "reference" / "lifecycle-state-rng.md",
        }
        for name, route in routes.items():
            with self.subTest(route=name):
                self.assertTrue(route.is_file())

        combined = "\n".join(route.read_text(encoding="utf-8") for route in routes.values())
        for contract in (
            "RewardsCmd.OfferCustom",
            "Returning `false` means unavailable/cancelled",
            "awaited `CardPileCmd`",
            "RunPersistent",
            "ModTopBarButtonSpec",
            "RitsuCatalogBrowser",
            "retain/dispose",
            "game-unobserved",
        ):
            self.assertIn(contract, combined)

        deferred = (
            "Progression",
            "post-run Badge",
            "Settings",
            "Telemetry",
            "Multiplayer",
            "Update Check",
        )
        runtime_surface = (modmaker / "surfaces" / "runtime-ui.md").read_text(encoding="utf-8")
        for boundary in deferred:
            self.assertIn(boundary, runtime_surface)

    def test_active_owner_composes_ordered_effect_primitives(self) -> None:
        self.assertEqual((2, 0, False), preflight.validate_spec_text(ACTIVE_OWNER_EFFECT_SPEC))

        api = SKILLS_DIR / "sts2api"
        reference = (api / "reference" / "effect-primitives.md").read_text(encoding="utf-8")
        surface = (SKILLS_DIR / "modmaker" / "surfaces" / "card.md").read_text(
            encoding="utf-8"
        )
        author = (SKILLS_DIR / "modmaker" / "author.md").read_text(encoding="utf-8")

        for binding in (
            "OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)",
            "base.Owner.Creature",
            "cardPlay.Target",
        ):
            self.assertIn(binding, surface)
        for lowering in (
            ".FromCard(cardSource)",
            "ICombatState combatState = cardSource.CombatState",
            ".TargetingAllOpponents(combatState)",
            ".TargetingRandomOpponents(combatState)",
            ".WithHitCount(hitCount)",
            "Call `Unpowered()` only",
            "PowerCmd.Apply<TPower>",
            "fromHandDraw: false",
            "PlayerCmd.GainEnergy",
        ):
            self.assertIn(lowering, reference)
        self.assertLess(reference.index("## Damage"), reference.index("## Draw Cards"))
        self.assertIn("emit each awaited call in SPEC order", author)
        self.assertIn("must be non-null", reference)

    def test_attached_owner_composes_without_losing_host_provenance(self) -> None:
        self.assertEqual((2, 0, False), preflight.validate_spec_text(ATTACHED_OWNER_EFFECT_SPEC))

        api = SKILLS_DIR / "sts2api"
        reference = (api / "reference" / "effect-primitives.md").read_text(encoding="utf-8")
        surface = (SKILLS_DIR / "modmaker" / "surfaces" / "enchantment.md").read_text(
            encoding="utf-8"
        )
        recipe = (api / "recipes" / "enchantment.md").read_text(encoding="utf-8")

        for binding in (
            "OnPlay(PlayerChoiceContext choiceContext, CardPlay? cardPlay)",
            "exact host Card `Card`",
            "Card.Owner.Creature",
            "Preserve the host Card as `cardSource`",
        ):
            self.assertIn(binding, surface)
        self.assertIn("drive the host Card", recipe)
        self.assertIn("cardPlay", reference)
        self.assertIn("Synchronous", surface)
        self.assertIn("cannot await commands", surface)

        affliction_surface = (SKILLS_DIR / "modmaker" / "surfaces" / "affliction.md").read_text(
            encoding="utf-8"
        )
        for binding in (
            "OnPlay(PlayerChoiceContext choiceContext, Creature? target)",
            "Card.Owner.Creature",
            "host Card as `cardSource`",
            "does not receive the enclosing `CardPlay`",
            "`cardPlay: null`",
        ):
            self.assertIn(binding, affliction_surface)

    def test_blocking_world_transaction_waits_for_ordinary_results(self) -> None:
        self.assertEqual((3, 0, False), preflight.validate_spec_text(BLOCKING_WORLD_EFFECT_SPEC))

        api = SKILLS_DIR / "sts2api"
        reference = (api / "reference" / "effect-primitives.md").read_text(encoding="utf-8")
        surface = (SKILLS_DIR / "modmaker" / "surfaces" / "event.md").read_text(
            encoding="utf-8"
        )

        for contract in (
            "mutable run owner `Owner`",
            "Preflight every cost/availability condition before the first mutation",
            "inspect rejected acquisition results",
            "only then call",
        ):
            self.assertIn(contract, surface)
        for lowering in (
            "player.RunState.CreateCard<TCard>",
            "PileType.Deck",
            "RelicCmd.Obtain<TRelic>",
            "potionResult",
        ):
            self.assertIn(lowering, reference)
        self.assertIn("The owning callback must await the acquisition", reference)
        self.assertIn("does not invent a combat target", surface)


if __name__ == "__main__":
    unittest.main()
