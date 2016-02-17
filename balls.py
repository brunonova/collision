import random

import math
from cocos.actions import CallFunc
from cocos.actions import FadeIn
from cocos.collision_model import CircleShape
from cocos.director import director
from cocos.euclid import Vector2
from cocos.sprite import Sprite
from pyglet import window

import util


class Player(Sprite):
	"""The player ball."""
	SPEED = 400  # movement speed with the keyboard

	def __init__(self, x, y):
		"""
		Creates the player ball.

		@param x: initial x position of the ball.
		@param y: initial y position of the ball.
		"""
		super().__init__("player.png")
		self.radius = self.image.width // 2
		self.anchor = self.radius, self.radius
		self.position = x, y  # WARNING: position is a tuple, not a vector!
		self.enabled = True
		self.cshape = CircleShape(Vector2(self.x, self.y), self.radius)

	def update(self, dt, mouseDelta: Vector2, keysPressed):
		if self.enabled:
			# Move player according to mouse/keyboard
			self.position += mouseDelta
			self.position += Player._keyboardDelta(keysPressed) * Player.SPEED * dt

			# Check window borders
			if self.x < self.radius:
				self.x = self.radius
			elif self.x > director.window.width - self.radius:
				self.x = director.window.width - self.radius
			if self.y < self.radius:
				self.y = self.radius
			elif self.y > director.window.height - self.radius:
				self.y = director.window.height - self.radius

			self.cshape.center = Vector2(self.x, self.y)  # the center must be a Vector2!

	@staticmethod
	def _keyboardDelta(keysPressed):
		"""
		Returns a vector that points to the direction the arrow keys are pressed.

		Each coordinate of the vector will have the value -1, 0 or 1.

		@param keysPressed: the keys currently held down.
		@return: direction of the arraw keys pressed in the keyboard.
		"""
		delta = Vector2(0, 0)

		if window.key.LEFT in keysPressed:
			delta.x -= 1
		if window.key.RIGHT in keysPressed:
			delta.x += 1
		if window.key.UP in keysPressed:
			delta.y += 1
		if window.key.DOWN in keysPressed:
			delta.y -= 1

		return delta


class Enemy(Sprite):
	SAFE_DISTANCE = 100  # minimum distance from the player when created
	SPEED = 300  # initial speed of the ball

	def __init__(self, playerX, playerY):
		"""
		Creates an enemy ball with a random position.

		@param playerX: x position of the player ball.
		@param playerY: y position of the player ball.
		"""
		super().__init__("enemy.png")
		self.radius = self.image.width // 2
		self.anchor = self.radius, self.radius
		self._setRandomPosition(playerX, playerY)
		self.speed = Vector2(0, 0)
		self.enabled = False
		self.opacity = 0
		self.do(FadeIn(1) + CallFunc(self._enable))

	def _enable(self):
		self.cshape = CircleShape(Vector2(self.x, self.y), self.radius)
		self._setRandomDirection()
		self.enabled = True

	def _setRandomPosition(self, playerX, playerY):
		while True:
			self.x = random.randint(self.radius, director.window.width - self.radius)
			self.y = random.randint(self.radius, director.window.height - self.radius)
			if util.distance(self.x, self.y, playerX, playerY) >= Enemy.SAFE_DISTANCE:
				break

	def _setRandomDirection(self):
		self.speed = util.vectorFromAngle(random.random() * math.pi * 2, Enemy.SPEED)

	def update(self, dt):
		if self.enabled:
			# Move ball
			self.position += self.speed * dt

			# Check borders
			if self.x < self.radius or self.x > director.window.width - self.radius:
				self.speed.x = -self.speed.x
				self.x += self.speed.x * dt
			if self.y < self.radius or self.y > director.window.height - self.radius:
				self.speed.y = -self.speed.y
				self.y += self.speed.y * dt

			self.cshape.center = Vector2(self.x, self.y)
