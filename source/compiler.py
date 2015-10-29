
from argparse import ArgumentParser


parser = ArgumentParser(description = 'Compile your NoTex input documents to presentable HTML!')
parser.add_argument(dest='input', nargs='?', default=None, help='The main input file to be compiled.')
parser.add_argument('--minimize', dest='minimize', type=bool, default=False, help='Decrease the output filesize.')

# - Single-file flag
# - Local vs cdn flag
# - include source
# - merge css/js

args = parser.parse_args()
print(args)


