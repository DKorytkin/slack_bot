#!/usr/bin/python3
#  -*- coding: utf-8 -*-
__author__ = 'Denis'

import time
from datetime import datetime
import concurrent.futures

from slackclient import SlackClient

from random_of_lists import run
from parse_data import mario_update_developers_vacations
from slack_token import SLACK_TOKEN, ID_CHANNEL_CONTENT, ID_MARIO
from common import (
    request_gif,
    get_mario_gif,
    parse_vacation,
    requests_bot_keys,
    mario_requests
)


def process_task(task):
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        pool.submit(task)


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
    convert string timestamp to datetime
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
    time.sleep(1)
    sc.api_call(
        'chat.postMessage',
        channel=channel,
        text=bot_message,
        username='Mario',
        icon_emoji=':mario:'
    )


# TODO don't work
def bot_typing(bot_id=ID_MARIO, channel=ID_CHANNEL_CONTENT):
    sc.api_call(
        'chat.postMessage',
        type='user_typing',
        channel=channel,
        user=bot_id,
    )


sc = SlackClient(SLACK_TOKEN)
if sc.rtm_connect():

    while True:
        result = None
        req = sc.rtm_read()

        # TODO исправить время
        # регулярный запуск
        if datetime.now().strftime('%H:%M:%S') == '18:05:55':
            process_task(send_message(bot_message=run()))
        if datetime.now().strftime("%A") == 'Sunday' and \
                        datetime.now().strftime('%H:%M:%S') == '18:06:55':
            process_task(send_message(bot_message=mario_requests('team bugs')))

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
            process_task(send_message(mario_requests(new_message.text)))

        if 'gif' in new_message.text:
            process_task(
                send_message(
                    get_mario_gif(request_gif(new_message.text))
                )
            )

        if parse_vacation(new_message.text):
            data_vacation = parse_vacation(new_message.text)
            process_task(
                send_message(
                    mario_update_developers_vacations(
                        vacation_data=data_vacation
                    )
                )
            )

else:
    print("Connection Failed, invalid token?")

