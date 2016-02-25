
from argparse import ArgumentParser
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from sys import argv
from os import chdir, makedirs
from os.path import join
from compiler.arguments import pre_parse
from compiler.main import setup_singletons, render_dir
from compiler.section import Section
from compiler.utils import hash_str


class AutoCompileHTTPServer(ThreadingMixIn, HTTPServer):
	def __init__(self, *args, **kwargs):
		self.setup_compiler()
		super(AutoCompileHTTPServer, self).__init__(*args, **kwargs)

	def setup_compiler(self):
		pre_opts, rest_args = pre_parse(argv[1:])
		self.logger, self.compile_conf, self.document_conf, self.cache, self.loader = setup_singletons(opts=pre_opts)
		self.compile_file = pre_opts.input
		self.output_dir = join(self.compile_conf.TMP_DIR, 'live', hash_str(self.compile_file)[:8])
		makedirs(self.output_dir, exist_ok=True, mode=0o700)
		self.do_compile()

	def do_compile(self):
		self.last_compile = datetime.now()
		section = Section(self.compile_file, loader=self.loader, logger=self.logger, cache=self.cache,
			compile_conf=self.compile_conf, document_conf=self.document_conf)
		render_dir(section=section, target_dir=self.output_dir,
			offline=True, allow_symlink=True)
		chdir(self.output_dir)  #todo: is there a better way?

	def process_request(self, socket, client_address):
		if (datetime.now() - self.last_compile).total_seconds() > 2.0:
			#todo: this shouldn't move all the static files, it should just serve them from their original location
			#todo: maybe this would be better in the handler (BaseHTTPRequestHandler.do_GET)
			self.do_compile()
		super(AutoCompileHTTPServer, self).process_request(socket, client_address)


def server(protocol='HTTP/1.0', port=8000, bind='localhost'):

	server_address = (bind, port)
	SimpleHTTPRequestHandler.protocol_version = protocol
	httpd = AutoCompileHTTPServer(server_address, SimpleHTTPRequestHandler)

	sa = httpd.socket.getsockname()
	print('Serving HTTP on', sa[0], 'port', sa[1], '...')
	try:
		httpd.serve_forever()
	except KeyboardInterrupt:
		print('\nKeyboard interrupt received, exiting.')
		httpd.server_close()
		exit(0)


if __name__ == '__main__':
	parser = ArgumentParser()
	parser.add_argument('--bind', default='', metavar='ADDRESS',
		help='Specify alternate bind address [default: all interfaces]')
	parser.add_argument('--port', default=8000, metavar='PORT', type=int,
		help='Specify alternate port [default: 8000]')
	args = parser.parse_known_args()[0]
	server(port=args.port, bind=args.bind)


