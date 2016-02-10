
from bs4 import BeautifulSoup


soup = BeautifulSoup('<p>Il a dit &lt;&lt;Sacr&eacute; bleu!&gt;&gt;</p>', 'lxml')
print(soup.prettify(formatter=None))
print(soup.prettify(formatter='html'))
print(soup.prettify(formatter='minimal'))
print(soup.prettify())


print(BeautifulSoup(soup.prettify(formatter=None), 'lxml').prettify(formatter=None))


