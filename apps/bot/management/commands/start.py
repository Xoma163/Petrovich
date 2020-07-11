from django.core.management import BaseCommand

from apps.bot.classes.bots.TgBot import TgBot
from apps.bot.classes.bots.VkBot import VkBot

vk_bot = VkBot()
tg_bot = TgBot()


def start_vk(debug=False):
    # bot.DEVELOP_DEBUG = debug
    # bot.start()
    # print('start vk')
    pass


def start_tg(debug=False):
    # tg_bot.DEVELOP_DEBUG = debug
    tg_bot.start()
    print('start tg')


def start_camera():
    print('start camera')


class Command(BaseCommand):

    def __init__(self):
        super().__init__()

    def handle(self, *args, **kwargs):
        if 'debug' in kwargs:
            debug = kwargs['debug']
        else:
            debug = False

        start_vk(debug)
        start_tg(debug)
        if not debug:
            start_camera()
