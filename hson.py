#!/usr/bin/env python3

import argparse
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
from tags import (CardSet, CardType, Class,
                  Faction, CardRace, Rarity,
                  Mechanics, tag_to_val,
                  val_to_tag)


def dir_of_this_py_file():
    return os.path.dirname(os.path.abspath(__file__))


def find_first_match(regex, l):
    """Returns the first item in the list l that matches
    the regex provided
    """
    return next(i for i in l if re.search(regex, i))


def unzip_disunity(to_dir):
    """Unzips the disunity_v zipfile into a directory named disunity
    """
    files = os.listdir(dir_of_this_py_file())
    disunity_zip = find_first_match("disunity.+\.zip", files)
    if disunity_zip is None:
        raise IOError("cannot find disunity zipfile @ " + disunity_zip)
    else:
        with zipfile.ZipFile(disunity_zip, "r") as z:
            z.extractall(to_dir)


def disunity(commands, filename):
    """Runs disunity commands on the given filename
    filename should be the absolute path to a unity3d file
    """
    disunity_dir = os.path.join(dir_of_this_py_file(), "disunity")
    disunity_jar_loc = os.path.join(disunity_dir, "disunity.jar")
    if not os.path.exists(disunity_jar_loc):
        unzip_disunity(disunity_dir)
        if not os.path.exists(disunity_jar_loc):
            raise IOError("cannot find disunity jar @ " + disunity_jar_loc)
    args = ["java", "-jar", disunity_jar_loc, commands, filename]
    subprocess.call(args)


def disunity_extract(filename):
    """Runs disunity extract on the given filename
    filename should be the absolute path to a unity3d file
    """
    disunity("extract", filename)


def card_xmls(data_dir):
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


class EnumNameEncoder(json.JSONEncoder):
    """A JSON Encoder that uses the name attribute for Enums
    """
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.name
        else:
            return obj.__dict__


class EnumValueEncoder(json.JSONEncoder):
    """A JSON Encoder that uses the value attribute for Enums
    """
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        else:
            return obj.__dict__


class Entity:
    """
    Represents a single in game Entity
    """
    def __init__(self, el, lang):
        """
        - el is a single ElementTree.Element object with an Entity tag
        from one of the language specific Hearthstone card xml files
        - lang is the language string, currently only used for the image
        urlls
        """
        self.id = el.attrib["CardID"]
        self.name = _get_text(el, "CARDNAME")
        self.set = _to_enum_or_none(CardSet, _get_attrib(el, "CARD_SET"))
        self.type = _to_enum_or_none(CardType, _get_attrib(el, "CARDTYPE"))
        self.faction = _to_enum_or_none(Faction, _get_attrib(el, "FACTION"))
        self.rarity = _to_enum_or_none(Rarity, _get_attrib(el, "RARITY"))
        self.hero = _to_enum_or_none(Class, _get_attrib(el, "CLASS"))
        self.race = _to_enum_or_none(CardRace, _get_attrib(el, "CARDRACE"))
        self.cost = _to_int_or_none(_get_attrib(el, "COST"))
        self.attack = _to_int_or_none(_get_attrib(el, "ATK"))
        self.health = _to_int_or_none(_get_attrib(el, "HEALTH"))
        self.durability = _to_int_or_none(_get_attrib(el, "DURABILITY"))
        self.elite = _to_int_or_none(_get_attrib(el, "ELITE")) == 1
        self.artist = _get_text(el, "ARTISTNAME")
        self.mechanics = [m for m in Mechanics
                          if _get_attrib(el, m.name) is not None]
        self.text_in_hand = _get_text(el, "CARDTEXT_INHAND")
        self.text_in_play = _get_text(el, "CARDTEXT_INPLAY")
        self.flavor = _get_text(el, "FLAVORTEXT")
        self.collectible = _to_int_or_none(_get_attrib(el, "COLLECTIBLE")) == 1
        self.how_to_get = _get_text(el, "HOW_TO_EARN")
        self.how_to_get_golden = _get_text(el, "HOW_TO_EARN_GOLDEN")
        # for debug purposes
        self.unknown_tags = []
        for c in el.iter():
            val = _to_int_or_none(c.attrib.get('enumID', None))
            if val is not None and not val in val_to_tag()['GAMETAG']:
                self.unknown_tags.append(val)
        # card images
        base_uri = "http://wow.zamimg.com/images/hearthstone/cards"
        self.image_original = "{0}/{1}/original/{2}.png".format(
            base_uri, lang.lower(), self.id)
        self.image_golden = "{0}/{1}/animated/{2}_premium.gif".format(
            base_uri, lang.lower(), self.id)
        # if this card is a minion or weapon and the cost is None, set
        # cost to 0
        is_minion = lambda e: e.type == CardType.MINION
        is_weapon = lambda e: e.type == CardType.WEAPON
        if self.cost is None and (is_minion(self) or is_weapon(self)):
            self.cost = 0

    def __str__(self):
        return json.dumps(self, sort_keys=True, indent=4, cls=EnumNameEncoder,
                          ensure_ascii=False)


