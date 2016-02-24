
from genericpath import getsize
from shutil import copy2
from struct import pack
from base64 import urlsafe_b64encode
from hashlib import sha256
from os import getcwd, chdir, symlink
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


def hash_str(text):
	sha2 = sha256()
	sha2.update(text.encode('ascii'))
	return urlsafe_b64encode(sha2.digest()).decode('ascii')[:-1]


def hash_file(path):
	"""
	Take a hash of a file. Contains filesize to apparently prevent length extension attacks (idea taken from git).
	File is read in 1MB blocks to work on low-memory devices.
	"""
	#todo: not here, but I should check that all filenames in the package are boring
	sha2 = sha256()
	size = pack('l', getsize(path))
	sha2.update(size + b'notex')
	with open(path, 'rb') as fh:
		while True:
			block = fh.read(1024)
			if not block:
				break
			sha2.update(block)
	return urlsafe_b64encode(sha2.digest()).decode('ascii')[:-1]


def link_or_copy(src, dst, exist_ok=False, follow_symlinks=True):
	"""
	Try to symlink a file, fall back to copying if symlink doesn't work.
	"""
	# if system() == 'Linux':
	try:
		try:
			symlink(src, dst)
		except NotImplementedError:
			copy2(src, dst, follow_symlinks=follow_symlinks)
			return False
		else:
			return True
	except FileExistsError as err:
		if not exist_ok:
			raise err


