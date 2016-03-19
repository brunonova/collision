# Collision - A ball dodging game
# Copyright (C) 2016 Bruno Nova <brunomb.nova@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import gettext, os, pyglet
from cocos.director import director

from .scenes.menu import MenuScene


def startGame():
	"""Starts the game."""
	#TODO: set a window icon
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
	director.init(caption="Collision", width=600, height=600, resizable=True)
	# TODO: remove default handler
	#director.window.pop_handlers()
	director.run(MenuScene())
