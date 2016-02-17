import math
import random
from cocos.actions import CallFunc
from cocos.actions import FadeIn
from cocos.collision_model import CircleShape
from cocos.director import director
from cocos.euclid import Vector2
from cocos.sprite import Sprite
from pyglet import window

import util

__all__ = ["Player", "Enemy", "Coin"]


class Ball(Sprite):
	"""Base class for player and enemy balls."""

	def __init__(self, image, *args, **kwargs):
		super().__init__(image, *args, **kwargs)
		self.radius = self.image.width // 2  # radius of the ball
		self.cshape = CircleShape(Vector2(self.x, self.y), self.radius)

	def ensureWithinBorders(self):
		"""
		Checks if the ball is inside the window, moving it if it's not.

		The cshape is also updated.
		"""
		width, height = director.get_window_size()
		self.x = min(max(self.x, self.radius), width - self.radius)
		self.y = min(max(self.y, self.radius), height - self.radius)
		self.cshape.center = Vector2(self.x, self.y)

	def setRandomPosition(self, playerX, playerY, minPlayerDistance):
		"""
		Moves the ball to a random position.

		@param playerX: x position of the player.
		@param playerY: y position of the player.
		@param minPlayerDistance: minimum distance from the player when created.
		"""
		while True:
			width, height = director.get_window_size()
			x = random.randint(self.radius, width - self.radius)
			y = random.randint(self.radius, height - self.radius)
			if util.distance(x, y, playerX, playerY) >= minPlayerDistance:
				break
		self.position = x, y
		self.cshape.center = Vector2(x, y)


class Player(Ball):
	"""The player ball."""
	SPEED = 400  # movement speed with the keyboard

	def __init__(self, x, y):
		"""
		Creates the player ball.

		@param x: initial x position of the ball.
		@param y: initial y position of the ball.
		"""
		super().__init__("player.png")
		self.anchor = self.radius, self.radius
		self.position = x, y  # WARNING: position is a tuple, not a vector!
		self.cshape.center = Vector2(x, y)  # the center must be a Vector2!

	def update(self, dt, mouseDelta: Vector2, keysPressed):
		# Move player according to mouse/keyboard
		self.position += mouseDelta
		self.position += Player._keyboardDelta(keysPressed) * Player.SPEED * dt
		self.ensureWithinBorders()  # check borders

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


class Enemy(Ball):
	"""An enemy ball."""
	PLAYER_DISTANCE = 100  # minimum distance from the player when created

	def __init__(self, playerX, playerY, initial_speed):
		"""
		Creates an enemy ball with a random position.

		@param playerX: x position of the player ball.
		@param playerY: y position of the player ball.
		@param initial_speed: initial speed of the ball.
		"""
		super().__init__("enemy.png")
		self.anchor = self.radius, self.radius
		self._initialSpeed = initial_speed
		self.setRandomPosition(playerX, playerY, Enemy.PLAYER_DISTANCE)
		self.speed = Vector2(0, 0)
		self.enabled = False  # whether the ball is moving and is collidable
		self.opacity = 0
		self.do(FadeIn(1) + CallFunc(self._enable))

	def update(self, dt):
		if self.enabled:
			# Move ball
			self.position += self.speed * dt

			# Check borders
			if self.x < self.radius or self.x > director.window.width - self.radius:
				self.speed.x = -self.speed.x
			if self.y < self.radius or self.y > director.window.height - self.radius:
				self.speed.y = -self.speed.y
			self.ensureWithinBorders()

	@staticmethod
	def bounceBalls(b1: "Enemy", b2: "Enemy"):
		"""
		Bounces two balls off one another after a collision.

		@param b1: the 1st ball.
		@param b2: the 2nd ball.
		"""
		p1 = Vector2(b1.x, b1.y)
		p2 = Vector2(b2.x, b2.y)
		delta = p1 - p2
		dist = util.distance(b1.x, b1.y, b2.x, b2.y)

		if dist == 0:
			dist = b1.radius * 2 - 1
			delta = Vector2(b1.radius * 2, 0)
		mtd = delta * (((b1.radius * 2) - dist) / dist)

		im1 = im2 = 1  # inverse mass quantities

		# Push-pull them appart
		p1 += mtd * (im1 / (im1 + im2))
		p2 -= mtd * (im2 / (im1 + im2))
		b1.position = p1.x, p1.y
		b2.position = p2.x, p2.y

		# Ensure the balls are still inside the window
		b1.ensureWithinBorders()
		b2.ensureWithinBorders()

		# Impact speed
		v = b1.speed - b2.speed
		mtd.normalize()
		vn = v.dot(mtd)

		# Sphere intersecting but moving away from each other already
		if vn > 0:
			return

		# Collision impulse
		restitution = 1
		i = (-(1 + restitution) * vn) / (im1 + im2)
		impulse = mtd * i

		# Change in momentum
		b1.speed += impulse * im1
		b2.speed -= impulse * im2

	def _enable(self):
		self._setRandomDirection()
		self.enabled = True

	def _setRandomDirection(self):
		self.speed = util.vectorFromAngle(random.random() * math.pi * 2, self._initialSpeed)


class Coin(Ball):
	"""A coin, used when the type of game is "Coins"."""
	PLAYER_DISTANCE = 200  # minimum distance from the player when created

	def __init__(self, playerX, playerY):
		"""
		Creates a coin with a random position.

		@param playerX: x position of the player ball.
		@param playerY: y position of the player ball.
		"""
		super().__init__("coin.png")
		self.anchor = self.radius, self.radius
		self.setRandomPosition(playerX, playerY, Coin.PLAYER_DISTANCE)
		self.enabled = False  # whether the coin can be catched
		self.opacity = 0
		self.do(FadeIn(1) + CallFunc(self._enable))

	def _enable(self):
		self.enabled = True
