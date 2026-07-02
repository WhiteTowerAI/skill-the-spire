# Interview — one short intake round

Goal: turn the user's one sentence into enough certainty to write `SPEC.md`,
**asking as little as possible**. The user is a non-programmer; keep it plain.

## Rules

- **One round only.** Ask only what's genuinely ambiguous. Everything else gets a
  sensible default (state the default, don't ask).
- **No jargon.** Say "when does it happen?" not "which combat hook?". Never ask
  about classes, namespaces, or APIs.
- **Batch the questions.** Ask all needed clarifications together, not one by one.

## What to resolve (only if unclear from the sentence)

1. **Element type.** Relic / card / potion? Infer if possible:
   - Owns a passive/triggered effect the player *has* → **relic**.
   - Something the player *plays* from hand with an energy cost → card.
   - A one-shot consumable → potion.
   - **M2 only supports relics.** If it's clearly a card/potion, say that's coming
     in a later milestone and offer to model the closest relic, or stop.
2. **Trigger** (for a relic): when does the effect happen? Map the user's words to
   a lifecycle moment — "start of combat", "start of each turn", "when you play a
   card", "start of each floor". If they said it, don't re-ask.
3. **Effect**: what exactly happens, in game terms (energy, damage, block, draw,
   a power/status). Get numbers if they matter ("double", "gain 2", "lose all").

## Defaults (apply silently unless the user specified otherwise)

- **Rarity**: Common.
- **Pool**: SharedRelicPool (drops for any character).
- **Name**: derive a short, flavorful name from the concept; confirm in the SPEC summary.
- **Art**: placeholder (the template's fallback icon). Custom art is M4.
- **Author**: reuse the project's configured author, else "OpenMod".

## Output

A compact intake you carry into `spec.md`:

```
element: relic
name: <proposed>
rarity: Common
trigger: start of combat (turn 1)
effect: <plain-language, with numbers>
art: placeholder
```

Do not write files here — `spec.md` does that. If nothing was ambiguous, skip
straight to `spec.md` with the inferred intake.
