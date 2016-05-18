#!/usr/bin/python3
#  -*- coding: utf8 -*-
__author__ = 'Denis'


import time
import json
from token import SLACK_TOKEN
from slackclient import SlackClient


with open('questions.json', 'r') as file_questions:
    questions = json.load(file_questions)
questions_keys = list(questions.keys())


def is_message(text):
    if text[0]['type'] == 'message':
        return text[0]


def is_text(text):
    return text[0]['text'].lower()


sc = SlackClient(SLACK_TOKEN)
if sc.rtm_connect():

    while True:
        if sc.rtm_read():
            req = sc.rtm_read()
            if is_message(req):
                print(req)
                time.sleep(1)
                if is_text(req) in questions_keys:
                    key = is_text(req)
                    sc.api_call(
                        'chat.postMessage',
                        channel=req[0]['channel'],
                        text=questions[key],
                        username='Mario',
                        icon_emoji=':mario:'
                    )
else:
    print("Connection Failed, invalid token?")


# print(sc.api_call('api.test'))
# print(sc.api_call('im.open', user='U0DF0B546'))
