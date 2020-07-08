import urllib.request
import logging
from urllib.parse import quote
import time
from os import environ

def send_notifications(chat_id, text):
    host = f"http://192.168.18.10:8080/send_notification/{chat_id}/{quote(text)}"

    req = urllib.request.Request(url=host)
    response_stream = urllib.request.urlopen(req)
    json_response = response_stream.read()
    logging.info(json_response)

if __name__ == '__main__':
    print("Aqui hago cosas muy largas y mientras acaba me voy a ver la tele!")
    time.sleep(3)
    send_notifications(int(environ.get('MY_TELEGRAM_ID')), 'Entrenamiento ML terminado!')
