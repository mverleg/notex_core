
from dogpile.cache import make_region


region = make_region().configure(
	'dogpile.cache.memory_pickle',
)

def gen():
	print('gettign')
	return 42

print('got', region.get_or_create('test', gen))
print('got', region.get_or_create('test', gen))



region = make_region().configure(
	'dogpile.cache.dbm',
	arguments = {
		'filename': '/tmp/bla',
	}
)

def gen():
	print('gettign')
	return 43

print('now', region.get_or_create('test2', gen))
print('now', region.get_or_create('test2', gen))


