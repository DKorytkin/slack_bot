__author__ = 'Denis'
from conect_url import get_version_prod, get_mario_gif, get_default_version

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
}

requests_bot_keys = list(requests_for_bot.keys())
