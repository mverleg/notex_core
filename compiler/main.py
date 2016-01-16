
#todo: need to load source before I can add argument parsers, but need source file argument and maybe more to be able to load
#todo: merge as late as possible to make caching more effective (before 'compile_2html' but possibly after 'tags')
#todo: cache should be nuked if packages change

#todo: add loader to settings and to pre_parse

from sys import argv
from compiler.arguments import pre_parse


"""
Pre-parse
Get path to input file (and parse some general options).
"""
pre_opts, rest_args = pre_parse(argv[1:])

"""
Configuration.
"""
from compiler.conf import settings
settings.verbosity = pre_opts.verbosity

"""
Must be combined:
1. Load files
2. Pre-process
3. Parse
(Since files must be parsed to find imports).
"""
#todo: this doesn't work, I can't set the parser directives in a file that needs to be parsed first




# arguments I
# load & structure
# get modules
# arguments II
# pre-process
# parse
# include
# load (install)
# substitute
# tags
# static files
# compile_2html
# postprocess

from compiler.loader import SourceLoader


SourceLoader(paths=())




