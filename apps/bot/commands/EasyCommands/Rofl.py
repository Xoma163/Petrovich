from apps.bot.classes.common.CommonCommand import CommonCommand
from apps.bot.classes.common.CommonMethods import random_event


class Rofl(CommonCommand):
    def __init__(self):
        names = ["орнуть"]
        super().__init__(names)

    def start(self):
        return random_event(
            ["хд", ":D", "ор", "ору", "😆", ":DDD", "лол", "кек", "лол кек чебурек", "рофл", "ахаха", "АХАХА"])
