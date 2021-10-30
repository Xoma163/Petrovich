from apps.bot.classes.Command import Command
from apps.bot.classes.consts.Consts import TURRET_WORDS
from apps.bot.utils.utils import random_probability, random_event


class Turret(Command):
    conversation = True
    priority = 85

    def accept(self, event):
        if event.chat and event.chat.need_turret and random_probability(3):
            msg = random_event(TURRET_WORDS)
            event.bot.parse_and_send_msgs(msg, event.peer_id)
        return False

    def start(self):
        pass
