# !/usr/bin/python3
#  -*- coding: utf-8 -*-
__author__ = 'Denis'


import requests
from collections import namedtuple
import re

from bs4 import BeautifulSoup

from random_of_lists import run
from objects import DEFAULT_VERSION, QA_REPORT
from slack_token import ID_MARIO_UAPROM


requests_bot_keys = ['game', u'who is on duty today?', 'team bugs', 'help']
Vacations = namedtuple('Vacations', ['dev_name', 'date_start', 'date_over'])
Absent = namedtuple('Absent', ['dev_name', 'status'])
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
    # if domen not in ['uaprom', 'ruprom']:
    #     return req['by_version']['{}2'.format(domen)]['cfg']['title']
    # else:
    return req['by_version']['{}2'.format(domen)]['cfg']['title']


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
    vacation_pattern = (
        r'^<@{id}>\s+?(\w+)\sв\sотпуске\s\w\s'
        r'(\d{day}-\d{month}-\d{year})\s\w\w\s'
        r'(\d{day}-\d{month}-\d{year})'.format(
            id=ID_MARIO_UAPROM,
            day='{1,2}',
            month='{1,2}',
            year='{2,4}'
        )
    )
    absent_pattern = (
        r'^<@{id}>\s+?(\w+)\s'
        r'(в отгуле|отсутствует|сегодня не будет|работает из дому|'
        r'на дому|преподает|нет на месте)'.format(id=ID_MARIO_UAPROM)
    )
    if re.search(
            pattern=vacation_pattern,
            string=message,
            flags=re.IGNORECASE
    ):
        result = re.search(
            pattern=vacation_pattern,
            string=message,
            flags=re.IGNORECASE
        )
        return Vacations(
            dev_name=result.group(1),
            date_start=result.group(2),
            date_over=result.group(3)
        )
    elif re.search(
            pattern=absent_pattern,
            string=message,
            flags=re.IGNORECASE
    ):
        result = re.search(
            pattern=absent_pattern,
            string=message,
            flags=re.IGNORECASE
        )
        return Absent(
            dev_name=result.group(1),
            status=result.group(2)
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
    html_text = get_request(QA_REPORT).text
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
        return bool(
            point >= danger_bug_poin
        )

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
    verision_str = (
        '\n `default` - {default}'
        '\n*production:*'
        '\n\t `uaprom` - {uaprom}'
        '\n\t `ruprom` - {ruprom}'
        '\n\t `belprom` - {belprom}'
        '\n\t `kazprom` - {kazprom}'
        '\n\t `mdprom` - {mdprom}'.format(
            default=get_default_version(),
            uaprom=get_version_prod('uaprom'),
            ruprom=get_version_prod('ruprom'),
            belprom=get_version_prod('byprom'),
            kazprom=get_version_prod('kzprom'),
            mdprom=get_version_prod('mdprom')
        )
    )
    return verision_str


def is_help(danger_bug_poin):
    help_str = [
        u'`who is on duty today?` - _provides person on duty for fix bugs_ :bug:',
        u'`team bugs` - _team bugs > {} point_'.format(danger_bug_poin),
        u'`@mario SURNAME в отпуске '
        u'с 01-01-1900 по 01-02-1900` - _Set vacation_ ',
        u'`gif` ... - _receive random GIPHY on request_',
        u'`game` - _play with Mario_',
        u'_coming soon ..._',
    ]
    return '\n'.join(help_str)


def mario_requests(text):
    if text == requests_bot_keys[0]:
        return play_mario()
    elif text == requests_bot_keys[1]:
        return run()
    elif text == requests_bot_keys[2]:
        remind = bugs_reminder(danger_bug_poin)
        if remind:
            return remind
        else:
            return "Cool!! :tada: We don't have danger bugs (bug_point > {})"\
                .format(
                    danger_bug_poin
                )
    elif text == requests_bot_keys[3]:
        return is_help(danger_bug_poin)


