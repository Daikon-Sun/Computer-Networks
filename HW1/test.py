from bs4 import BeautifulSoup
import requests
import sys

horoscopes = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra',
              'Scorpio', 'Sagittarius', 'Capricornus', 'Aquarius', 'Pisces']

idx = horoscopes.index(sys.argv[1])

r = requests.get('http://astro.click108.com.tw/daily_5.php?iAcDay=2018-10-23&iAstro={}'.format(idx))
r.encoding = 'utf-8'
s = BeautifulSoup(r.text, 'html.parser')

today_content = str(s.find_all(class_='TODAY_CONTENT')[0].find_all('p')[1])[3:-4]
print(len(today_content))
