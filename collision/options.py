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

from gettext import gettext as _


class Options:
	"""Holds the game options."""
	# Game version
	VERSION = "0.0.1"

	# Names of the multiple-choice options
	TYPE_NAMES = _("Time"), _("Coins")
	DIFFICULTY_NAMES = _("Easy"), _("Medium"), _("Hard")

	# Values of the multiple-choice options
	TIME, COINS = 0, 1
	EASY, MEDIUM, HARD = 0, 1, 2

	# Parameters that depend on difficulty
	INTERVAL_ADD_ENEMY = 20, 15, 10  # Interval between enemy balls additions
	ENEMY_SPEED = 200, 300, 400  # Initial enemy balls speed
	COINS_ADD_ENEMY = 8, 6, 4  # Coins needed to add a new enemy ball

	# Other constants
	BACKGROUND_COLOR = (192, 192, 192, 255)
	FONT_COLOR = (0, 0, 0, 255)
	FONT_COLOR_NOT_SELECTED = (92, 92, 92, 255)
	FONT_NAME = "Ubuntu"

	def __init__(self):
		self.type = Options.TIME
		self.difficulty = Options.MEDIUM
		self.ballsCollide = True
		self.bonuses = True

	def isTime(self):
		return self.type == Options.TIME

	def isCoins(self):
		return self.type == Options.COINS

	def isEasy(self):
		return self.difficulty == Options.EASY

	def isMedium(self):
		return self.difficulty == Options.MEDIUM

	def isHard(self):
		return self.difficulty == Options.HARD

	def getIntervalAddEnemy(self):
		return Options.INTERVAL_ADD_ENEMY[self.difficulty]

	def getEnemySpeed(self):
		return Options.ENEMY_SPEED[self.difficulty]

	def getCoinsAddEnemy(self):
		return Options.COINS_ADD_ENEMY[self.difficulty]
