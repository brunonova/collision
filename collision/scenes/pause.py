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

from cocos.actions import FadeIn, FadeOut, Repeat
from cocos.director import director
from cocos.layer import Layer
from cocos.scene import Scene
from cocos.text import Label
from gettext import gettext as _
from pyglet import window
from pyglet.event import EVENT_HANDLED

from ..options import Options
from ..util import ScreenshotLayer


class PauseScene(Scene):
	"""The Pause Screen scene."""
	def __init__(self):
		super().__init__(ScreenshotLayer(), PauseLayer())


class PauseLayer(Layer):
	"""Layer that shows "PAUSE"."""
	is_event_handler = True

	def __init__(self):
		super().__init__()

		width, height = director.get_window_size()
		paused = Label(_("PAUSE"), font_name="Ubuntu", font_size=64, bold=True,
		               color=Options.FONT_COLOR, anchor_x="center", anchor_y="center")
		paused.position = width // 2, height // 2
		paused.do(Repeat(FadeOut(0.3) + FadeIn(0.3)))  # blink
		self.add(paused)

	def on_key_press(self, key, modifiers):
		if key in (window.key.P, window.key.PAUSE, window.key.ESCAPE):
			director.pop()
			return EVENT_HANDLED
