#!/usr/bin/python3
#  -*- coding: utf-8 -*-
__author__ = 'Denis'

import time
from datetime import datetime
import concurrent.futures
from websocket._exceptions import WebSocketConnectionClosedException

from slackclient import SlackClient

from random_of_lists import run
from objects import holidays, day_off
from parse_data import mario_update_developers_vacations, update_all_issues
from slack_token import SLACK_TOKEN, ID_CHANNEL_CONTENT
from common import (
    request_gif,
    get_mario_gif,
    parse_vacation,
    requests_bot_keys,
    mario_requests
)

TIME_RUN = '09:35:55'
TIME_PARSE = '30'
TIME_DANGER = '13:13:13'
DAY_DANGER = 'Thursday'


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


def run_regular_tasks():
    def is_not_holiday():
        return bool(
            datetime.now().strftime("%d.%m.%y") not in holidays and
            datetime.now().strftime("%A") not in day_off
        )

    def is_ready_parse(str_time):
        return bool(
            datetime.now().strftime('%M') == str_time
        )

    def is_ready_danger_bugs(str_day, str_time):
        return bool(
            datetime.now().strftime('%A') == str_day and
            datetime.now().strftime('%H:%M:%S') == str_time
        )

    def is_ready_run(str_time):
        return bool(
            datetime.now().strftime('%H:%M:%S') == str_time
        )

    if is_ready_parse(TIME_PARSE):
        print('RUN update_all_issues')
        process_task(update_all_issues)
    if is_ready_run(TIME_RUN) and is_not_holiday():
        process_task(send_message(bot_message=run()))
    if is_ready_danger_bugs(DAY_DANGER, TIME_DANGER):
        process_task(send_message(bot_message=mario_requests('team bugs')))


class Message:
    def __init__(self, req):
        self.type = is_message(req)
        self.channel = is_channel(req)
        self.user = is_user(req)
        self.date_create = is_date(req)
        self.text = is_text(req)


def send_message(bot_message, channel=ID_CHANNEL_CONTENT, token=SLACK_TOKEN):
    time.sleep(1)
    sc = SlackClient(token)
    sc.api_call(
        'chat.postMessage',
        channel=channel,
        text=bot_message,
        username='Mario',
        icon_emoji=':mario:'
    )


def slack_read():
    try:
        return sc.rtm_read()
    except (WebSocketConnectionClosedException, ConnectionResetError, OSError):
        print('!!! ERROR connection !!!')
        slack_read()

sc = SlackClient(SLACK_TOKEN)
if sc.rtm_connect():
    while True:
        time.sleep(1)
        req = slack_read()
        # регулярный запуск
        run_regular_tasks()

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
                    mario_update_developers_vacations(
                        vacation_data=data_vacation
                    )
                )
else:
    print('drop connection, invalid token')
