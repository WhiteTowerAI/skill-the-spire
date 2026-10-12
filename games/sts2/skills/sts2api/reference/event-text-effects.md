# Normal Event Extra Atmosphere

Every Event page and option already follows the default style of
`reference/vanilla-text-style.md`: option costs `[red]`, gains `[green]`, counts `[blue]`,
glossary terms `[gold]`, and second-person narrative pages. That needs no request.

This page covers only the **extra atmosphere** a user asks for beyond that default, such as a
shaking or glowing phrase. Normal/default-layout Events may use the same bounded rich-text
vocabulary as vanilla Event descriptions. This is host-native presentation: localization supplies balanced
BBCode tags and the existing `MegaRichTextLabel` parses and animates them. Generated mods
do not create a VFX node, Tween, Shader, font, or scene for this feature.

## Supported vocabulary

The pinned vanilla Event localization uses exactly this authored subset:

| Kind | Allowed tags | Use |
|---|---|---|
| emphasis | `b` | short static emphasis |
| color | `aqua`, `blue`, `gold`, `green`, `orange`, `purple`, `red` | semantic or atmospheric color |
| motion | `jitter`, `sine` | short shaking or wave-like spans |

Use tags only in normal Event **page descriptions** and **option descriptions**. Keep the
Event title and option titles plain: titles also identify buttons, metrics/history entries,
and self-test choices.

Every tag must be balanced and nested in reverse closing order. Prefer one short animated
span at a time. These are known-good vanilla shapes:

```text
A [jitter][gold]golden sign[/gold][/jitter] points onward.
The [sine][purple]darkness breathes[/purple][/sine].
[b]CLANG! CLANG!!![/b]
```

Do not emit arbitrary Godot BBCode, tag parameters, custom colors, or user-supplied raw
markup. In particular, `fade_in`, `fly_in`, `thinky_dots`, and `pink` exist in the global
host control but are not part of the vanilla Event-localization subset promoted here.
`ancient_banner` is installed only by the dedicated Ancient name-banner node and is not a
normal Event tag.

## Why no generated code is needed

`NEventLayout` resolves `%EventDescription` as `MegaRichTextLabel` and calls
`SetDescription(formattedText)` whenever Event state changes. `NEventOptionButton` also
renders its combined title/description through `MegaRichTextLabel`. That class enables
BBCode and installs the built-in effect set. A page transition replaces the label text, so
there are no owned children or cleanup hooks to emit.

The animation implementations read the game's text-effects preference directly where the
host supports it. They do not use Fast Mode. Do not add custom timing or preference logic,
and do not promise that every vanilla effect responds identically to the setting.

## Authoring contract

SPEC records only the intended spans, not literal source markup:

```text
extra atmosphere:
  INITIAL: "golden sign" -> jitter + gold
  FOLLOWED: "darkness breathes" -> sine + purple
```

At author time, apply only the allowed tags to the exact phrase in the corresponding page
`.description` or option `.description` entry of `events.json`. Do not translate the tags themselves and
do not duplicate them around a whole paragraph merely because the user requested
"dramatic text."

## Verification

Reuse the Event `MapNode` suite. One headed run is sufficient:

1. enter the real normal Event and resolve `%EventDescription` as a BBCode-enabled
   `MegaRichTextLabel` with every required allowed effect type installed;
2. assert the formatted localization reaches the label with the intended balanced tags;
3. capture a settled page where the short colored/moving spans are visibly distinct;
4. change to a second authored page, assert the same label contains only the new page's
   tags, and capture it;
5. keep the Event's existing structured outcome proof, `selftest done`, and no fresh error
   block. Do not re-run unrelated outcome branches in a separate rich-text project.

## Native-presentation pass

All six ordered native-presentation candidates are now implemented with headed
evidence:

1. **Cross-content bounded rich text:** `reference/content-text-effects.md` owns the
   per-surface Card/relic/potion/power allowlists, SmartFormat/keyword composition, and the
   real Card plus standard Hover Tip proof.
2. **Event option presentation:** `reference/event-option-presentation.md` owns enabled
   typed Hover Tips and normal `CreateModRelicOption<T>` title/description/metadata. Locked tips are
   natively suppressed, and the normal-layout relic image is explicitly deferred because
   its button consumer is Ancient-only.
3. **Native lethal-choice warnings:** that same reference owns exact-cost
   `ThatDoesDamage`/`ThatDecreasesMaxHp`, including safe and inclusive-lethal HP/Max HP
   headed proof.

4. **Native Card/relic acquisition previews:** `reference/event-native-presentation.md`
   owns exact add/obtain ordering, native consumers, duplicate prevention, and cleanup.
5. **Bounded one-shot native screen shake:** that reference owns the single `weak_short`
   profile and preserves the game's player-configured multiplier, including off.
6. **Curated built-in noncombat Event VFX:** that reference owns only `trial_noble`, using
   the vanilla-observed portrait host, exact scene/position, inherited process mode, and
   scene-owned cleanup. The preliminary `VfxContainer` candidate was superseded by the
   actual Trial production contract; this is not arbitrary VFX support.

With items 4-6 complete, direct work resumes Character static presentation, including the
Ancient opening name banner and Ancient dialogue presentation. `RichTextAncientBanner` is
installed by `NAncientNameBanner`, not by the normal Event label, so it remains a dedicated
Character/Architect item.

## Future outlook (not planned)

Positioned speech/thought bubbles remain an unsupported future idea.
`TalkCmd` needs a real `Creature` speaker, while normal portrait Events do not provide one;
keep requests for this as an explicit future gap.
