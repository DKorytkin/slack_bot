# !/usr/bin/python3
#  -*- coding: utf-8 -*-
__author__ = 'Denis'


import requests
from collections import namedtuple
import re

from bs4 import BeautifulSoup

from random_of_lists import run
from objects import DEFAULT_VERSION


Vacations = namedtuple('Vacations', ['dev_name', 'date_start', 'date_over'])
danger_bug_poin = 150


def get_request(url):
    req = requests.get(url=url, verify=False)
    return req


def get_mario_gif(req):
    gif_url = (
        'http://api.giphy.com/v1/gifs/random?api_key=dc6zaTOxFJmzC&tag={}'
        .format(req)
    )
    res = get_request(gif_url)
    res = res.json()
    return res['data']['image_original_url']


def get_version_prod(domen):
    # probably better to use regex
    url = 'https://ai.uaprom/stats/{}'.format(domen)
    req = get_request(url)
    req =req.json()
    return req['by_version']['{}1'.format(domen)]['cfg']['title']


def get_default_version(req=get_request(DEFAULT_VERSION)):
    result = req.json()
    return result['text']


def request_gif(text):
    if text == 'gif':
        return 'super+mario'
    pattern = r'.*?gif.(\w+)+\s?(\w+)?\s?(\w+)?'
    text = re.search(pattern=pattern, string=text, flags=re.IGNORECASE)
    result = []
    for i in range(1, 4):
        if text.group(i):
            result.append(text.group(i))
    return '+'.join(result)


def play_mario():
    return '<http://onlajnigry.net/mario.html|play with me>'


def parse_vacation(message):
    # TODO поменять паттерн ID_MARIO
    pattern = r'^<@U1ANC9117>.(\w+)\sв отпуске с (\d{1,2}-\d{1,2}-\d{2,4}) по\s(\d{1,2}-\d{1,2}-\d{2,4})'

    if re.search(pattern=pattern, string=message, flags=re.IGNORECASE):
        result = re.search(
            pattern=pattern,
            string=message,
            flags=re.IGNORECASE
        )
        return Vacations(
            dev_name=result.group(1),
            date_start=result.group(2),
            date_over=result.group(3)
        )


def get_danger_bugs():
    def is_task_name(element):
        if element.a is not None:
            if element.a.string is not None:
                return element.a.string

    def is_task_summary(element):
        if element.p is not None:
            if element.p.string is not None:
                return element.p.string

    def is_info(element):
        tds = []
        list_td = element.find_all('td')
        for td in list_td:
            if td.string is not None:
                tds.append(td.string)
        try:
            return tds[0], tds[2]
        except IndexError:
            return None

    danger_bugs = {}
    html_text = get_request('http://qareport.uaprom/?component_id=10042').text
    soup = BeautifulSoup(html_text, 'html.parser')
    table = soup.find('table')
    table_body = table.find('tbody')
    for i in table_body.find_all('tr'):
        task_name, link, summary, qa_report_point, implementer = [
            None for i in range(5)
            ]
        if is_task_name(i):
            task_name = is_task_name(i)
            link = i.a.get('href')
        if is_task_summary(i):
            summary = is_task_summary(i)
        if is_info(i):
            qa_report_point, implementer = is_info(i)
            # TODO
            # Баг переведен на другую команду?
            # 'Баллы не засчитываются,
            # когда в компонентах указана команда imposer либо architect.'
            # is_info будет None
            danger_bugs.update({task_name: {
                'link': link,
                'summary': summary,
                'qa_report_point': qa_report_point,
                'implementer': implementer
            }})
    return danger_bugs


def bugs_reminder(danger_bug_poin):
    """
    return string bugs >= 150 points
    """
    def is_danger_point(text):
        point = int(bugs_qareport[text]['qa_report_point'])
        if point >= danger_bug_poin:
            return True

    bugs_qareport = get_danger_bugs()
    danger_bugs = []
    for bug in bugs_qareport:
        if is_danger_point(bug):
            sting = '{name} - `{point} points`\n<{url}|{summary}>'.format(
                name=bugs_qareport[bug]['implementer'],
                point=bugs_qareport[bug]['qa_report_point'],
                url=bugs_qareport[bug]['link'],
                summary=bugs_qareport[bug]['summary']
            )
            danger_bugs.append(sting)
    return '\n\n'.join(danger_bugs)


def get_versions():
    verision_str = '\n `default` - {default}' \
                   '\n*production:*' \
                   '\n\t `uaprom` - {uaprom}' \
                   '\n\t `ruprom` - {ruprom}' \
                   '\n\t `belprom` - {belprom}' \
                   '\n\t `kazprom` - {kazprom}' \
                   '\n\t `mdprom` - {mdprom}'.format(
                        default=get_default_version(),
                        uaprom=get_version_prod('uaprom'),
                        ruprom=get_version_prod('ruprom'),
                        belprom=get_version_prod('byprom'),
                        kazprom=get_version_prod('kzprom'),
                        mdprom=get_version_prod('mdprom')
                   )

    return verision_str


def is_help(danger_bug_poin):
    help_str = [
        u'`default` - _view Default version_',
        u'`person on duty` - _provides person on duty on fix bugs_ :bug:',
        u'`team bugs` - _team bugs > {} point_'.format(danger_bug_poin),
        u'`@mario SURNAME в отпуске '
        u'с 01-01-1900 по 01-02-1900` - _Set vacation_ ',
        u'`gif` ... - _receive a random GIF on request_',
        u'`game` - _play with Mario_',
        u'_coming soon_',
    ]
    return '\n'.join(help_str)

requests_bot_keys = ['default', 'game', u'person on duty', 'team bugs', 'help']


def mario_requests(text):
    if text == requests_bot_keys[0]:
        return get_versions()
    elif text == requests_bot_keys[1]:
        return play_mario()
    elif text == requests_bot_keys[2]:
        return run()
    elif text == requests_bot_keys[3]:
        remind = bugs_reminder(danger_bug_poin)
        if remind:
            return remind
        else:
            return "We don't have danger bugs (bug_point > {})".format(
                danger_bug_poin
            )
    elif text == requests_bot_keys[4]:
        return is_help(danger_bug_poin)


