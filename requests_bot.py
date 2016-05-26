__author__ = 'Denis'
from conect_url import get_version_prod, get_mario_gif


requests_for_bot = {
    'default': get_version_prod(),
    'gif': get_mario_gif(),
}

requests_bot_keys = list(requests_for_bot.keys())
