# Art route setup

Read this page only after the user picks art choice 1, 2, or 3 in the interview's art
question (`${MODMAKER_SKILL_DIR}/interview.md`). Choice 0, or no answer, records
`art: placeholder` and needs nothing here. Set up only the chosen route; never probe the
others.

## Record the route

- **1. Your agent's own image tool:** record `art source: host-tool`.
- **2. Your own image service:** ask which service, then set it up per
  `reference/art-backends.md`: a built-in name needs only a key variable in the user's own
  environment, and any other endpoint or local command is a named entry in the user's
  config file; offer to write that entry with `api_key_env` instead of the key. Never ask
  the user to paste a key into the conversation. Then run
  `python ${GAME_TOOLS_DIR}/gen_sprite.py check --backend <name>` once (it requests no
  image). On success record `art source: backend:<name>`; on failure say what is missing
  and let the user fix it, pick another choice, or keep placeholder.
- **3. Images you already have:** ask which file belongs to which asset; record
  `art source: local-image`. When the art sits inside a larger picture (a whole card with
  frame and text), crop it with `gen_sprite.py grid` and `import --crop` per
  `reference/art-contract.md` § Using the tool; anything beyond a rectangular crop is the
  user's own edit.

## Style note and cost (choices 1 and 2)

Capture one overall subject/style note. `${MODMAKER_SKILL_DIR}/author.md` derives each
asset's subject from its SPEC. Before any paid route, show how many image calls it will
spend.

## Character art tier (choices 1 and 2)

For a Character, offer its art tier in the same message as the style note, with the call
counts from `character_art_tiers` in `reference/catalogs/art-contract-sts2-0.107.1.json`:

- **minimal**: selection portrait plus the combat, rest, and merchant bodies; everything
  else keeps the base-game Ironclad art;
- **standard**: all static Character art, no combat animation; or
- **full**: standard plus combat animation: idle breathing, attack, hit, and death.

No answer means minimal. Record `character art tier: <name>`. The locked selection
portrait and map marker are in no tier; generate them only when the user names them.

Whenever the user picks **full** or otherwise asks for the Character to move in combat,
tell them plainly before recording it: the animation is drawn as one large image that must
come back at 2048x2048, and a 1024x1024 result was rejected as too blurry. Name whether
their route can do it, from the list in `reference/character-combat-cues.md`
§ Acquisition and normalization (Codex's built-in `image_gen` can; the built-in `openai`,
`gemini`, and `openrouter` defaults cannot without a newer model and a config change).
When it cannot, offer **standard** or a route switch, and record what the user chooses. No
other Character art needs 2K: the selection background asks for 2K when the route supports
it but works from a smaller image.
