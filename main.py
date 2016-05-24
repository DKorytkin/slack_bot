#!/usr/bin/python3
#  -*- coding: utf8 -*-
__author__ = 'Denis'

from slack_token import SLACK_TOKEN
from slackclient import SlackClient
from datetime import datetime
import time
import json
from conect_url import get_mario_gif, get_version_prod
import re
import requests

ID_CHANNEL_CONTENT = 'G0MGYKMA8'
ID_MARIO = 'U1ANC9117'
ID_TEAM = 'T0DF1FYHE'
ID_MY = 'U0DF0B546'

with open('questions.json', 'r') as file_questions:
    questions = json.load(file_questions)
questions_keys = list(questions.keys())


def is_message(text):
    """
    text it's request
    filter request have message
    """
    if not text:
        pass
    if text[0]['type'] == 'message':
        return text[0]


def is_channel(text):
    """
    text it's request
    filter by one channel
    """
    if text[0]['channel'] == 'G0MGYKMA8':
        return text


def is_text(text):
    """
    text convert to lower case
    KeyError if message edited
    """
    try:
        return text[0]['text'].lower()
    except KeyError:
        edit_message = text[0]['message']
        return edit_message['text'].lower()


def is_date(text):
    """
    convert timestamp to datetime
    """
    return datetime.fromtimestamp(float(text[0]['ts']))


def is_user(text):
    """
    filter message by user
    """
    try:
        return text[0]['user']
    except KeyError:
        pass


class Message:
    def __init__(self, req):
        self.type = req[0]['type']
        self.channel = req[0]['channel']
        self.user = req[0]['user']
        self.team = req[0]['team']
        self.date_create = is_date(req[0]['ts'])
        self.text = req[0]['message']


sc = SlackClient(SLACK_TOKEN)
if sc.rtm_connect():

    while True:
        result = None
        req = sc.rtm_read()
        if not req:
            continue
        if not is_message(req) or not is_user(req) or not is_channel(req):
            continue
        print(req)
        # if is_date(req) < datetime.now():
        #     continue
        if req[0]['text'] == '<@{}>:'.format(ID_MARIO):
            result = get_mario_gif()
        if req[0]['text'] == 'prod':
            result = get_version_prod()
        # if is_text(req) not in questions_keys:
        #     continue

        time.sleep(1)
        # pattern = '(.*)?(<@{}>:).?(\w+.\w+)?.?'.format(ID_MARIO)
        # test = re.search(pattern=pattern, string=req[0]['text'], flags=re.IGNORECASE)
        # print('TEST', test.group(1), test.group(2), test.group(3))

        # add user typing {'type': 'user_typing', 'user': 'U0DF0B546', 'channel': 'G0MGYKMA8'}
        key = is_text(req)
        # result = questions[key]
        sc.api_call(
            'chat.postMessage',
            channel=ID_CHANNEL_CONTENT,
            text='<@{}> {}'.format(req[0]['user'], result if result else questions[key]),
            username='Mario',
            icon_emoji=':mario:',
        )
else:
    print("Connection Failed, invalid token?")


# print(sc.api_call('api.test'))
# print(sc.api_call('im.open', user='U0DF0B546'))
