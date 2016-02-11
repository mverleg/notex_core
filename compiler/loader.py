
from logging import warning
from os import getcwd
from os.path import isdir, isfile, exists, join, abspath


class SourceFileNotFound(FileNotFoundError):
	pass


class SourceLoader:
	"""
	Load source files directly, without caching.
	"""
	def __init__(self, dir_paths, include_cwd=True):
		"""
		:param dir_paths: Iterable of paths from which files can be loaded.
		"""
		assert hasattr(dir_paths, '__iter__')
		self.dir_paths = list(dir_paths)
		if include_cwd:
			self.dir_paths.append(getcwd())
		for path in dir_paths:
			if isdir(path):
				self.dir_paths.append(abspath(path))
			elif exists(path):
				warning('path "{0:}" is on your path, but it is not a directory'.format(path))
			else:
				warning('path "{0:}" is on your path, but it does not exist'.format(path))

	def search_paths(self, file_path):
		"""
		Generate the list of full paths where file_path is searched.
		"""
		for dir in self.dir_paths:
			full_path = abspath(join(dir, file_path))
			assert full_path.startswith(dir), \
				'file "{0:s}" was found at "{1:s}" but this is not inside "{2:s}"'.format(file_path, full_path, dir)
			yield full_path

	def exists(self, file_path):
		"""
		Check whether a path exists.
		"""
		for full_path in self.search_paths(file_path):
			if isfile(full_path):
				return full_path
		return None

	def find(self, file_path):
		"""
		Find a source file. Goes through the paths provided at initialization, and returns the first match that exists.

		:param file_path: Relative path for the source file.
		:return: Return the full path if the file exists.
		:raises SourceFileNotFound: Raises exception if the file doesn't exist.
		"""
		match = self.exists(file_path)
		if match is None:
			tried = tuple(self.search_paths(file_path))
			raise SourceFileNotFound('Did not find "{0:s}"; tried "{1:s}"'.format(file_path, '", "'.join(tried)))
		return match

	def load(self, file_path):
		"""
		Load a source file. It will be searched for in the paths provided at initialization.

		:param file_path: The relative path to load the file from.
		:return: Text from the file (unicode).
		"""
		found = self.find(file_path)
		try:
			with open(found, 'r') as fh:
				return fh.read()
		except (OSError, IOError) as err:
			raise SourceFileNotFound('File "{0:s}" was found at "{1:s}", but could not be loaded. Reason: "{2:s}"'
				.format(file_path, found, str(err)))


# todo: maybe cached version using mtime


