import socket
from bs4 import BeautifulSoup
import requests
import random


class irc_client:

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, host, port):
        self.socket.connect((host, port))
        print('<irc_client> Connected to {} :{}'.format(host, port))

    def send(self, msg):
        self.socket.send((msg+'\n').encode())

    def get(self):
        return self.socket.recv(1024).decode('utf-8')

    def user(self, user_name, host_name, server_name, real_name, nick_name):
        user = 'USER ' + user_name + ' ' + host_name + ' ' + server_name + ' :' + real_name + '\n'
        self.send('USER {} {} {} :{}'.format(user_name, host_name, server_name, real_name))
        self.send('NICK {}'.format(nick_name))

    def is_ping(self, text):
        msg = text.split()
        if len(msg) > 0 and msg[0] == 'PING':
            self.send('PONG {}'.format(msg[1]))
            return True
        else:
            return False

    def join(self, channelName):
        self.send('JOIN {}'.format(channelName))
        print('<irc_client> Join channel: {}'.format(channelName))

    def priv_msg(self, channel, msg):
        self.send('PRIVMSG {} :{}'.format(channel, msg))
        print('<irc_client> Sent message to {} :{}'.format(channel, msg))


user_name = 'Bot'
host_name = 'NTU'
server_name = 'ntu.edu.tw'
real_name = 'Fan-Keng Sun'
nick_name = 'bot_b03901056'
channel = '#CN_DEMO56'
login_msg = 'Hello, I am {}, {}.'.format(user_name, nick_name)
lower_bound, upper_bound = 1, 10

irc = irc_client()
irc.connect('chat.freenode.net', 6667)
irc.user(user_name, host_name, server_name, real_name, nick_name)
irc.join(channel)
irc.priv_msg(channel, login_msg)


command_prefix = 'PRIVMSG ' + channel + ' :'
horoscopes = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra',
              'Scorpio', 'Sagittarius', 'Capricornus', 'Aquarius', 'Pisces']
horoscope_commands = [command_prefix + horoscope for horoscope in horoscopes]
guess_command = command_prefix + '!guess'
song_command = command_prefix + '!song'
chat_command = command_prefix + '!chat'
bye_command = command_prefix + '!bye'


def get_soup(url):
    r = requests.get(url)
    r.encoding = 'utf-8'
    return BeautifulSoup(r.text, 'html.parser')

def get_daily_horoscope(horoscope):
    idx = horoscopes.index(horoscope)
    s = get_soup('http://astro.click108.com.tw/daily_5.php?iAcDay=2018-10-23&iAstro={}'.format(idx))
    today_content = str(s.find_all(class_='TODAY_CONTENT')[0].find_all('p')[1])[3:-4]
    if len(today_content) > 100:
        period = today_content.find('。')
        semicolon = today_content.find('；')
        comma = today_content.find('，')
        if period != -1:
            today_content = today_content[:period+1]
        elif semicolon != -1:
            today_content = today_content[:semicolon] + '。'
        else:
            today_content = today_content[:comman] + '，'
    return today_content

def get_song_url(song_name):
    s = get_soup('https://www.youtube.com/results?search_query={}'.format(song_name))
    t = s.find_all(class_='yt-uix-tile-link yt-ui-ellipsis yt-ui-ellipsis-2 yt-uix-sessionlink spf-link ', href=True)[0]['href']
    return 'https://www.youtube.com' + str(t)

mode = 0

while(True):
    text = irc.get()
    print('~~~' + text + '~~~')

    if not irc.is_ping(text):
        text = text[:-2]

        if mode == 0:
            if any(text.endswith(horoscope_command) for horoscope_command in horoscope_commands):
                target, horoscope = text.split('PRIVMSG')[1].strip().split()
                horoscope = horoscope[1:]
                # print('reply the daily horoscope of {}'.format(horoscope))
                reply = get_daily_horoscope(horoscope)
                irc.priv_msg(target, reply)

            elif song_command in text:
                target, _, song_name = text.split('PRIVMSG')[1].strip().split(' ', 2)
                # print('reply the song url of {}'.format(song_name))
                reply = get_song_url(song_name)
                irc.priv_msg(target, reply)

            elif text.endswith(guess_command):
                target, _ = text.split('PRIVMSG')[1].strip().split()
                # print('start guessing')
                reply = '猜一個 {}～{} 之間的數字！'.format(lower_bound, upper_bound)
                irc.priv_msg(target, reply)
                mode = 1
                num = random.randint(lower_bound, upper_bound)
                cur_low = lower_bound
                cur_upp = upper_bound

            elif text.endswith(guess_command):
                other_user = text.split('!')[0]
                target, _ = text.split('PRIVMSG')[1].strip().split()
                print('start chatting with')
                mode = 2

        elif mode == 1:
            content = text.split('PRIVMSG')[1].strip().split()[1:]
            content = ' '.join(content)[1:]
            if not content.isdigit():
                continue
            guess_num = int(content)
            if guess_num > upper_bound or guess_num < lower_bound:
                reply = '數字在 {}～{} 之間！'.format(lower_bound, upper_bound)
            elif guess_num > cur_upp or guess_num < cur_low:
                reply = '已知數字在 {}～{} 之間！'.format(cur_low, cur_upp)
            elif guess_num < num:
                reply = '大於 {}！'.format(guess_num)
                cur_low = guess_num + 1
            elif guess_num > num:
                reply = '小於 {}！'.format(guess_num)
                cur_upp = guess_num - 1
            else:
                reply = '正確答案為 {}，恭喜答對！'.format(num)
                mode = 0
            irc.priv_msg(target, reply)



