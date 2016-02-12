#!/usr/bin/env python3
import random

import math

from cocos.actions import FadeIn, CallFunc, FadeOut
from cocos.collision_model import CircleShape, CollisionManagerGrid
from cocos.director import director
from cocos.euclid import Vector2
from cocos.layer import ColorLayer
from cocos.scene import Scene
from cocos.sprite import Sprite
from pyglet import window

import util


class GameLayer(ColorLayer):
	is_event_handler = True

	def __init__(self):
		super().__init__(192, 192, 192, 255)
		self.keys_pressed = set()
		self.mouse_dx = self.mouse_dy = 0
		self.collman = CollisionManagerGrid(0, 0, self.width, self.height, 30, 30)
		self.new_enemy_timer = 0
		self.schedule(self.update)

		# Create player ball
		self.player = Player(director.window.width // 2, director.window.height // 2)
		self.add(self.player)

		# Create enemy balls
		self.enemies = [Enemy(self.player.x, self.player.y) for x in range(3)]
		for enemy in self.enemies:
			self.add(enemy)

	def update(self, dt):
		self.collman.clear()

		# Update player ball
		self.player.update(dt, self.mouse_dx, self.mouse_dy, self.keys_pressed)
		self.mouse_dx = self.mouse_dy = 0
		self.collman.add(self.player)

		# Update enemy balls
		for enemy in self.enemies:
			enemy.update(dt)
			if enemy.enabled:
				self.collman.add(enemy)

		# Check collisions between player and enemies
		for enemy in self.enemies:
			if enemy.enabled and self.collman.they_collide(self.player, enemy):
				self.game_over()

		# Check collisions between enemies
		for i, enemy in enumerate(self.enemies):
			for j, other in enumerate(self.enemies):
				if j > i and enemy.enabled and other.enabled and \
				   self.collman.they_collide(enemy, other):
					self.bounce_balls(enemy, other)

		# Add a new enemy ball every 10 seconds
		self.new_enemy_timer += dt
		if self.new_enemy_timer >= 10:
			self.new_enemy_timer -= 10
			enemy = Enemy(self.player.x, self.player.y)
			self.enemies.append(enemy)
			self.add(enemy)

	def on_key_press(self, key, modifiers):
		self.keys_pressed.add(key)

	def on_key_release(self, key, modifiers):
		if key in self.keys_pressed:
			self.keys_pressed.remove(key)

	def on_mouse_motion(self, x, y, dx, dy):
		self.mouse_dx += dx
		self.mouse_dy += dy

	def game_over(self):
		self.player.enabled = False
		self.new_enemy_timer = -500
		self.player.do((FadeOut(2)) + CallFunc(exit, 0))
		for enemy in self.enemies:
			enemy.enabled = False
			enemy.stop()

	def bounce_balls(self, b1: Enemy, b2: Enemy):
		pass


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
		self._set_random_position(player_x, player_y)
		self.vx = self.vy = 0
		self.enabled = False
		self.opacity = 0
		self.do(FadeIn(1) + CallFunc(self._enable))

	def _enable(self):
		self.cshape = CircleShape(Vector2(self.x, self.y), Enemy.RADIUS)
		self._set_random_direction()
		self.enabled = True

	def _set_random_position(self, player_x, player_y):
		while True:
			self.x = random.randint(Enemy.RADIUS, director.window.width - Enemy.RADIUS)
			self.y = random.randint(Enemy.RADIUS, director.window.height - Enemy.RADIUS)
			if util.distance(self.x, self.y, player_x, player_y) >= Enemy.SAFE_DISTANCE:
				break

	def _set_random_direction(self):
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


if __name__ == "__main__":
	director.init(caption="Collision", width=500, height=500)
	director.window.set_exclusive_mouse(True)
	director.run(Scene(GameLayer()))
