#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
from shutil import rmtree
from glob import glob
from os import remove, listdir
from os.path import isfile, join, expandvars, expanduser


def is_valid_json(json):
    """ Checks if the json file is correct """

    isvalid = True

    for program, option in json.items():

        if not program:
            print("[ERROR] Missing program name for: " + option)

        for name in option:

            if not 'active' in option[name]:
                isvalid = False
                print("[ERROR] Missing 'active' attribute for '" + name + "'")

            if not 'path' in option[name]:
                isvalid = False
                print("[ERROR] Missing 'path' attribute for '" + name + "'")

            if not 'description' in option[name]:
                print("[WARNING] Missing 'description' attribute for '" + name + "'")

    return isvalid


def expand(path):
    return expandvars(expanduser(path))


def rm_content(path):
    """ Remove file or direcotry content """

    if isfile(path):
        remove(path)
    else:
        for f in listdir(path):

            file_path = join(path, f)

            if isfile(file_path):
                remove(file_path)
            else:
                rmtree(file_path)


def do_clean(json):
    """ Traverse through json file removing files/directories """

    for program, option in json.items():

        for name in option:

            active = option[name]['active']
            paths = option[name]['path']

            if not active:
                continue

            if isinstance(paths, list):
                paths = [expand(path) for path in paths]
            else:
                paths = [expand(paths)]

            for path in paths:
                for f in glob(path):
                    print("Removing '" + f + "'")
                    rm_content(f)


if __name__ == '__main__':    

    cleaners_dir = 'cleaners'

    for cleaner in listdir(cleaners_dir):
        with open(join(cleaners_dir, cleaner)) as f:
            data = json.load(f)
            if is_valid_json(data):
                do_clean(data)
