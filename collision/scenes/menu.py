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

import pyglet
from cocos.director import director
from cocos.layer import ColorLayer, MultiplexLayer
from cocos.menu import MenuItem, ToggleMenuItem, MultipleMenuItem, \
     shake, shake_back
from cocos.scene import Scene
from gettext import gettext as _
from pyglet.window import key

from ..util import CustomizedMenu
from ..options import Options
from .game import GameScene


class MenuScene(Scene):
	"""The scene that displays the main menu."""
	def __init__(self):
		menuLayer = MenuLayer()
		optionsLayer = OptionsLayer(menuLayer)
		super().__init__(ColorLayer(*Options.BACKGROUND_COLOR),
						 MultiplexLayer(menuLayer, optionsLayer))


class MenuLayer(CustomizedMenu):
	"""Layer that displays the menu."""
	def __init__(self):
		super().__init__("Collision")

		# Initialize game options
		self.options = Options()

		# Add the items and create the menu
		items = [
			MenuItem(_("Play"), self.onPlay),
			MenuItem(_("Options"), self.onOptions),
			MenuItem(_("Quit"), self.on_quit),
		]
		self.create_menu(items, shake(), shake_back())

	def onPlay(self):
		director.push(GameScene(self.options))

	def onOptions(self):
		self.parent.switch_to(1)

	def on_enter(self):
		super().on_enter()
		director.window.set_exclusive_mouse(False)  # ensure cursor is available

	def on_quit(self):
		pyglet.app.exit()


class OptionsLayer(CustomizedMenu):
	"""Layer that display an options menu."""

	def __init__(self, menuLayer):
		super().__init__(_("Options"))
		self.menuLayer = menuLayer

		# Add the items and create the menu
		items = [
			MultiMenuItem(_("Type: "), self.onType,
			              [_("Time"), _("Coins")], self.menuLayer.options.type),
			MultiMenuItem(_("Difficulty: "), self.onDifficulty,
			              [_("Easy"), _("Medium"), _("Hard")],
			              self.menuLayer.options.difficulty),
			ToggleMenuItem(_("Full screen: "), self.onFullscreen,
			               director.window.fullscreen),
			MenuItem(_("< Back"), self.on_quit),
		]
		self.create_menu(items, shake(), shake_back())

	def onType(self, index):
		self.menuLayer.options.type = index

	def onDifficulty(self, index):
		self.menuLayer.options.difficulty = index

	def onBonuses(self, value):
		self.menuLayer.options.bonuses = value

	def onBallsCollide(self, value):
		self.menuLayer.options.ballsCollide = value

	def onFullscreen(self, value):
		director.window.set_fullscreen(value)

	def on_quit(self):
		self.parent.switch_to(0)


class MultiMenuItem(MultipleMenuItem):
	"""
	MultipleMenuItem that "wraps around" the list of item.

	This class is similar to MultipleMenuItem, except that:
	* Clicking or pressing RIGHT/ENTER on the last option selects the 1st item;
	* Clicking or pressing LEFT on the 1st item selects the last item.
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def on_key_press(self, symbol, modifiers):
		if symbol == key.LEFT and self.idx == 0:
			# Select the last item+1 so that the call to the parent's on_key_press
			# will select the last item
			self.idx = len(self.items)
		elif symbol in (key.RIGHT, key.ENTER) and self.idx == len(self.items) - 1:
			# Select the first item-1 so that the call to the parent's on_key_press
			# will select the first item
			self.idx = -1
		return super().on_key_press(symbol, modifiers)
