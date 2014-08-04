#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
from glob import glob
from shutil import rmtree
from os import remove, listdir, access
from os.path import isfile, join, expandvars, expanduser, dirname, realpath


logging.basicConfig(format='%(levelname)s:%(name)s: %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.ERROR)

_CLEANERS_DIR = dirname(realpath(__file__)) + "/cleaners"

_IGNORE_FILE = "ignore.json"

_JSON_IGNORE = 'Ignore'
_JSON_ACTIVE = 'active'
_JSON_PATH = 'path'
_JSON_DESCR = 'decription'


def expand(path):
    return expandvars(expanduser(path))


def can_delete(path):
    return access(path, os.W_OK)


def is_valid_json(json):
    """ Checks if a cleaner or ignore file is valid """

    if _JSON_IGNORE in list(json.keys()):
        return is_valid_ignore(json)
    else:
        return is_valid_cleaner(json)


def is_valid_ignore(json):
    """ Checks if an ignore file is valid """

    for ignore in get_ignore_set():
        if not exists(join(_CLEANERS_DIR, ignore)):
            log.error("No such file '%s'", ignore)
            return False
    return True


def is_valid_cleaner(json):
    """ Checks if a cleaner file is valid """

    isvalid = True

    for program, option in json.items():

        if not program:
            log.critical("Missing program name in '%s'", option)

        for name in option:

            if not _JSON_ACTIVE in option[name]:
                isvalid = False
                log.error("'%s':'%s' is missing 'Active' attribute", program, name)

            if not _JSON_PATH in option[name]:
                isvalid = False
                log.error("'%s':'%s' is missing 'Path' attribute", program, name)

            if not _JSON_DESCR in option[name]:
                log.warning("'%s':'%s' is missing 'Description' attribute", program, name)

    return isvalid


def rm_content(path):
    """ Remove file or direcotry content """

    if isfile(path):
        rm_content_file(path)
    else:
        rm_content_dir(path)


def rm_content_file(path):
    if can_delete(path):
        remove(path)
        log.info("'%s' removed '%s'", name, f)
    else:
        log.error("Permission denied '%s'", path)


def rm_content_dir(path):
    try:
        for f in listdir(path):

            try:
                file_path = join(path, f)

                if isfile(file_path):
                    remove(file_path)
                else:
                    rmtree(file_path)

                log.info("'%s' removed '%s'", name, f)
            except PermissionError:
                log.error("Permission denied '%s'", f)

    except FileNotFoundError:
        log.error("No such file or directory '%s'", path)


def get_cleaners_set():
    return set(listdir(_CLEANERS_DIR))


def get_ignore_set():
    ignore = []
    with open(join(_CLEANERS_DIR, _IGNORE_FILE)) as f:
        data = json.load(f)
        ignore = data[_JSON_IGNORE]
    return set(ignore)


def do_clean(json):
    """ Traverse through json file removing files/directories """

    for program, option in json.items():

        for name in option:

            active = option[name][_JSON_ACTIVE]
            paths = option[name][_JSON_PATH]

            if not active:
                continue

            log.info("Cleaning '%s' files", name)

            if isinstance(paths, list):
                paths = [expand(path) for path in paths]
            else:
                paths = [expand(paths)]

            for path in paths:
                for f in glob(path):
                    rm_content(f)


if __name__ == '__main__':

    cleaners = get_cleaners_set() - get_ignore_set()

    for cleaner in cleaners:
        with open(join(_CLEANERS_DIR, cleaner)) as f:

            data = json.load(f)

            if is_valid_json(data):
                do_clean(data)
            else:
                log.error("Invalid file format '%s'", f.name)
