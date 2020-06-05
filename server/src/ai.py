from random import randrange
from config import Config

PLAYER_CHAR = "@"
WALL_CHAR = "#"
BOULDER_CHAR = "O"
GRASS_CHAR = "."
GRASS_ALT_CHAR = "_"
LADDER_CHAR = "H"
BUSH_CHAR = "B"
GEYSIR_CHAR = "M"
DOOR_CHAR = "D"
FORTIFIED_CHAR = "▓"
EMPTY_CHAR = " "

NO_GO = [BOULDER_CHAR, WALL_CHAR, DOOR_CHAR, FORTIFIED_CHAR, LADDER_CHAR, GEYSIR_CHAR]

class Bot:
	def __init__(self, game, pos, floor):
		self.game = game

		self.pos = pos
		self.floor = floor
		self.zombieToDir = 0

		self.sniffedPlayerPos = None
		self.sniffedPlayerDir = None

	def move(self):		
		if self.sniffedPlayerPos == None:
			self.moveRandom()
		else:
			self.moveForPlayer()
		self.sniffPlayers()
		

	def moveForPlayer(self):
		newPos = self.game.getNextPos(self.pos, self.sniffedPlayerDir)
		title = self.game.getTitle(newPos, floor = self.floor)

		if title == PLAYER_CHAR: # Kill player
			self.sniffedPlayerPos = self.sniffedPlayerDir = None
			self.pos = newPos

			for playerId in self.game.players:
				if self.game.players[playerId].position == newPos:
					self.game.kill(playerId, False)

		elif title in NO_GO:
			self.sniffedPlayerPos = self.sniffedPlayerDir = None
			
		elif newPos == self.sniffedPlayerPos:
			self.sniffedPlayerPos = self.sniffedPlayerDir = None
			self.pos = newPos

		else:
			self.pos = newPos

	def moveRandom(self):
		# Do random turns occasionally
		if randrange(0, Config.botRandomTurnChange) == 0:
			self.zombieToDir = randrange(0, 4)

		tries = 0
		def tryMoving():
			nonlocal tries
			newPos = self.game.getNextPos(self.pos, self.zombieToDir)

			if self.game.getTitle(newPos, floor = self.floor) in [EMPTY_CHAR, GRASS_CHAR]:
				self.pos = newPos

			else:
				self.zombieToDir = randrange(0, 4)
				if tries > 6: return
				tryMoving()
				tries += 1

		tryMoving()

	def sniffPlayers(self):
		def getPos(direction, steps):
			pos = self.pos
			for x in range(0, steps + 1):
				pos = self.game.getNextPos(pos, direction)

			return pos


		blockedDirections = []
		for i in range(0, Config.botSniffRange):
			for direction in range(0, 4):
				if not direction in blockedDirections:
					nextPos = getPos(direction, i)

					title = self.game.getTitle(nextPos, floor = self.floor)
					if title == PLAYER_CHAR:
						self.sniffedPlayerPos = nextPos
						self.sniffedPlayerDir = direction
						return
					elif title in NO_GO:
						blockedDirections.append(direction)