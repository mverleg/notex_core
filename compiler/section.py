
from inspect import signature
from copy import copy
from os.path import dirname, basename
from compiler.leaf import MultiThreadedLeaf
from compiler.utils import hash_str, InvalidDocumentError
from notexp.package import Package
from notexp.packages import PackageList
from notexp.resource import StaticResource, StyleResource, ScriptResource, get_resources, Resource
from parse_render_lxml.parser import LXML_Parser


class Section:
	"""
	Handle (load, pre-process, parse, include, arguments, tags, substitutions) a rendered document.
	"""
	resource_types = {
		'static': StaticResource,
		'styles': StyleResource,
		'scripts': ScriptResource,
	}

	def __init__(self, path, loader, logger, cache, compile_conf, document_conf):
		#todo: depth limit
		self.path = path
		self.leaf = MultiThreadedLeaf(path=path, loader=loader, logger=logger, preproc=(), parser=LXML_Parser())
		self.soup = self.leaf.get()
		self.logger = logger
		self.cache = cache
		self.compile_conf = compile_conf
		self.document_conf = document_conf  # unused?
		self.packages = self.get_packages(self.soup)
		self.styles, self.scripts, self.static = self.get_resources(self.soup)

	def get_packages(self, soup):
		packages = []
		pack_tags = soup.find_all('package')
		for pack_tag in pack_tags:
			package_args = copy(pack_tag.attrs)
			assert 'name' in package_args, '<package> must specify a name [got "{0:s}"]' \
				.format('" & "'.join('{0:s}={1:}'.format(k, v) for k, v in pack_tag.attrs.items()))
			name = package_args.pop('name')
			version = package_args.pop('version', '==*')
			print('  load package {0:s}{1:s} with {2:d} arguments'.format(name, version, len(package_args)))
			pkg = Package(name=name, version=version, options=package_args, logger=self.logger, cache=self.cache,
				compile_conf=self.compile_conf).load()
			packages.append(pkg)
			pack_tag.extract()
		return PackageList(packages, logger=self.logger, cache=self.cache, compile_conf=self.compile_conf,
			document_conf=self.document_conf)

	def get_resources(self, soup):
		conf = {nm: [] for nm in self.resource_types.keys()}
		resource_tags = soup.find_all('resource')
		allowed_attrs = set(param.name for param in signature(Resource.__init__).parameters.values() if param.kind == param.KEYWORD_ONLY)
		for resource_tag in resource_tags:
			resource = copy(resource_tag.attrs)
			resource_type = resource.pop('type', 'static')
			if resource_type not in self.resource_types:
				raise InvalidDocumentError('<resource> type must be one of {0:} if specified'
					.format(', '.join(self.resource_types.keys())))
			if resource.keys() - allowed_attrs:
				raise InvalidDocumentError(('did not recognize these attributes given to <resource>: [{0:s}]; known arguments'
					' are [{1:s}]').format(', '.join(resource.keys() - allowed_attrs), ', '.join(allowed_attrs)))
			conf[resource_type].append(resource)
			resource_tag.extract()
		section_name = 'section_{0:8s}'.format(hash_str(self.path))
		section_dir = dirname(self.path)
		return get_resources(group_name=section_name, path=section_dir,
			logger=self.logger, cache=self.cache, compile_conf=self.compile_conf, style_conf=conf['styles'],
			script_conf=conf['scripts'], static_conf=conf['static'], note='from section {0:s}'.format(basename(self.path))
		)[1:]

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

	def get_template(self):
		raise NotImplementedError('Section objects do not have templates, just styles, scripts and static resources')

	def _get_resources(self, attr_name, offline, minify):
		resources = []
		for resource in getattr(self, attr_name):
			if offline:
				resource.make_offline()
			if minify:
				resource.minify()
			resources.append(resource)
		return resources

	def get_styles(self, offline=False, minify=False):
		return self._get_resources('styles', offline=offline, minify=minify)

	def get_scripts(self, offline=False, minify=False):
		return self._get_resources('scripts', offline=offline, minify=minify)

	def get_static(self, offline=False, minify=False):
		return self._get_resources('static', offline=offline, minify=minify)


class UsefulButUnusedExampleForMultiprocessing:  #todo: change to section
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


