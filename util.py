from cocos.euclid import Vector2


def distance(x1, y1, x2, y2):
	x, y = x2 - x1, y2 - y1
	return Vector2(x, y).magnitude()
