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

import math, random, pyglet
from cocos.actions import CallFunc, FadeIn, FadeOut
from cocos.collision_model import CircleShape
from cocos.director import director
from cocos.euclid import Vector2
from cocos.sprite import Sprite
from pyglet import window

from . import util

__all__ = ["Player", "Enemy", "Coin", "Bonus", "Missile"]


class Ball(Sprite):
	"""Base class for player and enemy balls."""

	def __init__(self, image, *args, **kwargs):
		super().__init__(image, *args, **kwargs)

		# Determine if the image is a simple image or an Animation
		if isinstance(image, pyglet.image.Animation):
			realImage = image.frames[0].image  # it's an animation
		else:
			realImage = self.image  # it's an image

		self.radius = realImage.width // 2  # radius of the ball
		self.image_anchor = self.radius, self.radius
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
		self.position = x, y  # WARNING: position is a tuple, not a vector!
		self.cshape.center = Vector2(x, y)  # the center must be a Vector2!

		self._frozen = False
		self._invulnerable = False
		self.invulnerableSprite = Sprite("player_invulnerable.png", opacity=0)
		self.add(self.invulnerableSprite, z=0.8)

	def freeze(self):
		"""Freezes the ball."""
		self.image = pyglet.resource.image("player_frozen.png")
		self._frozen = True

	def unfreeze(self):
		"""Unfreezes the ball."""
		self._frozen = False
		self.image = pyglet.resource.image("player.png")

	def isFrozen(self):
		"""Returns whether the ball is frozen."""
		return self._frozen

	def makeInvulnerable(self):
		"""Makes the ball invulnerable."""
		self.invulnerableSprite.stop()
		self._invulnerable = True
		self.invulnerableSprite.opacity = 255

	def makeVulnerable(self):
		"""Makes the ball vulnerable after an animation."""
		if self.isInvulnerable():
			self.invulnerableSprite.stop()
			actions = FadeOut(0.2) + (FadeIn(0.2) + FadeOut(0.2)) * 4 + \
			          CallFunc(self._makeVulnerable)
			self.invulnerableSprite.do(actions)

	def isInvulnerable(self):
		"""Returns whether the ball is invulnerable."""
		return self._invulnerable

	def update(self, dt, mouseDelta: Vector2, keysPressed):
		# Move player according to mouse/keyboard
		if not self.isFrozen():
			self.position += mouseDelta
			self.position += Player._keyboardDelta(keysPressed) * Player.SPEED * dt
			self.ensureWithinBorders()  # check borders

	def _makeVulnerable(self):
		self.invulnerableSprite.opacity = 0
		self._invulnerable = False

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
	MASS = 1  # mass of the ball (used when balls collide)

	def __init__(self, playerX, playerY, initial_speed):
		"""
		Creates an enemy ball with a random position.

		@param playerX: x position of the player ball.
		@param playerY: y position of the player ball.
		@param initial_speed: initial speed of the ball.
		"""
		super().__init__("enemy.png")
		self._initialSpeed = initial_speed
		self.setRandomPosition(playerX, playerY, Enemy.PLAYER_DISTANCE)
		self.speed = Vector2(0, 0)
		self.mass = Enemy.MASS
		self.enabled = False  # whether the ball is moving and is collidable
		self.opacity = 0
		self.do(FadeIn(1) + CallFunc(self._enable))

	def update(self, dt, factor):
		if self.enabled:
			# Move ball
			self.position += self.speed * dt * factor

			# Check borders
			width, height = director.get_window_size()
			if self.x < self.radius or self.x > width - self.radius:
				self.speed.x = -self.speed.x
			if self.y < self.radius or self.y > height - self.radius:
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
		dist = delta.magnitude()

		if dist == 0:  # prevent a possible division by zero
			dist = b1.radius + b2.radius - 1
			delta = Vector2(b1.radius + b2.radius, 0)

		# Minimum Translation Distance to push balls apart after the collision
		mtd = delta * ((b1.radius + b2.radius - dist) / dist)

		# Inverse mass quantities
		im1, im2 = 1 / b1.mass, 1 / b2.mass

		# Push-pull them apart
		b1.position += mtd * (im1 / (im1 + im2))
		b2.position -= mtd * (im2 / (im1 + im2))

		# Ensure the balls are still inside the window
		b1.ensureWithinBorders()
		b2.ensureWithinBorders()

		# Impact speed
		v = b1.speed - b2.speed
		vn = v.dot(mtd.normalize())

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
		super().__init__(Coin._loadAnimation())
		self.setRandomPosition(playerX, playerY, Coin.PLAYER_DISTANCE)
		self.enabled = False  # whether the coin can be caught
		self.opacity = 0
		self.do(FadeIn(1) + CallFunc(self._enable))

	def _enable(self):
		self.enabled = True

	@staticmethod
	def _loadAnimation():
		sheet = pyglet.resource.image("coin.png")
		grid = pyglet.image.ImageGrid(sheet, 1, 61)
		textures = pyglet.image.TextureGrid(grid)
		return pyglet.image.Animation.from_image_sequence(textures, 0.02)


class Bonus(Ball):
	"""A bonus that gives the player an advantage or a disadvantage when caught."""
	PLAYER_DISTANCE = 200  # minimum distance from the player when created

	def __init__(self):
		"""Creates a bonus (disabled and hidden)."""
		super().__init__("bonus.png")
		self.enabled = False  # whether the bonus can be caught
		self.opacity = 0

	def show(self, playerX, playerY):
		"""
		Shows the bonus and enables it.

		@param playerX: x position of the player ball.
		@param playerY: y position of the player ball.
		"""
		if not self.enabled:
			self.setRandomPosition(playerX, playerY, Bonus.PLAYER_DISTANCE)
			self.enabled = True
			self.opacity = 0
			self.do(FadeIn(0.5))

	def hide(self):
		"""Hides the bonus and disables it."""
		self.enabled = False
		self.opacity = 0
		self.stop()


class Missile(Ball):
	"""A homing-missile that tries to hit the player."""
	PLAYER_DISTANCE = 200  # minimum distance from the player when created
	SPEED = 200  # speed of the missile

	def __init__(self):
		"""Creates a bonus (disabled and hidden)."""
		super().__init__("missile.png")
		self.enabled = False  # whether the missile moves and is collidable
		self.opacity = 0
		self.direction = 0

	def show(self, playerX, playerY):
		"""
		Shows the missile and enables it.

		@param playerX: x position of the player ball.
		@param playerY: y position of the player ball.
		"""
		if not self.enabled:
			self.setRandomPosition(playerX, playerY, Missile.PLAYER_DISTANCE)
			self.direction = self._getPlayerDirection(playerX, playerY)
			self.do(FadeIn(0.5) + CallFunc(self._enable))

	def hide(self):
		"""Hides the missile and disables it."""
		self.enabled = False
		self.opacity = 0
		self.stop()

	def update(self, dt, playerX, playerY):
		# The missile needs to be rotated when fading in (not enabled yet)
		self.direction = self._getPlayerDirection(playerX, playerY)
		self.rotation = -math.degrees(self.direction)  # rotation is in degrees!

		if self.enabled:
			speed = util.vectorFromAngle(self.direction, Missile.SPEED * dt)
			self.position += speed
			self.cshape.center = Vector2(self.x, self.y)

	def _enable(self):
		self.enabled = True

	def _getPlayerDirection(self, playerX, playerY):
		return math.atan2(playerY - self.y, playerX - self.x)
