
from threading import *
import time
import random


class GameRoom:
	def __init__(self):
		self.players = []        
		self.nempty = 4        # empty seats
		self.ninside = 0       # players started playing ninside>0 -> game in progress
		self.lck = Lock()
		self.turn = Condition(self.lck)
		self.gamestart = Condition(self.lck)

	def enter(self, name):
		self.lck.acquire()
		while self.ninside >= 4:
			self.turn.wait()

		print (name, " entered")
		self.nempty -= 1
		self.ninside += 1
		self.players.append(name)
		if self.nempty == 0:
			self.gamestart.notifyAll()
			print("game started: ", self.players)
		else:
				while self.ninside < 4:
					self.gamestart.wait()

		self.lck.release()

	def exit(self, name):
		self.lck.acquire()
		print (name, " exiting")
		self.nempty += 1
		self.players.remove(name)

		if self.nempty == 4:
			self.ninside = 0
			self.turn.notifyAll()
		self.lck.release()


def player(room,name):
	time.sleep(random.random()/100)
	room.enter(name)
	time.sleep(random.random()/100)
	room.exit(name)


gr = GameRoom()

t = []
for i in range(52):
	t.append(Thread(target=player, args=(gr, str(i))))

for tr in t:
	tr.start()

for tr in t:
	tr.join()










