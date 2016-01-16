
from collections import OrderedDict
from bs4 import BeautifulSoup


class Document():
	def __init__(self, top_node):
		self.top_node = top_node
		self.soup = top_node.merge()
		assert isinstance(self.soup, BeautifulSoup)


class SourceNode():
	"""
	Node in parser tree, corresponding to one source file.
	"""
	#todo: max depth, max total and/or prevent duplicates... maybe just max depth
	def __init__(self, path, parser, preprocessors, loader):
		"""
		For this node in the sources tree, load, parse, pre-process and then do the same for any includes.

		:param path: Path to the source file to be loaded.
		:param parser: A callable that converts text to a BeautifulSoup element tree.
		:param preprocessors: An iterable or preprocessors to apply to the text before parsing it.
		:param loader: A callable that loads a given path and returns the text contained within.
		"""
		self.path = path
		self.text = loader(self.path)  #todo: better error, showing all parent nodes
		for preprocessor in preprocessors:
			self.text = preprocessor(self.text)
		self.soup = parser(self.text)  # todo: better error
		""" Find & follow includes. """
		self.children = OrderedDict()
		for include in self.soup.find_all('include'):
			assert include.has_attr('src'), '' #todo
			node = SourceNode(include['src'], parser=parser, preprocessors=preprocessors, loader=loader)
			self.children[include] = node  #todo: hope it's hashable

	def merge(self):
		"""
		Join this node and all ancestors into one beautiful soup.
		"""
		#todo: on hold
		blended = self.soup
		for include, node in self.children.items():
			subsoup = node.merge()
			#todo: add a comment about the include when in debug mode?
			include.replace_with(subsoup)
		return blended


