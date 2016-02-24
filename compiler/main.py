
from itertools import chain
from sys import argv
from os import mkdir, getcwd
from os.path import realpath, dirname, exists, join
from shutil import rmtree
from compiler.arguments import pre_parse
from compiler.cache import DogpileAndFileCache
from compiler.conf import CompileSettings, DocumentSettings
from compiler.log import BasicLogger
from compiler.loader import SourceLoader
from compiler.section import Section
from compiler.utils import cd


def render_dir(packages, content, target_dir, *, offline=False, allow_symlink=False):
	#todo: This is just one render mode, and should become a package.
	with open(packages.get_template(), 'r') as fh:
		html = fh.read()
	if exists(target_dir):
		rmtree(target_dir)
	mkdir(target_dir)
	for resource in chain(packages.get_styles(offline=offline), packages.get_scripts(offline=offline),
			packages.get_static(offline=offline)):
		resource.copy(target_dir, allow_symlink=allow_symlink)
		# if resource.local_path:
		# 	#print('external: "{0:s}"'.format(resource.path))
		# 	pass
		# else:
		# 	#print('"{0:s}" -> "{1:s}"'.format(resource.full_path, join(target_dir, resource.path)))
		# 	makedirs(dirname(join(target_dir, resource.path)), exist_ok=True)
		# 	copy2(resource.full_path, join(target_dir, resource.path), follow_symlinks=True)
	styles = '\n\t\t'.join(style.html for style in packages.get_styles())
	scripts = '\n\t\t'.join(script.html for script in packages.get_scripts())
	document = html.format(content=content, styles=styles, scripts=scripts)
	with open(join(target_dir, 'index.html'), 'w+') as fh:
		fh.write(document)


def setup_singletons(opts):
	"""
	Configure some singleton configuration classes.
	"""
	logger = BasicLogger(verbosity=opts.verbosity)
	logger.info('created logger', level=2)
	compile_conf = CompileSettings(logger=logger, opts=opts)
	logger.info('load compile settings', level=2)
	document_conf = DocumentSettings(logger=logger)
	logger.info('load document settings', level=2)
	cache = DogpileAndFileCache(cache_dir=join(compile_conf.TMP_DIR, 'filecache'))
	logger.info('created cache binding', level=2)
	# settings.logger = logger
	logger.info('create file loader', level=2)
	loader = SourceLoader(dir_paths=(dirname(realpath(opts.input)),))
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
		content = section.get()
		target = target or join(getcwd(), 'my_document')
		render_dir(packages=section.packages, content=content, target_dir=target, offline=offline,
			allow_symlink=allow_symlink)


if __name__ == '__main__':
	do_compile()


