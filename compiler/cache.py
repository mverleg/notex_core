
from time import time
from glob import iglob
from urllib.request import urlretrieve
from zipfile import ZipFile
from dogpile_cache_autoselect import auto_select_backend
from os import makedirs, remove, chmod
from os.path import join, getmtime, isfile, exists
from tempfile import gettempdir
from compiler.utils import hash_str, hash_int


#todo: make a proxy cache in case someone wants to disable this one (dogpile has a proxy, files need proxy too)


class DogpileAndFileCache:
	def __init__(self, dogpile=None, cache_dir=None, file_expiration_time=None, filename_mangler=None):
		"""
		Select a dogpile.cache backend automatically (or attempt to, anyway).
		"""
		if dogpile is None:
			dogpile = auto_select_backend(between_runs=True)
		self.dogpile = dogpile
		self.file_expiration_time = file_expiration_time or self.dogpile.expiration_time or (24 * 3600)
		if cache_dir is None:
			cache_dir = join(gettempdir(), 'dogpile_file_cache')
		self.file_dir = cache_dir
		makedirs(self.file_dir, exist_ok=True, mode=0o700)
		self.check_cleanup_files()
		self.filename_mangler = filename_mangler or self.dogpile.key_mangler or hash_str

	def get(self, *args, **kwargs):
		return self.dogpile.get(*args, **kwargs)

	def set(self, *args, **kwargs):
		return self.dogpile.set(*args, **kwargs)

	def delete(self, *args, **kwargs):
		return self.dogpile.delete(*args, **kwargs)

	def get_or_create(self, *args, **kwargs):
		return self.dogpile.get_or_create(*args, **kwargs)

	def cache_on_arguments(self, *args, **kwargs):
		return self.dogpile.cache_on_arguments(*args, **kwargs)

	def check_cleanup_files(self, cleanup_deadtime=120):
		"""
		Check if a cleanup of files is necessary based on cleanup_deadtime (seconds).

		First update timestamp, then run the task, to avoid dogpile effect.
		"""
		cudt = self.dogpile.get('dogpile_file_cache_last_cleanup')
		if not cudt or time() - cudt > cleanup_deadtime:
			self.dogpile.set('dogpile_file_cache_last_cleanup', time())
			self.cleanup_files()

	def cleanup_files(self):
		"""
		Remove all expired files.
		"""
		#todo: this needs python 3.5 for the ** thing
		#todo: cleaned files may have had another expiry time set when created (probably acceptable though, it's just cache)
		files = iglob(join(self.file_dir, '**'), recursive=True)
		for file in files:
			if isfile(file) and time() - getmtime(file) > self.file_expiration_time:
				remove(file)

	@staticmethod
	def get_func_str(func):
		"""
		Return a probably-unique string for a function, including (one time) partials. Not safe for file paths.
		"""
		if hasattr(func, '__module__'):
			return '{0:s}-{1:s}'.format(func.__module__, func.__name__)
		else:
			txt = 'partial-{0:s}-{1:s}-{2:}-{3:}'.format(func.func.__module__, func.func.__name__,
				'_'.join(str(arg) for arg in func.args),
				'_'.join('{0:s}-{1:s}'.format(key, arg) for key, arg in func.keywords.items())
			)
			return txt

	@staticmethod
	def get_file_cache_key(url, func, rzip, *, dependencies=(), extra=''):
		"""
		Generate a string to use as a key for caching this object.

		:param dependencies: A list of file paths that this result depends on; their last-modified time will be included in the key (so they expire when their dependencies change).
		:param extra: Extra information to add in the key; if this changes, the old cache value expires (cannot be found anymore).
		"""
		assert (bool(url) + bool(func) + bool(rzip) == 1), 'precisely one of url, func or rzip should be set'
		for dependency in dependencies:
			try:
				extra += '.' + hash_int(getmtime(dependency))
			except FileNotFoundError:
				extra += '.'
		if url:
			key = 'dfc_url_{0:s}'.format(url)
		elif func:
			key = 'dfc_func_{0:s}'.format(DogpileAndFileCache.get_func_str(func))
		elif rzip:
			tsstr = hash_int(getmtime(rzip)) if exists(rzip) else '0'
			key = 'dfc_rzip_{0:s}+{1:s}'.format(rzip, tsstr)
		else:
			raise AssertionError('one of url, func or rzip should be set')
		if extra:
			key += '.' + extra
		if len(key) > 24:
			return hash_str(key)[:24]
		return key

	def set_file(self, url=None, func=None, rzip=None, *, dependencies=(), extra=''):
		#todo: how to cascade all the changes if an input file changes? should add modified time to the key (this will automatically propagate if something is cached 20 times)
		"""
		Cache a file (download it from a url and store it somewhere until it expires).
		"""
		key = self.get_file_cache_key(url=url, func=func, rzip=rzip, dependencies=dependencies, extra=extra)
		print('\n*****\n   RECREATING CACHE FOR {0:}\n   {1:}\n*****\n'.format(key, self.get_func_str(func) if func else '??'))
		if url:
			cached_path = join(self.file_dir, self.filename_mangler(url))
			urlretrieve(url, cached_path)
			chmod(cached_path, 0o700)
		elif func:
			cached_path = join(self.file_dir, self.filename_mangler(self.get_func_str(func)))
			func(cached_path)
			chmod(cached_path, 0o700)
		elif rzip:
			cached_path = join(self.file_dir, self.filename_mangler(rzip))
			self.dogpile.set('dogpile_file_cache_rzip_{0:s}'.format(rzip), cached_path)
			makedirs(cached_path, exist_ok=True, mode=0o700)
			with ZipFile(rzip, 'r') as fh:
				fh.extractall(path=cached_path)
		else:
			raise AssertionError('unknown file generator')
		self.dogpile.set(key, cached_path)
		return cached_path

	def get_file(self, url=None, func=None, rzip=None, *, dependencies=(), extra=''):
		"""
		Return the path to a cached file if it exists, or None otherwise.
		"""
		key = self.get_file_cache_key(url=url, func=func, rzip=rzip, dependencies=dependencies, extra=extra)
		found = self.dogpile.get(key)
		if found and exists(found):
			if time() - getmtime(found) < self.file_expiration_time:
				return found
			else:
				remove(found)
				return None
		else:
			return None

	def get_or_create_file(self, url=None, func=None, rzip=None, *, dependencies=(), extra=''):
		"""
		Return the path to a cached file, creating it first if it does not exist.
		"""
		found = self.get_file(url=url, func=func, rzip=rzip, dependencies=dependencies, extra=extra)
		if not found:
			found = self.set_file(url=url, func=func, rzip=rzip, dependencies=dependencies, extra=extra)
		return found

	def delete_file(self, url=None, func=None, rzip=None, *, dependencies=(), extra=''):
		"""
		Delete a cached file.
		"""
		key = self.get_file_cache_key(url=url, func=func, rzip=rzip, dependencies=dependencies, extra=extra)
		found = self.dogpile.get(key)
		if found:
			self.dogpile.delete(key)
			remove(found)


if __name__ == '__main__':
	cache = DogpileAndFileCache(file_expiration_time=2)
	print('1', cache.get_or_create_file(url='http://php.markv.nl/public/ggg.jpg'))
	print('2', cache.get_or_create_file(url='http://php.markv.nl/public/ggg.jpg'))
	print('3', cache.delete_file(url='http://php.markv.nl/public/ggg.jpg'))
	print('4', cache.get_or_create_file(url='http://php.markv.nl/public/ggg.jpg'))


