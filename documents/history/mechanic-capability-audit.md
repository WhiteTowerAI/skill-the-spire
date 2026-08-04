# Stateful mechanic capability audit (2026-07-15)

> **Maintainer-only. NOT shipped.** This audit answers a narrower question than the
> Content Capability Graph: when a supported element remembers something, which state
> lifetimes can the pipeline author and prove without guessing?

## Contract

Every stateful effect records `event + threshold/phase + lifetime + reset +
persistence + proof`. A counter is state on a real relic/card/power, not a new element type.

Only rows marked **pipeline-supported** may be advertised without a qualification.
`grounded` means the stable STS2/BaseLib pattern is documented, but its exact scenario
shape has not completed this repository's Type + Scenario + natural-language gates.

| Mechanic family | Lifetime / storage | Grounded analog | Current proof | Support | Remaining boundary |
|---|---|---|---|---|---|
| Stateless lifecycle trigger | none | `Lantern`, existing card/potion/relic canaries | existing Type + `CombatPlayer` cells | **pipeline-supported** | effect-specific Cmd must still exist in the pack |
| Every N turns across combats | run; `[SavedProperty] int` modulo progress | `HappyFlower`, `Nunchaku`, `PenNib`, `TuningFork` | `CadenceCanary`: progress `1 -> 2`, save restore `2`, second-combat threshold `2 -> 0`, Energy `3 -> 4` | **pipeline-supported (relic int cadence)** | profile/meta persistence remains out of scope |
| On turn N / every N turns in each combat | combat; `PlayerCombatState.TurnNumber` | `StoneCalendar` | `CadenceCanary`: turn-2 effect, next combat `TurnNumber=1`, no second activation | **pipeline-supported (relic turn cadence)** | other owner/side hooks still need their effect-specific Cmd |
| Every N cards/events this turn | turn; ordinary `int`, owner-turn reset | `OrnamentalFan`, `LetterOpener` | stable-v0.107.1 decompile + copyable state page; no dedicated generated scenario | **grounded** | play N events, prove trigger, start next turn, prove zero/reset |
| Once per combat | combat; ordinary `bool`, reset on `AfterRoomEntered(CombatRoom)` | `Permafrost` | stable decompile + copyable state page; no dedicated generated scenario | **grounded** | fire twice in combat 1 (one effect), enter combat 2 (eligible again) |
| Previous-turn memory | combat; ordinary current/previous fields | `Pocketwatch` | stable decompile + copyable shift/reset pattern | **grounded** | play events on turn 1, prove turn-2 decision, then combat reset |
| Limited uses / cumulative total this run | run; `[SavedProperty] int/bool` | `WingedBoots`, `Girya`, `WongosMysteryTicket` | holder/value support grounded; CadenceCanary proves custom-relic int serialization but not the used-up lifecycle | **grounded** | exhaust limit, assert disabled/remaining UI, save round trip |
| Persistent state on a Card/Enchantment/Modifier | run; supported base holder + supported `[SavedProperty]` value | BaseLib `SavePatchUtils` holder scan | decompile only | **grounded** | one real custom holder save/resume scenario per family |
| Counter Power stack amount | combat model state; explicit amount domain | vanilla Power Cmds + Honed Edge review | zero/fewer/at-least consumption matrix and post-hook amount contract | **pipeline-supported** | this is not a cross-combat counter; never substitute it for run state |
| Potion or arbitrary custom-holder saved state | no base holder support | BaseLib warns and points to `SavedSpireField` / extended saves | warning path grounded only | **not supported** | separate advanced-save recipe + serialization/network canary |
| Profile/meta progress across runs | progress-save API, not run save | not grounded for mods | none | **not supported** | separate milestone; never claim `[SavedProperty]` survives run end |
| Arbitrary object/dictionary/float saved state | advanced serialization | not base `[SavedProperty]` | none | **not supported** | explicit serializer, versioning, multiplayer and migration contract |
| Wall-clock/real-time timer | process/time source | none | none | **not supported** | deterministic/replay-safe design required first |

## BaseLib save boundary

BaseLib 3.3.x injects a custom type into `SavedPropertiesTypeCache` when it finds a valid
`[SavedProperty]` on a supported holder. Base values: `int`, `bool`, `string`, `ModelId`,
`int[]`, enum/enum arrays, `SerializableCard`, `SerializableCard[]`, and
`List<SerializableCard>`. Base holders: `RelicModel`, `CardModel`, `EnchantmentModel`,
and `ModifierModel`. The shipped stateful relic path deliberately uses `int`/`bool` only.

## Evidence

- STS2 stable v0.107.1 decompile:
  `HappyFlower`, `StoneCalendar`, `OrnamentalFan`, `LetterOpener`, `Permafrost`,
  `Pocketwatch`, `WingedBoots`.
- BaseLib v3.3.5 decompile:
  `PostModInitPatch`, `SavePatchUtils`, `SavedSpireFieldPatch`.
- `CadenceCanary` (gitignored `.claude/canary-cadence-work`, 2026-07-15): build
  0 warnings / 0 errors; Tier 1 PASS; Tier 2 PASS through two real combats and an
  in-process `SavedProperties.From`/`Fill` round trip.
- Shipped contracts:
  `reference/stateful-mechanics.md`, `reference/selftest-harness.md`, and the
  interview/SPEC/author routing.
