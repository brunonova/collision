import pyglet
from cocos.director import director
from cocos.layer import ColorLayer, MultiplexLayer
from cocos.menu import Menu, MenuItem, ToggleMenuItem
from cocos.scene import Scene
from gettext import gettext as _

import constants
from game import GameScene


class MenuScene(Scene):
	"""The scene that displays the main menu."""
	def __init__(self):
		menuLayer = MenuLayer()
		optionsLayer = OptionsLayer(menuLayer)
		super().__init__(ColorLayer(*constants.BACKGROUND_COLOR),
						 MultiplexLayer(menuLayer, optionsLayer))


class MenuLayer(Menu):
	"""Layer that displays the menu."""
	def __init__(self):
		super().__init__("Collision")

		# Initialize game options
		self.options = {"ballsCollide": True}

		# Customize the menu
		self.font_title["color"] = constants.FONT_COLOR
		self.font_item["color"] = constants.FONT_COLOR_NOT_SELECTED
		self.font_item_selected["color"] = constants.FONT_COLOR

		# Add the items and create the menu
		items = [
			MenuItem(_("Play"), self.onPlay),
			MenuItem(_("Options"), self.onOptions),
			MenuItem(_("Quit"), self.on_quit)
		]
		self.create_menu(items)

	def onPlay(self):
		director.push(GameScene(self.options))

	def onOptions(self):
		self.parent.switch_to(1)

	def on_enter(self):
		super().on_enter()
		director.window.set_exclusive_mouse(False)  # ensure cursor is available

	def on_quit(self):
		pyglet.app.exit()


class OptionsLayer(Menu):
	"""Layer that display an options menu."""

	def __init__(self, menuLayer):
		super().__init__(_("Options"))
		self.menuLayer = menuLayer

		# Customize the menu
		self.font_title["color"] = constants.FONT_COLOR
		self.font_item["color"] = constants.FONT_COLOR_NOT_SELECTED
		self.font_item_selected["color"] = constants.FONT_COLOR

		# Add the items and create the menu
		items = [
			ToggleMenuItem(_("Ball collisions: "), self.onBallsCollide,
			               self.menuLayer.options["ballsCollide"]),
			MenuItem(_("Quit"), self.on_quit)
		]
		self.create_menu(items)

	def onBallsCollide(self, value):
		self.menuLayer.options["ballsCollide"] = value

	def on_quit(self):
		self.parent.switch_to(0)
