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
from cocos.text import Label
from gettext import gettext as _

from .game import GameScene
from .highScores import HighScoresScene
from ..options import Options
from ..util import CustomizedMenu, MultiMenuItem


class MenuScene(Scene):
	"""The scene that displays the main menu."""
	def __init__(self):
		menuLayer = MenuLayer()
		optionsLayer = OptionsLayer(menuLayer)
		super().__init__(BackgroundLayer(),
						 MultiplexLayer(menuLayer, optionsLayer))


class BackgroundLayer(ColorLayer):
	"""Layer that displays the version of the game."""
	def __init__(self):
		super().__init__(*Options.BACKGROUND_COLOR)

		version = Label(font_name=Options.FONT_NAME, font_size=16,
		                color=Options.FONT_COLOR_NOT_SELECTED,
		                anchor_x="right", anchor_y="bottom")
		version.position = director.get_window_size()[0] - 5, 5
		version.element.text = _("Version: {}").format(Options.VERSION)
		self.add(version)


class MenuLayer(CustomizedMenu):
	"""Layer that displays the menu."""
	def __init__(self):
		super().__init__("Collision")

		# Initialize game options
		self.options = Options()
		if self.options.fullscreen: director.window.set_fullscreen(True)

		# Add the items and create the menu
		items = [
			MenuItem(_("Play"), self.onPlay),
			MenuItem(_("Options"), self.onOptions),
			MenuItem(_("High Scores"), self.onHighScores),
			MenuItem(_("Quit"), self.on_quit),
		]
		self.create_menu(items, shake(), shake_back())

	def onPlay(self):
		director.push(GameScene(self.options))

	def onOptions(self):
		self.parent.switch_to(1)

	def onHighScores(self):
		director.push(HighScoresScene(self.options))

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
			               self.menuLayer.options.fullscreen),
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
		self.menuLayer.options.fullscreen = value
		director.window.set_fullscreen(value)

	def on_quit(self):
		self.parent.switch_to(0)
