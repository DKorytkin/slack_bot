__author__ = 'Denis'
import requests

MARIO_GIF = 'http://api.giphy.com/v1/gifs/random?api_key=dc6zaTOxFJmzC&tag=super+mario'
STATUS_UAPROM = 'https://ai.uaprom/stats/uaprom'


def get_request(url):
    req = requests.get(url=url, verify=False)
    return req.json()


def get_mario_gif(req=get_request(MARIO_GIF)):
    return req['data']['image_original_url']


def get_version_prod(req=get_request(STATUS_UAPROM)):
    # probably better to use regex
    return req['by_version']['uaprom1']['cfg']['title']


