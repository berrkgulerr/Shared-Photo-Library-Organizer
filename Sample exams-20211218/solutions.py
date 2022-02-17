import re
from subprocess import Popen,PIPE
from threading import *
import time
import random
from multiprocessing import Process,Array,Lock
from socket import *

#Q1

class Cart:
    def __init__(self,a,b):
        self.a = a
        self.b = b
        self.sizea = len(a)
        self.sizeb = len(b)
        self.counta = 0
        self.countb = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.countb < self.sizeb:
            self.current = (self.a[self.counta],self.b[self.countb])
            self.countb += 1
            return self.current
        else: 
            self.countb = 0
            self.counta += 1
            if self.counta < self.sizea:
                self.current = (self.a[self.counta],self.b[self.countb])
                self.countb += 1
                return self.current
            else:
                raise StopIteration

def cart(a, b):
    sizea = len(a)
    sizeb = len(b)

    for i in range(sizea):
        for j in range(sizeb):
            yield (a[i], b[j])


print("class Cart")
for i in Cart([1,2],["a","b"]):
    print(i)

print("---------------------------")

print("def cart")

for i in cart([1,2],["a","b"]):
    print(i)
print("---------------------------")

#################################################################################################################

#################################################################################################################
#Q2

def sortuniq(inpfilepath, outfilepath):
    inp = open(inpfilepath, "r")
    out = open(outfilepath, "w")
    p = Popen(["/usr/bin/sort"], stdin=inp ,stdout = PIPE)
    q = Popen(["/usr/bin/uniq"], stdin = p.stdout, stdout = out)


    p.wait()
    q.wait()
    inp.close()
    out.close()



#sortuniq("/home/berk/Desktop/CENG445 - SCRIPT/Sample exams-20211218/inp", "/home/berk/Desktop/CENG445 - SCRIPT/Sample exams-20211218/out")




#################################################################################################################

#################################################################################################################
#Q3

class Logger:
    def __init__(self, filepath):
        self.fp = open(filepath, 'r')

    def __del__(self):
        self.fp.close()

    def nextline(self):
        return self.fp.readline()


class Highlighter:
    def __init__(self, t):
        self.obj = t

    def __getattr__(self, __name: str):
        return getattr(self.obj, __name)


class HLDate(Highlighter):
    def nextline(self):
        '''
        get next line of log from member object and return
        with replacing all date occurences of 02/12/2015 into
        **02/12/2015**
        '''
        regstr = "(?P<date>(\d\d)/(\d\d)/(\d\d\d\d))"
        line = self.obj.nextline()
        return re.sub(regstr, "**\g<date>**", line)


class HLIP(Highlighter):
    def nextline(self):
        '''
        get next line of log from member object and return
        with replacing all IP occurences like 144.122.1.121 into
        144.122.*.*
        '''
        regstr = "(?P<g1>(\d+)\.(\d+))\.(\d+)\.(\d+)"
        line = self.obj.nextline()
        return re.sub(regstr, "\g<g1>.*.*", line)


a = HLIP(HLDate(Logger('test_q3.txt')))
b = HLIP(Logger('test_q3.txt'))
c = HLDate(Logger('test_q3.txt'))

l = a.nextline()
while l != '':
    print(l)
    l = a.nextline()

# This uses the pattern: Decorator.



#################################################################################################################

#################################################################################################################
#Q4

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



#################################################################################################################

#################################################################################################################
#Q5


def parsecommand(self, line):         # parse client input provided for convenience
	(req, num) = line.rstrip('\n').split(' ')
	return (req, int(num))

class Server(Process):

	def __init__(self, sock,  lock, items, prices):
		self.lock = lock
		self.items = items
		self.prices = prices
		self.sock = sock
		Process.__init__(self)

	def run(self):
		request = self.sock.recv(1024)
		while request != '':
			(req,num) = parsecommand(request)
			if num < 0 or num > len(self.prices):
				self.sock.send("ERROR\n")
			elif req == 'PRICE':
				self.sock.send(str(self.prices[num]) + '\n')
			elif req == 'BUY':
				self.lock.acquire()
				if self.items[num] > 0:
					self.sock.send("OK\n")
					self.items[num] -= 1
				else:
					self.sock.send("SOLD\n")
				self.lock.release()
			else:
				self.sock.send("WHAT?\n")
			request = self.sock.recv(1024)


def startserver(host, port, prices):
	sock = socket(AF_INET, SOCK_STREAM)
	sock.bind( (host, port))
	sock.listen(10)
	l = len(prices)
	items = Array('i', l)
	for i in range(l):
		items[i] = 1
	lck = Lock()
	av = sock.accept()
	while av:
		print('accepted: ', av[1])
		s = Server(av[0], lck, items, prices)
		s.start()
		av = sock.accept()

if __name__ == '__main__':
	import sys
	print(sys.argv)
	startserver('0.0.0.0', int(sys.argv[1]), map(float, sys.argv[2].split(',')))


