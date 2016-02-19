from gettext import gettext as _


class Options:
	"""Holds the game options."""

	# Names of the multiple-choice options
	TYPE_NAMES = _("Time"), _("Coins")
	DIFFICULTY_NAMES = _("Easy"), _("Medium"), _("Hard")

	# Values of the multiple-choice options
	TIME, COINS = 0, 1
	EASY, MEDIUM, HARD = 0, 1, 2

	# Parameters that depend on difficulty
	INTERVAL_ADD_ENEMY = 20, 15, 10  # Interval between enemy balls additions
	ENEMY_SPEED = 200, 350, 500  # Initial enemy balls speed
	COINS_ADD_ENEMY = 8, 6, 4  # Coins needed to add a new enemy ball

	# Other constants
	BACKGROUND_COLOR = (192, 192, 192, 255)
	FONT_COLOR = (0, 0, 0, 255)
	FONT_COLOR_NOT_SELECTED = (92, 92, 92, 255)

	def __init__(self):
		self.type = Options.TIME
		self.difficulty = Options.MEDIUM
		self.ballsCollide = True

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
