
from argparse import ArgumentParser
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from sys import argv, stdout
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
		self.logger.info('live directory is {0:s}'.format(self.output_dir), level=1)
		makedirs(self.output_dir, exist_ok=True, mode=0o700)
		chdir(self.output_dir)  #todo: is there a better way?
		self.do_compile()

	def do_compile(self):
		self.last_compile = datetime.now()
		section = Section(self.compile_file, loader=self.loader, logger=self.logger, cache=self.cache,
			compile_conf=self.compile_conf, document_conf=self.document_conf)
		render_dir(section=section, target_dir=self.output_dir,
			offline=True, minify=True, allow_symlink=True)

	def process_request(self, socket, client_address):
		if (datetime.now() - self.last_compile).total_seconds() > 3.0:
			#todo: relies on input path being absolute (which argparse currently makes sure of)
			#todo: should somehow not recompile until all requests including static files have completed (like only reload on html files)
			#todo: this shouldn't move all the static files, it should just serve them from their original location
			#todo: maybe this would be better in the handler (BaseHTTPRequestHandler.do_GET)
			try:
				self.do_compile()
			except Exception as err:
				with open(join(self.output_dir, 'index.html'), 'w+') as fh:
					fh.write(str(err))
				raise
		super(AutoCompileHTTPServer, self).process_request(socket, client_address)


def server(protocol='HTTP/1.0', port=8000, bind='localhost'):

	server_address = (bind, port)
	SimpleHTTPRequestHandler.protocol_version = protocol
	httpd = AutoCompileHTTPServer(server_address, SimpleHTTPRequestHandler)

	sa = httpd.socket.getsockname()
	stdout.write('Site online at http://{0:s}:{1:d}\n'.format(bind, port))
	try:
		httpd.serve_forever()
	except KeyboardInterrupt:
		print('\nKeyboard interrupt received, exiting.')
		httpd.server_close()
		exit(0)


if __name__ == '__main__':
	parser = ArgumentParser()
	parser.add_argument('--bind', default='localhost', metavar='ADDRESS',
		help='Specify alternate bind address [default: localhost]')
	parser.add_argument('--port', default=8000, metavar='PORT', type=int,
		help='Specify alternate port [default: 8000]')
	args = parser.parse_known_args()[0]
	server(port=args.port, bind=args.bind)


