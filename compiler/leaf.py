
from threading import Thread


class Leaf:
	"""
	Load and parse an included or rendered document.
	"""
	def __init__(self, path, loader, logger, pre_processors, parser, depth=0):
		self.soup = self._load(path=path, loader=loader, logger=logger, pre_processors=pre_processors, parser=parser, depth=depth)

	def get(self):
		return self.soup

	@staticmethod
	def _get_single(path, logger, loader, pre_processors, parser, depth):
		"""
		Load and pre-process a single source file.
		"""
		logger.info('{1:s}load "{0:s}"'.format(path, ' ' * depth), level=2)
		content = loader.load(path)

		""" Pre-processing """
		for pre_processor in pre_processors:
			logger.info(' {2:s}pre-process "{0:s}" using "{1:}"'.format(path, pre_processor, ' ' * depth), level=2)
			content = pre_processor(content)
			assert isinstance(content, str), 'pre-processor "{0:}" returned a non-string object {1:}'.format(
				pre_processor, content)

		""" Parse. """
		logger.info(' {1:s}parse "{0:s}"'.format(path, ' ' * depth), level=2)
		return parser.parse('<notex-leaf origin="{0:s}">'.format(path) + content + '</notex-leaf>')

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
	def _load(path, logger, loader, pre_processors, parser, depth):
		"""
		Load, pre-process and parse an included file (leaf) and recursively load any other leafs.
		"""
		""" Load & pre-process this file. """
		soup = Leaf._get_single(path=path, logger=logger, loader=loader, pre_processors=pre_processors, parser=parser, depth=depth)

		""" Handle includes. """
		incls = soup.find_all('include')
		if not Leaf._depth_limit(incls=incls, logger=logger, depth=depth):
			for incl in incls:
				if Leaf._with_src(incl=incl, logger=logger, path=path):
					sub = Leaf(path=incl.attrs['src'], loader=loader, logger=logger, pre_processors=pre_processors,
					           parser=parser, depth=depth + 1)
					incl.replace_with(sub.get())

		""" Return soup. """
		return soup.html.body.contents[0]


class MultiThreadedLeaf:
	"""
	Load and parse an included or rendered document.
	"""
	def __init__(self, path, loader, logger, pre_processors, parser, depth=0, incl_dict=None):
		if incl_dict is None:
			incl_dict = {}
		self.incl_dict = incl_dict
		self.path = path
		self.depth = depth
		self._worker = Thread(target=self._load_async, kwargs=dict(path=self.path, logger=logger, loader=loader,
			pre_processors=pre_processors, parser=parser, depth=self.depth, incl_dict=incl_dict), daemon=True)
		self._worker.start()
		self.soup = None

	def get(self):
		"""
		Join the worker threads (they store the results). Merge all the leafs if this is the top node. Returns soup.
		"""
		if self._worker is not None:
			self._worker.join()
			self._worker = None
		if self.soup is None and self.depth == 0:
			#todo: should not behave differently based on depth; just make a special method for recursion other than .get()
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
	def _load_async(path, logger, loader, pre_processors, parser, depth, incl_dict):
		"""
		Load, pre-process and parse an included file (leaf). Recursively load other leafs but store them in a dict
		as updating the main tree concurrently might cause problems.
		"""
		""" Check the file hasn't been processed yet (not thread-safe, but it's not dangerous). """
		if path in incl_dict:
			logger.info('{0:s}load "{1:s}": already loading/loaded'.format(' ' * depth, path))
			return
		incl_dict[path] = None

		""" Load & pre-process this file. """
		soup = Leaf._get_single(path=path, logger=logger, loader=loader, pre_processors=pre_processors, parser=parser, depth=depth)

		""" Handle includes. """
		incls = soup.find_all('include')
		subleafs = []
		if not Leaf._depth_limit(incls=incls, logger=logger, depth=depth):
			for incl in incls:
				if Leaf._with_src(incl=incl, logger=logger, path=path):
					sub = MultiThreadedLeaf(path=incl.attrs['src'], loader=loader, logger=logger, pre_processors=pre_processors,
					                        parser=parser, depth=depth + 1, incl_dict=incl_dict)
					subleafs.append(sub)

		""" Add soup. """
		incl_dict[path] = soup.html.body.contents[0]

		""" Don't stop before subleafs are ready. """
		for sub in subleafs:
			sub.get()


