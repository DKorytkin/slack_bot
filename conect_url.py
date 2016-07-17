__author__ = 'Denis'


import requests
import re
from collections import namedtuple
from objects import DEFAULT_VERSION


Vacations = namedtuple('Vacations', ['dev_name', 'date_start', 'date_over'])


def get_request(url):
    req = requests.get(url=url, verify=False)
    return req


def get_mario_gif(req):
    gif_url = 'http://api.giphy.com/v1/gifs/random?api_key=dc6zaTOxFJmzC&tag={}'.format(req)
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
    pattern = r'^<@U1ANC9117>:.(\w+)\sв отпуске с (\d{1,2}-\d{1,2}-\d{2,4}) по\s(\d{1,2}-\d{1,2}-\d{2,4})'

    if re.search(pattern=pattern, string=message, flags=re.IGNORECASE):
        result = re.search(pattern=pattern, string=message, flags=re.IGNORECASE)
        return Vacations(dev_name=result.group(1), date_start=result.group(2), date_over=result.group(3))

