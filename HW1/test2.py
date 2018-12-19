from bs4 import BeautifulSoup
import requests
import sys

r = requests.get('https://www.youtube.com/results?search_query={}'.format(sys.argv[1]))
r.encoding = 'utf-8'
s = BeautifulSoup(r.text, 'html.parser')

t = s.find_all(class_='yt-uix-tile-link yt-ui-ellipsis yt-ui-ellipsis-2 yt-uix-sessionlink spf-link ', href=True)[0]['href']
print('https://www.youtube.com'+str(t))
