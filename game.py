from cocos.actions import FadeOut, CallFunc
from cocos.collision_model import CollisionManagerGrid
from cocos.director import director
from cocos.euclid import Vector2
from cocos.layer import Layer, ColorLayer
from cocos.scene import Scene
from cocos.text import Label
from gettext import gettext as _

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

		self.lblTime = Label(bold=True, color=constants.FONT_COLOR,
		                     anchor_x="left", anchor_y="bottom")
		self.lblTime.position = 10, 0
		self.add(self.lblTime)

		self.lblEnemies = Label(bold=True, color=constants.FONT_COLOR,
		                        anchor_x="right", anchor_y="bottom")
		self.lblEnemies.position = director.window.width - 10, 0
		self.add(self.lblEnemies)

		self.schedule(self.update)

	def update(self, dt):
		if not self.gameLayer.isGameOver:
			self.time += dt
			self.lblTime.element.text = _("Time: {}").format(int(self.time))
			self.lblEnemies.element.text = _("Balls: {}").format(self.gameLayer.getNumberOfEnemies())


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
		self.mouseDelta = Vector2(0, 0)
		self.collMan = CollisionManagerGrid(0, 0, self.width, self.height, 30, 30)
		self.player = None
		self.enemies = []
		self.isGameOver = False
		self.schedule(self.update)
		self.schedule_interval(self.addEnemyHandler, 10)  # add new enemy every 10 seconds

	def on_enter(self):
		super().on_enter()
		director.window.set_exclusive_mouse(True)  # "grab" the mouse

		# Create player ball
		self.player = Player(director.window.width // 2, director.window.height // 2)
		self.add(self.player)

		# Create enemy balls
		for x in range(3):
			self.addEnemy()

	def on_exit(self):
		super().on_exit()
		director.window.set_exclusive_mouse(False)  # "free" the mouse

	def addEnemy(self):
		"""
		Adds a new enemy ball.

		@return: the added ball.
		"""
		enemy = Enemy(self.player.x, self.player.y)
		self.enemies.append(enemy)
		self.add(enemy)
		return enemy

	def addEnemyHandler(self, dt):
		if not self.isGameOver:
			self.addEnemy()

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

	def on_key_press(self, key, modifiers):
		self.keysPressed.add(key)

	def on_key_release(self, key, modifiers):
		if key in self.keysPressed:
			self.keysPressed.remove(key)

	def on_mouse_motion(self, x, y, dx, dy):
		self.mouseDelta += Vector2(dx, dy)
