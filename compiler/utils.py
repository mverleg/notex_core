
from sys import stdout
from compiler.conf import settings


def log(msg, level=1):
	if level >= settings.verbosity:
		stdout.write(str(msg) + '\n')


