# STS2-native Character Foundation grammar

Load this reference only when the request creates, revises, or discusses a playable
Character or its content set. It guides design conversation; it does not add a runtime
route and never overrides the supported capability graph.

## Evidence boundary

This slice is pinned to STS2 `0.107.1` and the
`ritsulib-0.5.4-sts2-0.107.1` profile. Exact starter inventories come from direct
inspection of the five Character types in the pinned `sts2.dll` and are recorded in
`design/catalogs/character-foundation-sts2-0.107.1.json`. Exact Card identities,
localized titles, costs, tags, and values come from
`reference/vanilla-overrides/catalogs/sts2-0.107.1.json`.

`baselines/spire-codex/data/characters.json` and `cards.json` are useful corroborating
research, not independent authority. Recheck the pinned assembly/catalog before promoting
facts for another host version.

Keep these categories explicit in reasoning and artifacts:

- **Pinned fact:** a value or identity checked against the exact versioned game/catalog.
- **Observed convention:** a pattern inferred from the five native Characters. It is a
  strong default, not an engine restriction or universal rule.
- **Creative decision:** the selected custom Character's names, mechanics, counts, values,
  and intentional departures. Attribute these to the user's idea or the proposed design,
  never to vanilla.

## Pinned starter facts

| Character | Exact native starter deck | Total | Identity teaching cards |
| --- | --- | ---: | --- |
| Ironclad | 5 `StrikeIronclad`, 4 `DefendIronclad`, 1 `Bash` | 10 | Bash introduces Vulnerable |
| Silent | 5 `StrikeSilent`, 5 `DefendSilent`, 1 `Neutralize`, 1 `Survivor` | 12 | Neutralize and Survivor introduce Weak and discard |
| Defect | 4 `StrikeDefect`, 4 `DefendDefect`, 1 `Zap`, 1 `Dualcast` | 10 | Zap and Dualcast introduce Orb channel/evoke play |
| Necrobinder | 4 `StrikeNecrobinder`, 4 `DefendNecrobinder`, 1 `Bodyguard`, 1 `Unleash` | 10 | Bodyguard and Unleash introduce Osty |
| Regent | 4 `StrikeRegent`, 4 `DefendRegent`, 1 `FallingStar`, 1 `Venerate` | 10 | Falling Star and Venerate introduce debuffs and Stars |

Each Character owns distinct Strike and Defend model types, but all five display as
`Strike` / `Defend` in English and `打击` / `防御` in Simplified Chinese. All ten are
`Basic` Cards with these exact pinned properties:

- Strike: 1 Energy, `6 -> 9` damage, `CardTag.Strike`.
- Defend: 1 Energy, `5 -> 8` Block, `CardTag.Defend`.

The native totals are 10 or 12. The observed counts are a design range, not a universal
ten-Card rule and not a universal `4/4/2` rule.

## Native-shaped recommendation

Before asking the user to design a starter deck, recommend one exact deck that expresses
their stated Character identity. Unless the idea itself supports another native analogy,
start from this compact proposal:

- 4 named Character-specific `Strike` Cards with the pinned Strike shape;
- 4 named Character-specific `Defend` Cards with the pinned Defend shape;
- 1 named low-complexity Basic setup Card that exposes the core mechanic;
- 1 named low-complexity Basic payoff Card that uses or advances it;
- 1 Starter relic whose simple effect makes that same first-run lesson reliable.

An exact proposal includes every Card name, count, base effect, upgrade, total deck size,
and the Starter relic effect. Derive the two teaching Cards from the requested fantasy and
use only grounded operations. Do not show placeholders as if they were a completed
recommendation, and do not ask the user to name ten Cards or choose raw counts from a blank
form.

If the central mechanic is still unknown and materially changes the teaching pair, ask
about that one high-impact player decision first. Then propose the complete deck. If the
mechanic is clear, present the exact proposal at confirmation without adding a deck
question. A Character/content-set request loads this same Foundation grammar first; full
pool roles, archetype coverage, economy, and balance planning remain M7.3 work.

Use native analogies deliberately:

- `5 Strike / 4 Defend / 1 identity` fits one self-contained teaching Card and a slightly
  more attack-weighted opening, as in Ironclad.
- `4 Strike / 4 Defend / 2 identity` fits a setup/payoff pair, as in Defect,
  Necrobinder, and Regent.
- A 12-Card starter is observed on Silent, but the single example does not make 12 Cards a
  general recommendation.

These are observed conventions. The chosen shape, teaching effects, and values remain
creative decisions.

## Deliberate departures

Do not reject an implementable departure merely because it is non-native. State the
departure and its player-facing consequences before confirmation:

- **Onboarding:** more unique or more complex Basic Cards increase the number of rules a
  player must learn in the first combats; fewer teaching Cards may hide the core mechanic.
- **Compatibility:** renaming Strike/Defend is player-facing only, but removing
  `CardTag.Strike` or `CardTag.Defend` also opts out of effects that inspect those tags.
- **Balance:** changing deck size or duplicate counts changes first-hand frequency, early
  consistency, upgrade/removal pressure, and how often the Starter relic's lesson appears.

Ask only for an unresolved consequence that changes the deliverable, such as whether
renamed baseline Cards retain their native tags. Once the user accepts the trade-off,
preserve the departure literally; do not silently normalize it back to the recommendation.

## SPEC handoff

For a Character, carry these fields into the Character Foundation block in `SPEC.md`:

- grammar profile and pinned facts used;
- observed convention used as the recommendation;
- exact creative deck/relic decision and rationale; and
- deliberate departure plus onboarding, compatibility, and balance consequences, or
  `none`.

This bounded design basis is not M7.4 `DESIGN.md` traceability and does not authorize an
unsupported operation.
