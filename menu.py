import pyglet
from cocos.director import director
from cocos.menu import Menu, MenuItem
from cocos.scene import Scene
from gettext import gettext as _

from game import GameScene


class MenuScene(Scene):
	def __init__(self):
		super().__init__(MenuLayer())


class MenuLayer(Menu):
	def __init__(self):
		super().__init__("Collision")
		self.menu_anchor_x = self.menu_anchor_y = "center"

		items = [MenuItem(_("Play"), self.onPlay),
		         MenuItem(_("Quit"), self.on_quit)]
		self.create_menu(items)

	def onPlay(self):
		director.push(GameScene())

	def on_enter(self):
		super().on_enter()
		director.window.set_exclusive_mouse(False) # ensure cursor is available

	def on_quit(self):
		pyglet.app.exit()