def _get_attrib(el, name):
    """Returns the value of the value attribute of the element with
    enumID attribute equal to id or None if the element isn't found
    """
    n = el.find("./Tag[@enumID='{0}']".format(tag_to_val()["GAMETAG"][name]))
    return n.attrib["value"] if not n is None else None


def _get_text(el, name):
    """Returns the text of the element with enumID attribute equal to id
    or None if the element isn't found
    """
    n = el.find("./Tag[@enumID='{0}']".format(tag_to_val()["GAMETAG"][name]))
    return n.text if n is not None else None


def _to_int_or_none(val):
    """attempts to convert val to int or None
    """
    return int(val) if val is not None else None


def _to_enum_or_none(enumeration, val):
    ival = _to_int_or_none(val)
    return enumeration(ival) if ival is not None else None


def hearthstone_data_dir():
    """Returns the absolute directory containing the
    hearthstone unity3d files in a platform independent
    manner
    """
    win_prog_files = os.environ.get(
        "ProgramFiles(x86)", os.path.join("C:", os.sep, "Program Files (x86)"))
    default_dirs = {
        "win32": os.path.join(win_prog_files, "Hearthstone", "Data", "Win"),
        "darwin": os.path.join(os.sep, "Applications", "Hearthstone", "Data",
                               "OSX")
    }
    return default_dirs[sys.platform]


def write_json_card_defs(output_dir, data_dir, Encoder=EnumNameEncoder):
    """
    """
    to_json = lambda root, lang: json.dumps(
        [Entity(e, lang) for e in root.iter('Entity')],
        sort_keys=True, indent=4, cls=Encoder, ensure_ascii=False)
    for (lang, xml) in card_xmls(data_dir).items():
        filename = os.path.join(output_dir, "{0}.json".format(lang))
        with open(filename, 'w+', encoding='utf-8') as f:
            f.write(to_json(xml.getroot(), lang))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--raw', default=False, required=False,
                        action='store_true',
                        help="""Output the raw integer values specified in the
                        Hearthstone data file rather than the human readble
                        string representation""")
    parser.add_argument('-d', '--data-dir', default=hearthstone_data_dir(),
                        required=False,
                        help="""Hearthstone data directory.
                        Only required for a non-default Hearthstone install.
                        Default windows location:
                        C:\\Program Files (x86)\\Hearthstone\\Data\\Win
                        Default osx location:
                        /Applications/Hearthstone/Data/OSX""")
    parser.add_argument('-o', '--output-dir',
                        default=os.path.join(dir_of_this_py_file(), "output"),
                        required=False,
                        help="""Output directory. By default, outputs data into
                        the directory_of_this_py_file/output/""")
    args = parser.parse_args()
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    write_json_card_defs(args.output_dir, args.data_dir,
                         EnumValueEncoder if args.raw else EnumNameEncoder)

if __name__ == "__main__":
    main()
