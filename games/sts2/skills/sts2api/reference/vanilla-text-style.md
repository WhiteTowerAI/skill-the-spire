# Vanilla Text Style

Every player-facing string a generated Mod ships must read like the
game: the same names for shared terms, the same highlight colors, the same number
presentation, the same line breaks, and native Simplified Chinese. This is the **default**
for every surface, not an optional effect, and it needs no user request. A player notices a
white "Vulnerable", a run-on Card description, or a Chinese term the game never uses at
once.

This page owns the house style. `reference/content-text-effects.md` and
`reference/event-text-effects.md` own only the *extra*, user-requested emphasis beyond it.
Build runs `text_style.py`: broken markup fails the Build, and style drift is listed in
`.text-style.log` for the author to fix.

## Vocabulary: look terms up, never invent them

`reference/catalogs/text-glossary-sts2-0.107.1.json` is extracted from the game's own
`eng`/`zhs` localization. Each row gives:

| Field | Meaning |
|---|---|
| `eng`, `zhs` | The exact vanilla name in each language. Use it verbatim: Block/格挡, Vulnerable/易伤, Draw Pile/抽牌堆, Exhaust/消耗, Upgrade/升级, Deck/牌组, Hand/手牌. |
| `color` | The highlight vanilla uses for it: `gold` for game terms, `purple` for Enchantment names, `red` for Curses. |
| `eng_colored` / `eng_plain`, `zhs_colored` / `zhs_plain` | How often vanilla highlights the term in rules text. Highlight a term that vanilla highlights consistently (Block 229/0); leave plain a term vanilla usually leaves plain (Attack 2/64, Max HP 3/49). |
| `zhs_measure` | The Chinese measure word vanilla puts before the term: 点 for Block/Strength/Dexterity/Focus/Energy, 层 for Vulnerable/Weak/Poison/Doom and other stacking debuffs, 个 for Orbs. |
| `kinds` | Where the term comes from: `keyword`, `power`, `orb`, `enchantment`, `affliction`, `hover_tip`, or `observed` in rules text. |

Search the glossary before writing any game term in either language. Never translate a
vanilla term yourself, and do not reuse a vanilla name for a different Mod concept by default:
players read it as the vanilla mechanic.

A **deliberate name collision** is the exception. When the user keeps such a name on purpose
(for example 闪电 for a Mod effect that is not the Lightning Orb, because their theme calls it
that), keep it, record it once in `DESIGN.md` § Decisions with the reason, and write it
**plain** wherever it means the Mod concept: a highlight promises the vanilla term and its
tooltip. A Mod-owned Keyword, Power, Orb, Enchantment, or Affliction with that title follows the
next paragraph instead, since it has its own tooltip. Build keeps listing `term ... is not
highlighted` for the plain uses; once the collision is recorded, those warnings are expected
and need no fix.

The Mod's own titled content is vocabulary too. A custom Keyword, Power, Orb, Enchantment, or
Affliction keeps one exact name per language everywhere, and every *other* string that names
it highlights it like vanilla does (`[gold]`, or `[purple]` for an Enchantment). An entry may
leave its own name plain in its own description.

## Universal rules

1. **Highlight terms, not sentences.** Wrap only the term itself:
   `Apply {VulnerablePower:diff()} [gold]Vulnerable[/gold].` Highlight keywords, Powers,
   Orbs, piles (Hand, Draw Pile, Discard Pile, Exhaust Pile, Deck), Block, Gold, Stars, the
   card actions Exhaust, Transform, Upgrade, Enchant, Channel, Evoke, Forge, Summon, Remove,
   and the names of specific Cards, Relics, or Potions the text creates or names
   (`[gold]{Cards:plural:Shiv|Shivs}[/gold]`). Leave generic words plain: card types
   (Attack, Skill, Power), damage, HP, Max HP, card(s), enemy, turn.
2. **Numbers follow the surface** (table below). A Card number is a `{Name:diff()}` token
   with no color: `:diff()` already turns it green or red when the value changes. Every other
   surface wraps a displayed number in `[blue]`, healing and Max HP gains in `[green]`, and
   Event costs in `[red]`.
3. **Use the native formatters.** Energy renders as icons through `energyIcons()` and Stars
   through `starIcons()` (for example `{Energy:energyIcons()}`), never the words "1 Energy"
   on a Card. English counts use `{Cards:plural:card|cards}`. Upgrade-only text uses the
   formatter in `reference/mechanics.md` §2.
4. **One Card effect per line.** Separate independent Card effects with `\n`, one sentence
   per line. A condition and its result stay in one sentence. Other surfaces write one short
   paragraph, without line breaks.
5. **End sentences.** English rules text ends each sentence with `.`; Chinese with `。`.
   Selection prompts are one short sentence.
6. **Titles and names are plain.** Content titles, Event and option titles, Monster names,
   move names, Encounter and Act titles, and Character names carry no markup. English titles
   use Title Case.
7. **Never duplicate composed text.** The game composes Card keyword lines (`Exhaust.`,
   `Ethereal.`), the upgraded title `+`, Energy cost, and Card type. Do not write them into
   a description.
