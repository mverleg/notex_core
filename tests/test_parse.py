
from compiler.main import parse_to_document, Document, pretty_render


def test_parse_demo():
	path = 'demodoc/main.html'
	doc = parse_to_document(path)
	res = pretty_render(doc)
	print(res)
	assert False
	assert isinstance(doc, Document)


