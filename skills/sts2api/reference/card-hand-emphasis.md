# Conditional Card hand emphasis

Use this reference only when a Card SPEC selects hand emphasis. The supported generated
shape is one or more ordered rules on one generated Card type. Each rule has one
player-facing meaning, a deterministic live-state condition, one fixed color, an integer
priority, and an explicit unplayable-visibility choice.

This route is pinned to STS2 `0.107.1` and RitsuLib `0.6.7`. It uses the official Card
Hand Glow API without generating Harmony, reflection, Publicizer, or IL.

## Semantic and runtime contract

- Preserve one or more ordered rules in SPEC order.
- The highest active priority wins. If active priorities tie, ties favor the later listed
  rule because it is registered later. Prefer distinct priorities unless the requested
  order itself is meaningful.
- `gold` means an actionable bonus, `red` means a warning, and a custom color must resolve
  to one opaque Godot `Color`. Color is presentation only and never changes the effect.
- `while unplayable: hide` is the default. Lower `show` only when the warning or bonus is
  still useful while the Card cannot be played.
- A rule that returns no match must leave the normal playable/gold/red hand feedback in
  control. Do not hide, replace, or recolor the Card body.

Do not author emphasis that is merely decorative. Do not retain a Card instance in the
registration lambda, poll remote-player state, or make a semantic rule depend on a node,
hover state, drag state, or screen geometry.

## Lowering

For exactly one `gold` or `red` rule with no competing rule, the generated Card may use the
native channel directly:

```csharp
protected override bool ShouldGlowGoldInternal => <typed live-state condition>;
// or:
protected override bool ShouldGlowRedInternal => <typed live-state condition>;
```

For multiple rules or any custom color, put every rule for that Card in one typed outline
registration. Do not mix native gold/red overrides with outline rules on the same generated
Card type; the two routes do not share one priority resolver.

Add the rules to the same content-pack builder that registers the Card:

```csharp
using Godot;
using STS2RitsuLib.Scaffolding.Cards.HandOutline;

RitsuLibFramework.CreateContentPack(ModId)
    .Card<ColorlessCardPool, Cards.<CardName>>()
    .CardHandOutline<Cards.<CardName>>(
        ModCardHandOutlineRules<Cards.<CardName>>.Of(
            ModCardHandOutlineSwitchRule<Cards.<CardName>>.Fixed(
                card => <lower-priority condition>,
                Colors.Gold,
                priority: 10,
                visibleWhenUnplayable: false),
            ModCardHandOutlineSwitchRule<Cards.<CardName>>.Fixed(
                card => <higher-priority condition>,
                <resolved custom Color>,
                priority: 20,
                visibleWhenUnplayable: true)))
    .Apply();
```

Use `Fixed`, not `Dynamic` or `Switch`, for the current generated semantic shape. Its
fixed-color rule has `RefreshEveryFrame: false`; normal combat-state refreshes reevaluate
the full hand and restore vanilla color before RitsuLib applies the best active rule. A
condition whose value can change without a normal combat-state refresh is outside this
authoring slice. Stop and report that boundary instead of enabling polling or adding a
patch.

When resolving a custom color, write an explicit `new Color(r, g, b)` with each component
in `[0,1]`; never preserve user text as executable code. Use `Colors.Gold` and `Colors.Red`
for the semantic built-ins.

## Verification

Use `CombatPlayer` with the real generated Card in hand. The structured check must prove
the exact states that drive no rule, one rule, and conflicting rules, plus the winner's
priority and the Card's playable/unplayable state. It must not treat a trigger log as a
rendered result.

The headed observation must cover:

- activation and deactivation after the real state mutation;
- highest-priority resolution and the documented later-listed tie if a tie is authored;
- `VisibleWhenUnplayable` show/hide behavior;
- hover, drag, hand entry, and hand exit cleanup;
- unobstructed cost, art, rules text, rarity, selection, and native playable feedback.

If headed observation is delegated to the user, record their exact observation and
keep every unrun automated or Tier 2 check as an exception rather than a pass.
