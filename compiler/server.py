
import webbrowser
from time import sleep
from functools import partial
from http.server import SimpleHTTPRequestHandler
from mimetypes import guess_type
from socketserver import ThreadingTCPServer
from threading import Thread
from os.path import basename, join, getsize


class NotexHandler(SimpleHTTPRequestHandler):
	def do_GET(self):
		path = self.path  #.rstrip('/')
		if path in ('', '/'):
			self.serve_document(path)
		elif path.split('.')[-1] in ('ico', 'png', 'jpg', 'gif', 'css', 'js'):
			self.serve_static(path)
		else:
			self.send_response(307)
			self.send_header('Location', '/')
			self.end_headers()

	def serve_document(self, path):
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.end_headers()
		self.wfile.write(bytes('hello world', 'UTF-8'))

	def serve_static(self, path):
		filepath = join('static', path.lstrip('/'))
		mime = guess_type(basename(filepath))
		self.send_response(200)
		self.send_header('Content-type', mime[0])
		self.send_header('Content-length', getsize(filepath))
		self.end_headers()
		with open(filepath, 'rb') as fh:
			self.wfile.write(fh.read())


def open_in_browser(url):
	sleep(0.5)
	webbrowser.open(url, new=False, autoraise=True)


def launch_server(host, port, input, show=True):
	print('launching server at {0:s}:{1:d} showing "{2:s}"'.format(host, port, input))
	ThreadingTCPServer.allow_reuse_address = True
	httpd = ThreadingTCPServer((host, port), NotexHandler)
	if show:
		thrd = Thread(target=partial(open_in_browser, url='http://{0:s}:{1:d}'.format(host, port)))
		thrd.start()
	try:
		httpd.serve_forever()
	except KeyboardInterrupt:
		httpd.server_close()


