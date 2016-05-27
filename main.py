#!/usr/bin/python3
#  -*- coding: utf-8 -*-
__author__ = 'Denis'

from slack_token import SLACK_TOKEN
from slackclient import SlackClient
from datetime import datetime
from requests_bot import requests_bot_keys, requests_for_bot
import time
import json


ID_CHANNEL_CONTENT = 'G0MGYKMA8'
ID_MARIO = 'U1ANC9117'
ID_TEAM = 'T0DF1FYHE'
ID_MY = 'U0DF0B546'
bot_id = 'B19M4PG3Z'

with open('questions.json', 'r') as file_questions:
    questions = json.load(file_questions)
questions_keys = list(questions.keys())


def is_message(text):
    """
    text it's request
    filter request have message
    """
    if 'type' in text[0]:
        if text[0]['type'] == 'message':
            return text[0]['type']
    return None


def is_channel(text):
    """
    text it's request
    filter by one channel
    """
    if 'channel' in text[0]:
        if text[0]['channel'] == 'G0MGYKMA8':
            return text[0]['channel']
    return None


def is_text(text):
    """
    text convert to lower case
    KeyError if message edited
    """
    if 'subtype' in text[0]:
        if text[0]['subtype'] == 'message_changed':
            edit_message = text[0]['message']
            return edit_message['text'].lower()
    if 'text' in text[0]:
        return text[0]['text'].lower()


def is_date(text):
    """
    convert timestamp to datetime
    """
    return datetime.fromtimestamp(float(text[0]['ts']))


def is_user(text):
    """
    filter message by user
    """
    if 'subtype' in text[0]:
        if text[0]['subtype'] == 'message_changed':
            edit_message = text[0]['message']
            if 'user' in edit_message:
                return edit_message['user']
    if 'user' in text[0]:
        return text[0]['user']


class Message:
    def __init__(self, req):
        self.type = is_message(req)
        self.channel = is_channel(req)
        self.user = is_user(req)
        self.date_create = is_date(req)
        self.text = is_text(req)


def send_message(bot_message, channel=ID_CHANNEL_CONTENT):
    sc.api_call(
        'chat.postMessage',
        channel=channel,
        text='<@{}> {}'.format(new_message.user, bot_message),
        username='Mario',
        icon_emoji=':mario:'
    )


def bot_typing(bot_id=ID_MARIO, channel=ID_CHANNEL_CONTENT):
    sc.api_call(
        'chat.postMessage',
        channel=channel,
        type='user_typing',
        user=bot_id,
    )


sc = SlackClient(SLACK_TOKEN)
if sc.rtm_connect():

    while True:
        result = None
        req = sc.rtm_read()
        if not req:
            continue
        print(req)

        if not is_message(req):
            continue
        if not is_user(req):
            continue
        if not is_channel(req):
            continue

        new_message = Message(req)
        print(new_message.text)

        if new_message.text in requests_bot_keys:
            result = requests_for_bot[new_message.text]

        if new_message.text in questions_keys:
            result = questions[new_message.text]

        # pattern = '(.*)?(<@{}>:).?(\w+.\w+)?.?'.format(ID_MARIO)
        # test = re.search(pattern=pattern, string=req[0]['text'], flags=re.IGNORECASE)
        # print('TEST', test.group(1), test.group(2), test.group(3))

        if result:
            bot_typing()
            time.sleep(1)
            send_message(bot_message=result)
else:
    print("Connection Failed, invalid token?")


