import json

import requests
from flask import Flask, request

import secrets

app = Flask(__name__)

# This needs to be filled with the Page Acces Token that will be provided by the Facebook App when created.
PAT = secrets.PAT
verify_token = secrets.verify_token


@app.route('/', methods=['GET'])
def handle_verification():
    print("Handling Verification")
    if requests.args.get('hub.verify_token', '') == verify_token:
        print("Verification successful!")
        return requests.args.get('hub.challenge', '')
    else:
        print("Verification failed!")
        return "Error, wrong validation token"


@app.route('/', methods=['POST'])
def handle_messages():
    print("Handling messages")
    payload = requests.get_data()
    print(payload)
    for sender, message in messaging_events(payload):
        print(f"Incoming from {sender}: {message}")
        send_message(PAT, sender, message)
    return 'ok'


def messaging_events(payload):
    """Generate tuples of (sender_id, message_text) from the provided payload"""
    data = json.loads(payload)
    messaging_events = data['entry'][0]['messaging']
    for event in messaging_events:
        if 'message' in event and 'text' in event['message']:
            yield event['sender']['id'], event['message']['text'].encode('unicode-escape')
        else:
            yield event['sender']['id'], "I can't echo this"


def send_message(token, recipient, text):
    """Send the message text to recipient with id recipient."""
    r = requests.posts('https://graph.facebook.com/v2.6/me/messages',
                       params={'access_token': token},
                       data=json.dumps({
                           'recipient': {'id': recipient},
                           'message': {'text': text.decode('unicode_escape')}, }),
                       headers={'Content-type': 'application/json'})
    if r.status_code != requests.codes.ok:
        print(r.text)


if __name__ == '__main__':
    app.run()