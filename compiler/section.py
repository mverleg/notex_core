
from copy import copy
from compiler.leaf import MultiThreadedLeaf
from package import Package
from packages import PackageList
from parse_render__lxml.parser import LXML_Parser


class Section:
	"""
	Handle (load, pre-process, parse, include, arguments, tags, substitutions) a rendered document.
	"""
	def __init__(self, path, loader, logger):
		#todo: depth limit
		#self.provisional(path=path, loader=loader, logger=logger)
		#todo tmp
		self.leaf = MultiThreadedLeaf(path=path, loader=loader, logger=logger, preproc=(), parser=LXML_Parser())
		self.soup = self.leaf.get()
		self.packages = self.get_packages(self.soup, logger=logger)

	def get_packages(self, soup, logger):
		packages = []
		pack_tags = soup.find_all('package')
		for pack_tag in pack_tags:
			package_args = copy(pack_tag.attrs)
			assert 'name' in package_args, 'package must specify a name [got "{0:s}"]' \
				.format('" & "'.join('{0:s}={1:}'.format(k, v) for k, v in pack_tag.attrs.items()))
			name = package_args.pop('name')
			version = package_args.pop('version', '==*')
			print('  load package {0:s}{1:s} with {2:d} arguments'.format(name, version, len(package_args)))
			# logger.info('  load package {0:s}{1:s} for "{2:s}" with {3:d} arguments'.format(  # todo
			# 	name, version, path, len(package_args)), level=2)
			pkg = Package(name=name, version=version, options=package_args).load()
			packages.append(pkg)
			pack_tag.extract()
		return PackageList(packages)

	def do_leaf(self, path, loader, logger):
		"""
		Construct a context-guess and go through loading, pre-processing and parsing.
		"""
		preproc = ()
		parser = LXML_Parser()
		leaf = MultiThreadedLeaf(path=path, loader=loader, logger=logger, preproc=(), parser=parser)
		leaf.get()

	def final(self, path, loader, logger):
		"""
		Use the now-determined context and go through loading, pre-processing and parsing again if needed.
		"""
		preproc = ()
		parser = LXML_Parser()
		leaf = MultiThreadedLeaf(path=path, loader=loader, logger=logger, preproc=(), parser=parser)
		leaf.get()

	def get(self):
		#todo tmp
		return self.soup.prettify(formatter='minimal')


class MultiprocLeaf:  #todo: change to section
	"""
	Load, pre-process and parse an included or rendered document, using a worker process.
	"""
	#todo: for multi-process communication, see modular_render or http://stackoverflow.com/a/35351997/723090
	def __init__(self, path, loader, logger, preproc, parser, depth=0):
		#todo: how to deal with errors?
		self.pipe, remote_pipe = Pipe()
		self.parser = LXML_Parser()
		self.depth = depth
		self._worker = Process(target=self._load_async, kwargs=dict(path=path, loader=loader, logger=logger,
			preproc=preproc, parser=self.parser, depth=self.depth, pipe=remote_pipe))
		self._worker.start()
		register(partial(MultithreadLeaf._stop_worker, self._worker))
		self.html = self.soup = None

	def get(self):
		if self.soup is None:
			self.soup = self._get_soup_from_html_or_worker()
		return self.soup

	def get_html(self):
		if self.html is None and self._worker:
			self._get_html_from_worker()
		return self.html

	def _get_html_from_worker(self):
		"""
		Make the worker send the html it produced (when it's ready).
		"""
		self.pipe.send('!')
		self.html = self.pipe.recv()
		self.pipe.close()
		self._worker.join()
		self._worker = None
		return self.html

	def _get_soup_from_html_or_worker(self):
		if self.html is None:
			assert self._worker
			self.html = self._get_html_from_worker()
		if self.soup is None:
			self.soup = self.parser.parse(self.html)
		return self.soup

	@staticmethod
	def _load_async(path, logger, loader, preproc, parser, depth, pipe):
		"""
		Load, pre-process and parse an included file (leaf) and recursively load any other leafs.
		This should be run in a subprocess or thread, communicating through `pipe`.
		"""
		soup = Leaf._get_single(path=path, logger=logger, loader=loader, preproc=preproc, parser=parser, depth=depth)

		"""
		Includes
		Make sure to start all of them first and then start joining them, otherwise parallelism isn't used.
		"""
		incls = soup.find_all('include')
		if not Leaf._depth_limit(incls=incls, logger=logger, depth=depth):
			subleafs = []
			for incl in incls:
				if Leaf._with_src(incl=incl, logger=logger, path=path):
					sub = MultithreadLeaf(path=incl.attrs['src'], loader=loader, logger=logger, preproc=preproc,
					                      parser=parser, depth=0)
					subleafs.append((incl, sub))
			for incl, sub in subleafs:
				#todo: I should find some way to not have to parse this
				incl.replace_with(sub.get())

		"""
		Send back as html
		Did a benchmark; prettify & parsing again is 20-40% slower, but pickle doesn't always work due to recursion
		limit and according to StackOverflow other problems.
		Additionally, the result may have to go up several levels. If I can somehow keep it as html, it only needs to
		be converted back and forth once (pickle would need this at every level).
		"""
		html = soup.prettify()

		""" Wait (blocking) until the result is requested """
		pipe.recv()
		pipe.send(html)
		pipe.close()

	@staticmethod
	def _stop_worker(worker):
		if worker and worker.is_alive():
			worker.terminate()
