__author__ = 'Denis'
import requests
import re

DEFAULT_VERSION = 'https://bwd.cat/widgets/2'


def get_request(url):
    req = requests.get(url=url, verify=False)
    return req.json()


def get_mario_gif(req):
    gif_url = 'http://api.giphy.com/v1/gifs/random?api_key=dc6zaTOxFJmzC&tag={}'.format(req)
    res = get_request(gif_url)
    return res['data']['image_original_url']


def get_version_prod(domen):
    # probably better to use regex
    # url = 'https://ai.uaprom/stats/{}'.format(domen)
    # req = get_request(url)
    # return req['by_version']['{}1'.format(domen)]['cfg']['title']
    return '16.21.1'

def get_default_version(req=get_request(DEFAULT_VERSION)):
    return req['text']


def request_gif(text):
    if text == 'gif':
        return 'super+mario'
    pattern = r'.*?gif.(\w+)+\s?(\w+)?\s?(\w+)?'
    test = re.search(pattern=pattern, string=text, flags=re.IGNORECASE)
    print('TEST', test.group())
    print(test.group(1), test.group(2), test.group(3))
    result = []
    for i in range(1, 4):
        if test.group(i):
            result.append(test.group(i))
    return '+'.join(result)

