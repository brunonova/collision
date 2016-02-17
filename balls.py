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
	RADIUS = 16
	SPEED = 400

	def __init__(self, x, y):
		"""
		Creates the player ball.
		:param x: Initial x position of the ball.
		:param y: Initial y position of the ball.
		"""
		super().__init__("player.png")
		self.anchor = Player.RADIUS, Player.RADIUS
		self.position = x, y
		self.enabled = True
		self.cshape = CircleShape(Vector2(self.x, self.y), Player.RADIUS)

	def update(self, dt, mouse_dx, mouse_dy, keys_pressed):
		if self.enabled:
			# Handle mouse
			self.x += mouse_dx
			self.y += mouse_dy

			# Handle keyboard
			if window.key.LEFT in keys_pressed:
				self.x -= Player.SPEED * dt
			if window.key.RIGHT in keys_pressed:
				self.x += Player.SPEED * dt
			if window.key.UP in keys_pressed:
				self.y += Player.SPEED * dt
			if window.key.DOWN in keys_pressed:
				self.y -= Player.SPEED * dt

			# Check window borders
			if self.x < Player.RADIUS:
				self.x = Player.RADIUS
			elif self.x > director.window.width - Player.RADIUS:
				self.x = director.window.width - Player.RADIUS
			if self.y < Player.RADIUS:
				self.y = Player.RADIUS
			elif self.y > director.window.height - Player.RADIUS:
				self.y = director.window.height - Player.RADIUS

			self.cshape.center = Vector2(self.x, self.y)


class Enemy(Sprite):
	RADIUS = 16
	SAFE_DISTANCE = 100
	SPEED = 300

	def __init__(self, player_x, player_y):
		"""
		Creates an enemy ball with a random position.
		:param player_x: X position of the player ball.
		:param player_y: Y position of the player ball.
		"""
		super().__init__("enemy.png")
		self.anchor = Enemy.RADIUS, Enemy.RADIUS
		self._setRandomPosition(player_x, player_y)
		self.vx = self.vy = 0
		self.enabled = False
		self.opacity = 0
		self.do(FadeIn(1) + CallFunc(self._enable))

	def _enable(self):
		self.cshape = CircleShape(Vector2(self.x, self.y), Enemy.RADIUS)
		self._setRandomDirection()
		self.enabled = True

	def _setRandomPosition(self, player_x, player_y):
		while True:
			self.x = random.randint(Enemy.RADIUS, director.window.width - Enemy.RADIUS)
			self.y = random.randint(Enemy.RADIUS, director.window.height - Enemy.RADIUS)
			if util.distance(self.x, self.y, player_x, player_y) >= Enemy.SAFE_DISTANCE:
				break

	def _setRandomDirection(self):
		direction = random.random() * math.pi * 2
		self.vx = math.cos(direction) * Enemy.SPEED
		self.vy = math.sin(direction) * Enemy.SPEED

	def update(self, dt):
		if self.enabled:
			# Move ball
			self.x += self.vx * dt
			self.y += self.vy * dt

			# Check borders
			if self.x < Enemy.RADIUS or self.x > director.window.width - Enemy.RADIUS:
				self.vx = -self.vx
				self.x += self.vx * dt
			if self.y < Enemy.RADIUS or self.y > director.window.height - Enemy.RADIUS:
				self.vy = -self.vy
				self.y += self.vy * dt

			self.cshape.center = Vector2(self.x, self.y)
