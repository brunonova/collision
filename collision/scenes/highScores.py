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
from cocos.layer import ColorLayer, Layer
from cocos.menu import MenuItem, shake, shake_back, fixedPositionMenuLayout
from cocos.scene import Scene
from gettext import gettext as _

from cocos.text import Label

from ..options import Options
from ..scores import Scores
from ..util import CustomizedMenu, MultiMenuItem


class HighScoresScene(Scene):
	"""The scene that displays the high scores table."""
	def __init__(self, options: Options):
		"""
		Creates the scene.

		@param options: game options.
		"""
		scoresLayer = ScoresLayer()
		super().__init__(ColorLayer(*Options.BACKGROUND_COLOR),
		                 scoresLayer,
		                 MenuLayer(options, scoresLayer))


class MenuLayer(CustomizedMenu):
	"""Layer that shows the menu of the scene."""
	def __init__(self, options, scoresLayer):
		"""
		Creates the layer.

		@param options: game options.
		@param scoresLayer: the Scores layer.
		"""
		super().__init__(_("High Scores"))
		self.options = options
		self.type = self.options.type
		self.difficulty = self.options.difficulty
		self.scoresLayer = scoresLayer
		self.scores = Scores()

		# Create the items
		items = [
			MultiMenuItem(_("Type: "), self.onType,
			              [_("Time"), _("Coins")], self.type),
			MultiMenuItem(_("Difficulty: "), self.onDifficulty,
			              [_("Easy"), _("Medium"), _("Hard")], self.difficulty),
			MenuItem(_("< Back"), self.on_quit),
		]

		# Define the positions of the items
		width, height = director.get_window_size()
		positions = [
			(width // 2, height - 100),
			(width // 2, height - 150),
			(width // 2, 80),
		]

		# Create the menu
		self.create_menu(items, shake(), shake_back(),
		                 layout_strategy=fixedPositionMenuLayout(positions))

		# Update the scores in the Scores Layer
		self._updateScores()

	def onType(self, index):
		self.type = index
		self._updateScores()

	def onDifficulty(self, index):
		self.difficulty = index
		self._updateScores()

	def on_quit(self):
		director.pop()

	def _updateScores(self):
		self.scoresLayer.updateScores(self.scores.getHighScores(self.type, self.difficulty),
		                              self.type)


class ScoresLayer(Layer):
	"""The layer that displays the high scores table."""
	def __init__(self):
		super().__init__()
		width, height = director.get_window_size()
		left = 10
		right = width - 10
		top = height - 240
		padding = 40

		# Add header labels
		self.nameHeader = _makeLabel(_("Name:"), left, top, bold=True)
		self.add(self.nameHeader)
		self.scoreHeader = _makeLabel(_("Time:"), right, top, "right", bold=True)
		self.add(self.scoreHeader)

		# Add scores labels
		self.names = []
		self.scores = []
		for i in range(Scores.MAX_HIGH_SCORES):
			y = top - padding * (i + 1)
			self.names.append(_makeLabel("-", left, y))
			self.add(self.names[i])
			self.scores.append(_makeLabel("-", right, y, "right"))
			self.add(self.scores[i])

	def updateScores(self, scores, type):
		"""
		Updates the scores table.

		@param scores: list of high scores for the current type and difficulty.
		@param type: currently selected type of game.
		"""
		size = len(scores)

		self.scoreHeader.element.text = _("Time:") if type == Options.TIME else _("Coins:")

		for i in range(Scores.MAX_HIGH_SCORES):
			if i >= size:
				self.names[i].element.text = "-"
				self.scores[i].element.text = "-"
			else:
				self.names[i].element.text = scores[i]["name"]
				self.scores[i].element.text = str(scores[i]["score"])


def _makeLabel(text, x, y, anchorX="left", anchorY="center", bold=False):
	lbl =  Label(font_name=Options.FONT_NAME, font_size=20,
	             color=Options.FONT_COLOR, bold=bold,
	             anchor_x=anchorX, anchor_y=anchorY)
	lbl.position = x, y
	lbl.element.text = text
	return lbl
