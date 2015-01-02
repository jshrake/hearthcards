#!/usr/bin/env python3

import argparse
import json
import os
import card_def
from util import dir_of_this_py_file, hearthstone_data_dir


def write_json_card_defs(output_dir, data_dir, repr):
    """
    """
    to_json = lambda root: json.dumps(
        [repr(card_def.CardDef(e)) for e in root.iter('Entity')],
        sort_keys=True, indent=4, ensure_ascii=False)
    for (lang, xml) in card_def.card_defs(data_dir).items():
        filename = os.path.join(output_dir, "{0}.json".format(lang))
        with open(filename, 'w+', encoding='utf-8') as f:
            f.write(to_json(xml.getroot()))


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
    machine_repr = lambda cd: cd.repr()
    human_repr = lambda cd: cd.human_repr()
    write_json_card_defs(args.output_dir, args.data_dir,
                         machine_repr if args.raw
                         else human_repr)

if __name__ == "__main__":
    main()
