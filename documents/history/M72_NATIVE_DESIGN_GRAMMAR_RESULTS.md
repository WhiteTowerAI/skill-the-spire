# M7.2 STS2-native Design Grammar Results

Date: 2026-08-04

## Result

M7.2 source development is complete after explicit human-lead selection. Character and
Character/content-set requests now lazily load
`sts2-api/design/character-foundation.md` after routing and before creative questions. The
reference keeps three knowledge classes distinct:

- **pinned fact:** exact `0.107.1` game/catalog identity or value;
- **observed convention:** a recommendation inferred from the five native Characters, not
  an engine restriction; and
- **creative decision:** the selected custom names, mechanics, counts, values, and accepted
  departures.

For a clear Character mechanic, the skill recommends one exact native-shaped starter deck
before asking for deck details. The normal starting proposal is four Character-specific
Strike, four Character-specific Defend, and two low-complexity setup/payoff identity Cards,
plus a Starter relic that reinforces the same lesson. It is explicitly not a universal
`4/4/2` or ten-Card rule. An implementable departure remains allowed after its onboarding,
Strike/Defend-tag compatibility, and early-balance consequences are recorded.

The Character intake and SPEC now preserve the grammar profile, pinned facts used,
observed analogy, exact creative deck/relic decision, rationale, and any deliberate
departure. This is bounded M7.2 design grounding, not M7.3 content-set/balance planning or
M7.4 `DESIGN.md` traceability, and it does not expand the runtime capability graph.

## Checked Inventory

`design/catalogs/character-foundation-sts2-0.107.1.json` records the exact five native
starter decks, HP, Gold, and Starter relics. The inventory was checked directly against
the installed pinned `sts2.dll` Character types. Its recorded assembly identity matches the
M6.7 catalog:

- SHA-256: `a1f9e653f1e28e4076558fee1e60d218619cb7e057b887c6417f62c62c6d7a52`;
- MVID: `97f10687-c306-4798-ab75-8b9f23f34dfb`.

The exact fact tests also parse the M6.7 catalog and check every Character-specific Strike
and Defend model: distinct internal type; English and Simplified-Chinese display title;
Basic rarity; 1 Energy; Strike/Defend tag; `6 -> 9` damage or `5 -> 8` Block. The
`spire-codex` Character data agrees with the direct inventory but remains corroborating
research rather than sole authority.

## Behavioral Contract

`games/sts2/tests/m72-native-grammar-scenarios.md` records three semantic cases:

1. a Character with a clear mechanic and unspecified deck receives an exact native-shaped
   proposal without a blank ten-Card questionnaire;
2. a Character/content-set request begins from the Foundation teaching pair while full
   role/archetype/economy/balance planning remains M7.3; and
3. a deliberate implementable 12-unique-Basic departure is preserved after one unresolved
   tag question and explicit consequence handling.

A source-contract review checked all three against the shipped instructions. No independent
forward-model output was produced, so actual model behavior is not inferred from the
scenario definitions or static assertions.

## Verification

- focused M7.2 native-grammar contract: `8/8` passed;
- adjacent M7.1 routing and semantic contracts: combined focused run `31/31` passed;
- complete STS2 Python regression: `193/193` passed;
- Python compilation: passed for `games/sts2/tools`;
- `quick_validate.py`: passed for source modmaker/sts2-api, plugin modmaker/sts2-api, and
  portable modmaker/sts2-api;
- plugin and portable payloads: `164` effective files each, zero parity differences;
- forced publish repeatability: both passes produced tree SHA-256
  `9bc725d1b82a377cbadae5721db3e4da049435b7f22e16e9e576b48b9144c0b0`;
- new grammar source/plugin/portable SHA-256:
  `546f326260f1f81117a090b9843ae3a6bb6885be984f23593602e3697b2b2024`;
- new checked inventory source/plugin/portable SHA-256:
  `d1d9e131fb99cf6f9bb96afd68fdccfbf2bd13df32f65e36a08f55e4cbf1b35e`.

## Explicit Exceptions

- No independent fresh-agent or forward-model execution of the three prompts was run.
- No generated Mod, build, game launch, Tier 1, Tier 2/SelfTest, headed review, or playtest
  was run. M7.2 changes prompt/design workflow only and does not change generated runtime
  behavior or presentation.
- No balance or enjoyment claim is made from native analogy or static tests.
- M7.3 and later Packages were not started or authorized by this result.
