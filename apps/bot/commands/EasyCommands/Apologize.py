import time

from apps.bot.classes.common.CommonCommand import CommonCommand
from apps.bot.classes.common.CommonMethods import random_event, random_probability


class Apologize(CommonCommand):
    def __init__(self):
        names = ["извинись", "извиняйся", "извинитесь"]

        super().__init__(names, api=False)

    def start(self):
        phrases = ["Извини", "Нет", "Сам извинись", "за что?", "КАВО", "Ты уверен?"]
        phrase = random_event(phrases)
        self.bot.send_message(self.event.peer_id, phrase)
        # ToDo: запускать асинхронную таску по отправке сообщения, результат ретёрнить
        if phrase == "Извини":
            if random_probability(25):
                time.sleep(3)
                self.bot.send_message(self.event.peer_id, "сь")
