# -*- coding: utf-8 -*-
from pathlib import Path
import paramiko
import telebot
import psycopg2
import configparser
from sshtunnel import SSHTunnelForwarder
from telebot import types
from random import choice
from string import digits


file_name = 'conf.ini'
file_name = Path(__file__).parent.joinpath(file_name)

config = configparser.ConfigParser()
config.read(file_name, encoding='utf-8-sig')
gfg = config['DB']

bot = telebot.TeleBot(gfg['bot_token'])


CODE_TRANS = ''

key_path = Path(__file__).parent.joinpath(gfg['ssh_key'])
private_file = paramiko.RSAKey.from_private_key_file(key_path)
server = SSHTunnelForwarder(
    (gfg['ssh_host_name'], int(gfg['ssh_port'])),
    ssh_private_key=private_file,
    ssh_username=(gfg['ssh_user']),
    allow_agent=False,
    remote_bind_address=('localhost', 5434))
server.start()
print("server connected")

conn = psycopg2.connect(database=gfg['db_name'], user=gfg['db_user'],
                        password=gfg['db_password'], host='localhost',
                        port=server.local_bind_port)
conn.autocommit = True
curs = conn.cursor()


@bot.message_handler(commands=['start'])
def send_welcome(message):
    promo_code = bot.send_message(message.chat.id, 'Введите промокод')
    bot.register_next_step_handler(promo_code, phone_get)


def phone_gen_keyboard1():
    keyboard1 = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    gen_button = types.KeyboardButton("Сгенерировать номер телефона")
    code_check_button = types.KeyboardButton("Получить код подтверждения")
    info_button = types.KeyboardButton("Wiki DR")
    figma_button = types.KeyboardButton("Figma DR")
    keyboard1.add(gen_button, code_check_button, info_button, figma_button)
    return keyboard1


def phone_gen_keyboard2():
    keyboard2 = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    confirm_button = types.KeyboardButton("Узнать код")
    keyboard2.add(confirm_button)
    return keyboard2


def phone_gen():
    sqlite_select_query = "SELECT COUNT(phone) FROM users WHERE phone = '{phone}'"
    count_true = False
    while not count_true:
        cursor = conn.cursor()
        rnd_phone_gen1 = '7001' + ''.join(choice(digits) for i in range(7))
        cursor.execute(sqlite_select_query.format(phone=rnd_phone_gen1))
        count = cursor.fetchone()
        cursor.close()
        print(count)
        if count[0] == 0:
            count_true = True
    return rnd_phone_gen1


def number_check(message):
    try:
        cursor = conn.cursor()
        user_phone_number = message.text
        print(user_phone_number)
        code_chek_query = "SELECT code FROM sms_code where phone = '{phone}' and active = 1"
        cursor.execute(code_chek_query.format(phone=user_phone_number))
        code_output = cursor.fetchall()
        print(code_output)
        global CODE_TRANS
        CODE_TRANS = code_output[0]
    except IndexError:
        CODE_TRANS = "Номер не найден"


@bot.message_handler(content_types=['text'])
def phone_get(message):
    if message.text == 'dr-test':
        bot.send_message(message.from_user.id, 'Выбери кнопку на клавиатуре', reply_markup=phone_gen_keyboard1())
    elif message.text == 'Получить код подтверждения':
        msg = bot.send_message(message.chat.id, 'Введите номер телефона, после отправки нажмите на клавиатуру',
                               reply_markup=phone_gen_keyboard2())
        bot.register_next_step_handler(msg, number_check)
    elif message.text == "Сгенерировать номер телефона":
        bot.send_message(message.from_user.id, phone_gen())
    elif message.text == 'Узнать код':
        bot.send_message(message.from_user.id, CODE_TRANS, reply_markup=phone_gen_keyboard1())
    elif message.text == '/help':
        bot.send_message(message.from_user.id, 'По вопросам работы бота пиши @abnthony')
    elif message.text == 'Wiki DR':
        bot.send_message(message.from_user.id, 'https://xwiki.dr-telemed.ru')
    elif message.text == 'Figma DR':
        bot.send_message(message.from_user.id, 'https://www.figma.com/files/project/14993058/DR-telemed')


bot.infinity_polling()


