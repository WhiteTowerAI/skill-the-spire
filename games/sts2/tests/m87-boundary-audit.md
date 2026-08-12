# M8.7 product-boundary audit ledger

This is the active source-development ledger for the boundary families selected in
`documents/IMPLEMENTATION_PLAN.md`. It freezes the restriction classification before the v3
authoring contract changes. The evidence is pinned to STS2 `0.107.1`, RitsuLib `0.5.4`
(`8b971a79e6b0a62daddd948790cd3661bb13a930`), and the official tutorial checkout
`5a9110b3c1b1c428f9f349e51cd4a155266b92e3`. Historical proof records are evidence only.

Categories are the Package contract's exact categories: **1** game/framework hard boundary,
**2** current open-mod implementation boundary, **3** proof-fixture detail promoted to policy,
**4** deliberate reliability/safety constraint, and **5** unresolved research question.

| Finding | Existing restriction and pinned evidence | Category | M8.7 disposition |
|---|---|---:|---|
| B-01 secondary resources | `character-resource.md` admits one combat-only zero-default resource in one fixed Character UI. RitsuLib `SecondaryResourceDefinition`, `SecondaryResourcePersistencePolicy`, `SecondaryResourceTurnStartPolicy`, `SecondaryResourcePlayUse`, payment planning/commit, and `NSecondaryResourceCounterRow` expose named bounded resources, combat/run persistence, fixed/X and required/optional/extra uses, shortfall handling, and multi-counter UI. | 2, 3 | Replace the one-resource fixture with a bounded list contract and exact public registry/state/payment/UI lowering. Keep native Energy separate, require authoritative payment before payoff, and keep multiplayer unclaimed (1, 4). X repeatable-extra payment remains rejected by the pinned API contract (1). |
| B-02 Monster moves | `monster.md` admits deterministic cycles and exhaustive conditional branches and says random is a different design. STS2 `RandomBranchState.GetNextState(Creature, Rng)` exposes weighted branches using the move machine's supplied run RNG. | 2, 3 | Admit deterministic, conditional, and explicitly weighted random branches. Require positive weights, registered successors, reachable states, exact intent/effect pairs, and the supplied RNG route. Dynamic prompt-authored weight delegates remain blocked (4, 5). |
| B-03 Monster/Encounter composition | The current recipe makes exactly one Monster+Encounter vertical slice. Public `ModMonsterTemplate`, `ModEncounterTemplate`, `AllPossibleMonsters`, and `GenerateMonsters` independently model registrations and roster edges. | 2, 3 | Admit separate Monster and Encounter nodes, reusable Monsters, multi/repeated rosters, and checked actual/all-possible consistency. Keep unique registration and grounded placement (1, 4). Registration alone remains non-observation (4). |
| B-04 Monster HP | The current surface uses one `hp` value and lowers equal `MinInitialHp`/`MaxInitialHp`. Both public overrides exist independently. | 3 | Admit positive ordered `min_hp`/`max_hp`; equal values remain shorthand. Ascension formulas remain a separate unresolved route (5), and one observed roll never proves the range distribution (4). |
| B-05 Character starts | The current Foundation hardcodes normal 3 Energy, no starter Potions, and a narrow deck/relic shape. `CharacterModel` exposes `StartingHp`, `StartingGold`, `MaxEnergy`, `BaseOrbSlotCount`, typed pools, `StartingDeck`, `StartingRelics`, and `StartingPotions`; RitsuLib `ModCharacterTemplate` seals typed pool resolution and exposes additive starter registration for all three starter kinds. | 2, 3 | Make HP, Gold, MaxEnergy, Orb slots, starter multisets, and typed pools explicit current-SPEC decisions. Require game-valid nonnegative/positive domains and every starter to exist in the registered typed content graph (1, 4). Native values remain analogies, not forced defaults. |
| B-06 Rest Site owner | The shipped route admits only a Relic owner, although `TryModifyRestSiteOptions` is an `AbstractModel` hook and Card is in its dispatch listener surface; RitsuLib owns `ModRestSiteOptionTemplate`. Modifier ownership has no selected custom owner surface. | 2, 3, 5 | Admit Relic and Card owners through the same public hook/template lifecycle. Modifier remains blocked (5). Keep singleplayer, render-time snapshot, eligibility/affordability separation, deterministic preflight, matching owner/state handles, no same-visit success repeat, and native stay/leave (1, 4). |
| B-08 computed Card values | The reference semantics already describe every value independently, but the surface and examples center one named formula and one focused matrix. RitsuLib `ModCardVars.Computed*` factories and typed execution reads are per DynamicVar and compose on one Card. | 2, 3 | Admit zero or more uniquely named value declarations. Each retains a pure formula, complete inputs, domain, timing, upgrade, text binding, role-specific zero rendering, and exactly-once native hook application (1, 4). No RNG/mutation/hidden inputs. |
| B-09 bounded state | Current authoring has a Relic cadence and one ordered-card-buffer profile. RitsuLib `AttachedState`/`SavedAttachedState` and `SavedProperties` compatibility support reusable bounded owner state. | 2, 3 | Admit a closed structural state vocabulary: bounded scalar schema, declared lifetime/transitions/reset/persistence/visibility/consumers/outputs, exact owner and grounded hooks. Keep arbitrary executable state machines, retained played-Card instances/custom zones, unsupported saved types, and missing refresh routes blocked (1, 4). |
| B-10 forced Events | `forced-followup-event.md` admits one token, one act, one target. Public `ModifyUnknownMapPointRoomTypes` and `ModifyNextEvent` accept bounded mapping logic. | 2, 3 | Admit a bounded ordered mapping list with explicit act set, priority, fail-closed conflict, consumption, and a finite unique terminating sequence. Keep singleplayer, neutral returns, pool exclusion, no mutable canonical cache, no fixed map-node guarantee, and save/resume `game-unobserved` (1, 4, 5). |
| B-13 new-Card Star costs | The new-Card surface declares Energy only while computed values can display/gain Stars. STS2 `CardModel` publicly exposes `CanonicalStarCost`/`HasStarCostX` alongside the native Energy cost lifecycle, and vanilla Cards use fixed Star costs. | 2, 3 | Admit independent native Energy and fixed/X Star declarations, upgrades, text/icons, and payment flags. Keep a parallel Star store forbidden; reject simultaneous Energy-X and Star-X until their combined replay/payment semantics are grounded (1, 5). Fixed/X combinations remain `game-unobserved`. |
| B-15 Event acquisition/shake | The current option envelope admits one acquisition-presentation value and only `weak_short`. Native public Cmds support ordered Card/relic acquisition; STS2 `TheArchitect` uses both `Weak/Short` and `Strong/Normal` through `NGame.ScreenShake`. | 2, 3 | Admit an ordered unique list of known Card/relic acquisitions and allowlisted `weak_short`/`strong_normal` one-shot profiles. Require one grant per item, matching native presentation, setting-respecting bounded shake, and no duplicate/custom holder (1, 4). Rumble, hit stop, custom targets, Forever, and arbitrary VFX remain blocked. |

## Retained non-selected boundaries

B-07 keyword icons, B-11 broader target predicates, B-12 per-frame hand emphasis, and B-14
parameterized Character combat cues are not selected. Their current authoring boundaries stay
unchanged. M8.7 also does not promote multiplayer, arbitrary Harmony/reflection/Publicizer/IL,
arbitrary custom UI/VFX, physical retained-card zones, or cross-Mod conflict coordination.

## Evidence labels

The pinned framework is expressible for the admitted shapes above. M8.7 can make them
`open-mod-authorable` only after their v3 contract, lowering guidance, and shared structural
validation settle. Existing narrow proof fixtures keep their recorded observation status; every
newly generalized variant is `game-unobserved`. No compile, Tier 1, Tier 2, headed review, game
launch, or save round trip is established by this ledger.
