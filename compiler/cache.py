
from time import time
from glob import iglob
from urllib.request import urlretrieve
from zipfile import ZipFile
from dogpile_cache_autoselect import auto_select_backend
from os import makedirs, remove, chmod
from os.path import join, getmtime, isfile, exists
from tempfile import gettempdir
from compiler.utils import hash_str


class DogpileAndFileCache:
	file_arg_msg = 'precisely one of url, func or rzip should be set'

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
		files = iglob(join(self.file_dir, '**'), recursive=True)
		for file in files:
			if isfile(file) and time() - getmtime(file) > self.file_expiration_time:
				remove(file)

	def set_file(self, url=None, func=None, rzip=None):
		"""
		Cache a file (download it from a url and store it somewhere until it expires).
		"""
		assert (bool(url) + bool(func) + bool(rzip) == 1), self.file_arg_msg
		cached_path = join(self.file_dir, self.filename_mangler(url or func or rzip))
		if url:
			self.dogpile.set('dogpile_file_cache_url_{0:s}'.format(url), cached_path)
			urlretrieve(url, cached_path)
			chmod(cached_path, 0o700)
		elif rzip:
			makedirs(cached_path, exist_ok=True, mode=0o700)
			self.dogpile.set('dogpile_file_cache_rzip_{0:s}'.format(rzip), cached_path)
			with ZipFile(rzip, 'r') as fh:
				fh.extractall(path=cached_path)
		else:
			NotImplementedError('only url->file and rzip->dir cache implemented')
		return cached_path

	def get_file(self, url=None, func=None, rzip=None):
		"""
		Return the path to a cached file if it exists, or None otherwise.
		"""
		assert (bool(url) + bool(func) + bool(rzip) == 1), self.file_arg_msg
		if url or rzip:
			method_name, path = ('url', url) if url else ('rzip', rzip)
			found = self.dogpile.get('dogpile_file_cache_{1:s}_{0:s}'.format(path, method_name))
			if found and exists(found):
				if time() - getmtime(found) < self.file_expiration_time:
					return found
				else:
					remove(found)
					return None
			else:
				return None
		else:
			NotImplementedError('only url->file and rzip->dir cache implemented')

	def get_or_create_file(self, url=None, func=None, rzip=None):
		"""
		Return the path to a cached file, creating it first if it does not exist.
		"""
		assert (bool(url) + bool(func) + bool(rzip) == 1), self.file_arg_msg
		if url or rzip:
			found = self.get_file(url=url, func=func, rzip=rzip)
			if not found:
				found = self.set_file(url=url, func=func, rzip=rzip)
			return found
		else:
			NotImplementedError('only url->file and rzip->dir cache implemented')

	def delete_file(self, url=None, func=None, rzip=None):
		"""
		Delete a cached file.
		"""
		assert (bool(url) + bool(func) + bool(rzip) == 1), self.file_arg_msg
		if url or rzip:
			method_name, path = ('url', url) if url else ('rzip', rzip)
			found = self.dogpile.get('dogpile_file_cache_{1:s}_{0:s}'.format(path, method_name))
			if found:
				self.dogpile.delete('dogpile_file_cache_{1:s}_{0:s}'.format(path, method_name))
				remove(found)
		else:
			NotImplementedError('only url->file and rzip->dir cache implemented')


if __name__ == '__main__':
	cache = DogpileAndFileCache(file_expiration_time=2)
	print('1', cache.get_or_create_file(url='http://php.markv.nl/public/ggg.jpg'))
	print('2', cache.get_or_create_file(url='http://php.markv.nl/public/ggg.jpg'))
	print('3', cache.delete_file(url='http://php.markv.nl/public/ggg.jpg'))
	print('4', cache.get_or_create_file(url='http://php.markv.nl/public/ggg.jpg'))


