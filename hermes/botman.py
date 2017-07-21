import time

import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, ForceReply
from telepot import namedtuple

from . import config


bot = None
inline_id = None

def send_picture(path, caption=''):
    photo = open(path, 'rb')
    for u in config['AUTH_USERS']:
        print('[*] Sending %s picture to %s' % (path.split('/')[-1], u))
        bot.sendPhoto(u, photo, caption=caption)


def send_message(text):
    for u in config['AUTH_USERS']:
        bot.sendMessage(u, text)


def send_video(path):
    # TODO: send video
    return


def start():
    print("[+] Starting Hermes Bot ...")
    global bot
    bot = telepot.Bot(config["TOKEN"])
    config['AUTH_USERS'] = [config['SUPER_USER']]

    MessageLoop(bot, {
            'chat': on_chat_message,
            'callback_query': on_callback_query,
        }).run_as_thread()
    print("[+] Bot is listening...")


def on_chat_message(msg):
    print(msg)
    content_type, chat_type, chat_id = telepot.glance(msg)
    print('Chat:', content_type, chat_type, chat_id)
    if chat_id != config['SUPER_USER']:
        print('UNAUTHORIZED ACCESS...')
        return

    if content_type != 'text':
        return

    command = msg['text'].lower()
    print("[*] Command : %s" % command)
    if command == '/ping':
        bot.sendMessage(chat_id, "PONG")

    elif command == '/check':
        config["SEND_PIC"] = True

    # elif command == '/cancel':
    #     markup = ReplyKeyboardRemove()
    #     bot.sendMessage(chat_id, 'Huuuumm...', reply_markup=markup)

    elif command == '/settings':
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Modules", callback_data="mod"),
                InlineKeyboardButton(text="Config", callback_data="conf"),
            ]
        ])
        global inline_id
        inline_id = bot.sendMessage(chat_id, 'CHOOSE MUTHAFUCKA:', reply_markup=keyboard)


def on_callback_query(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    print('Callback Query:', query_id, from_id, query_data)

    def send_modules():
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=mod_name, callback_data="mod_"+mod_name) for mod_name in config['registry']
            ],
            [
                InlineKeyboardButton(text="<- Back", callback_data="back_inline"),
            ]
        ])

        global inline_id
        if inline_id:
            msg_idf = telepot.message_identifier(inline_id)
            bot.editMessageReplyMarkup(msg_idf, reply_markup=keyboard)
            bot.answerCallbackQuery(query_id, 'Choosing detection module')
        else:
            inline_id = bot.sendMessage(from_id, 'CHOOSE MUTHAFUCKA:', reply_markup=keyboard)
            bot.answerCallbackQuery(query_id, 'Choosing detection module')


    def choose_module():
        module = query_data[4:]
        config['module'] = module

    cmd_router = {
        'mod': send_modules,
    }

    for t in config['registry']:
        cmd_router['mod_'+t] = choose_module

    if query_data in cmd_router:
        cmd_func = cmd_router[query_data]
        cmd_func()
        return

    # if query_data == 'mod':
    #     print('[-----------] NAO DEU CERTO')
    #     keyboard = InlineKeyboardMarkup(inline_keyboard=[
    #         [
    #             InlineKeyboardButton(text=mod_name, callback_data="mod_"+mod_name) for mod_name in config['registry']
    #         ],
    #         [
    #             InlineKeyboardButton(text="<- Back", callback_data="back_inline"),
    #         ]
    #     ])

    #     global inline_id
    #     if inline_id:
    #         msg_idf = telepot.message_identifier(inline_id)
    #         bot.editMessageReplyMarkup(msg_idf, reply_markup=keyboard)
    #     else:
    #         inline_id = bot.sendMessage(from_id, 'CHOOSE MUTHAFUCKA:', reply_markup=keyboard)
    #         bot.answerCallbackQuery(query_id, 'Choosing modules to run.')

    if query_data == 'conf' :
        bot.answerCallbackQuery(query_id, 'callback conf stub')
        return

    # elif query_data.startswith('mod_'):
    #     module = query_data[4:]
    #     config['module'] = module

    elif query_data == 'back_inline':
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Modules", callback_data="mod"),
                InlineKeyboardButton(text="Config", callback_data="conf"),
            ]
        ])

        global inline_id
        if inline_id:
            msg_idf = telepot.message_identifier(inline_id)
            bot.editMessageReplyMarkup(msg_idf, reply_markup=keyboard)
        else:
            inline_id = bot.sendMessage(from_id, 'CHOOSE MUTHAFUCKA:', reply_markup=keyboard)









