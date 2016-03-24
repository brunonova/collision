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

from cocos.director import director
from cocos.menu import EntryMenuItem, MenuItem, shake, shake_back
from cocos.scene import Scene
from gettext import gettext as _

from ..options import Options
from ..scores import Scores
from ..util import CustomizedMenu, ScreenshotLayer


class GameOverScene(Scene):
	"""The Game Over menu scene."""
	def __init__(self, score, balls, options: Options, highScores: Scores):
		super().__init__(ScreenshotLayer(), GameOverLayer(score, balls, options, highScores))


class GameOverLayer(CustomizedMenu):
	"""Layer that shows the Game Over screen."""
	def __init__(self, score, balls, options, highScores):
		super().__init__(_("High score!"))
		self.score = score
		self.balls = balls
		self.options = options
		self.highScores = highScores
		self.name = ""

		items = [
			EntryMenuItem(_("Your name: "), self.onName, self.name, max_length=15),
			MenuItem(_("OK"), self.onOk),
		]
		self.create_menu(items, shake(), shake_back())

	def onName(self, value):
		self.name = value

	def onOk(self):
		# Add the high score if the name is not empty
		if len(self.name) > 0:
			self.highScores.addHighScore(self.options.type, self.options.difficulty,
			                             self.name, self.score)
		self.on_quit()

	def on_quit(self):
		# Pop 2 scenes (the current Game Over scene and the Game scene)
		director.pop()
		director.pop()
