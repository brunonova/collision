import math
from cocos.director import director
from cocos.euclid import Vector2


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
