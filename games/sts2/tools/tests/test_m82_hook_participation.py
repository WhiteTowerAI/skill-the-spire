"""M8.2 step 3: hook-participation declarations on the surfaces that can receive them.

Step 1 produced the catalog; this step spends it. Three things have to hold together, and each
of them is a way the M7.6 Wrath failure comes back if it drifts:

1. the route page's declared capability ids are exactly the catalog's authorable set, so a hook
   cannot be documented as authorable without being reachable (the `art-contract` pattern: code
   owns the values, the page is a projection, a test holds them together);
2. every surface that can receive hooks declares the envelope field and owes the paired proof,
   with the neutral-case assertion that a single-value test cannot substitute for; and
3. preflight rejects a declaration whose surface is not in the dispatching iterator's listener
   set, whose shape the catalog contradicts, or whose hook another route already owns.

Point 3 is the load-bearing one. A hook overridden on a surface that never receives it compiles,
ships, and silently does nothing -- so offering the full list uniformly would have *added*
instances of the bug this Package exists to prevent.
"""
from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parents[1]
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import design_trace
import skill_prose
import spec_envelope_trace


CATALOG_PATH = (
    TOOLS_DIR.parent
    / "skills"
    / "sts2-api"
    / "reference"
    / "catalogs"
    / "model-hooks-sts2-0.107.1.json"
)
ROUTE_PAGE = (
    TOOLS_DIR.parent / "skills" / "sts2-api" / "reference" / "model-hook-participation.md"
)
RECIPES_DIR = TOOLS_DIR.parent / "skills" / "sts2-api" / "recipes"

# The seven surfaces the catalog marks authorable. Character, event, and keyword are absent
# because no listener set contains them; they must not grow a participation field.
AUTHORABLE_SURFACES = ("card", "enchantment", "monster", "orb", "potion", "power", "relic")
NON_AUTHORABLE_SURFACES = ("character", "event", "keyword")


