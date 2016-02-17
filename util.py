import math
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
