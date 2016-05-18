#!/usr/bin/python3
#  -*- coding: utf8 -*-
__author__ = 'Denis'

import time
import json
from token import SLACK_TOKEN
from slackclient import SlackClient


with open('questions.json', 'r') as file_questions:
    questions = json.load(file_questions)
print(questions)

sc = SlackClient(SLACK_TOKEN)
if sc.rtm_connect():
    print(sc.api_call('api.test'))
    print(sc.api_call('im.open', user='U0DF0B546'))
    while True:
        text = sc.rtm_read()
        if text:
            if text[0]['type'] == 'message':
                print(text)
                time.sleep(1)
                if text[0]['text'].lower() == u'привет!':
                    sc.api_call('chat.postMessage', channel=text[0]['channel'], text=u'Привет, как дела?', username='Mario', icon_emoji=':mario:')
else:
    print("Connection Failed, invalid token?")


