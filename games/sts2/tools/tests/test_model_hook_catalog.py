"""The pinned model-hook surface as data, and the invariants the catalog must hold.

M8.2 needs the authoring surface to know which scalar/decision hooks a given generated
element can actually *receive*. That is not the same question as which hooks exist: `Hook`
dispatches through iterators whose listener sets differ, and the run-scope set carries no
Powers, Orbs, or Monsters. A hook overridden outside its dispatching set compiles, ships,
and never fires -- the exact shape of the M7.6 Wrath failure, so getting it wrong would add
instances of the bug M8.2 exists to prevent.

`reference/catalogs/model-hooks-sts2-0.107.1.json` is a generated projection of the pinned
`0.107.1` decompile, written by `collect_model_hooks.py`. Unlike the art contract, the source
is maintainer-only and gitignored, so `--check` cannot run in a clean checkout. These tests
therefore validate the *committed* catalog's internal consistency and its agreement with the
shipped prose, and skip the freshness re-extraction when the decompile is absent.

What these tests do not establish: that any hook behaves as described in a running game.
Reachability is derived from pinned source and cross-checked against vanilla implementors;
only a real host run proves a generated override fires.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path


TOOLS_DIR = Path(__file__).resolve().parents[1]
COLLECTOR = TOOLS_DIR / "collect_model_hooks.py"
REPO_ROOT = TOOLS_DIR.parents[2]
STS2_API_DIR = REPO_ROOT / "games" / "sts2" / "skills" / "sts2-api"
CATALOG_PATH = (
    STS2_API_DIR / "reference" / "catalogs" / "model-hooks-sts2-0.107.1.json"
)
NON_CARD_PATH = STS2_API_DIR / "reference" / "vanilla-non-card-overrides.md"
DECOMP_ROOT = REPO_ROOT / "baselines" / "decomp" / "sts2_full"

sys.path.insert(0, str(TOOLS_DIR))
import collect_model_hooks  # noqa: E402


def snake(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


class SemanticIdTests(unittest.TestCase):
    """The id a SPEC declares is catalog data, not something each consumer derives.

    `vanilla-non-card-overrides.md` already names these hooks in snake_case for vanilla
    owners. A custom surface declaring the same hook must use the same id, or the two halves
    of one assembly fact drift — so the id is carried in the catalog and checked against both
    the CLR name and the shipped vanilla list.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        cls.hooks = {entry["hook"]: entry for entry in cls.catalog["hooks"]}

    def test_every_hook_carries_a_semantic_id(self) -> None:
        seen: set[str] = set()
        for name, entry in self.hooks.items():
            with self.subTest(hook=name):
                semantic_id = entry.get("semantic_id")
                self.assertTrue(semantic_id, f"{name} has no semantic_id")
                self.assertEqual(snake(name), semantic_id)
                self.assertNotIn(semantic_id, seen, f"duplicate semantic id {semantic_id}")
                seen.add(semantic_id)

    def test_semantic_ids_match_the_shipped_vanilla_naming(self) -> None:
        reference = NON_CARD_PATH.read_text(encoding="utf-8")
        for family, intro in (
            ("numeric", "The scalar list is every public"),
            ("decision", "The decision list is every public"),
        ):
            start = reference.find(intro)
            fence = reference.find("```text", start)
            end = reference.find("```", fence + 7)
            listed = set(re.findall(r"[a-z][a-z0-9_]+", reference[fence + 7 : end]))
            catalog_ids = {
                entry["semantic_id"]
                for entry in self.hooks.values()
                if entry["family"] == family
            }
            with self.subTest(family=family):
                self.assertEqual(listed, catalog_ids)


class ModelHookCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        cls.hooks = {entry["hook"]: entry for entry in cls.catalog["hooks"]}

    def test_schema_and_counts(self) -> None:
        self.assertEqual(collect_model_hooks.SCHEMA, self.catalog["schema"])
        self.assertEqual("0.107.1", self.catalog["host_version"])
        counts = self.catalog["counts"]
        # Counted from the pinned assembly, not chosen. The 26 and 28 also appear in
        # `vanilla-non-card-overrides.md`, which the pairing test below holds to them.
        self.assertEqual(26, counts["numeric"])
        self.assertEqual(28, counts["decision"])
        self.assertEqual(14, counts["trymodify"])
        self.assertEqual(len(self.hooks), counts["total"])

    def test_digest_matches_content(self) -> None:
        self.assertEqual(
            collect_model_hooks.catalog_digest(self.catalog),
            self.catalog["catalog_sha256"],
            "catalog_sha256 does not match its own content; it was hand-edited",
        )

    def test_every_hook_records_a_neutral_default(self) -> None:
        """The default is what a guard must return outside its case.

        A hook that returns its modifier unconditionally still passes a single-value
        assertion while changing every unrelated interaction in the game, so the neutral
        value is authoring input, not trivia.
        """
        for name, entry in self.hooks.items():
            with self.subTest(hook=name):
                self.assertTrue(entry["neutral_default"].strip())
                self.assertTrue(entry["signature"].startswith(entry["return_type"]))
                self.assertIn(entry["family"], {"numeric", "decision", "trymodify"})

    def test_every_hook_resolves_to_a_known_dispatch_iterator(self) -> None:
        """An unresolved scope is a gap, never a permissive default (INV-3)."""
        known = set(collect_model_hooks.ITERATORS)
        for name, entry in self.hooks.items():
            with self.subTest(hook=name):
                self.assertTrue(
                    entry["dispatchers"], f"{name} has no Hook.cs dispatcher recorded"
                )
                self.assertTrue(entry["dispatch_iterators"])
                for form in entry["dispatch_iterators"]:
                    self.assertIn(form, known, f"{name} dispatches through unknown {form}")
        self.assertEqual([], self.catalog["unresolved_hooks"])
        self.assertEqual(0, self.catalog["counts"]["unresolved"])

    def test_unresolved_hooks_are_never_authorable(self) -> None:
        for name, entry in self.hooks.items():
            if entry.get("unresolved"):
                with self.subTest(hook=name):
                    self.assertEqual([], entry["authorable_surfaces"])

    def test_no_reachability_contradiction_against_vanilla(self) -> None:
        """A vanilla override on a family the catalog calls unreachable means the
        derivation is wrong.

        This is the check that invalidated the first attempt at this table. A context-window
        heuristic put `ModifyDamageAdditive` in run-only scope while vanilla Powers override
        it; body-scoped dispatcher attribution resolved it to `ModifyDamageInternal`, which
        iterates with a combat state.
        """
        self.assertEqual([], self.catalog["reachability_contradictions"])

    def test_authorable_surfaces_follow_listener_membership(self) -> None:
        surfaces = collect_model_hooks.GENERATED_SURFACES
        for name, entry in self.hooks.items():
            if entry.get("unresolved"):
                continue
            listeners = set(entry["listener_families"])
            expected = {
                surface
                for surface, listener in surfaces.items()
                if listener in listeners
            }
            if entry.get("enchantment_redirect"):
                expected.discard("enchantment")
            with self.subTest(hook=name):
                self.assertEqual(sorted(expected), entry["authorable_surfaces"])

    def test_run_only_hooks_are_unreachable_on_combat_only_surfaces(self) -> None:
        """The constraint the whole catalog exists for.

        A Power, Orb, or Monster is only in the combat listener set. A hook dispatched
        exclusively through `runState.IterateHookListeners(null)` can therefore never reach
        one, and offering it as authorable there would ship silent no-ops.
        """
        combat_only = {"power", "orb", "monster"}
        run_only_form = "runState.IterateHookListeners(null)"
        checked = 0
        for name, entry in self.hooks.items():
            if entry["dispatch_iterators"] != [run_only_form]:
                continue
            checked += 1
            with self.subTest(hook=name):
                self.assertEqual(
                    set(), combat_only & set(entry["authorable_surfaces"])
                )
        self.assertGreater(checked, 0, "no run-only hooks found; the split is not modelled")

    def test_enchantment_redirects_replace_the_general_hook(self) -> None:
        """`EnchantmentModel` documents five hooks an Enchantment MUST use instead."""
        redirects = collect_model_hooks.ENCHANTMENT_REDIRECTS
        self.assertEqual(5, len(redirects))
        for general, replacement in redirects.items():
            with self.subTest(hook=general):
                entry = self.hooks[general]
                self.assertEqual(replacement, entry["enchantment_redirect"])
                self.assertNotIn(
                    "enchantment",
                    entry["authorable_surfaces"],
                    f"{general} must route to {replacement} on an Enchantment",
                )

    def test_declaration_shape_follows_the_signature(self) -> None:
        """Three shapes, because a collection edit cannot be declared as a value.

        A `TryModify*` with an `out` parameter replaces a value and declares like a scalar
        hook plus a taken/not-taken flag. One carrying a `List<>`/`ISet<>`/`ICollection<>`
        mutates a list the host owns, and its `bool` reports only that it touched it — so its
        declaration must say what is added or removed and how it composes with other editors,
        which is a different authoring shape rather than a longer one.
        """
        shapes = self.catalog["declaration_shapes"]
        self.assertEqual(54, shapes["scalar-return"])
        self.assertEqual(6, shapes["out-replacement"])
        self.assertEqual(8, shapes["collection-edit"])

        for name, entry in self.hooks.items():
            shape = entry["declaration_shape"]
            with self.subTest(hook=name):
                if shape == "collection-edit":
                    self.assertIn("collection_parameter", entry)
                    self.assertNotIn("out_parameter", entry)
                elif shape == "out-replacement":
                    self.assertIn("out_parameter", entry)
                    self.assertTrue(entry["out_parameter"].startswith("out "))
                    self.assertNotIn("collection_parameter", entry)
                else:
                    self.assertNotIn("collection_parameter", entry)
                    self.assertNotIn("out_parameter", entry)

    def test_every_out_replacement_is_a_trymodify(self) -> None:
        for name, entry in self.hooks.items():
            if entry["declaration_shape"] == "out-replacement":
                with self.subTest(hook=name):
                    self.assertEqual("trymodify", entry["family"])

    def test_route_owned_hooks_name_a_real_shipped_route(self) -> None:
        """A hook an existing route already owns must route through it, not around it.

        `TryModifyRestSiteOptions` is how the shipped Relic-owned Rest Site option is
        contributed, and that route carries boundaries the raw hook does not — singleplayer,
        absent versus natively disabled, fixed Gold, a fully preflightable outcome. Offering
        the bare hook beside it would let a generated Mod bypass all four.
        """
        owners = collect_model_hooks.ROUTE_OWNERS
        self.assertTrue(owners, "no route ownership recorded")
        for hook, route in owners.items():
            with self.subTest(hook=hook):
                self.assertIn(hook, self.hooks)
                self.assertEqual(route, self.hooks[hook]["owned_by_route"])
                self.assertTrue(
                    (STS2_API_DIR / route).is_file(),
                    f"{hook} names route {route}, which does not exist",
                )

    def test_shipped_vanilla_lists_match_the_assembly(self) -> None:
        """`vanilla-non-card-overrides.md` states the same 26 and 28 for vanilla owners.

        Two independently maintained statements of one assembly fact. Comparing them is how
        a future host bump that changes the hook surface fails loudly instead of leaving one
        of the two silently wrong.
        """
        reference = NON_CARD_PATH.read_text(encoding="utf-8")

        def listed(after: str) -> set[str]:
            start = reference.find(after)
            self.assertNotEqual(-1, start, f"missing list intro: {after!r}")
            fence = reference.find("```text", start)
            end = reference.find("```", fence + 7)
            return set(re.findall(r"[a-z][a-z0-9_]+", reference[fence + 7 : end]))

        for family, intro in (
            ("numeric", "The scalar list is every public"),
            ("decision", "The decision list is every public"),
        ):
            expected = {
                snake(name)
                for name, entry in self.hooks.items()
                if entry["family"] == family
            }
            with self.subTest(family=family):
                self.assertEqual(expected, listed(intro))


class CollectorFreshnessTests(unittest.TestCase):
    """Re-extraction, when the maintainer-only decompile is present.

    Skipped in a clean checkout: `baselines/` is gitignored, so a contributor without the
    research snapshot cannot regenerate the catalog. That is why the tests above validate the
    committed file on its own terms rather than relying on this one.
    """

    def test_committed_catalog_is_current(self) -> None:
        if not DECOMP_ROOT.is_dir():
            self.skipTest("maintainer-only decompile absent; cannot re-extract")
        result = subprocess.run(
            [sys.executable, str(COLLECTOR), "extract", "--check"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            0,
            result.returncode,
            f"catalog is stale; re-run collect_model_hooks.py extract\n"
            f"{result.stdout}{result.stderr}",
        )


if __name__ == "__main__":
    unittest.main()
