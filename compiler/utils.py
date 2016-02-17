
from os import getcwd, chdir
from os.path import expanduser


class cd:
	"""
	Context manager for changing the current working directory
	http://stackoverflow.com/a/13197763/723090
	"""
	def __init__(self, new_path):
		self.new_path = expanduser(new_path)

	def __enter__(self):
		self.savedPath = getcwd()
		chdir(self.new_path)

	def __exit__(self, etype, value, traceback):
		chdir(self.savedPath)


