# hson
hson is a Python 3 tool for extracting Hearthstone game data

# usage
    usage: hson.py [-h] [-r] [-d DATA_DIR] [-o OUTPUT_DIR]

    optional arguments:
      -h, --help            show this help message and exit
      -r, --raw             Output the raw integer values specified in the
                            Hearthstone data file rather than the human readble
                            string representation
      -d DATA_DIR, --data-dir DATA_DIR
                            Hearthstone data directory. Only required for a non-
                            default Hearthstone install.
                            Default windows location:
                                C:\Program Files (x86)\Hearthstone\Data\Win
                            Default osx location:
                                /Applications/Hearthstone/Data/OSX
      -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                            Output directory for json files

# dependencies
Some version of Java for [disunity](https://github.com/ata4/disunity).