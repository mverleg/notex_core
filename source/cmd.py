
from argparse import ArgumentParser, FileType, SUPPRESS
from json import dump
from os import makedirs
from os.path import dirname, exists
from sys import argv, stderr
from tempfile import tempdir
from conf import settings


def parse(args):
	#todo: add one-letter shortcuts for most arguments
	if not args:
		args = ['--help']
	top_parser = ArgumentParser(description='Command line interface for NoTeX functionality.')
	cmd_parsers = top_parser.add_subparsers(dest='action', help='What do you want NoTeX to do? Use `action --help` to get info about a specific action, e.g. compile --help')

	compile = cmd_parsers.add_parser('compile', help='Compile your NoTex input documents to presentable web documents (HTML/css/javascript...)')
	live = cmd_parsers.add_parser('live', help='Instead of compiling to a file, run a simpleweb server to display your document and recompile automatically on reload (not for use in production).')
	clean = cmd_parsers.add_parser('clean', help='Clean up temporary files.')
	show_conf = cmd_parsers.add_parser('show_conf', help='Print all configuration values including defaults to the screen.') # todo: this one should also be available at notexpm
	make_conf = cmd_parsers.add_parser('make_conf', help='Make a default configuration file.') # todo: this one should also be available at notexpm

	top_parser.add_argument('--version', action='version', version=settings.get_version())

	for parser in [compile, live]:
		parser.add_argument(dest='input', nargs='?', type=str, default=SUPPRESS,
			help='The main input file to be compiled (you can also use --input NAME).')
		parser.add_argument('--input', dest='input', type=str, help=SUPPRESS)

	compile.add_argument(dest='output', nargs='?', type=str, default=SUPPRESS,
		help='The name of the output directory (or base name of the output file if --single-file is used) (you can also use --output NAME).')
	compile.add_argument('--output', dest='output', type=str, help=SUPPRESS)

	live.add_argument(dest='port', nargs='?', type=int, default=SUPPRESS,
		help='The port on which the server should be reachable (on localhost) (you can also use --port NUMBER).')
	live.add_argument('--port', dest='port', type=int, default=6689, help=SUPPRESS)

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

	if opts.action in ['compile', 'live']:
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

	if opts.action == 'show_conf':  # todo: move this code somewhere else
		print(settings.get_config_string())
		exit()

	if opts.action == 'make_conf':
		conf_path = settings.get_user_config_location()
		if exists(conf_path):
			stderr.write('Configuration file already exists at "{0:s}"; not making any changes.\n'.format(conf_path))
			exit()
		else:
			conf = settings.get_defaults()  #todo: use a more minimal subset of defaults as initial config file
			makedirs(dirname(conf_path), exist_ok=True)
			with open(conf_path, 'w+') as fh:
				dump(conf, fp=fh, indent=2, sort_keys=False)
			exit()

	print(opts)

	return opts


if __name__ == '__main__':
	parse(argv[1:])


