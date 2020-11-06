import urllib.request
import logging
from urllib.parse import quote
import time
from os import environ

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_notifications(chat_id, text):
    host = "0.0.0.0"
    url_ = f"http://{host}:8080/send_notification/{chat_id}/{quote(text)}"

    req = urllib.request.Request(url=url_)
    response_stream = urllib.request.urlopen(req)
    json_response = response_stream.read()
    logging.info(json_response)

if __name__ == '__main__':
    print("Aqui hago cosas muy largas y mientras acaba me voy a ver la tele!")
    time.sleep(1)
    logger.info(f"Sending message to {environ.get('MY_TELEGRAM_ID')}")
    send_notifications(int(environ.get('MY_TELEGRAM_ID')), 'Entrenamiento ML terminado!')
