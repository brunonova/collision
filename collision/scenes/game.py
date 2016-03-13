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

from ..balls import Bonus
from ..timer import Timer
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
		self.timers = dict()
		if self.options.isTime():
			# Timer to add new enemy
			self.timers["addEnemy"] = Timer(options.getIntervalAddEnemy(),
			                                callback=self.onAddEnemyTimer)
		if self.options.bonuses:
			# Timers related to bonuses
			self.timers["showBonus"] = Timer(random.randint(3, 10),
			                                 callback=self.onShowBonusTimer,
			                                 cond=lambda: not self.bonus.enabled,
											 min_=3, max_=10)
			self.timers["speedDown"] = Timer()
			self.timers["speedUp"] = Timer()

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

		# Select the bonus
		bonus = random.randint(0, 1)
		if bonus == 0:
			self.timers["speedUp"].time = 0
			self.timers["speedDown"].time = 6
		else:
			self.timers["speedDown"].time = 0
			self.timers["speedUp"].time = 3

	def isSpeedDown(self):
		return self.options.bonuses and self.timers["speedDown"].time > 0

	def isSpeedUp(self):
		return self.options.bonuses and self.timers["speedUp"].time > 0

	def onAddEnemyTimer(self, timer):
		timer.time += self.options.getIntervalAddEnemy()
		self.addEnemy()

	def onShowBonusTimer(self, timer, min_, max_):
		timer.time = random.randint(min_, max_)
		self.bonus.show(self.player.x, self.player.y)

	def update(self, dt):
		if not self.isGameOver:
			self.collMan.clear()

			# Update player ball
			self.player.update(dt, self.mouseDelta, self.keysPressed)
			self.mouseDelta = Vector2(0, 0)
			self.collMan.add(self.player)

			# Update enemy balls
			factor = 0.5 if self.isSpeedDown() else 1.5 if self.isSpeedUp() else 1.0
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

			# Update timers
			for timer in self.timers.values():
				timer.update(dt)

	def on_key_press(self, key, modifiers):
		self.keysPressed.add(key)
		if key in (window.key.P, window.key.PAUSE):
			self.pauseGame()

	def on_key_release(self, key, modifiers):
		if key in self.keysPressed:
			self.keysPressed.remove(key)

	def on_mouse_motion(self, x, y, dx, dy):
		self.mouseDelta += Vector2(dx, dy)
