import random

from cocos.actions import FadeOut, CallFunc
from cocos.collision_model import CollisionManagerGrid
from cocos.director import director
from cocos.euclid import Vector2
from cocos.layer import Layer, ColorLayer
from cocos.scene import Scene
from cocos.text import Label
from gettext import gettext as _
from pyglet import window

from collision.balls import Bonus
from ..options import Options
from .pause import PauseScene
from ..balls import *


class GameScene(Scene):
	"""The scene that runs the actual game."""
	def __init__(self, options: Options):
		"""
		Creates the scene.

		@param options: game options.
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
		self.score = Label(font_name="Ubuntu", font_size=16, color=Options.FONT_COLOR,
		                   anchor_x="left", anchor_y="bottom")
		self.score.position = 10, 0
		self.add(self.score)

		# Enemy ball count label
		self.enemies = Label(font_name="Ubuntu", font_size=16, color=Options.FONT_COLOR,
		                     anchor_x="right", anchor_y="bottom")
		self.enemies.position = director.get_window_size()[0] - 10, 0
		self.add(self.enemies)

		self.schedule(self.update)

	def update(self, dt):
		if not self.gameLayer.isGameOver:
			if self.gameLayer.options.isTime():
				self.time += dt
				self.score.element.text = _("Time: {}").format(int(self.time))
			else:
				self.score.element.text = _("Coins: {}").format(self.gameLayer.coins)
			self.enemies.element.text = _("Balls: {}").format(self.gameLayer.getNumberOfEnemies())


class GameLayer(ColorLayer):
	"""Layer that shows and controls the actual game."""
	is_event_handler = True

	def __init__(self, options: Options):
		"""
		Creates the layer.

		@param options: game options.
		"""
		super().__init__(*Options.BACKGROUND_COLOR)

		self.options = options
		self.keysPressed = set()
		self.enemies = []
		self.isGameOver = False
		self.coins = 0
		self.mouseDelta = Vector2(0, 0)

		# Set timers (all timers count down)
		self.intervalAddEnemy = options.getIntervalAddEnemy()
		self.timerAddEnemy = self.intervalAddEnemy  # timer to add new enemy
		self.timerShowBonus = random.randint(3, 10)  # timer to show bonus
		self.timerSpeedDown = 0  # timer to stop the speed down bonus

		# Create player ball
		width, height = director.get_window_size()
		self.player = Player(width // 2, height // 2)
		self.add(self.player, z=0.3)

		# Create enemy balls
		for x in range(3):
			self.addEnemy()

		if self.options.isCoins():
			# Create coin
			self.coin = Coin(self.player.x, self.player.y)
			self.add(self.coin, z=0.2)

		if self.options.bonuses:
			# Create bonus
			self.bonus = Bonus()
			self.add(self.bonus, z=0.0)

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
		speed = self.options.getEnemySpeed()
		enemy = Enemy(self.player.x, self.player.y, speed)
		self.enemies.append(enemy)
		self.add(enemy, z=0.1)
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
		"""Pauses the game."""
		if not self.isGameOver:
			director.push(PauseScene.create())

	def giveBonus(self):
		"""Gives a random advantage or disadvantage to the player."""
		self.bonus.hide()
		self.timerSpeedDown = 8

	def isSpeedDown(self):
		return self.timerSpeedDown > 0

	def update(self, dt):
		if not self.isGameOver:
			self.collMan.clear()

			# Update player ball
			self.player.update(dt, self.mouseDelta, self.keysPressed)
			self.mouseDelta = Vector2(0, 0)
			self.collMan.add(self.player)

			# Update enemy balls
			factor = 0.5 if self.isSpeedDown() else 1.0
			for enemy in self.enemies:
				enemy.update(dt, factor)
				if enemy.enabled:
					self.collMan.add(enemy)

			# Check collision between player and coin
			if self.options.isCoins() and self.coin.enabled:
				self.collMan.add(self.coin)
				if self.collMan.they_collide(self.player, self.coin):
					self.coins += 1
					# Move the coin to a random position
					self.coin.setRandomPosition(self.player.x, self.player.y,
					                            Coin.PLAYER_DISTANCE)
					if self.coins % self.options.getCoinsAddEnemy() == 0:
						self.addEnemy()  # add an enemy every N coins

			# Check collision between player and bonus
			if self.options.bonuses and self.bonus.enabled:
				self.collMan.add(self.bonus)
				if self.collMan.they_collide(self.player, self.bonus):
					self.giveBonus()

			# Check collisions between player and enemies
			for enemy in self.enemies:
				if enemy.enabled and self.collMan.they_collide(self.player, enemy):
					self.gameOver()

			# Check collisions between enemies
			if self.options.ballsCollide:
				for i, enemy in enumerate(self.enemies):
					for j, other in enumerate(self.enemies):
						if j > i and enemy.enabled and other.enabled \
						   and self.collMan.they_collide(enemy, other):
							Enemy.bounceBalls(enemy, other)

			if self.options.bonuses and not self.bonus.enabled:
				# Count down time to add show the bonus
				self.timerShowBonus -= dt
				if self.timerShowBonus <= 0:
					self.timerShowBonus += random.randint(3, 10)
					self.bonus.show(self.player.x, self.player.y)

			if self.options.isTime():
				# Count time to add a new enemy ball
				self.timerAddEnemy -= dt
				if self.timerAddEnemy <= 0:
					self.timerAddEnemy += self.intervalAddEnemy
					self.addEnemy()

			# Count down bonus timers
			if self.timerSpeedDown > 0:
				self.timerSpeedDown -= dt

	def on_key_press(self, key, modifiers):
		self.keysPressed.add(key)
		if key in (window.key.P, window.key.PAUSE):
			self.pauseGame()

	def on_key_release(self, key, modifiers):
		if key in self.keysPressed:
			self.keysPressed.remove(key)

	def on_mouse_motion(self, x, y, dx, dy):
		self.mouseDelta += Vector2(dx, dy)
