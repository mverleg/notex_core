
from argparse import ArgumentParser, FileType
from sys import argv
from tempfile import tempdir
from versions import regex_str


def parse(args):
	if len(args) == 1:
		args = [args[0], '--help']
	parser = ArgumentParser(description = 'Compile your NoTex input documents to presentable HTML!')
	parser.add_argument(dest='input', nargs='?', type=FileType('r'), default='main.html',
		help='The main input file to be compiled.')
	parser.add_argument(dest='output', nargs='?', type=str, default='document',
		help='The name of the output directory (or base name of the output file if --single-file is used).')
	parser.add_argument('--version', dest='version', type=regex_str(r'(?:\*|[0-9]+)'), default='*',
		help='Request a specific compiler version, usable for consistent results. Likely to abort if the current version isn\'t correct.')
	parser.add_argument('--minimize', dest='minimize', action='store_true',
		help='Decrease the output filesize at the cost of readability by removing whitespace and merging styles and scripts.')  #todo: maybe this should be default
	parser.add_argument('--remote', dest='remote', action='store_true',
		help='Don\'t download all the files but use remote versions. Decreases the number of files in the project, but will need internet to open the document.')
	parser.add_argument('--single-file', dest='single', action='store_true',
		help='Attempt to merge all dependencies into a single file. This is not always possible, e.g. for large images other than svg.')
	parser.add_argument('--clean', dest='clean', action='store_true',
		help='Do a clean compile, ignoring existing temporary files.')
	parser.add_argument('--tempdir', dest='tempdir', type=str, default=tempdir,
		help='The directory to store temporary files')
	return parser.parse_args(args)

if __name__ == '__main__':
	parse(argv)


