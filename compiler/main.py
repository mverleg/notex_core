
from sys import argv
from compiler.arguments import pre_parse
from compiler.conf import Settings
from compiler.log import BasicLogger
from compiler.loader import SourceLoader



"""
arguments I
FOR document:
	pre-process I (defaults or cached)
	parse I (defaults or cached)
	get modules & settings
	arguments II
	IF pre-processing or parsing is different:
		pre-process II (completely redo)
		parse II (complete redo, ignore requirements)
	include >>
	tags
	substitutions
linking
external files
rendering
post-process
"""


"""
Command-line arguments
Get path to input file and handle some general options.
"""
pre_opts, rest_args = pre_parse(argv[1:])

"""
Configure settings including logger.
"""
logger = BasicLogger(verbosity=pre_opts.verbosity)
logger.info('created logger', level=2)
settings = Settings()
settings.logger = logger
settings.logger.info('loaded settings & logger', level=2)

"""
Load first source file
"""
SourceLoader(paths=())


"""
Must be combined:
1. Load files
2. Pre-process
3. Parse
(Since files must be parsed to find imports).
"""









