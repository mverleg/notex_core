
from sys import stdout
from sys import stderr


class BasicLogger:
	def __init__(self, verbosity=1, out=None, err=None):
		self.verbosity = int(verbosity)
		if out is None:
			out = stdout
		if err is None:
			err = stderr
		self.out = out
		self.err = err

	def info(self, msg, level=1):
		if level <= self.verbosity:
			self.out.write('{0:s}\n'.format(msg))

	def warn(self, msg, level=1):
		if level <= self.verbosity:
			self.err.write('{0:s}\n'.format(msg))


