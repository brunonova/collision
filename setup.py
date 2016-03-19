#!/usr/bin/env python3
import os
from setuptools import setup, find_packages

from collision.options import Options

# Find directory path
path = os.path.dirname(os.path.abspath(__file__))

# Read README.md file
with open(os.path.join(path, "README.md")) as f:
	longDescription = f.read()

setup(
	name = "Collision",
	version = Options.VERSION,
	author = "Bruno Nova",
	author_email = "brunomb.nova@gmail.com",
	description = "A ball dodging game",
	long_description = longDescription,
	license = "GPLv3",
	keywords = "game",
	url = "https://github.com/brunonova/collision",

	packages = find_packages(),
	package_data = {"collision": ["res/*", "mo/*/*/*.mo"]},
	scripts = ["bin/collision"],
	install_requires = ["cocos2d"],
)
