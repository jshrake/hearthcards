import json
from enum import IntEnum
from pkg_resources import resource_string
import os


def tag_to_val():
    return json.loads(
        resource_string(
            __name__, os.path.join('data', 'tags.json')).decode('utf-8'))


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
