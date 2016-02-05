#!/usr/bin/env python

from argparse import ArgumentParser, SUPPRESS
from json import dump
from sys import stderr, stdout
from os import makedirs
from os.path import dirname, exists, basename
from pkg_resources import get_distribution, DistributionNotFound
from tempfile import tempdir
from compiler.server import launch_server


def pre_parse(args):
	"""
	Pre-parse path to input file (or some general options).
	"""

	if not args:
		args = ['--help']

	parser = ArgumentParser(add_help=False, usage='{0:s} CONFIGFILE --help'.format(basename(__file__)),
		description='Command line interface for NoTeX functionality.\n\nCommands provided by extensions will become visible if you provide an input file!',
		epilog='Provide an input file to load all commands provided by it\'s extensions.')

	parser.add_argument(dest='input', nargs='?', type=str, default=SUPPRESS,
		help='The main input file (you can also use --input PATH).')
	parser.add_argument('--input', dest='input', type=str, help=SUPPRESS)

	parser.add_argument('-v', '--verbose', dest='verbosity', action='count', default=0, help='Show more information (can be stacked, -vv).')
	parser.add_argument('--version', dest='show_version', action='store_true', help='Show version information and exit.')
	parser.add_argument('-h', '--help', dest='show_help', action='store_true', help='Show this help and exit.')

	opts, rest = parser.parse_known_args(args)

	if opts.show_help:
		parser.print_help()
		exit()

	if opts.show_version:
		try:
			version = get_distribution('notex').version  #todo package name
		except DistributionNotFound as err:
			stderr.write('Unable to obtain version through PyPi. Reason: {0:s}\n'.format(str(err)))
		else:
			stdout.write('{0:}\n'.format(version))
		exit()

	opts.verbosity += 1

	return opts, rest


def parse(args, settings):
	#todo: add one-letter shortcuts for most arguments
	if not args:
		args = ['--help']
	top_parser = ArgumentParser(description='Command line interface for NoTeX functionality. Commands provided by extensions are only visible if you provide an input file.')
	cmd_parsers = top_parser.add_subparsers(dest='action', help='What do you want NoTeX to do? Use `action --help` to get info about a specific action, e.g. compile_2html --help')

	compile = cmd_parsers.add_parser('compile_2html', help='Compile your NoTex input documents to presentable web documents (HTML/css/javascript...)')
	live = cmd_parsers.add_parser('live', help='Instead of compiling to a file, run a simple web server to display your document and recompile automatically on reload (not for use in production).')
	clean = cmd_parsers.add_parser('clean', help='Clean up temporary files.')
	show_conf = cmd_parsers.add_parser('show_conf', help='Print all configuration values including defaults to the screen.') # todo: this one should also be available at notexpm
	make_conf = cmd_parsers.add_parser('make_conf', help='Make a default configuration file.') # todo: this one should also be available at notexpm

	#top_parser.add_argument('--version', action='version', version=settings.get_version())

	for parser in [compile, live]:
		parser.add_argument(dest='input', nargs='?', type=str, default=SUPPRESS,
			help='The main input file to be compiled (you can also use --input NAME).')
		parser.add_argument('--input', dest='input', type=str, help=SUPPRESS)

	compile.add_argument(dest='output', nargs='?', type=str, default=SUPPRESS,
		help='The name of the output directory (or base name of the output file if --single-file is used) (you can also use --output NAME).')
	compile.add_argument('--output', dest='output', type=str, help=SUPPRESS)

	live.add_argument('--host', dest='host', type=str, default='localhost', help='The host on which the server should be reachable.')
	live.add_argument(dest='port', nargs='?', type=int, default=6689,
		help='The port on which the server should be reachable (on localhost) (you can also use --port NUMBER).')
	live.add_argument('--port', dest='port', type=int, default=SUPPRESS, help=SUPPRESS)
	live.add_argument('--browser', dest='open_browser', action='store_true', help='Try to open the page in the default browser.')

	for parser in [compile, live]:
		parser.add_argument('--review-mode', dest='review', action='store_true',
			help='Create the document in review mode, allowing readers to leave corrections and comments.')
		parser.add_argument('--use_version', dest='version', type=str, default='*',  # maybe use a fancy regex data type
			help='Request a specific compiler version, usable for consistent results. Likely to abort if the current version isn\'t correct.')
		parser.add_argument('--minimize', dest='minimize', action='store_true',
			help='Decrease the output filesize at the cost of readability by removing whitespace and merging styles and scripts. Side effects are possible; make sure to check!')  # e.g. js strict mode
		parser.add_argument('--remote', dest='remote', action='store_true',
			help='Don\'t download all the files but use remote versions. Decreases the number of files in the project, but will need internet to open the document, and raises some privacy concerns.')
		parser.add_argument('--single-file', dest='single', action='store_true',
			help='Attempt to merge all dependencies into a single file. This is not always possible, e.g. for large images other than svg.')

	for parser in [compile, live, clean]:
		parser.add_argument('--tempdir', dest='tempdir', type=str, default=tempdir,
			help='The directory to store temporary files')

	opts = top_parser.parse_args(args)
	print(opts)

	#todo: everything after this should probably be moved

	if opts.action in ['compile_2html', 'live']:
		if opts.minimize:
			print('--minimize is not yet implemented; option ignored')
		if opts.review:
			print('--review-mode is not yet implemented; option ignored')
		if opts.version != '*':
			print('--version is not yet implemented; option ignored')
		if opts.remote:
			print('--remote is not yet implemented; option ignored')
		if opts.single:
			print('--single-file is not yet implemented; option ignored')

	if opts.action == 'live':
		launch_server(opts.host, opts.port, opts.input, opts.open_browser)

	if opts.action == 'show_conf':  # todo: move this code somewhere else
		print(settings._get_config_string())
		exit()

	#todo: this shouldn't be happening here
	if opts.action == 'make_conf':
		conf_path = settings._get_user_config_location()
		if exists(conf_path):
			stderr.write('Configuration file already exists at "{0:s}"; not making any changes.\n'.format(conf_path))
			exit()
		else:
			conf = settings._get_defaults()  #todo: use a more minimal subset of defaults as initial config file
			makedirs(dirname(conf_path), exist_ok=True)
			with open(conf_path, 'w+') as fh:
				dump(conf, fp=fh, indent=2, sort_keys=False)
			exit()

	return opts


if __name__ == '__main__':
	stderr.write('This should not be called directly.\n')


