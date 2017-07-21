import time

import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, ForceReply
from telepot import namedtuple

from . import config


bot = None
inline_id = None

def send_picture(path, caption=''):
    for u in config['AUTH_USERS']:
        print('[*] Sending %s picture to %s' % (path.split('/')[-1], u))
        photo = open(path, 'rb')
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
    config['INVITE'] = []

    MessageLoop(bot, {
            'chat': on_chat_message,
            'callback_query': on_callback_query,
        }).run_as_thread()
    print("[+] Bot is listening...")


def _get_chat(chat_id):
    chat_dsc = bot.getChat(chat_id)
    if chat_dsc['type'] == 'group':
        return chat_dsc['title']
    elif chat_dsc['type'] == 'private':
        return ' '.join( [ chat_dsc.get('first_name', ''), chat_dsc.get('last_name', '') ] )


def on_chat_message(msg):
    print(msg)
    content_type, chat_type, chat_id = telepot.glance(msg)
    print('Chat:', content_type, chat_type, chat_id)

    if content_type != 'text':
        return

    try:
        if msg['text'][0:5] == '/auth':
            config['INVITE'].append(chat_id)
            return
    except:
        pass

    if chat_id != config['SUPER_USER']:
        print('UNAUTHORIZED ACCESS...')
        return

    command = msg['text'].lower()
    print("[*] Command : %s" % command)
    if command == '/ping':
        bot.sendMessage(chat_id, "PONG")

    elif command == '/check':
        config["SEND_PIC"] = True

    elif command == '/settings':
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Modules", callback_data="mod"),
                InlineKeyboardButton(text="Config", callback_data="conf"),
            ]
        ])
        global inline_id
        inline_id = bot.sendMessage(chat_id, 'Settings', reply_markup=keyboard)

    elif command == '/list_invites':
        kb_list = [InlineKeyboardButton(text=_get_chat(u), callback_data="auth_%s" % u) for u in config['INVITE']]
        kb_auth = [InlineKeyboardButton(text=_get_chat(u), callback_data="auth_%s" % u) for u in config['AUTH_USERS'] if u != config['SUPER_USER']]

        if len(kb_auth) > 0:
            keyboard_auth = InlineKeyboardMarkup(inline_keyboard=[
                kb_auth,
            ])
            bot.sendMessage(chat_id, 'Authorized chats :', reply_markup=keyboard_auth)

        if len(kb_list) > 0:
            keyboard_list = InlineKeyboardMarkup(inline_keyboard=[
                kb_list,
            ])
            global inline_id
            inline_id = bot.sendMessage(chat_id, 'Waiting List:', reply_markup=keyboard_list)
            config['INVITE'] = []
        else:
            bot.sendMessage(chat_id, 'No chats in the waiting list...')


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
        bot.answerCallbackQuery(query_id, 'Running %s' % module)


    def runtime_configure():
        bot.answerCallbackQuery(query_id, 'callback conf stub')
        return


    def back_inline():
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Modules", callback_data="mod"),
                InlineKeyboardButton(text="Config", callback_data="conf"),
            ]
        ])
        bot.answerCallbackQuery(query_id, '')

        global inline_id
        if inline_id:
            msg_idf = telepot.message_identifier(inline_id)
            bot.editMessageReplyMarkup(msg_idf, reply_markup=keyboard)
        else:
            inline_id = bot.sendMessage(from_id, 'CHOOSE MUTHAFUCKA:', reply_markup=keyboard)


    cmd_router = {
        'mod': send_modules,
        'conf': runtime_configure,
        'back_inline': back_inline
    }

    for t in config['registry']:
        cmd_router['mod_'+t] = choose_module

    if query_data in cmd_router:
        cmd_func = cmd_router[query_data]
        cmd_func()
        return

    else:
        if query_data.startswith('auth_'):
            if int(query_data[5:]) in config['AUTH_USERS']:
                config['AUTH_USERS'].remove(int(query_data[5:]))
                bot.answerCallbackQuery(query_id, '%s unauthorized.' % query_data[5:])
                if int(query_data[5:]) in config['INVITE']:
                    config['INVITE'].remove(int(query_data[5:]))
            else:
                config['AUTH_USERS'].append(int(query_data[5:]))
                bot.answerCallbackQuery(query_id, '%s authorized.' % query_data[5:])
                bot.sendMessage(int(query_data[5:]), 'You were authorized by hermes super user.')


