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
# random string generator
import string
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CODE_LENGTH = 20
SSH_PUBLIC_PORT = 2202


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


def send_message(text:str, chat_id:int):
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

def get_random_string(length:int):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

############
#
# Logic interactions
#
############

@get('/send_notification/<telegram_id>/<text>')
def send_notification(telegram_id, text):
    # check if the user is a registered one
    dbm = DBManager()

    if dbm.exist_user_by_telegram_id(telegram_id):
        logger.info(send_message(text=text, chat_id=telegram_id))
        return HTTPResponse(status=200)
    else:
        return HTTPResponse(status=400)



def account_check(telegram_id):
    # return if user exist + username + role
    # e.g. (False, None, None) or (12345, 'Pepet', 'user')
    dbm = DBManager()
    resultset = dbm.get_user(telegram_id)
    logger.info(resultset)
    if len(resultset) == 0:
        return False, None, None
    else:
        # its a shame there is no named tuple
        return (True, resultset[1], resultset[3])


def info_message(telegram_id_from):
    logger.info(send_message(f'Your telegram ID is: {telegram_id_from}.\nUse your ID to call me in the '
                             f'send\\_notification method\n'
                             f'IP Address to access the services is {get_public_ip()}\n'
                             f'ssh public port: {SSH_PUBLIC_PORT}', chat_id=telegram_id_from))


def process_single_message(update):
    # discard estrange messages
    try:
        telegram_id_from = int(update.get('message').get('from').get('id'))
    except AttributeError:
        return
    # check user "credentials"
    is_registered, username, role = account_check(telegram_id_from)
    logging.info(f'{telegram_id_from} is_registered -> {is_registered}')
    # kind of message to the bot; allowed: plain text and call_back
    if 'callback_query' in update:
        input_text = str(update.get('callback_query').get('data'))
    elif 'message' in update:
        input_text = str(update.get('message').get('text'))
    else:
        input_text = None

    # Discard incorrect message formats
    if input_text is None:
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
        dbm = DBManager()
        if input_text == 'gettemp':
            logger.info(send_message(f'Temperature -> {get_temperature()}ºC', telegram_id_from))

        elif input_text == 'listcodes':
            codes = dbm.list_codes()
            codes_msg =  '\n'.join(codes) if codes else 'No codes yet!'
            logging.info(send_message(codes_msg,chat_id=telegram_id_from))

        # generate, add the code, send it to the user
        elif input_text == 'addcode':
            new_code = get_random_string(CODE_LENGTH)
            dbm.add_code(new_code)
            logger.info(send_message(f'New code generated: {new_code}', chat_id=telegram_id_from))

        # only remove last code to not overcomplicate logic
        # this is VERY suboptimal, but it works atm
        elif input_text == 'removecode':
            all_codes = dbm.list_codes()
            if all_codes:
                dbm.delete_code(all_codes[-1])
                # remove last element
                codes = all_codes[:-1]
                codes_msg = '\n'.join(codes) if codes else 'No codes yet!'
                logging.info(send_message(codes_msg,chat_id=telegram_id_from))
        # add a default message on the admin side too
        else:
            info_message(telegram_id_from)
    else:
        info_message(telegram_id_from)

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
        sleep(0.7)
