# Implementation plan: 0.6.0 stabilization

## Status

The RitsuLib migration and external clean-workspace Codex acceptance are closed at the
supported boundary.

- R0-R6: complete with hosted evidence.
- R7: canceled by the human lead; it did not pass.
- R8: complete. Repository cleanup, active-document reset, Codex plugin conversion,
  payload generation, validation, and idempotence checks passed.
- External acceptance: passed in a fresh user-run Codex workspace with a working in-game
  result.

Version `0.6.0` remains an unreleased development baseline. Migration acceptance does not
mean the product is ready for a GitHub release: remaining bugs and content-quality work
take priority.

## R8 Gate

R8 closed with all of the following true:

1. Active source, recipes, scaffold, project files, and manifests have no selectable
   BaseLib implementation path.
2. Historical BaseLib runtime binaries and migration proof directories are removed;
   offline research checkouts remain clearly non-active.
3. README, AGENTS, project status, tests, and skill entry points agree on the RitsuLib-only
   boundary and external acceptance result.
4. `plugins/open-mod` is a valid Codex plugin at `0.6.0` with a repo-local marketplace.
5. `skills/` is regenerated as the portable payload.
6. Both publish modes are idempotent.
7. Unit tests, Python compilation, skill/plugin validation, dependency audit, and
   `git diff --check` pass.

R8 itself did not require another headed STS2 run because the lead replaced R7 with a
separate fresh-user test. That external Codex test subsequently passed. Existing R0-R6
hosted evidence is not rerun without a real regression.

## Current Runtime Architecture

```text
idea -> interview -> semantic SPEC -> grounded recipe -> pinned scaffold
     -> author -> build/package -> Tier 1 -> hosted Tier 2 -> bounded repair
```

The supported framework profile is fixed at RitsuLib `0.4.62` / STS2 `0.107.1`. The
build wrapper validates project, restore, runtime variant, host version, manifest, and
deployed artifacts before verification.

## Verification Ownership

- `CombatPlayer`: content core, stateful cadence, Scry.
- `CombatEnemy`: Monster + Encounter and move vocabulary.
- `MapNode`: Event behavior/presentation and bounded forced follow-up.
- `RunStart` / Character: Foundation, static presentation, resource/UI, ordered buffer.

Use local assertions for deterministic rules. Use one hosted proof per independent
lifecycle or presentation invariant. Fresh acceptance projects are disposable after their
result is recorded.

## Current Work

Triage and fix bugs found through real user testing while executing the lead-approved
M6.5 Character content-quality milestone below. Do not prepare a GitHub release until the
lead explicitly decides that stabilization is sufficient.

The old plan's first recommended RitsuLib expansion slice was promotion of the Scry helper
into the documented Card pipeline; R6 absorbed and completed that work. It is not a
remaining migration gate. Do not automatically start M7, another expansion slice,
multiplayer presentation, audio, or animation/material work outside the bounded M6.5
packages. M6.5's bounded non-Spine `Idle`/`Attack`/`Hit`/`Dead` cues and card-pool frame
material do not authorize broader production animation or custom-material work.

## M6.5 - Character Content Quality

M6.5 is the next approved content-quality milestone. It improves the existing RitsuLib-only
Character pipeline; it does not reopen M6 migration work, revive R7, or imply that any item
below is already supported. Promote each surface only after its own real consumer proof.

M6.5 contains these work packages:

- **CharacterArtBundle and role-based reference routing.** Define one structured bundle
  for every Character art slot, including required/optional status, output path,
  dimensions, alpha policy, fallback, and real consumer. Do not generate a separate
  character sheet or any extra canonical identity image. Use the required selection
  portrait as the identity reference only for identity-sensitive combat, rest, merchant,
  and combat-cue assets, alongside the type-matched STS2 style references. Derive a concise
  palette/motif brief from the user's description and selection portrait for card/UI,
  energy, background, and icon work; those requests do not receive the portrait as an
  image reference. Preserve the existing per-paid-call consent boundary. Add bundle
  validation and a contact-sheet/composite review; do not use a brittle image-similarity
  score as runtime acceptance.

  Keep the checked 132x195 selection and 512x512 combat output dimensions, but add a
  separate visible-subject footprint contract for each real host. Recalibrate selection
  composition/normalization so the portrait is not over-zoomed or clipped in either its
  button or selected panel. Recalibrate the transparent combat cut-out's fill fraction and
  public RitsuLib visual scale/position so it is comparable to a grounded vanilla player
  footprint rather than filling the 512x512 canvas one-to-one. Pin the reviewed content
  box, baseline, and transform only after settled headed comparison; prove the visible
  subject bounds and absence of UI/body clipping or overlap. Do not "fix" either problem
  by changing the contract pixel dimensions.

  The full-energy scene still consumes five 256x256 layers. When the generated-art route
  is selected, make exactly one image-generation call for the Character-specific layer 1;
  user import and the checked fallback remain valid alternatives. Layers 2-5 are copied
  from four reviewed transparent PNG templates supplied by the human lead and committed
  as source assets. Validate the dimensions, alpha policy, exact slot mapping, packed
  paths, and five-layer composite. Do not generate per-Character replacements for
  template layers 2-5, and do not invent placeholder templates before the lead supplies
  the four PNGs.

