# hearthcards
hearthcards is a Python 3 library for Hearthstone analysis

# install
    python setup.py install

# uninstall
    python setup.py clean --all

# test
    python3 -m unittest

# usage
See [hearthcards/tests/test_arena.py](hearthcards/tests/test_arena.py)

# dependencies
hearthcards currently extracts the card data directly from the Hearthstone game client data files using [disunity](https://github.com/ata4/disunity).
- Python 3.4
- Installed Hearthstone game client
- Java for [disunity](https://github.com/ata4/disunity)

In the future, I may remove the Hearthstone and Java dependencies by adding an option to load the card definition data from a (JSON?) file.

# hson
hearthcards comes with a `hson`, a command-line utility for extracting all card data from the Hearthstone asset files and generating JSON output.

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

