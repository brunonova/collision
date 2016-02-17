#!/usr/bin/env python3
import random
import math
import gettext
from gettext import gettext as _
from cocos.actions import FadeIn, CallFunc, FadeOut
from cocos.collision_model import CircleShape, CollisionManagerGrid
from cocos.director import director
from cocos.euclid import Vector2
from cocos.layer import ColorLayer, Layer
from cocos.menu import Menu, MenuItem
from cocos.scene import Scene
from cocos.sprite import Sprite
from cocos.text import Label
from pyglet import window

import util


class HUDLayer(Layer):
	def __init__(self, gameLayer):
		super().__init__()

		self.gameLayer = gameLayer
		self.time = 0

		self.lblTime = Label(bold=True, color=(0, 0, 0, 255), anchor_x="left", anchor_y="bottom")
		self.lblTime.position = 10, 0
		self.add(self.lblTime)

		self.lblEnemies = Label(bold=True, color=(0, 0, 0, 255), anchor_x="right", anchor_y="bottom")
		self.lblEnemies.position = director.window.width - 10, 0
		self.add(self.lblEnemies)

	def update(self, dt):
		self.time += dt
		self.lblTime.element.text = _("Time: {}").format(int(self.time))
		self.lblEnemies.element.text = _("Balls: {}").format(self.gameLayer.getNumberOfEnemies())


class GameLayer(ColorLayer):
	is_event_handler = True

	def __init__(self):
		super().__init__(192, 192, 192, 255)
		self.keysPressed = set()
		self.mouseDx = self.mouseDy = 0
		self.collMan = CollisionManagerGrid(0, 0, self.width, self.height, 30, 30)
		self.newEnemyTimer = 0
		self.schedule(self.update)

		# Create player ball
		self.player = Player(director.window.width // 2, director.window.height // 2)
		self.add(self.player)

		# Create enemy balls
		self.enemies = [Enemy(self.player.x, self.player.y) for x in range(3)]
		for enemy in self.enemies:
			self.add(enemy)

		self.hudLayer = HUDLayer(self)
		self.add(self.hudLayer, z=1)

	def on_enter(self):
		super().on_enter()
		director.window.set_exclusive_mouse(True)

	def on_exit(self):
		super().on_exit()
		director.window.set_exclusive_mouse(False)

	def update(self, dt):
		self.collMan.clear()

		# Update player ball
		self.player.update(dt, self.mouseDx, self.mouseDy, self.keysPressed)
		self.mouseDx = self.mouseDy = 0
		self.collMan.add(self.player)

		# Update enemy balls
		for enemy in self.enemies:
			enemy.update(dt)
			if enemy.enabled:
				self.collMan.add(enemy)

		# Check collisions between player and enemies
		for enemy in self.enemies:
			if enemy.enabled and self.collMan.they_collide(self.player, enemy):
				self.gameOver()

		# Check collisions between enemies
		for i, enemy in enumerate(self.enemies):
			for j, other in enumerate(self.enemies):
				if j > i and enemy.enabled and other.enabled and \
				   self.collMan.they_collide(enemy, other):
					self.bounceBalls(enemy, other)

		# Add a new enemy ball every 10 seconds
		self.newEnemyTimer += dt
		if self.newEnemyTimer >= 10:
			self.newEnemyTimer -= 10
			enemy = Enemy(self.player.x, self.player.y)
			self.enemies.append(enemy)
			self.add(enemy)

		# Update the HUD
		self.hudLayer.update(dt)

	def on_key_press(self, key, modifiers):
		self.keysPressed.add(key)

	def on_key_release(self, key, modifiers):
		if key in self.keysPressed:
			self.keysPressed.remove(key)

	def on_mouse_motion(self, x, y, dx, dy):
		self.mouseDx += dx
		self.mouseDy += dy

	def gameOver(self):
		self.player.enabled = False
		self.newEnemyTimer = -500
		self.player.do((FadeOut(2)) + CallFunc(lambda: director.replace(Scene(MainMenu()))))
		for enemy in self.enemies:
			enemy.enabled = False
			enemy.stop()

	def bounceBalls(self, b1: 'Enemy', b2: 'Enemy'):
		p1 = Vector2(b1.x, b1.y)
		p2 = Vector2(b2.x, b2.y)
		delta = p1 - p2
		dist = util.distance(b1.x, b1.y, b2.x, b2.y)

		if dist == 0:
			dist = Enemy.RADIUS * 2 - 1
			delta = Vector2(Enemy * 2, 0)
		mtd = delta * (((Enemy.RADIUS * 2) - dist) / dist)

		im1 = im2 = 1  # inverse mass quantities

		# Push-pull them appart
		p1 += mtd * (im1 / (im1 + im2))
		p2 -= mtd * (im2 / (im1 + im2))
		b1.position = p1.x, p1.y
		b2.position = p2.x, p2.y

		# Impact speed
		v = Vector2(b1.vx - b2.vy, b1.vy - b2.vy)
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
		vel1 = Vector2(b1.vx, b1.vy)
		vel2 = Vector2(b2.vx, b2.vy)
		vel1 += impulse * im1
		vel2 -= impulse * im2
		b1.vx, b1.vy = vel1.x, vel1.y
		b2.vx, b2.vy = vel2.x, vel2.y

		# TODO: Check borders

	def getNumberOfEnemies(self):
		return len(self.enemies)


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


class MainMenu(Menu):
	def __init__(self):
		super().__init__("Collision")
		self.menu_anchor_x = self.menu_anchor_y = "center"

		items = [MenuItem(_("Play"), self.on_play),
		         MenuItem(_("Quit"), self.on_quit)]
		self.create_menu(items)

	def on_play(self):
		director.replace(Scene(GameLayer()))

	def on_quit(self):
		exit()


if __name__ == "__main__":
	gettext.bindtextdomain("collision", "./mo")
	gettext.textdomain("collision")
	director.init(caption="Collision", width=500, height=500)
	# TODO: remove default handler
	director.run(Scene(MainMenu()))
