from os import environ
import sys
from time import sleep
import json
import requests
import logging
from urllib.parse import quote_plus
from bottle import get, run
import threading
import urllib.request

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#############
#
# GENERAL TELEGRAM METHODS
#
#############

def get_url(url):
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
            return float(temperature_file.read().strip())/1000
    except IOError:
        return -1


############
#
# Concrete methods
#
############

@get('/send_notification/<chat_id>/<text>')
def send_notification(chat_id, text):
    logger.info(send_message(text=text, chat_id=chat_id))
    return
    

def process_single_message(update):
    chat_from = update.get('message').get('from').get('id')
    logger.info(get_public_ip())
    logger.info(send_message(f'Your telegram ID is: {chat_from}.\nUse your ID to call me in the send\\_notification method\n'
                             f'IP Address to access the services is {get_public_ip()}\n'
                             f'Server temperature is {get_temperature()} Cº', chat_id=int(chat_from)))


def process_batch_messages(last_update_id):
    """
    Read the messages, process them 
    """
    updates = get_updates(last_update_id)
    if 'result' in updates and len(updates['result']) > 0:
        logger.info("some notifications!")
        last_update_id = get_last_update_id(updates) + 1
        for update in updates['result']:
            process_single_message(update)
    return last_update_id



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
