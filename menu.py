import pyglet
from cocos.director import director
from cocos.layer import ColorLayer, MultiplexLayer
from cocos.menu import Menu, MenuItem, ToggleMenuItem, MultipleMenuItem
from cocos.scene import Scene
from gettext import gettext as _

from pyglet.window import key

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
		self.options = {
			"ballsCollide": True,
			"difficulty": constants.MEDIUM
		}

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
			MultiMenuItem(_("Difficulty: "), self.onDifficulty,
			              [_("Easy"), _("Medium"), _("Hard")], constants.MEDIUM),
			ToggleMenuItem(_("Ball collisions: "), self.onBallsCollide,
			               self.menuLayer.options["ballsCollide"]),
			MenuItem(_("Back"), self.on_quit)
		]
		self.create_menu(items)

	def onDifficulty(self, index):
		self.menuLayer.options["difficulty"] = index

	def onBallsCollide(self, value):
		self.menuLayer.options["ballsCollide"] = value

	def on_quit(self):
		self.parent.switch_to(0)


class MultiMenuItem(MultipleMenuItem):
	"""
	MultipleMenuItem that "wraps around" the list of item.

	This class is similar to MultipleMenuItem, except that:
	* Clicking or pressing RIGHT/ENTER on the last option selects the 1st item;
	* Clicking or pressing LEFT on the 1st item selects the last item.
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def on_key_press(self, symbol, modifiers):
		if symbol == key.LEFT and self.idx == 0:
			# Select the last item+1 so that the call to the parent's on_key_press
			# will select the last item
			self.idx = len(self.items)
		elif symbol in (key.RIGHT, key.ENTER) and self.idx == len(self.items) - 1:
			# Select the first item-1 so that the call to the parent's on_key_press
			# will select the first item
			self.idx = -1
		return super().on_key_press(symbol, modifiers)
