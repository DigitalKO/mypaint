# This file is part of MyPaint.
# Copyright (C) 2015 by Andrew Chadwick <a.t.chadwick@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.


"""Pythonic wrappers for some standard GLib routines.

MyPaint is strict about using Unicode internally for everything, but
when GLib returns a filename, all hell can break loose (the data isn't
unicode, and may not even be UTF-8). This module works around that.

"""


## Imports

import sys
from logging import getLogger
logger = getLogger(__name__)

from gi.repository import GLib


## File path getter functions


def filename_to_unicode(opsysstring):
    """Converts a str representing a filename from GLib to unicode.

    :param str opsysstring: a string in the (GLib) encoding for filenames
    :returns: the converted filename
    :rtype: unicode

    >>> from gi.repository import GLib
    >>> filename_to_unicode('/ascii/only/path')
    u'/ascii/only/path'
    >>> filename_to_unicode(None) is None
    True

    This is just a more Pythonic wrapper around g_filename_to_utf8() for
    now. If there are compatibility reasons to change it, fallbacks
    involving sys.getfilesystemencoding exist.

    """
    if opsysstring is None:
        return None
    # On Windows, they're always UTF-8 regardless.
    if sys.platform == "win32":
        return opsysstring.decode("utf-8")
    # Other systems are dependent in opaque ways on the environment.
    if not isinstance(opsysstring, str):
        raise TypeError("Argument must be bytes")
    ustring = GLib.filename_to_utf8(opsysstring, -1, 0, 0)
    if ustring is None:
        raise UnicodeDecodeError(
            "GLib failed to convert %r to a UTF-8 string. "
            "Consider setting G_FILENAME_ENCODING if your file system's "
            "filename encoding scheme is not UTF-8."
            % (opsysstring,)
        )
    return ustring.decode("utf-8")


def get_user_config_dir():
    """Like g_get_user_config_dir(), but always unicode"""
    d_fs = GLib.get_user_config_dir()
    return filename_to_unicode(d_fs)


def get_user_data_dir():
    """Like g_get_user_data_dir(), but always unicode"""
    d_fs = GLib.get_user_data_dir()
    return filename_to_unicode(d_fs)


def get_user_cache_dir():
    """Like g_get_user_cache_dir(), but always unicode"""
    d_fs = GLib.get_user_cache_dir()
    return filename_to_unicode(d_fs)


def get_user_special_dir(d_id):
    """Like g_get_user_special_dir(), but always unicode"""
    d_fs = GLib.get_user_special_dir(d_id)
    return filename_to_unicode(d_fs)


## First-import cache forcing

def init_user_dir_caches():
    """Caches the GLib user directories

    >>> init_user_dir_caches()

    The first time this module is imported is from a particular point in
    the launch script, after all the i18n setup is done and before
    lib.mypaintlib is imported. If they're not cached up-front in this
    manner, get_user_config_dir() & friends may return literal "?"s in
    place of non-ASCII characters (Windows systems with non-ASCII user
    profile dirs are known to trigger this).

    The debugging prints may be useful too.

    """
    logger.debug("Init g_get_user_config_dir(): %r", get_user_config_dir())
    logger.debug("Init g_get_user_data_dir(): %r", get_user_data_dir())
    logger.debug("Init g_get_user_cache_dir(): %r", get_user_cache_dir())
    # It doesn't matter if some of these are None
    for i in range(GLib.UserDirectory.N_DIRECTORIES):
        k = GLib.UserDirectory(i)
        logger.debug(
            "Init g_get_user_special_dir(%s): %r",
            k.value_name,
            get_user_special_dir(k),
        )

## Module testing

def _test():
    import doctest
    doctest.testmod()


if __name__ == '__main__':
    _test()
