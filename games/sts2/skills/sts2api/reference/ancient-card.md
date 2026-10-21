# Reference: Ancient Card

Read this beside `recipes/card.md` only when a SPEC Card has rarity `Ancient`. Everything in the
Card recipe still applies (class, text, numbers, proof); this page adds how an Ancient Card is
reached, where it is registered, how it looks, and what the game does with it natively.

## What it is

An Ancient Card (`CardRarity.Ancient`, "Ancient Card" / `先古卡`) is a Card the player gets from
an Ancient's gift, never from a normal reward. Vanilla has 18: eight in `EventCardPool`, each
added by an Ancient Relic on pickup (Neow's Torment adds Neow's Fury), and two per Character in
that Character's pool, one from Archaic Tooth's transcendence and one from Dusty Tome.

Vanilla code treats the rarity specially, with no Mod code involved:

- combat rewards and the Shop never offer it, and in-combat generation (Discovery, Attack
  Potion, Call of the Void, and similar) never creates it;
- transforming one yields a Colorless Common, Uncommon, or Rare Card;
- the Card Library lists it under its own Ancients filter;
- `NCard` draws it with the full-card layout: the portrait fills the card behind an Ancient
  border, title banner, and a text background chosen by Card type.

## SPEC fields

Add to the Card's SPEC envelope:

```markdown
  - rarity: Ancient
  - acquisition: relic pickup <Relic> | Dusty Tome <Character> | Archaic Tooth <starter Card>
                 | new Ancient option <Ancient, option> | existing Ancient option <Ancient, option>
                 | Event <Event, option>
  - pool: EventCardPool | <Character>CardPool
```

`acquisition` is required. A normal run never offers an Ancient Card, so one with no
acquisition cannot be obtained; stop at intake and ask how the player gets it. A request that
only wants the look ("make it look like an Ancient card") is not this route; see § Limits.

## Pick the route

| acquisition | pool | implement with |
|---|---|---|
| relic pickup | `EventCardPool` (vanilla home), or the Character's pool | § Relic pickup below; the Relic itself follows `recipes/relic.md` |
| Dusty Tome | the Character's pool | `recipes/character.md` § Registration, `.DustyTomeCard<,>()` |
| Archaic Tooth | the Character's pool | `recipes/character.md` § Registration, `.ArchaicToothTranscendence<,>()` |
| new Ancient option | `EventCardPool` | `recipes/ancient.md`: `CreateModRelicOption<T>()` with a relic-pickup Relic, or an option callback that adds the Card |
| existing Ancient option | `EventCardPool` | `reference/vanilla-ancient-overrides.md`: an `add_card` or `obtain_relic` effect whose model has `"source": "mod"` |
| Event | `EventCardPool` | `recipes/event.md` acquisitions |

A Dusty Tome Card and an Archaic Tooth Card are different Cards: Dusty Tome never picks a
transcendence Card.

## Class and registration

Use the Card recipe's shell with `CardRarity.Ancient` in the constructor and register it in the
pool above:

```csharp
public StarfallEdict() : base(2, CardType.Attack, CardRarity.Ancient, TargetType.AnyEnemy) { }
```

```csharp
    .Card<EventCardPool, Cards.StarfallEdict>()
```

Leave `CardAssetProfile.VisualStyle` at its default: the rarity alone selects the Ancient
layout, and the vanilla border, banner, and text background need no paths. Set only
`PortraitPath`. Do not use `ContentAssetProfiles.AncientCard(...)`; it points the portrait at a
base-game path that a Mod does not ship.

## Relic pickup

The Neow's Torment shape: an Ancient Relic in `EventRelicPool` whose pickup adds one Card and
shows the native preview. Relic rewards draw only from the shared and Character pools, never
`EventRelicPool`, so something must offer the Relic (an Ancient option, an Event, or a test
grant).

```csharp
public sealed class Astrolabe : ModRelicTemplate
{
    public override RelicRarity Rarity => RelicRarity.Ancient;

    public override bool HasUponPickupEffect => true;

    protected override IEnumerable<IHoverTip> AdditionalHoverTips =>
        HoverTipFactory.FromCardWithCardHoverTips<StarfallEdict>();

    public override async Task AfterObtained()
    {
        CardModel card = Owner.RunState.CreateCard<StarfallEdict>(Owner);
        CardCmd.PreviewCardPileAdd(await CardPileCmd.Add(card, PileType.Deck), 2f);
    }
}
```

```csharp
    .Relic<EventRelicPool, Relics.Astrolabe>()
```

Relic text follows Neow's Torment: `"Upon pickup, add [blue]1[/blue] [gold]Starfall
Edict[/gold] to your [gold]Deck[/gold]."` / `"拾起时，将[blue]1[/blue]张[gold]星陨敕令[/gold]加入你的[gold]牌组[/gold]。"`

## Art

An Ancient Card's portrait is the whole card: import it with `--spec card_ancient` (606×852)
and write it with § The Ancient card portrait prompt template in `reference/art-contract.md`.
Without art, the checked 1000×760 placeholder is center-cropped into the full-card layout;
that is the accepted fallback.

## Proof

- The Card itself: a face check or scenario exactly as `recipes/card.md` selects.
- The acquisition: drive the real source and assert the Deck gained exactly one Card of the
  type, with `Rarity == CardRarity.Ancient` and the SPEC pool. For relic pickup,
  `await t.ObtainRelic<TRelic>()` in a `plan.RunStart` scenario; for Dusty Tome and Archaic
  Tooth, the Character recipe's proof; for an Ancient option, the Ancient's driver body.
- Headed review: the Ancient layout and art in the hand, the Deck view, the Card Library's
  Ancients filter, and the upgrade preview, in both languages.

## Limits

- `CardVisualStyle.Ancient` can give a non-Ancient Card the Ancient layout, and
  `CardVisualStyle.Standard` can give an Ancient Card the normal one. Both are
  framework-expressible but not authored by this pack.
- Dusty Tome and Archaic Tooth mappings exist only for Characters a Mod registers them for; a
  vanilla Character keeps its own Ancient Cards.
