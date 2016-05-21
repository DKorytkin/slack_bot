#!/usr/bin/python3
#  -*- coding: utf8 -*-
__author__ = 'Denis'

from slack_token import SLACK_TOKEN
from slackclient import SlackClient
from datetime import datetime
import time
import json
import requests


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


sc = SlackClient(SLACK_TOKEN)
if sc.rtm_connect():

    while True:
        req = sc.rtm_read()
        if not req:
            continue
        if not is_message(req):
            continue
        if not is_channel(req):
            continue
        if is_date(req) < datetime.now():
            continue
        print(req)
        if is_text(req) not in questions_keys:
            continue

        time.sleep(1)

        key = is_text(req)
        sc.api_call(
            'chat.postMessage',
            channel=req[0]['channel'],
            text=questions[key],
            username='Mario',
            icon_emoji=':mario:',
        )
else:
    print("Connection Failed, invalid token?")


# print(sc.api_call('api.test'))
# print(sc.api_call('im.open', user='U0DF0B546'))
