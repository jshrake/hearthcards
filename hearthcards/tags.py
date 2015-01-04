import json
from enum import IntEnum
from collections import namedtuple
from pkg_resources import resource_string
import os


def tag_to_val():
    return json.loads(
        resource_string(
            __name__, os.path.join('data','tags.json')).decode('utf-8'))


def val_to_tag():
    """Inverse of tag_to_val sans the mechanics list
    """
    return {outer_k: {v: k for (k, v) in outer_v.items()}
            for (outer_k, outer_v) in tag_to_val().items()
            if isinstance(outer_v, dict)}


GameTag = IntEnum('GameTag', tag_to_val().get('GAMETAG').items())
CardSet = IntEnum('CardSet', tag_to_val().get('CARD_SET').items())
CardType = IntEnum('CardType', tag_to_val().get('CARDTYPE').items())
Class = IntEnum('Class', tag_to_val().get('CLASS').items())
Faction = IntEnum('Faction', tag_to_val().get('FACTION').items())
CardRace = IntEnum('CardRace', tag_to_val().get('CARDRACE').items())
Rarity = IntEnum('Rarity', tag_to_val().get('RARITY').items())
Step = IntEnum('Step', tag_to_val().get('STEP').items())
Zone = IntEnum('Zone', tag_to_val().get('ZONE').items())
SpellZone = IntEnum('SpellZone', tag_to_val().get('SPELL_ZONE').items())
Requirement = IntEnum('Requirement', tag_to_val().get('REQUIREMENT').items())
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
