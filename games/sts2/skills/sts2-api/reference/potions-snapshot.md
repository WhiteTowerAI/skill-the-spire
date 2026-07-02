# Potions — content snapshot (from spire-codex)

> **Distilled content facts, not a data dump.** A short reference so `recipes/potion.md`
> can pick a realistic effect + a vanilla analog without a live query every time.
> Source: **spire-codex** (`https://spire-codex.com/api/potions?lang=eng`), the
> reverse-engineered STS2 database. Game data © Mega Crit Games; spire-codex code is
> PolyForm Noncommercial. This captures names/rarity/pool/effect only — for full
> fields (image URLs, raw loc, dynamic vars) query the API per `grounding.md`.
> Snapshot taken 2026-07-02 against STS2 v0.107.x; 63 potions total.

## Enum values (confirmed against the decompile, for the recipe)

These are the C# enums a `PotionModel` overrides — the decompile is authoritative;
the spire-codex "rarity" strings below map to `PotionRarity`.

- **`PotionRarity`** (`...Core.Entities.Potions`): `None, Common, Uncommon, Rare, Event, Token`.
- **`PotionUsage`** (`...Core.Entities.Potions`): `None, CombatOnly, AnyTime, Automatic`.
  - `CombatOnly` — usable only in combat (damage, block, most buffs). Most potions.
  - `AnyTime` — usable in or out of combat (heal, max-HP, card generation).
  - `Automatic` — fires without manual use (e.g. Fairy in a Bottle).
- **`TargetType`** (`...Core.Entities.Cards`; **potions share the card enum**):
  `None, Self, AnyEnemy, AllEnemies, RandomEnemy, AnyPlayer, AnyAlly, AllAllies,
  TargetedNoCreature, Osty`.
  - Self-buffs generally use **`AnyPlayer`** (e.g. Block/Dexterity Potion), not
    `Self` — potions target a player creature (see PotionModel.IsValidTarget; potion
    targeting differs from cards). Single-enemy damage uses **`AnyEnemy`**; whole-
    room uses **`AllEnemies`**.

## Rarity distribution

Common 20 · Uncommon 20 · Rare 20 · Event 2 · Token 1. Pools: `shared` 46 (colorless,
any character — the default), plus small character pools (`ironclad`, `silent`,
`defect`, `regent`, `necrobinder`) 3 each, and `event` 2. **Use `SharedPotionPool`
unless the request is character-specific.**

## The 63 potions (name · pool · effect)

Effects are the eng hover text with markup stripped. Bracketed `[energy:N]`/`[star:N]`
denote the game's icon-prefixed resources.

### Common
- Attack Potion [shared] — Choose 1 of 3 random Attack cards to add into your Hand. Free to play this turn.
- Block Potion [shared] — Gain 12 Block.
- Blood Potion [ironclad] — Heal for 20% of your Max HP.
- Colorless Potion [shared] — Choose 1 of 3 random Colorless cards to add into your Hand. Free to play this turn.
- Dexterity Potion [shared] — Gain 2 Dexterity.
- Energy Potion [shared] — Gain [energy:2].
- Explosive Ampoule [shared] — Deal 10 damage to ALL enemies.
- Fire Potion [shared] — Deal 20 damage.
- Flex Potion [shared] — Gain 5 Strength. At the end of your turn, lose 5 Strength.
- Focus Potion [defect] — Gain 2 Focus.
- Poison Potion [silent] — Apply 6 Poison.
- Potion of Doom [necrobinder] — Apply 33 Doom.
- Power Potion [shared] — Choose 1 of 3 random Power cards to add into your Hand. Free to play this turn.
- Skill Potion [shared] — Choose 1 of 3 random Skill cards to add into your Hand. Free to play this turn.
- Speed Potion [shared] — Gain 5 Dexterity. At the end of your turn, lose 5 Dexterity.
- Star Potion [regent] — Gain [star:3].
- Strength Potion [shared] — Gain 2 Strength.
- Swift Potion [shared] — Draw 3 cards.
- Vulnerable Potion [shared] — Apply 3 Vulnerable.
- Weak Potion [shared] — Apply 3 Weak.

