import re
import os
import zipfile
import subprocess
import tempfile
from pkg_resources import resource_filename


def disunity(commands, filename):
    """Runs disunity commands on the given filename
    filename should be the absolute path to a unity3d file
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        disunity_jar_loc = os.path.join(tmp_dir, "disunity.jar")
        _unzip_disunity(tmp_dir)
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
    disunity_zip = resource_filename(__name__, 'data/disunity_v0.3.4.zip')
    if disunity_zip is None:
        raise IOError("cannot find disunity zipfile @ " + disunity_zip)
    else:
        with zipfile.ZipFile(disunity_zip, "r") as z:
            z.extractall(to_dir)
