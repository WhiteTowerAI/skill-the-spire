# Surface: power

Everything the pipeline needs for one custom Power, in one place: the SPEC fields it must
declare, the element class the author writes, and the proof its verification owes. Read
this page at the `spec.md`, `author.md`, and `verify.md` stages for every authored custom
Power, whether it stands alone or is a dependency of a Card, relic, or potion.

## SPEC fields

Include one block for every authored custom Power.

A Power is usually a dependency of a Card, relic, or potion rather than a standalone Mod, so
this block sits alongside its host's `content:` section in the same SPEC. It uses the same
shared sections as every other surface; `contract`, `mod id`, and `author` are declared once
for the whole SPEC by the host.

```markdown
- **content**:
  - name: <shown name>
  - surface: power
  - logical id: <stable local stem>
  - type: Buff | Debuff
  - stack type: Counter | Single
  - amount domain: `[0, unbounded]` (default for Counter) | `[<min>, <max>]`
  - signed amounts: no (default) | yes - <what negative stacks mean>
- **registration**:
  - availability: shared
  - ownership: <the creature that carries it: player | enemy>
  - placement: applied by <the host element that applies it>
- **localization**:
  - languages: [eng, zhs]
  - fields: title=<shown name>; description=<hover text using {Amount}>
  - smartDescription: <usually the same text; required>
  - formatting: dynamic value placeholders; plain | bounded vanilla rich text
  - text spans: <description phrase -> blue/gold; apply to smartDescription too>
- **effects**:
  - trigger: <the exact hook or passive boundary the behavior runs on>
  - target: owner | the creature the owner affects
  - sequence: <precise hook/passive behavior with exact numbers>
  - scaling: <named values and bounds, or none>
- **hook participation**: none | one or more; see § Hook participation in `spec.md`
  - Power receives combat-scope hooks only (45 of 68). Run-scope hooks never reach a Power:
    the override compiles and never fires. `Owner` is a `Creature` directly.
- **state**:
  - lifetime: permanent | decays <amount> at <boundary> | removed when <condition>
  - owner: the creature holding the Power
  - reset: <exact boundary, or none for permanent>
  - visible state: native Amount display
- **presentation**:
  - assets: power icon; placeholder | generate
  - art source: runtime-imagegen | vofy | byo-http | local-image (generate only)
  - native presentation: standard Power icon plus composed title/description Hover Tip
  - extra badges: none | one
    - meaning: <player-facing auxiliary value distinct from Amount>
      value: <state value or bounded display rule>
      corner: top-left
      format: plain | bounded color rich text; at most 6 visible characters
      refresh: <state change that updates it>
      remove: <condition that hides/removes it>
- **fallback**:
  - missing asset: checked template power icon
  - unavailable seam: preserve behavior or stop with an explicit unsupported boundary
- **proof**:
  - scenario: driven through its real host (see § Self-test driver body)
  - driver: <the host interaction that applies it>
  - invariants: <exact expected/observed amount and the dependent effect it causes>
  - lifetime case: <the observation that proves the declared lifetime; required whenever
    lifetime is not "permanent">
- **adapter output** (written to MEMORY after acceptance): resolved content id,
  localization keys (`title`, `description`, `smartDescription`), power icon asset role,
  and framework diagnostic record
```

`amount domain` is mandatory for every custom `Counter`. Keep the nonnegative default
unless the design explicitly defines negative-stack behavior; `AllowNegative` is an
implementation property, not a substitute for this SPEC decision. Write finite bounds
as numbers rather than leaving them implicit. `Single` is a flag-like Power with hidden
amount 1, so it does not need a Counter domain.

`lifetime` is mandatory because a Power that never decays is a different design from one
that does, and the two are indistinguishable in a single-turn proof — see § Proof matrix.

A signed domain has a presentation consequence worth deciding deliberately: the engine
re-derives the displayed polarity from the current amount, so a Power whose amount crosses
zero flips its label color mid-combat. If that is not intended, keep the nonnegative default.

`{Amount}` is substituted by the engine, and the Hover Tip is composed from `title` plus
`description`/`smartDescription`. Write the placeholder, never a literal stack count, and do
not hand-write a second copy of the tip text.

