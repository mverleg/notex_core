
"""
Automatically select an available backend to use for dogpile.cache.

* Makes an effort (relying on questionable trends) to get a faster backend if there are multiple available.
* Only searches local backends; if your cache server is external or needs special parameters, configure it manually.

Issue: https://bitbucket.org/zzzeek/dogpile.cache/issues/93/auto-select-an-available-backend
"""

from sys import stderr
from os.path import join
from tempfile import gettempdir
from dogpile.cache import make_region


def is_available(package):
	try:
		__import__(package)
	except ImportError:
		return False
	else:
		return True


def auto_select_backend(region_kwargs=None, between_runs=True, require_server=False, verbose=False):
	"""
	Try to auto-detect a cache backend.

	:param region_kwargs: Parameters passed on to the region (dictionary).
	:param between_runs: If True, only selects backends that persist between runs.
	:param require_server: If True, raises an exception if no working server-backend is found (redis, memcached).
	:param verbose: If True, prints choices that are being made.
	"""
	region_kwargs = region_kwargs or {}
	""" Redis """
	if is_available('redis'):
		region = make_region(**region_kwargs).configure(
			'dogpile.cache.redis',
			arguments={
				'distributed_lock': True
			},
		)
		from redis.exceptions import ConnectionError
		try:
			region.get_or_create('test', lambda: 'dogpile autoselect backend')
		except ConnectionError:
			if verbose:
				print('didn\'t select redis because there is no connection to the server, even though "redis" package '
					'is installed (also install the redis server, not just the python binding)')
		else:
			region.delete('test')
			if verbose:
				print('selected "redis" backend!')
			return region
	elif verbose:
		print('didn\'t select redis because "redis" package is not installed')

	""" Memcached - pylibmc """
	if is_available('pylibmc'):
		region = make_region(**region_kwargs).configure(
			'dogpile.cache.pylibmc',
			arguments={
				'url': 'localhost',
			},
		)
		from pylibmc import ConnectionError
		try:
			region.get_or_create('test', lambda: 'dogpile autoselect backend')
		except ConnectionError:
			if verbose:
				print('didn\'t select pylibmc (memcached) because there is no connection to the server, even though '
					'"pylibmc" package is installed (also install the memcached server, not just the python client)')
		else:
			region.delete('test')
			if verbose:
				print('selected "pylibmc" (memcached) backend!')
			return region
	elif verbose:
		print('didn\'t select pylibmc (memcached) because "pylibmc" package is not installed')

	""" Memcached - memcached """
	if is_available('memcache'):
		region = make_region(**region_kwargs).configure(
			'dogpile.cache.memcached',
			arguments={
				'url': ['localhost'],
			},
		)
		try:
			region.get_or_create('test', lambda: 'dogpile autoselect backend')
		except TypeError: # yes it throw a TypeError "a bytes-like object is required" if it can't connect
			if verbose:
				print('didn\'t select memcached because there is no connection to the server, even though "python-'
					'memcached" package is installed (also install the memcached server, not just the python client)')
		else:
			region.delete('test')
			if verbose:
				print('selected "memcached" backend!')
			return region
	elif verbose:
		print('didn\'t select memcached because "python-memcached" package is not installed')

	""" Memcached - bmemcached """
	if is_available('bmemcached'):
		region = make_region(**region_kwargs).configure(
			'dogpile.cache.bmemcached',
			arguments={
				'url': ['localhost'],
			},
		)
		try:
			region.get_or_create('test', lambda: 'dogpile autoselect backend')
		except Exception as err:
			if verbose:
				print('didn\'t select bmemcached because there was a problem (not sure what, to be honest)')
			stderr.write('memcached problem: ' + str(err) + '\n')
		else:
			region.delete('test')
			if verbose:
				print('selected "bmemcached" backend!')
			return region
	elif verbose:
		print('didn\'t select bmemcached because python-binary-memcached" package is not installed')

	if require_server:
		raise NotImplementedError('No working server backends were found (and require_server is True)')
	else:
		if verbose:
			print('Accepting lack of server backends since require_server is False')

	""" memory_pickle """
	# I chose `memory_pickle` instead of `memory` because the later might have strange side effects
	# since objects can be changed after being stored in cache.
	if not between_runs:
		region = make_region(**region_kwargs).configure(
			'dogpile.cache.memory_pickle',
			arguments={},
		)
		try:
			region.get_or_create('test', lambda: 'dogpile autoselect backend')
		except Exception as err:
			if verbose:
				print('didn\'t select memory_pickle because there was a problem (not sure what, to be honest)')
			stderr.write('memory_pickle problem: ' + str(err) + '\n')
		else:
			region.delete('test')
			if verbose:
				print('selected "memory_pickle" backend!')
			return region
	else:
		if verbose:
			print('not considering memory_pickle because between_runs is True (default)')

	""" dbm """
	fname = join(gettempdir(), 'dogpile.cache.dbm')
	region = make_region(**region_kwargs).configure(
		'dogpile.cache.dbm',
		arguments={
			'filename': fname,
		},
	)
	try:
		region.get_or_create('test', lambda: 'dogpile autoselect backend')
	except Exception as err:
		if verbose:
			print('didn\'t select dbm because there was a problem (not sure what, to be honest)')
		stderr.write('dbm problem: ' + str(err) + '\n')
	else:
		region.delete('test')
		if verbose:
			print('selected "dbm" (file based) backend!')
			print('dbm cache file: "{0:s}"'.format(fname))
		return region

	""" null (last resort) """
	print('no real backend could be reached without configuration')
	region = make_region(**region_kwargs).configure(
		'dogpile.cache.null',
	)
	try:
		region.get_or_create('test', lambda: 'dogpile autoselect backend')
	except Exception as err:
		if verbose:
			print('didn\'t select null because there was a problem (hopefully no one ever gets to see this message '
				'except by reading the source - null backend doesn\'t do anything so it should have no trouble)')
		stderr.write('dbm problem: ' + str(err) + '\n')
	else:
		region.delete('test')
		if verbose:
			print('selected "null" backend (which doesn\'t do anything)')
		return region


if __name__ == '__main__':
	auto_select_backend(verbose=True)


