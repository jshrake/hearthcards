#!/usr/bin/env python3

import argparse
import json
import os
from hearthcards import hearthstone_data_dir, card_db


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--raw', default=False, required=False,
                        action='store_true',
                        help="""Output the raw integer values specified in the
                        Hearthstone data file rather than the human readable
                        string representations. Useful for application interop.""")
    parser.add_argument('-d', '--data-dir', default=hearthstone_data_dir(),
                        required=False,
                        help="""Hearthstone data directory containing the 
                        cardxml0.unity3d file.
                        Only required for a non-default Hearthstone install.
                        Default install location on Windows:
                        C:\\Program Files (x86)\\Hearthstone\\Data\\Win
                        Default install location on OS X:
                        /Applications/Hearthstone/Data/OSX""")
    parser.add_argument('-o', '--output-dir',
                        default=os.path.join(os.getcwd(), "hson-output"),
                        required=False,
                        help="""Output directory. By default, outputs data into
                        current/working/directory/hson-output/""")
    args = parser.parse_args()
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    machine_repr = lambda card, lang: card.repr(lang)
    human_repr = lambda card, lang: card.human_repr(lang)
    repr = machine_repr if args.raw else human_repr
    card_defs = card_db(args.data_dir)
    for (lang, cards) in card_defs.items():
        data = [repr(card, lang) for card in cards]
        filename = os.path.join(args.output_dir, "{0}.json".format(lang))
        with open(filename, 'w+', encoding='utf-8') as f:
            f.write(json.dumps(data, sort_keys=True,
                               indent=4, ensure_ascii=False))

if __name__ == "__main__":
    main()
