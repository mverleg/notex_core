
from sys import stdout
from sys import stderr


class BasicLogger:
	def __init__(self, verbosity=1, out=None, err=None, strict=False):
		self.verbosity = int(verbosity)
		if out is None:
			out = stdout
		if err is None:
			err = stderr
		self.out = out
		self.err = err
		self.strict = strict

	def info(self, msg, level=1):
		if level <= self.verbosity:
			self.out.write('{0:s}\n'.format(msg))

	def warn(self, msg, level=1):
		if level <= self.verbosity:
			self.err.write('{0:s}\n'.format(msg))

	def strict_fail(self, msg):
		"""
		Warn in non-strict mode or stop in strict mode.
		"""
		stderr.write('{0:s}\n',format(msg))
		if self.strict:
			exit(1)


