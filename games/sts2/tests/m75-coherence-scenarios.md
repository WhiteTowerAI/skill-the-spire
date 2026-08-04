# M7.5 theme, narrative, presentation, and coherence scenarios

These repository-owned cases define the behavioral review surface for M7.5. They evaluate
cross-artifact contradictions, proportional coherence, explicit creative tension, and
bounded revision propagation. They do not prove runtime behavior, presentation quality,
translation quality, balance, enjoyment, Tier 1, Tier 2, or human playtest results.

Review behavior semantically rather than matching preferred prose. A response passes when
it preserves the same anchors, conflicts, decisions, affected artifacts, and boundaries;
exact headings and sentences may differ.

## Common rubric

- **Decision authority:** derive anchors from accepted `D-###` decisions; never let SPEC,
  generated files, or easier implementation overwrite DESIGN.
- **Adaptive depth:** review only intentional selected surfaces; keep a narrow exact Card
  compact and treat placeholder art as a fallback rather than invented visual identity.
- **Player-facing linkage:** explain how each applicable mechanic, name, localization,
  visual, Event-text, or Character surface communicates an anchor.
- **Specific conflict:** cite both conflicting artifacts/decisions and the visible
  consequence; do not report generic "theme mismatch."
- **Creative tension:** preserve an accepted ironic or contrasting expression as deliberate
  tension instead of automatically normalizing it.
- **Localization meaning:** preserve terms, rules, costs, numbers, targets, and outcomes;
  do not require literal sentence parity or claim unreviewed translation quality.
- **Scope honesty:** coherence never creates a runtime route, leaks future scope into SPEC,
  or turns flavor/presentation into behavior evidence.
- **Bounded propagation:** revision queues only affected UPDATE/REVIEW/REVERIFY targets plus
  high-risk PRESERVE decisions and reopens only invalidated stages.

## Case 1 - Event localization contradicts its cost and presentation

**Existing artifacts**

- DESIGN says an altar offers a dangerous bargain: lose `20 HP` to gain a relic.
- SPEC implements exactly `20 HP`, nonlethal, then grants the relic.
- English Event text says "Pay 20 HP"; Simplified Chinese says "失去20点最大生命".
- The selected portrait prompt calls the altar "a free welcoming gift with no sacrifice."

**Expected behavior**

1. Load coherence review because Event mechanics, localization, narrative, and visuals are
   all intentional surfaces. Anchor the accepted dangerous-bargain decision.
2. Report two specific conflicts: Simplified Chinese changes HP loss into Max HP loss, and
   the visual prompt promises no cost. Explain that players receive incompatible rule and
   risk signals.
3. Keep DESIGN/SPEC authoritative. Recommend correcting the translation's gameplay meaning
   and aligning the prompt with visible sacrifice. Do not change the mechanic to match the
   downstream mistakes or claim the English wording proves runtime behavior.
4. Stop before authoring while either conflict is unresolved. After correction, record
   localization and visual expressions as aligned and leave `conflicts` empty.
5. Require only semantic localization review and the normal selected visual consumer check
   if an asset is regenerated. Do not demand literal wording across all languages or a full
   end-to-end acceptance.

**Failure signals**

- calls both texts equivalent because each contains `20`;
- silently changes SPEC to Max HP loss;
- rewrites every language into the same sentence structure;
- treats the free-gift prompt as harmless mood; or
- expands the Event into an unsupported layout/VFX route for stronger atmosphere.

## Case 2 - Character contrast requires one explicit creative decision

**Input and draft**

> Build a patient Frost Oracle who studies enemy intent, prepares defense, and releases one
> precise payoff. The draft Card names use calm divination vocabulary, but the proposed
> Character title is "Wildfire Berserker" and the custom-art brief calls for uncontrolled
> flames and reckless charging.

**Expected behavior**

1. Load Character Foundation and coherence review. Derive anchors for patient foresight and
   prepared defense/payoff; do not add a lore bible or load unrelated balance planning.
2. Identify the title/art brief versus mechanic/Card-name conflict specifically. Ask one
   creative resolution: align the title/art, intentionally redefine the Character fantasy,
   or keep the contrast as a deliberate tension with its player-facing purpose.
3. Preserve every settled mechanic, starter-deck decision, and supported boundary while the
   identity decision is open. Do not rename Cards or change the loop merely because art is
   easier to revise.
4. If the user chooses deliberate contrast, record `deliberate-tension` and explain how the
   apparent aggression masks precise preparation. Do not continue reporting it as an
   unresolved conflict.
5. Keep placeholder art as placeholder if no custom visual route was selected; do not
   invent a palette to complete the check.

**Failure signals**

- automatically renames the Character without asking;
- flattens an explicitly accepted contrast back into literal frost imagery;
- changes gameplay to reckless attacks without reopening the design decision;
- asks a long questionnaire about every color, Card, and line of lore; or
- treats Character coherence as proof that the design is fun or balanced.

## Case 3 - Temper rename and palette revision propagates narrowly

**Existing settled design**

- A Glassblower Character builds `Heat`, then Shapes it into attack or defense.
- Normal 3 Energy, the setup/payoff starter pair, and static presentation are accepted.
- Spine animation is `OUT-OF-SCOPE`; voiced lines are `DEFER`.
- Existing localization, Event dialogue, and art prompts use the display term `Heat`.

**Revision request**

> Rename the visible mechanic to Temper and shift the selected custom-art palette from hot
> orange to kiln blue. Keep the rules and everything else unchanged.

**Expected behavior**

1. Use revision and preserve stable design/operation IDs. Record **keep** for rules, normal
   Energy, starter pair, accepted static consumers, rejected Spine, and deferred voice;
   **change** only for display terminology and selected palette.
2. Update the identity anchor from the visible term Heat to Temper without changing the
   source/sink formula or runtime semantics.
3. Produce an ordered queue: UPDATE DESIGN and user-facing SPEC terminology; UPDATE
   localization and art prompts; REVIEW Event text and technical identifiers for actual
   dependency; PRESERVE the mechanic rules, Spine exclusion, and voice deferral; REVERIFY
   only regenerated visible consumers and any changed generated behavior.
4. Do not rename stable localization keys/runtime IDs solely because the display term
   changed. Do not reopen Author/Build for a DESIGN-only future-vision wording change.
5. Update DESIGN first, then affected SPEC/outputs, rerun coherence and design trace, and
   reopen only PLAN stages named by the confirmed queue.

**Failure signals**

- restarts the Character interview or assigns new IDs to unchanged requirements;
- changes Heat gain/spend values while renaming it;
- reintroduces Spine or moves voiced lines into the current slice;
- blindly renames every internal identifier; or
- schedules a full fresh Mod acceptance for prompt/localization-only edits.

## Review record

Record the reviewer, date, cases inspected, and any deviation. Static contract and
validator passes mean only that shipped instructions contain and mechanically preserve the
M7.5 structure. Independent forward-model or human artifact review must be recorded
literally and cannot be inferred from this file.
