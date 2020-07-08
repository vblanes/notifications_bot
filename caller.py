import urllib.request
import json
import logging
from urllib.parse import quote

if __name__ == '__main__':

    chat_id = 6771943
    text = 'Text with spaces'
    host = f"http://localhost:8080/send_notification/{chat_id}/{quote(text)}"

    req = urllib.request.Request(url=host)
    response_stream = urllib.request.urlopen(req)
    json_response = response_stream.read()
    logging.info(json_response)

