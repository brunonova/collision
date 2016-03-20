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

import configparser, os, sys
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
		self._readConfig()  # Read the config file

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

	@staticmethod
	def getUserConfigFolder():
		"""Returns the path to the user's .config or AppData/Local folder."""
		home = os.environ["HOME"]
		if sys.platform == "win32":  # Windows
			return os.path.join(home, "AppData", "Local", "collision")
		else:  # Linux or other
			return os.path.join(home, ".config", "collision")

	@property
	def type(self):
		value = self._config.getint("Options", "type", fallback=Options.TIME)
		# Ensure the value is valid
		return value if 0 <= value < len(Options.TYPE_NAMES) else Options.TIME

	@type.setter
	def type(self, value):
		self._config["Options"]["type"] = str(value)
		self._saveConfig()

	@property
	def difficulty(self):
		value = self._config.getint("Options", "difficulty", fallback=Options.MEDIUM)
		# Ensure the value is valid
		return value if 0 <= value < len(Options.DIFFICULTY_NAMES) else Options.MEDIUM

	@difficulty.setter
	def difficulty(self, value):
		self._config["Options"]["difficulty"] = str(value)
		self._saveConfig()

	@property
	def fullscreen(self):
		return self._config.getboolean("Options", "fullscreen", fallback=False)

	@fullscreen.setter
	def fullscreen(self, value):
		self._config["Options"]["fullscreen"] = "yes" if value else "no"
		self._saveConfig()

	@property
	def ballsCollide(self):
		return True

	@property
	def bonuses(self):
		return True

	def _readConfig(self):
		self._config = configparser.ConfigParser()
		self._configDir = Options.getUserConfigFolder()
		self._configFilename = os.path.join(self._configDir, "options.ini")
		self._config.read(self._configFilename)

		# Create the Options section if it doesn't exist
		if not "Options" in self._config.sections():
			self._config["Options"] = {}

	def _saveConfig(self):
		os.makedirs(self._configDir, exist_ok=True)
		with open(self._configFilename, "w") as file:
			self._config.write(file)
