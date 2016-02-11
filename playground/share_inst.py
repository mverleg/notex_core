
from multiprocessing import Lock, Process, Array, Manager, Pipe
from random import randint
from time import sleep, time

from os import getpid


class Test:
	def __init__(self):
		self.ll = Lock()

	def log(self, txt):
		self.ll.acquire()
		print(txt)
		self.ll.release()

def bla(k, pids, logr, cntr):
	logr.log('hello from {0:d}'.format(getpid()))
	pids[k] = getpid()
	cntr[getpid()] = randint(0, 256)

def blockproc(pipe):
	t = time()
	d = pipe.recv()
	print('blocked for {0:.6f} and got "{1:s}"'.format(time() - t, d))
	pipe.close()

pids = Array('i', range(10))

mngr = Manager()
container = mngr.dict()

if __name__ == '__main__':
	logr = Test()

	procs = []
	for k in range(10):
		p = Process(target=bla, args=(k, pids, logr, container))
		p.start()
		procs.append(p)

	sleep(0.5)

	for p in procs:
		p.join()

	print(pids[:])
	print(container)

	# blocking mode?
	local, remote = Pipe()
	p = Process(target=blockproc, args=(remote,))
	p.start()
	sleep(1.100)
	local.send('hello there, still waiting?')
	local.close()
	p.join()


