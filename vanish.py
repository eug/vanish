#!/bin/env python


import json
from shutil import rmtree
from glob import glob
from os import remove, listdir
from os.path import isfile, join, expandvars, expanduser

def is_valid_json(json):
	""" Checks if the json file is correct """

	isvalid = True

	for program, value in json.items():

		if not program:
			print("[ERROR] Missing program name for: " + value)

		for name in value:
			
			if not 'active' in value[name]:
				isvalid = False
				print("[ERROR] Missing 'active' attribute for '" + name + "'")

			if not 'path' in value[name]:
				isvalid = False
				print("[ERROR] Missing 'path' attribute for '" + name + "'")

			if not 'description' in value[name]:
				print("[WARNING] Missing 'description' attribute for '" + name + "'")

	return isvalid


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

	for program, value in json.items():
		
		for name in value:

			active = value[name]['active']
			path   = value[name]['path']
			path   = expanduser(path)
			path   = expandvars(path)

			if not active: continue

			for f in glob(path):
				print("Removing '" + f + "'")
				rm_content(f)


if __name__ == '__main__':
	
	with open("default.json") as default:
		
		json = json.load(default)

		if is_valid_json(json):
			do_clean(json)
