import re
import os
import zipfile
import subprocess
from util import dir_of_this_py_file


def disunity(commands, filename):
    """Runs disunity commands on the given filename
    filename should be the absolute path to a unity3d file
    """
    disunity_dir = os.path.join(dir_of_this_py_file(), "disunity")
    disunity_jar_loc = os.path.join(disunity_dir, "disunity.jar")
    if not os.path.exists(disunity_jar_loc):
        _unzip_disunity(disunity_dir)
        if not os.path.exists(disunity_jar_loc):
            raise IOError("cannot find disunity jar @ " + disunity_jar_loc)
    args = ["java", "-jar", disunity_jar_loc, commands, filename]
    subprocess.call(args)


def extract(filename):
    """Runs disunity extract on the given filename
    filename should be the absolute path to a unity3d file
    """
    disunity("extract", filename)


def _find_first_match(regex, l):
    """Returns the first item in the list l that matches
    the regex provided
    """
    return next(i for i in l if re.search(regex, i))


def _unzip_disunity(to_dir):
    """Unzips the disunity_v zipfile into a directory named disunity
    """
    files = os.listdir(dir_of_this_py_file())
    disunity_zip = _find_first_match("disunity.+\.zip", files)
    if disunity_zip is None:
        raise IOError("cannot find disunity zipfile @ " + disunity_zip)
    else:
        with zipfile.ZipFile(disunity_zip, "r") as z:
            z.extractall(to_dir)
