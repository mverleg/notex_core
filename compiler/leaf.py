
from threading import Thread
from bs4 import BeautifulSoup


class Leaf:
	"""
	Load and parse an included or rendered document.
	"""
	def __init__(self, path, loader, logger, preproc, parser, depth=0):
		self.soup = self._load(path=path, loader=loader, logger=logger, preproc=preproc, parser=parser, depth=depth)

	def get(self):
		return self.soup

	@staticmethod
	def _get_single(path, logger, loader, preproc, parser, depth):
		"""
		Load and pre-process a single source file.
		"""
		logger.info('{1:s}load "{0:s}"'.format(path, ' ' * depth), level=2)
		content = loader.load(path)

		""" Pre-processing """
		for pre_processor in preproc:
			logger.info(' {2:s}pre-process "{0:s}" using "{1:s}"'.format(path, pre_processor, ' ' * depth), level=2)
			content = pre_processor(content)

		""" Parse. """
		logger.info(' {1:s}parse "{0:s}"'.format(path, ' ' * depth), level=2)
		return parser.parse('<leaf origin="{0:s}">'.format(path) + content + '</leaf>')

	@staticmethod
	def _depth_limit(incls, logger, depth):
		if depth >= 10:
			logger.strict_fail('includes reached a depth of {0:d}; not going deeper'.format(depth))
			for incl in incls:
				incl.extract()
			return True
		return False

	@staticmethod
	def _with_src(incl, logger, path):
		if not 'src' in incl.attrs:
			logger.strict_fail('{0:s}: <include> tag without `src` attribute'.format(path))
			incl.extract()
			return False
		return True

	@staticmethod
	def _load(path, logger, loader, preproc, parser, depth):
		"""
		Load, pre-process and parse an included file (leaf) and recursively load any other leafs.
		"""
		""" Load & preproc this file. """
		soup = Leaf._get_single(path=path, logger=logger, loader=loader, preproc=preproc, parser=parser, depth=depth)

		""" Handle includes. """
		incls = soup.find_all('include')
		if not Leaf._depth_limit(incls=incls, logger=logger, depth=depth):
			for incl in incls:
				if Leaf._with_src(incl=incl, logger=logger, path=path):
					sub = Leaf(path=incl.attrs['src'], loader=loader, logger=logger, preproc=preproc,
						parser=parser, depth=depth + 1)
					incl.replace_with(sub.get())

		""" Return soup. """
		return soup.html.body.leaf


