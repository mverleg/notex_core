
from tempfile import mkstemp


name = mkstemp(text=True)[1]
print(name)
with open(name, 'w+') as fh:
	for k in range(5):
		fh.write('hello {0:d}\n'.format(k))

with open(name, 'r') as fh1:
	with open(name, 'r') as fh2:
		print('fh1: {0:}'.format(fh1.readline().rstrip('\n')))
		print('fh1: {0:}'.format(fh1.readline().rstrip('\n')))
		print('fh2: {0:}'.format(fh2.readline().rstrip('\n')))
		print('fh2: {0:}'.format(fh2.readline().rstrip('\n')))
		print('fh2: {0:}'.format(fh2.readline().rstrip('\n')))

print('so concurrent reads work just fine')


