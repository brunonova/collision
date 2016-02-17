#!/usr/bin/env python3
import gettext, os, pyglet
from cocos.director import director

from menu import MenuScene


if __name__ == "__main__":
	# Find directory path
	path = os.path.dirname(os.path.abspath(__file__))

	# Setup gettext
	gettext.bindtextdomain("collision", os.path.join(path, "mo"))
	gettext.textdomain("collision")

	# Setup resource paths
	pyglet.resource.path.append(os.path.join(path, "res"))
	pyglet.resource.reindex()
	pyglet.font.add_directory(os.path.join(path, "res"))

	# Start game
	director.init(caption="Collision", width=600, height=600)
	# TODO: remove default handler
	director.run(MenuScene())
