# Surface: orb

Everything the pipeline needs for one custom Orb, in one place: the SPEC envelope it must
declare, the element class the author writes, and the proof its verification owes. Read this
page at the `spec.md`, `author.md`, and `verify.md` stages when SPEC declares an orb.

An orb has three separate behaviors and no trigger of its own — every one of them runs
through a host Card, relic, or Power. That is why it gets a full envelope while keyword and
enchantment do not: an orb is real content with its own identity and its own slot lifecycle,
merely without a self-contained trigger. Envelope added 2026-08-07 by human-lead decision.

## SPEC envelope

```markdown
- **element**: orb
- **logical id**: <stable local stem>
- **mod id**: <stable mod identity>
- **channel host**: <the Card/relic/Power that channels it, and when>
- **passive**: <what it does per turn, with numbers>
- **evoke**: <what it does when evoked, with numbers>
- **passive value**: <declared scaling name and value>
- **evoke value**: <declared scaling name and value>
- **slots**: <how the design expects slot capacity to be obtained and its bounds>
- **eviction**: engine default (oldest evoked first when channeling into full slots) |
  <the declared design if it intentionally differs>
- **display**:
  - title: <shown name>
  - description: <plain fallback text; read when no smartDescription resolves>
  - smartDescription: <text using {Passive} and {Evoke}; required for live values>
  - text spans: <phrase -> semantic color intent>
- **art**: placeholder | generate (one 100x100 icon; the persistent combat body stays the
  checked Frost Spine fallback)
- **art source**: runtime-imagegen | vofy | byo-http | local-image  (generate only)
- **proof**:
  - scenario: CombatPlayer
  - driver: channel through the real host, advance a turn, then evoke
  - invariants: <exact expected/observed state for channel, passive, and evoke>
  - boundary cases: <full-slot eviction, empty-queue evoke, or none>
- **derived ids** (adapter resolves after the semantic SPEC is accepted):
  - logical id: `<stable local stem>`
  - localization fields: `title`, `description`, `smartDescription`
  - asset role: orb icon
```

## `smartDescription` is what makes the numbers live

`OrbModel` substitutes `{Passive}`, `{Evoke}`, and `{energyPrefix}` only when a
`.smartDescription` key exists. Without it the engine falls back to a dumb tip that shows
`.description` verbatim, with no substitution — so any value modified at runtime, Focus
included, becomes invisible to the player while the tooltip keeps stating the base number.

Ship all three keys in `localization/eng/orbs.json`, and put the placeholders in
`smartDescription`:

```json
{
  "<MOD>_ORB_<TYPE>.title": "Display Name",
  "<MOD>_ORB_<TYPE>.description": "Passive and Evoke rules.",
  "<MOD>_ORB_<TYPE>.smartDescription": "[gold]Passive:[/gold] {Passive}.\n[gold]Evoke:[/gold] {Evoke}."
}
```

The `Passive:` and `Evoke:` labels are author-written, not engine-composed — that is why they
appear literally above. Only the `{Passive}`/`{Evoke}` values are substituted.

## Author the element class

**Custom orb** - add `<ModName>Code/Orbs/<OrbName>.cs` from `recipes/orb.md` and extend
`ModOrbTemplate`:

- Add exactly one `.Orb<TOrb>()` step to `MainFile.Content.cs`. Implement channel,
  passive, and evoke as separate behavior contracts through a real Card/relic/power host.
- Ship `orbs.json` with `.title`, `.description`, and `.smartDescription`; the third is what
  makes `{Passive}`/`{Evoke}` render live.
- Generated art is one 100x100 icon shared by the smart tooltip and trigger flash. Use the
  checked `OrbAssetProfile` Frost fallback when it is absent.
- Override the protected `ChannelSfx` with the verified Frost event. The icon is not the
  persistent combat body; `ContentAssetProfiles.Orb("frost_orb")` retains the Frost Spine
  scene until custom animation is separately proven.

## Self-test driver body

**orb** → `InCombat`, driven entirely through the real host: channel via the host, advance a
turn so the passive fires on its own, then evoke.

`OrbCmd.Channel<T>`, `OrbCmd.Passive`, and `OrbCmd.EvokeNext` are the host commands. Note
that calling `OrbCmd.Passive` directly is a *diagnostic*, not the passive proof — see below.

## Proof matrix

- Assert queue capacity and presence after channel, including the title resolving to the
  shipped localization.
- Assert the passive post-state and the evoke post-state with exact expected/observed values,
  and assert removal from the queue after evoke.
- **Prove all three behaviors, not one.** Channel, passive, and evoke are independent
  contracts; an orb that channels and evokes correctly but whose passive never fires is a
  different design from the declared one.
- **Fire the passive through the real per-turn path.** The engine triggers passives from the
  turn-end queue walk, which consults a public trigger-count hook. Calling `OrbCmd.Passive`
  directly bypasses that hook, so a passive that the game would never trigger — or would
  trigger the wrong number of times — still passes. Advance a real turn instead, and assert
  the resulting state.
- Assert the declared slot bounds, and the full-slot case: channeling into full slots evokes
  the oldest orb first. If SPEC declares `engine default`, assert that observed order rather
  than assuming it.
- Assert `{Passive}`/`{Evoke}` resolve in the real smart tooltip. A dumb-tip fallback shows
  plausible text, so a missing `smartDescription` is invisible to every state assertion.
  Visible icon support additionally needs the real smart tooltip and trigger flash in a headed
  run; the persistent body stays labeled as the Frost fallback until a compatible custom Spine
  scene is separately proven.

## Manual fallback (only when the harness cannot reach its scenario)

There is no dev-console command that grants an orb. Grant its **channel host** by that host's
own route in `verify.md` § Manual fallback, then play or trigger the host to channel, end a
turn for the passive, and evoke. An orb reached any other way is not evidence that its
declared host channels it.
