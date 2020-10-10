from os import environ
import string
import random
import sys
from time import sleep
import json
import requests
import logging
from urllib.parse import quote_plus
from bottle import get, run, HTTPResponse
import threading
import urllib.request
from dbmanager import DBManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


#############
#
# GENERAL TELEGRAM METHODS
#
#############
def get_url(url: str):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates(offset=None):
    try:
        # peticion para obtener las novedades
        url = URL + "getUpdates"
        # offset es el numero del ultimo mensaje recibido
        # el objetivo es no volver a pedirlo to-do
        if offset:
            url += "?offset={}".format(offset)
        # llamada a la funcion auxiliar
        js = get_json_from_url(url)
        return js
    except Exception as e:
        logger.error(e)


def get_last_update_id(updates):
    return max([int(el['update_id']) for el in updates['result']])


def send_message(text, chat_id):
    text = quote_plus(text)
    url = URL + f"sendMessage?text={text}&chat_id={chat_id}&parse_mode=Markdown"
    return get_url(url)


############
#
# UTILS
#
############
def get_public_ip():
    ip_addr = urllib.request.urlopen('https://ident.me').read().decode('utf8')
    return ip_addr


def get_temperature():
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as temperature_file:
            return float(temperature_file.read().strip()) / 1000
    except IOError:
        return -1


############
#
# Logic interactions
#
############

@get('/send_notification/<chat_id>/<text>')
def send_notification(chat_id, text):
    # check if the user is a registered one
    dbm = DBManager()
    if dbm.exist_user(chat_id):
        logger.info(send_message(text=text, chat_id=chat_id))
        return HTTPResponse(status=200)
    else:
        return HTTPResponse(status=400)


def account_check(telegramid):
    # return if user exist + username + role
    # e.g. (False, None, None) or (12345, 'Pepet', 'user')
    dbm = DBManager()
    resultset = dbm.get_user(telegramid)
    if len(resultset) == 0:
        return False, None, None
    else:
        # its a shame there is no named tuple
        return True, resultset[1], resultset[3]


def process_single_message(update):
    telegram_id_from = update.get('message').get('from').get('id')
    # check user "credentials"
    is_registered, username, role = account_check(telegram_id_from)
    # kind of message to the bot; allowed: plain text and call_back
    if 'callback_query' in update:
        input_text = update.get('callback_query').get('data')
    elif 'message' in update:
        input_text = update.get('message').get('text')
    else:
        input_text = None

    # Discard incorrect message formats
    if telegram_id_from is None or input_text is None:
        logger.info(send_message('This bot only supports text messages, commands and callbacks', telegram_id_from))
        return

    # TODO maybe not create an instace every time???
    dbm = DBManager()
    # User is not registered
    if not is_registered:
        # check if the message is a code!
        if dbm.exist_code(input_text):
            # pick info about the user and register it
            field_username = update.get('message').get('from').get('username', '')
            field_first_name = update.get('message').get('from').get('first_name', '')
            field_last_name = update.get('message').get('from').get('last_name', '')
            if username:
                username = field_username
            else:
                username = f"{field_first_name} {field_last_name}"

            dbm.add_user(telegram_id_from, username, role='user', password=None)
            dbm.delete_code(input_text)
            logger.info(f'User {username} added correctly')
            logger.info(send_message('Registration successful ', telegram_id_from))
            return
        else:
            send_message('To register yourself in the bot, copy a valid registration code', telegram_id_from)
            return

    # Users only can get the conectivity info
    if role == 'admin':
        if input_text == 'gettemp':
            logger.info(send_message(f'Temperature -> {get_temperature()}ºC', telegram_id_from))
        elif input_text == 'listcodes':
            codes_list = dbm.list_codes()
            logger.info(send_message('\n'.join(codes_list), chat_id=telegram_id_from))
        # only add one code
        elif input_text == 'addcode':
            # generate 16 chars code
            random_code = ''.join(random.choice(string.ascii_lowercase) for _ in range(16))
            dbm.add_code(code=random_code)
            logger.info(send_message(f"Code {random_code} added to the database", chat_id=telegram_id_from))
        # only remove last code to not overcomplicate logic
        elif input_text == 'removecode':
            codes_list = dbm.list_codes()
            dbm.delete_code(codes_list[-1])
            logger.info(send_message("Last code deleted!", chat_id=telegram_id_from))

    else:
        logger.info(send_message(f'Your telegram ID is: {telegram_id_from}.\nUse your ID to call me in the '
                                 f'send\\_notification method\n'
                                 f'IP Address to access the services is {get_public_ip()}\n',
                                 chat_id=int(telegram_id_from)))


def process_batch_messages(last_update_id_: int):
    """
    Read the messages, process them 
    """
    updates = get_updates(last_update_id_)
    if 'result' in updates and len(updates['result']) > 0:
        last_update_id_ = get_last_update_id(updates) + 1
        for update in updates['result']:
            process_single_message(update)
    return last_update_id_


if __name__ == '__main__':
    PRIVATE_TOKEN = environ.get('NOTIFICATION_BOT_TOKEN', None)
    if PRIVATE_TOKEN is None:
        logger.error("Unable to read token!")
        sys.exit(-1)
    URL = f"https://api.telegram.org/bot{PRIVATE_TOKEN}/"

    # Host bottle API
    threading.Thread(target=run, kwargs=dict(host='0.0.0.0', port=8080)).start()

    last_update_id = None
    while True:
        last_update_id = process_batch_messages(last_update_id)
        # be gentle with Telegram servers
        sleep(0.5)