class MultiThreadedLeaf:
	"""
	Load and parse an included or rendered document.
	"""
	def __init__(self, path, loader, logger, preproc, parser, depth=0, incl_dict=None):
		if incl_dict is None:
			incl_dict = {}
		self.incl_dict = incl_dict
		self.path = path
		self.depth = depth
		self._worker = Thread(target=self._load_async, kwargs=dict(path=self.path, logger=logger, loader=loader,
			preproc=preproc, parser=parser, depth=self.depth, incl_dict=incl_dict), daemon=True)
		self._worker.start()
		self.soup = None

	def get(self):
		"""
		Join the worker threads (they store the results). Merge all the leafs if this is the top node.
		"""
		if self._worker is not None:
			self._worker.join()
			self._worker = None
		if self.soup is None and self.depth == 0:
			self.soup = self._substitute_includes(self.incl_dict[self.path])
		return self.soup

	def _substitute_includes(self, soup):
		"""
		Recursively replace <include> tags in soup by their already-loaded content from self.incl_dict.
		"""
		for incl in soup.find_all('include'):
			assert incl.attrs['src'] in self.incl_dict, '{0:s} should exist in incl_dict but it only has [{1:}]'\
				.format(incl.attrs['src'], ', '.join(self.incl_dict))
			content = self.incl_dict[incl.attrs['src']]
			incl.replace_with(self._substitute_includes(content))
		return soup

	@staticmethod
	def _load_async(path, logger, loader, preproc, parser, depth, incl_dict):
		"""
		Load, pre-process and parse an included file (leaf). Recursively load other leafs but store them in a dict
		as updating the main tree concurrently might cause problems.
		"""
		""" Check the file hasn't been processed yet (not thread-safe, but it's not dangerous). """
		if path in incl_dict:
			logger.info('{0:s}load "{1:s}": already loading/loaded'.format(' ' * depth, path))
			return
		incl_dict[path] = None

		""" Load & preproc this file. """
		soup = Leaf._get_single(path=path, logger=logger, loader=loader, preproc=preproc, parser=parser, depth=depth)

		""" Handle includes. """
		incls = soup.find_all('include')
		subleafs = []
		if not Leaf._depth_limit(incls=incls, logger=logger, depth=depth):
			for incl in incls:
				if Leaf._with_src(incl=incl, logger=logger, path=path):
					sub = MultiThreadedLeaf(path=incl.attrs['src'], loader=loader, logger=logger, preproc=preproc,
						parser=parser, depth=depth + 1, incl_dict=incl_dict)
					subleafs.append(sub)

		""" Add soup. """
		incl_dict[path] = soup.html.body.leaf

		""" Don't stop before subleafs are ready. """
		for sub in subleafs:
			sub.get()

	# def get(self):
	# 	return self.soup
	#
	# @staticmethod
	# def _get_single(path, logger, loader, preproc, parser, depth):
	# 	"""
	# 	Load and pre-process a single source file.
	# 	"""
	# 	logger.info('{1:s}load "{0:s}"'.format(path, ' ' * depth), level=2)
	# 	content = loader.load(path)
	#
	# 	""" Pre-processing """
	# 	for pre_processor in preproc:
	# 		logger.info(' {2:s}pre-process "{0:s}" using "{1:s}"'.format(path, pre_processor, ' ' * depth), level=2)
	# 		content = pre_processor(content)
	# 	return content
	#
	# @staticmethod
	# def depth_limit(incls, logger, depth):
	# 	if depth >= 10:
	# 		logger.strict_fail('includes reached a depth of {0:d}; not going deeper'.format(depth))
	# 		for incl in incls:
	# 			incl.extract()
	# 		return True
	# 	return False
	#
	# @staticmethod
	# def with_src(incl, logger, path):
	# 	if not 'src' in incl.attrs:
	# 		logger.strict_fail('{0:s}: <include> tag without `src` attribute'.format(path))
	# 		return False
	# 	return True
	#
	# @staticmethod
	# def _load(path, logger, loader, preproc, parser, depth):
	# 	"""
	# 	Load, pre-process and parse an included file (leaf) and recursively load any other leafs.
	# 	"""
	# 	""" Load & preproc this file. """
	# 	html = Leaf._get_single(path=path, logger=logger, loader=loader, preproc=preproc, parser=parser, depth=depth)
	#
	# 	""" Parsing """
	# 	logger.info(' {1:s}parse "{0:s}"'.format(path, ' ' * depth), level=2)
	# 	soup = parser.parse(html)
	#
	# 	""" Handle includes. """
	# 	incls = soup.find_all('include')
	# 	if not Leaf.depth_limit(incls=incls, logger=logger, depth=depth):
	# 		for incl in incls:
	# 			if Leaf.with_src(incl=incl, logger=logger, path=path):
	# 				sub = Leaf(path=incl.attrs['src'], loader=loader, logger=logger, preproc=preproc,
	# 					parser=parser, depth=0).get()
	# 				incl.replace_with(sub)
	#
	# 	""" Return soup """
	# 	return soup



class MultiProcessLeaf:
	"""
	Load and parse an included or rendered document, using multiple threads for reading.
	"""
	#todo: make sure everything is thread-safe (like lock before parsing?)
	#todo: local data threading.local()
	def __init__(self, path, loader, logger, preproc, parser, depth=0, incl_dict=None):
		self.depth = depth
		if incl_dict is None:
			incl_dict = {}
		self.incl_dict = incl_dict
		self._worker = Thread(target=self._load_async, kwargs=dict(path=path, loader=loader, logger=logger,
			preproc=preproc, parser=parser, depth=self.depth, incl_dict=self.incl_dict), daemon=True)
		self._worker.start()
		self.html = self.soup = None

	def get(self):
		print('waiting for worker')
		self._worker.join()
		if self.html is None:
			print('')
			self.soup = BeautifulSoup('<div />', 'lxml')
			# self.soup = self._get_soup_from_html_or_worker()
		return self.soup

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

	@staticmethod
	def _load_async(path, logger, loader, preproc, parser, depth, incl_dict):
		"""
		Load, pre-process and parse an included file (leaf) and recursively load any other leafs.
		This should be run in a thread, communicating through a shared dictionary.
		"""
		""" Load and pre-process. """
		html = Leaf._get_single(path=path, logger=logger, loader=loader, preproc=preproc, parser=parser, depth=depth)

		""" Parsing """
		logger.info(' {1:s}find includes "{0:s}"'.format(path, ' ' * depth), level=2)
		incl_soup = parser.parse(html, only='include')

		""" Handle includes. """
		if not Leaf._depth_limit(incls=incl_soup, logger=logger, depth=depth):
			for incl in incl_soup:
				if Leaf._with_src(incl=incl, logger=logger, path=path):
					sub = MultiThreadedLeaf(path=incl.attrs['src'], loader=loader, logger=logger, preproc=preproc,
						parser=parser, depth=0, incl_dict=incl_dict).get()
					# incl.replace_with(sub)
					incl_dict[path] = sub

		""" Return soup """
		return incl_dict


