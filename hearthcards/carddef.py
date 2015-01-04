from . import disunity
import shutil
import tempfile
import xml.etree.ElementTree as ET
import os
from enum import Enum
from .tags import (GameTag, CardSet, CardType, Class,
                   Faction, CardRace, Rarity,
                   Requirement, Mechanics)
from .util import hearthstone_data_dir


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
            self._power_definition = el.attrib.get("definition", None)

        def read_play_requirement(el):
            enum_id = el.attrib.get("reqID", None)
            req = _to_enum_or_none(Requirement, enum_id)
            if req is not None:
                param = _to_int_or_none(el.attrib.get("param", None))
                self._play_requirements[req] = param or 0

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
            'PlayRequirement': read_play_requirement,
            'TriggeredPowerHistoryInfo': read_triggered_power_history_info,
        }
        for el in entity_el.iter():
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
        return _to_enum_or_none(CardType, self.get_tag(GameTag.CARDTYPE))

    @property
    def set(self):
        return _to_enum_or_none(CardSet, self.get_tag(GameTag.CARD_SET))

    @property
    def faction(self):
        return _to_enum_or_none(Faction, self.get_tag(GameTag.FACTION))

    @property
    def rarity(self):
        return _to_enum_or_none(Rarity, self.get_tag(GameTag.RARITY))

    @property
    def player_class(self):
        return _to_enum_or_none(Class, self.get_tag(GameTag.CLASS))

    @property
    def race(self):
        return _to_enum_or_none(CardRace, self.get_tag(GameTag.CARDRACE))

    @property
    def cost(self):
        return self.get_tag(GameTag.COST)

    @property
    def attack(self):
        return self.get_tag(GameTag.ATK)

    @property
    def health(self):
        return self.get_tag(GameTag.HEALTH)

    @property
    def durability(self):
        return self.get_tag(GameTag.DURABILITY)

    @property
    def is_elite(self):
        return self.get_tag(GameTag.ELITE) == 1

    @property
    def artist_name(self):
        return self.get_tag(GameTag.ARTISTNAME)

    @property
    def cardtext_inhand(self):
        return self.get_tag(GameTag.CARDTEXT_INHAND)

    @property
    def cardtext_inplay(self):
        return self.get_tag(GameTag.CARDTEXT_INPLAY)

    @property
    def flavor_text(self):
        return self.get_tag(GameTag.FLAVORTEXT)

    @property
    def is_collectible(self):
        return self.get_tag(GameTag.COLLECTIBLE) == 1

    @property
    def how_to_earn(self):
        return self.get_tag(GameTag.HOW_TO_EARN)

    @property
    def how_to_earn_golden(self):
        return self.get_tag(GameTag.HOW_TO_EARN_GOLDEN)

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
        return self._tags.get(game_tag, None)

    def has_requirement(self, req):
        return req in self._play_requirements

    def get_requirement(self, req):
        return self._play_requirements.get(req, None)

    def repr(self, lang):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "class": self.player_class,
            "rarity": self.rarity,
            "race": self.race,
            "elite": self.is_elite,
            "collectible": self.is_collectible,
            "set": self.set,
            "faction": self.faction,
            "cost": self.cost,
            "attack": self.attack,
            "health": self.health,
            "durability": self.durability,
            "how_to_earn": self.how_to_earn,
            "how_to_earn_golden": self.how_to_earn_golden,
            "flavor_text": self.flavor_text,
            "card_text_inhand": self.cardtext_inhand,
            "card_text_inplay": self.cardtext_inplay,
            "mechanics": self.mechanics,
            "entourage_cards": self.entourage_cards,
            "play_requirements": self.play_requirements,
            "card_image": self.image_uri(lang),
            "card_golden_image": self.image_golden_uri(lang)
        }

    def human_repr(self, lang):
        snake_case = lambda s: "".join(x.title() for x in s.split('_'))
        enum_name = lambda x: snake_case(x.name) if isinstance(x, Enum) else x
        tmp = {k: enum_name(v) for (k, v) in self.repr(lang).items()}
        tmp["mechanics"] = [snake_case(mech.name) for mech in self.mechanics]
        tmp["play_requirements"] = {enum_name(k): enum_name(v) for
                                    (k, v) in self.play_requirements.items()}
        return tmp


def card_db(data_dir=hearthstone_data_dir()):
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
                card_defs_from_xml(os.path.join(xml_files_dir, file))
                for file in os.listdir(xml_files_dir)}


def card_defs_from_xml(xmlfile):
    root = ET.parse(xmlfile).getroot()
    return [CardDef(el) for el in root.iter('Entity')]


def _to_int_or_none(val):
    """attempts to convert val to int or None
    """
    return int(val) if val is not None and val != '' else None


def _to_enum_or_none(enumeration, val):
    try:
        return enumeration(_to_int_or_none(val))
    except:
        return None
