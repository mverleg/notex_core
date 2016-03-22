
from bs4 import BeautifulSoup


soup = BeautifulSoup('<p>Il a dit &lt;&lt;Sacr&eacute; bleu!&gt;&gt;</p>', 'lxml')
print('None')
print(soup.prettify(formatter=None))
print('\nhtml')
print(soup.prettify(formatter='html'))
print('\nminimal')
print(soup.prettify(formatter='minimal'))
print('\ndefault')
print(soup.prettify())



