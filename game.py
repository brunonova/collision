from cocos.actions import FadeOut, CallFunc, FadeIn, Repeat
from cocos.collision_model import CollisionManagerGrid
from cocos.director import director
from cocos.euclid import Vector2
from cocos.layer import Layer, ColorLayer
from cocos.scene import Scene
from cocos.text import Label
from gettext import gettext as _
from pyglet import window

import constants
from balls import *


class GameScene(Scene):
	"""The scene that runs the actual game."""
	def __init__(self, options):
		"""
		Creates the scene.

		@param options: game options (a dictionary).
		"""
		gameLayer = GameLayer(options)
		hudLayer = HUDLayer(gameLayer)
		super().__init__(gameLayer, hudLayer)


class HUDLayer(Layer):
	"""Layer that shows the HUD."""
	def __init__(self, gameLayer):
		super().__init__()
		self.gameLayer = gameLayer
		self.time = 0

		# Time/coins label
		self.score = Label(font_name="Ubuntu", font_size=16, color=constants.FONT_COLOR,
		                   anchor_x="left", anchor_y="bottom")
		self.score.position = 10, 0
		self.add(self.score)

		# Enemy ball count label
		self.enemies = Label(font_name="Ubuntu", font_size=16, color=constants.FONT_COLOR,
		                     anchor_x="right", anchor_y="bottom")
		self.enemies.position = director.get_window_size()[0] - 10, 0
		self.add(self.enemies)

		self.schedule(self.update)

	def update(self, dt):
		if not self.gameLayer.isGameOver:
			if self.gameLayer.options["type"] == constants.TIME:
				self.time += dt
				self.score.element.text = _("Time: {}").format(int(self.time))
			else:
				self.score.element.text = _("Coins: {}").format(self.gameLayer.coins)
			self.enemies.element.text = _("Balls: {}").format(self.gameLayer.getNumberOfEnemies())


class GameLayer(ColorLayer):
	"""Layer that shows and controls the actual game."""
	is_event_handler = True

	def __init__(self, options):
		"""
		Creates the layer.

		@param options: game options (a dictionary).
		"""
		super().__init__(*constants.BACKGROUND_COLOR)

		self.options = options
		self.keysPressed = set()
		self.enemies = []
		self.isGameOver = False
		self.coins = 0
		self.mouseDelta = Vector2(0, 0)

		# Interval between enemy balls additions (depends on difficulty)
		self.intervalAddEnemy = (20, 15, 10)[self.options["difficulty"]]
		self.timerAddEnemy = 0

		# Create player ball
		width, height = director.get_window_size()
		self.player = Player(width // 2, height // 2)
		self.add(self.player)

		# Create enemy balls
		for x in range(3):
			self.addEnemy()

		if self.options["type"] == constants.COINS:
			# Create coin
			self.coin = Coin(self.player.x, self.player.y)
			self.add(self.coin, z=0.1)

		self.collMan = CollisionManagerGrid(0, 0, self.width, self.height, 30, 30)
		self.schedule(self.update)

	def on_enter(self):
		super().on_enter()
		director.window.set_exclusive_mouse(True)  # "grab" the mouse

	def on_exit(self):
		super().on_exit()
		director.window.set_exclusive_mouse(False)  # "free" the mouse

	def addEnemy(self):
		"""
		Adds a new enemy ball.

		@return: the added ball.
		"""
		# Ball speed depends on difficulty
		speed = (200, 350, 500)[self.options["difficulty"]]
		enemy = Enemy(self.player.x, self.player.y, speed)
		self.enemies.append(enemy)
		self.add(enemy)
		return enemy

	def gameOver(self):
		self.isGameOver = True

		# Fade out player ball and exit scene when done
		self.player.do((FadeOut(2)) + CallFunc(lambda: director.pop()))

		# Stop actions of enemy balls
		for enemy in self.enemies:
			enemy.stop()

	def getNumberOfEnemies(self):
		"""Returns the number of enemy balls."""
		return len(self.enemies)

	def pauseGame(self):
		"""Pauses or unpauses the game."""
		if not self.isGameOver:
			director.push(Scene(PauseLayer()))

	def update(self, dt):
		if not self.isGameOver:
			self.collMan.clear()

			# Update player ball
			self.player.update(dt, self.mouseDelta, self.keysPressed)
			self.mouseDelta = Vector2(0, 0)
			self.collMan.add(self.player)

			# Update enemy balls
			for enemy in self.enemies:
				enemy.update(dt)
				if enemy.enabled:
					self.collMan.add(enemy)

			# Check collision between player and coin
			if self.options["type"] == constants.COINS and self.coin.enabled:
				self.collMan.add(self.coin)
				if self.collMan.they_collide(self.player, self.coin):
					self.coins += 1
					# Move the coin to a random position
					self.coin.setRandomPosition(self.player.x, self.player.y,
					                            Coin.PLAYER_DISTANCE)
					# Add an enemy every 4/6/8 coins (depends on difficulty)
					if self.coins % (8, 6, 4)[self.options["difficulty"]] == 0:
						self.addEnemy()

			# Check collisions between player and enemies
			for enemy in self.enemies:
				if enemy.enabled and self.collMan.they_collide(self.player, enemy):
					self.gameOver()

			# Check collisions between enemies
			if self.options["ballsCollide"]:
				for i, enemy in enumerate(self.enemies):
					for j, other in enumerate(self.enemies):
						if j > i and enemy.enabled and other.enabled \
						   and self.collMan.they_collide(enemy, other):
							Enemy.bounceBalls(enemy, other)

			if self.options["type"] == constants.TIME:
				# Add new enemy every "intervalAddEnemy" seconds
				self.timerAddEnemy += dt
				if self.timerAddEnemy >= self.intervalAddEnemy:
					self.timerAddEnemy -= self.intervalAddEnemy
					self.addEnemy()

	def on_key_press(self, key, modifiers):
		self.keysPressed.add(key)
		if key in (window.key.P, window.key.PAUSE):
			self.pauseGame()

	def on_key_release(self, key, modifiers):
		if key in self.keysPressed:
			self.keysPressed.remove(key)

	def on_mouse_motion(self, x, y, dx, dy):
		self.mouseDelta += Vector2(dx, dy)


class PauseLayer(ColorLayer):
	"""Layer that shows "PAUSE"."""
	is_event_handler = True

	def __init__(self):
		super().__init__(*constants.BACKGROUND_COLOR)

		width, height = director.get_window_size()
		paused = Label(_("PAUSE"), font_name="Ubuntu", font_size=64, bold=True,
		               color=constants.FONT_COLOR, anchor_x="center", anchor_y="center")
		paused.position = width // 2, height // 2
		paused.do(Repeat(FadeOut(0.3) + FadeIn(0.3)))
		self.add(paused)

	def on_key_press(self, key, modifiers):
		if key in (window.key.P, window.key.PAUSE):
			director.pop()
