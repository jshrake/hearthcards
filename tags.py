from enum import Enum
from collections import namedtuple

_TAGFILE = 'tags.json'


def tag_to_val():
    import json
    if "m" not in tag_to_val.__dict__:
        with open(_TAGFILE, 'r') as f:
            tag_to_val.m = json.load(f)
    return tag_to_val.m


def val_to_tag():
    """Inverse of tag_to_val sans the mechanics list
    """
    if "m" not in val_to_tag.__dict__:
        val_to_tag.m = {outer_k: {v: k for (k, v) in outer_v.items()}
                        for (outer_k, outer_v) in tag_to_val().items()
                        if isinstance(outer_v, dict)}
    return val_to_tag.m


GameTag = Enum('GameTag', tag_to_val().get('GAMETAG').items())
CardSet = Enum('CardSet', tag_to_val().get('CARD_SET').items())
CardType = Enum('CardType', tag_to_val().get('CARDTYPE').items())
Class = Enum('Class', tag_to_val().get('CLASS').items())
Faction = Enum('Faction', tag_to_val().get('FACTION').items())
CardRace = Enum('CardRace', tag_to_val().get('CARDRACE').items())
Rarity = Enum('Rarity', tag_to_val().get('RARITY').items())
Step = Enum('Step', tag_to_val().get('STEP').items())
Zone = Enum('Zone', tag_to_val().get('ZONE').items())
Mechanics = [GameTag[m] for m in tag_to_val().get('MECHANICS')]


Locale = namedtuple('Locale', 'code country language')
Locales = {
    'enUS': Locale('enUS', 'United States', 'English'),
    'enGB': Locale('enGB', 'Great Britain', 'English'),
    'frFR': Locale('frFR', 'France', 'French'),
    'zhTW': Locale('zhTW', 'Taiwan', 'Chinese'),
    'zhCN': Locale('zhCN', 'China', 'Chinese'),
    'ruRU': Locale('ruRU', 'Russia', 'Russian'),
    'ptBR': Locale('ptBR', 'Brazil', 'Portuguese'),
    'ptPT': Locale('ptPT', 'Portugal', 'Portuguese'),
    'plPL': Locale('plPL', 'Poland', 'Polish'),
    'koKR': Locale('koKR', 'South Korea', 'Korean'),
    'itIT': Locale('itIT', 'Italy', 'Italian'),
    'esMX': Locale('esMX', 'Mexico', 'Spanish'),
    'esES': Locale('esES', 'Spain', 'Spanish'),
    'deDE': Locale('deDE', 'Germany', 'German')
}
