
from argparse import ArgumentParser
from http.server import SimpleHTTPRequestHandler, HTTPServer
from os import getcwd, chdir
from tempfile import mkdtemp
from compiler.main import do_compile


class AutoCompileHTTPServer(HTTPServer):
	def __init__(self, *args, **kwargs):
		self.source_dir = getcwd()
		self.target_dir = mkdtemp(prefix='notex')
		chdir(self.target_dir)  #todo: is there a better way?
		super(AutoCompileHTTPServer, self).__init__(*args, **kwargs)

	def process_request(self, request, client_address):
		do_compile(source=self.source_dir, target=self.target_dir)
		super(AutoCompileHTTPServer, self).process_request(request, client_address)


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


