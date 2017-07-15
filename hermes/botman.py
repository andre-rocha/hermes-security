import time

import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, ForceReply

from . import config


bot = None


def send_picture(path):
    photo = open(path, 'rb')
    for u in config["SEND_PIC"]["USERS"]:
        bot.sendPhoto(u, photo)

    config["SEND_PIC"]["USERS"] = []

def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print('Chat:', content_type, chat_type, chat_id)

    if content_type != 'text':
        return

    command = msg['text'].lower()
    print("[*] Command : %s" % command)
    if command == '/ping':
        bot.sendMessage(chat_id, "PONG")

    elif command == '/check':
        config["SEND_PIC"]["USERS"].append(chat_id)
        config["SEND_PIC"]["SEND"] = True



def on_callback_query(msg):
    query_id, from_id, data = telepot.glance(msg, flavor='callback_query')
    print('Callback query:', query_id, from_id, data)


def start():
    print("[+] Start up Telegram Bot ...")
    print(config['TOKEN'])
    global bot
    bot = telepot.Bot(config["TOKEN"])

    MessageLoop(bot,
        {
            'chat': on_chat_message,
            'callback_query': on_callback_query,
        }).run_as_thread()
    print("[+] Bot is listening...")