def snake(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def catalog() -> dict:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def expected_capability_ids() -> set[str]:
    """Every id the route page should declare: authorable hooks plus Enchantment redirects."""
    ids: set[str] = set()
    for hook in catalog()["hooks"]:
        if hook.get("owned_by_route"):
            continue
        ids.add(hook["semantic_id"])
        redirect = hook.get("enchantment_redirect")
        if redirect:
            ids.add(snake(redirect))
    return ids


class RoutePageProjectsTheCatalogTests(unittest.TestCase):
    """The page declares capabilities; the catalog decides which. A test keeps them equal."""

    def setUp(self) -> None:
        self.text = ROUTE_PAGE.read_text(encoding="utf-8")

    def test_declared_ids_equal_the_catalog_authorable_set(self) -> None:
        declared = design_trace.declared_capabilities(self.text)
        expected = expected_capability_ids()
        self.assertEqual(
            declared,
            expected,
            "the route page's declared capability ids drifted from the catalog; "
            f"page-only={sorted(declared - expected)} catalog-only={sorted(expected - declared)}",
        )

    def test_route_owned_hooks_are_not_offered_raw(self) -> None:
        """Rest Site contribution keeps four boundaries the bare hook does not carry."""
        declared = design_trace.declared_capabilities(self.text)
        owned = {
            hook["semantic_id"]
            for hook in catalog()["hooks"]
            if hook.get("owned_by_route")
        }
        self.assertEqual(len(owned), 2, "expected exactly two route-owned hooks")
        for capability_id in owned:
            self.assertNotIn(
                capability_id,
                declared,
                f"{capability_id} is owned by a shipped route and must not be declared here",
            )
        self.assertIn("rest-site-options.md", self.text)

    def test_page_points_at_the_catalog_instead_of_copying_a_hook_list(self) -> None:
        """Prose states rules; the catalog holds the data. A copied list would rot.

        Checked as a count, not a phrase: outside the capability declarations the page may name a
        handful of hooks as worked examples, but not enumerate the surface. `authorable_surfaces`
        must be named, because that is the field an author is told to read.
        """
        self.assertIn("authorable_surfaces", self.text)
        prose = design_trace.CAPABILITY_DECLARATION_RE.sub("", self.text)
        named = {
            hook["hook"] for hook in catalog()["hooks"] if hook["hook"] in prose
        }
        self.assertLess(
            len(named),
            15,
            f"the page names {len(named)} hooks in prose; that is a copied list, not a rule",
        )

    def test_page_resolves_as_a_supported_route_with_a_real_anchor(self) -> None:
        slugs = design_trace.heading_slugs(self.text)
        self.assertIn("capability-ids-this-route-provides", slugs)
        self.assertIn("value-shape-a-guard-a-value-and-a-neutral-return", slugs)


class SurfaceDeclarationTests(unittest.TestCase):
    """Each authorable surface declares the field; the others must not."""

    @staticmethod
    def envelope(slug: str) -> str:
        """The surface page with emphasis stripped.

        A top-level key is written `- **field**:` and a nested one `field:`. Stripping `**`
        lets one assertion cover both forms, matching `test_surface_cross_check.py`.
        """
        return skill_prose.surface(slug).replace("**", "")

    def test_authorable_surfaces_declare_the_envelope_field(self) -> None:
        for slug in AUTHORABLE_SURFACES:
            with self.subTest(surface=slug):
                self.assertIn("hook participation:", self.envelope(slug))

    def test_non_authorable_surfaces_do_not(self) -> None:
        """A field on a surface no listener set contains would be a promise nothing keeps."""
        for slug in NON_AUTHORABLE_SURFACES:
            with self.subTest(surface=slug):
                self.assertNotIn("hook participation:", self.envelope(slug))

    def test_each_surface_states_its_own_scope_and_owner_access(self) -> None:
        """Reachability and the owner property differ per surface; both are authoring input."""
        expectations = {
            "power": ("combat-scope hooks only", "`Owner` is a `Creature`"),
            "orb": ("combat-scope hooks only", "Owner.Creature"),
            "monster": ("combat-scope hooks only", "`Creature`, not `Owner`"),
            "relic": ("66 of 68", "Owner.Osty"),
            "potion": ("66 of 68", "Owner.Osty"),
            "card": ("combat pile", "Owner.Osty"),
        }
        for slug, phrases in expectations.items():
            page = skill_prose.surface(slug)
            for phrase in phrases:
                with self.subTest(surface=slug, phrase=phrase):
                    self.assertIn(phrase, page)

    def test_enchantment_page_and_recipe_both_carry_the_five_redirects(self) -> None:
        """A general hook here is wrong on the pinned host, so both pages must say so."""
        redirects = {
            snake(hook["enchantment_redirect"])
            for hook in catalog()["hooks"]
            if hook.get("enchantment_redirect")
        }
        self.assertEqual(len(redirects), 5)
        page = skill_prose.surface("enchantment")
        recipe = (RECIPES_DIR / "enchantment.md").read_text(encoding="utf-8")
        for capability_id in redirects:
            with self.subTest(capability=capability_id):
                self.assertIn(capability_id, page)
        for hook_name in ("EnchantDamageMultiplicative", "EnchantPlayCount"):
            self.assertIn(hook_name, recipe)
        self.assertIn("MUST use this hook instead of", recipe)

    def test_recipes_carry_the_authoring_line_for_every_authorable_surface(self) -> None:
        for slug in AUTHORABLE_SURFACES:
            recipe = (RECIPES_DIR / ("monster" if slug == "monster" else slug)).with_suffix(
                ".md"
            )
            with self.subTest(recipe=recipe.name):
                text = recipe.read_text(encoding="utf-8")
                self.assertIn("hook participation", text)
                self.assertIn("model-hook-participation.md", text)

    def test_scenarios_cover_the_three_documented_cases(self) -> None:
        """The behavioral rubrics travel with the Package that changes the behavior."""
        scenarios = (
            TOOLS_DIR.parent / "tests" / "m82-capability-conformance-scenarios.md"
        ).read_text(encoding="utf-8")
        for phrase in (
            "Scenario 1",
            "Scenario 2",
            "Scenario 3",
            "modify_damage_multiplicative",
            "try_modify_card_reward_options",
            "enchant_damage_multiplicative",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, scenarios)
        # The unrun real-host obligation is stated rather than implied.
        self.assertIn("unrun", scenarios)
        self.assertIn("missing verification, not missing support", scenarios)

    def test_guard_shape_names_the_vanilla_precedent_and_the_neutral_return(self) -> None:
        """The three-part body is copied from vanilla; a paraphrase loses the neutral case."""
        power_recipe = (RECIPES_DIR / "power.md").read_text(encoding="utf-8")
        self.assertIn("VulnerablePower", power_recipe)
        self.assertIn("IsPoweredAttack()", power_recipe)
        self.assertIn("return 1m", power_recipe)
        self.assertIn("DynamicVars", power_recipe)


class PreflightRejectionTests(unittest.TestCase):
    """Preflight must reject what cannot work, with a message naming what is missing."""

    def spec(self, *, surface: str = "power", capability: str, shape: str | None) -> str:
        shape_line = f"    shape: {shape}\n" if shape else ""
        shape_fields = ""
        if shape in {"value", "out-replacement"}:
            shape_fields += "    value: 2\n"
        if shape == "out-replacement":
            shape_fields += "    replaces: yes when the condition matches; declines otherwise\n"
        if shape == "collection":
            shape_fields += (
                "    edit: add one probe entry\n"
                "    other entries: preserved unchanged\n"
                "    ordering: base - no late dependency\n"
            )
        return (
            "# SPEC - Probe\n\n"
            "- **contract**: sts2-content-semantic/v2\n"
            "- **mod id**: probe\n"
            "- **author**: tester\n"
            "- **content**:\n"
            "  - name: Probe\n"
            f"  - surface: {surface}\n"
            "- **registration**:\n  - availability: shared\n"
            "- **localization**:\n  - languages: [eng, zhs]\n  - fields: title=Probe\n"
            "- **effects**:\n  - trigger: play\n"
            "- **hook participation**: one\n"
            f"  - capability: {capability}\n"
            f"{shape_line}"
            "    player-facing: probe\n"
            "    subject: the declaring element's owner\n"
            "    condition: only the declared owner interaction\n"
            "    dynamic value name: ProbeValue\n"
            "    outside the condition: preserve the host value unchanged\n"
            f"{shape_fields}"
            "- **state**: none\n"
            "- **presentation**:\n  - assets: none\n"
            "- **fallback**:\n  - missing asset: checked template\n"
            "- **proof**:\n  - scenario: CombatPlayer\n"
        )

    def test_reachable_declaration_passes(self) -> None:
        text = self.spec(capability="modify_damage_multiplicative", shape="value")
        self.assertEqual(spec_envelope_trace.validate_hook_participation(text), 1)

    def test_card_hook_after_optional_enchantment_field_stays_on_card(self) -> None:
        """The Card template's nested field must not capture a later top-level Card hook."""
        text = self.spec(
            surface="card", capability="modify_damage_multiplicative", shape="value"
        ).replace("  - surface: card\n", "  - surface: card\n  - enchantment: none\n")
        self.assertEqual(spec_envelope_trace.validate_hook_participation(text), 1)

    def test_card_hook_cannot_masquerade_as_an_enchantment_redirect(self) -> None:
        """The same parser bug could also falsely accept an Enchantment-only capability."""
        text = self.spec(
            surface="card", capability="enchant_damage_multiplicative", shape="value"
        ).replace("  - surface: card\n", "  - surface: card\n  - enchantment: none\n")
        with self.assertRaises(spec_envelope_trace.SpecEnvelopeError) as caught:
            spec_envelope_trace.validate_hook_participation(text)
        self.assertIn("on surface 'card'", str(caught.exception))

    def test_nonempty_participation_requires_a_capability(self) -> None:
        text = self.spec(
            capability="modify_damage_multiplicative", shape="value"
        ).replace("  - capability: modify_damage_multiplicative\n", "")
        with self.assertRaises(spec_envelope_trace.SpecEnvelopeError) as caught:
            spec_envelope_trace.validate_hook_participation(text)
        self.assertIn("has no capability entry", str(caught.exception))

    def test_value_participation_requires_every_semantic_field(self) -> None:
        valid = self.spec(capability="modify_damage_multiplicative", shape="value")
        required_lines = {
            "shape": "    shape: value\n",
            "player-facing": "    player-facing: probe\n",
            "subject": "    subject: the declaring element's owner\n",
            "condition": "    condition: only the declared owner interaction\n",
            "dynamic value name": "    dynamic value name: ProbeValue\n",
            "outside the condition": (
                "    outside the condition: preserve the host value unchanged\n"
            ),
            "value": "    value: 2\n",
        }
        for field, line in required_lines.items():
            with self.subTest(field=field):
                with self.assertRaises(spec_envelope_trace.SpecEnvelopeError) as caught:
                    spec_envelope_trace.validate_hook_participation(valid.replace(line, ""))
                self.assertIn(field, str(caught.exception))

    def test_out_replacement_requires_its_taken_flag(self) -> None:
        hook = next(
            entry
            for entry in catalog()["hooks"]
            if entry["declaration_shape"] == "out-replacement"
            and not entry.get("owned_by_route")
        )
        text = self.spec(
            surface=hook["authorable_surfaces"][0],
            capability=hook["semantic_id"],
            shape="out-replacement",
        ).replace(
            "    replaces: yes when the condition matches; declines otherwise\n", ""
        )
        with self.assertRaises(spec_envelope_trace.SpecEnvelopeError) as caught:
            spec_envelope_trace.validate_hook_participation(text)
        self.assertIn("replaces", str(caught.exception))

    def test_collection_requires_edit_preservation_and_ordering(self) -> None:
        hook = next(
            entry
            for entry in catalog()["hooks"]
            if entry["declaration_shape"] == "collection-edit"
            and not entry.get("owned_by_route")
        )
        valid = self.spec(
            surface=hook["authorable_surfaces"][0],
            capability=hook["semantic_id"],
            shape="collection",
        )
        for field, line in {
            "edit": "    edit: add one probe entry\n",
            "other entries": "    other entries: preserved unchanged\n",
            "ordering": "    ordering: base - no late dependency\n",
        }.items():
            with self.subTest(field=field):
                with self.assertRaises(spec_envelope_trace.SpecEnvelopeError) as caught:
                    spec_envelope_trace.validate_hook_participation(valid.replace(line, ""))
                self.assertIn(field, str(caught.exception))

    def test_hook_unreachable_on_the_declaring_surface_is_rejected(self) -> None:
        """A run-scope hook on a Power: the exact shape of the Watcher failure."""
        run_only = next(
            hook["semantic_id"]
            for hook in catalog()["hooks"]
            if "power" not in hook["authorable_surfaces"]
            and not hook.get("owned_by_route")
            and not hook.get("enchantment_redirect")
        )
        text = self.spec(capability=run_only, shape=None)
        with self.assertRaises(spec_envelope_trace.SpecEnvelopeError) as caught:
            spec_envelope_trace.validate_hook_participation(text)
        message = str(caught.exception)
        self.assertIn("cannot receive it", message)
        self.assertIn(run_only, message)
        self.assertIn("authorable on:", message)

    def test_contradicted_shape_is_rejected(self) -> None:
        """A collection edit declared as a value cannot express add/remove or composition."""
        collection = next(
            hook["semantic_id"]
            for hook in catalog()["hooks"]
            if hook["declaration_shape"] == "collection-edit"
            and not hook.get("owned_by_route")
        )
        surface = next(
            s
            for s in AUTHORABLE_SURFACES
            if s
            in next(
                hook["authorable_surfaces"]
                for hook in catalog()["hooks"]
                if hook["semantic_id"] == collection
            )
        )
        text = self.spec(surface=surface, capability=collection, shape="value")
        with self.assertRaises(spec_envelope_trace.SpecEnvelopeError) as caught:
            spec_envelope_trace.validate_hook_participation(text)
        self.assertIn("the catalog records 'collection'", str(caught.exception))

    def test_route_owned_hook_is_rejected_with_its_owner_named(self) -> None:
        owned = next(
            hook
            for hook in catalog()["hooks"]
            if hook.get("owned_by_route")
        )
        surface = owned["authorable_surfaces"][0]
        text = self.spec(surface=surface, capability=owned["semantic_id"], shape=None)
        with self.assertRaises(spec_envelope_trace.SpecEnvelopeError) as caught:
            spec_envelope_trace.validate_hook_participation(text)
        message = str(caught.exception)
        self.assertIn("owned by", message)
        self.assertIn("rest-site-options.md", message)

    def test_unknown_capability_is_rejected(self) -> None:
        text = self.spec(capability="modify_nonexistent_thing", shape=None)
        with self.assertRaises(spec_envelope_trace.SpecEnvelopeError) as caught:
            spec_envelope_trace.validate_hook_participation(text)
        self.assertIn("unknown capability", str(caught.exception))

    def test_enchantment_redirect_is_rejected_outside_an_enchantment(self) -> None:
        """`enchant_*` exists only on `EnchantmentModel`; a Power declaring one is wrong."""
        text = self.spec(capability="enchant_damage_multiplicative", shape="value")
        with self.assertRaises(spec_envelope_trace.SpecEnvelopeError) as caught:
            spec_envelope_trace.validate_hook_participation(text)
        self.assertIn("cannot receive it", str(caught.exception))

    def test_general_hook_redirected_on_enchantment_is_rejected(self) -> None:
        """The mirror case: the five general hooks are wrong on an Enchantment."""
        text = (
            "- **contract**: sts2-content-semantic/v2\n"
            "- **content**:\n  - name: Host\n  - surface: card\n"
            "  - enchantment: Sharpened - adds damage\n"
            "    hook participation: one\n"
            "    - capability: modify_damage_multiplicative\n"
            "      shape: value\n"
        )
        with self.assertRaises(spec_envelope_trace.SpecEnvelopeError) as caught:
            spec_envelope_trace.validate_hook_participation(text)
        self.assertIn("cannot receive it", str(caught.exception))

    def test_a_spec_without_participation_is_unaffected(self) -> None:
        """Additive: a project that declares none validates exactly as before."""
        text = "- **contract**: sts2-content-semantic/v2\n- **content**:\n  - surface: power\n"
        self.assertEqual(spec_envelope_trace.validate_hook_participation(text), 0)


if __name__ == "__main__":
    unittest.main()