- **Character-wide card/UI theming.** Add a Character card-pool frame material through
  RitsuLib's supported pool material surface. Turn the palette/motif brief into one
  structured theme contract covering `NameColor`, `EnergyLabelOutlineColor`,
  `DeckEntryCardColor`, `EnergyOutlineColor`, the card-frame base/HSV/material parameters,
  and the large/text energy-icon palette. Prefer deterministic recoloring of one reviewed
  fixed frame and material template; do not spend an image-generation call on a complete
  card frame.
  Split the large pool energy icon from the small text energy icon, grounding each size
  and consumer before implementation. Deterministically derive the top-panel outline and
  every generated Relic's 256x256 `relics/<slug>_outline.png` from the final transparent
  main icon's alpha silhouette with one reviewed width/color rule; make no additional AI
  call. Wire `IconOutlineTexturePath` and RitsuLib `RelicAssetProfile.IconOutlinePath`.
  Reusing the unmodified main icon is only a fallback, not outline-quality acceptance.
  Prove every named color/material consumer, both energy-icon consumers, normal/outlined
  top icons, and the exact normal/outline Relic pair in their real hosts.

- **Bounded non-Spine combat cue sequences.** Add identity-consistent frame assets and
  RitsuLib cue/state-machine wiring for `Idle`, `Attack`, `Hit`, and `Dead`. Define one
  stable visual baseline/pivot and readable bounds plus consumer-grounded intent, center,
  orb, and talk anchors so animation frames cannot move the Character or its UI around.
  Apply the same reviewed public `VisualNodeStyle` scale/position to every cue rather than
  tuning frames independently. Contract each cue's frame order/duration. Verify trigger
  routing, idle looping, one-shot attack/hit behavior, return to idle, death timing and
  terminal behavior, cleanup, stable visible footprint/geometry/anchors, and missing-asset
  fallback in a real combat. This package does not include a `Cast` cue, a Spine pipeline,
  or animated merchant/rest-site assets.

- **Fresh acceptance and payload refresh.** After the focused contract and hosted proofs
  above pass, generate one fresh natural-language Character Mod that exercises the
  complete M6.5 composition. Require the exact load marker, structured
  post-state/presentation proof, `selftest done`, settled screenshots for every visible
  host, and no fresh error block. Record durable evidence, retire the acceptance Mod, and
  regenerate both committed payloads from `games/sts2/`.

M6.5 is complete only when all listed work packages are pipeline-supported on STS2
`0.107.1` and RitsuLib `0.4.62`. A path existing in a profile, a successful PCK build, or a
fallback image appearing does not close a package. RitsuLib Character presentation
patches are non-critical, so each new route needs an exact-resource assertion plus visible
headed evidence in its real host.

M6.5 does not generate, import, resize, pack, wire, or visibly prove a custom map marker.
Keep the checked RitsuLib/game-native shared marker fallback. Because open-mod emits no
custom marker PNG, the 49x64 custom-asset contract creates no normalization, packaging, or
acceptance work.

## Future Character Outlook

Locked-selection presentation, Character-specific card trails (parameterized or custom),
the `Cast` combat cue, and any additional combat cue states are not part of M6.5. Spine
authoring, custom transition materials/shaders, production audio, multiplayer hands/remote
UI, native custom-Character Ancient presentation, animated merchant/rest-site production
assets, and release work also remain outside the milestone. These are future
possibilities, not scheduled follow-up packages; none starts without a later explicit lead
instruction. A custom map marker is not a future package; the product keeps the native
shared marker.
