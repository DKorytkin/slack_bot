#!/usr/bin/python3
#  -*- coding: utf8 -*-
__author__ = 'Denis'


import time
import json
from slack_token import SLACK_TOKEN
from slackclient import SlackClient
from datetime import datetime, timezone

with open('questions.json', 'r') as file_questions:
    questions = json.load(file_questions)
questions_keys = list(questions.keys())


def is_message(text):
    if text:
        if text[0]['type'] == 'message':
            return text[0]


def is_text(text):
    try:
        return text[0]['text'].lower()
    except:
        edit_message = text[0]['message']
        return edit_message['text'].lower()


def is_date(text):
    return datetime.fromtimestamp(float(text[0]['ts'])).strftime('%Y-%m-%d %H:%M:%S')


sc = SlackClient(SLACK_TOKEN)
if sc.rtm_connect():

    while True:
        req = sc.rtm_read()
        if req:
            if is_message(req):
                print(req)
                time.sleep(1)
                if is_text(req) in questions_keys and is_date(req) == datetime.now().strftime('%Y-%m-%d %H:%M:%S'):
                    print(is_date(req), datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
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
