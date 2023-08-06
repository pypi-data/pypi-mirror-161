# -*- coding: utf-8 -*-

import os
import re
import sys

from werkzeug import utils

try:
    from os import scandir
except:
    from scandir import scandir


def to_unicode_str(s):
    if sys.version_info < (3, 4) and not isinstance(s, unicode):
        if isinstance(s, str):
            try:
                s = s.decode('utf-8')
            except:
                s = s.decode('gbk')
        else:
            s = unicode(s)
    elif sys.version_info >= (3, 4) and not isinstance(s, str):
        s = str(s)
    return s


def url_path_to_local_abspath(path):
    # path = path.split('?', 1)[0]  # char `#` and `?` in path is a part of file not
    # path = path.split('#', 1)[0]  # special char of url_encode
    if path == '':
        path = '.'
    return normalize_path(os.path.abspath(path))


def normalize_path(path):
    p = os.path.normpath(path)
    if os.sep == '\\':
        p = p.replace('\\', '/')
    p = p.rstrip('/')
    return to_unicode_str(p)


def parents_path(path):
    """
    :param path:
    :return: return parents_path which does not contain the end '/', that is remove the end '/'
    """
    res = set()
    path = normalize_path(path)
    while '/' in path:
        sep_ind = path.rindex('/')
        res.add(path[:sep_ind])
        path = path[:sep_ind]
    if path.startswith('./') or not path.startswith('.'):
        res.add('.')
    return res


def parent_path(path):
    """
    :param path:
    :return: return path which does not contain the end '/'
    """
    path = normalize_path(path)
    if '/' not in path:
        return '.'
    else:
        sep_ind = path.rindex('/')
        return path[:sep_ind]


def get_filename(path):
    path = normalize_path(path)
    if '/' in path:
        sep_ind = path.rindex('/')
        return path[sep_ind + 1:]
    else:
        return path


def get_suffix(path):
    if '.' in path:
        return path[path.rindex('.') + 1:]
    else:
        return ''


def is_child(child_path, parent_path):
    nc = normalize_path(child_path)
    np = normalize_path(parent_path)
    if len(nc) > len(np) and nc.startswith(np + '/'):
        return True
    return False


def listdir(path):
    return scandir(to_unicode_str(path))


_filename_ascii_strip_re = re.compile(r"[^A-Za-z0-9_.-]")
_filename_ascii_add_strip_re = re.compile(r'[^A-Za-z0-9_\u4E00-\u9FBF\u3040-\u30FF\u31F0-\u31FF.-]')
_windows_device_files = (
    "CON",
    "AUX",
    "COM1",
    "COM2",
    "COM3",
    "COM4",
    "LPT1",
    "LPT2",
    "LPT3",
    "PRN",
    "NUL",
)
PY2 = sys.version_info[0] == 2
if PY2:
    text_type = unicode
else:
    text_type = str


def secure_filename(filename):
    r"""Pass it a filename and it will return a secure version of it.  This
    filename can then safely be stored on a regular file system and passed
    to :func:`os.path.join`.


    On windows systems the function also makes sure that the file is not
    named after one of the special device files.

    >>> secure_filename("My cool movie.mov")
    'My_cool_movie.mov'
    >>> secure_filename("../../../etc/passwd")
    'etc_passwd'
    >>> secure_filename(u'i contain cool \xfcml\xe4uts.txt')
    'i_contain_cool_umlauts.txt'

    The function might return an empty filename.  It's your responsibility
    to ensure that the filename is unique and that you abort or
    generate a random filename if the function returned an empty one.

    .. versionadded:: 0.5

    :param filename: the filename to secure
    """
    if isinstance(filename, text_type):
        from unicodedata import normalize

        filename = normalize("NFKD", filename).encode("utf-8", "ignore")
        if not PY2:
            filename = filename.decode("utf-8")
    for sep in os.path.sep, os.path.altsep:
        if sep:
            filename = filename.replace(sep, " ")

    filename = to_unicode_str(_filename_ascii_add_strip_re.sub('', '_'.join(
        filename.split()))).strip('._')
    # filename = str(_filename_ascii_strip_re.sub("", "_".join(filename.split()))).strip(
    #     "._"
    # )

    # on nt a couple of special files are present in each folder.  We
    # have to ensure that the target file is not such a filename.  In
    # this case we prepend an underline
    if (
            os.name == "nt"
            and filename
            and filename.split(".")[0].upper() in _windows_device_files
    ):
        filename = "_" + filename

    return filename


if __name__ == '__main__':
    print(os.getcwd())
