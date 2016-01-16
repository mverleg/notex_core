
from logging import warning
from os import getcwd
from os.path import isdir, isfile, exists, join, abspath


class SourceFileNotFound(FileNotFoundError):
	pass


class SourceLoader:
	"""
	Load source files directly, without caching.
	"""
	def __init__(self, paths, include_cwd=True):
		"""
		:param paths: Iterable of paths from which files can be loaded.
		"""
		assert hasattr(paths, '__iter__')
		self.paths = [getcwd()] if include_cwd else []
		for path in paths:
			if isdir(path):
				self.paths.append(abspath(path))
			elif exists(path):
				warning('path "{0:}" is on your path, but it is not a directory'.format(path))
			else:
				warning('path "{0:}" is on your path, but it does not exist'.format(path))

	def exists(self, path):
		"""
		Check whether a path exists.
		"""
		for dir in self.paths:
			full = abspath(join(dir, path))
			if isfile(full):
				assert full.startswith(dir), \
					'file "{0:s}" was found at "{1:s}" but this is not inside "{2:s}"'.format(path, full, dir)
				return full
		return None

	def find(self, path):
		"""
		Find a source file. Goes through the paths provided at initialization, and returns the first match that exists.

		:param path: Relative path for the source file.
		:return: Return the full path if the file exists.
		:raises SourceFileNotFound: Raises exception if the file doesn't exist.
		"""
		match = self.exists(path)
		if match is None:
			tried = [join(dir, path) for dir in self.paths]
			SourceFileNotFound('Did not find "{0:s}"; tried "{1:s}"'.format(path, '", "'.join(tried)))
		return match

	def load(self, path):
		"""
		Load a source file. It will be searched for in the paths provided at initialization.

		:param path: The relative path to load the file from.
		:return: Text from the file (unicode).
		"""
		found = self.find(path)
		try:
			with open(found, 'r') as fh:
				return fh.read()
		except (OSError, IOError) as err:
			raise SourceFileNotFound('File "{0:s}" was found at "{1:s}", but could not be loaded. Reason: "{2:s}"'
				.format(path, found, str(err)))


# todo: maybe cached version using mtime


