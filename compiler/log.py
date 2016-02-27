
from logging import Logger
from sys import stdout, stderr
from multiprocessing import Lock
from time import time


# todo: see https://docs.python.org/3/library/logging.html

# todo: the logger should also be able to get timer messages, which are logged in a separate file


class Ticker:  # todo: tmp
	def __init__(self):
		self.t = time()

	def __call__(self):
		dt = time() - self.t
		self.t = time()
		return 1000 * dt


class BasicLogger(Logger):
	"""
	Simple parallelism-safe logger that prints to stdout and stderr depending on verbosity.
	"""
	def __init__(self, verbosity=1, out=None, err=None, strict=False):
		self.verbosity = int(verbosity)
		if out is None:
			out = stdout
		if err is None:
			err = stderr
		self.out = out
		self.err = err
		self.strict = strict
		self.write_lock = Lock()

	def get_level(self):
		return self.verbosity

	def info(self, msg, level=1):
		if level <= self.verbosity:
			self.write_lock.acquire()
			self.out.write('{0:s}\n'.format(msg))
			self.write_lock.release()

	def warn(self, msg, level=1):
		if level <= self.verbosity:
			self.write_lock.acquire()
			self.err.write('{0:s}\n'.format(msg))
			self.write_lock.release()

	def strict_fail(self, msg):
		"""
		Warn in non-strict mode or stop in strict mode.
		"""
		self.write_lock.acquire()
		stderr.write('{0:s}\n'.format(msg))
		self.write_lock.release()
		if self.strict:
			exit(1)

	def exception(self, err):
		"""
		An exception has been raised.
		"""
		#todo: unused