Hand emphasis and extra badges are product semantics, not styling escape hatches. Record
why the player needs the signal and the game-state rule that owns it; never record RitsuLib
interfaces, predicates, `Color` objects, raw markup, rectangles, or invalidation event names
in SPEC. Relics use at most three distinct safe corners; Powers use at most one top-left
label because their preset label bands overlap in crowded rows. Every extra badge supplements
the native Power main amount instead of replacing it. Intent belongs to the public Extra
Badges Package and remains supported there, but it has no generated SPEC block because no
authoring recipe exists for it yet.

## Shared capability routes

Read `reference/model-capabilities.md` for separable behavior/state attached to this Power,
`reference/lifecycle-state-rng.md` when it crosses callbacks or persistence boundaries, and
`reference/shared-effect-hooks.md` for reachable per-hit attack, healing, Energy/Stars-gain
response, or maximum-hand-size behavior. The Power or its typed capability remains the owner and
inherits the Power's combat-scope lifetime.

Append only the selected reference's game-term SPEC block. Preserve amount/duration semantics,
exact phase/order, owner/subject guard, unchanged neutral behavior, and cleanup when the Power or
capability is removed. SelfTest must assert both the dependent effect and no second firing after
removal; do not use a process-wide listener.

## Ordinary effect projection

Choose an async Power hook whose phase and parameters match SPEC. `Owner` is the attached mutable
Creature; derive its Player only when `Owner.Player` is non-null. The Power is the truthful source
identity but not a Card source, and many hooks provide no `PlayerChoiceContext` or selected target.
Read `reference/effect-primitives.md` and author only commands whose required inputs are present.
For example, a guarded turn hook can affect `Owner`, while draw, targeted Power application, Orb
queue actions, or Max HP loss require the exact Player/context/target callback. A synchronous
value hook modifies its return value and cannot run an awaited effect sequence.

## Author the element class

**Custom power** — add `<ModName>Code/Powers/<PowerName>.cs` and extend `ModPowerTemplate`:

- Add exactly one `.Power<TPower>()` step to `MainFile.Content.cs`; do not rely on
  reflection discovery or add a pool attribute.
- Declare `Type`, `StackType`, and the SPEC amount domain. Clamp caller-owned changes and
  use `PowerCmd.ModifyAmount` to consume an existing nonnegative Counter.
- Emit `.title`, `.description`, and `.smartDescription` under the exact normalized public
  entry. Use `PowerAssetProfile` only for checked icon paths.
- Implement a non-permanent SPEC `lifetime` explicitly: tick it from the declared boundary
  hook with `PowerCmd.TickDownDuration(this)`. A Power that only ever gains amount is a
  permanent Power regardless of intent.
- For extra badges, implement `IPowerExtraIconAmountLabelSpecsProvider`; return only active
  bounded specs, never exceeding one `TopLeft` label, and add
  `IPowerExtraIconAmountLabelsChangeSource` only when the label state changes without
  `InvokeDisplayAmountChanged()`.

## Self-test driver body

A custom Power has no scenario of its own: it is driven through its real host. Use the
host's driver — a Card host uses `InCombat` per `surfaces/card.md` — and add the Power
assertions below to that run.

## Proof matrix

- Assert the applied amount with exact expected/observed values.
- Assert the dependent effect the amount causes, so the Power is proved to *do* something
  rather than merely exist at the right count.
- **Assert the declared lifetime.** Applied-amount plus one effect delta both observe the
  same turn, so a Power declared to decay passes that pair even when it never ticks — a
  temporary debuff silently becomes permanent. Whenever `lifetime` is not `permanent`,
  advance past the declared boundary and assert the reduced amount, then assert removal at
  zero. A Power declaring `permanent` records that and needs no extra case.
- Assert `Type` when the design depends on it being a Buff or a Debuff — it drives player-
  visible polarity and is never observed by an amount assertion alone.
- **Assert the declared amount domain at its bounds.** A single applied-amount assertion sits
  in the middle of the domain, so an unclamped Counter passes it while exceeding a finite
  maximum or going negative on consumption. For every finite bound, drive past it and assert
  the amount stopped there; for the nonnegative default, consume more than the current amount
  and assert no instance with a negative amount appears.
- For a signed domain, assert the negative-stack meaning declared in SPEC.
- **For hook participation — assert the neutral case outside the guard.** Modified-value and
  neutral-case assertions are both required: a hook that returns its modifier unconditionally
  passes a single-value test while changing every unrelated interaction in the run. Drive one
  event the guard is supposed to ignore and assert the value received by the host is unchanged.
  For a collection edit, also assert that an entry placed in the list before the edit survives.