8. **Only vanilla tags.** Tags must be balanced and nested in reverse closing order, and must
   come from the surface's set below. Never use `[color=...]`, tag parameters, or raw markup
   supplied by the user.

## Per-surface style

| Surface (table and key) | Numbers | Highlight | Lines | Shape |
|---|---|---|---|---|
| Card `cards.<ID>.description` | `{Damage:diff()}`, uncolored | `gold` terms; `purple` Enchantment names | `\n` between effects | `Deal {Damage:diff()} damage.\nApply {VulnerablePower:diff()} [gold]Vulnerable[/gold].` |
| Card `.selectionScreenPrompt` | `{Amount}` plain | `gold` piles only | one sentence | `Choose {Amount} {Amount:plural:card|cards} to put into your [gold]Hand[/gold].` |
| Relic `.description` | `[blue]{Block}[/blue]`, literal `[blue]3[/blue]`; heal `[green]{Heal}[/green]` | `gold` terms; `red` Curses; `purple` Enchantments | one paragraph | `At the start of each combat, gain [blue]{Block}[/blue] [gold]Block[/gold].` |
| Relic `.flavor` | none | plain prose | one or two sentences | `It still smells of the sea.` |
| Potion `.description` | `[blue]{Damage}[/blue]`; heal `[green]` | `gold` terms | one paragraph | `Apply [blue]{WeakPower}[/blue] [gold]Weak[/gold].` |
| Power `.smartDescription` | `[blue]{Amount}[/blue]` | `gold` terms | one paragraph | `At the start of your turn, gain [blue]{Amount}[/blue] [gold]Strength[/gold].` |
| Power `.description` | no `{Amount}`; literals `[blue]` | `gold` terms | one paragraph | the general rule, for when no stack count is known |
| Orb `.smartDescription` | `[blue]{Passive}[/blue]`, `[blue]{Evoke}[/blue]` | `gold` terms | `[gold]Passive:[/gold] …\n[gold]Evoke:[/gold] …` | see `recipes/orb.md` |
| Enchantment `.description` | `[blue]{Amount}[/blue]` | `gold` terms | one paragraph | `Increases [gold]Block[/gold] gained from this card by [blue]{Amount}[/blue].` |
| Affliction `.description` | `[blue]{Amount}[/blue]`, Energy icons | `gold` terms | one paragraph | `Take [blue]{Amount}[/blue] damage when this card is played.` |
| Modifier `.description` | `[blue]` | `gold` terms; `red` for a harsh downside | one paragraph | `Choose [blue]10[/blue] of [blue]30[/blue] cards to replace your starting [gold]Deck[/gold].` |
| Keyword `card_keywords.<ID>.description` | none | `gold` other terms | one or two sentences | `If this card is discarded from your [gold]Hand[/gold] before the end of your turn, play it for free.` |
| Hover tip `static_hover_tips.<ID>.description` | `[blue]` | `gold` terms | short | the shared rule |
| Event option `.description` | costs `[red]{HpLoss}[/red]`; heals and gains `[green]{Heal}[/green]`; counts `[blue]` | `gold` terms, obtained Relic and Card names; `red` fights and Curses | one line | `Lose [red]{HpLoss}[/red] HP. [gold]Upgrade[/gold] a random card.` |
| Event page `.description` | `[blue]` | narrative; atmospheric spans only per `event-text-effects.md` | paragraphs separated by `\n\n` | second-person present tense |
| Event, option, Encounter, Act titles | none | plain | one line | `Grab the Sword` |
| Encounter `.loss` | none | `[gold]{encounter}[/gold]` | one sentence | `{character} was chomped to death by [gold]{encounter}[/gold].` |
| Monster `.name`, `.moves.<MOVE>.title` | none | plain | one line | `Eye Lasers` |
| Character `.description` | none | plain | two short sentences joined by `\n` | identity line `\n` fighting-style line |
| Ancient dialogue `ancients.json` talk lines | none | spoken voice; see `reference/ancient-dialogue.md` | `\n` for a pause | |
| Rest Site option `.description` | `[blue]` counts; `[green]` heal/Max HP gain | `gold` terms | one sentence | `[gold]Upgrade[/gold] a card in your [gold]Deck[/gold].` |
| Rest Site option disabled text | none | whole sentence `[red]…[/red]` | one sentence | `[red]You need at least 2 removable cards in your Deck.[/red]` |
| Reward, Card Pile, Runtime UI text | `[blue]` | `gold` terms | short UI sentences | follow the nearest row above |

Allowed tags per table come from vanilla: Card `gold`/`purple`/`blue`; Relic
`blue`/`gold`/`green`/`purple`/`red`; Potion `blue`/`gold`/`green`; Power, Orb,
Enchantment, Affliction `blue`/`gold`; Modifier `blue`/`gold`/`red`; Rest Site and Hover Tip
`blue`/`gold`/`green`/`red`; Event descriptions the full set in `event-text-effects.md`.

## Simplified Chinese

