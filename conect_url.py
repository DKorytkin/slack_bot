__author__ = 'Denis'
import requests


MARIO_GIF = 'http://api.giphy.com/v1/gifs/random?api_key=dc6zaTOxFJmzC&tag=super+mario'
DEFAULT_VERSION = 'https://bwd.cat/widgets/2'


def get_request(url):
    req = requests.get(url=url, verify=False)
    return req.json()


def get_mario_gif(req=get_request(MARIO_GIF)):
    return req['data']['image_original_url']


def get_version_prod(domen):
    # probably better to use regex
    # arg req=get_request(STATUS_UAPROM)
    url = 'https://ai.uaprom/stats/{}'.format(domen)
    req = get_request(url)
    return req['by_version']['{}1'.format(domen)]['cfg']['title']


def get_default_version(req=get_request(DEFAULT_VERSION)):
    return req['text']
