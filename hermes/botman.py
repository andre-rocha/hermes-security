import time

import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, ForceReply
from telepot import namedtuple

from hermes import config
from hermes.pyimage.tmpimage import TempImage

bot = None
inline_id = None

def send_picture(path, caption='', clean=False):
    for u in config['AUTH_USERS']:
        print('[*] Sending %s picture to %s' % (path.split('/')[-1], u))
        photo = open(path, 'rb')
        bot.sendPhoto(u, photo, caption=caption)

    if clean:
        t = TempImage()
        t.set_path(path)
        t.cleanup()


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

    bot_info = bot.getMe()
    config['BOTINFO'] = bot_info

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
    else:
        command = msg['text']

    print("[*] Command : %s" % command)

    if command.endswith('@'+config['BOTINFO'].get('username')):
        command = "@".join(command.split('@')[:-1])

    if command == '/auth':
        if chat_id not in config['INVITE'] and chat_id not in config['AUTH_USERS']:
            config['INVITE'].append(chat_id)
            bot.sendMessage(chat_id, 'The admin will process your request.')
        elif chat_id in config['INVITE']:
            bot.sendMessage(chat_id, 'Your access is pending.')
        else:
            bot.sendMessage(chat_id, 'You already have access.')
        return

    if chat_id not in config['AUTH_USERS']:
        bot.sendMessage(chat_id, 'You don\'t have access...')
        print('UNAUTHORIZED ACCESS by %s' % _get_chat(chat_id))
        return

    if command == '/ping':
        bot.sendMessage(chat_id, "PONG")
        return

    elif command == '/check':
        config["SEND_PIC"] = True
        return

    elif command == '/settings':
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Modules", callback_data="modules:list"),
                InlineKeyboardButton(text="Config", callback_data="config:list"),
            ]
        ])
        global inline_id
        inline_id = bot.sendMessage(chat_id, 'Settings :', reply_markup=keyboard)
        return

    elif command == '/list_invites':
        kb_list = [InlineKeyboardButton(text=_get_chat(u), callback_data="auth:chat:%s" % u) for u in config['INVITE']]
        kb_auth = [InlineKeyboardButton(text=_get_chat(u), callback_data="auth:chat:%s" % u) for u in config['AUTH_USERS'] if u != config['SUPER_USER']]

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
            inline_id = bot.sendMessage(chat_id, 'Waiting List :', reply_markup=keyboard_list)
            config['INVITE'] = []
        else:
            bot.sendMessage(chat_id, 'No chats in the waiting list...')

        return


def on_callback_query(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    print('Callback Query:', query_id, from_id, query_data)

    def list_modules():
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=mod_name, callback_data="modules:run:"+mod_name) for mod_name in config['REGISTRY']
            ],
            [
                InlineKeyboardButton(text="<- Back", callback_data="menu:back:settings"),
            ]
        ])

        global inline_id
        if inline_id:
            msg_idf = telepot.message_identifier(inline_id)
            # bot.editMessageReplyMarkup(msg_idf, reply_markup=keyboard)
            bot.editMessageText(msg_idf, text='Modules :', reply_markup=keyboard)
        else:
            inline_id = bot.sendMessage(from_id, 'Modules :', reply_markup=keyboard)

        bot.answerCallbackQuery(query_id, 'Choosing detection module')


    def choose_module():
        module = query_data.split(':')[-1]
        config['module'] = module
        bot.answerCallbackQuery(query_id, 'Running %s' % module)


    def runtime_configure():
        bot.answerCallbackQuery(query_id, 'callback conf stub')
        return


    def back_settings():
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Modules", callback_data="modules:list"),
                InlineKeyboardButton(text="Config", callback_data="config:list"),
            ]
        ])
        bot.answerCallbackQuery(query_id, '')

        global inline_id
        if inline_id:
            msg_idf = telepot.message_identifier(inline_id)
            # bot.editMessageReplyMarkup(msg_idf, reply_markup=keyboard)
            bot.editMessageText(msg_idf, text='Settings :', reply_markup=keyboard)
        else:
            inline_id = bot.sendMessage(from_id, 'Settings:', reply_markup=keyboard)


    cmd_router = {
        'modules:list': list_modules,
        'config:list': runtime_configure,
        'menu:back:settings': back_settings
    }

    for t in config['REGISTRY']:
        cmd_router['modules:run:'+t] = choose_module

    if query_data in cmd_router:
        cmd_func = cmd_router[query_data]
        cmd_func()
        return

    else:
        if query_data.startswith('auth:chat:'):
            cid = int(query_data.split(':')[-1])
            if cid in config['AUTH_USERS']:
                config['AUTH_USERS'].remove(cid)
                bot.answerCallbackQuery(query_id, '%s unauthorized.' % _get_chat(cid))
                if int(query_data[5:]) in config['INVITE']:
                    config['INVITE'].remove(cid)
            else:
                config['AUTH_USERS'].append(cid)
                bot.answerCallbackQuery(query_id, '%s authorized.' % _get_chat(cid))
                bot.sendMessage(cid, 'You were authorized by hermes super user.')


