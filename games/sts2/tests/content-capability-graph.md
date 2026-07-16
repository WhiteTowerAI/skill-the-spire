# Current STS2 capability graph

This is the active support surface. Historical evidence rows and the M6 graph snapshot are
archived at `documents/history/content-capability-graph-through-m6.md`.

Support levels:

- **pipeline-supported:** natural-language intake through real hosted verification works;
- **scenario-verified:** a real host proof exists, but the generation/user path is not a
  current promise;
- **grounded:** API/host contract is known but not promoted;
- **unsupported:** preserve the idea as a pack gap.

## Pipeline-supported

| Capability | Host | Required proof | Current boundary |
|---|---|---|---|
| card / relic / potion / power | `CombatPlayer` | real source play/use/hook changes state | pooled registration rules; power auto-discovery |
| interaction | source host | source and dependent observations in dependency order | directed SPEC edge, not a `combo` type |
| keyword | `CombatPlayer` | host contains keyword and named rule changes state | tooltip alone is insufficient |
| enchantment | `CombatPlayer` | attachment plus altered host behavior | custom icon rendering remains provisional |
| orb | `CombatPlayer` | channel, passive, and evoke consequences | custom sprite rendering remains provisional |
| stateful relic cadence | multi-combat `CombatPlayer` | threshold/lifetime boundary; save round trip for run state | integer/bool relic state only |
| monster + encounter | `CombatEnemy` | encounter identity, move/history, exact state deltas | built-in fallback visual; custom Spine art unsupported |
| monster move vocabulary | multi-turn `CombatEnemy` | every declared cycle/branch and independent effect | deterministic/conditional branches |
| event / World Node | `MapNode` | real option UI click and run-state consequence | verified vanilla portrait placeholder |
| character Foundation | `RunStart` + `CombatPlayer` | selection, pools/starters, HP/energy, hosted mechanic | placeholder character visuals |
| character resource/payment/UI | Character suite | gain/affordability/spend/rejection/reset and live Label | combat-only, explicit payoff; not alternate Energy |
| ordered semantic buffer + dynamic output | Character suite | native source/compile destinations, visible order, overflow, output/history/effect/reset | semantic values only; source cards use native result piles |

## Scenario-verified infrastructure

| Capability | Boundary |
|---|---|
| typed capability kernel | Exact STS2 0.107.1 MVID-gated B postfix on `NCombatUi.Activate(CombatState)`; self-contained; no shared runtime |

## Direct next: M6 art coverage

The existing custom-art pipeline is pipeline-supported only for card, relic, power, and
potion assets. Before M7, research and extend it for the M6 surfaces currently marked
provisional/fallback: keyword/enchantment/orb presentation, monster scene/Spine assets,
event art, character select/combat art and animation, and character-mechanic UI.

Each promoted family needs a copyable path/size/format contract, deterministic import and
placement into the `.pck`, and real headed visual proof in its existing host. If a dynamic
scene or Spine family cannot be safely generated, retain the fallback and record the exact
grounded blocker rather than claiming support.

## Grounded / later depth

- run configuration and saved model references;
- owned entity / party roster;
- reward and rest-site option hosts;
- pet;
- run modifier;
- additional versioned patch bridges.

## Unsupported

- retained played-card `CustomPile` gameplay or custom zone UI;
- hidden card retention without a grounded presentation lifecycle;
- alternative-energy engine hooks;
- run-persistent or multiplayer character resources;
- vanilla content editing;
- novel Publicizer/transpiler targets generated from intuition;
- Act generation as part of the current Character/Core promise.

## Current regression ownership

Use `README.md` in this directory. Add a case to the nearest host suite when practical; a
separate project is allowed when it is the simpler maintainable choice. Fresh acceptance
projects do not become permanent fixtures automatically.
