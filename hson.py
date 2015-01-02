#!/usr/bin/env python

from enum import Enum
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile


def dir_of_this_py_file():
    return os.path.dirname(os.path.abspath(__file__))


def find_first_match(regex, l):
    """Returns the first item in the list l that matches
    the regex provided
    """
    return next(i for i in l if re.search(regex, i))


def unzip_disunity():
    """Unzips the disunity_v zipfile into a directory named disunity
    """
    files = os.listdir(dir_of_this_py_file())
    disunity_zip = find_first_match("disunity.+\.zip", files)
    if disunity_zip is None:
        raise IOError("cannot find disunity zipfile @ " + disunity_zip)
    else:
        with zipfile.ZipFile(disunity_zip, "r") as z:
            z.extractall(os.path.join(dir_of_this_py_file(), "disunity"))


def disunity(commands, filename):
    """Runs disunity commands on the given filename
    filename should be the absolute path to a unity3d file
    """
    disunity_jar_loc = os.path.join(
        dir_of_this_py_file(), "disunity", "disunity.jar")
    if not os.path.exists(disunity_jar_loc):
        unzip_disunity()
        if not os.path.exists(disunity_jar_loc):
            raise IOError("cannot find disunity jar @ " + disunity_jar_loc)
    args = ["java", "-jar", disunity_jar_loc, commands, filename]
    subprocess.call(args)


def disunity_extract(filename):
    """Runs disunity extract on the given filename
    filename should be the absolute path to a unity3d file
    """
    disunity("extract", filename)


def hearthstone_data_dir():
    """Returns the absolute directory containing the
    hearthstone unity3d files in a platform independent
    manner
    """
    win_prog_files = os.environ.get(
        "ProgramFiles(x86)", os.path.join("C:", os.sep, "Program Files (x86)"))
    default_dirs = {
        "win32": os.path.join(
            win_prog_files, "Hearthstone", "Data", "Win"),
        "darwin": os.path.join(
            os.sep, "Applications", "Hearthstone", "Data", "OSX")}
    return default_dirs[sys.platform]


def lang_to_card_def_xml():
    """Returns a dict of language to card xml files
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        # copy the cards xml unity3d file to a temp directory
        cardxml_filename = "cardxml0.unity3d"
        src = os.path.join(hearthstone_data_dir(), cardxml_filename)
        if not os.path.exists(src):
            raise IOError("Cannot find file " + src)
        dst = os.path.join(tmp_dir, cardxml_filename)
        shutil.copyfile(src, dst)
        # run disunity extract on the tmp cardxml0.unity3d file
        disunity_extract(dst)
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


def lang_to_entity_lists(m):
    return {k: entity_list(v.getroot(), k) for (k, v) in m.items()}


class CardSet(Enum):
    TestTemporary = 1
    Basic = 2
    Expert = 3
    Reward = 4
    Missions = 5
    Demo = 6
    Nil = 7
    Cheat = 8
    Blank = 9
    DebugSP = 10
    Promo = 11
    FP1 = 12
    PE1 = 13
    FP2 = 14
    PE2 = 15
    Credit = 16


class CardType(Enum):
    Game = 1
    Player = 2
    Hero = 3
    Minion = 4
    Ability = 5
    Enchantment = 6
    Weapon = 7
    Item = 8
    Token = 9
    HeroPower = 10


class Hero(Enum):
    Invalid1 = 0
    Invalid2 = 1
    Druid = 2
    Hunter = 3
    Mage = 4
    Paladin = 5
    Priest = 6
    Rogue = 7
    Shaman = 8
    Warlock = 9
    Warrior = 10
    Neutral = 11


class CardRarity(Enum):
    Invalid = 0
    Common = 1
    Free = 2
    Rare = 3
    Epic = 4
    Legendary = 5


class CardFaction(Enum):
    Horde = 1
    Alliance = 2
    Neutral = 3


class CardRace(Enum):
    Bloodelf = 1
    Draenei = 2
    Dwarf = 3
    Gnome = 4
    Goblin = 5
    Human = 6
    Nightelf = 7
    Orc = 8
    Tauren = 9
    Troll = 10
    Undead = 11
    Worgen = 12
    Goblin2 = 13
    Murloc = 14
    Demon = 15
    Scourge = 16
    Mechanical = 17
    Elemental = 18
    Ogre = 19
    Pet = 20
    Totem = 21
    Nerubian = 22
    Pirate = 23
    Dragon = 24


class Entity:

    def __init__(self, el, lang):
        self.id = el.attrib["CardID"]
        self.name = get_text(el, 185)
        self.set = to_card_set_safe(get_attrib(el, 183))
        self.type = to_card_type_safe(get_attrib(el, 202))
        self.faction = to_card_faction_safe(get_attrib(el, 201))
        self.rarity = to_card_rarity_safe(get_attrib(el, 203))
        self.hero = to_hero_safe(get_attrib(el, 199))
        self.race = to_card_race_safe(get_attrib(el, 200))
        self.cost = to_int_safe(get_attrib(el, 48))
        self.attack = to_int_safe(get_attrib(el, 47))
        self.health = to_int_safe(get_attrib(el, 45))
        self.artist = get_text(el, 342)
        self.abilities = []
        self.text = get_text(el, 184)
        self.flavor = get_text(el, 351)
        self.collectible = to_int_safe(get_attrib(el, 321)) == 1
        self.image_original = "http://wow.zamimg.com/images/hearthstone/cards/{0}/original/{1}.png".format(lang.lower(), self.id)
        self.image_golden = "http://wow.zamimg.com/images/hearthstone/cards/{0}/animated/{1}_premium.gif".format(lang.lower(), self.id)

    def to_json(self):
        class EnumValEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, Enum):
                    return obj.value
                else:
                    return obj.__dict__
        return json.dumps(self, sort_keys=True, indent=4, cls=EnumValEncoder)

    def to_human_json(self):
        class EnumNameEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, Enum):
                    return obj.name
                else:
                    return obj.__dict__
        return json.dumps(self, sort_keys=True, indent=4, cls=EnumNameEncoder)

    def __str__(self):
        return self.to_human_json()


def get_attrib(el, id):
    n = el.find("./Tag[@enumID='{0}']".format(id))
    return n.attrib["value"] if not n is None else None


def get_text(el, id):
    n = el.find("./Tag[@enumID='{0}']".format(id))
    return n.text if n is not None else None


def to_int_safe(val):
    return int(val) if val is not None else None


def to_cls_safe(cls, val):
    return cls(int(val)) if val is not None and int(val) is not None else None


def to_card_set_safe(val):
    return to_cls_safe(CardSet, val)


def to_card_type_safe(val):
    return to_cls_safe(CardType, val)


def to_card_faction_safe(val):
    return to_cls_safe(CardFaction, val)


def to_card_rarity_safe(val):
    return to_cls_safe(CardRarity, val)


def to_hero_safe(val):
    return to_cls_safe(Hero, val)


def to_card_race_safe(val):
    return to_cls_safe(CardRace, val)


def entity_list(xml_root, lang="enUS"):
    return [Entity(e, lang) for e in xml_root]
