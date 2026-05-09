
# Foundry VTT Actor Data Translation JSON Key Paths
This document provides the definitions for the technical data structures found in the campaign .md exports. Use these rules to interpret character sheets and items.


### Attribute Mappings
- `system.details.level` ⮕ Character Level
- `system.details.biography` ⮕ Background information / biography of the character. Has a strong influence on their knowledge and personality that will be portrayed.
- `system.details.alignment` ⮕ Character alignment. Explains the nature of the character and their intentions. See [_character_mechanics.md](./_character_mechanics.md) for more information.
- `system.details.race` ⮕ The character's species or lineage (e.g., Mechanatrix, human, elf, dwarf, half elf)
- `system.details.background` ⮕ character's background / upbringing. example: a noble, a farmer / peasant, a common thief, etc..
- `system.details.appearance` ⮕ textual description of the character's appearance
- `system.details.height` ⮕ character's height
- `system.details.eyes` ⮕ character's eye color
- `system.details.hair` ⮕ character's hair color
- `system.details.weight` ⮕ character's weight in pounds (lb)
- `system.details.skin` ⮕ character's skin color
- `system.details.gender` ⮕ character's gender. example: male, female, unknown, Construct (android, mechanical, cyborg, etc.), etc..
- `system.details.age` ⮕ Character's age in years
- `system.details.trait` ⮕ These are the small, repetitive habits, preferences, or mannerisms that make a character unique. They should be specific enough to act out (e.g., "I use polysyllabic words to sound more learned" or "I am always chewing on a piece of sour leaf").
- `system.details.ideal` ⮕ These are the fundamental ethical and moral beliefs that drive your character. They are the "Why" behind your actions. Ideals are often linked to your alignment (e.g., a Lawful Ideal might be "Tradition," while a Good Ideal might be "Self-Sacrifice").
- `system.details.bonds` ⮕ These represent your character's connections to the world. A bond is a person, place, or event that you would die to protect or redeem. It provides the Dungeon Master (DM) with "plot hooks" to pull your character into the story.
- `system.details.flaw` ⮕ This is a paradox, weakness, or vice that an opponent can exploit. Flaws make characters relatable and provide opportunities for dramatic failure and growth.

- `system.abilities.str.value` ⮕ Str = Strength: Physical Strength
- `system.abilities.dex.value` ⮕ Dex = Dexterity: Agility and Reflexes
- `system.abilities.con.value` ⮕ Con = Constitution: Toughness and Health
- `system.abilities.int.value` ⮕ Int = Intelligence and Knowledge
- `system.abilities.wis.value` ⮕ Wis = Wisdom: Perception and Insight
- `system.abilities.cha.value` ⮕ Cha = Charisma: Charisma and likeability

- `system.attributes.hp.value` ⮕ Current Hit Points (Health)
- `system.attributes.hp.max` ⮕ Maximum Health
- `system.attributes.ac.value` ⮕ Armor Class (Defense)


### Data Interpretation Rules
- **Ignore UUIDs:** Any string like `Actor.v8x9...` is a database pointer. Ignore it.
- **Ignore Flags:** Lines starting with `flags.` are internal system settings and irrelevant to lore.
- **Hierarchy:** The `biography` or `content` fields contain the most important narrative "Truth." Priority should be given to these over technical numbers.

### Special Context (Campaign Specific)
- **Mechanatrix:** A rare race of machine-organic hybrids. Treat any "Mechanatrix" as having high logic but low emotional intuition.
