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

class Timer:
	"""
	A timer that counts down and optionally calls a function when it reaches 0.

	The timer is NOT updated automatically! It must be updated manually by
	calling the "update(dt)" method from a CocosNode's scheduled "update" method.

	Also, when the timer reaches 0, it is not reset automatically! That must be
	done manually in the callback function.
	"""
	def __init__(self, time=0, callback=None, cond=None, *args, **kwargs):
		"""
		Creates a timer that counts down and optionally calls a function when it reaches 0.

		The timer is NOT updated automatically! It must be updated manually by
		calling the "update(dt)" method from a CocosNode's scheduled "update" method.

		Also, when the timer reaches 0, it is not reset automatically! That must be
		done manually in the callback function.

		@param time: the starting time (0 or a negative value disables the timer).
		@param callback: function to call when the timer reaches 0. The function
		                 receives the timer as the first argument, then "args"
		                 and "kwargs" as optional additional arguments.
		@param cond: optional condition (a callable) that must be met for the timer
		             to count down.
		@param args: optional arguments to pass to the callback function.
		@param kwargs: optional keyword arguments to pass to the callback function.
		"""
		self.time = time
		"""Time (seconds) left in the timer."""

		self.callback = callback
		self.cond = cond
		self.args = args
		self.kwargs = kwargs

	def update(self, dt):
		"""
		Updates the timer, calling the callback function if it reaches 0.

		This method must be called manually for the timer to be updated!

		@param dt: seconds passed since the last update.
		"""
		if self.time > 0 and (not callable(self.cond) or self.cond()):
			self.time -= dt

			if self.time <= 0 and callable(self.callback):
				self.callback(self, *self.args, **self.kwargs)
