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
from cocos.director import director
from cocos.menu import MenuItem, shake, shake_back, Menu
from cocos.scene import Scene
from gettext import gettext as _

from ..util import CustomizedMenu
from .. import util


class QuitScene(Scene):
	"""
	The in-game Quit menu scene.

	Don't use the constructor directly! Instead, call QuitScene.create().

	The scene will show a "screenshot" of the previous scene as background.
	The code is based on Cocos' pause module.
	"""
	def __init__(self, background=None):
		super().__init__(QuitLayer(background))

	@staticmethod
	def create():
		"""Creates and returns the Pause scene."""
		# "Take a screenshot" and pass it to the scene
		return QuitScene(util.takeScreenshot())


class QuitLayer(CustomizedMenu):
	"""Layer that shows a Quit menu."""
	def __init__(self, background):
		super().__init__(_("Quit?"))
		self.background = background

		items = [
			MenuItem(_("Yes"), self.onYes),
			MenuItem(_("No"), self.onNo),
		]
		self.create_menu(items, shake(), shake_back())

	def onYes(self):
		# Pop 2 scenes (the current Quit scene and the Game scene)
		director.pop()
		director.pop()

	def onNo(self):
		# Pop the current Quit scene
		director.pop()

	def draw(self):
		# Draw the screenshot as the background
		if self.background:
			width, height = director.get_window_size()
			self.background.blit(0, 0, width=width, height=height)
		super().draw()

	def on_quit(self):
		self.onNo()
