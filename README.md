# hearthcards
hearthcards is a Python 3 library for Hearthstone analysis

# install
    python setup.py install

# uninstall
    python setup.py clean --all

# test
    python3 -m unittest

# usage
```python
from hearthcards import arena, Hero, CardRace, GameTag
# The expected number of turns containing at least one 3-drop minion, given 10 turns remaining
is_3_drop = lambda card: card.is_minion and card.cost == 3
arena.draft_e(Hero.MAGE, is_3_drop, 10)
>>4.544

# The expected number of turns containing at least one spell
arena.draft_e(Hero.MAGE, lambda c: c.is_ability, 30)
>> 14.961

# The probability that at least 2 of the next 20 turns offers a Fireball
p = arena.draft_p(Hero.MAGE, lambda c: c.name == "Fireball", 20)
1.0 - sum([p(k=i) for i in range(0, 2)])
>> 0.162

# The expected number of turns containing at least one beast or taunt minion
beast_or_taunt = lambda c: c.is_minion and (c.race == CardRace.PET or GameTag.TAUNT in c.mechanics)
arena.draft_e(Hero.HUNTER, beast_or_taunt, 30)
>>16.4147

```

# dependencies
hearthcards currently extracts the card data directly from the Hearthstone game client data files using [disunity](https://github.com/ata4/disunity).
- Python 3.4
- Installed Hearthstone game client
- Java for [disunity](https://github.com/ata4/disunity)

In the future, I may remove the Hearthstone and Java dependencies by adding an option to load the card definition data from a (JSON?) file.

# hson
hearthcards comes with a `hson`, a command-line utility for extracting all card data from the Hearthstone asset files and generating JSON output.

    hson [-h] [-r] [-d DATA_DIR] [-o OUTPUT_DIR]

    optional arguments:
      -h, --help            show this help message and exit
      -r, --raw             Output the raw integer values specified in the
                            Hearthstone data file rather than the human readable
                            string representations. Useful for application
                            interop.
      -d DATA_DIR, --data-dir DATA_DIR
                            Hearthstone data directory containing the
                            cardxml0.unity3d file. Only required for a non-default
                            Hearthstone install. Default install location on
                            Windows: C:\Program Files (x86)\Hearthstone\Data\Win
                            Default install location on OS X:
                            /Applications/Hearthstone/Data/OSX
      -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                            Output directory. By default, outputs data into
                            current/working/directory/hson-output/

