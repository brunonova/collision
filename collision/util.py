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

import math, pyglet
from cocos.director import director
from cocos.euclid import Vector2
from cocos.menu import Menu
from pyglet.gl import GL_RGBA, GL_TEXTURE_2D
from pyglet.image import Texture

from .options import Options


def distance(x1, y1, x2, y2):
	"""
	Returns the distance between two points.

	@param x1: x-coordinate of the 1st point.
	@param y1: y-coordinate of the 1st point.
	@param x2: x-coordinate of the 2nd point.
	@param y2: y-coordinate of the 2nd point.
	@return: the distance between the points.
	"""
	return (Vector2(x2, y2) - Vector2(x1, y1)).magnitude()

def vectorFromAngle(angle, length=1):
	"""
	Creates and returns a vector with the specified angle and length/magnitude.

	@param angle: angle of the vector.
	@param length: length/magnitude of the vector.
	@return: the created vector
	"""
	return Vector2(math.cos(angle), math.sin(angle)) * length

def getWindowUsableSize():
	"""
	Determines and returns the usable size of the window.

	When the window is resized into a different aspect ratio (like when
	fullscreen is enabled), the game layers will preserve the aspect ration, but
	the window will have two vertical black bars.
	These bars are included in director.window.width, which may not be the
	intended behavior.

	@return: a tuple with the usable size (width, height).
	"""
	# Original and virtual window size and aspect ratio
	virtualSize = director.get_window_size()
	virtualRatio = virtualSize[0] / virtualSize[1]

	# Real window size and aspect ration
	realSize = director.window.width, director.window.height
	realRatio = realSize[0] / realSize[1]

	# Determine the usable size
	if realRatio == virtualRatio:  # same aspect ration
		return realSize
	elif realRatio > virtualRatio:  # real window is wider than virtual window
		return int(realSize[1] * virtualRatio), realSize[1]
	else:  # real window is taller than virtual window
		return realSize[0], int(realSize[0] / virtualRatio)

def takeScreenshot():
	"""
	Takes a screenshot of the window and returns it.

	@return: screenshot texture.
	"""
	width, height = getWindowUsableSize()
	texture = Texture.create_for_size(GL_TEXTURE_2D, width, height, GL_RGBA)
	texture.blit_into(pyglet.image.get_buffer_manager().get_color_buffer(), 0, 0, 0)
	return texture.get_region(0, 0, width, height)


class CustomizedMenu(Menu):
	"""The same as the Menu class, but with custom fonts."""
	def __init__(self, title=""):
		super().__init__(title)
		self.font_title["color"] = Options.FONT_COLOR
		self.font_title["font_name"] = Options.FONT_NAME
		self.font_title["font_size"] = 40
		self.font_item["color"] = Options.FONT_COLOR_NOT_SELECTED
		self.font_item["font_name"] = Options.FONT_NAME
		self.font_item["font_size"] = 30
		self.font_item_selected["color"] = Options.FONT_COLOR
		self.font_item_selected["font_name"] = Options.FONT_NAME
		self.font_item_selected["font_size"] = self.font_item["font_size"]
		self.font_item_selected["bold"] = True
