
from genericpath import getsize
from shutil import copy2, copytree, rmtree
from struct import pack
from base64 import urlsafe_b64encode
from hashlib import sha256
from os import getcwd, chdir, symlink, makedirs, remove
from os.path import expanduser, isdir, exists, dirname


class InvalidDocumentError(Exception):
	""" There was a problem in an input file. """


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


def hash_int(nr):
	"""
	Non-cryptographic hash of an integer number (for example a timestamp or the output of python's hash()).
	"""
	return urlsafe_b64encode(pack('=q', int(nr))).decode('ascii').rstrip('=').rstrip('A')


def hash_str(text):
	"""
	Take a hash of a string.
	"""
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


def link_or_copy(src, dst, *, allow_overwrite=False, exist_ok=False, follow_symlinks=True, allow_linking=True, create_dirs=True):
	"""
	Try to symlink a file (if allow_linking), fall back to copying if symlink doesn't work.
	Also works for linking/copying directories, and creates target directories as needed (if create_dirs).
	Follows symlinks (those tools that support it) if follow_symlinks and silently ignores existing if exist_ok.
	"""
	try:
		is_dir = isdir(src)
		if create_dirs and dirname(dst) and not exists(dirname(dst)):
			makedirs(dirname(dst), exist_ok=True)
		if allow_overwrite and exists(dst):
			if is_dir:
				rmtree(dst)
			else:
				remove(dst)
		if allow_linking:
			try:
				symlink(src, dst, target_is_directory=is_dir)
			except NotImplementedError:
				""" will copy later """
			else:
				return True
		if is_dir:
			copytree(src, dst, symlinks=follow_symlinks)
		else:
			copy2(src, dst, follow_symlinks=follow_symlinks)
		return False
	except FileExistsError as err:
		if not exist_ok:
			raise err


