import pyglet
from cocos.actions import FadeIn
from cocos.actions import Repeat, FadeOut
from cocos.director import director
from cocos.layer import ColorLayer
from cocos.scene import Scene
from cocos.text import Label
from gettext import gettext as _

from pyglet import window
from pyglet.gl import GL_TEXTURE_2D, GL_RGBA
from pyglet.image import Texture


class PauseScene(Scene):
	"""
	The Pause Screen scene.

	Don't use the constructor directly! Instead, call PauseScene.create().

	The scene will show a "screenshot" of the previous scene as background.
	The code is based on Cocos' pause module
	"""
	def __init__(self, background=None):
		super().__init__(PauseLayer(background))

	@staticmethod
	def create():
		# "Take a screenshot" and pass it to the scene
		width, height = director.window.width, director.window.height
		texture = Texture.create_for_size(GL_TEXTURE_2D, width, height, GL_RGBA)
		texture.blit_into(pyglet.image.get_buffer_manager().get_color_buffer(), 0, 0, 0)
		return PauseScene(texture.get_region(0, 0, width, height))


class PauseLayer(ColorLayer):
	"""Layer that shows "PAUSE"."""
	is_event_handler = True

	def __init__(self, background):
		super().__init__(25, 25, 25, 205)
		self.background = background

		width, height = director.get_window_size()
		paused = Label(_("PAUSE"), font_name="Ubuntu", font_size=64, bold=True,
		               color=(255, 255, 255, 255), anchor_x="center", anchor_y="center")
		paused.position = width // 2, height // 2
		paused.do(Repeat(FadeOut(0.3) + FadeIn(0.3)))  # blink
		self.add(paused)

	def draw(self):
		# Draw the screenshot as the background
		if self.background:
			self.background.blit(0, 0, width=self.width, height=self.height)
		super().draw()

	def on_key_press(self, key, modifiers):
		if key in (window.key.P, window.key.PAUSE):
			director.pop()
