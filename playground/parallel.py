
import pickle
from multiprocessing.pool import Pool
from sys import setrecursionlimit
from time import time
from os import getpid
from bs4 import BeautifulSoup


class Container():
	def __init__(self, soup):
		self.soup = soup

with open('../smalltest.html', 'r') as fh:
	html = fh.read()
	t = time()
	soup = BeautifulSoup(html, 'lxml')
	print('from html', time() - t)

global container
container = Container(soup)

def task(input):
	print('pid: {0:d}; soup {1:d}'.format(getpid(), id(container.soup)))
	c = len(soup.find_all('p'))
	return(input**2)

pool = Pool(processes=4)
res = pool.map(task, range(8))
print(res)

print('>> sharing soup globally works without extra memory usage on linux (at least without changes)')

if False or True:
	t = time()
	setrecursionlimit(50000)
	D = pickle.dumps(container)
	print('pickle takes', time() - t)
	t = time()
	setrecursionlimit(50000)
	container2 = pickle.loads(D)
	print('unpickle takes', time() - t)


print('>> python\'s recursion limit cannot go high enough to pickle a 5MB file\'s soup')

t = time()
S = container.soup.prettify(formatter='minimal')
print('to html', time() - t)

print('>> parsing takes about 0.41s per MB and rendering 0.21s')
print('>> this makes pickle about 22% slower and unpickle about 35% slower')