- **Terms**: the glossary `zhs` name, verbatim.
- **Punctuation**: full-width `，。：；！？（）“”`, ellipsis `……`. No half-width `,.:;!?`
  next to Chinese characters.
- **No spaces** between Chinese characters, numbers, tags, and placeholders:
  `获得[blue]{Block}[/blue]点[gold]格挡[/gold]。`, never `获得 [blue]{Block}[/blue] 点格挡`.
- **Measure words**: number, then measure word, then term. 点 for damage, Block, HP, and the
  glossary's 点 terms; 层 for the glossary's 层 terms; 张 for cards; 个 for Orbs; 回合 for
  turns; none before 金币. The glossary `zhs_measure` field gives the vanilla word.
- **Plurals**: Chinese has none. Drop English `{X:plural:…}` branches and write the variable
  once (`抽{Cards:diff()}张牌。`). The Build contract requires only that both languages
  reference the same variables and the same `:diff()`/`energyIcons()`/`starIcons()` values;
  grammar formatters (`plural`, `cond`, `show`, `choose`) may differ per language.
- **Vanilla sentence shapes** to reuse:

| English | Chinese |
|---|---|
| `Deal {Damage:diff()} damage.` | `造成{Damage:diff()}点伤害。` |
| `Gain {Block:diff()} [gold]Block[/gold].` | `获得{Block:diff()}点[gold]格挡[/gold]。` |
| `Apply {VulnerablePower:diff()} [gold]Vulnerable[/gold].` | `给予{VulnerablePower:diff()}层[gold]易伤[/gold]。` |
| `Draw {Cards:diff()} {Cards:plural:card|cards}.` | `抽{Cards:diff()}张牌。` |
| `Lose {HpLoss:diff()} HP.` | `失去{HpLoss:diff()}点生命。` |
| `Gain {Energy:energyIcons()}.` | `获得{Energy:energyIcons()}。` |
| `At the start of your turn, …` | `在你的回合开始时，……` |
| `At the start of each combat, …` | `每场战斗开始时，……` |
| `Heal [green]{Heal}[/green] HP.` | `回复[green]{Heal}[/green]点生命。` |
| `Add … into your [gold]Hand[/gold].` | `将……加入你的[gold]手牌[/gold]。` |

## Hover tips for named terms

A description that names a term the player may not know also shows its tooltip, as vanilla
does. The Card `Bash` declares `HoverTipFactory.FromPower<VulnerablePower>()`; `True Grit`
declares `HoverTipFactory.FromKeyword(CardKeyword.Exhaust)`; `Blade Dance` declares
`HoverTipFactory.FromCard<Shiv>()`. Every RitsuLib content template exposes the same seam:

```csharp
using MegaCrit.Sts2.Core.HoverTips;
using STS2RitsuLib.Keywords;

protected override IEnumerable<IHoverTip> AdditionalHoverTips =>
[
    HoverTipFactory.FromPower<VulnerablePower>(),      // a vanilla or Mod Power the text applies
    HoverTipFactory.FromKeyword(CardKeyword.Exhaust),  // a native keyword the text names
    HoverTipFactory.FromCard<Shiv>(),                  // a specific Card the text creates
    HoverTipFactory.FromOrb<FrostOrb>(),               // an Orb the text channels
    .. new[] { OtherCard.KeywordId }.ToHoverTips(),    // a Mod keyword the text names
    .. HoverTipFactory.FromEnchantment<MyEnchantment>(), // sequence-returning factories spread
];
```

`ModCardTemplate`, `ModRelicTemplate`, `ModPotionTemplate`, `ModPowerTemplate`,
`ModOrbTemplate`, and `ModAfflictionTemplate` all expose `AdditionalHoverTips` (pinned
`HoverTipFactory`: `FromPower<T>(int? amount = null)`, `FromKeyword`, `FromCard<T>`,
`FromOrb<T>`, `FromPotion<T>`, and the sequence-returning `FromRelic<T>`,
`FromEnchantment<T>`, `FromAffliction<T>`). A Card's *own* keywords already get their tips;
add a tip only for a term the text names. Relic and Potion keyword tips may also use the
template's `RegisteredKeywordIds`. Record each tip in SPEC `presentation.hover tips`.

## Self-check before Build

- Every game term matches the glossary in both languages, with the glossary color.
- Card numbers are uncolored `:diff()` tokens; every other displayed number is colored.
- Card effects sit on separate lines; titles are plain; no composed text is duplicated.
- Chinese uses full-width punctuation, no spaces, and the vanilla measure word.
- Every named Power, keyword, or created Card has its hover tip.

Build lists each remaining deviation in `.text-style.log`. Fix it, or record in `MEMORY.md`
why the vanilla shape does not apply to that string. A deliberate name collision recorded in
DESIGN (§ Vocabulary) already counts as recorded.

## Verification

Static style is a Build fact. Seeing it render is a headed fact: when SPEC selects headed
review for a Card or tooltip, look at the real Card body and Hover Tip and confirm the gold
terms, colored numbers, line breaks, and tooltip list match a comparable vanilla Card.
