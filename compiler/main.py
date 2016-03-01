

from time import time
t = time()
from itertools import chain
from sys import argv
from os import mkdir, getcwd
from os.path import realpath, dirname, exists, join
from shutil import rmtree
from compiler.arguments import pre_parse
from compiler.cache import DogpileAndFileCache
from compiler.conf import CompileSettings, DocumentSettings
from compiler.log import BasicLogger, Ticker
from compiler.loader import SourceLoader
from compiler.section import Section
from compiler.utils import cd, hash_str
print('{1:s} imports took {0:.0f}ms'.format(1000 * (time() - t), __name__))


def render_dir(section, target_dir, *, offline=True, minify=True, allow_symlink=False, remove_existing=False):
	#todo: This is just one render mode, and should become a package.
	content = section.get()
	packages = section.packages
	with open(packages.get_template().full_path, 'r') as fh:
		html = fh.read()
	if exists(target_dir):
		if remove_existing:
			rmtree(target_dir)
	else:
		mkdir(target_dir)
	modes = dict(offline=offline, minify=minify)
	for resource in chain(packages.yield_styles(**modes), packages.yield_scripts(**modes),
			packages.yield_static(**modes), section.yield_styles(**modes),
			section.yield_scripts(**modes), section.yield_static(**modes)):
		#todo: this could be parallel (and it's IO that's pretty slow on new documents)
		resource.copy(target_dir, allow_symlink=allow_symlink)
	styles = '\n\t\t'.join(style.html for style in chain(packages.yield_styles(), section.yield_styles()))
	scripts = '\n\t\t'.join(script.html for script in chain(packages.yield_scripts(), section.yield_scripts()))
	#todo: this will break if any code generates curly brackets dynamically, right?
	document = html.format(content=content, styles=styles, scripts=scripts)
	# linking todo: linkers should be for all packages, not just the top section
	#todo: this seems sooo wasteful, could take the majority of time on big documents
	#todo: also is ruins any custom parsers and (without extra effort) renderers
	linkers = tuple(packages.yield_linkers())
	if linkers:
		soup = packages.get_parser().parse(document)
		for linker in linkers:
			linker(soup)
		document = packages.get_renderer().render(soup)
	with open(join(target_dir, 'index.html'), 'w+') as fh:
		fh.write(document)


def setup_singletons(opts):
	"""
	Configure some singleton configuration classes.
	"""
	tick = Ticker()
	logger = BasicLogger(verbosity=opts.verbosity)
	logger.info('created logger ({0:.0f}ms)'.format(tick()), level=2)
	session_hash = hash_str(opts.input)
	compile_conf = CompileSettings(logger=logger, opts=opts, session=session_hash)
	logger.info('load compile settings ({0:.0f}ms)'.format(tick()), level=2)
	document_conf = DocumentSettings(logger=logger)
	logger.info('load document settings ({0:.0f}ms)'.format(tick()), level=2)
	cache = DogpileAndFileCache(cache_dir=join(compile_conf.TMP_DIR, 'filecache'))
	logger.info('created cache binding ({0:.0f}ms)'.format(tick()), level=2)
	loader = SourceLoader(dir_paths=(dirname(realpath(opts.input)),))
	logger.info('create file loader ({0:.0f}ms)'.format(tick()), level=2)
	# parser = LXML_Parser()
	return logger, compile_conf, document_conf, cache, loader


def do_compile(source=None, target=None, offline=True, allow_symlink=False):
	#todo: target from arguments
	"""
	"""
	with cd(source or getcwd()):
		"""
		Command-line arguments.
		Get path to input file and handle some general options.
		"""
		pre_opts, rest_args = pre_parse(argv[1:])

		logger, compile_conf, document_conf, cache, loader = setup_singletons(opts=pre_opts)

		section = Section(pre_opts.input, loader=loader, logger=logger, cache=cache, compile_conf=compile_conf,
			document_conf=document_conf)
		target = target or join(getcwd(), 'my_document')
		render_dir(section=section, target_dir=target, offline=offline,
			allow_symlink=allow_symlink)
		print('compiled document at file://{0:s}/index.html'.format(target))


if __name__ == '__main__':
	do_compile()


