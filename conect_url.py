__author__ = 'Denis'
import requests

MARIO_GIF = 'http://api.giphy.com/v1/gifs/random?api_key=dc6zaTOxFJmzC&tag=super+mario'


def get_request(url):
    req = requests.get(url)
    return req.json()


def get_mario_gif(req):
    return req['data']['image_original_url']


