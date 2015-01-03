import os
import sys


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
