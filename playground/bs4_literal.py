
from bs4 import CData, BeautifulSoup


tag = CData('<p>Hello!</p>')
soup = BeautifulSoup('<article><h1>Hi!</h1><gohere /><article>', 'lxml')

soup.find('gohere').replace_with(tag)

res = soup.prettify(formatter='minimal')
print(res)

print('doesn\'t work')


