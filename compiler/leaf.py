
from functools import partial
from multiprocessing import Process, Pipe
from time import sleep
from parser_lxml.parser import LXML_Parser
from atexit import register


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
		Load, pre-process and parse a single source file non-recursively.
		"""
		logger.info('{1:s}load "{0:s}"'.format(path, ' ' * depth), level=2)
		content = loader.load(path)

		""" Pre-processing """
		for pre_processor in preproc:
			logger.info(' {2:s}pre-process "{0:s}" using "{1:s}"'.format(path, pre_processor, ' ' * depth), level=2)
			content = pre_processor(content)

		""" Parsing """
		logger.info(' {1:s}parse "{0:s}"'.format(path, ' ' * depth), level=2)
		return parser.parse(content)

	@staticmethod
	def depth_limit(incls, logger, depth):
		if depth >= 10:
			logger.strict_fail('includes reached a depth of {0:d}; not going deeper'.format(depth))
			for incl in incls:
				incl.extract()
			return True
		return False

	@staticmethod
	def with_src(incl, logger, path):
		if not 'src' in incl.attrs:
			logger.strict_fail('{0:s}: <include> tag without `src` attribute'.format(path))
			return False
		return True

	@staticmethod
	def _load(path, logger, loader, preproc, parser, depth):
		"""
		Load, pre-process and parse an included file (leaf) and recursively load any other leafs.
		"""
		""" Handle this file. """
		soup = Leaf._get_single(path=path, logger=logger, loader=loader, preproc=preproc, parser=parser, depth=depth)

		""" Handle includes. """
		incls = soup.find_all('include')
		if not Leaf.depth_limit(incls=incls, logger=logger, depth=depth):
			for incl in incls:
				if Leaf.with_src(incl=incl, logger=logger, path=path):
					sub = Leaf(path=incl.attrs['src'], loader=loader, logger=logger, preproc=preproc,
						parser=parser, depth=0).get()
					incl.replace_with(sub)

		""" Return soup """
		return soup


class ParallelLeaf:
	"""
	Load and parse an included or rendered document, using a worker process.
	"""
	def __init__(self, path, loader, logger, preproc, parser, depth=0):
		#todo: how to deal with errors?
		self.pipe, remote_pipe = Pipe()
		self.parser = LXML_Parser()
		self._worker = Process(target=self._load_async, kwargs=dict(path=path, loader=loader, logger=logger,
			preproc=preproc, parser=self.parser, depth=depth, pipe=remote_pipe))
		self._worker.start()
		register(partial(ParallelLeaf._stop_worker, self._worker))
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
		if not Leaf.depth_limit(incls=incls, logger=logger, depth=depth):
			subleafs = []
			for incl in incls:
				if Leaf.with_src(incl=incl, logger=logger, path=path):
					sub = ParallelLeaf(path=incl.attrs['src'], loader=loader, logger=logger, preproc=preproc,
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


