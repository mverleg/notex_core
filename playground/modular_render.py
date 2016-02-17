
"""
Goals:
	1. Breat a soup into components, render them separately and combine them.
	2. Combine an (outer) soup and (inner) html into either a soup or html without rendering inner one.
Both of which'd be achieved if I can do the second one.
"""
from time import time

from collections import OrderedDict
from bs4 import BeautifulSoup, NavigableString
from re import sub


html = """
<section>
	<article id="alpha" />
	<div><div><div><div><div><div>
		<article id="beta">
			<h1>{Hi}</h1>
			<p>hi</p><p>hi</p><p>hi</p><p>hi</p><p>hi</p><p>hi</p><p>hi</p><p>hi</p><p>hi</p><p>hi</p>
			<div>
				<article id="gamma">
					<p>Yolooooooooooooooooooooo{0}</p>
					<p>hi</p><p>hi</p><p>hi</p><p>hi</p><p>hi</p><p>hi</p><p>hi</p><p>hi</p><p>hi</p><p>hi</p>
					<p>Yol{0}.</p>
				</article>
			<div>
		</article>
	</div></div></div></div></div></div>
</section>
"""

def regx_format(input):
	esc_html = sub(r'({|})', r'\1\1', input)
	soup = BeautifulSoup(esc_html, 'lxml')
	contents = OrderedDict()
	for article in reversed(soup.find_all('article')):
		id = article.attrs['id']
		contents[id] = article.prettify()
		article.replace_with(NavigableString('{' + id + ':s}'))
	rendered = {}
	for id, html in contents.items():
		rendered[id] = html.format(**rendered)
	return soup.prettify().format(**rendered)


def double_parse(input):
	soup = BeautifulSoup(input, 'lxml')
	contents = OrderedDict()
	for article in reversed(soup.find_all('article')):
		id = article.attrs['id']
		contents[id] = article.prettify()
	for id, html in contents.items():
		article = soup.find('article', dict(id=id))
		article.replace_with(BeautifulSoup(html, 'lxml').html.body.article)
	return soup.prettify()


res1 = regx_format(html).replace(' ', '').replace('\n', '')
res2 = double_parse(html).replace(' ', '').replace('\n', '')
assert res1 == res2

initt = time()
for k in range(1000):
	regx_format(html)
print('regx_format {0:.3f}s'.format(time() - initt))

initt = time()
for k in range(1000):
	double_parse(html)
print('double_parse {0:.3f}s'.format(time() - initt))
# 3 times slower


