import json

import praw
import requests
from flask import Flask, request

import secrets

app = Flask(__name__)

# This needs to be filled with the Page Acces Token that will be provided by the Facebook App when created.
PAT = secrets.PAT
verify_token = secrets.verify_token
reddit = praw.Reddit(client_id=secrets.reddit_client_id,
                     client_secret=secrets.reddit_client_secret,
                     user_agent='heroku user agent')


@app.route('/', methods=['GET'])
def handle_verification():
    print("Handling Verification")
    if request.args.get('hub.verify_token', '') == verify_token:
        print("Verification successful!")
        return request.args.get('hub.challenge', '')
    else:
        print("Verification failed!")
        return "Error, wrong validation token"


@app.route('/', methods=['POST'])
def handle_messages():
    print("Handling messages")
    payload = request.get_data()
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
    kind = parse(text)
    print(kind)
    if kind:
        for submission in reddit.subreddit('metal').search(f'flair:{kind}',
                                                           sort='new',
                                                           syntax='lucene'):
            payload = submission.url
            break
    else:
        payload = text.decode('unicode-escape')

    r = requests.post('https://graph.facebook.com/v2.6/me/messages',
                      params={'access_token': token},
                      data=json.dumps({
                          'recipient': {'id': recipient},
                          'message': {'text': payload}, }),
                      headers={'Content-type': 'application/json'})
    if r.status_code != requests.codes.ok:
        print(r.text)


metal_kinds = {
    'black': 'Black',
    'black/death': 'Black/Death',
    'black/thrash': 'Black/Thrash',
    'crossover': 'Crossover',
    'death': 'Death',
    'death/doom': 'Death/Doom',
    'death/grind': 'Death/Grind',
    'death/thrash': 'Death/Thrash',
    'dsbm': 'Depressive Black Metal',
    'drone': 'Drone',
    'folk': 'Folk',
    'funeral': 'Funeral Doom',
    'funeral/doom': 'Funeral Doom',
    'goregrind': 'Goregrind',
    'grind': 'Grind',
    'melodeath': 'Melodeath',
    'power': 'Power',
    'progressive': 'Progressive',
    'review': 'Review',
    'sludge': 'Sludge',
    'speed': 'Speed',
    'stoner': 'Stoner',
    'stoner/doom': 'Stoner Doom',
    'symphonic': 'Symphonic',
    'tech/death': 'Tech-Death',
    'technical': 'Tech-Death',
    'thrash': 'Thrash',
    'trad/doom': 'Trad Doom',
    'traditional': 'Traditional',
    'underground': 'Underground',
    'viking': 'Viking',
}

def parse(text):
    for word in (w.decode('unicode-escape').lower() for w in text.split()):
        print(f'word: {word}')
        if word in metal_kinds:
            return metal_kinds[word]
    return False


if __name__ == '__main__':
    app.run()
