from bs4 import BeautifulSoup
import random
import requests
import select
import socket
import sys
import time


class irc_client:

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, host, port):
        self.socket.connect((host, port))
        print('<irc_client> Connected to {} :{}'.format(host, port))

    def join(self, channel_name):
        self.send('JOIN {}'.format(channel_name))
        print('<irc_client> Join channel: {}'.format(channel_name))

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

    def priv_msg(self, channel, msg, show=True):
        self.send('PRIVMSG {} :{}'.format(channel, msg))
        if show:
            print('<irc_client> Sent message to {} :{}'.format(channel, msg))


host = 'chat.freenode.net'
port = 6667
user_name = 'Bot'
host_name = 'NTU'
server_name = 'ntu.edu.tw'
real_name = 'Fan-Keng Sun'
nick_name = 'bot_b03901056'
channel = '#CN_DEMO'
lower_bound, upper_bound = 1, 10

irc = irc_client()
irc.connect(host, port)
irc.user(user_name, host_name, server_name, real_name, nick_name)
irc.join(channel)
irc.priv_msg(channel, 'Hello, I am {}, {}.'.format(user_name, nick_name))


command_prefix = ' :'
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

while True:

    if mode == 2:
        readies = select.select([sys.stdin, irc.socket], [], [], 0)[0]
        for ready in readies:
            if ready is sys.stdin:
                reply = sys.stdin.readline()
                irc.priv_msg(other_user, reply, show=False)
                print('> ', end='', flush=True)
            else:
                text = irc.get()
                if not irc.is_ping(text):
                    text = text[:-2]
                    if text.endswith(bye_command):
                        print('\b' * 100, end='', flush=True)
                        reply = '=' * 7 + '{}已離開聊天室'.format(other_user) + '=' * 7
                        print(reply, flush=True)
                        irc.priv_msg(other_user, reply, show=False)
                        mode = 0
                    else:
                        cur_other_user = text.split('!')[0][1:]
                        if cur_other_user != other_user:
                            continue
                        content = text.split('PRIVMSG')[1].strip().split()[1:]
                        print('\b\b', end='')
                        print('{} : {}'.format(other_user, ' '.join(content)[1:]))
                        print('> ', end='', flush=True)


    else:
        text = irc.get()

        if not irc.is_ping(text):
            text = text[:-2]

            if mode == 0:
                if any(text.endswith(horoscope_command) for horoscope_command in horoscope_commands):
                    other_user = text.split('!')[0][1:]
                    target, horoscope = text.split('PRIVMSG')[1].strip().split()
                    horoscope = horoscope[1:]
                    reply = get_daily_horoscope(horoscope)
                    irc.priv_msg(other_user, reply)

                elif song_command in text:
                    other_user = text.split('!')[0][1:]
                    target, _, song_name = text.split('PRIVMSG')[1].strip().split(' ', 2)
                    reply = get_song_url(song_name)
                    irc.priv_msg(other_user, reply)

                elif text.endswith(guess_command):
                    other_user = text.split('!')[0][1:]
                    target, _ = text.split('PRIVMSG')[1].strip().split()
                    reply = '猜一個 {}～{} 之間的數字！'.format(lower_bound, upper_bound)
                    irc.priv_msg(other_user, reply)
                    mode = 1
                    num = random.randint(lower_bound, upper_bound)
                    cur_low = lower_bound
                    cur_upp = upper_bound

                elif text.endswith(chat_command):
                    other_user = text.split('!')[0][1:]
                    target, _ = text.split('PRIVMSG')[1].strip().split()
                    reply = '=' * 7 + '{}想跟你聯繫'.format(other_user) + '=' * 7
                    print(reply)
                    print('> ', end='', flush=True)
                    irc.priv_msg(other_user, reply, show=False)
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
                irc.priv_msg(other_user, reply)
