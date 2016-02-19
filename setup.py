#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
	name = "Collision",
	version = "0.0.1",
	author = "Bruno Nova",
	author_email = "brunomb.nova@gmail.com",
	description = "A game where you control a ball while dodging the others for as long as possible",
	#license = "?",
	keywords = "game",
	#url = "?",

	packages = find_packages(),
	package_data = {"collision": ["res/*", "mo/*/*/*.mo"]},
	scripts = ["bin/collision"],
	install_requires = ["cocos2d"]
)
