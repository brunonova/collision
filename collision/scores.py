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

import json, os

from .options import Options


class Scores:
	"""Stores, loads and handles the high scores."""
	MAX_HIGH_SCORES = 5  # Maximum number of high scores, per type and difficulty.

	def __init__(self):
		self.scores = {}
		self._loadScores()

	def getHighScores(self, type, difficulty):
		type, difficulty = str(type), str(difficulty)  # convert params to strings
		if type in self.scores and difficulty in self.scores[type]:
			return self.scores[type][difficulty]
		else:
			return []

	def isHighScore(self, type, difficulty, score):
		if score <= 0:  # a score of 0 is not a high score
			return False
		else:
			scores = self.getHighScores(type, difficulty)
			if len(scores) < Scores.MAX_HIGH_SCORES:  # limit not reached
				return True
			else:
				# Check if this score is better than the last high score
				return score > scores[Scores.MAX_HIGH_SCORES - 1]["score"]

	def addHighScore(self, type, difficulty, name, score, balls):
		type, difficulty = str(type), str(difficulty)  # convert params to strings

		# Create the dicts for type and difficulty if they don't exist
		if not type in self.scores:
			self.scores[type] = {}
		if not difficulty in self.scores[type]:
			self.scores[type][difficulty] = []

		# Add the score to the list of high scores
		scores = self.scores[type][difficulty]
		scoreDict = {"name": name, "score": score, "balls": balls}
		for i, s in enumerate(scores):
			if score > s["score"]:
				# Worse score found, so add the score before this one
				scores.insert(i, scoreDict)
				# If the limit of scores was exceeded, remove the last one
				if len(scores) > Scores.MAX_HIGH_SCORES:
					scores.pop()
				break
		else:
			# No worse score found, so add to the end if the limit is not exceeded
			if len(scores) < Scores.MAX_HIGH_SCORES:
				scores.append(scoreDict)

		self._saveScores()  # save scores to disk

	def _loadScores(self):
		#TODO: check exceptions
		#TODO: check validity
		self._scoresDir = Options.getUserDataFolder()
		filename = os.path.join(self._scoresDir, "scores.json")
		if os.path.exists(filename):
			with open(filename, "r") as file:
				self.scores = json.load(file)

	def _saveScores(self):
		#TODO: check exceptions
		filename = os.path.join(self._scoresDir, "scores.json")
		os.makedirs(self._scoresDir, exist_ok=True)
		with open(filename, "w") as file:
			json.dump(self.scores, file)
