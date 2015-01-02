import disunity
import shutil
import tempfile
import xml.etree.ElementTree as ET
import os
from enum import Enum
import json
from tags import (GameTag, CardSet, CardType, Class,
                  Faction, CardRace, Rarity,
                  Requirement, Mechanics)


class CardDef(object):
    """
    Represents a single in game Entity
    """
    def __init__(self, entity_el):
        """
        - el is a single ElementTree.Element object with an Entity tag
        from one of the language specific Hearthstone card xml files
        - lang is the language string, currently only used for the image
        urlls
        """
        self._tags = {}
        self._referenced_tags = {}
        self._play_requirements = {}
        self._entourage_cards = []
        self._power_history_info = {}
        self._mechanics = []

        def is_mechanic(t):
            return t in Mechanics

        def read_tag(el):
            enum_id = el.attrib.get("enumID", None)
            tag = GameTag(_to_int_or_none(enum_id))
            t = el.attrib.get("type", None)
            if t == 'String':
                self._tags[tag] = el.text
            else:
                value = _to_int_or_none(el.attrib.get("value", None))
                self._tags[tag] = value
                # check if the tag is a mechanic
                if is_mechanic(tag):
                    self._mechanics.append(tag)

        def read_referenced_tag(el):
            enum_id = el.attrib.get("enumID", None)
            tag = GameTag(_to_int_or_none(enum_id))
            value = _to_int_or_none(el.attrib.get("value", None))
            self._referenced_tags[tag] = value

        def read_master_power(el):
            self.master_power = el.text

        def read_power(el):
            def read_play_requirement(el):
                enum_id = el.attrib.get("reqID", None)
                req = _to_enum_or_none(Requirement, enum_id)
                if req is not None:
                    param = _to_int_or_none(el.attrib.get("param", None))
                    self._play_requirements[req] = param or 0
            self._power_definition = el.attrib.get("definition", None)
            for child in el.iter():
                read_play_requirement(child)

        def read_entourage_card(el):
            self._entourage_cards.append(el.attrib["cardID"])

        def read_triggered_power_history_info(el):
            effect_index = _to_int_or_none(el.attrib.get("effectIndex", None))
            if effect_index is not None:
                show = bool(el.attrib.get("showInHistory", False))
                self._power_history_info[effect_index] = show

        reader = {
            'Tag': read_tag,
            'ReferencedTag': read_referenced_tag,
            'MasterPower': read_master_power,
            'Power': read_power,
            'EntourageCard': read_entourage_card,
            'TriggeredPowerHistoryInfo': read_triggered_power_history_info,
        }
        for el in entity_el:
            action = reader.get(el.tag, lambda x: None)
            action(el)

        self._id = entity_el.attrib["CardID"]

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._tags[GameTag.CARDNAME]

    @property
    def type(self):
        return CardType(self._tags.get(GameTag.CARDTYPE, 0))

    @property
    def set(self):
        return CardSet(self._tags.get(GameTag.CARD_SET, 0))

    @property
    def faction(self):
        return Faction(self._tags.get(GameTag.FACTION, 0))

    @property
    def rarity(self):
        return Rarity(self._tags.get(GameTag.RARITY, 0))

    @property
    def player_class(self):
        return Class(self._tags.get(GameTag.CLASS, 0))

    @property
    def race(self):
        return CardRace(self._tags.get(GameTag.CARDRACE, 0))

    @property
    def cost(self):
        return self._tags.get(GameTag.COST, None)

    @property
    def attack(self):
        return self._tags.get(GameTag.ATK, None)

    @property
    def health(self):
        return self._tags.get(GameTag.HEALTH, None)

    @property
    def durability(self):
        return self._tags.get(GameTag.DURABILITY, None)

    @property
    def is_elite(self):
        return self._tags.get(GameTag.ELITE, 0) == 1

    @property
    def artist_name(self):
        return self._tags.get(GameTag.ARTISTNAME, None)

    @property
    def cardtext_inhand(self):
        return self._tags.get(GameTag.CARDTEXT_INHAND, None)

    @property
    def cardtext_inplay(self):
        return self._tags.get(GameTag.CARDTEXT_INPLAY, None)

    @property
    def flavor_text(self):
        return self._tags.get(GameTag.FLAVORTEXT, None)

    @property
    def is_collectible(self):
        return self._tags.get(GameTag.COLLECTIBLE, 0) == 1

    @property
    def how_to_earn(self):
        return self._tags.get(GameTag.HOW_TO_EARN, None)

    @property
    def how_to_earn_golden(self):
        return self._tags.get(GameTag.HOW_TO_EARN_GOLDEN, None)

    @property
    def entourage_cards(self):
        return self._entourage_cards

    @property
    def power_definition(self):
        return self._power_definition

    @property
    def play_requirements(self):
        return self._play_requirements

    @property
    def mechanics(self):
        return self._mechanics

    def image_uri(self, lang):
        base_uri = "http://wow.zamimg.com/images/hearthstone/cards"
        return "{0}/{1}/original/{2}.png".format(
            base_uri, lang.lower(), self.id)

    def image_golden_uri(self, lang):
        base_uri = "http://wow.zamimg.com/images/hearthstone/cards"
        return "{0}/{1}/animated/{2}_premium.gif".format(
            base_uri, lang.lower(), self.id)

    def has_tag(self, game_tag):
        return game_tag in self._tags

    def get_tag(self, game_tag):
        return self._tags[game_tag]

    def has_requirement(self, req):
        return req in self._play_requirements

    def get_requirement(self, req):
        return self._play_requirements[req]

    def repr(self):
        return {
            GameTag.CARD_ID: self.id,
            GameTag.CARDNAME: self.name,
            GameTag.CARDRACE: self.race,
            GameTag.CARDTYPE: self.type,
            GameTag.CLASS: self.player_class,
            GameTag.RARITY: self.rarity,
            GameTag.ELITE: self.is_elite,
            GameTag.COLLECTIBLE: self.is_collectible,
            GameTag.CARD_SET: self.set,
            GameTag.FACTION: self.faction,
            GameTag.COST: self.cost,
            GameTag.ATK: self.attack,
            GameTag.HEALTH: self.health,
            GameTag.DURABILITY: self.durability,
            GameTag.HOW_TO_EARN: self.how_to_earn,
            GameTag.HOW_TO_EARN_GOLDEN: self.how_to_earn_golden,
            GameTag.FLAVORTEXT: self.flavor_text,
            GameTag.CARDTEXT_INHAND: self.cardtext_inhand,
            GameTag.CARDTEXT_INPLAY: self.cardtext_inplay,
        }

    def human_repr(self):
        name_if_enum = lambda x: x.name if isinstance(x, Enum) else x
        tmp = {name_if_enum(k): name_if_enum(v)
               for (k, v) in self.repr().items()}
        tmp["MECHANICS"] = [mech.name for mech in self.mechanics]
        tmp["ENTOURAGE_CARDS"] = self.entourage_cards
        tmp["PLAY_REQUIREMENTS"] = {name_if_enum(k): name_if_enum(v) for
                                    (k, v) in self.play_requirements.items()}
        return tmp

    def __str__(self):
        return json.dumps(self.human_repr(),
                          sort_keys=True, indent=4,
                          ensure_ascii=False)


def card_defs(data_dir):
    """Returns a dict of language to card xml element tree objects
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        # copy the cards xml unity3d file to a temp directory
        cardxml_filename = "cardxml0.unity3d"
        src = os.path.join(data_dir, cardxml_filename)
        if not os.path.exists(src):
            raise IOError("Cannot find file " + src)
        dst = os.path.join(tmp_dir, cardxml_filename)
        shutil.copyfile(src, dst)
        # run disunity extract on the tmp cardxml0.unity3d file
        disunity.extract(dst)
        # build the dict
        xml_files_dir = os.path.join(
            tmp_dir, "cardxml0", "CAB-cardxml0", "TextAsset")
        if not os.path.exists(xml_files_dir):
            raise IOError(
                "disunity extract failed, cannot find temporary directory @ "
                + xml_files_dir)
        return {os.path.splitext(file)[0]:
                ET.parse(os.path.join(xml_files_dir, file))
                for file in os.listdir(xml_files_dir)}


def _to_int_or_none(val):
    """attempts to convert val to int or None
    """
    return int(val) if val is not None and val != '' else None


def _to_enum_or_none(enumeration, val):
    try:
        return enumeration(_to_int_or_none(val))
    except:
        return None
