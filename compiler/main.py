
from collections import OrderedDict
from sys import argv
from copy import copy
from compiler.arguments import pre_parse
from compiler._basic import Document
from compiler.conf import Settings
from compiler.log import BasicLogger
from compiler.loader import SourceLoader
from notexp.package import Package
from parser_lxml.parser import LXML_Parser


def compile_document(settings, path, depth=0):
	"""
	"""
	"""
	Load first source file.
	"""
	settings.logger.info('load "{0:s}"'.format(path), level=2)
	content = settings.loader.load(path)

	"""
	Pre-processing using a guessed list of pre-processors, since the real list is only available after parsing.
	"""
	preliminary_pre_processors = []  #todo
	for pre_processor in preliminary_pre_processors:
		settings.logger.info('  pre-process "{0:s}" using "{1:s}"'.format(path, pre_processor), level=2)
		content = pre_processor(content)

	"""
	Parsing using a guessed parser, since the real parser is not known yet.
	"""
	prelimiary_parser = LXML_Parser()
	soup = prelimiary_parser.parse(content)
	settings.logger.info(' parse "{0:s}"'.format(path), level=2)
	doc = Document(soup, None)

	"""
	Get modules...
	"""
	packages = []
	pack_tags = doc.soup.find_all('package')
	for pack_tag in pack_tags:
		package_args = copy(pack_tag.attrs)
		assert 'name' in package_args, 'package must specify a name in "{1:s}" [got "{0:s}"]' \
			.format('" & "'.join('{0:s}={1:}'.format(k, v) for k, v in pack_tag.attrs.items()), path)
		name = package_args.pop('name')
		version = package_args.pop('version', '==*')
		settings.logger.info('  load package {0:s}{1:s} for "{2:s}" with {3:d} arguments'.format(
			name, version, path, len(package_args)), level=2)
		pkg = Package(name=name, version=version, options=package_args).load()
		packages.append(pkg)
		pack_tag.extract()

	"""
	...and settings.
	"""
	total_conf = OrderedDict()
	config_tags = doc.soup.find_all('config')
	for conf_tag in config_tags:
		total_conf.update(conf_tag.attrs)
		conf_tag.extract()
	# print(total_conf)
	#todo: join with global settings

	# print(doc.soup)

	"""

	"""




		# <config base_path="value" property="value" />

# 		self.children = OrderedDict()
# 		for include in self.soup.find_all('include'):
# 			assert include.has_attr('src'), '' #todo
# 			node = SourceNode(include['src'], parser=parser, preprocessors=preprocessors, loader=loader)
# 			self.children[include] = node  #todo: hope it's hashable


def main():
	"""
	"""
	"""
	Command-line arguments.
	Get path to input file and handle some general options.
	"""
	pre_opts, rest_args = pre_parse(argv[1:])

	"""
	Configure some singleton configuration classes.
	"""
	logger = BasicLogger(verbosity=pre_opts.verbosity)
	logger.info('created logger', level=2)
	settings = Settings()
	settings.logger.info('load settings', level=2)
	settings.logger = logger
	logger.info('create file loader', level=2)
	settings.loader = SourceLoader(dir_paths=())

	"""
	Recursively compile all the documents.
	"""
	compile_document(settings, pre_opts.input)

if __name__ == '__main__':
	main()


