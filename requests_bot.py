#!/usr/bin/python3
#  -*- coding: utf-8 -*-
__author__ = 'Denis'

from bs4 import BeautifulSoup
from conect_url import get_version_prod, get_default_version, get_request
from random_of_lists import run


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
        task_name, link, summary, qa_report_point, implementer = [None for i in range(5)]

        if is_task_name(i):
            task_name = is_task_name(i)
            link = i.a.get('href')
        if is_task_summary(i):
            summary = is_task_summary(i)
        if is_info(i):
            qa_report_point, implementer = is_info(i)
            # TODO
            # Баг переведен на другую команду?
            # 'Баллы не засчитываются, когда в компонентах указана команда imposer либо architect.'
            # is_info будет None
            danger_bugs.update({task_name: {
                'link': link,
                'summary': summary,
                'qa_report_point': qa_report_point,
                'implementer': implementer
            }})
    return danger_bugs


def bugs_reminder():
    def is_danger_point(text):
        point = int(bugs_qareport[text]['qa_report_point'])
        if point >= 100:
            return True

    bugs_qareport = get_danger_bugs()
    danger_bugs = []
    for bug in bugs_qareport:
        print(bug)
        if is_danger_point(bug):
            sting = '{name} - `{point} points`\n<{url}|{summary}>'.format(
                name=bugs_qareport[bug]['implementer'],
                point=bugs_qareport[bug]['qa_report_point'],
                url=bugs_qareport[bug]['link'],
                summary=bugs_qareport[bug]['summary']
            )
            danger_bugs.append(sting)
    return '\n\n'.join(danger_bugs)


requests_for_bot = {
    'default': '\n `default` - {default}'
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
    ),
    'game': '<http://www.mario-games-free.net/swf/1.swf|play with me>',
    u'дежурный': run(),
    'team bugs': bugs_reminder(),
}

requests_bot_keys = list(requests_for_bot.keys())
