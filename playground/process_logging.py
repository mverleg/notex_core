
from functools import partial
from logging import getLogger, StreamHandler, Formatter, DEBUG, INFO, WARNING, ERROR, CRITICAL
from logging.handlers import QueueHandler
from sys import stdout
from multiprocessing import Process, Queue, current_process
from time import sleep
import atexit


def start_listener(queue):
	listener = getLogger('compile')
	handler = StreamHandler(stdout)
	handler.setFormatter(Formatter('%(asctime)s %(processName)-10s %(name)s %(levelname)-8s %(message)s'))
	listener.addHandler(handler)
	while True:
		try:
			record = queue.get()
			if record is None:
				break
			# level or filter
			listener.handle(record)
		except Exception:
			import sys, traceback
			print('The logger had a problem!', file=sys.stderr)
			traceback.print_exc(file=sys.stderr)


def start_sender(queue):
	sender = getLogger('compile')
	sender.addHandler(QueueHandler(queue))
	for k in range(5):
		sleep(.070)
		sender.log(DEBUG, '{0:s}: message #{1:d}'.format(current_process().name, k))


def kill_logger(proc):
	proc.join(timeout=0.1)
	proc.terminate()


def main():
	queue = Queue(-1)
	listener = Process(target=start_listener, args=(queue,))
	listener.start()
	atexit.register(partial(kill_logger, listener))
	senders = []
	for k in range(5):
		sleep(.150)
		worker = Process(target=start_sender, args=(queue,))
		senders.append(worker)
		worker.start()
		atexit.register(partial(kill_logger, worker))
	for sender in senders:
		sender.join()
	queue.put_nowait(None)
	listener.join()


if __name__ == '__main__':
	main()


