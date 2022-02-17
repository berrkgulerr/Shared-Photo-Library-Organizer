from multiprocessing import Process,Array,Lock
from socket import *

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
