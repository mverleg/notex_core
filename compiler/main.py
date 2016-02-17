
from itertools import chain
from collections import OrderedDict
from sys import argv
from copy import copy
from os import mkdir, getcwd, makedirs
from os.path import realpath, dirname, exists, join
from shutil import copyfile, rmtree
from compiler.arguments import pre_parse
from compiler.conf import CompileSettings, DocumentSettings
from compiler.log import BasicLogger
from compiler.loader import SourceLoader
from compiler.section import Section
from compiler.utils import cd
from notexp.package import Package
from parse_render__lxml.parser import LXML_Parser


def compile_document(path, logger, loader, depth=0):
	"""
	"""
	"""
	Load first source file.
	"""
	logger.info('load "{0:s}"'.format(path), level=2)
	content = loader._load(path)

	"""
	Pre-processing using a guessed list of pre-processors, since the real list is only available after parsing.
	"""
	preliminary_pre_processors = []  #todo
	for pre_processor in preliminary_pre_processors:
		logger.info('  pre-process "{0:s}" using "{1:s}"'.format(path, pre_processor), level=2)
		content = pre_processor(content)

	"""
	Parsing using a guessed parser, since the real parser is not known yet.
	"""
	prelimiary_parser = LXML_Parser()
	soup = prelimiary_parser.parse(content)
	logger.info(' parse "{0:s}"'.format(path), level=2)
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
		logger.info('  load package {0:s}{1:s} for "{2:s}" with {3:d} arguments'.format(
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

# 		self.children = OrderedDict()
# 		for include in self.soup.find_all('include'):
# 			assert include.has_attr('src'), '' #todo
# 			node = SourceNode(include['src'], parser=parser, preprocessors=preprocessors, loader=loader)
# 			self.children[include] = node  #todo: hope it's hashable

def render_dir(packages, content, target_dir, offline=False):
	#todo: This is just one render mode, and should become a package.
	with open(packages.get_template(), 'r') as fh:
		html = fh.read()
	if exists(target_dir):
		rmtree(target_dir)
	mkdir(target_dir)
	for resource in chain(packages.get_styles(offline=offline), packages.get_scripts(offline=offline),
			packages.get_static(offline=offline)):
		if resource.external:
			print('external: "{0:s}"'.format(resource.path))
		else:
			print('"{0:s}" -> "{1:s}"'.format(resource.full_path, join(target_dir, resource.path)))
			makedirs(dirname(join(target_dir, resource.path)), exist_ok=True)
			copyfile(resource.full_path, join(target_dir, resource.path), follow_symlinks=True)
	styles = '\n\t\t'.join(style.html for style in packages.get_styles())
	scripts = '\n\t\t'.join(script.html for script in packages.get_scripts())
	document = html.format(content=content, styles=styles, scripts=scripts)
	with open(join(target_dir, 'index.html'), 'w+') as fh:
		fh.write(document)


def do_compile(source=None, target=None):
	#todo: target from arguments
	"""
	"""
	with cd(source or getcwd()):
		"""
		Command-line arguments.
		Get path to input file and handle some general options.
		"""
		pre_opts, rest_args = pre_parse(argv[1:])
		path = pre_opts.input

		"""
		Configure some singleton configuration classes.
		"""
		logger = BasicLogger(verbosity=pre_opts.verbosity)
		logger.info('created logger', level=2)
		compile_settings = CompileSettings()
		document_settings = DocumentSettings()
		logger.info('load settings', level=2)
		# settings.logger = logger
		logger.info('create file loader', level=2)
		loader = SourceLoader(dir_paths=(dirname(realpath(path)),))
		# parser = LXML_Parser()

		section = Section(path, loader=loader, logger=logger)
		content = section.get()
		target = target or join(getcwd(), 'my_document')
		render_dir(packages=section.packages, content=content, target_dir=target, offline=True)


if __name__ == '__main__':
	do_compile()