### Uncommon
- Ashwater [ironclad] — Exhaust any number of cards in your Hand.
- Blessing of the Forge [shared] — Upgrade all cards in your Hand for the rest of combat.
- Bone Brew [necrobinder] — Summon 15.
- Clarity Extract [shared] — Draw 1 card. At the start of your next 3 turns, draw 1 additional card.
- Cunning Potion [silent] — Add 3 Upgraded Shivs into your Hand.
- Cure All [shared] — Gain [energy:1]. Draw 2 cards.
- Duplicator [shared] — This turn, your next card is played an extra time.
- Fortifier [shared] — Triple your Block.
- Fysh Oil [shared] — Gain 1 Strength and 1 Dexterity.
- Gambler's Brew [shared] — Discard any number of cards, then draw that many.
- Heart of Iron [shared] — Gain 7 Plating.
- King's Courage [regent] — Forge 15.
- Liquid Bronze [shared] — Gain 3 Thorns.
- Potion of Binding [shared] — Apply 1 Weak and 1 Vulnerable to ALL enemies.
- Potion of Capacity [defect] — Gain 2 Orb Slots.
- Powdered Demise [shared] — Enemy loses 9 HP at the end of each of its turns.
- Radiant Tincture [shared] — Gain [energy:1]. Gain an additional [energy:1] at the start of your next 3 turns.
- Regen Potion [shared] — Gain 5 Regen.
- Stable Serum [shared] — Retain your Hand for 2 turns.
- Touch of Insanity [shared] — Choose a card in your Hand. It is free to play this combat.

### Rare
- Beetle Juice [shared] — Enemy's attacks deal 30% less damage for the next 4 turns.
- Bottled Potential [shared] — Shuffle ALL your cards into your Draw Pile. Draw 5 cards.
- Cosmic Concoction [regent] — Add 3 Upgraded Colorless cards into your Hand.
- Distilled Chaos [shared] — Play the top 3 cards of your Draw Pile.
- Droplet of Precognition [shared] — Choose a card in your Draw Pile and add it into your Hand.
- Entropic Brew [shared] — Fill all your empty potion slots with random potions.
- Essence of Darkness [defect] — Channel a Dark for each of your Orb Slots.
- Fairy in a Bottle [shared] — When your HP would be reduced to 0, instead this potion is discarded and you heal to 30% of Max HP.
- Fruit Juice [shared] — Gain 5 Max HP.
- Ghost in a Jar [silent] — Gain 1 Intangible.
- Gigantification Potion [shared] — The next Attack you play deals triple damage.
- Liquid Memories [shared] — Put a card from your Discard Pile into your Hand. Free to play this turn.
- Lucky Tonic [shared] — Gain 1 Buffer.
- Mazaleth's Gift [shared] — Gain 1 Ritual.
- Orobic Acid [shared] — Add a random Attack, Skill, and Power into your Hand. Free to play this turn.
- Pot of Ghouls [necrobinder] — Add 2 Souls into your Hand.
- Shackling Potion [shared] — ALL enemies lose 7 Strength this turn.
- Ship in a Bottle [shared] — Gain 10 Block. Next turn, gain 10 Block.
- Snecko Oil [shared] — Draw 7 cards. Randomize the cost of cards in your Hand this turn.
- Soldier's Stew [ironclad] — All cards containing Strike gain 1 Replay this combat.

### Event / Token
- Foul Potion [event] — Deal 12 damage to ALL players and enemies. Can be thrown at the Merchant for 100 Gold.
- Glowwater Potion [event] — Exhaust your Hand. Draw 10 cards.
- Potion-Shaped Rock [token] — Deal 15 damage.

## How the recipe uses this

- **Pick a realistic effect + numbers** for the requested potion by matching the
  closest vanilla row (e.g. "a potion that heals" → Blood Potion/Fruit Juice shape).
- **The simplest, fully-modeled analogs** (self-buff and single-target damage) are
  `BlockPotion` and `FirePotion` — `recipes/potion.md` reproduces both in full.
- For an effect not represented here, or exact code signatures, follow
  `grounding.md` (content → live spire-codex; code → the local decompile).
