# Image backend config

Read this page only when the user selected a `backend:<name>` art route in the interview.

No backend runs unless the user chose it in the interview. Three built-in names need only
a key the user sets in their own environment, never in the conversation:

| `--backend` | key variable | transport | default model |
|---|---|---|---|
| `openai` | `OPENAI_API_KEY` | `images` at `https://api.openai.com/v1` | `gpt-image-1.5` |
| `gemini` | `GEMINI_API_KEY` | `gemini` at the Gemini API | `gemini-2.5-flash-image` |
| `openrouter` | `OPENROUTER_API_KEY` | `chat` at `https://openrouter.ai/api/v1` | `google/gemini-2.5-flash-image` |

`--model` overrides the model for one call; offer it when the user names a newer model their
account has. A variable the user sets after the agent session started is not visible to it;
the user restarts the session or writes a config entry instead.

Anything else is a named entry in `~/.skill-the-spire/art-backends.json` (or a file named
by `--config` / `$GEN_SPRITE_CONFIG`). The user owns that file. It lives outside every Mod
project and is **never committed — it may hold a key**. Prefer `api_key_env` (the name of a
variable holding the key) over `api_key`, so the file itself holds no secret. An entry
named like a built-in overrides it, and a file with one backend needs no `--backend`:

```json
{ "backends": {
    "my-gateway": { "mode": "images", "base_url": "https://api.example.com/v1",
                    "api_key_env": "MY_GATEWAY_KEY", "model": "<model id>" },
    "local":      { "mode": "command",
                    "command": ["my-image-cli", "--prompt", "{prompt}",
                                "--ratio", "{aspect_ratio}", "--out", "{out_dir}"],
                    "reference_args": ["--image", "{image}"] } } }
```

Before the first paid call, run `gen_sprite.py check --backend <name>` once. It checks the
config shape, that the key is present, and a command backend's executable and `preflight`.
It requests no image, so it costs nothing and does not prove the model will accept the
prompt.

- `images` — the OpenAI *Images* API: `/images/generations`, or multipart `/images/edits`
  with references. OpenAI's gpt-image models and any platform exposing that endpoint.
  The request size follows the spec's orientation (1024x1024, 1536x1024, or 1024x1536).
  Optional: `edit_url`, `request_size`, `timeout`, and `exact_size: true` for a model that
  takes custom sizes (`gpt-image-2`); it then asks for the contract size itself when that
  is larger than 1536 px, such as the 2048x2048 cue sheet.
- `chat` — the OpenAI *Chat Completions* API returning an image in the reply. Poe,
  OpenRouter, and most "one key, many models" gateways. References are inlined as
  `image_url` data URLs, and the tool parses the image back out of the reply (structured
  image array, inline base64 data URL, or an image link — in that order). Optional:
  `chat_url`, `chat_extra` (merged into the request body, e.g. OpenRouter's
  `modalities`), `timeout`. This transport sends no size; the prompt states the
  orientation.
- `gemini` — the Gemini API's native `generateContent` with image output. References are
  inline image parts, and `imageConfig.aspectRatio` is the closest of `aspect_ratios`.
  Optional: `base_url`, `aspect_ratios`, `timeout`, and `image_size: true` for a model
  that accepts `imageConfig.imageSize` (Gemini 3 image models); it then asks for `2K` on
  event, Character background, and cue sheet specs and `1K` otherwise.
- `command` — the user's own CLI, script, or local workflow (for example ComfyUI). The tool
  runs `command` with stdin closed and its output hidden, into a fresh empty `{out_dir}`,
  and requires exactly one image there. Tokens: `{prompt}` (folded to one line for Windows
  `.cmd` shims), `{out_dir}`, `{model}`, `{request_size}`, `{aspect_ratio}` (the
  closest of `aspect_ratios`, default `1:1 2:3 3:2 3:4 4:3 9:16 16:9 21:9`), and
  `{resolution}` (`2K` when the contract's long edge exceeds 1600 px, such as an event
  portrait, else `1K`). Each reference
  appends `reference_args` with `{image}`; without `reference_args`, references are
  skipped. Optional: `model`, `preflight` (commands that must exit 0 first, such as an
  auth check), `timeout` (default 600 seconds).

A missing key, missing or invalid config, or unknown backend name makes `generate` and
`check` fail with a clear message and a non-zero exit, and the caller falls back to the
placeholder.
