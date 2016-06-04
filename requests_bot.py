__author__ = 'Denis'
from conect_url import get_version_prod, get_default_version
from bs4 import BeautifulSoup
import re

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
}

requests_bot_keys = list(requests_for_bot.keys())


def get_danger_bugs(html):

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
        return tds[0], tds[2]

    danger_bugs = {}

    with open(html, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
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

            danger_bugs.update({task_name: {
                'link': link,
                'summary': summary,
                'qa_report_point': qa_report_point,
                'implementer': implementer
            }})
        return danger_bugs

print(get_danger_bugs('tmp.html'))
