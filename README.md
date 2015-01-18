# hearthcards
hearthcards is a Python 3 library for Hearthstone analysis

# install
  python setup.py install

# uninstall
  python setup.py clean --all

# usage
```python
from hearthcards (import card_db, Locale, CardType, 
                  CardRace, Class, GameTag, expected_number)
# extract card data from the unity3d cardxml file
all_cards = card_db()[Locale.US]
# the set of cards to draft from
draftable_cards = [c for c in all_cards if c.is_collectible and c.type != CardType.HERO]
# get the expected number of spells offered in an arena mage draft with 30 picks remaining
print(expected_number(Class.MAGE, draftable_cards, lambda c: c.is_ability, 30))
# get the expected number of mech minions in an arena warlock draft with 15 picks remaining
print(expected_number(Class.WARLOCK, draftable_cards, lambda c: c.race == CardRace.MECHANICAL, 15))
# get the expected number of minions with taunt with 10 picks remaining in a warrior draft
print(expected_number(Class.WARRIOR, draftable_cards, lambda c: GameTag.TAUNT in c.mechanics, 10))
```

# hson
hearthcards comes with a `hson`, a command-line utility for generating json descriptions of all cards for each language Hearthstone supports.

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

# dependencies
- Python 3.(4?)
- Hearthstone
- Java. hearthcards extracts data directly from the Hearthstone game client data files using [disunity](https://github.com/ata4/disunity), which requires some version of Java. 
