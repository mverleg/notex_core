
from functools import partial
from sys import stdout
from time import sleep
from dogpile.cache import make_region


def mangler(key):
	return 'notex_' + str(key)


cache = make_region(
	name = 'notex',
	key_mangler = mangler,
).configure(
	# 'dogpile.cache.memcached',
	'dogpile.cache.pylibmc',
	expiration_time = 2 * 60 * 60,
	arguments = {
		'url': ['127.0.0.1'],
	},
)

@cache.cache_on_arguments()
def fibo(n):
	if n < 2:
		return 1
	return fibo(n - 1) + fibo(n - 2)


for k in range(0, 35):
	stdout.write('{0:d}, '.format(fibo(k)))
print('\n>> much faster!')


def get_value(k):
	print('zzzzz')
	sleep(3)
	return 42


cache.get_or_create('42', partial(get_value, 2))
print('>> kept between requests!')
print('>> it\'s even kept between python-memcached and mylibmc actually')


